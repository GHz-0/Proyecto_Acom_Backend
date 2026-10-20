from django.contrib import admin

from .models import ActividadComplementaria, Constancia, Inscripcion, RegistroCreditos


@admin.register(ActividadComplementaria)
class ActividadComplementariaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "categoria", "responsable", "creditos_valor", "activa"]
    list_filter = ["categoria", "activa"]


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ["estudiante", "actividad", "estado", "fecha_inscripcion"]
    list_filter = ["estado", "actividad__categoria"]


admin.site.register(Constancia)
admin.site.register(RegistroCreditos)
