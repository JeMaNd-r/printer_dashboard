from datetime import UTC, datetime
from typing import Type

import factory
import factory.fuzzy
from factory import post_generation

from core.models import PrinterStatus, Project, StatusChoices, User

PRINTER_STATE_CHOICES: list[str] = [
    "IDLE",
    "PREPARING",
    "RUNNING",
    "PAUSED",
    "FINISHED",
    "UNKNOWN",
    "FAILED",
]


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for User

    Automatically creates User with firstname, lastname, email and password.

    :return : User
    """

    class Meta:
        model: Type[User] = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    password = factory.Faker("password")


class ProjectFactory(factory.django.DjangoModelFactory):
    """
    Factory for Project

    Automatically creates Project with name, description and status.
    Creation date is randomly generated. Owner is taken from UserFactory.

    :return : Project
    """

    project_name = factory.Faker("sentence")
    project_description = factory.Faker("text")
    owner = factory.SubFactory(UserFactory)
    is_created_manually = factory.fuzzy.FuzzyChoice([True, False])
    status = factory.fuzzy.FuzzyChoice(StatusChoices.values)

    class Meta:
        model: Type[Project] = Project

    @post_generation
    def post(self, create, extracted, **kwargs) -> None:
        self.created_at = factory.fuzzy.FuzzyDateTime(datetime(2020, 1, 2, tzinfo=UTC)).evaluate(2, None, {})
        self.save(update_fields=["created_at"])


class PrinterStatusFactory(factory.django.DjangoModelFactory):
    """
    Factory for PrinterStatus

    Automatically creates PrinterStatus with state, is_light_on and project.

    :return : PrinterStatus
    """

    class Meta:
        model: Type[PrinterStatus] = PrinterStatus

    project = factory.SubFactory(ProjectFactory)
    state = factory.fuzzy.FuzzyChoice(PRINTER_STATE_CHOICES)
    is_light_on = factory.fuzzy.FuzzyChoice([True, False])
