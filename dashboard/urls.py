from django.urls import path

from dashboard.views import dashboard, projects, stats

app_name = "dashboard"
urlpatterns = [
    path("", dashboard.DashboardView.as_view(), name="dashboard"),
    path("projects/", projects.ProjectListView.as_view(), name="project-list"),
    path("projects/<int:pk>/", projects.ProjectDetailView.as_view(), name="project-detail"),
    path("stats/", stats.PrinterDataListView.as_view(), name="stats"),
]
