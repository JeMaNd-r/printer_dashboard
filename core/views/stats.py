from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from core.filters import PrinterStatusFilter
from core.models import PrinterStatus
from core.serializers import PrinterStatusSerializer


class PrinterStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows printer states to be viewed.
    """

    queryset = PrinterStatus.objects.all()
    serializer_class = PrinterStatusSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["state"]
    ordering_fields = ["state", "project_id", "created_at"]
    filterset_class = PrinterStatusFilter
