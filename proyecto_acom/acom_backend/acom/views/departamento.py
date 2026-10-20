from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
from django.shortcuts import redirect, render

from .. import selectors
from ..domain.exceptions import AcomError
from ..services import inscripciones


@login_required
@permission_required("acom.can_validate_credits", raise_exception=True)
def panel_departamento(request, inscripcion_id):
    inscripcion = selectors.inscripcion_por_id(inscripcion_id)
    if inscripcion is None:
        raise Http404

    error = None
    if request.method == "POST":
        try:
            inscripciones.validar_y_registrar(inscripcion.id, request.user)
            return redirect("acom:panel_departamento", inscripcion_id=inscripcion.id)
        except AcomError as e:
            error = str(e)

    return render(
        request, "acom/panel_departamento.html", {"inscripcion": inscripcion, "error": error}
    )
