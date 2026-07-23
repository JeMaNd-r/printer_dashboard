from typing import Self

from core.models import PrinterData, PrinterStateChoices, Project, ProjectStatusChoices
from printer_api.api import PrinterBambuP1S


class DatabaseUpdater:
    """
    Retrieve and save printer status and/or project to database

    If necessary, add project to database and use that in printer status.
    Otherwise, use latest project for printer status.
    """

    def __init__(self, with_image: bool = False) -> None:
        self.printer_data = self.get_and_prepare_printer_data(with_image=with_image)

    def __enter__(self) -> Self:
        print("Database update started.")
        self.check_status_for_new_project()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        print("Database update finished.")
        save_status = self.check_if_saving_printer_data_needed()
        if save_status:
            self.save_printer_data_to_db()
            return
        print("Printer status didn't change from previous state. No save needed.")
        return

    PRINTER_PRINTING_STATES = [
        PrinterStateChoices.PREPARING,
        PrinterStateChoices.RUNNING,
        PrinterStateChoices.PAUSED,
        PrinterStateChoices.FAILED,
    ]

    def create_new_project(self, is_gcode_unique: bool = False) -> "Project":
        """
        Create new project based on printer state, save it to database and return it

        :return: Project object
        """

        print("Creating new project...")
        # Define project status based on printer state
        state_mapping = {
            PrinterStateChoices.IDLE: ProjectStatusChoices.UNKNOWN,
            PrinterStateChoices.PREPARING: ProjectStatusChoices.PRINTING,
            PrinterStateChoices.RUNNING: ProjectStatusChoices.PRINTING,
            PrinterStateChoices.PAUSED: ProjectStatusChoices.PRINTING,
            PrinterStateChoices.FINISHED: ProjectStatusChoices.DONE,
            PrinterStateChoices.UNKNOWN: ProjectStatusChoices.UNKNOWN,
            PrinterStateChoices.FAILED: ProjectStatusChoices.UNKNOWN,
        }

        project_status = state_mapping.get(self.printer_data.state)

        # Define project name
        project_name = f"Gcode file {self.printer_data.gcode_file_name}"

        if len(project_name) < 14:
            project_name = f"Unknown project on {self.printer_data.created_at}"

        elif not is_gcode_unique:
            project_name = f"{project_name} on {self.printer_data.created_at}"

        return Project.objects.create(project_name=project_name, is_created_manually=False, status=project_status)

    def get_and_prepare_printer_data(self, with_image: bool = False) -> "PrinterData":
        """
        Get data in dictionary from get_all_infos() and prepare as PrinterData object.

        Preparation steps:
        1. printer state of type GcodeState object is converted to str
        2. light state ("on"/"off") is removed from dictionary and then converted to boolean field value.

        :param with_image: Boolean value to indicate if image should be requested and saved or not

        :return: None
        """

        image = None

        with PrinterBambuP1S() as printer:
            printer_data = printer.get_all_infos()
            if with_image:
                image = printer.get_camera_image()

        # transform GCodeState value for printer state to str
        printer_data["state"] = printer_data["state"].value

        light_state = printer_data.pop("light_state")

        p = PrinterData(**printer_data)

        p.is_light_on = True if light_state == "on" else False

        if with_image:
            p.chamber_image = image

        return p

    def save_printer_data_to_db(self) -> None:
        """Save PrinterData object to database"""

        self.printer_data.save()
        print("Printer status saved to database.")

    def check_status_for_new_project(self) -> None:
        """
        Create new project if it doesn't exist and add accordingly to printer state field.

        Add new project based on the following logic:
        Current state has to be one of printing states.
        If last printer state was not printing, add new project.
        If last printer state was printing, check last state same gcode.
        -> If same gcode file, check if last state percentage is higher than current.
        --> If current state percentage is lower than previous, add new project.
        If no project added, add project from previous printer state to current one.
        If previous printer state was printing and new one is not, update project status.

        Project name will be based on GCode file and date if project has not been created manually before.

        :return: None
        """

        # If current state unknown, return current state without database or state changes
        if self.printer_data.state == PrinterStateChoices.UNKNOWN:
            return

        # If current state is not one of printing states, return current state without changes
        if self.printer_data.state not in self.PRINTER_PRINTING_STATES:
            return

        # Check if latest printer state in database was one of printing states.
        latest_stored_state = PrinterData.objects.order_by("-created_at").first()

        if latest_stored_state is None:
            self.printer_data.project = self.create_new_project(is_gcode_unique=True)

        # -> If last printer state was not printing, ADD NEW project.
        elif latest_stored_state.state not in self.PRINTER_PRINTING_STATES:
            self.printer_data.project = self.create_new_project(is_gcode_unique=True)

        # If last printer state was printing, check if last state has same gcode file.
        # -> If gcode file is not the same, ADD NEW project.
        elif latest_stored_state.gcode_file_name != self.printer_data.gcode_file_name:
            self.printer_data.project = self.create_new_project(is_gcode_unique=True)

        # If same gcode file, check if last state percentage is higher than current.
        # -> If current state percentage is lower than previous, ADD NEW project.
        elif latest_stored_state.percentage > self.printer_data.percentage:
            self.printer_data.project = self.create_new_project(is_gcode_unique=False)

        # else: don't save a new project but update with the latest project ID
        else:
            self.printer_data.project = latest_stored_state.project

            # if not printing but last state was, update project
            if (
                self.printer_data.state not in self.PRINTER_PRINTING_STATES
                and latest_stored_state.state in self.PRINTER_PRINTING_STATES
            ):
                print("Updating project status...")
                Project.objects.filter(id=self.printer_data.project_id).update(status=ProjectStatusChoices.DONE)

        return

    def check_if_saving_printer_data_needed(self) -> bool:
        """
        Compare latest printer state in database with current one.

        If latest printer state is similar to current one, return False (saving not needed), else True

        :return: True or False
        """
        latest_stored_state = PrinterData.objects.order_by("-created_at").first()
        values_latest_stored_state = {
            "state": latest_stored_state.state,
            "detailed_state": latest_stored_state.detailed_state,
            "gcode_file_name": latest_stored_state.gcode_file_name,
            "percentage": latest_stored_state.percentage,
            "project": latest_stored_state.project,
            "is_light_on": latest_stored_state.is_light_on,
        }

        values_printer_data = {
            "state": self.printer_data.state,
            "detailed_state": self.printer_data.detailed_state,
            "gcode_file_name": self.printer_data.gcode_file_name,
            "percentage": self.printer_data.percentage,
            "project": self.printer_data.project,
            "is_light_on": self.printer_data.is_light_on,
        }

        print(values_printer_data)

        if values_printer_data == values_latest_stored_state:
            return False
        return True
