import time
from typing import Any, Optional

import bambulabs_api
from django.conf import settings
from PIL import Image


class PrinterBambuP1S:
    """Retrieve data from a specified printer"""

    def __init__(
        self, ip_address: Optional[str] = None, access_code: Optional[str] = None, serial: Optional[str] = None
    ) -> None:
        """Connect to printer clients: MQTT, camera and FTP client"""
        ip_address = ip_address or settings.PRINTER_IP_ADDRESS
        access_code = access_code or settings.PRINTER_ACCESS_CODE
        serial = serial or settings.PRINTER_SERIAL

        if ip_address is None:
            raise ValueError("Printer connection variables are None. Set them in settings or .env.")
        if access_code is None:
            raise ValueError("Printer connection variables are None. Set them in settings or .env.")
        if serial is None:
            raise ValueError("Printer connection variables are None. Set them in settings or .env.")

        self.printer = bambulabs_api.Printer(ip_address, access_code, serial)

    def __enter__(self):
        self.connect()
        self._check_printer_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return

    def _check_printer_connection(self) -> None:
        """
        Check if printer is ready to send data.

        As long as printer state is UNKNOWN, no further data can be retrieved.
        Usually, after 1-3 attempts, a different state should be retrieved and further data can be requested.
        """

        time.sleep(5)

        attempts: int = 0
        max_attempts: int = 5

        while attempts < max_attempts:
            attempts += 1
            status = self.printer.get_state()
            print(f"Printer status: {status} (Attempt #{attempts})\n")
            if status != "UNKNOWN":
                break
            time.sleep(1)
        else:
            raise ValueError(f"Printer not available. Tried to get printer state {max_attempts} times.")

    def connect(self) -> None:
        """Connect to printer."""

        print("Connecting to printer...")
        self.printer.connect()
        print("Successfully connected to printer.")

    def disconnect(self) -> None:
        """Disconnect from printer."""

        print("Disconnecting from printer...")
        self.printer.disconnect()
        print("Successfully disconnected from printer.")

    def get_all_infos(self) -> dict[str, Any]:
        """Retrieve data from printer."""

        # WiFi signal will be returned as string with dBm and can be empty
        wifi_signal: Optional[str] = self.printer.wifi_signal()

        return {
            "state": self.printer.get_state(),  # also called GcodeState
            "detailed_state": self.printer.get_current_state().value,  # also called PrintStatus
            "wifi_signal_dbm": int(wifi_signal.replace("dBm", "")) if wifi_signal else None,
            "light_state": self.printer.get_light_state(),
            "percentage": self.printer.get_percentage(),
            "gcode_file_name": self.printer.gcode_file(),
            "source_type": self.printer.print_type(),
            "subtask_name": self.printer.subtask_name(),
            "current_layer_number": self.printer.current_layer_num(),
            "total_layers": self.printer.total_layer_num(),
            "temperature_bed": self.printer.get_bed_temperature(),
            "temperature_nozzle": self.printer.get_nozzle_temperature(),
            "temperature_chamber": self.printer.get_chamber_temperature(),
        }

    def get_camera_image(self) -> Image.Image:
        """Retrieve camera image from printer."""

        return self.printer.get_camera_image()

    def turn_light_on(self) -> bool:
        """Switch light of the printer on."""

        return self.printer.turn_light_on()

    def turn_light_off(self) -> bool:
        """Turn light of the printer off."""

        return self.printer.turn_light_off()
