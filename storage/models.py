from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class StatusChoices(models.IntegerChoices):
    """
    Define valid project status choices as Enum.
    """

    UNKNOWN = 0
    NOT_SCHEDULED = 10
    IN_WAITING_LIST = 20
    PRINTING = 30
    DONE = 40


class Project(models.Model):
    """
    Printing projects provided to the 3D printer

    Projects should get a name and be linked to a User.
    """

    project_name = models.CharField(max_length=255)
    project_description = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    is_created_manually = models.BooleanField(default=True)  # manually or using API
    status = models.IntegerField(choices=StatusChoices, default=StatusChoices.UNKNOWN)

    def __str__(self) -> str:
        return f"{self.project_name} from User ID {self.owner_id}"


class PrinterStatus(models.Model):
    """
    Printer statuses retrieved from the 3D printer
    """

    state = models.CharField(max_length=255)
    is_printing = models.BooleanField(default=False)
    project = models.ForeignKey(Project, null=True, on_delete=models.SET_NULL, related_name="printer_statuses")
    print_percentage = models.IntegerField(null=True)  # if "Unknown" or None returned by printer.: save as null
    created_at = models.DateTimeField(auto_now_add=True)
    is_light_on = models.BooleanField(default=False)
    wifi_signal_dbm = models.IntegerField(null=True)
    temperature_nozzle = models.FloatField(null=True)
    temperature_bed = models.FloatField(null=True)
    temperature_chamber = models.FloatField(null=True)
    fan_speed_chamber = models.IntegerField(null=True, validators=[MaxValueValidator(255), MinValueValidator(0)])
    fan_speed_aux = models.IntegerField(null=True, validators=[MaxValueValidator(255), MinValueValidator(0)])
    chamber_image = models.ImageField(upload_to="storage/chamber-images/", null=True)

    def __str__(self) -> str:
        return f"{self.state} at {self.created_at}"
