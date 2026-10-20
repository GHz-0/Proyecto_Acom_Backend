"""E5 — Periodos escolares y fechas de inscripción, capa por capa.

Las pruebas de dominio usan fechas fijas: ninguna depende del reloj real.
"""

from datetime import date

from django.test import SimpleTestCase

from acom.domain import reglas
from acom.domain.exceptions import AcomError, InscripcionCerradaError

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
