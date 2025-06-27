"""
Panel visual de Ares Aegis para mostrar la validación de integridad de herramientas.
Estilo minimalista japonés, limpio y diferente.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QApplication
from PySide6.QtCore import Qt

class PanelIntegridad(QWidget):
    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        self.setWindowTitle("Ares Aegis - Integridad de Herramientas")
        self.setStyleSheet("background: #fff; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #23272f; border-radius: 12px;")
        layout = QVBoxLayout()
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: 600; font-size: 14px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.advertencia_label.setWordWrap(True)
        self.resultados = QListWidget()
        self.boton_validar = QPushButton("Validar Integridad con Hashes Oficiales")
        self.boton_validar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #3c8dbc; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_validar.clicked.connect(self.validar)
        self.label_info = QLabel(
            "Ares Aegis: Este panel compara los binarios críticos con los hashes oficiales de Kali Linux.\n"
            "- Íntegro: Coincide con el hash oficial.\n"
            "- Modificado: El binario ha cambiado, posible riesgo.\n"
            "- Sin referencia: No hay hash oficial, verifique manualmente.\n"
            "Recomendación: Si detecta binarios modificados, reinstale el paquete o investigue el origen.")
        self.label_info.setStyleSheet("color: #28353B; font-size: 15px; font-weight: 500; margin-bottom: 10px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        layout.addWidget(self.label_info)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.resultados)
        layout.addWidget(self.boton_validar)
        self.setLayout(layout)

    def validar(self):
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Validando integridad... Por favor, espera.")
        QApplication.processEvents()
        self.boton_validar.setEnabled(False)
        try:
            resultados, advertencias = self.controlador.validar()
            self.resultados.clear()
            for herramienta, estado in resultados.items():
                if "Íntegro" in estado:
                    self.resultados.addItem(f"🟢 {herramienta}: {estado}")
                elif "Modificado" in estado:
                    self.resultados.addItem(f"🔴 {herramienta}: {estado}")
                elif "No encontrado" in estado:
                    self.resultados.addItem(f"⚠️ {herramienta}: {estado}")
                else:
                    self.resultados.addItem(f"🟡 {herramienta}: {estado}")
            if advertencias:
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
                self.advertencia_label.setText("\n".join(advertencias))
            else:
                self.advertencia_label.setText("")
        finally:
            self.boton_validar.setEnabled(True)
