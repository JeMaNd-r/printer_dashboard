from typing import Optional

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import FormView
from django_q.models import Schedule

from core.schedules import retrieve_printer_data_once, retrieve_printer_data_regularly, stop_retrieving_printer_data
from dashboard.forms import PrinterDataForm
from printer_api import script


class DashboardView(FormView):
    """A base view for displaying printer status with an "update" button."""

    form_class = PrinterDataForm
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        is_running_regularly: Optional[bool] = Schedule.objects.filter(name="Printer data retrieval regularly").exists()
        return {**data, "is_running_regularly": is_running_regularly}

    def post(self, request, *args, **kwargs):
        is_running_once: Optional[bool] = False

        if "light-off" in request.POST:
            script.switch_light(turn_on=False)
            return HttpResponseRedirect(reverse("dashboard:project-list"))

        if "retrieve-printer-data-once" in request.POST:
            retrieve_printer_data_once()
            is_running_once = True

        elif "retrieve-printer-data-regularly" in request.POST:
            retrieve_printer_data_regularly()

        elif "stop-retrieving-printer-data" in request.POST:
            stop_retrieving_printer_data()

        context = {
            "is_running_once": is_running_once,
        }

        context = {**self.get_context_data(), **context}

        return render(request, "dashboard/dashboard.html", context=context)
