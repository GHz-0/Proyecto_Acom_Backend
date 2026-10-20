"""Capa de dominio: SimpleTestCase, sin base de datos."""

from decimal import Decimal

from django.test import SimpleTestCase

from acom.domain import reglas
from acom.domain.estados import EstadoInscripcion as E
from acom.domain.estados import validar_transicion
from acom.domain.exceptions import AcomError, TransicionInvalidaError


class EstadosTest(SimpleTestCase):
    def test_camino_feliz(self):
        validar_transicion(E.INSCRITO, E.EVALUADO_APROBADO)
        validar_transicion(E.EVALUADO_APROBADO, E.CONSTANCIA_EMITIDA)
        validar_transicion(E.CONSTANCIA_EMITIDA, E.VALIDADO)

    def test_no_se_puede_saltar_pasos(self):
        with self.assertRaises(TransicionInvalidaError):
            validar_transicion(E.INSCRITO, E.CONSTANCIA_EMITIDA)

    def test_rechazado_y_validado_son_estados_finales(self):
        for final in (E.EVALUADO_RECHAZADO, E.VALIDADO):
            with self.assertRaises(TransicionInvalidaError):
                validar_transicion(final, E.INSCRITO)

    def test_errores_de_negocio_heredan_de_acom_error(self):
        self.assertTrue(issubclass(TransicionInvalidaError, AcomError))


class ReglasTest(SimpleTestCase):
    def test_limite(self):
        self.assertFalse(reglas.excede_limite(Decimal("4.99")))
        self.assertTrue(reglas.excede_limite(Decimal("5.00")))

    def test_faltantes_nunca_es_negativo(self):
        self.assertEqual(reglas.faltantes(Decimal("2.00")), Decimal("3.00"))
        self.assertEqual(reglas.faltantes(Decimal("7.00")), Decimal(0))

    def test_folio(self):
        self.assertEqual(reglas.generar_folio(42), "ACOM-000042")


class ReglaDeDependenciaTest(SimpleTestCase):
    def test_el_dominio_no_importa_django_ni_capas_superiores(self):
        import ast
        from pathlib import Path

        import acom.domain

        prohibidos = ("django", "acom.models", "acom.services", "acom.views", "acom.selectors")
        for archivo in Path(acom.domain.__file__).parent.glob("*.py"):
            for nodo in ast.walk(ast.parse(archivo.read_text())):
                if isinstance(nodo, ast.Import):
                    modulos = [a.name for a in nodo.names]
                elif isinstance(nodo, ast.ImportFrom) and nodo.level == 0:
                    modulos = [nodo.module]
                else:
                    continue
                for m in modulos:
                    self.assertFalse(
                        m.startswith(prohibidos), f"{archivo.name} importa {m}: viola la regla"
                    )
