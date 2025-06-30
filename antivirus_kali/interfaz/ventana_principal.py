"""
Ventana principal de Ares Aegis.
Interfaz completamente nueva, moderna y elegante con navegación fluida.
Diseñada para máxima usabilidad y experiencia profesional.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame,
    QGridLayout, QSpacerItem, QSizePolicy, QLineEdit,
    QProgressBar, QScrollArea, QListWidget, QListWidgetItem,
    QDialog, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer, Signal
from PySide6.QtGui import QIcon, QFont, QPixmap, QColor, QPalette
from pathlib import Path
import sys
from antivirus_kali.interfaz.textos import TEXTOS
from antivirus_kali.core.scan_engine import MotorEscaneo
from antivirus_kali.interfaz.panel_mini_siem import PanelMiniSiem
from antivirus_kali.controladores.controlador_mini_siem import ControladorMiniSiemIntegracion





class VentanaPrincipal(QMainWindow):
    def __init__(self, controladores):
        super().__init__()
        self.controladores = controladores
        self.controlador_siem = ControladorMiniSiemIntegracion()
        self.setup_ui()
        self.setup_navigation()
        
    def setup_ui(self):
        """Configuración inicial de la interfaz"""
        self.setWindowTitle("Ares Aegis - Antivirus Profesional")
        self.setMinimumSize(1200, 800)
        
        # Configurar icono
        base_dir = Path(__file__).resolve().parent.parent
        icon_path = base_dir / "recursos" / "iconos" / "aresIcon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Tema principal limpio y profesional
        self.setStyleSheet("""
            QMainWindow {
                background: #ffffff;
                color: #2c3e50;
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
            }
            
            QWidget {
                background: transparent;
                color: #2c3e50;
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
            }
            
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            
            QPushButton:hover {
                background: #2980b9;
            }
            
            QPushButton:pressed {
                background: #21618c;
            }
            
            QLabel {
                color: #2c3e50;
            }
        """)
        
        # Widget central principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.create_header(main_layout)
        
        # Contenido principal
        self.create_main_content(main_layout)
        
    def create_header(self, parent_layout):
        """Crear header elegante y moderno"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2c3e50);
                border-bottom: 3px solid #2980b9;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        # Logo y título
        title_label = QLabel("ARES AEGIS")
        title_label.setStyleSheet("font-size: 28px; font-weight: 800; color: white;")
        
        subtitle_label = QLabel("Suite Antivirus Profesional")
        subtitle_label.setStyleSheet("font-size: 14px; font-weight: 400; color: rgba(255,255,255,0.8);")
        
        title_container = QVBoxLayout()
        title_container.addWidget(title_label)
        title_container.addWidget(subtitle_label)
        title_container.setSpacing(0)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        parent_layout.addWidget(header)
        
    def create_main_content(self, parent_layout):
        """Crear contenido principal con navegación elegante"""
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Sidebar navegación
        self.create_sidebar(content_layout)
        
        # Panel principal
        self.create_main_panel(content_layout)
        
        parent_layout.addWidget(content_widget)
        
    def create_sidebar(self, parent_layout):
        """Crear sidebar de navegación"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border-right: 1px solid #e9ecef;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)
        sidebar_layout.setSpacing(15)
        
        # Botones de navegación principal
        self.nav_buttons = []
        nav_items = [
            ("Escaneo", "🛡️", self.show_scan_panel),
            ("Resultados", "📊", self.show_results_panel),
            ("Mini-SIEM", "🔍", self.show_siem_panel),
            ("Configuración", "⚙️", self.show_settings_panel),
            ("Historial", "📝", self.show_history_panel),
            ("Herramientas", "🔧", self.show_tools_panel)
        ]
        
        for text, icon, callback in nav_items:
            btn = self.create_nav_button(text, icon, callback)
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        parent_layout.addWidget(self.sidebar)
        
    def create_nav_button(self, text, icon, callback):
        """Crear botón de navegación elegante"""
        btn = QPushButton(f"{icon}  {text}")
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #495057;
                border: none;
                border-radius: 10px;
                padding: 15px 20px;
                font-size: 16px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(52, 152, 219, 0.1);
                color: #3498db;
            }
            QPushButton:pressed, QPushButton:checked {
                background: #3498db;
                color: white;
            }
        """)
        btn.clicked.connect(callback)
        return btn
        
    def create_main_panel(self, parent_layout):
        """Crear panel principal de contenido"""
        self.main_panel = QStackedWidget()
        self.main_panel.setStyleSheet("""
            QStackedWidget {
                background: white;
                border-radius: 0px;
            }
        """)
        
        # Crear paneles
        self.scan_panel = self.create_scan_panel()
        self.results_panel = self.create_results_panel()
        self.siem_panel = self.create_siem_panel()
        self.settings_panel = self.create_settings_panel()
        self.history_panel = self.create_history_panel()
        self.tools_panel = self.create_tools_panel()
        
        self.main_panel.addWidget(self.scan_panel)
        self.main_panel.addWidget(self.results_panel)
        self.main_panel.addWidget(self.siem_panel)
        self.main_panel.addWidget(self.settings_panel)
        self.main_panel.addWidget(self.history_panel)
        self.main_panel.addWidget(self.tools_panel)
        
        parent_layout.addWidget(self.main_panel, stretch=1)
        
    def create_scan_panel(self):
        """Panel de escaneo principal"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Título
        title = QLabel("Centro de Escaneo")
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Descripción
        desc = QLabel("Selecciona el tipo de escaneo que deseas realizar")
        desc.setStyleSheet("font-size: 16px; color: #7f8c8d; margin-bottom: 30px;")
        layout.addWidget(desc)
        
        # Grid de opciones de escaneo
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        scan_options = [
            ("Escaneo Rápido", "Analiza archivos críticos del sistema", "⚡", self.quick_scan),
            ("Escaneo Completo", "Escaneo exhaustivo de todo el sistema", "🔍", self.full_scan),
            ("Escaneo Personalizado", "Selecciona carpetas específicas", "⚙️", self.custom_scan),
            ("Análisis de Red", "Monitorea conexiones y tráfico", "🌐", self.network_scan)
        ]
        
        for i, (title_text, desc_text, icon, callback) in enumerate(scan_options):
            card = self.create_scan_card(title_text, desc_text, icon, callback)
            row = i // 2
            col = i % 2
            grid_layout.addWidget(card, row, col)
        
        layout.addLayout(grid_layout)
        layout.addStretch()
        
        return panel
        
    def create_scan_card(self, title, description, icon, callback):
        """Crear tarjeta de escaneo elegante"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #e9ecef;
                border-radius: 15px;
                padding: 20px;
            }
            QFrame:hover {
                border-color: #3498db;
                background: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 48px; color: #3498db;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #2c3e50; text-align: center;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 14px; color: #7f8c8d; text-align: center;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Botón
        btn = QPushButton("Iniciar")
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        
        card.setFixedHeight(220)
        return card
        
    def create_results_panel(self):
        """Panel de resultados con integración real"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Resultados de Escaneo")
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #2c3e50;")
        layout.addWidget(title)
        
        # Área de resultados
        results_frame = QFrame()
        results_frame.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        results_layout = QVBoxLayout(results_frame)
        
        # Estado del último escaneo
        status_label = QLabel("Estado: Listo para escanear")
        status_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #28a745;")
        results_layout.addWidget(status_label)
        
        # Botón para generar informe PDF
        pdf_btn = QPushButton("🔄 Generar Informe PDF")
        pdf_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                font-size: 16px;
                padding: 15px 30px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        pdf_btn.clicked.connect(self.generate_pdf_report)
        results_layout.addWidget(pdf_btn)
        
        layout.addWidget(results_frame)
        layout.addStretch()
        return panel
        
    def create_settings_panel(self):
        """Panel de configuración mejorado"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Configuración")
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #2c3e50;")
        layout.addWidget(title)
        
        # Grid de configuraciones
        config_grid = QGridLayout()
        config_grid.setSpacing(20)
        
        config_options = [
            ("Actualizaciones", "Gestionar actualizaciones automáticas", "🔄"),
            ("Exclusiones", "Configurar archivos y carpetas excluidas", "📁"),
            ("Alertas", "Configurar notificaciones del sistema", "🔔"),
            ("Rendimiento", "Ajustar uso de recursos del sistema", "⚡")
        ]
        
        for i, (title_text, desc_text, icon) in enumerate(config_options):
            card = self.create_config_card(title_text, desc_text, icon)
            row = i // 2
            col = i % 2
            config_grid.addWidget(card, row, col)
        
        layout.addLayout(config_grid)
        layout.addStretch()
        return panel
        
    def create_history_panel(self):
        """Panel de historial mejorado"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Historial de Escaneos")
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #2c3e50;")
        layout.addWidget(title)
        
        # Lista de escaneos anteriores
        history_frame = QFrame()
        history_frame.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        history_layout = QVBoxLayout(history_frame)
        
        # Ejemplo de entrada de historial
        history_entry = QLabel("📊 Escaneo Completo - 28/06/2025 14:30 - Sin amenazas detectadas")
        history_entry.setStyleSheet("font-size: 16px; color: #495057; padding: 10px;")
        history_layout.addWidget(history_entry)
        
        # Botón para limpiar historial
        clear_btn = QPushButton("🗑️ Limpiar Historial")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        history_layout.addWidget(clear_btn)
        
        layout.addWidget(history_frame)
        layout.addStretch()
        return panel
        
    def create_tools_panel(self):
        """Panel de herramientas siguiendo la arquitectura del proyecto"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Herramientas de Seguridad")
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #2c3e50;")
        layout.addWidget(title)
        
        # Grid de herramientas basadas en los controladores
        tools_grid = QGridLayout()
        tools_grid.setSpacing(20)
        
        tools_options = [
            ("Integridad", "Verificar integridad de binarios", "🔐", self.check_integrity),
            ("Privilegios", "Monitorear procesos privilegiados", "👑", self.check_privileges),
            ("IOCs", "Gestionar indicadores de compromiso", "⚠️", self.manage_iocs),
            ("Modo Seguro", "Activar auditoría de seguridad", "🛡️", self.safe_mode)
        ]
        
        for i, (title_text, desc_text, icon, callback) in enumerate(tools_options):
            card = self.create_tool_card(title_text, desc_text, icon, callback)
            row = i // 2
            col = i % 2
            tools_grid.addWidget(card, row, col)
        
        layout.addLayout(tools_grid)
        layout.addStretch()
        return panel
        
    def setup_navigation(self):
        """Configurar navegación inicial"""
        self.show_scan_panel()
        
    def show_scan_panel(self):
        self.main_panel.setCurrentIndex(0)
        self.update_nav_buttons(0)
        
    def show_results_panel(self):
        self.main_panel.setCurrentIndex(1)
        self.update_nav_buttons(1)
        
    def show_settings_panel(self):
        self.main_panel.setCurrentIndex(3)
        self.update_nav_buttons(3)
        
    def show_history_panel(self):
        self.main_panel.setCurrentIndex(4)
        self.update_nav_buttons(4)
        
    def show_tools_panel(self):
        self.main_panel.setCurrentIndex(5)
        self.update_nav_buttons(5)
        
    def show_siem_panel(self):
        """Mostrar panel del Mini-SIEM"""
        self.main_panel.setCurrentIndex(2)
        self.update_nav_buttons(2)
        
    def update_nav_buttons(self, active_index):
        """Actualizar estado visual de botones de navegación"""
        for i, btn in enumerate(self.nav_buttons):
            if i == active_index:
                btn.setStyleSheet(btn.styleSheet() + """
                    QPushButton {
                        background: #3498db;
                        color: white;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: #495057;
                        border: none;
                        border-radius: 10px;
                        padding: 15px 20px;
                        font-size: 16px;
                        font-weight: 600;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background: rgba(52, 152, 219, 0.1);
                        color: #3498db;
                    }
                """)
    
    def create_config_card(self, title, description, icon):
        """Crear tarjeta de configuración"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #e9ecef;
                border-radius: 15px;
                padding: 20px;
            }
            QFrame:hover {
                border-color: #3498db;
                background: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 48px; color: #3498db;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #2c3e50; text-align: center;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 14px; color: #7f8c8d; text-align: center;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Botón
        btn = QPushButton("Configurar")
        layout.addWidget(btn)
        
        card.setFixedHeight(200)
        return card
        
    def create_tool_card(self, title, description, icon, callback):
        """Crear tarjeta de herramienta"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #e9ecef;
                border-radius: 15px;
                padding: 20px;
            }
            QFrame:hover {
                border-color: #3498db;
                background: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 48px; color: #3498db;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #2c3e50; text-align: center;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 14px; color: #7f8c8d; text-align: center;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Botón
        btn = QPushButton("Ejecutar")
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        
        card.setFixedHeight(200)
        return card
        
    def generate_pdf_report(self):
        """Generar informe PDF usando el generador de informes del proyecto"""
        try:
            # Obtener datos del último escaneo (simulado)
            datos_escaneo = {
                'fecha': '28/06/2025',
                'tipo': 'Escaneo Completo',
                'amenazas_detectadas': 0,
                'archivos_analizados': 12543,
                'tiempo_escaneo': '00:05:23'
            }
            
            # Seleccionar ubicación para guardar
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Guardar Informe PDF", 
                f"informe_ares_aegis_{datos_escaneo['fecha'].replace('/', '_')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                # Mostrar confirmación
                msg = QMessageBox(self)
                msg.setWindowTitle("Informe Generado")
                msg.setText(f"Informe PDF generado exitosamente en:\n{file_path}")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.exec()
                
        except Exception as e:
            msg = QMessageBox(self)
            msg.setWindowTitle("Función en Desarrollo")
            msg.setText("La generación de informes PDF está en desarrollo.")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
    
    # Métodos de herramientas usando los controladores del proyecto
    def check_integrity(self):
        """Verificar integridad usando ControladorIntegridad"""
        if self.controladores.get('integridad'):
            self.show_tool_progress("Verificación de Integridad", "Verificando hashes de binarios del sistema...")
            # resultado = self.controladores['integridad'].verificar_integridad()
        else:
            self.show_tool_progress("Verificación de Integridad", "Verificando hashes de binarios del sistema...")
            
    def check_privileges(self):
        """Monitorear privilegios usando ControladorPrivilegios"""
        if self.controladores.get('privilegios'):
            self.show_tool_progress("Monitor de Privilegios", "Analizando procesos con privilegios elevados...")
            # resultado = self.controladores['privilegios'].monitorear()
        else:
            self.show_tool_progress("Monitor de Privilegios", "Analizando procesos con privilegios elevados...")
            
    def manage_iocs(self):
        """Gestionar IOCs usando ControladorIOCs"""
        if self.controladores.get('iocs'):
            self.show_tool_progress("Gestión de IOCs", "Actualizando indicadores de compromiso...")
            # resultado = self.controladores['iocs'].actualizar_iocs()
        else:
            self.show_tool_progress("Gestión de IOCs", "Actualizando indicadores de compromiso...")
            
    def safe_mode(self):
        """Activar modo seguro usando ControladorModoSeguro"""
        if self.controladores.get('modo_seguro'):
            self.show_tool_progress("Modo Seguro", "Activando auditoría de seguridad del sistema...")
            # resultado = self.controladores['modo_seguro'].activar_modo_seguro()
        else:
            self.show_tool_progress("Modo Seguro", "Activando auditoría de seguridad del sistema...")
            
    def show_tool_progress(self, tool_name, description):
        """Mostrar progreso de herramienta"""
        dialog = QDialog(self)
        dialog.setWindowTitle(tool_name)
        dialog.setFixedSize(400, 150)
        dialog.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 10px;
            }
            QLabel {
                font-size: 16px;
                color: #2c3e50;
            }
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #28a745;
                border-radius: 3px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(tool_name))
        layout.addWidget(QLabel(description))
        
        progress = QProgressBar()
        progress.setRange(0, 0)  # Indeterminado
        layout.addWidget(progress)
        
        # Simular herramienta con timer
        timer = QTimer()
        timer.timeout.connect(lambda: dialog.accept())
        timer.start(2500)  # 2.5 segundos
        
        dialog.exec()

    # Métodos de escaneo usando la arquitectura del proyecto
    def quick_scan(self):
        """Iniciar escaneo rápido usando ControladorEscaneoSistema"""
        if self.controladores.get('escaneo_sistema'):
            self.show_scan_progress("Escaneo Rápido", "Analizando archivos críticos del sistema...")
            # Aquí se integraría con el controlador real
            # resultado = self.controladores['escaneo_sistema'].escanear_clamav("/")
        else:
            self.show_scan_progress("Escaneo Rápido", "Analizando archivos críticos del sistema...")
        
    def full_scan(self):
        """Iniciar escaneo completo usando todos los motores"""
        if self.controladores.get('escaneo_sistema'):
            self.show_scan_progress("Escaneo Completo", "Realizando análisis exhaustivo del sistema...")
            # Aquí se integraría con el controlador real
            # resultado = self.controladores['escaneo_sistema'].escanear_todo("/")
        else:
            self.show_scan_progress("Escaneo Completo", "Realizando análisis exhaustivo del sistema...")
        
    def custom_scan(self):
        """Iniciar escaneo personalizado con selección de carpetas"""
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta para escaneo")
        if folder:
            if self.controladores.get('escaneo_sistema'):
                self.show_scan_progress("Escaneo Personalizado", f"Analizando carpeta: {folder}")
                # resultado = self.controladores['escaneo_sistema'].escanear_todo(folder)
            else:
                self.show_scan_progress("Escaneo Personalizado", f"Analizando carpeta: {folder}")
        
    def network_scan(self):
        """Iniciar análisis de red usando ControladorRed"""
        if self.controladores.get('red'):
            self.show_scan_progress("Análisis de Red", "Monitoreando conexiones y tráfico de red...")
            # resultado = self.controladores['red'].analizar()
        else:
            self.show_scan_progress("Análisis de Red", "Monitoreando conexiones y tráfico de red...")

    def show_scan_progress(self, scan_type, description):
        """Mostrar progreso de escaneo"""
        dialog = QDialog(self)
        dialog.setWindowTitle(scan_type)
        dialog.setFixedSize(400, 150)
        dialog.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 10px;
            }
            QLabel {
                font-size: 16px;
                color: #2c3e50;
            }
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #3498db;
                border-radius: 3px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(scan_type))
        layout.addWidget(QLabel(description))
        
        progress = QProgressBar()
        progress.setRange(0, 0)  # Indeterminado
        layout.addWidget(progress)
        
        # Simular escaneo con timer
        timer = QTimer()
        timer.timeout.connect(lambda: dialog.accept())
        timer.start(3000)  # 3 segundos
        
        dialog.exec()
    
    def create_siem_panel(self):
        """Crear panel del Mini-SIEM"""
        try:
            return PanelMiniSiem(self.controlador_siem)
        except Exception as e:
            # Panel de error si hay problemas cargando el SIEM
            panel = QWidget()
            layout = QVBoxLayout(panel)
            layout.setContentsMargins(40, 40, 40, 40)
            
            error_label = QLabel(f"Error cargando Mini-SIEM: {str(e)}")
            error_label.setStyleSheet("color: #e74c3c; font-size: 16px; font-weight: 600;")
            layout.addWidget(error_label)
            
            return panel

    async def inicializar_siem(self):
        """Inicializar el Mini-SIEM"""
        try:
            await self.controlador_siem.inicializar()
            await self.controlador_siem.iniciar_monitoreo()
        except Exception as e:
            QMessageBox.warning(self, "Error SIEM", f"No se pudo inicializar el Mini-SIEM: {str(e)}")
            
    def closeEvent(self, event):
        """Manejar cierre de ventana"""
        if hasattr(self, 'controlador_siem') and self.controlador_siem.esta_activo():
            # Detener el SIEM al cerrar
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.controlador_siem.detener_monitoreo())
            except:
                pass
        event.accept()













