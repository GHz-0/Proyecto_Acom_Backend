"""Reglas de negocio puras: reciben valores y devuelven valores, sin ORM."""

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
