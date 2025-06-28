#!/usr/bin/env python3
"""
Script de inicialización para Ares Aegis con Mini-SIEM
Configura y lanza el sistema completo de seguridad
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Configurar el path para importaciones
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ares_aegis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def mostrar_splash():
    """Mostrar pantalla de carga"""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # Crear splash screen
    splash_pixmap = QPixmap(400, 300)
    splash_pixmap.fill(Qt.GlobalColor.white)
    
    splash = QSplashScreen(splash_pixmap)
    splash.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
    
    # Agregar texto al splash
    font = QFont("Arial", 16, QFont.Weight.Bold)
    splash.setFont(font)
    splash.showMessage(
        "🛡️ ARES AEGIS\nSistema de Seguridad Avanzado\n\nInicializando...",
        Qt.AlignmentFlag.AlignCenter,
        Qt.GlobalColor.black
    )
    
    splash.show()
    app.processEvents()
    
    return splash, app

def verificar_dependencias():
    """Verificar que todas las dependencias estén disponibles"""
    dependencias = [
        'PySide6',
        'asyncio',
        'sqlite3',
        'json',
        'datetime',
        'logging'
    ]
    
    faltantes = []
    for dep in dependencias:
        try:
            __import__(dep)
        except ImportError:
            faltantes.append(dep)
    
    if faltantes:
        error_msg = f"Dependencias faltantes: {', '.join(faltantes)}"
        logger.error(error_msg)
        return False, error_msg
    
    return True, "Todas las dependencias están disponibles"

def verificar_permisos():
    """Verificar permisos necesarios para el sistema"""
    try:
        # Verificar escritura en directorio actual
        test_file = Path("test_permisos.tmp")
        test_file.write_text("test")
        test_file.unlink()
        
        # Verificar acceso a logs del sistema (para SIEM)
        log_paths = [
            "/var/log/auth.log",
            "/var/log/syslog",
            "/var/log/dpkg.log"
        ]
        
        acceso_logs = []
        for log_path in log_paths:
            if Path(log_path).exists() and os.access(log_path, os.R_OK):
                acceso_logs.append(log_path)
        
        logger.info(f"Acceso a logs: {len(acceso_logs)}/{len(log_paths)} archivos")
        return True, f"Permisos verificados. Acceso a {len(acceso_logs)} logs"
        
    except Exception as e:
        return False, f"Error verificando permisos: {e}"

def inicializar_componentes():
    """Inicializar todos los componentes del sistema"""
    try:
        # Importar controladores principales
        from antivirus_kali.controladores.controlador_mini_siem import ControladorMiniSiemIntegracion
        
        # Crear controladores
        controladores = {
            'siem': ControladorMiniSiemIntegracion()
        }
        
        logger.info("Controladores inicializados correctamente")
        return True, controladores
        
    except Exception as e:
        error_msg = f"Error inicializando componentes: {e}"
        logger.error(error_msg)
        return False, error_msg

def main():
    """Función principal de inicialización"""
    try:
        # Mostrar splash screen
        splash, app = mostrar_splash()
        
        # Verificaciones iniciales
        splash.showMessage("Verificando dependencias...", Qt.AlignmentFlag.AlignCenter)
        app.processEvents()
        
        exito, mensaje = verificar_dependencias()
        if not exito:
            QMessageBox.critical(None, "Error", mensaje)
            return 1
        
        splash.showMessage("Verificando permisos...", Qt.AlignmentFlag.AlignCenter)
        app.processEvents()
        
        exito, mensaje = verificar_permisos()
        if not exito:
            QMessageBox.warning(None, "Advertencia", mensaje)
        
        splash.showMessage("Inicializando componentes...", Qt.AlignmentFlag.AlignCenter)
        app.processEvents()
        
        exito, resultado = inicializar_componentes()
        if not exito:
            QMessageBox.critical(None, "Error", str(resultado))
            return 1
        
        controladores = resultado
        
        splash.showMessage("Cargando interfaz principal...", Qt.AlignmentFlag.AlignCenter)
        app.processEvents()
        
        # Importar y crear ventana principal
        from antivirus_kali.interfaz.ventana_principal import VentanaPrincipal
        
        ventana = VentanaPrincipal(controladores)
        
        # Cerrar splash y mostrar ventana principal
        splash.close()
        ventana.show()
        
        # Inicializar SIEM en background
        QTimer.singleShot(2000, lambda: asyncio.create_task(ventana.inicializar_siem()))
        
        logger.info("Ares Aegis iniciado exitosamente")
        
        # Ejecutar aplicación
        return app.exec()
        
    except Exception as e:
        logger.error(f"Error crítico en inicialización: {e}")
        QMessageBox.critical(None, "Error Crítico", f"No se pudo iniciar Ares Aegis:\n{str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
