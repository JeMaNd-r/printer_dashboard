from django.test import TestCase
from django.urls import reverse

from storage.factories import PrinterStatusFactory, ProjectFactory
from storage.models import PrinterStatus, Project


class TestProjectListView(TestCase):
    """
    Test the project list view
    """

    def test_no_projects(self):
        """If no projects exist, an appropriate error should be displayed"""

        response = self.client.get(reverse("dashboard:project-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No projects yet.")
        self.assertQuerySetEqual(response.context["project_list"], [])

    def test_project_list_view(self):
        """Check that the project list view works"""

        p1 = ProjectFactory()
        p2 = ProjectFactory()
        p3 = ProjectFactory()

        response = self.client.get(reverse("dashboard:project-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), 3)
        self.assertQuerySetEqual(
            response.context["project_list"].order_by("id"),
            [p1, p2, p3],
            transform=lambda p: p,
        )


class TestProjectDetailView(TestCase):
    """
    Test the project detail view
    """

    def test_project_detail_view(self):
        """Check that the project detail view shows existing projects"""

        p1 = ProjectFactory()
        p1_id = p1.id

        r1 = self.client.get(reverse("dashboard:project-detail", kwargs={"pk": p1_id}))
        r2 = self.client.get(reverse("dashboard:project-detail", kwargs={"pk": 200}))

        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 404)
        self.assertEqual(Project.objects.count(), 1)

        self.assertEqual(r1.context["project"], p1)


class TestPrinterStatusView(TestCase):
    """
    Test the printer status (list) view
    """

    def test_no_printer_states(self):
        """If no printer state was yet requested, an appropriate error should be displayed"""
        response = self.client.get(reverse("dashboard:stats"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No printer states yet.")
        self.assertQuerySetEqual(response.context["object_list"], [])

    def test_printer_status_list_view(self):
        """Check that the printer status list view works"""

        p1 = PrinterStatusFactory()
        p2 = PrinterStatusFactory()

        response = self.client.get(reverse("dashboard:stats"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PrinterStatus.objects.count(), 2)
        self.assertQuerySetEqual(
            response.context["object_list"].order_by("id"),
            [p1, p2],
            transform=lambda p: p,
        )

    def test_printer_status_link_to_project(self):
        pass  # TODO Add test to check list printer status & project
