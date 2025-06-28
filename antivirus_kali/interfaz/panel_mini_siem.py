"""
Panel de Mini-SIEM para la interfaz de Ares Aegis
Proporciona visualización y control del sistema de gestión de eventos de seguridad
"""

import asyncio
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QTextEdit, QProgressBar,
    QComboBox, QSpinBox, QCheckBox, QGroupBox, QListWidget,
    QListWidgetItem, QDialog, QDialogButtonBox, QFormLayout,
    QLineEdit, QDateTimeEdit, QScrollArea, QSplitter
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, pyqtSignal
from PySide6.QtGui import QFont, QColor, QPalette
import logging

logger = logging.getLogger(__name__)

class PanelMiniSiem(QWidget):
    """Panel principal del Mini-SIEM"""
    
    def __init__(self, controlador_siem=None):
        super().__init__()
        self.controlador_siem = controlador_siem
        self.setup_ui()
        self.setup_timers()
        
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("Mini-SIEM - Sistema de Gestión de Eventos de Seguridad")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        layout.addWidget(title)
        
        # Estado del sistema
        self.create_system_status(layout)
        
        # Pestañas principales
        self.create_main_tabs(layout)
        
    def create_system_status(self, parent_layout):
        """Crear panel de estado del sistema"""
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71);
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: white;
                font-weight: 600;
            }
        """)
        status_frame.setFixedHeight(80)
        
        status_layout = QHBoxLayout(status_frame)
        
        # Estado SIEM
        self.status_label = QLabel("🔍 Mini-SIEM: ACTIVO")
        self.status_label.setStyleSheet("font-size: 18px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # Botones de control
        self.btn_iniciar = QPushButton("▶️ Iniciar")
        self.btn_detener = QPushButton("⏹️ Detener")
        self.btn_diagnostico = QPushButton("🔧 Diagnóstico")
        
        for btn in [self.btn_iniciar, self.btn_detener, self.btn_diagnostico]:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.3);
                }
            """)
            
        self.btn_iniciar.clicked.connect(self.iniciar_siem)
        self.btn_detener.clicked.connect(self.detener_siem)
        self.btn_diagnostico.clicked.connect(self.ejecutar_diagnostico)
        
        status_layout.addWidget(self.btn_iniciar)
        status_layout.addWidget(self.btn_detener)
        status_layout.addWidget(self.btn_diagnostico)
        
        parent_layout.addWidget(status_frame)
        
    def create_main_tabs(self, parent_layout):
        """Crear pestañas principales"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                color: #2c3e50;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background: #bdc3c7;
            }
        """)
        
        # Tab Dashboard
        self.create_dashboard_tab()
        
        # Tab Eventos en Tiempo Real
        self.create_events_tab()
        
        # Tab Alertas
        self.create_alerts_tab()
        
        # Tab Estadísticas
        self.create_statistics_tab()
        
        # Tab Configuración
        self.create_config_tab()
        
        parent_layout.addWidget(self.tab_widget)
        
    def create_dashboard_tab(self):
        """Crear tab de dashboard"""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        layout.setSpacing(20)
        
        # Métricas principales
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        metrics_layout = QGridLayout(metrics_frame)
        
        # Cards de métricas
        self.metric_eventos_hoy = self.create_metric_card("Eventos Hoy", "0", "#3498db")
        self.metric_alertas_activas = self.create_metric_card("Alertas Activas", "0", "#e74c3c")
        self.metric_reglas_activas = self.create_metric_card("Reglas Activas", "0", "#27ae60")
        self.metric_fuentes_monitoreadas = self.create_metric_card("Fuentes Monitoreadas", "0", "#f39c12")
        
        metrics_layout.addWidget(self.metric_eventos_hoy, 0, 0)
        metrics_layout.addWidget(self.metric_alertas_activas, 0, 1)
        metrics_layout.addWidget(self.metric_reglas_activas, 1, 0)
        metrics_layout.addWidget(self.metric_fuentes_monitoreadas, 1, 1)
        
        layout.addWidget(metrics_frame)
        
        # Eventos recientes
        recent_frame = QFrame()
        recent_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.addWidget(QLabel("Eventos Recientes"))
        
        self.tabla_eventos_recientes = QTableWidget()
        self.tabla_eventos_recientes.setColumnCount(4)
        self.tabla_eventos_recientes.setHorizontalHeaderLabels([
            "Timestamp", "Categoría", "Severidad", "Mensaje"
        ])
        self.tabla_eventos_recientes.horizontalHeader().setStretchLastSection(True)
        self.tabla_eventos_recientes.setAlternatingRowColors(True)
        self.tabla_eventos_recientes.setRowCount(0)
        
        recent_layout.addWidget(self.tabla_eventos_recientes)
        layout.addWidget(recent_frame)
        
        self.tab_widget.addTab(dashboard_widget, "📊 Dashboard")
        
    def create_events_tab(self):
        """Crear tab de eventos en tiempo real"""
        events_widget = QWidget()
        layout = QVBoxLayout(events_widget)
        
        # Controles de filtrado
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        filter_layout = QHBoxLayout(filter_frame)
        
        filter_layout.addWidget(QLabel("Filtrar por:"))
        
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(["Todas", "authentication", "network", "system", "package"])
        filter_layout.addWidget(self.combo_categoria)
        
        self.combo_severidad = QComboBox()
        self.combo_severidad.addItems(["Todas", "INFO", "WARNING", "HIGH", "CRITICAL"])
        filter_layout.addWidget(self.combo_severidad)
        
        btn_aplicar_filtros = QPushButton("Aplicar Filtros")
        btn_aplicar_filtros.clicked.connect(self.aplicar_filtros_eventos)
        filter_layout.addWidget(btn_aplicar_filtros)
        
        filter_layout.addStretch()
        
        btn_limpiar_eventos = QPushButton("🗑️ Limpiar")
        btn_limpiar_eventos.clicked.connect(self.limpiar_tabla_eventos)
        filter_layout.addWidget(btn_limpiar_eventos)
        
        layout.addWidget(filter_frame)
        
        # Tabla de eventos
        self.tabla_eventos = QTableWidget()
        self.tabla_eventos.setColumnCount(6)
        self.tabla_eventos.setHorizontalHeaderLabels([
            "Timestamp", "Categoría", "Tipo", "Severidad", "Origen", "Mensaje"
        ])
        self.tabla_eventos.horizontalHeader().setStretchLastSection(True)
        self.tabla_eventos.setAlternatingRowColors(True)
        
        layout.addWidget(self.tabla_eventos)
        
        self.tab_widget.addTab(events_widget, "📝 Eventos en Tiempo Real")
        
    def create_alerts_tab(self):
        """Crear tab de alertas"""
        alerts_widget = QWidget()
        layout = QVBoxLayout(alerts_widget)
        
        # Estadísticas de alertas
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        stats_layout = QHBoxLayout(stats_frame)
        
        self.label_total_alertas = QLabel("Total de Alertas: 0")
        self.label_alertas_criticas = QLabel("Críticas: 0")
        self.label_alertas_altas = QLabel("Altas: 0")
        
        for label in [self.label_total_alertas, self.label_alertas_criticas, self.label_alertas_altas]:
            label.setStyleSheet("font-weight: 600; color: #856404;")
            
        stats_layout.addWidget(self.label_total_alertas)
        stats_layout.addWidget(self.label_alertas_criticas)
        stats_layout.addWidget(self.label_alertas_altas)
        stats_layout.addStretch()
        
        layout.addWidget(stats_frame)
        
        # Lista de alertas
        self.lista_alertas = QListWidget()
        self.lista_alertas.setStyleSheet("""
            QListWidget {
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f1f2f6;
            }
            QListWidget::item:selected {
                background: #3498db;
                color: white;
            }
        """)
        
        layout.addWidget(self.lista_alertas)
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        
        btn_exportar_alertas = QPushButton("📤 Exportar Alertas")
        btn_limpiar_alertas = QPushButton("🗑️ Limpiar Alertas")
        
        btn_exportar_alertas.clicked.connect(self.exportar_alertas)
        btn_limpiar_alertas.clicked.connect(self.limpiar_alertas)
        
        btn_layout.addWidget(btn_exportar_alertas)
        btn_layout.addWidget(btn_limpiar_alertas)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.tab_widget.addTab(alerts_widget, "🚨 Alertas")
        
    def create_statistics_tab(self):
        """Crear tab de estadísticas"""
        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)
        
        # Gráfico placeholder (se puede integrar con matplotlib)
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                min-height: 300px;
            }
        """)
        
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.addWidget(QLabel("📈 Gráficos de Eventos (Próximamente)"))
        chart_layout.addWidget(QLabel("• Eventos por día"))
        chart_layout.addWidget(QLabel("• Distribución por categoría"))
        chart_layout.addWidget(QLabel("• Tendencias de amenazas"))
        chart_layout.addStretch()
        
        layout.addWidget(chart_frame)
        
        # Tabla de estadísticas
        self.tabla_estadisticas = QTableWidget()
        self.tabla_estadisticas.setColumnCount(2)
        self.tabla_estadisticas.setHorizontalHeaderLabels(["Métrica", "Valor"])
        self.tabla_estadisticas.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.tabla_estadisticas)
        
        self.tab_widget.addTab(stats_widget, "📈 Estadísticas")
        
    def create_config_tab(self):
        """Crear tab de configuración"""
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        
        # Configuración de notificaciones
        notif_group = QGroupBox("Configuración de Notificaciones")
        notif_layout = QVBoxLayout(notif_group)
        
        self.check_notif_desktop = QCheckBox("Notificaciones de escritorio")
        self.check_notif_terminal = QCheckBox("Notificaciones en terminal")
        self.check_notif_log = QCheckBox("Registro en logs")
        
        self.check_notif_desktop.setChecked(True)
        self.check_notif_terminal.setChecked(True)
        self.check_notif_log.setChecked(True)
        
        notif_layout.addWidget(self.check_notif_desktop)
        notif_layout.addWidget(self.check_notif_terminal)
        notif_layout.addWidget(self.check_notif_log)
        
        btn_aplicar_notif = QPushButton("Aplicar Configuración")
        btn_aplicar_notif.clicked.connect(self.aplicar_config_notificaciones)
        notif_layout.addWidget(btn_aplicar_notif)
        
        layout.addWidget(notif_group)
        
        # Configuración de retención
        retention_group = QGroupBox("Configuración de Retención de Datos")
        retention_layout = QHBoxLayout(retention_group)
        
        retention_layout.addWidget(QLabel("Días de retención:"))
        self.spin_retention = QSpinBox()
        self.spin_retention.setRange(1, 365)
        self.spin_retention.setValue(30)
        retention_layout.addWidget(self.spin_retention)
        
        btn_aplicar_retention = QPushButton("Aplicar")
        btn_aplicar_retention.clicked.connect(self.aplicar_config_retention)
        retention_layout.addWidget(btn_aplicar_retention)
        
        retention_layout.addStretch()
        
        layout.addWidget(retention_group)
        
        # Gestión de reglas
        rules_group = QGroupBox("Gestión de Reglas de Correlación")
        rules_layout = QVBoxLayout(rules_group)
        
        btn_layout = QHBoxLayout()
        
        btn_agregar_regla = QPushButton("➕ Agregar Regla")
        btn_editar_regla = QPushButton("✏️ Editar Regla")
        btn_eliminar_regla = QPushButton("🗑️ Eliminar Regla")
        
        btn_agregar_regla.clicked.connect(self.agregar_regla_dialog)
        
        btn_layout.addWidget(btn_agregar_regla)
        btn_layout.addWidget(btn_editar_regla)
        btn_layout.addWidget(btn_eliminar_regla)
        btn_layout.addStretch()
        
        rules_layout.addLayout(btn_layout)
        
        self.lista_reglas = QListWidget()
        rules_layout.addWidget(self.lista_reglas)
        
        layout.addWidget(rules_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(config_widget, "⚙️ Configuración")
        
    def create_metric_card(self, titulo: str, valor: str, color: str) -> QFrame:
        """Crear tarjeta de métrica"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-left: 4px solid {color};
                border-radius: 5px;
                padding: 15px;
            }}
            QLabel {{
                color: #2c3e50;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        value_label = QLabel(valor)
        value_label.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {color};")
        
        title_label = QLabel(titulo)
        title_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        
        return card
        
    def setup_timers(self):
        """Configurar timers para actualización automática"""
        # Timer para actualizar dashboard cada 5 segundos
        self.timer_dashboard = QTimer()
        self.timer_dashboard.timeout.connect(self.actualizar_dashboard)
        self.timer_dashboard.start(5000)
        
        # Timer para eventos en tiempo real cada 2 segundos
        self.timer_eventos = QTimer()
        self.timer_eventos.timeout.connect(self.actualizar_eventos_tiempo_real)
        self.timer_eventos.start(2000)
        
    def actualizar_dashboard(self):
        """Actualizar métricas del dashboard"""
        if not self.controlador_siem:
            return
            
        try:
            stats = self.controlador_siem.obtener_estadisticas_completas()
            
            # Actualizar métricas
            dashboard_stats = stats.get('dashboard', {})
            self.metric_eventos_hoy.findChild(QLabel).setText(
                str(dashboard_stats.get('total_eventos', 0))
            )
            
            correlacion_stats = stats.get('correlacion', {})
            self.metric_reglas_activas.findChild(QLabel).setText(
                str(correlacion_stats.get('reglas_activas', 0))
            )
            
            # Actualizar estado
            estado = stats.get('estado', 'inactivo')
            if estado == 'activo':
                self.status_label.setText("🔍 Mini-SIEM: ACTIVO")
                self.status_label.parent().setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #27ae60, stop:1 #2ecc71);
                        border-radius: 10px;
                        padding: 15px;
                    }
                    QLabel {
                        color: white;
                        font-weight: 600;
                    }
                """)
            else:
                self.status_label.setText("🔍 Mini-SIEM: INACTIVO")
                self.status_label.parent().setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #e74c3c, stop:1 #c0392b);
                        border-radius: 10px;
                        padding: 15px;
                    }
                    QLabel {
                        color: white;
                        font-weight: 600;
                    }
                """)
                
        except Exception as e:
            logger.error(f"Error actualizando dashboard: {e}")
            
    def actualizar_eventos_tiempo_real(self):
        """Actualizar tabla de eventos en tiempo real"""
        if not self.controlador_siem:
            return
            
        try:
            eventos = self.controlador_siem.consultar_eventos_recientes(limite=20)
            
            # Actualizar tabla de eventos recientes en dashboard
            self.tabla_eventos_recientes.setRowCount(min(len(eventos), 10))
            
            for i, evento in enumerate(eventos[:10]):
                self.tabla_eventos_recientes.setItem(i, 0, 
                    QTableWidgetItem(str(evento.get('timestamp', ''))))
                self.tabla_eventos_recientes.setItem(i, 1, 
                    QTableWidgetItem(str(evento.get('event_category', ''))))
                self.tabla_eventos_recientes.setItem(i, 2, 
                    QTableWidgetItem(str(evento.get('severity', ''))))
                self.tabla_eventos_recientes.setItem(i, 3, 
                    QTableWidgetItem(str(evento.get('message', ''))))
                    
            # Actualizar tabla completa de eventos
            self.tabla_eventos.setRowCount(len(eventos))
            
            for i, evento in enumerate(eventos):
                self.tabla_eventos.setItem(i, 0, 
                    QTableWidgetItem(str(evento.get('timestamp', ''))))
                self.tabla_eventos.setItem(i, 1, 
                    QTableWidgetItem(str(evento.get('event_category', ''))))
                self.tabla_eventos.setItem(i, 2, 
                    QTableWidgetItem(str(evento.get('event_type', ''))))
                self.tabla_eventos.setItem(i, 3, 
                    QTableWidgetItem(str(evento.get('severity', ''))))
                self.tabla_eventos.setItem(i, 4, 
                    QTableWidgetItem(str(evento.get('source_type', ''))))
                self.tabla_eventos.setItem(i, 5, 
                    QTableWidgetItem(str(evento.get('message', ''))))
                    
        except Exception as e:
            logger.debug(f"Error actualizando eventos: {e}")
            
    def iniciar_siem(self):
        """Iniciar Mini-SIEM"""
        if self.controlador_siem:
            try:
                # Ejecutar en thread separado para no bloquear UI
                import threading
                threading.Thread(
                    target=lambda: asyncio.run(self.controlador_siem.iniciar()),
                    daemon=True
                ).start()
                logger.info("Mini-SIEM iniciado desde interfaz")
            except Exception as e:
                logger.error(f"Error iniciando Mini-SIEM: {e}")
                
    def detener_siem(self):
        """Detener Mini-SIEM"""
        if self.controlador_siem:
            try:
                import threading
                threading.Thread(
                    target=lambda: asyncio.run(self.controlador_siem.detener()),
                    daemon=True
                ).start()
                logger.info("Mini-SIEM detenido desde interfaz")
            except Exception as e:
                logger.error(f"Error deteniendo Mini-SIEM: {e}")
                
    def ejecutar_diagnostico(self):
        """Ejecutar diagnóstico del sistema"""
        if self.controlador_siem:
            try:
                import threading
                threading.Thread(
                    target=self._ejecutar_diagnostico_async,
                    daemon=True
                ).start()
            except Exception as e:
                logger.error(f"Error ejecutando diagnóstico: {e}")
                
    def _ejecutar_diagnostico_async(self):
        """Ejecutar diagnóstico de forma asíncrona"""
        try:
            resultado = asyncio.run(self.controlador_siem.realizar_diagnostico())
            # Mostrar resultado en dialog
            # self.mostrar_resultado_diagnostico(resultado)
        except Exception as e:
            logger.error(f"Error en diagnóstico async: {e}")
            
    def aplicar_filtros_eventos(self):
        """Aplicar filtros a la tabla de eventos"""
        # Implementar filtrado
        pass
        
    def limpiar_tabla_eventos(self):
        """Limpiar tabla de eventos"""
        self.tabla_eventos.setRowCount(0)
        
    def exportar_alertas(self):
        """Exportar alertas a archivo"""
        # Implementar exportación
        pass
        
    def limpiar_alertas(self):
        """Limpiar lista de alertas"""
        self.lista_alertas.clear()
        
    def aplicar_config_notificaciones(self):
        """Aplicar configuración de notificaciones"""
        if self.controlador_siem:
            self.controlador_siem.configurar_notificaciones(
                desktop=self.check_notif_desktop.isChecked(),
                terminal=self.check_notif_terminal.isChecked(),
                log=self.check_notif_log.isChecked()
            )
            
    def aplicar_config_retention(self):
        """Aplicar configuración de retención"""
        # Implementar cambio de retención
        pass
        
    def agregar_regla_dialog(self):
        """Mostrar diálogo para agregar regla"""
        dialog = DialogAgregarRegla(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config_regla = dialog.obtener_configuracion()
            if self.controlador_siem:
                self.controlador_siem.agregar_regla_personalizada(config_regla)
                
class DialogAgregarRegla(QDialog):
    """Diálogo para agregar reglas de correlación"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Regla de Correlación")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        
        self.edit_nombre = QLineEdit()
        self.edit_descripcion = QLineEdit()
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["umbral", "secuencial"])
        
        self.combo_severidad = QComboBox()
        self.combo_severidad.addItems(["INFO", "WARNING", "HIGH", "CRITICAL"])
        
        self.spin_umbral = QSpinBox()
        self.spin_umbral.setRange(1, 1000)
        self.spin_umbral.setValue(5)
        
        self.spin_ventana = QSpinBox()
        self.spin_ventana.setRange(60, 86400)  # 1 minuto a 1 día
        self.spin_ventana.setValue(300)
        
        form_layout.addRow("Nombre:", self.edit_nombre)
        form_layout.addRow("Descripción:", self.edit_descripcion)
        form_layout.addRow("Tipo:", self.combo_tipo)
        form_layout.addRow("Severidad:", self.combo_severidad)
        form_layout.addRow("Umbral:", self.spin_umbral)
        form_layout.addRow("Ventana (seg):", self.spin_ventana)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        
    def obtener_configuracion(self) -> dict:
        """Obtener configuración de la regla"""
        return {
            'nombre': self.edit_nombre.text(),
            'descripcion': self.edit_descripcion.text(),
            'tipo': self.combo_tipo.currentText(),
            'severidad': self.combo_severidad.currentText(),
            'umbral': self.spin_umbral.value(),
            'ventana_tiempo': self.spin_ventana.value(),
            'filtros': {}
        }
