"""Infraestructura: solo campos, constraints y __str__. Sin reglas de negocio."""

from django.conf import settings
from django.db import models

from .domain.estados import ETIQUETAS, EstadoInscripcion


class CategoriaActividad(models.TextChoices):
    INVESTIGACION = "investigacion", "Proyectos de investigación y desarrollo tecnológico"
    CURSO = "curso", "Cursos, talleres y diplomados"
    PUBLICACION = "publicacion", "Publicaciones y ponencias"
    CULTURAL_DEPORTIVA = "cultural_deportiva", "Actividades culturales y deportivas"
    TUTORIA = "tutoria", "Tutorías y asesorías"
    IMPACTO_SOCIAL = "impacto_social", "Proyectos de impacto social y ambiente"


class ActividadComplementaria(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=30, choices=CategoriaActividad.choices)
    descripcion = models.TextField(blank=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="actividades_responsable",
    )
    creditos_valor = models.DecimalField(max_digits=4, decimal_places=2)
    activa = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(creditos_valor__gt=0), name="actividad_creditos_positivos"
            )
        ]

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"


class Inscripcion(models.Model):
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inscripciones_acom"
    )
    actividad = models.ForeignKey(
        ActividadComplementaria, on_delete=models.PROTECT, related_name="inscripciones"
    )
    estado = models.CharField(
        max_length=20,
        choices=[(e.value, ETIQUETAS[e]) for e in EstadoInscripcion],
        default=EstadoInscripcion.INSCRITO,
    )
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    fecha_evaluacion = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["estudiante", "actividad"], name="uniq_inscripcion_por_actividad"
            )
        ]
        indexes = [models.Index(fields=["estudiante", "estado"])]
        permissions = [("can_validate_credits", "Puede validar constancias y registrar créditos")]

    def __str__(self):
        return f"{self.estudiante} — {self.actividad} ({self.get_estado_display()})"


class Constancia(models.Model):
    inscripcion = models.OneToOneField(
        Inscripcion, on_delete=models.CASCADE, related_name="constancia"
    )
    folio = models.CharField(max_length=30, unique=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    emitida_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return f"Constancia {self.folio}"


class RegistroCreditos(models.Model):
    inscripcion = models.OneToOneField(
        Inscripcion, on_delete=models.CASCADE, related_name="registro_creditos"
    )
    creditos_otorgados = models.DecimalField(max_digits=4, decimal_places=2)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    validado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(creditos_otorgados__gt=0), name="registro_creditos_positivos"
            )
        ]

    def __str__(self):
        return f"{self.creditos_otorgados} créditos — {self.inscripcion.estudiante}"
