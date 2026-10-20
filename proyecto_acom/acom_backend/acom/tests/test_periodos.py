"""E5 — Periodos escolares y fechas de inscripción, capa por capa.

Las pruebas de dominio usan fechas fijas: ninguna depende del reloj real.
"""

from datetime import date

from django.db import IntegrityError, transaction
from django.test import SimpleTestCase

from acom import selectors
from acom.domain import reglas
from acom.domain.exceptions import AcomError, InscripcionCerradaError
from acom.models import ActividadComplementaria, CategoriaActividad, Periodo

from .base import AcomTestCase

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
