from typing import Optional

from PIL import Image

from core.models import PrinterData, PrinterStateChoices, Project, ProjectStatusChoices
from printer_api.api import PrinterBambuP1S


class DatabaseUpdater:
    """
    Retrieve and save printer status and/or project to database

    If necessary, add project to database and use that in printer status.
    Otherwise, use latest project for printer status.
    """

    PRINTER_PRINTING_STATES: list = [
        PrinterStateChoices.PREPARING,
        PrinterStateChoices.RUNNING,
        PrinterStateChoices.PAUSED,
    ]

    def __init__(self, with_image: bool = False) -> None:
        self.with_image = with_image

    def run(self):
        printer_data = self.get_and_prepare_printer_data(with_image=self.with_image)

        print("Database update started.")
        self._check_status_for_new_project(printer_data)
        print("Printer data retrieved. Checking if saving needed...")

        save_status = self.check_if_saving_printer_data_needed(printer_data)
        if save_status:
            self.save_printer_data_to_db(printer_data)
            return
        print("Printer status didn't change from previous state. No save needed.")

    @staticmethod
    def get_and_prepare_printer_data(with_image: bool = False) -> "PrinterData":
        """
        Get data in dictionary from get_all_infos() and prepare as PrinterData object.

        Preparation steps:
        1. printer state of type GcodeState object is converted to str
        2. light state ("on"/"off") is removed from dictionary and then converted to boolean field value.

        :param with_image: Boolean value to indicate if image should be requested and saved or not

        """

        image: Optional[Image.Image] = None

        with PrinterBambuP1S() as printer:
            printer_data: dict = printer.get_all_infos()
            if with_image:
                image: Image.Image = printer.get_camera_image()

        # transform GCodeState value to model's Enum value
        printer_data["state"]: int = PrinterStateChoices[printer_data["state"].name].value

        if printer_data["detailed_state"] is None:
            printer_data["detailed_state"]: int = 40

        light_state: Optional[str] = printer_data.pop("light_state")

        p: PrinterData = PrinterData(**printer_data)

        p.is_light_on = True if light_state == "on" else False

        if with_image:
            p.chamber_image = image

        return p

    @staticmethod
    def save_printer_data_to_db(printer_data) -> None:
        """Save PrinterData object to database"""

        printer_data.save()
        print("Printer status saved to database.")

    @staticmethod
    def check_if_saving_printer_data_needed(printer_data: PrinterData) -> bool:
        """
        Compare latest printer state in database with current one.

        If latest printer state is similar to current one, return False (saving not needed), else True

        :return: True or False
        """

        if PrinterData.objects.count() == 0:
            print("No previous printer data available.")
            return True

        latest_stored_state: PrinterData = PrinterData.objects.order_by("-created_at").first()

        values_latest_stored_state = {
            "state": latest_stored_state.state,
            "detailed_state": latest_stored_state.detailed_state,
            "gcode_file_name": latest_stored_state.gcode_file_name,
            "percentage": latest_stored_state.percentage,
            "project": latest_stored_state.project,
            "is_light_on": latest_stored_state.is_light_on,
        }

        values_printer_data = {
            "state": printer_data.state,
            "detailed_state": printer_data.detailed_state,
            "gcode_file_name": printer_data.gcode_file_name,
            "percentage": printer_data.percentage,
            "project": printer_data.project,
            "is_light_on": printer_data.is_light_on,
        }

        if values_printer_data == values_latest_stored_state:
            print("Previous printer data same as current ones...")
            return False

        print("Previous printer data different from current one...")
        return True

    def _create_new_project(self, printer_data: PrinterData, is_gcode_unique: bool = False) -> "Project":
        """
        Create new project based on printer state, save it to database and return it

        :return: Project object
        """

        print("Creating new project...")
        # Define project status based on printer state
        state_mapping: dict = {
            PrinterStateChoices.IDLE: ProjectStatusChoices.UNKNOWN,
            PrinterStateChoices.PREPARING: ProjectStatusChoices.PRINTING,
            PrinterStateChoices.RUNNING: ProjectStatusChoices.PRINTING,
            PrinterStateChoices.PAUSED: ProjectStatusChoices.PRINTING,
            PrinterStateChoices.FINISHED: ProjectStatusChoices.DONE,
            PrinterStateChoices.UNKNOWN: ProjectStatusChoices.UNKNOWN,
            PrinterStateChoices.FAILED: ProjectStatusChoices.UNKNOWN,
        }

        project_status: Optional[int] = state_mapping.get(printer_data.state)

        # Define project name
        project_name: str = f"Gcode file {printer_data.gcode_file_name}"

        if len(project_name) < 14:
            project_name: str = f"Unknown project on {printer_data.created_at}"

        elif not is_gcode_unique:
            project_name: str = f"{project_name} on {printer_data.created_at}"

        return Project.objects.create(project_name=project_name, is_created_manually=False, status=project_status)

    def _check_status_for_new_project(self, printer_data: PrinterData) -> None:
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

        # If no previous printer state exists, ADD NEW project
        if PrinterData.objects.count() == 0:
            if printer_data.state in self.PRINTER_PRINTING_STATES:
                printer_data.project = self._create_new_project(printer_data=printer_data, is_gcode_unique=True)

            return

        latest_stored_state: PrinterData = PrinterData.objects.order_by("-created_at").first()

        # If current state is not printing, check if project update is needed
        if printer_data.state not in self.PRINTER_PRINTING_STATES:
            # If latest state was printing but current is not, update project status
            if latest_stored_state.state in self.PRINTER_PRINTING_STATES:
                print("Updating project status...")

                # If current status FAILED, change project status to UNKNOWN
                if printer_data.state == PrinterStateChoices.FAILED:
                    printer_data.project = latest_stored_state.project

                    new_project_status = ProjectStatusChoices.UNKNOWN
                    print("WARNING: Printer status FAILED.")
                    print(f"Project status {latest_stored_state.project_id} is set to UNKNOWN")

                # If not FAILED, change project status to DONE
                else:
                    new_project_status = ProjectStatusChoices.DONE

                Project.objects.filter(id=printer_data.project_id).update(status=new_project_status)

            return

        # If current is printing and last printer state was not printing, ADD NEW project.
        if latest_stored_state.state not in self.PRINTER_PRINTING_STATES:
            printer_data.project = self._create_new_project(printer_data=printer_data, is_gcode_unique=True)

        # If last printer state was printing, check if last state has same gcode file.
        # -> If gcode file is not the same, ADD NEW project.
        elif latest_stored_state.gcode_file_name != printer_data.gcode_file_name:
            printer_data.project = self._create_new_project(printer_data=printer_data, is_gcode_unique=True)

        # If same gcode file, check if last state percentage is higher than current.
        # -> If current state percentage is lower than previous, ADD NEW project.
        elif latest_stored_state.percentage == printer_data.percentage:
            printer_data.project = latest_stored_state.project
            return

        elif latest_stored_state.percentage is None or printer_data.percentage is None:
            printer_data.project = latest_stored_state.project

        elif latest_stored_state.percentage > printer_data.percentage:
            printer_data.project = self._create_new_project(printer_data=printer_data, is_gcode_unique=False)

        return
