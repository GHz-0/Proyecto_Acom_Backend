from django.urls import path

from . import views

app_name = "acom"

urlpatterns = [
    path("", views.lista_actividades, name="lista_actividades"),
    path("inscribirse/<int:actividad_id>/", views.inscribirse, name="inscribirse"),
    path("mis-inscripciones/", views.mis_inscripciones, name="mis_inscripciones"),
    path("responsable/<int:inscripcion_id>/", views.panel_responsable, name="panel_responsable"),
    path("departamento/<int:inscripcion_id>/", views.panel_departamento, name="panel_departamento"),
]
