from printer_api.api import PrinterBambuP1S

with PrinterBambuP1S() as printer:
    data = printer.get_all_infos()
    image = printer.get_camera_image()

    print(data)
    image.save("chamber-images/test.png")
