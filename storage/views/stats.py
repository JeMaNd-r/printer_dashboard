from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from storage.filters import PrinterStatusFilter
from storage.models import PrinterStatus
from storage.serializers import PrinterStatusSerializer


class PrinterStatusViewSet(viewsets.ModelViewSet):
    """
    Viewset for viewing and editing printer statuus.
    """

    queryset = PrinterStatus.objects.all()
    serializer_class = PrinterStatusSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["state"]
    ordering_fields = ["state", "project_id", "created_at"]
    filterset_class = PrinterStatusFilter
