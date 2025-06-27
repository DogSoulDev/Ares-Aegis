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
        self.setStyleSheet("background: #f6f6f6; font-family: 'Noto Sans JP'; color: #222;")
        layout = QVBoxLayout()
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px;")
        self.advertencia_label.setWordWrap(True)
        self.entrada = QLineEdit()
        self.entrada.setPlaceholderText("Introduce hash, IP o URL para analizar...")
        self.resultados = QListWidget()
        self.boton_verificar = QPushButton("Verificar IOC/Reputación")
        self.boton_verificar.clicked.connect(self.verificar)
        self.boton_agregar = QPushButton("Agregar IOC manualmente")
        self.boton_agregar.clicked.connect(self.agregar_ioc)
        self.label_info = QLabel("Ares Aegis: Este panel permite comprobar si un archivo, IP o dominio es malicioso según fuentes públicas.\nPuedes añadir IOCs manualmente para reforzar la protección.")
        self.label_info.setStyleSheet("color: #444; font-size: 13px;")
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

    def agregar_ioc(self):
        from PySide6.QtWidgets import QApplication
        valor = self.entrada.text().strip()
        self.resultados.clear()
        self.resultados.addItem("⏳ Agregando IOC manualmente... Por favor, espera.")
        QApplication.processEvents()
        if valor:
            self.iocs_manuales.add(valor)
            self.resultados.clear()
            self.resultados.addItem(f"IOC añadido manualmente: {valor}")
