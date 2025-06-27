"""
Punto de entrada principal de la aplicación Ares Aegis.
Inicializa controladores y lanza la interfaz principal.
"""


import sys
import os
# Asegurar que el directorio raíz del proyecto está en sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from PySide6.QtWidgets import QApplication
from antivirus_kali.interfaz.ventana_principal import VentanaPrincipal
from antivirus_kali.controladores.controlador_integridad import ControladorIntegridad
from antivirus_kali.controladores.controlador_red import ControladorRed
from antivirus_kali.controladores.controlador_privilegios import ControladorPrivilegios
from antivirus_kali.controladores.controlador_iocs import ControladorIOCs
from antivirus_kali.controladores.controlador_modo_seguro import ControladorModoSeguro
from antivirus_kali.controladores.controlador_escaneo_sistema import ControladorEscaneoSistema


if __name__ == "__main__":
    import os
    import traceback
    try:
        app = QApplication(sys.argv)
        rutas_herramientas = [
            "/bin/ls", "/bin/bash", "/usr/bin/apt", "/usr/bin/nmap", "/usr/bin/wireshark", "/usr/bin/python3", "/usr/bin/ufw"
        ]
        referencia_hashes = {}
        controladores = {
            'escaneo_sistema': ControladorEscaneoSistema(),
            'integridad': ControladorIntegridad(rutas_herramientas, referencia_hashes),
            'red': ControladorRed("192.168.1.0/24"),
            'privilegios': ControladorPrivilegios(),
            'iocs': ControladorIOCs("https://feodotracker.abuse.ch/downloads/ipblocklist.txt"),
            'modo_seguro': ControladorModoSeguro(),
        }
        ventana = VentanaPrincipal(controladores)
        ventana.show()
        sys.exit(app.exec())
    except Exception as e:
        # Loguear error en archivo visible para el wrapper
        with open("/tmp/ares_aegis_python_error.log", "w") as f:
            f.write("[Ares-Aegis Python Error] " + str(e) + "\n")
            f.write(traceback.format_exc())
        # Mostrar error en terminal si es posible
        print("[Ares-Aegis] Error crítico al iniciar la aplicación. Revisa /tmp/ares_aegis_python_error.log", file=sys.stderr)
        sys.exit(1)
