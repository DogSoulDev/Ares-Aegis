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
        self.setStyleSheet("background: #fff; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #222;")
        layout = QVBoxLayout()
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: 600; font-size: 14px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.advertencia_label.setWordWrap(True)
        self.resultados = QListWidget()
        self.label_info = QLabel(
            "Ares Aegis: Este panel permite activar protecciones rápidas para pentesting seguro:\n"
            "- Activar Modo Seguro: Habilita el firewall y bloquea conexiones no autorizadas.\n"
            "- Desactivar Modo Seguro: Desactiva el firewall temporalmente.\n"
            "- Auditar Configuración: Revisa configuraciones críticas como SSH.\n"
            "Recomendado: Mantén el modo seguro activado durante auditorías o pruebas.")
        self.label_info.setStyleSheet("color: #28353B; font-size: 15px; font-weight: 500; margin-bottom: 10px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.boton_activar = QPushButton("Activar Modo Seguro (Firewall ON)")
        self.boton_activar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #3c8dbc; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_activar.clicked.connect(self.activar)
        self.boton_desactivar = QPushButton("Desactivar Modo Seguro (Firewall OFF)")
        self.boton_desactivar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #e67e22; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_desactivar.clicked.connect(self.desactivar)
        self.boton_auditar = QPushButton("Auditar Configuración Crítica")
        self.boton_auditar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #6A8D73; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_auditar.clicked.connect(self.auditar)
        layout.addWidget(self.label_info)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.resultados)
        layout.addWidget(self.boton_activar)
        layout.addWidget(self.boton_desactivar)
        layout.addWidget(self.boton_auditar)
        # Detectar modo limitado
        import os
        self.modo_limitado = os.environ.get('ARES_AEGIS_LIMITADO') == '1'
        if self.modo_limitado:
            for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
                btn.setEnabled(False)
            self.advertencia_label.setText("⚠️ Modo limitado: Ejecuta como root para activar el modo seguro y auditar la configuración.")
        self.setLayout(layout)

    def activar(self):
        from PySide6.QtWidgets import QApplication
        self.resultados.clear()
        self.advertencia_label.setText("")
        for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
            btn.setEnabled(False)
        try:
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
        finally:
            for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
                btn.setEnabled(True)

    def desactivar(self):
        from PySide6.QtWidgets import QApplication
        self.resultados.clear()
        self.advertencia_label.setText("")
        for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
            btn.setEnabled(False)
        try:
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
        finally:
            for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
                btn.setEnabled(True)

    def auditar(self):
        from PySide6.QtWidgets import QApplication
        self.resultados.clear()
        self.advertencia_label.setText("")
        for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
            btn.setEnabled(False)
        try:
            self.resultados.addItem("⏳ Auditando configuración... Por favor, espera.")
            QApplication.processEvents()
            resultado, advertencia = self.controlador.auditar_configuracion()
            self.resultados.clear()
            # ...existing code...
        finally:
            for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
                btn.setEnabled(True)
        self.resultados.addItem(f"🔎 {resultado}")
        if advertencia:
            self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
            self.advertencia_label.setText(advertencia)
        else:
            self.advertencia_label.setText("")
