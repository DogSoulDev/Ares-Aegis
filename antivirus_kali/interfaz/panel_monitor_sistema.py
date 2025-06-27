"""
Panel de monitorización de CPU, RAM y procesos activos.
"""

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QListWidget, QPushButton)
from PySide6.QtCore import Qt
import sys

class MonitorizacionPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ares Aegis - Monitorización de Sistema")
        self.setStyleSheet('''
            QWidget { background: #fff; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #23272f; border-radius: 12px; }
            QLabel { font-size: 15px; }
            QListWidget { background: #f7f8fa; color: #23272f; font-size: 15px; border-radius: 8px; padding: 8px; border: 1px solid #e0e0e0; selection-background-color: #e3f2fd; selection-color: #23272f; }
            QListWidget::item { padding: 10px 12px; border-radius: 7px; margin-bottom: 2px; }
            QListWidget::item:selected { background: #c3e6ff; color: #23272f; font-weight: 700; border-left: 5px solid #2563eb; }
            QListWidget::item:hover { background: #e0e7ef; }
            QPushButton { background: #e0e7ef; color: #23272f; border-radius: 8px; font-size: 15px; padding: 7px 18px; font-weight: 600; border: 1px solid #cfd8dc; }
            QPushButton:hover { background: #dbeafe; color: #1e293b; }
            QPushButton:focus { outline: 2px solid #2563eb; }
            QPushButton#exportar { background: #3c8dbc; color: #fff; border-radius: 8px; font-size: 15px; padding: 7px 18px; font-weight: 600; border: 1px solid #2563eb; }
            QPushButton#exportar:hover { background: #2563eb; color: #fff; }
        ''')

        # Configuración de la interfaz
        self.initUI()

    def initUI(self):
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        layoutPrincipal = QVBoxLayout(centralWidget)
        layoutSuperior = QHBoxLayout()
        layoutInferior = QHBoxLayout()

        # Título
        titulo = QLabel("Monitorización de Sistema")
        titulo.setStyleSheet("font-size: 24px; font-weight: 600; color: #2563eb;")
        layoutPrincipal.addWidget(titulo, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Lista de procesos
        self.listaProcesos = QListWidget()
        layoutPrincipal.addWidget(self.listaProcesos)

        # Botones
        botonActualizar = QPushButton("Actualizar")
        botonExportar = QPushButton("Exportar")
        botonConfiguracion = QPushButton("Configuración")

        # Asignar objeto nombre a botón exportar
        botonExportar.setObjectName("exportar")

        layoutInferior.addWidget(botonActualizar)
        layoutInferior.addWidget(botonExportar)
        layoutInferior.addWidget(botonConfiguracion)

        layoutPrincipal.addLayout(layoutInferior)

        # Conectar señales
        botonActualizar.clicked.connect(self.actualizarDatos)
        botonExportar.clicked.connect(self.exportarDatos)
        botonConfiguracion.clicked.connect(self.abrirConfiguracion)

    def actualizarDatos(self):
        # Lógica para actualizar datos de monitorización
        pass

    def exportarDatos(self):
        # Lógica para exportar datos
        pass

    def abrirConfiguracion(self):
        # Lógica para abrir configuración
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MonitorizacionPanel()
    ventana.resize(800, 600)
    ventana.show()
    sys.exit(app.exec_())
