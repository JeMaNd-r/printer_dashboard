# Generated manually on 2026-07-28

from django.db import migrations

printer_states_conversion = {
    "Idle": 0,
    "Preparing": 10,
    "Running": 20,
    "Paused": 30,
    "Finished": 40,
    "Unknown": 50,
    "Failed": 60,
}


def forwards(apps, schema_editor):
    """Replace printer states strings with associated integer values"""

    printer_data_model = apps.get_model("core", "PrinterData")

    for printer_data in printer_data_model.objects.all():
        printer_data.state_new = printer_states_conversion[printer_data.state.capitalize()]
        printer_data.save()


def backwards(apps, schema_editor):
    """Replace printer states integers with associated strings"""

    backward_conversion = {v: k for k, v in printer_states_conversion.items()}
    printer_data_model = apps.get_model("core", "PrinterData")

    for printer_data in printer_data_model.objects.all():
        printer_data.state = backward_conversion[printer_data.state_new].upper()
        printer_data.save()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_add_new_printerdata_state"),
    ]

    operations = [
        migrations.RunPython(code=forwards, reverse_code=backwards),
    ]
