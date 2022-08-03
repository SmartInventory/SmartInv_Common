from django.http import Http404
from django.core.exceptions import PermissionDenied
from rest_framework import exceptions, status, serializers
from rest_framework.views import set_rollback, Response


def custom_exception_handler(exc, context):
    error = None
    data = None
    status_code = 512
    if "view" in context:
        error = f"error.{context['view'].basename}."
        if exc:
            error = error + str(type(exc).__name__).lower()

            if isinstance(exc, serializers.ValidationError):
                if "error" in exc.detail and len(exc.detail["error"]):
                    if isinstance(exc.detail["error"], str):
                        error = exc.detail["error"]
                    elif isinstance(exc.detail["error"], list):
                        error = exc.detail["error"][0]
            status_code = status.HTTP_400_BAD_REQUEST
            data = str(exc)
        else:
            error = error + "unknown"

    if isinstance(exc, Http404):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, PermissionDenied):
        status_code = status.HTTP_403_FORBIDDEN
    if isinstance(exc, exceptions.APIException):
        if isinstance(exc.detail, (list, dict)):
            data = exc.detail

    formatted_error = {"error": error or "error.system.unknown", "detail": data, "status_code": status_code}

    set_rollback()

    return Response(formatted_error, status=status_code)
