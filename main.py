#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🛡️ Ares Aegis - Sistema Antivirus y SIEM
🎌 Archivo Principal de Inicio
📅 Fecha: 3 de Julio, 2025
👤 Autor: DogSoulDev
🔰 Versión: 2.0.0

🌸 "En el silencio del código, la protección florece como sakura en primavera" 🌸
"""

import sys
import os
import signal
import logging
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar el logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ares_aegis.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('AresAegis')

def mostrar_banner():
    """🎌 Muestra el banner artístico del sistema"""
    banner = """
🎌 ════════════════════════════════════════════════════════════════════════ 🎌
    
            🛡️  ARES AEGIS - SISTEMA ANTIVIRUS Y SIEM  🛡️
            
    🌸 "En el silencio del código, la protección florece como sakura" 🌸
    
    🔰 Versión: 2.0.0
    👤 Autor: DogSoulDev  
    📅 Fecha: 3 de Julio, 2025
    🏯 Arquitectura: Estilo Japonés Moderno
    
    ⚔️  MÓDULOS ACTIVOS:
    🔍 Escaneador de Archivos       | 🌐 Monitor de Red
    🧬 Análisis Dinámico           | 📊 SIEM Inteligente  
    🔐 FIM (File Integrity)        | 🚨 Sistema de Alertas
    🛡️  Descontaminación          | 📈 Reportes Épicos
    
🎌 ════════════════════════════════════════════════════════════════════════ 🎌
"""
    print(banner)

def verificar_permisos():
    """🔒 Verifica que el programa se ejecute con permisos adecuados"""
    if os.geteuid() != 0:
        logger.warning("⚠️  Ejecutándose sin privilegios de root")
        logger.info("💡 Algunas funciones pueden estar limitadas")
        return False
    return True

def signal_handler(signum, frame):
    """🔌 Manejador de señales para cierre limpio"""
    logger.info("🔒 Recibida señal de cierre, finalizando Ares Aegis...")
    sys.exit(0)

def main():
    """🚀 Función principal"""
    try:
        # Configurar manejadores de señales
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Mostrar banner
        mostrar_banner()
        
        # Verificar permisos
        tiene_permisos = verificar_permisos()
        if tiene_permisos:
            logger.info("✅ Ejecutándose con privilegios de administrador")
        
        # Importar y crear el controlador principal
        from ares_aegis.controladores.controlador_principal import ControladorPrincipal
        
        logger.info("🔧 Inicializando sistema Ares Aegis...")
        
        # Crear el controlador principal
        controlador = ControladorPrincipal()
        
        logger.info("✅ Sistema Ares Aegis iniciado correctamente")
        logger.info("🎌 Para detener el sistema usa Ctrl+C")
        
        # Ejecutar el controlador principal
        controlador.ejecutar()
        
    except ImportError as e:
        logger.error(f"❌ Error de importación: {e}")
        logger.error("💡 Verifica que todos los módulos estén instalados")
        sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("🔒 Cierre del sistema solicitado por el usuario")
        
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        logger.error("🔧 Contacta con el desarrollador para soporte")
        sys.exit(1)
        
    finally:
        logger.info("🙏 ¡Gracias por usar Ares Aegis!")

if __name__ == "__main__":
    try:
        # Ejecutar la función principal
        main()
    except KeyboardInterrupt:
        print("\n🔒 Ares Aegis finalizado por el usuario")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1)
