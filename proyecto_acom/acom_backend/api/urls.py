from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = "api"

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("actividades/", views.ActividadListView.as_view(), name="actividades"),
    path(
        "actividades/<int:actividad_id>/inscribirse/",
        views.InscribirseView.as_view(),
        name="inscribirse",
    ),
    path("mis-inscripciones/", views.MisInscripcionesView.as_view(), name="mis_inscripciones"),
    path(
        "mis-inscripciones/resumen/",
        views.ResumenCreditosView.as_view(),
        name="resumen_creditos",
    ),
    path(
        "responsable/inscripciones/<int:inscripcion_id>/",
        views.InscripcionResponsableView.as_view(),
        name="inscripcion_responsable",
    ),
    path(
        "responsable/inscripciones/<int:inscripcion_id>/evaluar/",
        views.EvaluarInscripcionView.as_view(),
        name="evaluar_inscripcion",
    ),
    path(
        "responsable/inscripciones/<int:inscripcion_id>/emitir-constancia/",
        views.EmitirConstanciaView.as_view(),
        name="emitir_constancia",
    ),
    path(
        "departamento/inscripciones/<int:inscripcion_id>/validar/",
        views.ValidarCreditosView.as_view(),
        name="validar_creditos",
    ),
]
