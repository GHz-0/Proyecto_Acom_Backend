from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase

from acom.domain.estados import EstadoInscripcion
from acom.models import ActividadComplementaria, CategoriaActividad
from acom.services import inscripciones

User = get_user_model()


class AcomTestCase(TestCase):
    """Fixtures compartidos: estudiante, responsable, departamento y una actividad."""

    def setUp(self):
        self.estudiante = User.objects.create_user("estudiante1", password="x")
        self.responsable = User.objects.create_user("docente1", password="x")
        self.depto = User.objects.create_user("depto1", password="x")
        self.depto.user_permissions.add(Permission.objects.get(codename="can_validate_credits"))
        self.actividad = self.crear_actividad("Verano de Investigación", "2.00")

    def crear_actividad(self, nombre, creditos):
        return ActividadComplementaria.objects.create(
            nombre=nombre,
            categoria=CategoriaActividad.INVESTIGACION,
            responsable=self.responsable,
            creditos_valor=Decimal(creditos),
        )

    def inscripcion_con_constancia(self, actividad=None):
        insc = inscripciones.inscribir(self.estudiante, actividad or self.actividad)
        inscripciones.evaluar(insc.id, self.responsable, aprobado=True)
        inscripciones.emitir_constancia(insc.id, self.responsable)
        insc.refresh_from_db()
        assert insc.estado == EstadoInscripcion.CONSTANCIA_EMITIDA
        return insc
