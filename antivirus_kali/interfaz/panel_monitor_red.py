"""
Panel de monitorización de red y conexiones.
Visualiza tráfico y conexiones activas.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton
from PySide6.QtCore import Qt

class PanelMonitorRed(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ares Aegis - Monitorización de Red")
        self.setStyleSheet('''
            QWidget { background: #fff; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #23272f; border-radius: 12px; }
            QLabel { font-size: 15px; }
            QListWidget { background: #f7f8fa; color: #23272f; font-size: 15px; border-radius: 8px; padding: 8px; border: 1px solid #e0e0e0; selection-background-color: #e3f2fd; selection-color: #23272f; }
            QListWidget::item { padding: 10px 12px; border-radius: 7px; margin-bottom: 2px; }
            QListWidget::item:selected { background: #c3e6ff; color: #23272f; font-weight: 700; border-left: 5px solid #2563eb; }
            QListWidget::item:hover { background: #e0e7ef; }
            QPushButton { background: #e0e7ef; color: #23272f; border-radius: 8px; font-size: 15px; padding: 7px 18px; font-weight: 600; border: 1px solid #cfd8dc; }
            QPushButton:hover { background: #dbeafe; color: #1e293b; }
            QPushButton:focus { outline: 2px solid #2563eb; }
            QPushButton#exportar { background: #3c8dbc; color: #fff; border-radius: 8px; font-size: 15px; padding: 7px 18px; font-weight: 600; border: 1px solid #2563eb; }
            QPushButton#exportar:hover { background: #2563eb; color: #fff; }
        ''')
        # ...existing code...
