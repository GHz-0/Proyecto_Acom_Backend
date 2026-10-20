from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from .. import selectors
from ..domain.exceptions import AcomError
from ..forms import EvaluacionForm
from ..services import inscripciones


@login_required
def panel_responsable(request, inscripcion_id):
    inscripcion = selectors.inscripcion_de_responsable(inscripcion_id, request.user)
    if inscripcion is None:
        raise Http404

    form = EvaluacionForm()
    error = None
    if request.method == "POST":
        try:
            if "evaluar" in request.POST:
                form = EvaluacionForm(request.POST)
                if form.is_valid():
                    inscripciones.evaluar(
                        inscripcion.id,
                        request.user,
                        aprobado=form.cleaned_data["aprobado"],
                        observaciones=form.cleaned_data["observaciones"],
                    )
                    return redirect("acom:panel_responsable", inscripcion_id=inscripcion.id)
            elif "emitir_constancia" in request.POST:
                inscripciones.emitir_constancia(inscripcion.id, request.user)
                return redirect("acom:panel_responsable", inscripcion_id=inscripcion.id)
        except AcomError as e:
            error = str(e)

    return render(
        request,
        "acom/panel_responsable.html",
        {"inscripcion": inscripcion, "form": form, "error": error},
    )
