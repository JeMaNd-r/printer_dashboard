from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView

from core import data_updater
from dashboard.forms import PrinterDataForm
from printer_api import script


class DashboardView(FormView):
    """A base view for displaying printer status with an "update" button."""

    form_class = PrinterDataForm
    template_name = "dashboard/dashboard.html"

    def post(self, request, *args, **kwargs):
        if "update" in request.POST:
            data_updater.get_and_save_to_db(with_image=False)
            return HttpResponseRedirect(reverse("dashboard:stats"))

        if "light-off" in request.POST:
            script.switch_light(turn_on=False)
            return HttpResponseRedirect(reverse("dashboard:project-list"))

        return None
