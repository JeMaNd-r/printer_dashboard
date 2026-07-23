from typing import Type

import django_filters

from core.models import PrinterData


class PrinterDataFilter(django_filters.FilterSet):
    """
    Filter for PrinterData including year (taken from created_at)
    """

    year = django_filters.NumberFilter(field_name="created_at", lookup_expr="year")
    """Extend created_at filter to filter by year"""

    class Meta:
        model: Type[PrinterData] = PrinterData
        fields = ("created_at", "state", "detailed_state")
