import django_filters

from storage.models import PrinterStatus


class PrinterStatusFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name="created_at", lookup_expr="year")

    class Meta:
        model = PrinterStatus
        fields = ("created_at", "state")
