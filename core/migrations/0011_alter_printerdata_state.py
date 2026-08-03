# Generated manually on 2026-07-28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_alter_printerdata_state"),
    ]

    operations = [
        migrations.AlterField(
            model_name="printerdata",
            name="state",
            field=models.CharField(max_length=255),
        ),
    ]
