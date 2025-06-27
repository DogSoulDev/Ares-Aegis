import builtins
import pytest
import sys
from unittest.mock import patch

def test_no_password_terminal():
    # Simula input y getpass para asegurar que nunca se imprime la contraseña
    with patch('builtins.input', side_effect=Exception("No se debe pedir input de contraseña en terminal")):
        with patch('getpass.getpass', side_effect=Exception("No se debe pedir getpass en terminal")):
            import importlib
            # Si el módulo no está cargado, impórtalo primero
            if 'antivirus_kali.principal' not in sys.modules:
                import antivirus_kali.principal
            importlib.reload(sys.modules['antivirus_kali.principal'])
            assert True
