#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Launcher Simple para Ares-Aegis
Interfaz minimalista sin problemas de asyncio ni logging excesivo
"""

import sys
import os
from pathlib import Path

# Configurar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))

try:
    from PySide6.QtWidgets import QApplication
    from antivirus_kali.interfaz.ventana_principal_minimalista import VentanaPrincipalMinimalista
    
except ImportError as e:
    print(f"Error: {e}")
    print("Instalando dependencias necesarias...")
    os.system("pip install PySide6")
    sys.exit(1)


def main():
    """Función principal simplificada"""
    try:
        # Suprimir warnings de Qt sobre CSS
        os.environ['QT_LOGGING_RULES'] = '*.debug=false;*.warning=false'
        
        # Crear aplicación
        app = QApplication(sys.argv)
        app.setApplicationName("Ares-Aegis")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("Ares-Aegis Security")
        
        # Crear y mostrar ventana
        ventana = VentanaPrincipalMinimalista()
        ventana.show()
        
        print("Ares-Aegis iniciado exitosamente")
        
        # Ejecutar aplicación
        return app.exec()
        
    except Exception as e:
        print(f"Error al iniciar Ares-Aegis: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
