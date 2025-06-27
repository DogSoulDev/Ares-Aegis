import importlib

def test_dependencia_scapy():
    try:
        importlib.import_module('scapy')
    except ImportError:
        assert False, 'scapy no está instalado'

def test_dependencia_ufw():
    try:
        importlib.import_module('ufw')
    except ImportError:
        # ufw puede no tener módulo Python, pero debe estar el binario
        import shutil
        assert shutil.which('ufw'), 'ufw no está instalado ni como binario'
