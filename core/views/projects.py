from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from core.models import Project
from core.serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["project_name", "owner__username", "=owner__first_name", "=owner__last_name"]
    ordering_fields = ["project_name", "owner__username", "created_at", "updated_at"]
    filterset_fields = ["status"]
    ordering = "-updated_at"
