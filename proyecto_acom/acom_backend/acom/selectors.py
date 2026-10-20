"""Infraestructura: todas las lecturas. Las vistas y servicios no arman consultas."""

from decimal import Decimal

from django.db.models import Sum

from .models import ActividadComplementaria, Inscripcion, RegistroCreditos


def actividades_activas():
    return ActividadComplementaria.objects.filter(activa=True)


def inscripciones_de(estudiante):
    return Inscripcion.objects.filter(estudiante=estudiante).select_related("actividad")


def inscripcion_de_responsable(inscripcion_id, responsable):
    """None si la inscripción no existe o la actividad no es de este responsable."""
    return (
        Inscripcion.objects.select_related("estudiante", "actividad")
        .filter(pk=inscripcion_id, actividad__responsable=responsable)
        .first()
    )


def inscripcion_por_id(inscripcion_id):
    return (
        Inscripcion.objects.select_related("estudiante", "actividad")
        .filter(pk=inscripcion_id)
        .first()
    )


def total_validado(estudiante) -> Decimal:
    total = RegistroCreditos.objects.filter(inscripcion__estudiante=estudiante).aggregate(
        total=Sum("creditos_otorgados")
    )["total"]
    return Decimal(total or 0).quantize(Decimal("0.01"))
