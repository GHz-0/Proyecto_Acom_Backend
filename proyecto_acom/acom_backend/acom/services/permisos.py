"""Aplicación: quién puede ejecutar cada caso de uso. Un solo lugar para autorizar."""

from ..domain import reglas
from ..domain.exceptions import PermisoDenegadoError

PERMISO_VALIDAR = "acom.can_validate_credits"


def exigir_permiso(usuario, permiso: str) -> None:
    if not usuario.has_perm(permiso):
        raise PermisoDenegadoError("No tienes permiso para realizar esta acción.")


def exigir_responsable(actividad, usuario) -> None:
    if not reglas.es_responsable(actividad.responsable_id, usuario.id):
        raise PermisoDenegadoError("Solo el responsable de la actividad puede hacerlo.")
