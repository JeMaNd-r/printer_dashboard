from django.urls import include, path
from rest_framework.routers import SimpleRouter

from core.views.projects import ProjectViewSet
from core.views.stats import PrinterStatusViewSet

app_name = "core"

router = SimpleRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"stats", PrinterStatusViewSet)


urlpatterns = [path("", include(router.urls))]
