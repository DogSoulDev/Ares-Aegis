from antivirus_kali.controladores.controlador_modo_seguro import ControladorModoSeguro
from antivirus_kali.nucleo.modo_seguro import ModoSeguro
from antivirus_kali.nucleo.auditor_configuracion import AuditorConfiguracion
import pytest

def test_activar_modo_seguro(monkeypatch):
    class DummyModo(ModoSeguro):
        def activar(self):
            self.advertencia = None
    ctrl = ControladorModoSeguro()
    monkeypatch.setattr(ctrl, 'modo', DummyModo())
    advertencia = ctrl.activar_modo_seguro()
    assert advertencia is None

def test_desactivar_modo_seguro(monkeypatch):
    class DummyModo(ModoSeguro):
        def desactivar(self):
            self.advertencia = None
    ctrl = ControladorModoSeguro()
    monkeypatch.setattr(ctrl, 'modo', DummyModo())
    advertencia = ctrl.desactivar_modo_seguro()
    assert advertencia is None

def test_auditar_configuracion(monkeypatch):
    class DummyAuditor(AuditorConfiguracion):
        def revisar_ssh(self):
            return 'SSH seguro.'
    ctrl = ControladorModoSeguro()
    monkeypatch.setattr(ctrl, 'auditor', DummyAuditor())
    resultado = ctrl.auditar_configuracion()
    assert resultado == 'SSH seguro.'
