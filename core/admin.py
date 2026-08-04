from django.contrib import admin
from django.utils.html import format_html

from core.models import PrinterData, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    date_hierarchy = "updated_at"
    list_display = ["id", "status", "project_name", "created_at", "updated_at", "owner_id"]


@admin.register(PrinterData)
class PrinterDataAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = [
        "id",
        "state",
        "detailed_state",
        "is_light_on",
        "project_id",
        "percentage",
        "image_display",
        "created_at",
    ]

    @admin.display
    def image_display(self, obj):
        if obj.chamber_image:
            return format_html(
                "<img src='{}' height='20' />",
                obj.chamber_image.url,
            )
        return None
