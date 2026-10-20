"""Aplicación: un caso de uso por función. Orquesta permisos, dominio e infraestructura."""

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from .. import selectors
from ..domain import reglas
from ..domain.estados import EstadoInscripcion, validar_transicion
from ..domain.exceptions import (
    ActividadInactivaError,
    InscripcionDuplicadaError,
    LimiteCreditosError,
)
from ..models import Constancia, Inscripcion, RegistroCreditos
from ..signals import inscripcion_validada
from . import permisos


def inscribir(estudiante, actividad) -> Inscripcion:
    if not actividad.activa:
        raise ActividadInactivaError("Esta actividad ya no está activa.")
    try:
        with transaction.atomic():
            return Inscripcion.objects.create(estudiante=estudiante, actividad=actividad)
    except IntegrityError as e:
        raise InscripcionDuplicadaError("Ya estás inscrito en esta actividad.") from e


@transaction.atomic
def evaluar(inscripcion_id, usuario, aprobado: bool, observaciones: str = "") -> Inscripcion:
    inscripcion = (
        Inscripcion.objects.select_for_update().select_related("actividad").get(pk=inscripcion_id)
    )
    permisos.exigir_responsable(inscripcion.actividad, usuario)
    nuevo = (
        EstadoInscripcion.EVALUADO_APROBADO if aprobado else EstadoInscripcion.EVALUADO_RECHAZADO
    )
    validar_transicion(inscripcion.estado, nuevo)

    inscripcion.estado = nuevo
    inscripcion.fecha_evaluacion = timezone.now()
    inscripcion.observaciones = observaciones
    inscripcion.save(update_fields=["estado", "fecha_evaluacion", "observaciones"])
    return inscripcion


@transaction.atomic
def emitir_constancia(inscripcion_id, usuario) -> Constancia:
    inscripcion = (
        Inscripcion.objects.select_for_update().select_related("actividad").get(pk=inscripcion_id)
    )
    permisos.exigir_responsable(inscripcion.actividad, usuario)
    validar_transicion(inscripcion.estado, EstadoInscripcion.CONSTANCIA_EMITIDA)

    constancia = Constancia.objects.create(
        inscripcion=inscripcion,
        folio=reglas.generar_folio(inscripcion.id),
        emitida_por=usuario,
    )
    inscripcion.estado = EstadoInscripcion.CONSTANCIA_EMITIDA
    inscripcion.save(update_fields=["estado"])
    return constancia


@transaction.atomic
def validar_y_registrar(inscripcion_id, usuario) -> RegistroCreditos:
    permisos.exigir_permiso(usuario, permisos.PERMISO_VALIDAR)

    inscripcion = (
        Inscripcion.objects.select_for_update().select_related("actividad").get(pk=inscripcion_id)
    )
    # Bloquear al estudiante serializa validaciones simultáneas de sus inscripciones:
    # sin esto, dos validaciones a la vez leerían el mismo total y sobrepasarían el límite.
    get_user_model().objects.select_for_update().get(pk=inscripcion.estudiante_id)

    validar_transicion(inscripcion.estado, EstadoInscripcion.VALIDADO)
    if reglas.excede_limite(selectors.total_validado(inscripcion.estudiante)):
        raise LimiteCreditosError(
            f"El estudiante ya cubrió los {reglas.META_CREDITOS} créditos ACOM requeridos."
        )

    registro = RegistroCreditos.objects.create(
        inscripcion=inscripcion,
        creditos_otorgados=inscripcion.actividad.creditos_valor,
        validado_por=usuario,
    )
    inscripcion.estado = EstadoInscripcion.VALIDADO
    inscripcion.save(update_fields=["estado"])

    # Solo avisa si la transacción realmente se confirmó.
    transaction.on_commit(
        lambda: inscripcion_validada.send(sender=validar_y_registrar, inscripcion=inscripcion)
    )
    return registro
