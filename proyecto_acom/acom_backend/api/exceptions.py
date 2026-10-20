"""Traduce errores del dominio (acom.domain.exceptions) a respuestas HTTP.

Las vistas de la API nunca inspeccionan estas excepciones directamente: las
dejan subir, y este handler central decide el código de estado — el mismo
principio de "un solo lugar" que ya usa acom.services.permisos.
"""

from rest_framework.response import Response
from rest_framework.views import exception_handler

from acom.domain.exceptions import AcomError, PermisoDenegadoError


def acom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, PermisoDenegadoError):
        return Response({"detail": str(exc)}, status=403)

    if isinstance(exc, AcomError):
        return Response({"detail": str(exc)}, status=400)

    return None
