"""Serializers: solo forma/representación. La lógica sigue viviendo en acom.services."""

from rest_framework import serializers

from acom.models import ActividadComplementaria, Constancia, Inscripcion, RegistroCreditos


class ActividadComplementariaSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source="get_categoria_display", read_only=True)
    responsable_nombre = serializers.CharField(source="responsable.get_username", read_only=True)

    class Meta:
        model = ActividadComplementaria
        fields = [
            "id",
            "nombre",
            "categoria",
            "categoria_display",
            "descripcion",
            "responsable_nombre",
            "creditos_valor",
            "activa",
        ]
        read_only_fields = fields


class ConstanciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Constancia
        fields = ["folio", "fecha_emision", "emitida_por"]
        read_only_fields = fields


class RegistroCreditosSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroCreditos
        fields = ["creditos_otorgados", "fecha_registro"]
        read_only_fields = fields


class InscripcionSerializer(serializers.ModelSerializer):
    actividad = ActividadComplementariaSerializer(read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    constancia = ConstanciaSerializer(read_only=True)
    registro_creditos = RegistroCreditosSerializer(read_only=True)

    class Meta:
        model = Inscripcion
        fields = [
            "id",
            "actividad",
            "estado",
            "estado_display",
            "fecha_inscripcion",
            "fecha_evaluacion",
            "observaciones",
            "constancia",
            "registro_creditos",
        ]
        read_only_fields = fields


class InscripcionListaSerializer(serializers.ModelSerializer):
    """Versión ligera para listados — sin anidar actividad completa ni relaciones 1:1."""

    actividad_nombre = serializers.CharField(source="actividad.nombre", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Inscripcion
        fields = ["id", "actividad_nombre", "estado", "estado_display", "fecha_inscripcion"]
        read_only_fields = fields


class EvaluarInscripcionSerializer(serializers.Serializer):
    aprobado = serializers.BooleanField()
    observaciones = serializers.CharField(required=False, allow_blank=True, default="")


class ResumenCreditosSerializer(serializers.Serializer):
    creditos_totales = serializers.DecimalField(max_digits=4, decimal_places=2)
    creditos_faltantes = serializers.DecimalField(max_digits=4, decimal_places=2)
