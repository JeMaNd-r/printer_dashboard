from django import forms

from core.models import PrinterStatus


class PrinterStatusForm(forms.Form):
    """A form for displaying printer status."""

    model = PrinterStatus
