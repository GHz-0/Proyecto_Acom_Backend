"""Máquina de estados de una inscripción. La regla es un dato, no ifs dispersos."""

from enum import StrEnum

from .exceptions import TransicionInvalidaError


class EstadoInscripcion(StrEnum):
    INSCRITO = "inscrito"
    EVALUADO_APROBADO = "evaluado_aprobado"
    EVALUADO_RECHAZADO = "evaluado_rechazado"
    CONSTANCIA_EMITIDA = "constancia_emitida"
    VALIDADO = "validado"


ETIQUETAS = {
    EstadoInscripcion.INSCRITO: "Inscrito",
    EstadoInscripcion.EVALUADO_APROBADO: "Evaluado — aprobado",
    EstadoInscripcion.EVALUADO_RECHAZADO: "Evaluado — rechazado",
    EstadoInscripcion.CONSTANCIA_EMITIDA: "Constancia emitida",
    EstadoInscripcion.VALIDADO: "Validado (créditos registrados)",
}

TRANSICIONES = {
    EstadoInscripcion.INSCRITO: {
        EstadoInscripcion.EVALUADO_APROBADO,
        EstadoInscripcion.EVALUADO_RECHAZADO,
    },
    EstadoInscripcion.EVALUADO_APROBADO: {EstadoInscripcion.CONSTANCIA_EMITIDA},
    EstadoInscripcion.CONSTANCIA_EMITIDA: {EstadoInscripcion.VALIDADO},
}


def validar_transicion(actual: str, nuevo: str) -> None:
    if nuevo not in TRANSICIONES.get(actual, set()):
        raise TransicionInvalidaError(f"No se puede pasar de '{actual}' a '{nuevo}'.")
