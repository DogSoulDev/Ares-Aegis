#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Launcher Completo de Ares Aegis
Lanza la interfaz completa con todos los módulos integrados
"""

import sys
import os
from pathlib import Path

# Configurar el path para imports
proyecto_root = Path(__file__).parent.parent
sys.path.insert(0, str(proyecto_root))

# Configurar logging silencioso para Qt
os.environ["QT_LOGGING_RULES"] = "*.debug=false;*.warning=false;qt.qpa.*=false"

try:
    from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QPixmap, QFont
    
    # Importar la interfaz completa
    from antivirus_kali.interfaz.ventana_principal_completa import VentanaPrincipalCompleta
    from antivirus_kali.utilidades.logger import SiemLogger
    
    def main():
        """Función principal del launcher completo"""
        try:
            print("🛡️ Iniciando Ares Aegis - Sistema de Seguridad Completo")
            print("📊 Cargando: Antivirus + Mini-SIEM + Herramientas del Sistema")
            print("=" * 60)
            
            # Configurar aplicación
            app = QApplication(sys.argv)
            app.setApplicationName("Ares Aegis")
            app.setApplicationVersion("2.0")
            app.setOrganizationName("Ares Aegis Security")
            
            # Configurar fuente
            fuente = QFont("Segoe UI", 10)
            app.setFont(fuente)
            
            # Configurar logging
            logger = SiemLogger(__name__)
            logger.info("Iniciando Ares Aegis - Interfaz Completa")
            
            # Crear splash screen simple
            splash = None
            try:
                pixmap = QPixmap(400, 200)
                pixmap.fill(Qt.GlobalColor.blue)
                splash = QSplashScreen(pixmap)
                splash.setStyleSheet("""
                    QSplashScreen {
                        background-color: #2C3E50;
                        color: white;
                        font-size: 14px;
                        font-weight: bold;
                    }
                """)
                splash.showMessage(
                    "🛡️ Ares Aegis\nCargando interfaz completa...", 
                    Qt.AlignmentFlag.AlignCenter,
                    Qt.GlobalColor.white
                )
                splash.show()
                app.processEvents()
            except Exception as e:
                logger.warning(f"No se pudo crear splash screen: {e}")
            
            # Crear ventana principal
            ventana = VentanaPrincipalCompleta()
            
            # Configurar ventana
            ventana.setWindowTitle("Ares Aegis - Sistema de Seguridad Completo")
            ventana.resize(1400, 900)
            
            # Centrar en pantalla
            screen = app.primaryScreen().geometry()
            window_rect = ventana.geometry()
            x = (screen.width() - window_rect.width()) // 2
            y = (screen.height() - window_rect.height()) // 2
            ventana.move(x, y)
            
            # Ocultar splash y mostrar ventana
            if splash:
                splash.finish(ventana)
            
            ventana.show()
            
            logger.info("Interfaz completa iniciada exitosamente")
            print("✅ Interfaz completa cargada exitosamente")
            print("🔧 Todas las herramientas están disponibles")
            print("🚨 Mini-SIEM activado y monitoreando")
            print("🦠 Protección antivirus habilitada")
            
            # Ejecutar aplicación
            return app.exec()
            
        except Exception as e:
            error_msg = f"Error iniciando interfaz completa: {e}"
            print(f"❌ {error_msg}")
            
            try:
                logger = SiemLogger(__name__)
                logger.error(error_msg)
                import traceback
                logger.error(traceback.format_exc())
            except:
                import traceback
                print(traceback.format_exc())
                
            return 1
            
    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("📦 Instale las dependencias necesarias:")
    print("   pip install PySide6")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    import traceback
    print(traceback.format_exc())
    sys.exit(1)
