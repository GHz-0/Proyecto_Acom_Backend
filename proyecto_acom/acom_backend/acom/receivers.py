import logging

from django.dispatch import receiver

from .signals import inscripcion_validada

logger = logging.getLogger(__name__)


@receiver(inscripcion_validada)
def notificar_creditos_registrados(sender, inscripcion, **kwargs):
    logger.info(
        "Créditos registrados: %s ganó %s créditos por '%s'",
        inscripcion.estudiante,
        inscripcion.actividad.creditos_valor,
        inscripcion.actividad.nombre,
    )
