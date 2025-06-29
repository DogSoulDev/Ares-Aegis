#!/usr/bin/env python3
"""
Ares Aegis - Antivirus Avanzado para Kali Linux
Punto de entrada principal del sistema

Autor: DogSoulDev
Versión: 2.0.0
"""

import sys
import os
import logging

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal que delega al main de src."""
    try:
        # Importar y ejecutar el main desde src
        import main as src_main
        return src_main.main()
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("   Verifique que la estructura del proyecto esté correcta")
        return 1
    except Exception as e:
        print(f"❌ Error ejecutando Ares Aegis: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
