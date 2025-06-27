from antivirus_kali.nucleo.monitor_privilegios import MonitorPrivilegios
import pytest

def test_procesos_root_sospechosos_vacio(monkeypatch):
    class DummyPsutil:
        def process_iter(self, attrs):
            return []
    monkeypatch.setattr('psutil.process_iter', lambda attrs: [])
    monitor = MonitorPrivilegios()
    assert monitor.procesos_root_sospechosos() == []

def test_procesos_root_sospechosos_detecta(monkeypatch):
    class DummyProc:
        def __init__(self, info):
            self.info = info
    procesos = [
        DummyProc({'pid': 1, 'name': 'systemd', 'username': 'root', 'cmdline': ['systemd']}),
        DummyProc({'pid': 2, 'name': 'malware', 'username': 'root', 'cmdline': ['malware']}),
        DummyProc({'pid': 3, 'name': 'otro', 'username': 'root', 'cmdline': ['otro']})
    ]
    monkeypatch.setattr('psutil.process_iter', lambda attrs: procesos)
    monitor = MonitorPrivilegios()
    sospechosos = monitor.procesos_root_sospechosos()
    assert any(p['name'] == 'malware' for p in sospechosos)
    assert all(p['username'] == 'root' for p in sospechosos)
