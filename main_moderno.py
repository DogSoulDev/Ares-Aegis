#!/usr/bin/env python3
"""
Ares Aegis - Sistema Avanzado de Ciberseguridad
Punto de entrada con INTERFAZ MODERNA

Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Versión: 3.0.0 - Interfaz Moderna
"""

import sys
import os
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ares_aegis.vista.interfaz_moderna_nueva import InterfazModerna
from ares_aegis.utilidades.ayuda_logging import configurar_logging_completo


def main():
    """Función principal de entrada con interfaz moderna."""
    try:
        logger = configurar_logging_completo()
        
        logger.info("=" * 60)
        logger.info("Iniciando Ares Aegis - INTERFAZ MODERNA")
        logger.info("=" * 60)
        
        app = InterfazModerna()
        app.ejecutar()
        
        return True
        
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario")
        logging.info("Aplicación interrumpida por el usuario")
        return True
        
    except Exception as e:
        print(f"Error crítico: {e}")
        logging.error(f"Error crítico en main moderno: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
