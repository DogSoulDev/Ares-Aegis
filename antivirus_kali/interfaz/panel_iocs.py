"""
Panel visual de Ares Aegis para mostrar amenazas detectadas por IOCs y reputación de repositorios.
Estilo minimalista japonés, limpio y diferente.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QListWidget
from PySide6.QtCore import Qt


class PanelIOCs(QWidget):
    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        self.setWindowTitle("Ares Aegis - Detección de IOCs y Reputación")
        self.setStyleSheet("background: #fff; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #23272f; border-radius: 12px;")
        layout = QVBoxLayout()
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: 600; font-size: 14px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.advertencia_label.setWordWrap(True)
        self.entrada = QLineEdit()
        self.entrada.setPlaceholderText("Introduce hash, IP o URL para analizar...")
        self.entrada.setStyleSheet("padding: 10px 14px; font-size: 15px; border-radius: 7px; border: 1.5px solid #e0e0e0; background: #f7f8fa; margin-bottom: 8px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.resultados = QListWidget()
        self.boton_verificar = QPushButton("Verificar IOC/Reputación")
        self.boton_verificar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #3c8dbc; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_verificar.clicked.connect(self.verificar)
        self.boton_agregar = QPushButton("Agregar IOC manualmente")
        self.boton_agregar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #6A8D73; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_agregar.clicked.connect(self.agregar_ioc)
        self.label_info = QLabel("Ares Aegis: Este panel permite comprobar si un archivo, IP o dominio es malicioso según fuentes públicas.\nPuedes añadir IOCs manualmente para reforzar la protección.")
        self.label_info.setStyleSheet("color: #28353B; font-size: 15px; font-weight: 500; margin-bottom: 10px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        layout.addWidget(self.label_info)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.entrada)
        layout.addWidget(self.resultados)
        layout.addWidget(self.boton_verificar)
        layout.addWidget(self.boton_agregar)
        self.setLayout(layout)
        self.iocs_manuales = set()


    def verificar(self):
        from PySide6.QtWidgets import QApplication
        valor = self.entrada.text().strip()
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.boton_verificar.setEnabled(False)
        self.boton_agregar.setEnabled(False)
        try:
            self.resultados.addItem("⏳ Verificando IOC/Reputación... Por favor, espera.")
            QApplication.processEvents()
            advertencias = []
            if not valor:
                self.resultados.clear()
                self.resultados.addItem("Introduce un valor para analizar.")
                return
            if valor in self.iocs_manuales:
                self.resultados.clear()
                self.resultados.addItem(f"🔴 {valor}: IOC manualmente marcado como malicioso.")
                advertencias.append("Este IOC fue marcado manualmente como malicioso. Confirma su procedencia.")
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
                self.advertencia_label.setText("\n".join(advertencias))
                return
            resultado, advertencias_api = self.controlador.verificar_ioc(valor)
            self.resultados.clear()
            if "malicioso" in resultado:
                self.resultados.addItem(f"🔴 {resultado}")
            else:
                self.resultados.addItem(f"🟢 {resultado}")
            advertencias.extend(advertencias_api)
            if advertencias:
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
                self.advertencia_label.setText("\n".join(advertencias))
            else:
                self.advertencia_label.setText("")
        finally:
            self.boton_verificar.setEnabled(True)
            self.boton_agregar.setEnabled(True)

    def agregar_ioc(self):
        from PySide6.QtWidgets import QApplication
        valor = self.entrada.text().strip()
        self.resultados.clear()
        self.boton_verificar.setEnabled(False)
        self.boton_agregar.setEnabled(False)
        try:
            self.resultados.addItem("⏳ Agregando IOC manualmente... Por favor, espera.")
            QApplication.processEvents()
            if valor:
                self.iocs_manuales.add(valor)
                self.resultados.clear()
                self.resultados.addItem(f"IOC añadido manualmente: {valor}")
        finally:
            self.boton_verificar.setEnabled(True)
            self.boton_agregar.setEnabled(True)
