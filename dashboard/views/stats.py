from django.views import generic

from core.models import PrinterData


class PrinterDataListView(generic.ListView):
    model = PrinterData
    template_name = "dashboard/printerdata_list.html"

    queryset = PrinterData.objects.order_by("-created_at")
