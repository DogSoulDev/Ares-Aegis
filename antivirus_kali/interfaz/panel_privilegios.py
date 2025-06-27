"""
Panel visual de Ares Aegis para mostrar procesos con privilegios sospechosos.
Estilo minimalista japonés, limpio y diferente.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget
from PySide6.QtCore import Qt


class PanelPrivilegios(QWidget):
    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        self.setWindowTitle("Ares Aegis - Monitoreo de Privilegios y Seguridad")
        self.setStyleSheet("background: #fff; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #23272f; border-radius: 12px;")
        layout = QVBoxLayout()
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: 600; font-size: 14px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.advertencia_label.setWordWrap(True)
        self.resultados = QListWidget()
        self.boton_monitorear = QPushButton("Comprobar Privilegios y Procesos")
        self.boton_monitorear.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #3c8dbc; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_monitorear.clicked.connect(self.monitorear)
        # Detectar modo limitado
        import os
        self.modo_limitado = os.environ.get('ARES_AEGIS_LIMITADO') == '1'
        if self.modo_limitado:
            self.boton_monitorear.setEnabled(False)
            self.advertencia_label.setText("⚠️ Modo limitado: Ejecuta como root para monitoreo completo de privilegios.")
        self.label_info = QLabel("Ares Aegis: Este panel muestra si tienes permisos de administrador (root) y si hay procesos sospechosos ejecutándose con privilegios elevados.\nSi ves advertencias, revisa los procesos listados.")
        self.label_info.setStyleSheet("color: #28353B; font-size: 15px; font-weight: 500; margin-bottom: 10px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        layout.addWidget(self.label_info)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.resultados)
        layout.addWidget(self.boton_monitorear)
        self.setLayout(layout)

    def monitorear(self):
        import os
        from PySide6.QtWidgets import QListWidgetItem, QApplication
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.boton_monitorear.setEnabled(False)
        try:
            advertencias = []
            if os.geteuid() == 0:
                self.resultados.addItem("🟢 Tienes permisos de administrador (root). Ten cuidado con los cambios.")
            else:
                self.resultados.addItem("🟡 No tienes permisos de root. Algunas funciones avanzadas pueden estar limitadas.")
                advertencias.append("No tienes permisos de root. El monitoreo puede ser incompleto.")
            self.resultados.addItem("⏳ Monitoreando privilegios... Por favor, espera.")
            QApplication.processEvents()
            sospechosos = self.controlador.monitorear_privilegios()
            if sospechosos:
                self.resultados.addItem("🔴 Procesos sospechosos con privilegios elevados:")
                for proc in sospechosos:
                    item = QListWidgetItem(f"PID: {proc['pid']} | Nombre: {proc['name']} | CMD: {' '.join(proc['cmdline'])}")
                    item.setBackground(Qt.GlobalColor.red)
                    item.setForeground(Qt.GlobalColor.white)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    self.resultados.addItem(item)
                advertencias.append("Se detectaron procesos sospechosos ejecutándose como root. Revisa cuidadosamente.")
            else:
                self.resultados.addItem("🟢 No se detectaron procesos sospechosos ejecutándose como root.")
            if advertencias:
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
                self.advertencia_label.setText("\n".join(advertencias))
            else:
                self.advertencia_label.setText("")
        finally:
            self.boton_monitorear.setEnabled(True)
