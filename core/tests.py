import random
from typing import Any
from unittest.mock import MagicMock, patch

from bambulabs_api import GcodeState, PrintStatus
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

    def _generate_fake_printer_state(self, **kwargs: Any) -> dict:
        fake_printer_data = {
            "state": GcodeState.UNKNOWN,
            "detailed_state": None,
            "wifi_signal_dbm": int("-12dBm".replace("dBm", "")),
            "light_state": "on",
            "percentage": None,
            "gcode_file_name": "",
            "source_type": None,
            "subtask_name": None,
            "current_layer_number": None,
            "total_layers": None,
            "temperature_bed": None,
            "temperature_nozzle": None,
            "temperature_chamber": None,
        }

        return {**fake_printer_data, **kwargs}

    @patch("core.data_updater.DatabaseUpdater.get_and_prepare_printer_data")
    def test_no_change_if_unknown_state(self, mock_get_and_prepare_printer_data):
        """If state is unknown, no change is made"""

        mock_get_and_prepare_printer_data.return_value = PrinterData(state=PrinterStateChoices.UNKNOWN)
        DatabaseUpdater().run()

        p = PrinterData.objects.first()

        self.assertEqual(PrinterData.objects.count(), 1)
        self.assertEqual(p.state, PrinterStateChoices.UNKNOWN)
        self.assertEqual(Project.objects.count(), 0)
        self.assertIsNone(p.project)

    def test_prepare_printer_data_with_unknown_state(self):
        """Check that printer data is correctly prepared from api dictionary output when state unknown"""

        fake_printer_data_unknown = self._generate_fake_printer_state()

        with patch("core.data_updater.PrinterBambuP1S") as mock_printer_class:
            mock_instance = MagicMock()

            mock_instance.get_all_infos.return_value = fake_printer_data_unknown
            mock_printer_class.return_value.__enter__.return_value = mock_instance
            mock_printer_class.return_value.__exit__.return_value = None

            printer_state_unknown = DatabaseUpdater.get_and_prepare_printer_data(with_image=False)

        self.assertEqual(PrinterData.objects.count(), 0)
        self.assertEqual(printer_state_unknown.state, 50)
        self.assertEqual(printer_state_unknown.detailed_state, 40)
        self.assertEqual(printer_state_unknown.wifi_signal_dbm, -12)
        self.assertTrue(printer_state_unknown.is_light_on)

    def test_prepare_printer_data_with_given_state(self):
        """Check that printer data is correctly prepared from api dictionary output when state provided"""

        fake_printer_data_state = self._generate_fake_printer_state(
            state=GcodeState.RUNNING,
            detailed_state=PrintStatus.FILAMENT_LOADING.value,
            gcode_file_name="123 layer X.mf3",
        )

        with patch("core.data_updater.PrinterBambuP1S") as mock_printer_class:
            mock_instance = MagicMock()

            # define second printer state
            mock_instance.get_all_infos.return_value = fake_printer_data_state
            mock_printer_class.return_value.__enter__.return_value = mock_instance
            mock_printer_class.return_value.__exit__.return_value = None

            printer_state_none = DatabaseUpdater.get_and_prepare_printer_data(with_image=False)

        self.assertEqual(printer_state_none.state, 20)
        self.assertEqual(printer_state_none.detailed_state, 24)
        self.assertEqual(printer_state_none.gcode_file_name, "123 layer X.mf3")

    @patch("core.data_updater.DatabaseUpdater.get_and_prepare_printer_data")
    def test_save_state_if_different_before(self, mock_get_and_prepare_printer_data):
        """If current state is different from previously saved one, save current one."""

        mock_get_and_prepare_printer_data.return_value = PrinterData(state=PrinterStateChoices.PREPARING)
        DatabaseUpdater().run()

        mock_get_and_prepare_printer_data.return_value = PrinterData(state=PrinterStateChoices.RUNNING)
        DatabaseUpdater().run()

        mock_get_and_prepare_printer_data.return_value = PrinterData(
            state=PrinterStateChoices.RUNNING, gcode_file_name="Test file.3mf"
        )
        DatabaseUpdater().run()

        mock_get_and_prepare_printer_data.return_value = PrinterData(state=PrinterStateChoices.UNKNOWN)
        DatabaseUpdater().run()

        mock_get_and_prepare_printer_data.return_value = PrinterData(state=PrinterStateChoices.RUNNING)
        DatabaseUpdater().run()

        self.assertEqual(PrinterData.objects.count(), 5)

    @patch("core.data_updater.DatabaseUpdater.get_and_prepare_printer_data")
    def test_no_save_if_same_state(self, mock_get_and_prepare_printer_data):
        """If state is same as previous, new state is not saved"""

        mock_get_and_prepare_printer_data.return_value = PrinterData(state=PrinterStateChoices.RUNNING)
        DatabaseUpdater().run()
        DatabaseUpdater().run()

        self.assertEqual(PrinterData.objects.count(), 1)

    @patch("core.data_updater.DatabaseUpdater.get_and_prepare_printer_data")
    def test_add_project_when_printing_and_no_other_state(self, mock_get_and_prepare_printer_data):
        """If new PrinterData is printing, add Project to database and link to current printer status"""

        mock_get_and_prepare_printer_data.return_value = PrinterData(state=PrinterStateChoices.RUNNING)
        DatabaseUpdater().run()

        printer_data = PrinterData.objects.first()
        project = Project.objects.first()

        self.assertEqual(PrinterData.objects.count(), 1)
        self.assertEqual(Project.objects.count(), 1)
        self.assertIsNotNone(printer_data.project)
        self.assertEqual(printer_data.project_id, project.id)

    @patch("core.data_updater.DatabaseUpdater.get_and_prepare_printer_data")
    def test_take_previous_project(self, mock_get_and_prepare_printer_data):
        """If current print same project, take project from previous printer status"""

        previous_printer_data = PrinterData.objects.create(
            state=PrinterStateChoices.PREPARING, project=ProjectFactory(status=ProjectStatusChoices.PRINTING)
        )

        mock_get_and_prepare_printer_data.return_value = PrinterData(state=PrinterStateChoices.RUNNING)
        DatabaseUpdater().run()

        latest_printer_data = PrinterData.objects.order_by("-created_at").first()

        self.assertEqual(PrinterData.objects.count(), 2)
        self.assertEqual(Project.objects.count(), 1)
        self.assertIsNotNone(latest_printer_data.project)
        self.assertEqual(latest_printer_data.project_id, previous_printer_data.project_id)

    @patch("core.data_updater.DatabaseUpdater.get_and_prepare_printer_data")
    def test_update_projects_when_previous_different(self, mock_get_and_prepare_printer_data):
        """
        If new PrinterData is printing and different from state before,
        add Project to database and link to current printer status
        """

        # running (+ project) -> failed -> running (+ project) > idle -> running (+ project)
        mock_get_and_prepare_printer_data.return_value = PrinterData(state=PrinterStateChoices.RUNNING)
        DatabaseUpdater().run()

        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.first().status, ProjectStatusChoices.PRINTING)

        mock_get_and_prepare_printer_data.return_value = PrinterData(state=PrinterStateChoices.FAILED)
        DatabaseUpdater().run()

        latest_printer_data = PrinterData.objects.order_by("-created_at").first()

        self.assertEqual(PrinterData.objects.count(), 2)
        self.assertEqual(latest_printer_data.gcode_file_name, PrinterData.objects.first().gcode_file_name)
        self.assertEqual(Project.objects.count(), 1)
        self.assertIsNotNone(latest_printer_data.project)
        self.assertEqual(Project.objects.first().status, ProjectStatusChoices.UNKNOWN)

        mock_get_and_prepare_printer_data.return_value = PrinterData(state=PrinterStateChoices.RUNNING)
        DatabaseUpdater().run()

        self.assertEqual(PrinterData.objects.count(), 3)
        self.assertEqual(Project.objects.count(), 2)

        mock_get_and_prepare_printer_data.return_value = PrinterData(state=PrinterStateChoices.IDLE)
        DatabaseUpdater().run()

        self.assertEqual(PrinterData.objects.count(), 4)
        self.assertEqual(Project.objects.count(), 2)

        mock_get_and_prepare_printer_data.return_value = PrinterData(state=PrinterStateChoices.RUNNING)
        DatabaseUpdater().run()

        self.assertEqual(PrinterData.objects.count(), 5)
        self.assertEqual(Project.objects.count(), 3)
