"""
Panel de consola/log para mostrar información de acciones, tiempos y procesos.
Integra logging profesional y permite centralizar los eventos de la app.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit
from PySide6.QtCore import Qt
import logging

class PanelConsola(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Consola de Actividad - Ares Aegis")
        self.setStyleSheet("background: transparent; font-family: 'Fira Mono', 'JetBrains Mono', 'Consolas', monospace; color: #bdbdbd;")
        layout = QVBoxLayout()
        self.label = QLabel("Consola de actividad")
        self.label.setStyleSheet("color: #bdbdbd; font-size: 15px; font-weight: 600; margin-bottom: 6px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; background: transparent; border: none;")
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background: #23272f; color: #bdbdbd; font-family: 'Fira Mono', 'JetBrains Mono', 'Consolas', monospace; font-size: 15px; border-radius: 10px; padding: 10px; border: none; line-height: 1.5;")
        layout.addWidget(self.label)
        layout.addWidget(self.log_text)
        self.setLayout(layout)
        # Configura logging para que todo lo que se loguee aparezca aquí
        self._setup_logging()

    def _setup_logging(self):
        class QTextEditHandler(logging.Handler):
            def __init__(self, widget):
                super().__init__()
                self.widget = widget
            def emit(self, record):
                msg = self.format(record)
                self.widget.appendPlainText(msg)
        handler = QTextEditHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
        logging.getLogger().addHandler(handler)
        # Logging a archivo para eventos críticos y advertencias
        file_handler = logging.FileHandler('ares_aegis.log', encoding='utf-8')
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logging.getLogger().addHandler(file_handler)
        logging.getLogger().setLevel(logging.INFO)

    def log(self, mensaje, nivel="info"):
        """Permite loguear mensajes desde cualquier parte de la app."""
        if nivel == "info":
            logging.info(mensaje)
        elif nivel == "warning":
            logging.warning(mensaje)
        elif nivel == "error":
            logging.error(mensaje)
        elif nivel == "debug":
            logging.debug(mensaje)
        else:
            self.log_text.appendPlainText(mensaje)

    def clear(self):
        self.log_text.clear()
