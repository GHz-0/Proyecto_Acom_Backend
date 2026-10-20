"""Presentación: parsea la petición, llama al servicio y traduce errores a mensajes."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .. import selectors
from ..domain import reglas
from ..domain.exceptions import AcomError
from ..models import ActividadComplementaria
from ..services import inscripciones


@login_required
def lista_actividades(request):
    hoy = timezone.localdate()
    actividades = list(selectors.actividades_activas())
    for actividad in actividades:  # solo para mostrar: la regla vive en el dominio
        actividad.inscripcion_abierta = reglas.inscripcion_abierta(
            hoy, actividad.inscripcion_abre, actividad.inscripcion_cierra
        )
    return render(request, "acom/lista_actividades.html", {"actividades": actividades})


@login_required
def inscribirse(request, actividad_id):
    actividad = get_object_or_404(ActividadComplementaria, pk=actividad_id, activa=True)
    error = None
    if request.method == "POST":
        try:
            inscripciones.inscribir(request.user, actividad)
            return redirect("acom:mis_inscripciones")
        except AcomError as e:
            error = str(e)
    return render(
        request, "acom/confirmar_inscripcion.html", {"actividad": actividad, "error": error}
    )


@login_required
def mis_inscripciones(request):
    total = selectors.total_validado(request.user)
    return render(
        request,
        "acom/mis_inscripciones.html",
        {
            "inscripciones": selectors.inscripciones_de(request.user),
            "creditos_totales": total,
            "creditos_faltantes": reglas.faltantes(total),
        },
    )
