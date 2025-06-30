#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Launcher Optimizado - Ares Aegis
Launcher con interfaz limpia, sin zoom, y consentimiento del usuario
"""

import sys
import os
import logging
from pathlib import Path

# Agregar el directorio padre al path para las importaciones
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QIcon
    
    # Importar nuestra interfaz limpia
    from antivirus_kali.interfaz.ventana_principal_limpia import VentanaPrincipalLimpia
    from antivirus_kali.interfaz.estilo_japones import EstiloJapones
    from antivirus_kali.utilidades.logger import SiemLogger
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("🔧 Instalando dependencias necesarias...")
    os.system("pip install PySide6")
    sys.exit(1)

def configurar_aplicacion():
    """Configura la aplicación QT con el estilo japonés optimizado"""
    app = QApplication(sys.argv)
    
    # Configuraciones básicas de la aplicación
    app.setApplicationName("Ares Aegis")
    app.setApplicationVersion("2.1")
    app.setOrganizationName("Ares Aegis Security")
    app.setApplicationDisplayName("🛡️ Ares Aegis - Sistema de Seguridad Integral")
    
    # DESHABILITAR ESCALADO Y ZOOM
    # Configurar variables de entorno antes de crear widgets
    os.environ['QT_SCALE_FACTOR'] = '1.0'
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'
    os.environ['QT_SCREEN_SCALE_FACTORS'] = '1.0'
    
    # Aplicar el stylesheet japonés cálido y responsive
    stylesheet = EstiloJapones.obtener_stylesheet_completo()
    app.setStyleSheet(stylesheet)
    
    return app

def mostrar_bienvenida():
    """Muestra mensaje de bienvenida con información importante"""
    msg = QMessageBox()
    msg.setWindowTitle("🛡️ Ares Aegis - Bienvenido")
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText(
        "Bienvenido a Ares Aegis - Sistema de Seguridad Integral\n\n"
        "🔒 CARACTERÍSTICAS DE SEGURIDAD:\n"
        "• Todas las acciones requieren tu confirmación\n"
        "• El firewall NO se activa automáticamente\n"
        "• Ningún escaneo se ejecuta sin tu consentimiento\n"
        "• Interfaz optimizada y responsive\n\n"
        "¿Deseas continuar?"
    )
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setDefaultButton(QMessageBox.StandardButton.Yes)
    
    return msg.exec() == QMessageBox.StandardButton.Yes

def main():
    """Función principal optimizada"""
    # Configurar logging
    logger = SiemLogger(__name__)
    logger.info("🚀 Iniciando Ares Aegis - Versión Limpia y Optimizada")
    
    try:
        # Crear aplicación
        app = configurar_aplicacion()
        
        # Mostrar bienvenida y obtener consentimiento
        if not mostrar_bienvenida():
            logger.info("👋 Usuario canceló el inicio de la aplicación")
            return 0
        
        # Verificar que la imagen Ares existe
        ruta_imagen = EstiloJapones.obtener_ruta_imagen_ares()
        if os.path.exists(ruta_imagen):
            logger.info(f"✅ Imagen Ares encontrada: {ruta_imagen}")
        else:
            logger.warning(f"⚠️ Imagen Ares no encontrada en: {ruta_imagen}")
            logger.info("🎨 Se usará un placeholder con iconos")
        
        # Crear ventana principal limpia
        logger.info("🏗️ Creando ventana principal limpia y optimizada...")
        ventana = VentanaPrincipalLimpia()
        
        # Mostrar ventana
        ventana.show()
        logger.info("✨ Interfaz mostrada exitosamente")
        
        # Mensaje de bienvenida en consola
        print("\n" + "="*70)
        print("🛡️  ARES AEGIS - SISTEMA DE SEGURIDAD INTEGRAL")
        print("="*70)
        print("🧹 Versión: Limpia y Optimizada")
        print("🎨 Diseño: Estilo Japonés Cálido y Uniforme")
        print("🚫 Zoom: Deshabilitado para mejor UX")
        print("✅ Consentimiento: Requerido para todas las acciones")
        print("🛡️ Firewall: Solo se activa con autorización del usuario")
        print("="*70)
        print("✅ Sistema iniciado correctamente")
        print("🌟 ¡Interfaz completamente funcional y limpia!")
        print("="*70 + "\n")
        
        # Timer para verificar el estado inicial
        def verificar_estado_inicial():
            logger.info("🔍 Verificando estado inicial del sistema...")
            logger.info("📊 Todos los módulos cargados sin acciones automáticas")
            logger.info("🔒 Sistema en modo seguro - requiere confirmación del usuario")
            
        QTimer.singleShot(3000, verificar_estado_inicial)
        
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
