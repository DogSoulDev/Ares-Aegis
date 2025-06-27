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
        self.setStyleSheet("background: #f6f6f6; font-family: 'Noto Sans JP'; color: #222;")
        layout = QVBoxLayout()
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px;")
        self.advertencia_label.setWordWrap(True)
        self.resultados = QListWidget()
        self.boton_monitorear = QPushButton("Comprobar Privilegios y Procesos")
        self.boton_monitorear.clicked.connect(self.monitorear)
        self.label_info = QLabel("Ares Aegis: Este panel muestra si tienes permisos de administrador (root) y si hay procesos sospechosos ejecutándose con privilegios elevados.\nSi ves advertencias, revisa los procesos listados.")
        self.label_info.setStyleSheet("color: #444; font-size: 13px;")
        layout.addWidget(self.label_info)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.resultados)
        layout.addWidget(self.boton_monitorear)
        self.setLayout(layout)

    def monitorear(self):
        import os
        self.resultados.clear()
        self.advertencia_label.setText("")
        advertencias = []
        if os.geteuid() == 0:
            self.resultados.addItem("🟢 Tienes permisos de administrador (root). Ten cuidado con los cambios.")
        else:
            self.resultados.addItem("🟡 No tienes permisos de root. Algunas funciones avanzadas pueden estar limitadas.")
            advertencias.append("No tienes permisos de root. El monitoreo puede ser incompleto.")
        from PySide6.QtWidgets import QApplication
        self.resultados.addItem("⏳ Monitoreando privilegios... Por favor, espera.")
        QApplication.processEvents()
        sospechosos = self.controlador.monitorear_privilegios()
        if sospechosos:
            self.resultados.addItem("🔴 Procesos sospechosos con privilegios elevados:")
            for proc in sospechosos:
                self.resultados.addItem(f"PID: {proc['pid']} | Nombre: {proc['name']} | CMD: {' '.join(proc['cmdline'])}")
            advertencias.append("Se detectaron procesos sospechosos ejecutándose como root. Revisa cuidadosamente.")
        else:
            self.resultados.addItem("🟢 No se detectaron procesos sospechosos ejecutándose como root.")
        if advertencias:
            self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
            self.advertencia_label.setText("\n".join(advertencias))
        else:
            self.advertencia_label.setText("")
