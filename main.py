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

# Añadir el directorio src al path para importaciones
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

try:
    from vista.interfaz_principal_gui import InterfazPrincipalGUI
    from controladores.controlador_principal import ControladorPrincipal
    from utilidades.escalacion_privilegios import gestionar_privilegios_inicial
except ImportError as e:
    print(f"Error de importación: {e}")
    print("Verifique que todos los módulos están correctamente instalados")
    sys.exit(1)


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


def main():
    """Función principal."""
    print("🛡️  Iniciando Ares Aegis: Antivirus Avanzado para Kali Linux")
    print("=" * 60)

    # Gestionar privilegios antes de continuar
    modo_privilegios = gestionar_privilegios_inicial()

    # Configurar logging
    configurar_logging()
    logger = logging.getLogger(__name__)

    # Mostrar información sobre el modo de ejecución
    if modo_privilegios == 'root':
        print("✅ Ares Aegis iniciado con privilegios completos")
        logger.info("Aplicación iniciada con privilegios de root")
    else:
        print("⚠️  Ares Aegis iniciado en modo limitado")
        logger.warning("Aplicación iniciada en modo limitado")

    try:
        # Inicializar controlador principal
        logger.info("Inicializando controlador principal...")
        controlador = ControladorPrincipal()

        # Configurar el modo de privilegios en el controlador
        controlador.modo_privilegios = modo_privilegios

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

        # Configurar el modo de privilegios en la interfaz
        interfaz.modo_privilegios = modo_privilegios

        # Iniciar loop principal de la GUI
        logger.info("Iniciando bucle principal de la interfaz")
        if modo_privilegios == 'root':
            print("✅ Ares Aegis iniciado correctamente con funcionalidad completa")
        else:
            print("⚠️  Ares Aegis iniciado en modo limitado")
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
