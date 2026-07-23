import random

from django.test import TestCase

from core.factories import PRINTER_STATE_CHOICES, PrinterDataFactory, ProjectFactory, UserFactory
from core.models import PrinterData, Project, ProjectStatusChoices
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
        printer_state = random.choice(PRINTER_STATE_CHOICES)
        s = PrinterDataFactory(state=printer_state)

        self.assertQuerySetEqual(PrinterData.objects.order_by("id"), [s])
        self.assertEqual(s.state, printer_state)
        self.assertEqual(s.project.id, Project.objects.first().id)
        self.assertEqual(s.__str__(), f"{printer_state} at {s.created_at}")


class TestDatabaseUpdates(TestCase):
    """
    Test the database update functionality
    """

    # TODO: fix tests after refactoring of data_updater.py
    # def test_add_project_when_printing(self):
    #     """If new PrinterData is printing, add Project to database and link to current printer status"""
    #
    #     printer = PrinterData(state=PrinterStateChoices.RUNNING)
    #     previous_no_project_id = printer.project_id
    #
    #     data_updater.check_for_new_project(current_state=printer)
    #
    #     project = Project.objects.first()
    #
    #     self.assertEqual(Project.objects.count(), 1)
    #     self.assertEqual(printer.project, project)
    #     self.assertNotEqual(previous_no_project_id, printer.project_id)
    #
    # def test_take_previous_project(self):
    #     """If current print same project, take project from previous printer status"""
    #
    #     PrinterData.objects.create(state=PrinterStateChoices.PREPARING)
    #     printer2 = PrinterData(state=PrinterStateChoices.RUNNING)
    #     previous_no_project_id = printer2.project
    #
    #     data_updater.check_for_new_project(printer2)
    #     printer2.save()
    #
    #     self.assertEqual(PrinterData.objects.count(), 2)
    #     self.assertEqual(Project.objects.count(), 1)
    #     self.assertIsNotNone(printer2.project)
    #     self.assertNotEqual(printer2.project, previous_no_project_id)


# TODO: add tests for API
