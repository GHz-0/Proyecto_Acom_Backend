from django import forms


class EvaluacionForm(forms.Form):
    aprobado = forms.TypedChoiceField(
        choices=[("1", "Aprobar"), ("0", "Rechazar")],
        coerce=lambda v: v == "1",
        widget=forms.RadioSelect,
    )
    observaciones = forms.CharField(widget=forms.Textarea, required=False)
