
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Punto de entrada principal para Ares-Aegis
Launcher con interfaz minimalista japonesa
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
    Función principal que lanza Ares Aegis con interfaz minimalista limpia.
    """
    try:
        # Importar y ejecutar el launcher simple
        from antivirus_kali.launcher_simple import main as launcher_simple
        return launcher_simple()
        
    except ImportError as e:
        print(f"Error importando launcher simple: {e}")
        print("Intentando con launcher minimalista...")
        
        # Método de respaldo usando launcher minimalista
        try:
            from antivirus_kali.launcher_minimalista import main as launcher_min
            return launcher_min()
            
        except Exception as respaldo_error:
            print(f"Error en launcher minimalista: {respaldo_error}")
            print("Intentando método de respaldo...")
            return _ejecutar_respaldo()
    
    except Exception as e:
        print(f"Error crítico al iniciar Ares Aegis: {e}")
        return _ejecutar_respaldo()


def _ejecutar_respaldo():
    """
    Método de respaldo para iniciar la aplicación cuando los launchers no están disponibles.
    """
    try:
        from PySide6.QtWidgets import QApplication
        from antivirus_kali.interfaz.ventana_principal_minimalista import VentanaPrincipalMinimalista
        
        app = QApplication(sys.argv)
        app.setApplicationName("Ares-Aegis")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("Ares-Aegis Security")
        
        # Crear y mostrar ventana principal minimalista
        ventana = VentanaPrincipalMinimalista()
        ventana.show()
        
        print("Ares Aegis iniciado en modo de respaldo con interfaz minimalista")
        return app.exec()
        
    except Exception as e:
        print(f"Error en método de respaldo: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
