from typing import Any
from unittest.mock import MagicMock, patch

from bambulabs_api import GcodeState, PrintStatus
from django.db.models import F
from django.test import TestCase

from core.data_updater import DatabaseUpdater
from core.factories import ProjectFactory
from core.models import PrinterData, PrinterStateChoices, Project, ProjectStatusChoices
from core.tests.utils import generate_test_image


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
    def test_update_projects_when_previous_state_different(self, mock_get_and_prepare_printer_data):
        """
        If new PrinterData is printing and different from state before,
        add Project to database and link to current printer status
        """

        # test cycle: running (+ project) -> failed -> running (+ project) -> idle -> running (+ project)
        test_image_1 = generate_test_image(image_name="test_image_1", color="#000000")

        mock_get_and_prepare_printer_data.return_value = PrinterData(
            state=PrinterStateChoices.RUNNING, chamber_image=test_image_1
        )
        DatabaseUpdater(with_image=True).run()

        self.assertEqual(Project.objects.count(), 1)

        project_first = Project.objects.first()
        self.assertEqual(project_first.status, ProjectStatusChoices.PRINTING)
        self.assertIsNotNone(project_first.image)
        self.assertEqual(project_first.image.name, "test_image_1.jpeg")
        # TODO: why image field none? not saved because of logic or issue with test?

        # before: running, now: failed
        mock_get_and_prepare_printer_data.return_value = PrinterData(
            state=PrinterStateChoices.FAILED,
            chamber_image=generate_test_image(image_name="test_image_2", color="#AAAAAA"),
        )
        DatabaseUpdater(with_image=True).run()

        latest_printer_data = PrinterData.objects.order_by("-created_at").first()

        self.assertEqual(PrinterData.objects.count(), 2)
        self.assertEqual(latest_printer_data.gcode_file_name, PrinterData.objects.first().gcode_file_name)
        self.assertEqual(Project.objects.count(), 1)
        self.assertIsNotNone(latest_printer_data.project)

        project_updated = Project.objects.first()
        self.assertEqual(project_updated.status, ProjectStatusChoices.UNKNOWN)
        self.assertIsNotNone(project_updated.image)
        self.assertNotEqual(project_first.image, project_updated.image)
        self.assertEqual(Project.objects.filter(image=F("test_image_1")).count(), 0)  # should be replaced

        # before: failed, now: running
        test_image_3 = generate_test_image(image_name="test_image_3", color="#ff0000")

        mock_get_and_prepare_printer_data.return_value = PrinterData(
            state=PrinterStateChoices.RUNNING, chamber_image=test_image_3
        )
        DatabaseUpdater(with_image=True).run()

        self.assertEqual(PrinterData.objects.count(), 3)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.filter(image=F("test_image_3")).count(), 1)

        # before: running, now: idle
        mock_get_and_prepare_printer_data.return_value = PrinterData(
            state=PrinterStateChoices.IDLE,
            chamber_image=generate_test_image(image_name="test_image_4", color="#0000ff"),
        )
        DatabaseUpdater(with_image=True).run()

        self.assertEqual(PrinterData.objects.count(), 4)
        self.assertEqual(Project.objects.count(), 2)

        project_idle = Project.objects.order_by("-created_at").first()

        self.assertEqual(project_idle.status, ProjectStatusChoices.PRINTING)
        self.assertEqual(project_idle.image.name, "test_image_3.jpeg")

        # before: idle, now: running
        mock_get_and_prepare_printer_data.return_value = PrinterData(
            state=PrinterStateChoices.RUNNING,
            chamber_image=generate_test_image(image_name="test_image_5", color="#00ff00"),
        )
        DatabaseUpdater(with_image=True).run()

        self.assertEqual(PrinterData.objects.count(), 5)
        self.assertEqual(Project.objects.count(), 3)
