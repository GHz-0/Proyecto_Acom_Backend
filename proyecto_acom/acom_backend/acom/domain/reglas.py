"""Reglas de negocio puras: reciben valores y devuelven valores, sin ORM."""

from datetime import date
from decimal import Decimal

META_CREDITOS = Decimal("5.00")


def excede_limite(creditos_actuales: Decimal) -> bool:
    return creditos_actuales >= META_CREDITOS


def faltantes(creditos_actuales: Decimal) -> Decimal:
    return max(Decimal(0), META_CREDITOS - creditos_actuales)


def es_responsable(responsable_id: int, usuario_id: int) -> bool:
    return responsable_id == usuario_id


def generar_folio(inscripcion_id: int) -> str:
    return f"ACOM-{inscripcion_id:06d}"


def inscripcion_abierta(hoy: date, abre: date | None, cierra: date | None) -> bool:
    """¿Se puede inscribir alguien en la fecha `hoy`?

    La ventana es inclusiva en ambos extremos. Una fecha ausente (`None`) significa
    «sin límite» de ese lado, así que sin ninguna fecha la inscripción siempre está
    abierta: las actividades anteriores a los periodos escolares siguen funcionando.

    `hoy` llega siempre como parámetro; el dominio nunca consulta el reloj real.
    """
    if abre is not None and hoy < abre:
        return False
    if cierra is not None and hoy > cierra:
        return False
    return True
