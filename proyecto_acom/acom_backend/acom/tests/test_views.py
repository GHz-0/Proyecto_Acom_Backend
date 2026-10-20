"""Capa de presentación: flujo HTTP y traducción de errores a respuestas."""

from django.urls import reverse

from acom.domain.estados import EstadoInscripcion
from acom.models import Inscripcion
from acom.services import inscripciones

from .base import AcomTestCase


class FlujoHttpTest(AcomTestCase):
    def test_flujo_completo_por_http(self):
        self.client.force_login(self.estudiante)
        r = self.client.post(reverse("acom:inscribirse", args=[self.actividad.id]))
        self.assertRedirects(r, reverse("acom:mis_inscripciones"))
        insc = Inscripcion.objects.get()

        self.client.force_login(self.responsable)
        url = reverse("acom:panel_responsable", args=[insc.id])
        self.client.post(url, {"evaluar": "1", "aprobado": "1", "observaciones": "Bien"})
        self.client.post(url, {"emitir_constancia": "1"})

        self.client.force_login(self.depto)
        self.client.post(reverse("acom:panel_departamento", args=[insc.id]))

        insc.refresh_from_db()
        self.assertEqual(insc.estado, EstadoInscripcion.VALIDADO)

        self.client.force_login(self.estudiante)
        r = self.client.get(reverse("acom:mis_inscripciones"))
        self.assertContains(r, "Créditos acumulados: 2.00")


class ErroresHttpTest(AcomTestCase):
    def test_doble_inscripcion_muestra_error_y_no_500(self):
        inscripciones.inscribir(self.estudiante, self.actividad)
        self.client.force_login(self.estudiante)
        r = self.client.post(reverse("acom:inscribirse", args=[self.actividad.id]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Ya estás inscrito")

    def test_estudiante_no_accede_al_panel_de_departamento(self):
        insc = self.inscripcion_con_constancia()
        self.client.force_login(self.estudiante)
        r = self.client.post(reverse("acom:panel_departamento", args=[insc.id]))
        self.assertEqual(r.status_code, 403)
        insc.refresh_from_db()
        self.assertEqual(insc.estado, EstadoInscripcion.CONSTANCIA_EMITIDA)

    def test_otro_docente_recibe_404_en_panel_responsable(self):
        insc = inscripciones.inscribir(self.estudiante, self.actividad)
        self.client.force_login(self.depto)  # no es el responsable
        r = self.client.get(reverse("acom:panel_responsable", args=[insc.id]))
        self.assertEqual(r.status_code, 404)

    def test_anonimo_es_redirigido_al_login(self):
        r = self.client.get(reverse("acom:lista_actividades"))
        self.assertEqual(r.status_code, 302)
