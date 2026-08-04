from bambulabs_api import PrintStatus
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User


class ProjectStatusChoices(models.IntegerChoices):
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
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    is_created_manually = models.BooleanField(default=True)  # manually or using API
    status = models.IntegerField(choices=ProjectStatusChoices, default=ProjectStatusChoices.UNKNOWN)

    image = models.ImageField(upload_to="core/projects/", null=True)

    def __str__(self) -> str:
        return f"{self.project_name} from User ID {self.owner_id}"


# PrintState from bambulab_api contains None for UNKNOWN instead of integer, therefore re-define necessary.
DETAILED_STATE_CHOICES = [(m.value, m.name.title()) for m in PrintStatus if m.value is not None] + [(40, "Unknown")]


class PrinterStateChoices(models.IntegerChoices):
    """
    Define valid printing status choices as Enum.

    GcodeState Enum from bambulab_api contains str, not int. Therefore, define Enum with values instead.
    """

    IDLE = 0, _("Idle")
    PREPARING = 10, _("Preparing")
    RUNNING = 20, _("Running")
    PAUSED = 30, _("Paused")
    FINISHED = 40, _("Finished")
    UNKNOWN = 50, _("Unknown")
    FAILED = 60, _("Failed")


class PrinterData(models.Model):
    """
    Printer statuses retrieved from the 3D printer

    Note: Printer state refers to the state of the printer while
    detailed status refers to the current print (project).
    """

    state = models.IntegerField(choices=PrinterStateChoices, default=PrinterStateChoices.UNKNOWN)  # gcode state

    # Project related data
    detailed_state = models.IntegerField(choices=DETAILED_STATE_CHOICES, default=None, null=True)
    percentage = models.IntegerField(null=True)  # if "Unknown" or None returned by printer.: save as null
    gcode_file_name = models.CharField(max_length=255, null=True)
    source_type = models.CharField(max_length=255, null=True)
    subtask_name = models.CharField(max_length=255, null=True)  # could be same as gcode file name without extension
    current_layer_number = models.IntegerField(null=True)
    total_layers = models.IntegerField(null=True)

    is_light_on = models.BooleanField(default=False)

    wifi_signal_dbm = models.IntegerField(null=True)
    temperature_nozzle = models.FloatField(null=True)
    temperature_bed = models.FloatField(null=True)
    temperature_chamber = models.FloatField(null=True)

    chamber_image = models.ImageField(upload_to="core/chamber-images/", null=True)

    project = models.ForeignKey(Project, null=True, on_delete=models.SET_NULL, related_name="printer_states")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.state} at {self.created_at}"
