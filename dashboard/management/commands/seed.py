from django.core.management.base import BaseCommand

from core.factories import PrinterStatusFactory, ProjectFactory, UserFactory


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
        for i in range(1, 10):
            UserFactory()
            ProjectFactory()
            PrinterStatusFactory()
