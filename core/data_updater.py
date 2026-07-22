"""
Retrieve and save printer status and/or project to database

If necessary, add project to database and use that in printer status.
Otherwise, use latest project for printer status.
"""

from bambulabs_api import GcodeState

from core.models import PrinterStatus, PrinterStatusChoices, Project, ProjectStatusChoices
from printer_api.api import PrinterBambuP1S

PRINTER_PRINTING_STATES = [
    PrinterStatusChoices.PREPARING,
    PrinterStatusChoices.RUNNING,
    PrinterStatusChoices.PAUSED,
    PrinterStatusChoices.FAILED,
]


def create_new_project(project_name: str, printer_state: str) -> "Project":
    """
    Create new project based on printer state, save it to database and return it

    :return: Project object
    """

    # Define project status based on printer state
    state_mapping = {
        PrinterStatusChoices.IDLE: ProjectStatusChoices.UNKNOWN,
        PrinterStatusChoices.PREPARING: ProjectStatusChoices.PRINTING,
        PrinterStatusChoices.RUNNING: ProjectStatusChoices.PRINTING,
        PrinterStatusChoices.PAUSED: ProjectStatusChoices.PRINTING,
        PrinterStatusChoices.FINISHED: ProjectStatusChoices.DONE,
        PrinterStatusChoices.UNKNOWN: ProjectStatusChoices.UNKNOWN,
        PrinterStatusChoices.FAILED: ProjectStatusChoices.UNKNOWN,
    }

    project_status = state_mapping.get(printer_state)

    return Project.objects.create(project_name=project_name, is_created_manually=False, status=project_status)


def get_and_prepare_printer_data(with_image: bool = False) -> "PrinterStatus":
    """
    Get data in dictionary from get_all_infos() and prepare as PrinterStatus object.

    Preparation steps:
    1. light state ("on"/"off") is removed from dictionary and then converted to boolean field value.
    3. Similarly, is_printing is populated using printer_state

    :param with_image: Boolean value to indicate if image should be requested and saved or not

    :return: None
    """

    with PrinterBambuP1S() as printer:
        printer_data = printer.get_all_infos()
        light_state = printer_data.pop("light_state")

        p = PrinterStatus(**printer_data)

        if p.printer_state == GcodeState.RUNNING:
            p.is_printing = True
        else:
            p.is_printing = False

        p.is_light_on = True if light_state == "on" else False

        if with_image:
            p.chamber_image = printer.get_camera_image()

        return p


def save_printer_status_to_db(printer_state: PrinterStatus) -> None:
    """Save PrinterStatus object to database"""

    printer_state.save()
    print("Printer status saved to database.")


def check_for_new_project(current_state: PrinterStatus) -> None:
    """
    Create new project if it doesn't exist.

    Add new project based on the following logic:
    Current state has to be one of printing states.
    If last printer state was not printing, add new project.
    If last printer state was printing, check last state same gcode.
    -> If same gcode file, check if last state print_percentage is higher than current.
    --> If current state percentage is lower than previous, add new project.
    If no project added, add project from previous printer state to current one.
    If previous printer state was printing and new one is not, update project status.

    Project name will be based on GCode file and date if project has not been created manually before.

    :return: None
    """

    # If current state unknown, return current state without database or state changes
    if current_state.printer_state == PrinterStatusChoices.UNKNOWN:
        return current_state

    # Check if current state is one of printing states.
    if current_state.printer_state in PRINTER_PRINTING_STATES:
        # Check if latest printer state in database was one of printing states.
        latest_stored_state = PrinterStatus.objects.order_by("-created_at").first()

        if latest_stored_state is None:
            new_project_name = f"Gcode file {current_state.print_gcode_file}"

            if new_project_name == "":
                new_project_name = f"Unknown project on {current_state.created_at}"

            new_project = create_new_project(
                project_name=new_project_name,
                printer_state=current_state.printer_state,
            )

            current_state.project = new_project

        # -> If last printer state was not printing, ADD NEW project.
        elif latest_stored_state.printer_state not in PRINTER_PRINTING_STATES:
            new_project_name = f"Gcode file {current_state.print_gcode_file}"

            if new_project_name == "":
                new_project_name = f"Unknown project on {current_state.created_at}"

            new_project = create_new_project(
                project_name=new_project_name,
                printer_state=current_state.printer_state,
            )

            current_state.project = new_project

        # If last printer state was printing, check if last state has same gcode file.
        # -> If gcode file is not the same, ADD NEW project.
        elif latest_stored_state.print_gcode_file != current_state.print_gcode_file:
            new_project_name = f"Gcode file {current_state.print_gcode_file}"

            if new_project_name == "":
                new_project_name = f"Unknown project on {current_state.created_at}"

            new_project = create_new_project(
                project_name=new_project_name,
                printer_state=current_state.printer_state,
            )
            current_state.project = new_project

        # If same gcode file, check if last state print_percentage is higher than current.
        # -> If current state percentage is lower than previous, ADD NEW project.
        elif latest_stored_state.print_percentage > current_state.print_percentage:
            new_project_name = f"Gcode file {current_state.print_gcode_file} on {current_state.created_at.date()}"

            if new_project_name == "":
                new_project_name = f"Unknown project on {current_state.created_at}"

            new_project = create_new_project(
                project_name=new_project_name,
                printer_state=current_state.printer_state,
            )

            current_state.project = new_project

        # else: don't save a new project but update with the latest project ID
        else:
            current_state.project = latest_stored_state.project

            # if not printing but last state was, update project
            if (
                current_state.printer_state not in PRINTER_PRINTING_STATES
                and latest_stored_state.printer_state in PRINTER_PRINTING_STATES
            ):
                Project.objects.filter(id=current_state.project_id).update(status=ProjectStatusChoices.DONE)

    return None


def check_if_saving_printer_status_needed():
    pass
