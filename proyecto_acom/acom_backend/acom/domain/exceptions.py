"""Errores del dominio. Sin dependencias de Django."""


class AcomError(Exception):
    """Base de todos los errores de negocio: las vistas capturan esta clase."""


class TransicionInvalidaError(AcomError):
    """Se intentó mover una inscripción a un estado que no le corresponde."""


class LimiteCreditosError(AcomError):
    """El estudiante ya alcanzó los créditos ACOM requeridos para titularse."""


class InscripcionDuplicadaError(AcomError):
    """El estudiante ya está inscrito en esa actividad."""


class ActividadInactivaError(AcomError):
    """La actividad ya no acepta inscripciones."""


class PermisoDenegadoError(AcomError):
    """El usuario no tiene permiso para ejecutar este caso de uso."""
