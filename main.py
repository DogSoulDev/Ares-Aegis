#!/usr/bin/env python3
"""
Ares Aegis: Antivirus Avanzado para Kali Linux
Punto de entrada principal de la aplicación

Autor: DogSoulDev
Versión: 2.0.0
Licencia: GPL v3
"""

import sys
import os
import logging
from pathlib import Path

# Agregar el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from vista.interfaz_principal_gui import InterfazPrincipalGUI
import tkinter as tk


def configurar_registro():
    """Configura el sistema de registro."""
    directorio_log = Path("/var/log/ares_aegis")
    try:
        directorio_log.mkdir(parents=True, exist_ok=True)
        archivo_log = directorio_log / "ares_aegis.log"
    except PermissionError:
        # Fallback para desarrollo sin privilegios root
        archivo_log = Path.home() / ".ares_aegis" / "ares_aegis.log"
        archivo_log.parent.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(archivo_log),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    registrador = logging.getLogger(__name__)
    registrador.info("=== Iniciando Ares Aegis ===")
    return registrador


def verificar_privilegios_root():
    """Verifica si se ejecuta con privilegios root."""
    if os.geteuid() != 0:
        print("ERROR: Ares Aegis requiere privilegios root.")
        print("Ejecute: sudo python3 main.py")
        return False
    return True

def main():
    """Función principal."""
    if not verificar_privilegios_root():
        sys.exit(1)
    
    registrador = configurar_registro()
    
    try:
        # Crear ventana principal
        ventana_raiz = tk.Tk()
        
        # Inicializar aplicación
        aplicacion = InterfazPrincipalGUI(ventana_raiz)
        
        # Ejecutar bucle principal
        ventana_raiz.mainloop()
        
    except Exception as e:
        registrador.error(f"Error crítico: {e}")
        sys.exit(1)
    
    registrador.info("=== Finalizando Ares Aegis ===")


if __name__ == "__main__":
    main()
