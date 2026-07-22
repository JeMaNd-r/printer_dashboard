"""Playground for new features of communication with printer api"""

from printer_api.api import PrinterBambuP1S


def switch_light(turn_on: bool = False):
    """
    Turn light of the printer on or off

    :param turn_on: Should the light be turned on
    :return: None
    """

    with PrinterBambuP1S() as printer:
        if turn_on:
            response = printer.turn_light_on()

        else:
            response = printer.turn_light_off()

        if response:
            print(f"Printer light state was switched {'on' if turn_on else 'off'}.")
        else:
            print("Printer light state could not be switched.")
