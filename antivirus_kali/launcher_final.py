#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Launcher Final - Ares Aegis
Interfaz completamente limpia, uniforme y funcional
"""

import sys
import os
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt
    
    # Importar la interfaz limpia
    from antivirus_kali.interfaz.ventana_principal_limpia import VentanaPrincipalLimpia
    from antivirus_kali.utilidades.logger import SiemLogger
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    os.system("pip install PySide6")
    sys.exit(1)

def aplicar_estilo_basico(app):
    """Aplica un estilo básico japonés sin problemas de parsing"""
    estilo = """
    /* Estilo Japonés Básico y Funcional */
    QMainWindow {
        background-color: #FFF8E7;
        color: #2F1B14;
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
    }
    
    QWidget {
        background-color: transparent;
        color: #2F1B14;
    }
    
    /* Panel de Navegación */
    QWidget[esPanelNavegacion="true"] {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
            stop:0 #F5E6D3, stop:1 #E8D5B7);
        border-right: 2px solid #8B4513;
        padding: 16px;
    }
    
    /* Títulos */
    QLabel[estiloTitulo="true"] {
        color: #8B4513;
        font-weight: bold;
        font-size: 18px;
        padding: 16px;
        margin: 8px 0px;
        background-color: #F0E68C;
        border-radius: 8px;
        border-left: 3px solid #8B4513;
    }
    
    QLabel[estiloSubtitulo="true"] {
        color: #CD853F;
        font-weight: 600;
        font-size: 14px;
        padding: 8px 12px;
        margin: 6px 0px;
        background-color: #F5E6D3;
        border-radius: 6px;
    }
    
    /* Botones */
    QPushButton {
        background-color: #F5E6D3;
        border: 2px solid #DEB887;
        color: #2F1B14;
        padding: 8px 12px;
        margin: 4px;
        border-radius: 6px;
        font-size: 14px;
        min-height: 32px;
    }
    
    QPushButton:hover {
        background-color: #F0E68C;
        border-color: #8B4513;
        color: #8B4513;
    }
    
    QPushButton:pressed {
        background-color: #8B4513;
        color: #FFF8E7;
    }
    
    QPushButton[esPrimario="true"] {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
            stop:0 #8B4513, stop:1 #CD853F);
        color: #FFF8E7;
        font-weight: bold;
        border: none;
    }
    
    QPushButton[esPrimario="true"]:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
            stop:0 #CD853F, stop:1 #8B4513);
    }
    
    QPushButton[esBotonNavegacion="true"] {
        background-color: transparent;
        border: none;
        text-align: left;
        padding: 8px 12px;
        margin: 2px;
        border-radius: 6px;
    }
    
    QPushButton[esBotonNavegacion="true"]:hover {
        background-color: #F0E68C;
        color: #8B4513;
    }
    
    /* GroupBox */
    QGroupBox {
        background-color: #FFF8E7;
        border: 2px solid #DEB887;
        border-radius: 8px;
        margin: 8px;
        padding: 12px;
        font-weight: 600;
        color: #8B4513;
    }
    
    /* Separadores */
    QFrame[frameShape="4"] {
        color: #8B4513;
        background-color: #8B4513;
        height: 2px;
        margin: 8px 0px;
    }
    
    QFrame[frameShape="5"] {
        color: #DEB887;
        background-color: #DEB887;
        width: 1px;
    }
    
    /* Labels especiales */
    QLabel[estiloTituloCard="true"] {
        color: #8B4513;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 4px;
    }
    
    QLabel[esEstadoVerde="true"] {
        color: #8B4513;
        font-weight: bold;
        font-size: 14px;
    }
    
    QLabel[esDescripcionCard="true"] {
        color: #5D4037;
        font-size: 12px;
        margin-top: 4px;
    }
    """
    
    app.setStyleSheet(estilo)

def main():
    """Función principal"""
    logger = SiemLogger(__name__)
    logger.info("🚀 Iniciando Ares Aegis - Versión Final Limpia")
    
    try:
        # Deshabilitar escalado
        os.environ['QT_SCALE_FACTOR'] = '1.0'
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'
        
        # Crear aplicación
        app = QApplication(sys.argv)
        app.setApplicationName("Ares Aegis")
        app.setApplicationVersion("2.1")
        
        # Aplicar estilo básico
        aplicar_estilo_basico(app)
        
        # Mostrar mensaje de bienvenida
        msg = QMessageBox()
        msg.setWindowTitle("🛡️ Ares Aegis")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(
            "Bienvenido a Ares Aegis\n\n"
            "✅ Interfaz completamente limpia y uniforme\n"
            "🔒 Todas las acciones requieren confirmación\n"
            "🚫 Sin zoom ni escalado automático\n"
            "🛡️ Firewall solo con autorización del usuario\n\n"
            "¿Deseas continuar?"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if msg.exec() != QMessageBox.StandardButton.Yes:
            return 0
        
        # Crear y mostrar ventana
        ventana = VentanaPrincipalLimpia()
        ventana.show()
        
        print("\n" + "="*60)
        print("🛡️  ARES AEGIS - VERSIÓN FINAL OPTIMIZADA")
        print("="*60)
        print("✅ Interfaz: Completamente limpia y uniforme")
        print("📏 Espaciado: Márgenes y padding consistentes")
        print("🚫 Zoom: Completamente deshabilitado")
        print("🔒 Seguridad: Solo acciones autorizadas por el usuario")
        print("🧹 Elementos: Solo funcionales y visibles")
        print("="*60)
        print("🌟 ¡Sistema listo para usar!")
        print("="*60 + "\n")
        
        return app.exec()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
