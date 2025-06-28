




from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QFrame, QSizePolicy, QLineEdit, QTableWidget, QTableWidgetItem, QStatusBar, QAbstractItemView
)
from PySide6.QtCore import Qt

class PanelEscaneoSistema(QWidget):
    """
    Interfaz base inspirada en Zenmap y Wireshark:
    - Panel lateral de acciones (botones grandes, navegación vertical)
    - Panel central de resultados (stacked, tarjetas, tablas)
    - Estructura profesional y lista para conectar lógica
    """

    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        self.setStyleSheet("""
            background: #f7f8fa;
            color: #23272f;
            font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(0)

        # --- Barra de título superior ---
        self.titulo = QLabel("Ares Aegis - Análisis de Sistema")
        self.titulo.setStyleSheet("font-size: 18px; font-weight: 800; color: #3c8dbc; padding: 8px 0 8px 0; letter-spacing: 0.2px;")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.titulo)

        # --- Layout horizontal principal ---
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(8)

        # --- Panel lateral de acciones ---
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("background: #23272f; border-radius: 8px;")
        self.sidebar.setFixedWidth(90)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(4, 8, 4, 8)
        sidebar_layout.setSpacing(6)

        self.acciones = [
            ("Resumen", self.mostrar_resumen),
            ("Escaneo Completo", self.escaneo_completo),
            ("Rootkits", self.analizar_rootkits),
            ("Procesos", self.analizar_procesos),
            ("Puertos", self.analizar_puertos),
            ("Servicios", self.analizar_servicios),
            ("Programas", self.listar_programas),
            ("Seleccionar objetivo", self.seleccionar_objetivo),
        ]
        self.boton_accion = []
        for nombre, slot in self.acciones:
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

        # --- Panel central de resultados ---
        self.central = QStackedWidget()
        self.central.setStyleSheet("background: #fff; border-radius: 6px;")
        self.vistas = {}
        for nombre, _ in self.acciones:
            vista = self._crear_vista_placeholder(nombre)
            self.vistas[nombre] = vista
            self.central.addWidget(vista)

        # --- Zona de filtros y búsqueda (tipo Wireshark/Zenmap) ---
        self.filtros = QFrame()
        self.filtros.setStyleSheet("background: #f7f8fa; border-bottom: 1px solid #d0d0d0; border-radius: 6px 6px 0 0;")
        filtros_layout = QHBoxLayout(self.filtros)
        filtros_layout.setContentsMargins(4, 4, 4, 4)
        filtros_layout.setSpacing(4)
        self.input_filtro = QLineEdit()
        self.input_filtro.setPlaceholderText("Filtrar resultados o buscar...")
        self.input_filtro.setStyleSheet("background: #fff; color: #23272f; border-radius: 6px; padding: 4px 6px; font-size: 12px; border: 1px solid #bbb;")
        icono_buscar = QLabel("🔍")
        icono_buscar.setStyleSheet("font-size: 14px; margin-right: 2px;")
        filtros_layout.addWidget(icono_buscar)
        filtros_layout.addWidget(self.input_filtro, stretch=1)
        self.boton_filtrar = QPushButton("Filtrar")
        self.boton_filtrar.setStyleSheet("background: #3c8dbc; color: #fff; border-radius: 6px; padding: 4px 10px; font-weight: 600; border: none; font-size: 12px;")
        filtros_layout.addWidget(self.boton_filtrar)

        # --- Zona de resultados tipo tabla (placeholder, reutilizable) ---
        self.tabla_resultados = QTableWidget(8, 4)
        self.tabla_resultados.setHorizontalHeaderLabels(["Archivo/Servicio", "Tipo", "Resultado", "Detalles"])
        self.tabla_resultados.setStyleSheet("background: #fff; color: #23272f; font-size: 12px; border-radius: 6px; border: 1px solid #d0d0d0;")
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

        body_layout.addWidget(self.sidebar)
        body_layout.addLayout(central_vbox, stretch=1)
        main_layout.addLayout(body_layout, stretch=1)

        # --- Barra de estado inferior ---
        self.status = QStatusBar()
        self.status.setStyleSheet("background: #f7f8fa; color: #3c8dbc; font-size: 11px; border-top: 1px solid #d0d0d0;")
        self.status.showMessage("Listo para analizar el sistema.")
        main_layout.addWidget(self.status)

        self.mostrar_resumen()

    def _crear_vista_placeholder(self, nombre):
        frame = QFrame()
        frame.setStyleSheet("background: #fff;")
        vbox = QVBoxLayout(frame)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel(f"<h2 style='color:#3c8dbc; font-size:15px;'>{nombre}</h2><p style='color:#23272f; font-size:11px;'>Panel en construcción</p>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 15px; color: #3c8dbc; margin-bottom: 4px;")
        vbox.addWidget(label)
        return frame

    def mostrar_resumen(self):
        self.central.setCurrentIndex(0)

    def escaneo_completo(self):
        self.central.setCurrentIndex(1)

    def analizar_rootkits(self):
        self.central.setCurrentIndex(2)

    def analizar_procesos(self):
        self.central.setCurrentIndex(3)

    def analizar_puertos(self):
        self.central.setCurrentIndex(4)

    def analizar_servicios(self):
        self.central.setCurrentIndex(5)

    def listar_programas(self):
        self.central.setCurrentIndex(6)

    def seleccionar_objetivo(self):
        self.central.setCurrentIndex(7)
