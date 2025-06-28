from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QFrame, QSizePolicy, QLineEdit, QTableWidget, QTableWidgetItem, QStatusBar, QAbstractItemView
)
from PySide6.QtCore import Qt

class BasePanelVisual(QWidget):
    """
    Panel visual base inspirado en Zenmap/Wireshark:
    - Barra de título
    - Panel lateral de acciones (opcional)
    - Zona de filtros y búsqueda
    - Panel central de resultados (stacked, tarjetas, tablas)
    - Barra de estado inferior
    """
    def __init__(self, titulo="Panel", acciones=None, columnas_tabla=None):
        super().__init__()
        self.setStyleSheet("""
            background: #181C20;
            color: #E6E6E6;
            font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;
        """)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        # --- Barra de título superior ---
        self.titulo = QLabel(titulo)
        self.titulo.setStyleSheet("font-size: 18px; font-weight: 800; color: #FFA639; padding: 8px 0 8px 8px;")
        main_layout.addWidget(self.titulo)
        # --- Layout horizontal principal ---
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        # --- Panel lateral de acciones (opcional) ---
        self.sidebar = None
        if acciones:
            self.sidebar = QFrame()
            self.sidebar.setStyleSheet("background: #23272f; border-right: 1px solid #222; border-radius: 8px;")
            self.sidebar.setFixedWidth(90)
            sidebar_layout = QVBoxLayout(self.sidebar)
            sidebar_layout.setContentsMargins(4, 8, 4, 8)
            sidebar_layout.setSpacing(6)
            self.boton_accion = []
            for nombre, slot in acciones:
                btn = QPushButton(nombre)
                btn.setStyleSheet("""
                    QPushButton {
                        background: #23272f;
                        color: #E6E6E6;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: 600;
                        padding: 6px 2px;
                        margin-bottom: 1px;
                        border: none;
                    }
                    QPushButton:hover {
                        background: #3c8dbc;
                        color: #fff;
                    }
                """)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                btn.clicked.connect(slot)
                sidebar_layout.addWidget(btn)
                self.boton_accion.append(btn)
            sidebar_layout.addStretch(1)
            body_layout.addWidget(self.sidebar)
        # --- Panel central de resultados ---
        self.central = QStackedWidget()
        self.central.setStyleSheet("background: #181C20; border-radius: 6px;")
        # --- Zona de filtros y búsqueda ---
        self.filtros = QFrame()
        self.filtros.setStyleSheet("background: #23272f; border-bottom: 1px solid #333; border-radius: 6px 6px 0 0;")
        filtros_layout = QHBoxLayout(self.filtros)
        filtros_layout.setContentsMargins(4, 4, 4, 4)
        filtros_layout.setSpacing(4)
        self.input_filtro = QLineEdit()
        self.input_filtro.setPlaceholderText("Filtrar resultados o buscar...")
        self.input_filtro.setStyleSheet("background: #181C20; color: #E6E6E6; border-radius: 6px; padding: 4px 6px; font-size: 12px; border: 1px solid #444;")
        icono_buscar = QLabel("🔍")
        icono_buscar.setStyleSheet("font-size: 14px; margin-right: 2px;")
        filtros_layout.addWidget(icono_buscar)
        filtros_layout.addWidget(self.input_filtro, stretch=1)
        self.boton_filtrar = QPushButton("Filtrar")
        self.boton_filtrar.setStyleSheet("background: #3c8dbc; color: #fff; border-radius: 6px; padding: 4px 10px; font-weight: 600; border: none; font-size: 12px;")
        filtros_layout.addWidget(self.boton_filtrar)
        # --- Zona de resultados tipo tabla (placeholder, reutilizable) ---
        self.tabla_resultados = QTableWidget(8, len(columnas_tabla) if columnas_tabla else 4)
        if columnas_tabla:
            self.tabla_resultados.setHorizontalHeaderLabels(columnas_tabla)
        else:
            self.tabla_resultados.setHorizontalHeaderLabels(["Columna 1", "Columna 2", "Columna 3", "Columna 4"])
        self.tabla_resultados.setStyleSheet("background: #23272f; color: #E6E6E6; font-size: 12px; border-radius: 6px; border: 1px solid #444;")
        self.tabla_resultados.verticalHeader().setVisible(False)
        self.tabla_resultados.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_resultados.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_resultados.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_resultados.setShowGrid(False)
        self.tabla_resultados.setAlternatingRowColors(True)
        self.tabla_resultados.setFixedHeight(180)
        # --- Layout central vertical ---
        central_vbox = QVBoxLayout()
        central_vbox.setContentsMargins(0, 0, 0, 0)
        central_vbox.setSpacing(4)
        central_vbox.addWidget(self.filtros)
        central_vbox.addWidget(self.central, stretch=1)
        central_vbox.addWidget(self.tabla_resultados)
        body_layout.addLayout(central_vbox, stretch=1)
        main_layout.addLayout(body_layout, stretch=1)
        # --- Barra de estado inferior ---
        self.status = QStatusBar()
        self.status.setStyleSheet("background: #23272f; color: #AEB0AB; font-size: 11px;")
        self.status.showMessage("Listo para analizar el sistema.")
        main_layout.addWidget(self.status)
    def agregar_vista_placeholder(self, nombre):
        frame = QFrame()
        frame.setStyleSheet("background: #181C20;")
        vbox = QVBoxLayout(frame)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel(f"<h2 style='color:#FFA639; font-size:15px;'>{nombre}</h2><p style='color:#AEB0AB; font-size:11px;'>Panel en construcción</p>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 15px; color: #FFA639; margin-bottom: 4px;")
        vbox.addWidget(label)
        self.central.addWidget(frame)
        return frame
