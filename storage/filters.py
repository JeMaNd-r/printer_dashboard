from typing import Type

import django_filters

from storage.models import PrinterStatus


class PrinterStatusFilter(django_filters.FilterSet):
    """
    Filter for PrinterStatus including year (taken from created_at)
    """

    year = django_filters.NumberFilter(field_name="created_at", lookup_expr="year")
    """Extend created_at filter to filter by year"""

    class Meta:
        model: Type[PrinterStatus] = PrinterStatus
        fields = ("created_at", "state")
