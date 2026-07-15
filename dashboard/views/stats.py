from django.views import generic

from storage.models import PrinterStatus


class PrinterStatusListView(generic.ListView):
    model = PrinterStatus
    template_name = "dashboard/printerstatus_list.html"
