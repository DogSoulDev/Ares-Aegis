"""
Panel visual de Ares Aegis para activar/desactivar el modo pentesting seguro y ver auditoría.
Estilo minimalista japonés, limpio y diferente.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget
from PySide6.QtCore import Qt


class PanelModoSeguro(QWidget):
    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        self.setWindowTitle("Ares Aegis - Modo Seguro y Auditoría de Seguridad")
        self.setStyleSheet("background: #f6f6f6; font-family: 'Noto Sans JP'; color: #222;")
        layout = QVBoxLayout()
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px;")
        self.advertencia_label.setWordWrap(True)
        self.resultados = QListWidget()
        self.label_info = QLabel(
            "Ares Aegis: Este panel permite activar protecciones rápidas para pentesting seguro:\n"
            "- Activar Modo Seguro: Habilita el firewall y bloquea conexiones no autorizadas.\n"
            "- Desactivar Modo Seguro: Desactiva el firewall temporalmente.\n"
            "- Auditar Configuración: Revisa configuraciones críticas como SSH.\n"
            "Recomendado: Mantén el modo seguro activado durante auditorías o pruebas.")
        self.label_info.setStyleSheet("color: #444; font-size: 13px;")
        self.boton_activar = QPushButton("Activar Modo Seguro (Firewall ON)")
        self.boton_activar.clicked.connect(self.activar)
        self.boton_desactivar = QPushButton("Desactivar Modo Seguro (Firewall OFF)")
        self.boton_desactivar.clicked.connect(self.desactivar)
        self.boton_auditar = QPushButton("Auditar Configuración Crítica")
        self.boton_auditar.clicked.connect(self.auditar)
        layout.addWidget(self.label_info)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.resultados)
        layout.addWidget(self.boton_activar)
        layout.addWidget(self.boton_desactivar)
        layout.addWidget(self.boton_auditar)
        self.setLayout(layout)

    def activar(self):
        from PySide6.QtWidgets import QApplication
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Activando modo seguro... Por favor, espera.")
        QApplication.processEvents()
        advertencia = self.controlador.activar_modo_seguro()
        self.resultados.clear()
        if advertencia:
            self.resultados.addItem(f"🔴 {advertencia}")
            self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
            self.advertencia_label.setText(advertencia)
        else:
            self.resultados.addItem("🟢 Modo seguro activado: Firewall habilitado y conexiones salientes bloqueadas.")
            self.advertencia_label.setText("")

    def desactivar(self):
        from PySide6.QtWidgets import QApplication
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Desactivando modo seguro... Por favor, espera.")
        QApplication.processEvents()
        advertencia = self.controlador.desactivar_modo_seguro()
        self.resultados.clear()
        if advertencia:
            self.resultados.addItem(f"🔴 {advertencia}")
            self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
            self.advertencia_label.setText(advertencia)
        else:
            self.resultados.addItem("🟡 Modo seguro desactivado: Firewall deshabilitado.")
            self.advertencia_label.setText("")

    def auditar(self):
        from PySide6.QtWidgets import QApplication
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Auditando configuración... Por favor, espera.")
        QApplication.processEvents()
        resultado, advertencia = self.controlador.auditar_configuracion()
        self.resultados.clear()
        self.resultados.addItem(f"🔎 {resultado}")
        if advertencia:
            self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
            self.advertencia_label.setText(advertencia)
        else:
            self.advertencia_label.setText("")
