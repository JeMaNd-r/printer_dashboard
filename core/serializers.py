from typing import Type

from rest_framework import serializers

from core.models import PrinterData, Project
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
    printer_states = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="core:printerdata-detail",
    )
    url = serializers.HyperlinkedIdentityField(
        view_name="core:project-detail",
        lookup_field="pk",
    )
    last_printer_state = serializers.SerializerMethodField()

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
            "printer_states",
            "last_printer_state",
        ]

    def get_last_printer_state(self, project):
        state = project.printer_states.order_by("-created_at", "-id").first()

        if state is None:
            return None

        return {
            "id": state.id,
            "state": state.state,
            "detailed_state": state.detailed_state,
            "detailed_state_label": state.get_detailed_state_display(),
            "created_at": state.created_at,
            "percentage": state.percentage,
        }


class PrinterDataSerializer(serializers.ModelSerializer):
    """
    Serializer for PrinterData model

    Extends rest_framework.serializers.ModelSerializer to include project.
    Project can be currently printing, finished or None.
    Project url leads to project detail view.
    In addition, provide URL linking to printer status detail view.
    """

    detailed_state_label = serializers.CharField(
        source="get_detailed_state_display",
        read_only=True,
    )

    project = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="core:project-detail",
    )

    url = serializers.HyperlinkedIdentityField(
        view_name="core:printerdata-detail",
        lookup_field="pk",
    )

    class Meta:
        model = PrinterData
        fields = [
            "url",
            "id",
            "state",
            "detailed_state",
            "detailed_state_label",
            "gcode_file_name",
            "source_type",
            "subtask_name",
            "current_layer_number",
            "total_layers",
            "created_at",
            "is_light_on",
            "wifi_signal_dbm",
            "percentage",
            "project",
            "temperature_nozzle",
            "temperature_bed",
            "temperature_chamber",
            "chamber_image",
        ]
