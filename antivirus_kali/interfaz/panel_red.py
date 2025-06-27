"""
Panel visual de Ares Aegis para mostrar el análisis de red y honeypots.
Estilo minimalista japonés, limpio y diferente.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget
from PySide6.QtCore import Qt


class PanelRed(QWidget):
    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        self.setWindowTitle("Ares Aegis - Análisis de Red y Honeypots")
        self.setStyleSheet("background: #f6f6f6; font-family: 'Noto Sans JP'; color: #222;")
        layout = QVBoxLayout()
        self.resultados = QListWidget()
        self.boton_analizar = QPushButton("Analizar Red y Honeypots")
        self.boton_analizar.clicked.connect(self.analizar)
        self.label_info = QLabel(
            "Ares Aegis: Este panel analiza la red local y detecta posibles honeypots o dispositivos anómalos.\n"
            "- Si ejecutas como root, el análisis es más profundo.\n"
            "- Se detectan MACs genéricas, puertos inusuales y dispositivos con comportamiento sospechoso.\n"
            "Recomendación: Si ves dispositivos sospechosos, revisa su procedencia y limita su acceso a la red.")
        self.label_info.setStyleSheet("color: #444; font-size: 13px;")
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px;")
        layout.addWidget(self.label_info)
        layout.addWidget(self.resultados)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.boton_analizar)
        self.setLayout(layout)

    def analizar(self):
        from PySide6.QtWidgets import QApplication
        self.resultados.clear()
        self.resultados.addItem("⏳ Analizando red... Por favor, espera.")
        QApplication.processEvents()
        sospechosos, advertencias, explicaciones = self.controlador.analizar_red()
        self.resultados.clear()
        # Feedback visual minimalista y didáctico
        if advertencias:
            advertencia_texto = "\n".join(advertencias)
            if any("root" in adv.lower() for adv in advertencias):
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
                self.advertencia_label.setText("⚠️ <b>Permiso insuficiente:</b> Ejecuta como <b>root</b> para un análisis completo.\n" + advertencia_texto)
            elif any("scapy" in adv.lower() for adv in advertencias):
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
                self.advertencia_label.setText("⚠️ <b>Error con Scapy:</b> No se pudo usar el motor avanzado de red.\n" + advertencia_texto)
            elif any("arp" in adv.lower() for adv in advertencias):
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
                self.advertencia_label.setText("⚠️ <b>Comando 'arp' no disponible:</b> Instala el paquete <b>net-tools</b> para análisis básico de red.\n" + advertencia_texto)
            else:
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px;")
                self.advertencia_label.setText(advertencia_texto)
        else:
            self.advertencia_label.setText("")
        if not sospechosos:
            self.resultados.addItem("🟢 No se detectaron dispositivos sospechosos en la red.")
        else:
            self.resultados.addItem("🔴 Dispositivos sospechosos detectados:")
            for disp in sospechosos:
                self.resultados.addItem(f"IP: {disp.get('ip','')} | MAC: {disp.get('mac','')}")
            for exp in explicaciones:
                self.resultados.addItem(f"⚠️ {exp}")
