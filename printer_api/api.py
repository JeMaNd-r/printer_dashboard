import time

import bambulabs_api
from django.conf import settings
from PIL import Image


class PrinterBambuP1S:
    """Retrieve data from a specified printer"""

    def __init__(
        self, ip_address: str | None = None, access_code: str | None = None, serial: str | None = None
    ) -> None:
        ip_address = ip_address or settings.PRINTER_IP_ADDRESS
        access_code = access_code or settings.PRINTER_ACCESS_CODE
        serial = serial or settings.PRINTER_SERIAL

        if ip_address is None or access_code is None or serial is None:
            raise ValueError("Printer connection variables are None. Set them in settings or .env.")

        self.printer = bambulabs_api.Printer(ip_address, access_code, serial)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return

    def _check_printer_connection(self) -> None:
        """
        Check if printer is ready to send data.

        As long as printer state is UNKNOWN, no further data can be retrieved.
        After 1-3 attempts, a different state should be retrieved and further data can be requested.
        """

        attempts = 0
        max_attempts = 5

        while attempts < max_attempts:
            attempts += 1
            status = self.printer.get_state()
            print(f"Printer status: {status} (Attempt #{attempts})\n")
            if status != "UNKNOWN":
                break
            time.sleep(2)

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

    def get_all_infos(self) -> dict:
        """Retrieve data from printer."""

        self._check_printer_connection()

        return {
            "printer_state": self.printer.get_state(),
            "printer_current_state": self.printer.get_current_state(),
            "wifi_signal": self.printer.wifi_signal(),
            "light_state": self.printer.get_light_state(),
            "print_percentage": self.printer.get_percentage(),
            "print_gcode_file": self.printer.gcode_file(),
            "print_type": self.printer.print_type(),
            "temperature_bed": self.printer.get_bed_temperature(),
            "temperature_nozzle": self.printer.get_nozzle_temperature(),
            "temperature_chamber": self.printer.get_chamber_temperature(),
        }

    def get_camera_image(self) -> Image.Image:
        """Retrieve camera image from printer."""

        return self.printer.get_camera_image()
