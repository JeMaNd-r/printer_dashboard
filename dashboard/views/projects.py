from django.views import generic

from core.models import Project


class ProjectListView(generic.ListView):
    model = Project
    template_name = "dashboard/project_list.html"


class ProjectDetailView(generic.DetailView):
    model = Project
    template_name = "dashboard/project_detail.html"
