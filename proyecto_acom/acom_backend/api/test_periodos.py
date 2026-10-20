"""E5 en la API: filtro por periodo, campos nuevos y 400 fuera de la ventana."""

from datetime import date
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from acom.models import ActividadComplementaria, CategoriaActividad, Inscripcion, Periodo

User = get_user_model()

ABRE = date(2026, 8, 17)
CIERRA = date(2026, 8, 28)


class ApiPeriodosTest(APITestCase):
    def setUp(self):
        self.estudiante = User.objects.create_user("estudiante1", password="clave-segura-1")
        self.responsable = User.objects.create_user("docente1", password="clave-segura-1")
        self.p1 = Periodo.objects.create(
            clave="2026-1", inicio=date(2026, 1, 12), fin=date(2026, 6, 1)
        )
        self.p2 = Periodo.objects.create(
            clave="2026-2", inicio=date(2026, 8, 17), fin=date(2026, 12, 18)
        )
        self.a1 = self.crear("Taller enero", periodo=self.p1)
        self.a2 = self.crear(
            "Taller agosto", periodo=self.p2, inscripcion_abre=ABRE, inscripcion_cierra=CIERRA
        )
        self.libre = self.crear("Sin periodo")
        self.autenticar()

    def crear(self, nombre, **extra):
        return ActividadComplementaria.objects.create(
            nombre=nombre,
            categoria=CategoriaActividad.CURSO,
            responsable=self.responsable,
            creditos_valor=Decimal("1.00"),
            **extra,
        )

    def autenticar(self, username="estudiante1"):
        r = self.client.post(
            reverse("api:token_obtain"), {"username": username, "password": "clave-segura-1"}
        )
        self.assertEqual(r.status_code, 200, r.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")

    def nombres(self, **params):
        r = self.client.get(reverse("api:actividades"), params)
        self.assertEqual(r.status_code, 200, r.data)
        return sorted(a["nombre"] for a in r.data)

    def test_sin_filtro_lista_todas_incluidas_las_que_no_tienen_periodo(self):
        self.assertEqual(self.nombres(), ["Sin periodo", "Taller agosto", "Taller enero"])

    def test_filtra_por_periodo(self):
        self.assertEqual(self.nombres(periodo="2026-2"), ["Taller agosto"])
        self.assertEqual(self.nombres(periodo="2026-1"), ["Taller enero"])

    def test_periodo_inexistente_da_lista_vacia(self):
        self.assertEqual(self.nombres(periodo="2099-9"), [])

    def test_periodo_vacio_no_filtra(self):
        self.assertEqual(len(self.nombres(periodo="")), 3)

    def test_el_filtro_exige_autenticacion(self):
        self.client.credentials()
        r = self.client.get(reverse("api:actividades"), {"periodo": "2026-2"})
        self.assertEqual(r.status_code, 401)

    def test_la_respuesta_incluye_periodo_y_ventana(self):
        r = self.client.get(reverse("api:actividades"), {"periodo": "2026-2"})
        self.assertEqual(r.data[0]["periodo"], "2026-2")
        self.assertEqual(r.data[0]["inscripcion_abre"], "2026-08-17")
        self.assertEqual(r.data[0]["inscripcion_cierra"], "2026-08-28")

    def test_actividad_sin_periodo_ni_fechas_devuelve_nulls(self):
        r = self.client.get(reverse("api:actividades"))
        libre = next(a for a in r.data if a["nombre"] == "Sin periodo")
        self.assertIsNone(libre["periodo"])
        self.assertIsNone(libre["inscripcion_abre"])
        self.assertIsNone(libre["inscripcion_cierra"])

    def test_inscribirse_fuera_de_la_ventana_devuelve_400_claro(self):
        url = reverse("api:inscribirse", kwargs={"actividad_id": self.a2.id})
        with mock.patch("django.utils.timezone.localdate", return_value=date(2026, 9, 30)):
            r = self.client.post(url)
        self.assertEqual(r.status_code, 400)
        self.assertIn("cerró el 28/08/2026", r.data["detail"])
        self.assertEqual(Inscripcion.objects.count(), 0)

    def test_inscribirse_antes_de_abrir_devuelve_400_claro(self):
        url = reverse("api:inscribirse", kwargs={"actividad_id": self.a2.id})
        with mock.patch("django.utils.timezone.localdate", return_value=date(2026, 8, 1)):
            r = self.client.post(url)
        self.assertEqual(r.status_code, 400)
        self.assertIn("abre el 17/08/2026", r.data["detail"])

    def test_inscribirse_dentro_de_la_ventana_devuelve_201(self):
        url = reverse("api:inscribirse", kwargs={"actividad_id": self.a2.id})
        with mock.patch("django.utils.timezone.localdate", return_value=date(2026, 8, 20)):
            r = self.client.post(url)
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["actividad"]["periodo"], "2026-2")

    def test_actividad_sin_fechas_se_inscribe_siempre(self):
        url = reverse("api:inscribirse", kwargs={"actividad_id": self.libre.id})
        r = self.client.post(url)
        self.assertEqual(r.status_code, 201, r.data)

    def test_el_esquema_openapi_documenta_el_filtro(self):
        r = self.client.get("/api/schema/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"name: periodo", r.content)
