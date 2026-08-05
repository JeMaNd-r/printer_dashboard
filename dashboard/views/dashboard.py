from typing import Optional

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import FormView
from django_q.models import Schedule

from core.models import DETAILED_STATE_CHOICES, PrinterData, PrinterStateChoices
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

        latest_printer_data = PrinterData.objects.order_by("created_at").last()
        is_light_on: Optional[bool] = latest_printer_data.is_light_on
        printer_data: Optional[PrinterData] = latest_printer_data
        if (
            printer_data.temperature_chamber > 30
            or printer_data.temperature_bed > 30
            or printer_data.temperature_nozzle > 30
        ):
            is_hot = True
        else:
            is_hot = False

        context = {
            "is_running_regularly": is_running_regularly,
            "is_light_on": is_light_on,
            "is_hot": is_hot,
            "printer_data": {
                "state": PrinterStateChoices(printer_data.state).label,
                "detailed_state": dict(DETAILED_STATE_CHOICES).get(printer_data.detailed_state),
                "created_at": printer_data.created_at,
                "temperature_nozzle": printer_data.temperature_nozzle,
                "temperature_bed": printer_data.temperature_bed,
                "temperature_chamber": printer_data.temperature_chamber,
            },
        }
        return {**data, **context}

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
