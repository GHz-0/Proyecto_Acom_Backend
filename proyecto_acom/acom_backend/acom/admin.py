from django.contrib import admin

from .models import ActividadComplementaria, Constancia, Inscripcion, Periodo, RegistroCreditos


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ["clave", "inicio", "fin"]


@admin.register(ActividadComplementaria)
class ActividadComplementariaAdmin(admin.ModelAdmin):
    list_display = [
        "nombre",
        "categoria",
        "responsable",
        "creditos_valor",
        "periodo",
        "inscripcion_abre",
        "inscripcion_cierra",
        "activa",
    ]
    list_filter = ["categoria", "activa", "periodo"]


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ["estudiante", "actividad", "estado", "fecha_inscripcion"]
    list_filter = ["estado", "actividad__categoria"]


admin.site.register(Constancia)
admin.site.register(RegistroCreditos)
