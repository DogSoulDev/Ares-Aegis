"""
Ventana principal de Ares Aegis.
Estilo minimalista japonés, navegación entre paneles innovadores.
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout
from interfaz.panel_integridad import PanelIntegridad
from interfaz.panel_red import PanelRed
from interfaz.panel_privilegios import PanelPrivilegios
from interfaz.panel_iocs import PanelIOCs
from interfaz.panel_modo_seguro import PanelModoSeguro
from interfaz.panel_escaneo_sistema import PanelEscaneoSistema


class VentanaPrincipal(QMainWindow):
    def __init__(self, controladores):
        from PySide6.QtGui import QIcon
        import os
        super().__init__()
        self.setWindowTitle("Ares Aegis - Antivirus modular para Kali Linux")
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recursos", "iconos", "aresIcon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setStyleSheet("background: #f6f6f6; font-family: 'Noto Sans JP'; color: #222;")
        self.setMinimumSize(900, 600)
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
        layout.addWidget(tabs)
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)
