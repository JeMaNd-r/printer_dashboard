# Third Party Packages
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler


def handle(exc, ctx):
    """
    This is a custom exception handler for our APIs.
    cf. https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling
    """
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if ctx["request"].accepted_renderer.format != "json":
        ctx["request"].accepted_renderer = JSONRenderer()
    response = exception_handler(exc, ctx)

    # If unexpected error occurs (server error, etc.)
    if response is None:
        return response

    if isinstance(exc.detail, (list, dict)):
        response.data = {"detail": response.data}

    return response
