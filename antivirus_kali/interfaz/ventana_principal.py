"""
Ventana principal de Ares Aegis.
Estilo minimalista japonés, navegación entre paneles innovadores.
"""

"""
Ventana principal de Ares Aegis.
Interfaz moderna, minimalista y profesional.
Organiza la navegación y paneles principales.
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget, QPushButton
from PySide6.QtCore import Qt
from pathlib import Path
from antivirus_kali.interfaz.panel_integridad import PanelIntegridad
from antivirus_kali.interfaz.panel_red import PanelRed
from antivirus_kali.interfaz.panel_privilegios import PanelPrivilegios
from antivirus_kali.interfaz.panel_iocs import PanelIOCs
from antivirus_kali.interfaz.panel_modo_seguro import PanelModoSeguro
from antivirus_kali.interfaz.panel_escaneo_sistema import PanelEscaneoSistema
from antivirus_kali.interfaz.panel_consola import PanelConsola
from antivirus_kali.interfaz.textos import TEXTOS



class VentanaPrincipal(QMainWindow):
    def __init__(self, controladores):
        from PySide6.QtGui import QIcon, QPixmap
        super().__init__()
        self.setWindowTitle(TEXTOS["app_title"])
        # Usar pathlib para rutas robustas
        base_dir = Path(__file__).resolve().parent.parent
        icon_path = base_dir / "recursos" / "iconos" / "aresIcon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.setStyleSheet("background: #f7f8fa; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #23272f;")
        self.setMinimumSize(1000, 700)

        # Paneles: una sola instancia de consola para todo
        self.panel_consola = PanelConsola()
        self.panel_escaneo = PanelEscaneoSistema(controladores['escaneo_sistema'], panel_consola=self.panel_consola)
        self.panel_integridad = PanelIntegridad(controladores['integridad'], panel_consola=self.panel_consola)
        self.panel_red = PanelRed(controladores['red'], panel_consola=self.panel_consola)
        self.panel_privilegios = PanelPrivilegios(controladores['privilegios'], panel_consola=self.panel_consola)
        self.panel_iocs = PanelIOCs(controladores['iocs'], panel_consola=self.panel_consola)
        self.panel_modo_seguro = PanelModoSeguro(controladores['modo_seguro'], panel_consola=self.panel_consola)
        from antivirus_kali.interfaz.panel_historial import PanelHistorial
        self.panel_historial = PanelHistorial()
        from antivirus_kali.interfaz.panel_configuracion import PanelConfiguracion
        self.panel_configuracion = PanelConfiguracion()

        self.categorias = [
            ("Análisis de Sistema", "system-search"),
            ("Historial de Análisis", "view-history"),
            ("Configuración", "settings-configure"),
            ("Red", "network-wired"),
            ("Integridad", "security-high"),
            ("Amenazas", "dialog-warning"),
            ("Modo Seguro", "security-medium"),
            ("Privilegios", "user-shield"),
            ("Exportar PDF", "document-save"),
            ("Ayuda / Soporte", "help-browser"),
        ]

        self.subopciones = {
            "Análisis de Sistema": [],
            "Historial de Análisis": [],
            "Configuración": [],
            "Red": [
                ("Análisis de Red y Honeypots", self.panel_red.analizar_threaded, "Analiza la red local y detecta dispositivos o honeypots sospechosos."),
            ],
            "Integridad": [
                ("Validar Integridad con Hashes Oficiales", self.panel_integridad.validar_threaded, "Verifica la integridad de los binarios críticos del sistema."),
            ],
            "Amenazas": [
                ("Verificar IOC/Reputación", self.panel_iocs.verificar_threaded, "Comprueba archivos, IPs o dominios contra fuentes públicas de amenazas."),
                ("Agregar IOC manualmente", self.panel_iocs.agregar_ioc_threaded, "Permite añadir IOCs manualmente para reforzar la protección."),
            ],
            "Modo Seguro": [
                ("Activar Modo Seguro", self.panel_modo_seguro.activar_threaded, "Activa protecciones rápidas y firewall para pentesting seguro."),
                ("Desactivar Modo Seguro", self.panel_modo_seguro.desactivar_threaded, "Desactiva el firewall temporalmente."),
                ("Auditar Configuración Crítica", self.panel_modo_seguro.auditar_threaded, "Revisa configuraciones críticas como SSH."),
            ],
            "Privilegios": [
                ("Comprobar Privilegios y Procesos", self.panel_privilegios.monitorear_threaded, "Monitorea procesos con privilegios elevados y posibles riesgos."),
            ],
            "Exportar PDF": [
                ("Exportar PDF personalizado", self.exportar_pdf_personalizado, "Exporta la información seleccionada por el usuario en un PDF profesional."),
            ],
            "Ayuda / Soporte": [],
        }


        # --- NUEVO DISEÑO MODERNO Y COHERENTE ---

        # --- NUEVO SIDEBAR CON LOGO Y NOMBRE ARRIBA ---
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)
        self.sidebar.setMinimumWidth(290)
        self.sidebar.setMaximumWidth(320)
        self.sidebar.setStyleSheet("background: #222c36;")

        # Logo y nombre arriba
        logo_path = base_dir / "recursos" / "Ares.jpeg"
        logo_label = QLabel()
        if logo_path.exists():
            logo_pixmap = QPixmap(str(logo_path))
            logo_scaled = logo_pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_scaled)
            logo_label.setStyleSheet("border-radius: 12px; margin-top: 28px; margin-bottom: 8px; margin-left: auto; margin-right: auto;")
        nombre_label = QLabel(TEXTOS["header"]["nombre"])
        nombre_label.setStyleSheet("font-size: 26px; font-weight: 900; color: #fff; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; margin-bottom: 24px; margin-left: auto; margin-right: auto;")
        nombre_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(0)
        logo_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        logo_layout.addWidget(nombre_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.sidebar_layout.addWidget(logo_container)

        # Menú lateral
        self.menu = QListWidget()
        self.menu.setMinimumWidth(260)
        self.menu.setMaximumWidth(300)
        self.menu.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.menu.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.menu.setStyleSheet('''
            QListWidget {
                background: #222c36;
                border: none;
                font-size: 17px;
                color: #e6e6e6;
                padding: 0px;
                outline: none;
            }
            QListWidget::viewport {
                background: #222c36;
            }
            QListWidget::item {
                padding: 16px 28px 16px 28px;
                margin: 8px 0px;
                border-radius: 12px;
                text-align: left;
                color: #e6e6e6;
                font-weight: 500;
                letter-spacing: 0.2px;
                min-width: 200px;
                max-width: 260px;
            }
            QListWidget::item:selected {
                background: #3c8dbc;
                color: #fff;
                font-weight: 600;
            }
            QListWidget::item:hover {
                background: #2d3a4a;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                width: 0px;
                height: 0px;
                background: transparent;
            }
        ''')
        from PySide6.QtGui import QIcon, QPixmap
        for cat, icon in self.categorias:
            texto = cat
            item = QListWidgetItem(f"  {texto}")
            item.setIcon(QIcon.fromTheme(icon))
            item.setToolTip(TEXTOS["sidebar"].get(cat, f"Panel: {cat}"))
            self.menu.addItem(item)
        self.menu.setFixedHeight(self.menu.sizeHintForRow(0) * len(self.categorias) + 18 * len(self.categorias))
        # Mejora visual: resalta la opción seleccionada con una barra lateral
        self.menu.setStyleSheet(self.menu.styleSheet() + '''
            QListWidget::item:selected {
                border-left: 6px solid #ffb300;
                background: #3c8dbc;
                color: #fff;
                font-weight: 700;
            }
        ''')

        # --- PANEL CENTRAL REDISEÑADO (DASHBOARD MODERNO) ---
        self.central_stack = QStackedWidget()
        # Fondo uniforme y moderno para toda la zona central
        self.central_stack.setStyleSheet("background: #f7f8fa;")
        self.paneles_categoria = {}
        for cat, _ in self.categorias:
            panel = QWidget()
            panel.setStyleSheet("background: #f7f8fa;")
            panel_layout = QVBoxLayout(panel)
            panel_layout.setContentsMargins(48, 36, 48, 36)
            panel_layout.setSpacing(28)
            # Título accesible
            titulo = QLabel(cat)
            titulo.setStyleSheet("font-size: 26px; color: #23272f; margin-bottom: 12px; font-weight: 900; text-align: center; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
            titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            titulo.setToolTip(f"Panel de {cat}. Opciones y acciones de {cat.lower()}.")
            panel_layout.addWidget(titulo)
            # Panel específico (resultados, widgets, etc.)
            if cat == "Análisis de Sistema":
                self.panel_escaneo.setStyleSheet("background: #f7f8fa;")
                panel_layout.addWidget(self.panel_escaneo)
            elif cat == "Historial de Análisis":
                self.panel_historial.setStyleSheet("background: #f7f8fa;")
                panel_layout.addWidget(self.panel_historial)
            elif cat == "Configuración":
                self.panel_configuracion.setStyleSheet("background: #f7f8fa;")
                panel_layout.addWidget(self.panel_configuracion)
            elif cat == "Red":
                self.panel_red.setStyleSheet("background: #f7f8fa;")
                panel_layout.addWidget(self.panel_red)
            elif cat == "Integridad":
                self.panel_integridad.setStyleSheet("background: #f7f8fa;")
                panel_layout.addWidget(self.panel_integridad)
            elif cat == "Amenazas":
                self.panel_iocs.setStyleSheet("background: #f7f8fa;")
                panel_layout.addWidget(self.panel_iocs)
            elif cat == "Modo Seguro":
                self.panel_modo_seguro.setStyleSheet("background: #f7f8fa;")
                panel_layout.addWidget(self.panel_modo_seguro)
            elif cat == "Privilegios":
                self.panel_privilegios.setStyleSheet("background: #f7f8fa;")
                panel_layout.addWidget(self.panel_privilegios)
            elif cat == "Ayuda / Soporte":
                # Panel de ayuda moderno
                ayuda = QWidget()
                ayuda_layout = QVBoxLayout(ayuda)
                ayuda_layout.setContentsMargins(24, 12, 24, 12)
                ayuda_layout.setSpacing(18)
                l1 = QLabel("<b>Ayuda y Soporte de Ares Aegis</b>")
                l1.setStyleSheet("font-size: 22px; color: #23272f; font-weight: 800;")
                ayuda_layout.addWidget(l1)
                l2 = QLabel("<ul style='font-size:15px;'><li>Consulta la <a href='https://github.com/DogSoulDev/Ares-Aegis/wiki'>documentación oficial</a> para guías y preguntas frecuentes.</li><li>Reporta problemas o sugiere mejoras en <a href='https://github.com/DogSoulDev/Ares-Aegis/issues'>GitHub Issues</a>.</li><li>Contacta al equipo: <a href='mailto:soporte@aresaegis.com'>soporte@aresaegis.com</a></li></ul>")
                l2.setOpenExternalLinks(True)
                l2.setStyleSheet("font-size: 15px; color: #23272f;")
                ayuda_layout.addWidget(l2)
                l3 = QLabel("<b>Recursos útiles:</b><br>- <a href='https://www.kali.org/docs/'>Documentación Kali Linux</a><br>- <a href='https://www.clamav.net/documents/'>ClamAV Docs</a><br>- <a href='https://bleachbit.org/documentation'>BleachBit Docs</a>")
                l3.setOpenExternalLinks(True)
                l3.setStyleSheet("font-size: 14px; color: #23272f;")
                ayuda_layout.addWidget(l3)
                ayuda_layout.addStretch(1)
                panel_layout.addWidget(ayuda)
            self.central_stack.addWidget(panel)
            self.paneles_categoria[cat] = panel

        self.sidebar_layout.addWidget(self.menu)
        self.sidebar_layout.addStretch(1)


        # Layout principal horizontal: sidebar + contenido
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.central_stack, stretch=1)

        # Terminal de información siempre visible abajo (solo una vez, misma instancia que panel_consola)
        terminal_bg = QWidget()
        terminal_layout = QVBoxLayout(terminal_bg)
        terminal_layout.setContentsMargins(24, 8, 24, 16)
        terminal_layout.setSpacing(0)
        terminal_bg.setStyleSheet("background: #23272f; border-radius: 12px; border: none; margin-bottom: 0px;")
        self.panel_consola.setStyleSheet("background: #23272f; color: #bdbdbd; font-family: 'Fira Mono', monospace; font-size: 15px; border: none;")
        terminal_layout.addWidget(self.panel_consola)

        # Layout vertical final: contenido + terminal
        layout_vertical = QVBoxLayout()
        layout_vertical.setContentsMargins(0, 0, 0, 0)
        layout_vertical.setSpacing(0)
        layout_vertical.addLayout(main_layout, stretch=8)
        layout_vertical.addWidget(terminal_bg, stretch=1)
        container = QWidget()
        container.setLayout(layout_vertical)
        self.setCentralWidget(container)

        self.menu.currentRowChanged.connect(self.on_menu_changed)
        self.menu.setCurrentRow(0)
        self.on_menu_changed(0)

    def exportar_pdf_personalizado(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import getpass
        # 1. Selección de ruta destino
        ruta_pdf, _ = QFileDialog.getSaveFileName(self, "Guardar informe PDF", "informe_ares_aegis.pdf", "PDF Files (*.pdf)")
        if not ruta_pdf:
            return
        # 2. Obtener resumen profesional (solo de Análisis de Sistema por ahora)
        try:
            resumen = self.panel_escaneo.controlador.obtener_resumen(self.panel_escaneo.base_hashes)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el resumen: {e}")
            return
        usuario = getpass.getuser()
        # 3. Exportar PDF profesional
        try:
            ruta_final = self.panel_escaneo.controlador.exportar_informe(resumen, ruta=ruta_pdf, usuario=usuario)
            if Path(ruta_final).exists():
                QMessageBox.information(self, "Exportación exitosa", f"Informe PDF exportado correctamente a:\n{ruta_final}")
            else:
                QMessageBox.warning(self, "Exportación incompleta", f"No se pudo guardar el PDF en la ruta seleccionada.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar el PDF: {e}")

    def on_menu_changed(self, idx):
        if idx < 0:
            return
        cat = self.categorias[idx][0]
        self.central_stack.setCurrentWidget(self.paneles_categoria[cat])
        # No loguear cambios de categoría en la consola, solo logs relevantes de análisis y errores
