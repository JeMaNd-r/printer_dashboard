from django import forms

from core.models import PrinterData


class PrinterDataForm(forms.Form):
    """A form for displaying printer status."""

    model = PrinterData
