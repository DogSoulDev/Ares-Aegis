"""
Ventana principal de Ares Aegis.
Estilo minimalista japonés, navegación entre paneles innovadores.
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from antivirus_kali.interfaz.panel_integridad import PanelIntegridad
from antivirus_kali.interfaz.panel_red import PanelRed
from antivirus_kali.interfaz.panel_privilegios import PanelPrivilegios
from antivirus_kali.interfaz.panel_iocs import PanelIOCs
from antivirus_kali.interfaz.panel_modo_seguro import PanelModoSeguro
from antivirus_kali.interfaz.panel_escaneo_sistema import PanelEscaneoSistema


class VentanaPrincipal(QMainWindow):
    def __init__(self, controladores):
        from PySide6.QtGui import QIcon, QPixmap
        import os
        super().__init__()
        self.setWindowTitle("Ares Aegis - Antivirus modular para Kali Linux")
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recursos", "iconos", "aresIcon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setStyleSheet("background: #f6f6f6; font-family: 'Noto Sans JP'; color: #222;")
        self.setMinimumSize(900, 600)

        # Banner principal con Ares.jpeg (responsive)
        banner_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recursos", "Ares.jpeg")
        banner_label = None
        if os.path.exists(banner_path):
            banner_label = QLabel()
            pixmap = QPixmap(banner_path)
            # Escalado inicial, se ajusta en resizeEvent
            scaled = pixmap.scaledToWidth(700, Qt.TransformationMode.SmoothTransformation)
            banner_label.setPixmap(scaled)
            banner_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
            banner_label.setStyleSheet("margin-top: 18px; margin-bottom: 8px; border-radius: 12px;")
            self._banner_pixmap = pixmap
            self._banner_label = banner_label
        else:
            self._banner_pixmap = None
            self._banner_label = None

        tabs = QTabWidget()
        # Escaneo del sistema como primera pestaña
        tabs.addTab(PanelEscaneoSistema(controladores['escaneo_sistema']), "Ares Aegis: Escaneo Sistema 🛡️")
        tabs.addTab(PanelIntegridad(controladores['integridad']), "Ares Aegis: Integridad")
        tabs.addTab(PanelRed(controladores['red']), "Ares Aegis: Red/Honeypots")
        tabs.addTab(PanelPrivilegios(controladores['privilegios']), "Ares Aegis: Privilegios")
        tabs.addTab(PanelIOCs(controladores['iocs']), "Ares Aegis: IOCs/Reputación")
        tabs.addTab(PanelModoSeguro(controladores['modo_seguro']), "Ares Aegis: Modo Seguro")
        contenedor = QWidget()
        layout = QVBoxLayout()
        if banner_label:
            layout.addWidget(banner_label)
        layout.addWidget(tabs)
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)

    def resizeEvent(self, event):
        # Hacer el banner responsive al ancho de la ventana
        if hasattr(self, '_banner_label') and self._banner_label and self._banner_pixmap:
            ancho = min(self.width() - 80, 900)
            alto_max = 180
            scaled = self._banner_pixmap.scaledToWidth(ancho, Qt.TransformationMode.SmoothTransformation)
            if scaled.height() > alto_max:
                scaled = self._banner_pixmap.scaledToHeight(alto_max, Qt.TransformationMode.SmoothTransformation)
            self._banner_label.setPixmap(scaled)
        super().resizeEvent(event)
