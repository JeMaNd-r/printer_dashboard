from django.urls import include, path
from rest_framework.routers import SimpleRouter

from storage.views.projects import ProjectViewSet
from storage.views.stats import PrinterStatusViewSet

app_name = "storage"

router = SimpleRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"stats", PrinterStatusViewSet)


urlpatterns = [path("", include(router.urls))]
