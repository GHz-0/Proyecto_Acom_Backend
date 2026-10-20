"""Presentación de la API: parsea la petición, llama a acom.services, serializa la respuesta.

Mismo principio que acom/views/*.py — esta capa NO contiene reglas de negocio,
solo traduce HTTP <-> servicios. La autorización por rol (responsable,
departamento) ya la hace acom.services.permisos; aquí solo se repite el check
de "permiso de Django" cuando conviene devolver un 403 sin tocar la base de
datos primero.
"""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from acom import selectors
from acom.domain import reglas
from acom.models import ActividadComplementaria
from acom.services import inscripciones

from .serializers import (
    ActividadComplementariaSerializer,
    ConstanciaSerializer,
    EvaluarInscripcionSerializer,
    InscripcionListaSerializer,
    InscripcionSerializer,
    RegistroCreditosSerializer,
    ResumenCreditosSerializer,
)


class PuedeValidarCreditos(permissions.BasePermission):
    """Refleja el permiso de Django 'acom.can_validate_credits' (departamento académico)."""

    def has_permission(self, request, view):
        return request.user.has_perm("acom.can_validate_credits")


@extend_schema(tags=["Actividades"])
class ActividadListView(APIView):
    """Catálogo de actividades complementarias activas, abiertas a inscripción."""

    @extend_schema(responses=ActividadComplementariaSerializer(many=True))
    def get(self, request):
        actividades = selectors.actividades_activas()
        return Response(ActividadComplementariaSerializer(actividades, many=True).data)


@extend_schema(tags=["Estudiante"])
class InscribirseView(APIView):
    """El estudiante autenticado se inscribe a una actividad activa."""

    @extend_schema(
        request=None,
        responses={
            201: InscripcionSerializer,
            400: OpenApiResponse(description="Actividad inactiva o ya inscrito"),
        },
    )
    def post(self, request, actividad_id):
        actividad = get_object_or_404(ActividadComplementaria, pk=actividad_id)
        inscripcion = inscripciones.inscribir(request.user, actividad)
        return Response(InscripcionSerializer(inscripcion).data, status=201)


@extend_schema(tags=["Estudiante"])
class MisInscripcionesView(APIView):
    """Inscripciones del estudiante autenticado, con su resumen de créditos ACOM."""

    @extend_schema(responses=InscripcionListaSerializer(many=True))
    def get(self, request):
        inscripciones_qs = selectors.inscripciones_de(request.user)
        return Response(InscripcionListaSerializer(inscripciones_qs, many=True).data)


@extend_schema(tags=["Estudiante"])
class ResumenCreditosView(APIView):
    """Créditos ACOM validados y faltantes para el estudiante autenticado."""

    @extend_schema(responses=ResumenCreditosSerializer)
    def get(self, request):
        total = selectors.total_validado(request.user)
        data = {"creditos_totales": total, "creditos_faltantes": reglas.faltantes(total)}
        return Response(ResumenCreditosSerializer(data).data)


@extend_schema(tags=["Responsable"])
class InscripcionResponsableView(APIView):
    """Detalle de una inscripción, visible solo para el responsable de esa actividad."""

    @extend_schema(responses=InscripcionSerializer)
    def get(self, request, inscripcion_id):
        inscripcion = selectors.inscripcion_de_responsable(inscripcion_id, request.user)
        if inscripcion is None:
            return Response({"detail": "No encontrada."}, status=404)
        return Response(InscripcionSerializer(inscripcion).data)


@extend_schema(tags=["Responsable"])
class EvaluarInscripcionView(APIView):
    """El responsable de la actividad aprueba o rechaza la inscripción."""

    @extend_schema(
        request=EvaluarInscripcionSerializer,
        responses={
            200: InscripcionSerializer,
            403: OpenApiResponse(description="No eres el responsable"),
        },
    )
    def post(self, request, inscripcion_id):
        datos = EvaluarInscripcionSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        inscripcion = inscripciones.evaluar(
            inscripcion_id,
            request.user,
            aprobado=datos.validated_data["aprobado"],
            observaciones=datos.validated_data["observaciones"],
        )
        return Response(InscripcionSerializer(inscripcion).data)


@extend_schema(tags=["Responsable"])
class EmitirConstanciaView(APIView):
    """El responsable emite la constancia de una inscripción ya evaluada y aprobada."""

    @extend_schema(request=None, responses={201: ConstanciaSerializer})
    def post(self, request, inscripcion_id):
        constancia = inscripciones.emitir_constancia(inscripcion_id, request.user)
        return Response(ConstanciaSerializer(constancia).data, status=201)


@extend_schema(tags=["Departamento académico"])
class ValidarCreditosView(APIView):
    """El departamento académico valida la constancia y registra los créditos otorgados."""

    permission_classes = [permissions.IsAuthenticated, PuedeValidarCreditos]

    @extend_schema(
        request=None,
        responses={
            201: RegistroCreditosSerializer,
            400: OpenApiResponse(
                description="Ya alcanzó el límite de créditos, o transición inválida"
            ),
        },
    )
    def post(self, request, inscripcion_id):
        registro = inscripciones.validar_y_registrar(inscripcion_id, request.user)
        return Response(RegistroCreditosSerializer(registro).data, status=201)
