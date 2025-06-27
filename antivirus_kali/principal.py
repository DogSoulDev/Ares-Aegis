"""
Punto de entrada principal de la aplicación Ares Aegis.
Inicializa controladores y lanza la interfaz principal.
"""

import sys
from PySide6.QtWidgets import QApplication
from antivirus_kali.interfaz.ventana_principal import VentanaPrincipal
from antivirus_kali.controladores.controlador_integridad import ControladorIntegridad
from antivirus_kali.controladores.controlador_red import ControladorRed
from antivirus_kali.controladores.controlador_privilegios import ControladorPrivilegios
from antivirus_kali.controladores.controlador_iocs import ControladorIOCs
from antivirus_kali.controladores.controlador_modo_seguro import ControladorModoSeguro
from antivirus_kali.controladores.controlador_escaneo_sistema import ControladorEscaneoSistema


if __name__ == "__main__":
    print("""
    =============================================
      🛡️  Ares Aegis - Antivirus modular para Kali Linux
    =============================================
    """)
    app = QApplication(sys.argv)
    # Configuración de ejemplo para pruebas
    rutas_herramientas = ["/usr/bin/nmap", "/usr/bin/wireshark"]
    referencia_hashes = {"/usr/bin/nmap": "HASH_DE_REFERENCIA", "/usr/bin/wireshark": "HASH_DE_REFERENCIA"}
    controladores = {
        'escaneo_sistema': ControladorEscaneoSistema(),  # Panel principal
        'integridad': ControladorIntegridad(rutas_herramientas, referencia_hashes),
        'red': ControladorRed("192.168.1.0/24"),
        'privilegios': ControladorPrivilegios(),
        'iocs': ControladorIOCs("https://example.com/feed_iocs.txt"),
        'modo_seguro': ControladorModoSeguro(),
    }
    ventana = VentanaPrincipal(controladores)
    ventana.show()
    sys.exit(app.exec())
