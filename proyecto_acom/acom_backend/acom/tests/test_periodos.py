"""E5 — Periodos escolares y fechas de inscripción, capa por capa.

Las pruebas de dominio usan fechas fijas: ninguna depende del reloj real.
"""

from datetime import date
from unittest import mock

from django.db import IntegrityError, transaction
from django.test import SimpleTestCase
from django.urls import reverse

from acom import selectors
from acom.domain import reglas
from acom.domain.exceptions import (
    AcomError,
    ActividadInactivaError,
    InscripcionCerradaError,
)
from acom.models import ActividadComplementaria, CategoriaActividad, Inscripcion, Periodo
from acom.services import inscripciones

from .base import AcomTestCase, User

ABRE = date(2026, 8, 17)
CIERRA = date(2026, 8, 28)


class InscripcionAbiertaDominioTest(SimpleTestCase):
    """Capa de dominio: SimpleTestCase, sin base de datos."""

    def test_sin_fechas_esta_abierta(self):
        self.assertTrue(reglas.inscripcion_abierta(date(2026, 1, 1), None, None))

    def test_dentro_de_la_ventana(self):
        self.assertTrue(reglas.inscripcion_abierta(date(2026, 8, 20), ABRE, CIERRA))

    def test_los_extremos_son_inclusivos(self):
        self.assertTrue(reglas.inscripcion_abierta(ABRE, ABRE, CIERRA))
        self.assertTrue(reglas.inscripcion_abierta(CIERRA, ABRE, CIERRA))

    def test_un_dia_antes_de_abrir_esta_cerrada(self):
        self.assertFalse(reglas.inscripcion_abierta(date(2026, 8, 16), ABRE, CIERRA))

    def test_un_dia_despues_de_cerrar_esta_cerrada(self):
        self.assertFalse(reglas.inscripcion_abierta(date(2026, 8, 29), ABRE, CIERRA))

    def test_ventana_de_un_solo_dia(self):
        self.assertTrue(reglas.inscripcion_abierta(ABRE, ABRE, ABRE))
        self.assertFalse(reglas.inscripcion_abierta(date(2026, 8, 18), ABRE, ABRE))

    def test_solo_fecha_de_apertura(self):
        self.assertFalse(reglas.inscripcion_abierta(date(2026, 8, 16), ABRE, None))
        self.assertTrue(reglas.inscripcion_abierta(ABRE, ABRE, None))
        self.assertTrue(reglas.inscripcion_abierta(date(2030, 1, 1), ABRE, None))

    def test_solo_fecha_de_cierre(self):
        self.assertTrue(reglas.inscripcion_abierta(date(2020, 1, 1), None, CIERRA))
        self.assertTrue(reglas.inscripcion_abierta(CIERRA, None, CIERRA))
        self.assertFalse(reglas.inscripcion_abierta(date(2026, 8, 29), None, CIERRA))

    def test_el_error_es_un_error_de_negocio(self):
        # La API lo traduce a 400 y las vistas HTML lo capturan como AcomError.
        self.assertTrue(issubclass(InscripcionCerradaError, AcomError))

    def test_el_dominio_nunca_consulta_el_reloj(self):
        import ast
        from pathlib import Path

        import acom.domain

        relojes = {"now", "today", "utcnow", "localdate", "localtime"}
        for archivo in Path(acom.domain.__file__).parent.glob("*.py"):
            for nodo in ast.walk(ast.parse(archivo.read_text())):
                if isinstance(nodo, ast.Attribute):
                    self.assertNotIn(
                        nodo.attr, relojes, f"{archivo.name} usa el reloj ({nodo.attr}): recíbelo"
                    )


class InfraestructuraPeriodosTest(AcomTestCase):
    """Capa de infraestructura: constraints del modelo y selector con filtro."""

    def periodo(self, clave="2026-2", inicio=date(2026, 8, 17), fin=date(2026, 12, 18)):
        return Periodo.objects.create(clave=clave, inicio=inicio, fin=fin)

    def periodo_anterior(self):
        return self.periodo("2026-1", inicio=date(2026, 1, 12), fin=date(2026, 6, 1))

    def crear(self, nombre, **extra):
        return ActividadComplementaria.objects.create(
            nombre=nombre,
            categoria=CategoriaActividad.CURSO,
            responsable=self.responsable,
            creditos_valor=1,
            **extra,
        )

    def test_la_clave_del_periodo_es_unica(self):
        self.periodo()
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.periodo()

    def test_el_periodo_no_puede_terminar_antes_de_empezar(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.periodo("2026-3", inicio=date(2026, 12, 18), fin=date(2026, 8, 17))

    def test_la_ventana_no_puede_cerrar_antes_de_abrir(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.crear(
                "Mal", inscripcion_abre=date(2026, 8, 28), inscripcion_cierra=date(2026, 8, 17)
            )

    def test_la_ventana_acepta_una_sola_fecha_o_ninguna(self):
        self.crear("Solo abre", inscripcion_abre=date(2026, 8, 17))
        self.crear("Solo cierra", inscripcion_cierra=date(2026, 8, 28))
        self.assertEqual(ActividadComplementaria.objects.count(), 3)  # + la del fixture

    def test_un_periodo_con_actividades_no_se_puede_borrar(self):
        periodo = self.periodo()
        self.crear("Con periodo", periodo=periodo)
        with self.assertRaises(Exception), transaction.atomic():
            periodo.delete()

    def test_actividades_activas_sin_periodo_devuelve_todas(self):
        periodo = self.periodo()
        self.crear("Con periodo", periodo=periodo)
        nombres = {a.nombre for a in selectors.actividades_activas()}
        self.assertEqual(nombres, {"Verano de Investigación", "Con periodo"})

    def test_actividades_activas_filtra_por_instancia_de_periodo(self):
        p1, p2 = self.periodo_anterior(), self.periodo("2026-2")
        self.crear("A", periodo=p1)
        self.crear("B", periodo=p2)
        self.assertEqual([a.nombre for a in selectors.actividades_activas(p2)], ["B"])

    def test_actividades_activas_filtra_por_clave(self):
        p1, p2 = self.periodo_anterior(), self.periodo("2026-2")
        self.crear("A", periodo=p1)
        self.crear("B", periodo=p2)
        self.assertEqual([a.nombre for a in selectors.actividades_activas("2026-1")], ["A"])

    def test_el_filtro_por_periodo_no_incluye_inactivas(self):
        periodo = self.periodo()
        self.crear("Activa", periodo=periodo)
        self.crear("Inactiva", periodo=periodo, activa=False)
        self.assertEqual([a.nombre for a in selectors.actividades_activas("2026-2")], ["Activa"])

    def test_clave_inexistente_devuelve_vacio(self):
        self.assertEqual(list(selectors.actividades_activas("2099-9")), [])

    def test_clave_vacia_equivale_a_no_filtrar(self):
        self.assertEqual(selectors.actividades_activas("").count(), 1)


class InscribirConVentanaTest(AcomTestCase):
    """Capa de aplicación: `inscribir` valida la ventana con `hoy` inyectado (fechas fijas)."""

    def setUp(self):
        super().setUp()
        self.actividad.inscripcion_abre = ABRE
        self.actividad.inscripcion_cierra = CIERRA
        self.actividad.save()

    def test_inscribe_dentro_de_la_ventana(self):
        insc = inscripciones.inscribir(self.estudiante, self.actividad, hoy=date(2026, 8, 20))
        self.assertEqual(insc.actividad, self.actividad)

    def test_inscribe_el_primer_y_el_ultimo_dia(self):
        inscripciones.inscribir(self.estudiante, self.actividad, hoy=ABRE)
        otro = self.crear_actividad("Otra", "1.00")
        otro.inscripcion_abre, otro.inscripcion_cierra = ABRE, CIERRA
        otro.save()
        inscripciones.inscribir(self.estudiante, otro, hoy=CIERRA)
        self.assertEqual(Inscripcion.objects.count(), 2)

    def test_antes_de_abrir_lanza_error_claro_y_no_inscribe(self):
        with self.assertRaises(InscripcionCerradaError) as ctx:
            inscripciones.inscribir(self.estudiante, self.actividad, hoy=date(2026, 8, 16))
        self.assertIn("abre el 17/08/2026", str(ctx.exception))
        self.assertIn(self.actividad.nombre, str(ctx.exception))
        self.assertEqual(Inscripcion.objects.count(), 0)

    def test_despues_de_cerrar_lanza_error_claro_y_no_inscribe(self):
        with self.assertRaises(InscripcionCerradaError) as ctx:
            inscripciones.inscribir(self.estudiante, self.actividad, hoy=date(2026, 8, 29))
        self.assertIn("cerró el 28/08/2026", str(ctx.exception))
        self.assertEqual(Inscripcion.objects.count(), 0)

    def test_solo_fecha_de_cierre_mensaje_de_cierre(self):
        self.actividad.inscripcion_abre = None
        self.actividad.save()
        with self.assertRaises(InscripcionCerradaError) as ctx:
            inscripciones.inscribir(self.estudiante, self.actividad, hoy=date(2026, 9, 1))
        self.assertIn("cerró el 28/08/2026", str(ctx.exception))

    def test_solo_fecha_de_apertura_mensaje_de_apertura(self):
        self.actividad.inscripcion_cierra = None
        self.actividad.save()
        with self.assertRaises(InscripcionCerradaError) as ctx:
            inscripciones.inscribir(self.estudiante, self.actividad, hoy=date(2026, 1, 1))
        self.assertIn("abre el 17/08/2026", str(ctx.exception))

    def test_sin_fechas_se_inscribe_en_cualquier_momento(self):
        libre = self.crear_actividad("Sin fechas", "1.00")
        for hoy in (date(1999, 1, 1), date(2999, 12, 31)):
            Inscripcion.objects.all().delete()
            inscripciones.inscribir(self.estudiante, libre, hoy=hoy)
        self.assertEqual(Inscripcion.objects.count(), 1)

    def test_sin_hoy_usa_la_fecha_local_actual(self):
        with mock.patch("django.utils.timezone.localdate", return_value=date(2026, 8, 20)):
            inscripciones.inscribir(self.estudiante, self.actividad)
        self.assertEqual(Inscripcion.objects.count(), 1)

        otro = User.objects.create_user("estudiante2", password="x")
        with (
            mock.patch("django.utils.timezone.localdate", return_value=date(2026, 9, 30)),
            self.assertRaises(InscripcionCerradaError),
        ):
            inscripciones.inscribir(otro, self.actividad)

    def test_actividad_inactiva_sigue_dando_su_propio_error(self):
        self.actividad.activa = False
        self.actividad.save()
        with self.assertRaises(ActividadInactivaError):
            inscripciones.inscribir(self.estudiante, self.actividad, hoy=date(2026, 8, 20))


HOY_EN_VENTANA = date(2026, 8, 20)
HOY_FUERA = date(2026, 9, 30)


class PresentacionHtmlPeriodosTest(AcomTestCase):
    """Capa de presentación (HTML): muestra la ventana y traduce el error a un mensaje."""

    def setUp(self):
        super().setUp()
        self.periodo = Periodo.objects.create(
            clave="2026-2", inicio=date(2026, 8, 17), fin=date(2026, 12, 18)
        )
        self.actividad.periodo = self.periodo
        self.actividad.inscripcion_abre = ABRE
        self.actividad.inscripcion_cierra = CIERRA
        self.actividad.save()
        self.client.force_login(self.estudiante)

    def en(self, hoy):
        return mock.patch("django.utils.timezone.localdate", return_value=hoy)

    def test_la_lista_muestra_periodo_y_ventana(self):
        with self.en(HOY_EN_VENTANA):
            r = self.client.get(reverse("acom:lista_actividades"))
        self.assertContains(r, "Periodo 2026-2")
        self.assertContains(r, "Inscripción: del 17/08/2026 al 28/08/2026")

    def test_la_lista_ofrece_inscribirse_solo_con_la_ventana_abierta(self):
        url = reverse("acom:inscribirse", args=[self.actividad.id])
        with self.en(HOY_EN_VENTANA):
            abierta = self.client.get(reverse("acom:lista_actividades"))
        self.assertContains(abierta, url)
        self.assertNotContains(abierta, "Inscripción cerrada")

        with self.en(HOY_FUERA):
            cerrada = self.client.get(reverse("acom:lista_actividades"))
        self.assertNotContains(cerrada, url)
        self.assertContains(cerrada, "Inscripción cerrada")

    def test_actividad_sin_fechas_se_muestra_sin_restriccion(self):
        self.actividad.periodo = None
        self.actividad.inscripcion_abre = self.actividad.inscripcion_cierra = None
        self.actividad.save()
        r = self.client.get(reverse("acom:lista_actividades"))
        self.assertContains(r, "sin restricción de fechas")
        self.assertContains(r, reverse("acom:inscribirse", args=[self.actividad.id]))

    def test_la_confirmacion_muestra_la_ventana(self):
        r = self.client.get(reverse("acom:inscribirse", args=[self.actividad.id]))
        self.assertContains(r, "Periodo: 2026-2")
        self.assertContains(r, "Inscripción: del 17/08/2026 al 28/08/2026")

    def test_inscribirse_fuera_de_la_ventana_muestra_error_y_no_500(self):
        with self.en(HOY_FUERA):
            r = self.client.post(reverse("acom:inscribirse", args=[self.actividad.id]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "cerró el 28/08/2026")
        self.assertEqual(Inscripcion.objects.count(), 0)

    def test_inscribirse_dentro_de_la_ventana_redirige(self):
        with self.en(HOY_EN_VENTANA):
            r = self.client.post(reverse("acom:inscribirse", args=[self.actividad.id]))
        self.assertRedirects(r, reverse("acom:mis_inscripciones"))
        self.assertEqual(Inscripcion.objects.count(), 1)
