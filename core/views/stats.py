from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from core.filters import PrinterDataFilter
from core.models import PrinterData
from core.serializers import PrinterDataSerializer


class PrinterDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows printer states to be viewed.
    """

    queryset = PrinterData.objects.all()
    serializer_class = PrinterDataSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["state"]
    ordering_fields = ["state", "project_id", "created_at"]
    filterset_class = PrinterDataFilter
