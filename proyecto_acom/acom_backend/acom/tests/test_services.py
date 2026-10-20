"""Capa de aplicación: casos de uso contra base de datos real."""

from decimal import Decimal
from unittest import mock

from acom import selectors
from acom.domain.estados import EstadoInscripcion
from acom.domain.exceptions import (
    ActividadInactivaError,
    InscripcionDuplicadaError,
    LimiteCreditosError,
    PermisoDenegadoError,
    TransicionInvalidaError,
)
from acom.services import inscripciones

from .base import AcomTestCase, User


class FlujoTest(AcomTestCase):
    def test_flujo_completo_hasta_registro_de_creditos(self):
        insc = self.inscripcion_con_constancia()
        self.assertEqual(insc.constancia.folio, f"ACOM-{insc.id:06d}")

        with self.captureOnCommitCallbacks(execute=True):
            registro = inscripciones.validar_y_registrar(insc.id, self.depto)

        insc.refresh_from_db()
        self.assertEqual(insc.estado, EstadoInscripcion.VALIDADO)
        self.assertEqual(registro.creditos_otorgados, Decimal("2.00"))
        self.assertEqual(selectors.total_validado(self.estudiante), Decimal("2.00"))

    def test_rechazo_no_permite_emitir_constancia(self):
        insc = inscripciones.inscribir(self.estudiante, self.actividad)
        inscripciones.evaluar(insc.id, self.responsable, aprobado=False, observaciones="No cumple")
        with self.assertRaises(TransicionInvalidaError):
            inscripciones.emitir_constancia(insc.id, self.responsable)

    def test_no_se_puede_emitir_constancia_sin_evaluar(self):
        insc = inscripciones.inscribir(self.estudiante, self.actividad)
        with self.assertRaises(TransicionInvalidaError):
            inscripciones.emitir_constancia(insc.id, self.responsable)

    def test_no_se_puede_evaluar_dos_veces(self):
        insc = inscripciones.inscribir(self.estudiante, self.actividad)
        inscripciones.evaluar(insc.id, self.responsable, aprobado=True)
        with self.assertRaises(TransicionInvalidaError):
            inscripciones.evaluar(insc.id, self.responsable, aprobado=False)


class InscripcionTest(AcomTestCase):
    def test_doble_inscripcion_lanza_error_de_negocio(self):
        inscripciones.inscribir(self.estudiante, self.actividad)
        with self.assertRaises(InscripcionDuplicadaError):
            inscripciones.inscribir(self.estudiante, self.actividad)

    def test_actividad_inactiva(self):
        self.actividad.activa = False
        self.actividad.save()
        with self.assertRaises(ActividadInactivaError):
            inscripciones.inscribir(self.estudiante, self.actividad)


class AutorizacionTest(AcomTestCase):
    def test_solo_el_responsable_puede_evaluar(self):
        insc = inscripciones.inscribir(self.estudiante, self.actividad)
        otro = User.objects.create_user("docente2", password="x")
        with self.assertRaises(PermisoDenegadoError):
            inscripciones.evaluar(insc.id, otro, aprobado=True)

    def test_solo_el_responsable_puede_emitir_constancia(self):
        insc = inscripciones.inscribir(self.estudiante, self.actividad)
        inscripciones.evaluar(insc.id, self.responsable, aprobado=True)
        with self.assertRaises(PermisoDenegadoError):
            inscripciones.emitir_constancia(insc.id, self.estudiante)

    def test_un_estudiante_no_puede_validar_sus_propios_creditos(self):
        insc = self.inscripcion_con_constancia()
        with self.assertRaises(PermisoDenegadoError):
            inscripciones.validar_y_registrar(insc.id, self.estudiante)


class LimiteCreditosTest(AcomTestCase):
    def registrar(self, actividad):
        insc = self.inscripcion_con_constancia(actividad)
        inscripciones.validar_y_registrar(insc.id, self.depto)
        return insc

    def test_no_se_registran_creditos_pasado_el_limite(self):
        self.registrar(self.actividad)  # 2.00
        self.registrar(self.crear_actividad("Diplomado", "3.00"))  # 5.00: en la meta

        insc = self.inscripcion_con_constancia(self.crear_actividad("Extra", "1.00"))
        with self.assertRaises(LimiteCreditosError):
            inscripciones.validar_y_registrar(insc.id, self.depto)


class SignalTest(AcomTestCase):
    def test_signal_se_emite_solo_al_confirmar_la_transaccion(self):
        from acom.signals import inscripcion_validada

        recibidos = mock.Mock()
        inscripcion_validada.connect(recibidos, weak=False)
        self.addCleanup(inscripcion_validada.disconnect, recibidos)

        insc = self.inscripcion_con_constancia()
        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            inscripciones.validar_y_registrar(insc.id, self.depto)
        recibidos.assert_not_called()  # aún no hay commit

        for cb in callbacks:
            cb()
        recibidos.assert_called_once()
