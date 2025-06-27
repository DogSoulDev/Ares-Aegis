from antivirus_kali.controladores.controlador_privilegios import ControladorPrivilegios
from antivirus_kali.nucleo.monitor_privilegios import MonitorPrivilegios
import pytest

class DummyMonitor(MonitorPrivilegios):
    def procesos_root_sospechosos(self):
        return [
            {'pid': 123, 'name': 'malware', 'username': 'root', 'cmdline': ['malware', '--evil']},
            {'pid': 456, 'name': 'otro', 'username': 'root', 'cmdline': ['otro']}
        ]

def test_controlador_privilegios_detecta_sospechosos(monkeypatch):
    ctrl = ControladorPrivilegios()
    monkeypatch.setattr(ctrl, 'monitor', DummyMonitor())
    sospechosos = ctrl.monitorear_privilegios()
    assert isinstance(sospechosos, list)
    assert len(sospechosos) == 2
    assert sospechosos[0]['name'] == 'malware'

def test_controlador_privilegios_sin_sospechosos(monkeypatch):
    class DummyMonitorVacio(MonitorPrivilegios):
        def procesos_root_sospechosos(self):
            return []
    ctrl = ControladorPrivilegios()
    monkeypatch.setattr(ctrl, 'monitor', DummyMonitorVacio())
    sospechosos = ctrl.monitorear_privilegios()
    assert sospechosos == []
