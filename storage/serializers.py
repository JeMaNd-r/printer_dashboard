from rest_framework import serializers

from storage.models import PrinterStatus, Project
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
        ]


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True, default=None)

    url = serializers.HyperlinkedIdentityField(
        view_name="storage:project-detail",
        lookup_field="pk",
    )

    class Meta:
        model = Project
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
        ]


class PrinterStatusSerializer(serializers.ModelSerializer):
    project = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="storage:project-detail",
    )

    url = serializers.HyperlinkedIdentityField(
        view_name="storage:printerstatus-detail",
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
