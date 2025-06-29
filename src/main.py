#!/usr/bin/env python3
"""
Punto de Entrada Principal - Ares Aegis
Antivirus Avanzado para Kali Linux

Autor: DogSoulDev
Versión: 2.0.0
"""

import sys
import os
import tkinter as tk
import logging

# Añadir el directorio actual al path para importaciones
sys.path.insert(0, os.path.dirname(__file__))

from vista.interfaz_principal_gui import InterfazPrincipalGUI
from controladores.controlador_principal import ControladorPrincipal


def configurar_logging():
    """Configura el sistema de logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ares_aegis.log'),
            logging.StreamHandler()
        ]
    )


def verificar_privilegios():
    """Verifica si se ejecuta con privilegios de root."""
    if os.geteuid() != 0:
        print("❌ ERROR: Ares Aegis requiere privilegios de root")
        print("   Ejecute: sudo python3 src/main.py")
        return False
    return True


def main():
    """Función principal."""
    print("🛡️  Iniciando Ares Aegis: Antivirus Avanzado para Kali Linux")
    print("=" * 60)
    
    # Configurar logging
    configurar_logging()
    logger = logging.getLogger(__name__)
    
    # Verificar privilegios (solo advertencia para testing)
    if not verificar_privilegios():
        print("⚠️  ADVERTENCIA: Ejecutando sin privilegios de root")
        print("   Algunas funciones pueden no estar disponibles")
    
    try:
        # Inicializar controlador principal
        logger.info("Inicializando controlador principal...")
        controlador = ControladorPrincipal()
        
        # Intentar iniciar el sistema
        if controlador.iniciar_sistema():
            logger.info("Sistema iniciado correctamente")
        else:
            logger.warning("Sistema iniciado con limitaciones")
        
        # Crear ventana principal
        logger.info("Creando interfaz gráfica...")
        root = tk.Tk()
        
        # Inicializar interfaz
        interfaz = InterfazPrincipalGUI(root, controlador)
        
        # Iniciar loop principal de la GUI
        logger.info("Iniciando bucle principal de la interfaz")
        print("✅ Ares Aegis iniciado correctamente")
        print("   Interfaz gráfica disponible")
        
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n⚡ Interrupción por teclado detectada")
        logger.info("Aplicación cerrada por el usuario")
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        logger.error(f"Error crítico en main: {e}")
        return 1
    
    finally:
        print("🔒 Ares Aegis finalizado")
        logger.info("Aplicación finalizada")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
