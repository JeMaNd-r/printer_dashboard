from typing import Type

from rest_framework import serializers

from core.models import PrinterStatus, Project
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[User] = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
        ]


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model

    Extends rest_framework.serializers.ModelSerializer to include owner and printer statuses
    that are linked to the respective project ID.
    In addition, provide URL linking to project detail view.
    Note: because project and printer status are related, printer state urls are provided
    and link to printer status detail view.
    """

    owner = UserSerializer(read_only=True, default=None)
    printer_statuses = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="core:printerstatus-detail",
    )
    url = serializers.HyperlinkedIdentityField(
        view_name="core:project-detail",
        lookup_field="pk",
    )

    class Meta:
        model: Type[Project] = Project
        fields = [
            "url",
            "id",
            "project_name",
            "project_description",
            "created_at",
            "updated_at",
            "status",
            "is_created_manually",
            "owner",
            "printer_statuses",
        ]


class PrinterStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for PrinterStatus model

    Extends rest_framework.serializers.ModelSerializer to include project.
    Project can be currently printing, finished or None.
    Project url leads to project detail view.
    In addition, provide URL linking to printer status detail view.
    """

    project = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="core:project-detail",
    )

    url = serializers.HyperlinkedIdentityField(
        view_name="core:printerstatus-detail",
        lookup_field="pk",
    )

    class Meta:
        model = PrinterStatus
        fields = [
            "url",
            "id",
            "state",
            "created_at",
            "is_printing",
            "is_light_on",
            "print_percentage",
            "project",
            "temperature_nozzle",
        ]
