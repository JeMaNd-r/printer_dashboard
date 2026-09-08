from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def generate_test_image(
    width: int = 100,
    height: int = 100,
    format: str = "JPEG",
    mode: str = "RGB",
    color: str = "#FFFFFF",
    image_name: str = "test_image",
) -> SimpleUploadedFile:
    """
    Generate an in-memory image for testing.

    :param width: Image width in pixels.
    :param height: Image height in pixels.
    :param format: Image format (JPEG, PNG, etc.).
    :param mode: Image mode (RGB, RGBA, etc.).
    :param color: Background color (e.g., "#FFFFFF" for white).
    :param image_name: Name of the image file.

    :return: Django-compatible in-memory file
    :rtype: SimpleUploadedFile
    """

    image = Image.new(mode=mode, size=(width, height), color=color)
    buffer = BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)

    return SimpleUploadedFile(
        name=f"{image_name}.{format.lower()}", content=buffer.getvalue(), content_type=f"image/{format.lower()}"
    )
