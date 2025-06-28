

"""
Punto de entrada principal de la aplicación Ares Aegis.
Versión optimizada que utiliza el launcher mejorado.
"""

import sys
import os
from pathlib import Path

# Añadir raíz del proyecto al sys.path para imports universales
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


def main():
    """
    Función principal que lanza Ares Aegis usando el launcher optimizado.
    """
    try:
        # Importar y ejecutar el launcher mejorado
        from antivirus_kali.launcher import main as launcher_main
        return launcher_main()
        
    except ImportError as e:
        print(f"Error importando launcher: {e}")
        print("Intentando con método de respaldo...")
        
        # Método de respaldo usando principal.py
        try:
            from antivirus_kali import principal
            if hasattr(principal, 'main'):
                return principal.main()
            else:
                # Ejecución manual del bloque principal
                return _ejecutar_respaldo()
                
        except Exception as respaldo_error:
            print(f"Error en método de respaldo: {respaldo_error}")
            return 1
    
    except Exception as e:
        print(f"Error crítico al iniciar Ares Aegis: {e}")
        return 1


def _ejecutar_respaldo():
    """
    Método de respaldo para iniciar la aplicación cuando el launcher no está disponible.
    """
    try:
        from PySide6.QtWidgets import QApplication
        from antivirus_kali.interfaz.ventana_principal import VentanaPrincipal
        from antivirus_kali.controladores.controlador_integridad import ControladorIntegridad
        from antivirus_kali.controladores.controlador_red import ControladorRed
        from antivirus_kali.controladores.controlador_privilegios import ControladorPrivilegios
        from antivirus_kali.controladores.controlador_iocs import ControladorIOCs
        from antivirus_kali.controladores.controlador_modo_seguro import ControladorModoSeguro
        from antivirus_kali.controladores.controlador_escaneo_sistema import ControladorEscaneoSistema
        from antivirus_kali.controladores.controlador_mini_siem import ControladorMiniSiemIntegracion
        
        app = QApplication(sys.argv)
        
        # Configuración básica
        rutas_herramientas = ["/usr/bin/nmap", "/usr/bin/wireshark"]
        referencia_hashes = {
            "/usr/bin/nmap": "HASH_DE_REFERENCIA",
            "/usr/bin/wireshark": "HASH_DE_REFERENCIA"
        }
        
        # Crear controladores
        controladores = {
            'escaneo_sistema': ControladorEscaneoSistema(),
            'integridad': ControladorIntegridad(rutas_herramientas, referencia_hashes),
            'red': ControladorRed("192.168.1.0/24"),
            'privilegios': ControladorPrivilegios(),
            'iocs': ControladorIOCs("https://example.com/feed_iocs.txt"),
            'modo_seguro': ControladorModoSeguro(),
            'siem': ControladorMiniSiemIntegracion()
        }
        
        # Crear y mostrar ventana principal
        ventana = VentanaPrincipal(controladores)
        ventana.show()
        
        print("Ares Aegis iniciado en modo de respaldo")
        return app.exec()
        
    except Exception as e:
        print(f"Error en método de respaldo: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
