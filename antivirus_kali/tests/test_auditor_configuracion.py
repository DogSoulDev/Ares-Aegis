from antivirus_kali.nucleo.auditor_configuracion import AuditorConfiguracion
import builtins
import pytest

def test_revisar_ssh_root(monkeypatch):
    def fake_open(file, *args, **kwargs):
        class DummyFile:
            def read(self):
                return 'PermitRootLogin yes'
            def __enter__(self): return self
            def __exit__(self, exc_type, exc_val, exc_tb): pass
        return DummyFile()
    monkeypatch.setattr(builtins, 'open', fake_open)
    auditor = AuditorConfiguracion()
    assert 'PermitRootLogin' in auditor.revisar_ssh()

def test_revisar_ssh_seguro(monkeypatch):
    def fake_open(file, *args, **kwargs):
        class DummyFile:
            def read(self):
                return 'PermitRootLogin no'
            def __enter__(self): return self
            def __exit__(self, exc_type, exc_val, exc_tb): pass
        return DummyFile()
    monkeypatch.setattr(builtins, 'open', fake_open)
    auditor = AuditorConfiguracion()
    assert auditor.revisar_ssh() == 'SSH seguro.'

def test_revisar_ssh_error(monkeypatch):
    def fake_open(file, *args, **kwargs):
        raise IOError('fail')
    monkeypatch.setattr(builtins, 'open', fake_open)
    auditor = AuditorConfiguracion()
    assert 'No se pudo revisar SSH' in auditor.revisar_ssh()
