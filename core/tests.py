import random

from django.test import TestCase

from core.data_updater import DatabaseUpdater
from core.factories import PrinterDataFactory, ProjectFactory, UserFactory
from core.models import PrinterData, PrinterStateChoices, Project, ProjectStatusChoices
from users.models import User


class TestModels(TestCase):
    """
    Test the core models
    """

    def test_user_creation(self) -> None:
        """Check that the user model can be created successfully"""
        u = UserFactory(first_name="ABCD")

        self.assertEqual(u.first_name, "ABCD")
        self.assertQuerySetEqual(User.objects.order_by("id"), [u])

    def test_project_creation(self) -> None:
        """Check that the project model can be created successfully"""
        project_status = random.choice(ProjectStatusChoices.values)
        project_name = "This is the projects name"
        p = ProjectFactory(project_name=project_name, status=project_status)
        update_date = p.updated_at
        self.assertQuerySetEqual(Project.objects.order_by("id"), [p])
        self.assertEqual(p.project_name, project_name)
        self.assertEqual(p.status, project_status)
        self.assertEqual(p.owner.id, User.objects.first().id)
        self.assertEqual(p.__str__(), f"{project_name} from User ID {p.owner.id}")

        p.project_description = "Bla bla bla"  # to test modified date
        p.save()
        self.assertTrue(update_date < p.updated_at)

    def test_printer_status_creation(self) -> None:
        """Check that the printer status model can be created successfully"""
        printer_state = random.choice(PrinterStateChoices.values)
        s = PrinterDataFactory(state=printer_state)

        self.assertQuerySetEqual(PrinterData.objects.order_by("id"), [s])
        self.assertEqual(s.state, printer_state)
        self.assertEqual(s.project.id, Project.objects.first().id)
        self.assertEqual(s.__str__(), f"{printer_state} at {s.created_at}")


class TestDatabaseUpdates(TestCase):
    """
    Test the database update functionality
    """

    # TODO: use mock:
    class DatabaseUpdaterTest(DatabaseUpdater):
        def __init__(
            self, state: PrinterStateChoices = PrinterStateChoices.RUNNING, gcode_file_name: str | None = None
        ) -> None:
            self.printer_data = PrinterData(state=state, gcode_file_name=gcode_file_name)
            # Note: PrinterDataFactory would already assign a project to printer data

    def test_no_change_if_unknown_state(self):
        """If state is unknown, no change is made"""

        with self.DatabaseUpdaterTest(state=PrinterStateChoices.UNKNOWN):
            pass

        self.assertEqual(PrinterData.objects.count(), 1)
        self.assertEqual(Project.objects.count(), 0)
        self.assertIsNone(PrinterData.objects.first().project)

    def test_save_state_if_different_before(self):
        """If current state is different from previously saved one, save current one."""

        with self.DatabaseUpdaterTest(state=PrinterStateChoices.PREPARING):
            pass

        with self.DatabaseUpdaterTest(state=PrinterStateChoices.RUNNING):
            pass

        with self.DatabaseUpdaterTest(state=PrinterStateChoices.RUNNING, gcode_file_name="Test file.3mf"):
            pass

        with self.DatabaseUpdaterTest(state=PrinterStateChoices.UNKNOWN):
            pass

        with self.DatabaseUpdaterTest(state=PrinterStateChoices.RUNNING):
            pass

        self.assertEqual(PrinterData.objects.count(), 5)

    def test_no_save_if_same_state(self):
        """If state is same as previous, new state is not saved"""

        with self.DatabaseUpdaterTest(state=PrinterStateChoices.RUNNING):
            pass

        with self.DatabaseUpdaterTest(state=PrinterStateChoices.RUNNING):
            pass

        self.assertEqual(PrinterData.objects.count(), 1)

    def test_add_project_when_printing_and_no_other_state(self):
        """If new PrinterData is printing, add Project to database and link to current printer status"""

        with self.DatabaseUpdaterTest():
            pass

        printer_data = PrinterData.objects.first()
        project = Project.objects.first()

        self.assertEqual(PrinterData.objects.count(), 1)
        self.assertEqual(Project.objects.count(), 1)
        self.assertIsNotNone(printer_data.project)
        self.assertEqual(printer_data.project_id, project.id)

    def test_take_previous_project(self):
        """If current print same project, take project from previous printer status"""

        previous_printer_data = PrinterData.objects.create(
            state=PrinterStateChoices.PREPARING, project=ProjectFactory(status=ProjectStatusChoices.PRINTING)
        )

        with self.DatabaseUpdaterTest():
            pass

        latest_printer_data = PrinterData.objects.order_by("-created_at").first()

        self.assertEqual(PrinterData.objects.count(), 2)
        self.assertEqual(Project.objects.count(), 1)
        self.assertIsNotNone(latest_printer_data.project)
        self.assertEqual(latest_printer_data.project_id, previous_printer_data.project_id)

    def test_update_projects_when_previous_different(self):
        """
        If new PrinterData is printing and different from state before,
        add Project to database and link to current printer status
        """

        # running (+ project) -> failed -> running (+ project) > idle -> running (+ project)
        with self.DatabaseUpdaterTest(state=PrinterStateChoices.RUNNING):
            pass

        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.first().status, ProjectStatusChoices.PRINTING)

        with self.DatabaseUpdaterTest(state=PrinterStateChoices.FAILED):
            pass

        latest_printer_data = PrinterData.objects.order_by("-created_at").first()

        self.assertEqual(PrinterData.objects.count(), 2)
        self.assertEqual(latest_printer_data.gcode_file_name, PrinterData.objects.first().gcode_file_name)
        self.assertEqual(Project.objects.count(), 1)
        self.assertIsNotNone(latest_printer_data.project)
        self.assertEqual(Project.objects.first().status, ProjectStatusChoices.UNKNOWN)

        with self.DatabaseUpdaterTest(state=PrinterStateChoices.RUNNING):
            pass

        self.assertEqual(PrinterData.objects.count(), 3)
        self.assertEqual(Project.objects.count(), 2)

        with self.DatabaseUpdaterTest(state=PrinterStateChoices.IDLE):
            pass

        self.assertEqual(PrinterData.objects.count(), 4)
        self.assertEqual(Project.objects.count(), 2)

        with self.DatabaseUpdaterTest(state=PrinterStateChoices.RUNNING):
            pass

        self.assertEqual(PrinterData.objects.count(), 5)
        self.assertEqual(Project.objects.count(), 3)
