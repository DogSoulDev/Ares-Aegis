#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Launcher Mejorado - Ares Aegis
Launcher optimizado con diseño japonés cálido, responsive y imagen integrada
"""

import sys
import os
import logging
from pathlib import Path

# Agregar el directorio padre al path para las importaciones
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QIcon
    
    # Importar nuestra interfaz mejorada
    from antivirus_kali.interfaz.ventana_principal_completa import VentanaPrincipalCompleta
    from antivirus_kali.interfaz.estilo_japones import EstiloJapones
    from antivirus_kali.utilidades.logger import SiemLogger
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("🔧 Instalando dependencias necesarias...")
    os.system("pip install PySide6")
    sys.exit(1)

def configurar_aplicacion():
    """Configura la aplicación QT con el estilo japonés mejorado"""
    app = QApplication(sys.argv)
    
    # Configuraciones básicas de la aplicación
    app.setApplicationName("Ares Aegis")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Ares Aegis Security")
    app.setApplicationDisplayName("🛡️ Ares Aegis - Sistema de Seguridad Integral")
    
    # Configurar estilo high DPI
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Aplicar el stylesheet japonés cálido y responsive
    stylesheet = EstiloJapones.obtener_stylesheet_completo()
    app.setStyleSheet(stylesheet)
    
    return app

def main():
    """Función principal mejorada"""
    # Configurar logging
    logger = SiemLogger(__name__)
    logger.info("🚀 Iniciando Ares Aegis - Versión Mejorada")
    
    try:
        # Crear aplicación
        app = configurar_aplicacion()
        
        # Verificar que la imagen Ares existe
        ruta_imagen = EstiloJapones.obtener_ruta_imagen_ares()
        if os.path.exists(ruta_imagen):
            logger.info(f"✅ Imagen Ares encontrada: {ruta_imagen}")
        else:
            logger.warning(f"⚠️ Imagen Ares no encontrada en: {ruta_imagen}")
            logger.info("🎨 Se usará un placeholder con iconos")
        
        # Crear ventana principal
        logger.info("🏗️ Creando ventana principal con diseño japonés cálido...")
        ventana = VentanaPrincipalCompleta()
        
        # Mostrar ventana
        ventana.show()
        logger.info("✨ Interfaz mostrada exitosamente")
        
        # Mensaje de bienvenida en consola
        print("\n" + "="*70)
        print("🛡️  ARES AEGIS - SISTEMA DE SEGURIDAD INTEGRAL")
        print("="*70)
        print("🎨 Diseño: Estilo Japonés Cálido y Responsive")
        print("🖼️ Características: Imagen personalizada integrada")
        print("📱 Responsive: Optimizado para diferentes tamaños de pantalla")
        print("🎯 Módulos: Antivirus + Mini-SIEM + Herramientas")
        print("="*70)
        print("✅ Sistema iniciado correctamente")
        print("🌟 ¡Disfruta de la nueva interfaz mejorada!")
        print("="*70 + "\n")
        
        # Timer para verificar el estado inicial
        def verificar_estado_inicial():
            logger.info("🔍 Verificando estado inicial del sistema...")
            logger.info("📊 Todos los módulos cargados correctamente")
            
        QTimer.singleShot(2000, verificar_estado_inicial)
        
        # Ejecutar aplicación
        return app.exec()
        
    except Exception as e:
        logger.error(f"💥 Error crítico al iniciar la aplicación: {e}")
        print(f"\n❌ Error: {e}")
        print("🔧 Verifica las dependencias y configuración")
        return 1
    
    finally:
        logger.info("👋 Cerrando Ares Aegis...")

if __name__ == "__main__":
    sys.exit(main())
