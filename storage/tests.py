import random

from django.test import TestCase

from storage.factories import PRINTER_STATE_CHOICES, PrinterStatusFactory, ProjectFactory, UserFactory
from storage.models import PrinterStatus, Project, StatusChoices
from users.models import User


class TestStorage(TestCase):
    """
    Test the storage methods
    """

    def test_user_creation(self) -> None:
        """Check that the user model can be created successfully"""
        u = UserFactory(first_name="ABCD")

        self.assertEqual(u.first_name, "ABCD")
        self.assertQuerySetEqual(User.objects.order_by("id"), [u])

    def test_project_creation(self) -> None:
        """Check that the project model can be created successfully"""
        project_status = random.choice(StatusChoices.values)
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

    def test_printerstatus_creation(self) -> None:
        """Check that the printerstatus model can be created successfully"""
        printer_state = random.choice(PRINTER_STATE_CHOICES)
        s = PrinterStatusFactory(state=printer_state)

        self.assertQuerySetEqual(PrinterStatus.objects.order_by("id"), [s])
        self.assertEqual(s.state, printer_state)
        self.assertEqual(s.project.id, Project.objects.first().id)
        self.assertEqual(s.__str__(), f"{printer_state} at {s.created_at}")


# TODO: add tests for API
