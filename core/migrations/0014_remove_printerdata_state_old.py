# Generated manually on 2026-07-28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_add_data_to_new_printerdata_state"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="printerdata",
            name="state",
        ),
    ]
