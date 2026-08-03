# Generated manually on 2026-07-28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_alter_printerdata_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="printerdata",
            name="state_new",
            field=models.IntegerField(
                choices=[
                    (0, "Idle"),
                    (10, "Preparing"),
                    (20, "Running"),
                    (30, "Paused"),
                    (40, "Finished"),
                    (50, "Unknown"),
                    (60, "Failed"),
                ],
                default=50,
            ),
        ),
    ]
