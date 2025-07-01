#!/usr/bin/env python3
"""
Ares Aegis - Sistema Antivirus y SIEM
Punto de entrada principal del sistema

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import sys
import time
import signal
from pathlib import Path

def verificar_privilegios():
    """Verifica si el script se ejecuta con privilegios de administrador."""
    if os.geteuid() != 0:
        print("🚨 Error: Este programa requiere privilegios de administrador")
        print("💡 Ejecuta con: sudo python3 main.py")
        sys.exit(1)

def manejar_senal(signum, frame):
    """Maneja las señales del sistema para cierre limpio."""
    print("\n🛑 Señal de interrupción recibida. Cerrando Ares Aegis...")
    # Aquí se podría agregar limpieza adicional
    sys.exit(0)

def main():
    """Función principal."""
    # Configurar manejo de señales
    signal.signal(signal.SIGINT, manejar_senal)
    signal.signal(signal.SIGTERM, manejar_senal)
    
    print("🛡️  Iniciando Ares Aegis - Sistema Antivirus y SIEM")
    print("=" * 50)
    
    # Verificar privilegios
    verificar_privilegios()
    
    try:
        # Importar e inicializar la interfaz principal
        from ares_aegis.vista.interfaz_principal_gui import InterfazPrincipalGUI
        
        print("🔧 Inicializando interfaz gráfica...")
        interfaz = InterfazPrincipalGUI()
        
        print("✅ Sistema iniciado exitosamente")
        print("🖥️  Abriendo interfaz gráfica...")
        
        # Ejecutar la interfaz
        interfaz.ejecutar()
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que todos los módulos estén presentes")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
    finally:
        print("🔒 Ares Aegis finalizado")

if __name__ == "__main__":
    main()
