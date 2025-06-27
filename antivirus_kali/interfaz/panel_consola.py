"""
Panel de consola/log para mostrar información de acciones, tiempos y procesos.
Integra logging profesional y permite centralizar los eventos de la app.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtCore import Qt
import logging

class PanelConsola(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Consola de Actividad - Ares Aegis")
        self.setStyleSheet('''
            QWidget { background: #fff; font-family: 'Fira Mono', 'JetBrains Mono', 'Consolas', monospace; color: #23272f; border-radius: 12px; }
            QLabel { font-size: 16px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #2563eb; font-weight: 700; margin-bottom: 6px; }
            QComboBox { background: #f7f8fa; color: #23272f; font-size: 14px; border-radius: 7px; padding: 4px 12px; border: 1px solid #e0e0e0; }
            QComboBox:focus { outline: 2px solid #2563eb; }
            QPushButton { background: #3c8dbc; color: #fff; border-radius: 7px; font-size: 14px; padding: 6px 18px; font-weight: 600; border: 1px solid #2563eb; }
            QPushButton:hover { background: #2563eb; color: #fff; }
            QPushButton:focus { outline: 2px solid #2563eb; }
            QPlainTextEdit { background: #23272f; color: #bdbdbd; font-family: 'Fira Mono', 'JetBrains Mono', 'Consolas', monospace; font-size: 15px; border-radius: 10px; padding: 10px; border: none; line-height: 1.5; }
        ''')
        layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        self.label = QLabel("🖥️ Consola de actividad")
        self.label.setAccessibleName("Título consola de actividad")
        hlayout.addWidget(self.label)
        from PySide6.QtWidgets import QComboBox, QPushButton, QFileDialog
        self.filtro_combo = QComboBox()
        self.filtro_combo.addItems(["Todos", "Info", "Advertencia", "Error"])
        self.filtro_combo.setToolTip("Filtra los mensajes del log por nivel de importancia.")
        self.filtro_combo.currentIndexChanged.connect(self.filtrar_logs)
        hlayout.addWidget(self.filtro_combo)
        self.btn_exportar = QPushButton("Exportar log")
        self.btn_exportar.setToolTip("Exporta el log mostrado a un archivo de texto.")
        self.btn_exportar.setAccessibleName("Botón exportar log")
        self.btn_exportar.clicked.connect(self.exportar_log)
        hlayout.addWidget(self.btn_exportar)
        layout.addLayout(hlayout)
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setToolTip("Aquí se muestran los eventos y acciones relevantes de la aplicación en tiempo real.")
        layout.addWidget(self.log_text)
        self.setLayout(layout)
        self._logs = []  # (nivel, mensaje)
        self._setup_logging()

    def _setup_logging(self):
        class QTextEditHandler(logging.Handler):
            def __init__(self, panel):
                super().__init__()
                self.panel = panel
            def emit(self, record):
                msg = self.format(record)
                nivel = record.levelname.lower()
                self.panel._logs.append((nivel, msg))
                self.panel.filtrar_logs()
        handler = QTextEditHandler(self)
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
        logging.getLogger().addHandler(handler)
        # Logging a archivo para eventos críticos y advertencias
        file_handler = logging.FileHandler('ares_aegis.log', encoding='utf-8')
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logging.getLogger().addHandler(file_handler)
        logging.getLogger().setLevel(logging.INFO)

    def log(self, mensaje, nivel="info"):
        """Permite loguear mensajes desde cualquier parte de la app. Solo logs relevantes de análisis y errores."""
        if nivel == "info":
            logging.info(mensaje)
        elif nivel == "warning":
            logging.warning(mensaje)
        elif nivel == "error":
            logging.error(mensaje)
        elif nivel == "debug":
            logging.debug(mensaje)
        # No mostrar logs triviales ni clicks
    def filtrar_logs(self):
        filtro = self.filtro_combo.currentText()
        self.log_text.clear()
        for nivel, msg in self._logs:
            if filtro == "Todos":
                self.log_text.appendPlainText(msg)
            elif filtro == "Info" and nivel == "info":
                self.log_text.appendPlainText(msg)
            elif filtro == "Advertencia" and nivel == "warning":
                self.log_text.appendPlainText(msg)
            elif filtro == "Error" and nivel == "error":
                self.log_text.appendPlainText(msg)

    def exportar_log(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        ruta, _ = QFileDialog.getSaveFileName(self, "Exportar log", "ares_aegis_log.txt", "Text Files (*.txt)")
        if ruta:
            with open(ruta, 'w', encoding='utf-8') as f:
                for nivel, msg in self._logs:
                    f.write(f"[{nivel.upper()}] {msg}\n")
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Log exportado")
            dlg.setText(f"<b>Log exportado a:</b><br><span style='font-size:14px;color:#2563eb'>{ruta}</span>")
            dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
            dlg.setStyleSheet("QLabel{font-size:15px;}QMessageBox{background:#f7f8fa;} QPushButton{background:#3c8dbc;color:#fff;border-radius:7px;padding:6px 18px;font-size:15px;} QPushButton:hover{background:#2563eb;}")
            dlg.setAccessibleName("Diálogo log exportado")
            dlg.exec()

    def clear(self):
        self.log_text.clear()
