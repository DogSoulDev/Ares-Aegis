from antivirus_kali.nucleo.escaneo_sistema import EscaneoSistema
import tempfile
import pytest
from unittest.mock import patch

def test_escanear_rootkits():
    escaneo = EscaneoSistema()
    with patch('subprocess.check_output', return_value='rootkit1\nrootkit2') as mock_sub:
        result = escaneo.escanear_rootkits()
        assert isinstance(result, list)
        assert result == ['rootkit1', 'rootkit2']

def test_escanear_procesos():
    escaneo = EscaneoSistema()
    with patch('subprocess.check_output', return_value='user1 1234 suspicious_process\nuser2 5678 malware'):
        result = escaneo.escanear_procesos_sospechosos()
        assert isinstance(result, list)
        assert any('suspicious' in r or 'malware' in r for r in result)

def test_escanear_puertos():
    escaneo = EscaneoSistema()
    with patch('subprocess.check_output', return_value='tcp LISTEN 0 128 *:22 *:*\nudp UNCONN 0 0 *:68 *:*'):
        result = escaneo.escanear_puertos_abiertos()
        assert isinstance(result, list)
        assert any('tcp' in r or 'udp' in r for r in result)

def test_escanear_servicios():
    escaneo = EscaneoSistema()
    with patch('subprocess.check_output', return_value='sshd.service loaded active running OpenSSH Daemon'):
        result = escaneo.escanear_servicios_activos()
        assert isinstance(result, list)
        assert any('sshd' in r for r in result)

def test_escanear_integridad():
    escaneo = EscaneoSistema()
    base = {'/bin/ls': 'HASH_FAKE'}
    with patch.object(EscaneoSistema, 'calcular_hash_archivo', return_value='HASH_FAKE'):
        result = escaneo.escanear_integridad_binarios(base)
        assert isinstance(result, dict)
        assert result == {}

def test_obtener_programas():
    escaneo = EscaneoSistema()
    with patch('subprocess.check_output', return_value='nano\nvim\npython3'):
        result = escaneo.obtener_programas_instalados()
        assert isinstance(result, list)
        assert 'nano' in result and 'vim' in result and 'python3' in result
