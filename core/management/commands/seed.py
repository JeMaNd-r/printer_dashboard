import random

from django.core.management.base import BaseCommand

from core.factories import PrinterDataFactory, ProjectFactory
from core.models import PrinterStateChoices


class Command(BaseCommand):
    help = "seed database"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")
        self._run_seed()
        self.stdout.write("Done")

    def _run_seed(self):
        """
        Seed database with printer statuses, projects and users

        :return: Nothing
        """
        state_sequences = [
            [
                PrinterStateChoices.PREPARING,
                PrinterStateChoices.RUNNING,
                PrinterStateChoices.RUNNING,
                PrinterStateChoices.PAUSED,
                PrinterStateChoices.FINISHED,
            ],
            [],
            [
                PrinterStateChoices.PREPARING,
                PrinterStateChoices.PAUSED,
                PrinterStateChoices.FINISHED,
            ],
            [
                PrinterStateChoices.PREPARING,
                PrinterStateChoices.RUNNING,
                PrinterStateChoices.FAILED,
            ],
        ]

        for _ in range(1, 10):
            project = ProjectFactory()
            state_sequence = random.choices(
                state_sequences,
                weights=[6, 1, 2, 1],
                k=1,
            )[0]

            for state in state_sequence:
                PrinterDataFactory(project=project, state=state)
