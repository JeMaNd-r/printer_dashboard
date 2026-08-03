# Generated manually on 2026-07-28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0014_remove_printerdata_state_old"),
    ]

    operations = [
        migrations.RenameField(
            model_name="printerdata",
            old_name="state_new",
            new_name="state",
        ),
    ]
