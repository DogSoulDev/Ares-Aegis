#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Panel Especializado para Mini-SIEM
Integra todas las funcionalidades de monitoreo y análisis de seguridad
"""

from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import json
from collections import defaultdict, deque

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QGroupBox,
    QComboBox, QSpinBox, QCheckBox, QLineEdit, QSplitter, QTabWidget,
    QListWidget, QListWidgetItem, QHeaderView, QAbstractItemView,
    QTextEdit, QProgressBar, QSlider, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QMutex, QDateTime
from PySide6.QtGui import QFont, QIcon, QColor, QPalette

from ..estilo_japones import EstiloJapones
from antivirus_kali.utilidades.logger import SiemLogger

class MonitorEventos(QThread):
    """Hilo para monitorear eventos de seguridad en tiempo real"""
    
    # Señales
    evento_detectado = Signal(dict)  # evento completo
    estadisticas_actualizadas = Signal(dict)  # estadísticas actuales
    alerta_critica = Signal(str, str)  # tipo, mensaje
    
    def __init__(self):
        super().__init__()
        self.mutex = QMutex()
        self.activo = True
        self.logger = SiemLogger(__name__)
        self.eventos_buffer = deque(maxlen=1000)
        self.contador_eventos = defaultdict(int)
        
    def detener(self):
        """Detiene el monitoreo"""
        self.mutex.lock()
        self.activo = False
        self.mutex.unlock()
        
    def run(self):
        """Ejecuta el monitoreo en segundo plano"""
        try:
            while self.activo:
                self._generar_eventos_simulados()
                self.msleep(2000)  # Eventos cada 2 segundos
                
        except Exception as e:
            self.logger.error(f"Error en monitor de eventos: {e}")
            
    def _generar_eventos_simulados(self):
        """Genera eventos simulados para demostración"""
        if not self.activo:
            return
            
        import random
        
        tipos_eventos = [
            ("login_exitoso", "Inicio de sesión exitoso", "INFO"),
            ("login_fallido", "Intento de login fallido", "WARNING"),
            ("archivo_modificado", "Archivo del sistema modificado", "INFO"),
            ("proceso_sospechoso", "Proceso sospechoso detectado", "WARNING"),
            ("conexion_red", "Nueva conexión de red", "INFO"),
            ("escalacion_privilegios", "Intento de escalación de privilegios", "CRITICAL"),
            ("malware_detectado", "Malware detectado", "CRITICAL"),
            ("acceso_no_autorizado", "Acceso no autorizado detectado", "CRITICAL"),
            ("trafico_anomalo", "Tráfico de red anómalo", "WARNING"),
            ("vulnerabilidad_detectada", "Vulnerabilidad detectada", "HIGH")
        ]
        
        # Generar 1-3 eventos por ciclo
        num_eventos = random.randint(1, 3)
        
        for _ in range(num_eventos):
            tipo, descripcion, severidad = random.choice(tipos_eventos)
            
            evento = {
                "timestamp": datetime.now(),
                "tipo": tipo,
                "descripcion": descripcion,
                "severidad": severidad,
                "origen": random.choice(["sistema", "red", "aplicacion", "usuario"]),
                "usuario": random.choice(["root", "admin", "user1", "guest", "service"]),
                "ip_origen": f"192.168.1.{random.randint(1, 254)}",
                "detalles": self._generar_detalles_evento(tipo),
                "id": f"EVT-{random.randint(10000, 99999)}"
            }
            
            self.eventos_buffer.append(evento)
            self.contador_eventos[severidad] += 1
            
            self.evento_detectado.emit(evento)
            
            # Generar alerta crítica si es necesario
            if severidad in ["CRITICAL", "HIGH"]:
                self.alerta_critica.emit(severidad, f"{descripcion} - {evento['detalles']}")
                
        # Emitir estadísticas actualizadas
        estadisticas = {
            "total_eventos": len(self.eventos_buffer),
            "eventos_criticos": self.contador_eventos["CRITICAL"],
            "eventos_altos": self.contador_eventos["HIGH"],
            "eventos_warning": self.contador_eventos["WARNING"],
            "eventos_info": self.contador_eventos["INFO"],
            "eventos_ultima_hora": self._contar_eventos_ultima_hora()
        }
        
        self.estadisticas_actualizadas.emit(estadisticas)
        
    def _generar_detalles_evento(self, tipo: str) -> str:
        """Genera detalles específicos para cada tipo de evento"""
        import random
        
        detalles_map = {
            "login_exitoso": [
                "Usuario autenticado vía SSH",
                "Login desde consola local",
                "Autenticación web exitosa"
            ],
            "login_fallido": [
                "Contraseña incorrecta",
                "Usuario no encontrado",
                "Cuenta bloqueada"
            ],
            "archivo_modificado": [
                "Modificación en /etc/passwd",
                "Cambio en configuración del sistema",
                "Actualización de archivo de log"
            ],
            "proceso_sospechoso": [
                "Proceso con alta CPU",
                "Proceso sin firma digital",
                "Proceso accediendo a archivos sensibles"
            ],
            "conexion_red": [
                "Conexión saliente HTTPS",
                "Conexión SSH entrante",
                "Tráfico P2P detectado"
            ],
            "escalacion_privilegios": [
                "Uso de sudo sin autorización",
                "Intento de acceso root",
                "Modificación de permisos críticos"
            ],
            "malware_detectado": [
                "Troyano en directorio temporal",
                "Ransomware bloqueado",
                "Rootkit detectado en kernel"
            ],
            "acceso_no_autorizado": [
                "Acceso fuera de horario laboral",
                "IP no autorizada",
                "Múltiples intentos fallidos"
            ],
            "trafico_anomalo": [
                "Volumen inusual de datos",
                "Conexiones a IPs sospechosas",
                "Protocolos no autorizados"
            ],
            "vulnerabilidad_detectada": [
                "CVE-2023-12345 detectada",
                "Puerto abierto sin autorización",
                "Servicio desactualizado"
            ]
        }
        
        return random.choice(detalles_map.get(tipo, ["Evento de seguridad"]))
        
    def _contar_eventos_ultima_hora(self) -> int:
        """Cuenta eventos de la última hora"""
        ahora = datetime.now()
        hace_una_hora = ahora - timedelta(hours=1)
        
        return sum(1 for evento in self.eventos_buffer 
                  if evento["timestamp"] >= hace_una_hora)


class PanelMiniSiem(QWidget):
    """Panel principal para todas las funcionalidades del Mini-SIEM"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = SiemLogger(__name__)
        self.monitor_eventos = MonitorEventos()
        self.eventos_criticos = []
        self.reglas_personalizadas = []
        self._setup_ui()
        self._conectar_señales()
        self._iniciar_monitoreo()
        
    def _setup_ui(self):
        """Configura la interfaz del panel"""
        layout = QVBoxLayout(self)
        layout.setSpacing(EstiloJapones.ESPACIADO['normal'])
        
        # Título
        titulo = QLabel("🔍 Mini-SIEM Dashboard")
        titulo.setProperty("estiloTitulo", "true")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Panel de estado general
        self._crear_panel_estado_general(layout)
        
        # Tabs principales
        tabs_siem = QTabWidget()
        
        # Tab de eventos en tiempo real
        self._crear_tab_eventos_tiempo_real(tabs_siem)
        
        # Tab de análisis de amenazas
        self._crear_tab_analisis_amenazas(tabs_siem)
        
        # Tab de reglas y alertas
        self._crear_tab_reglas_alertas(tabs_siem)
        
        # Tab de estadísticas avanzadas
        self._crear_tab_estadisticas_avanzadas(tabs_siem)
        
        # Tab de configuración SIEM
        self._crear_tab_configuracion_siem(tabs_siem)
        
        layout.addWidget(tabs_siem)
        
    def _crear_panel_estado_general(self, layout):
        """Crea el panel de estado general del SIEM"""
        frame_estado = QFrame()
        frame_estado.setMaximumHeight(120)
        frame_estado.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        layout_estado = QHBoxLayout(frame_estado)
        
        # Métricas principales
        metricas = [
            ("🟢 Estado del Sistema", "Activo", "estado_sistema"),
            ("📊 Eventos Totales", "0", "total_eventos"),
            ("🚨 Alertas Críticas", "0", "alertas_criticas"),
            ("⚠️ Eventos de Riesgo Alto", "0", "eventos_alto_riesgo"),
            ("📈 Eventos/Hora", "0", "eventos_por_hora"),
            ("🔄 Última Actualización", "Nunca", "ultima_actualizacion")
        ]
        
        self.labels_metricas = {}
        
        for titulo, valor_inicial, clave in metricas:
            widget_metrica = QWidget()
            layout_metrica = QVBoxLayout(widget_metrica)
            layout_metrica.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            label_titulo = QLabel(titulo)
            label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_titulo.setStyleSheet("font-weight: bold; color: #495057;")
            
            label_valor = QLabel(valor_inicial)
            label_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_valor.setStyleSheet("font-size: 18px; font-weight: bold; color: #007BFF;")
            
            self.labels_metricas[clave] = label_valor
            
            layout_metrica.addWidget(label_titulo)
            layout_metrica.addWidget(label_valor)
            
            layout_estado.addWidget(widget_metrica)
            
        layout.addWidget(frame_estado)
        
    def _crear_tab_eventos_tiempo_real(self, tabs):
        """Crea el tab de eventos en tiempo real"""
        tab_eventos = QWidget()
        layout = QVBoxLayout(tab_eventos)
        
        # Controles superiores
        layout_controles = QHBoxLayout()
        
        self.combo_filtro_severidad = QComboBox()
        self.combo_filtro_severidad.addItems(["Todas las severidades", "CRITICAL", "HIGH", "WARNING", "INFO"])
        layout_controles.addWidget(QLabel("Filtrar por severidad:"))
        layout_controles.addWidget(self.combo_filtro_severidad)
        
        self.combo_filtro_origen = QComboBox()
        self.combo_filtro_origen.addItems(["Todos los orígenes", "sistema", "red", "aplicacion", "usuario"])
        layout_controles.addWidget(QLabel("Origen:"))
        layout_controles.addWidget(self.combo_filtro_origen)
        
        btn_limpiar_eventos = QPushButton("🗑️ Limpiar")
        btn_pausar_monitor = QPushButton("⏸️ Pausar")
        layout_controles.addWidget(btn_limpiar_eventos)
        layout_controles.addWidget(btn_pausar_monitor)
        layout_controles.addStretch()
        
        layout.addLayout(layout_controles)
        
        # Tabla de eventos
        self.tabla_eventos = QTableWidget()
        self.tabla_eventos.setColumnCount(7)
        self.tabla_eventos.setHorizontalHeaderLabels([
            "Timestamp", "Severidad", "Tipo", "Descripción", "Origen", "Usuario", "IP Origen"
        ])
        
        # Configurar tabla
        header = self.tabla_eventos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.tabla_eventos.setAlternatingRowColors(True)
        self.tabla_eventos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_eventos.setSortingEnabled(True)
        
        layout.addWidget(self.tabla_eventos)
        
        tabs.addTab(tab_eventos, "🔄 Eventos en Tiempo Real")
        
    def _crear_tab_analisis_amenazas(self, tabs):
        """Crea el tab de análisis de amenazas"""
        tab_amenazas = QWidget()
        layout = QVBoxLayout(tab_amenazas)
        
        # Splitter horizontal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo - Alertas críticas
        self._crear_panel_alertas_criticas(splitter)
        
        # Panel derecho - Análisis detallado
        self._crear_panel_analisis_detallado(splitter)
        
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
        
        tabs.addTab(tab_amenazas, "🚨 Análisis de Amenazas")
        
    def _crear_panel_alertas_criticas(self, parent):
        """Crea el panel de alertas críticas"""
        widget_alertas = QWidget()
        layout = QVBoxLayout(widget_alertas)
        
        # Título
        titulo = QLabel("🚨 Alertas Críticas")
        titulo.setProperty("estiloSubtitulo", "true")
        layout.addWidget(titulo)
        
        # Lista de alertas
        self.lista_alertas_criticas = QListWidget()
        self.lista_alertas_criticas.setMaximumHeight(200)
        layout.addWidget(self.lista_alertas_criticas)
        
        # Botones de acción
        layout_botones_alertas = QHBoxLayout()
        btn_investigar = QPushButton("🔍 Investigar")
        btn_resolver = QPushButton("✅ Resolver")
        btn_escalar = QPushButton("⬆️ Escalar")
        
        layout_botones_alertas.addWidget(btn_investigar)
        layout_botones_alertas.addWidget(btn_resolver)
        layout_botones_alertas.addWidget(btn_escalar)
        
        layout.addLayout(layout_botones_alertas)
        
        # Panel de correlación de eventos
        grupo_correlacion = QGroupBox("🔗 Correlación de Eventos")
        layout_correlacion = QVBoxLayout(grupo_correlacion)
        
        self.texto_correlacion = QTextEdit()
        self.texto_correlacion.setMaximumHeight(150)
        self.texto_correlacion.setPlainText("Esperando eventos para análisis de correlación...")
        layout_correlacion.addWidget(self.texto_correlacion)
        
        layout.addWidget(grupo_correlacion)
        
        # Indicadores de riesgo
        grupo_riesgo = QGroupBox("⚠️ Nivel de Riesgo Actual")
        layout_riesgo = QVBoxLayout(grupo_riesgo)
        
        self.label_nivel_riesgo = QLabel("BAJO")
        self.label_nivel_riesgo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_nivel_riesgo.setStyleSheet("""
            font-size: 24px; font-weight: bold; 
            color: white; background-color: #28A745; 
            padding: 10px; border-radius: 8px;
        """)
        layout_riesgo.addWidget(self.label_nivel_riesgo)
        
        self.progreso_riesgo = QProgressBar()
        self.progreso_riesgo.setRange(0, 100)
        self.progreso_riesgo.setValue(15)
        layout_riesgo.addWidget(self.progreso_riesgo)
        
        layout.addWidget(grupo_riesgo)
        
        parent.addWidget(widget_alertas)
        
    def _crear_panel_analisis_detallado(self, parent):
        """Crea el panel de análisis detallado"""
        widget_analisis = QWidget()
        layout = QVBoxLayout(widget_analisis)
        
        # Tabs de análisis
        tabs_analisis = QTabWidget()
        
        # Tab de análisis de comportamiento
        tab_comportamiento = QWidget()
        layout_comportamiento = QVBoxLayout(tab_comportamiento)
        
        self.tabla_comportamiento = QTableWidget()
        self.tabla_comportamiento.setColumnCount(4)
        self.tabla_comportamiento.setHorizontalHeaderLabels([
            "Patrón", "Frecuencia", "Riesgo", "Acción Recomendada"
        ])
        layout_comportamiento.addWidget(self.tabla_comportamiento)
        
        tabs_analisis.addTab(tab_comportamiento, "📊 Análisis de Comportamiento")
        
        # Tab de línea de tiempo
        tab_timeline = QWidget()
        layout_timeline = QVBoxLayout(tab_timeline)
        
        self.lista_timeline = QListWidget()
        layout_timeline.addWidget(self.lista_timeline)
        
        tabs_analisis.addTab(tab_timeline, "⏰ Línea de Tiempo")
        
        # Tab de análisis de red
        tab_red = QWidget()
        layout_red = QVBoxLayout(tab_red)
        
        self.tabla_conexiones = QTableWidget()
        self.tabla_conexiones.setColumnCount(5)
        self.tabla_conexiones.setHorizontalHeaderLabels([
            "IP Origen", "IP Destino", "Puerto", "Protocolo", "Estado"
        ])
        layout_red.addWidget(self.tabla_conexiones)
        
        tabs_analisis.addTab(tab_red, "🌐 Análisis de Red")
        
        layout.addWidget(tabs_analisis)
        
        parent.addWidget(widget_analisis)
        
    def _crear_tab_reglas_alertas(self, tabs):
        """Crea el tab de reglas y alertas"""
        tab_reglas = QWidget()
        layout = QVBoxLayout(tab_reglas)
        
        # Splitter para reglas y configuración
        splitter_reglas = QSplitter(Qt.Orientation.Vertical)
        
        # Panel superior - Reglas existentes
        grupo_reglas_existentes = QGroupBox("📋 Reglas de Detección Activas")
        layout_reglas_existentes = QVBoxLayout(grupo_reglas_existentes)
        
        self.tabla_reglas = QTableWidget()
        self.tabla_reglas.setColumnCount(5)
        self.tabla_reglas.setHorizontalHeaderLabels([
            "Nombre", "Tipo", "Severidad", "Estado", "Activaciones"
        ])
        
        # Poblar con reglas predefinidas
        self._cargar_reglas_predefinidas()
        
        layout_reglas_existentes.addWidget(self.tabla_reglas)
        
        # Botones para reglas
        layout_botones_reglas = QHBoxLayout()
        btn_nueva_regla = QPushButton("➕ Nueva Regla")
        btn_editar_regla = QPushButton("✏️ Editar")
        btn_eliminar_regla = QPushButton("🗑️ Eliminar")
        btn_importar_reglas = QPushButton("📥 Importar")
        btn_exportar_reglas = QPushButton("📤 Exportar")
        
        layout_botones_reglas.addWidget(btn_nueva_regla)
        layout_botones_reglas.addWidget(btn_editar_regla)
        layout_botones_reglas.addWidget(btn_eliminar_regla)
        layout_botones_reglas.addWidget(btn_importar_reglas)
        layout_botones_reglas.addWidget(btn_exportar_reglas)
        layout_botones_reglas.addStretch()
        
        layout_reglas_existentes.addLayout(layout_botones_reglas)
        splitter_reglas.addWidget(grupo_reglas_existentes)
        
        # Panel inferior - Configuración de alertas
        grupo_config_alertas = QGroupBox("🔔 Configuración de Alertas")
        layout_config_alertas = QFormLayout(grupo_config_alertas)
        
        self.check_alertas_email = QCheckBox("Enviar alertas por email")
        self.check_alertas_syslog = QCheckBox("Enviar a syslog")
        self.check_alertas_webhook = QCheckBox("Webhook personalizado")
        
        self.input_email_destino = QLineEdit("admin@empresa.com")
        self.input_webhook_url = QLineEdit("https://webhook.ejemplo.com/alertas")
        
        self.spin_umbral_critico = QSpinBox()
        self.spin_umbral_critico.setRange(1, 100)
        self.spin_umbral_critico.setValue(5)
        
        layout_config_alertas.addRow("", self.check_alertas_email)
        layout_config_alertas.addRow("Email destino:", self.input_email_destino)
        layout_config_alertas.addRow("", self.check_alertas_syslog)
        layout_config_alertas.addRow("", self.check_alertas_webhook)
        layout_config_alertas.addRow("URL Webhook:", self.input_webhook_url)
        layout_config_alertas.addRow("Umbral para alertas críticas:", self.spin_umbral_critico)
        
        splitter_reglas.addWidget(grupo_config_alertas)
        
        splitter_reglas.setSizes([400, 200])
        layout.addWidget(splitter_reglas)
        
        tabs.addTab(tab_reglas, "⚙️ Reglas y Alertas")
        
    def _crear_tab_estadisticas_avanzadas(self, tabs):
        """Crea el tab de estadísticas avanzadas"""
        tab_estadisticas = QWidget()
        layout = QVBoxLayout(tab_estadisticas)
        
        # Grid de estadísticas
        grid_stats = QGridLayout()
        
        # Widgets de estadísticas visuales
        self._crear_widget_estadistica("📊 Eventos por Hora", "0", 0, 0, grid_stats)
        self._crear_widget_estadistica("🚨 Alertas Generadas", "0", 0, 1, grid_stats)
        self._crear_widget_estadistica("🎯 Precisión de Detección", "95%", 0, 2, grid_stats)
        self._crear_widget_estadistica("⏱️ Tiempo Promedio de Respuesta", "2.3s", 1, 0, grid_stats)
        self._crear_widget_estadistica("🔍 Falsos Positivos", "2", 1, 1, grid_stats)
        self._crear_widget_estadistica("📈 Tendencia de Amenazas", "↗️ +15%", 1, 2, grid_stats)
        
        layout.addLayout(grid_stats)
        
        # Gráficos (placeholder)
        grupo_graficos = QGroupBox("📈 Gráficos de Tendencias")
        layout_graficos = QVBoxLayout(grupo_graficos)
        
        label_graficos = QLabel("📊 Área reservada para gráficos interactivos\n(Funcionalidad en desarrollo)")
        label_graficos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_graficos.setMinimumHeight(200)
        label_graficos.setStyleSheet("border: 2px dashed #BDBDBD; background-color: #F5F5F5;")
        
        layout_graficos.addWidget(label_graficos)
        layout.addWidget(grupo_graficos)
        
        tabs.addTab(tab_estadisticas, "📊 Estadísticas Avanzadas")
        
    def _crear_tab_configuracion_siem(self, tabs):
        """Crea el tab de configuración del SIEM"""
        tab_config = QWidget()
        layout = QVBoxLayout(tab_config)
        
        # Scroll area para configuraciones
        scroll = QScrollArea()
        widget_scroll = QWidget()
        layout_scroll = QVBoxLayout(widget_scroll)
        
        # Configuración de motores
        grupo_motores = QGroupBox("⚙️ Configuración de Motores de Detección")
        layout_motores = QFormLayout(grupo_motores)
        
        self.check_motor_yara = QCheckBox("Motor YARA")
        self.check_motor_yara.setChecked(True)
        
        self.check_motor_suricata = QCheckBox("Motor Suricata")
        self.check_motor_suricata.setChecked(True)
        
        self.check_motor_custom = QCheckBox("Reglas personalizadas")
        self.check_motor_custom.setChecked(True)
        
        layout_motores.addRow("Motores activos:", self.check_motor_yara)
        layout_motores.addRow("", self.check_motor_suricata)
        layout_motores.addRow("", self.check_motor_custom)
        
        layout_scroll.addWidget(grupo_motores)
        
        # Configuración de retención de datos
        grupo_retencion = QGroupBox("💾 Retención de Datos")
        layout_retencion = QFormLayout(grupo_retencion)
        
        self.spin_dias_retencion = QSpinBox()
        self.spin_dias_retencion.setRange(1, 365)
        self.spin_dias_retencion.setValue(30)
        self.spin_dias_retencion.setSuffix(" días")
        
        self.spin_max_eventos = QSpinBox()
        self.spin_max_eventos.setRange(1000, 1000000)
        self.spin_max_eventos.setValue(10000)
        self.spin_max_eventos.setSuffix(" eventos")
        
        layout_retencion.addRow("Días de retención:", self.spin_dias_retencion)
        layout_retencion.addRow("Máximo eventos en memoria:", self.spin_max_eventos)
        
        layout_scroll.addWidget(grupo_retencion)
        
        # Configuración de rendimiento
        grupo_rendimiento = QGroupBox("🚀 Configuración de Rendimiento")
        layout_rendimiento = QFormLayout(grupo_rendimiento)
        
        self.slider_frecuencia_monitor = QSlider(Qt.Orientation.Horizontal)
        self.slider_frecuencia_monitor.setRange(1, 10)
        self.slider_frecuencia_monitor.setValue(5)
        self.label_frecuencia = QLabel("5 segundos")
        
        self.slider_hilos_procesamiento = QSlider(Qt.Orientation.Horizontal)
        self.slider_hilos_procesamiento.setRange(1, 8)
        self.slider_hilos_procesamiento.setValue(2)
        self.label_hilos = QLabel("2 hilos")
        
        layout_rendimiento.addRow("Frecuencia de monitoreo:", self.slider_frecuencia_monitor)
        layout_rendimiento.addRow("", self.label_frecuencia)
        layout_rendimiento.addRow("Hilos de procesamiento:", self.slider_hilos_procesamiento)
        layout_rendimiento.addRow("", self.label_hilos)
        
        # Conectar sliders a labels
        self.slider_frecuencia_monitor.valueChanged.connect(
            lambda v: self.label_frecuencia.setText(f"{v} segundos")
        )
        self.slider_hilos_procesamiento.valueChanged.connect(
            lambda v: self.label_hilos.setText(f"{v} hilos")
        )
        
        layout_scroll.addWidget(grupo_rendimiento)
        
        # Botones de acción
        layout_botones_config = QHBoxLayout()
        btn_guardar_config = QPushButton("💾 Guardar Configuración")
        btn_guardar_config.setProperty("esPrimario", "true")
        btn_restaurar_config = QPushButton("🔄 Restaurar por Defecto")
        btn_exportar_config = QPushButton("📤 Exportar Configuración")
        
        layout_botones_config.addWidget(btn_guardar_config)
        layout_botones_config.addWidget(btn_restaurar_config)
        layout_botones_config.addWidget(btn_exportar_config)
        layout_botones_config.addStretch()
        
        layout_scroll.addLayout(layout_botones_config)
        
        # Configurar scroll
        scroll.setWidget(widget_scroll)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        tabs.addTab(tab_config, "⚙️ Configuración SIEM")
        
    def _crear_widget_estadistica(self, titulo: str, valor: str, fila: int, columna: int, grid):
        """Crea un widget de estadística visual"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        label_titulo = QLabel(titulo)
        label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_titulo.setStyleSheet("font-weight: bold; color: #6C757D;")
        
        label_valor = QLabel(valor)
        label_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_valor.setStyleSheet("font-size: 24px; font-weight: bold; color: #007BFF;")
        
        layout.addWidget(label_titulo)
        layout.addWidget(label_valor)
        
        grid.addWidget(frame, fila, columna)
        
    def _cargar_reglas_predefinidas(self):
        """Carga reglas predefinidas en la tabla"""
        reglas_predefinidas = [
            ("Login Fallido Múltiple", "Autenticación", "HIGH", "Activa", "12"),
            ("Acceso Root No Autorizado", "Privilegios", "CRITICAL", "Activa", "3"),
            ("Tráfico Sospechoso", "Red", "WARNING", "Activa", "8"),
            ("Modificación Archivo Sistema", "Integridad", "HIGH", "Activa", "5"),
            ("Proceso Sin Firma", "Malware", "WARNING", "Activa", "15"),
            ("Conexión IP Blacklist", "Red", "CRITICAL", "Activa", "2"),
            ("Escalación Privilegios", "Privilegios", "CRITICAL", "Activa", "1"),
            ("Hash Malicioso Detectado", "Malware", "CRITICAL", "Activa", "0")
        ]
        
        self.tabla_reglas.setRowCount(len(reglas_predefinidas))
        
        for fila, (nombre, tipo, severidad, estado, activaciones) in enumerate(reglas_predefinidas):
            self.tabla_reglas.setItem(fila, 0, QTableWidgetItem(nombre))
            self.tabla_reglas.setItem(fila, 1, QTableWidgetItem(tipo))
            self.tabla_reglas.setItem(fila, 2, QTableWidgetItem(severidad))
            self.tabla_reglas.setItem(fila, 3, QTableWidgetItem(estado))
            self.tabla_reglas.setItem(fila, 4, QTableWidgetItem(activaciones))
            
    def _conectar_señales(self):
        """Conecta las señales de los componentes"""
        # Señales del monitor de eventos
        self.monitor_eventos.evento_detectado.connect(self._procesar_evento)
        self.monitor_eventos.estadisticas_actualizadas.connect(self._actualizar_estadisticas)
        self.monitor_eventos.alerta_critica.connect(self._procesar_alerta_critica)
        
    def _iniciar_monitoreo(self):
        """Inicia el monitoreo de eventos"""
        if not self.monitor_eventos.isRunning():
            self.monitor_eventos.start()
            self.logger.info("Monitor de eventos SIEM iniciado")
            
    def _procesar_evento(self, evento: Dict[str, Any]):
        """Procesa un nuevo evento detectado"""
        # Agregar a tabla si pasa los filtros
        if self._evento_pasa_filtros(evento):
            self._agregar_evento_tabla(evento)
            
        # Actualizar análisis de correlación
        self._actualizar_correlacion(evento)
        
    def _evento_pasa_filtros(self, evento: Dict[str, Any]) -> bool:
        """Verifica si el evento pasa los filtros actuales"""
        # Filtro de severidad
        filtro_severidad = self.combo_filtro_severidad.currentText()
        if filtro_severidad != "Todas las severidades" and evento["severidad"] != filtro_severidad:
            return False
            
        # Filtro de origen
        filtro_origen = self.combo_filtro_origen.currentText()
        if filtro_origen != "Todos los orígenes" and evento["origen"] != filtro_origen:
            return False
            
        return True
        
    def _agregar_evento_tabla(self, evento: Dict[str, Any]):
        """Agrega un evento a la tabla de eventos"""
        row = self.tabla_eventos.rowCount()
        self.tabla_eventos.insertRow(row)
        
        timestamp_str = evento["timestamp"].strftime("%H:%M:%S")
        
        items = [
            timestamp_str,
            evento["severidad"],
            evento["tipo"],
            evento["descripcion"],
            evento["origen"],
            evento["usuario"],
            evento["ip_origen"]
        ]
        
        for col, item_text in enumerate(items):
            item = QTableWidgetItem(str(item_text))
            
            # Colorear según severidad
            if evento["severidad"] == "CRITICAL":
                item.setBackground(QColor("#FFEBEE"))
            elif evento["severidad"] == "HIGH":
                item.setBackground(QColor("#FFF3E0"))
            elif evento["severidad"] == "WARNING":
                item.setBackground(QColor("#FFFDE7"))
                
            self.tabla_eventos.setItem(row, col, item)
            
        # Mantener máximo 1000 filas
        if self.tabla_eventos.rowCount() > 1000:
            self.tabla_eventos.removeRow(0)
            
        # Scroll automático
        self.tabla_eventos.scrollToBottom()
        
    def _actualizar_estadisticas(self, estadisticas: Dict[str, Any]):
        """Actualiza las métricas generales"""
        self.labels_metricas["total_eventos"].setText(str(estadisticas["total_eventos"]))
        self.labels_metricas["alertas_criticas"].setText(str(estadisticas["eventos_criticos"]))
        self.labels_metricas["eventos_alto_riesgo"].setText(str(estadisticas["eventos_altos"]))
        self.labels_metricas["eventos_por_hora"].setText(str(estadisticas["eventos_ultima_hora"]))
        self.labels_metricas["ultima_actualizacion"].setText(datetime.now().strftime("%H:%M:%S"))
        
        # Actualizar nivel de riesgo
        self._actualizar_nivel_riesgo(estadisticas)
        
    def _actualizar_nivel_riesgo(self, estadisticas: Dict[str, Any]):
        """Actualiza el indicador de nivel de riesgo"""
        criticos = estadisticas["eventos_criticos"]
        altos = estadisticas["eventos_altos"]
        warnings = estadisticas["eventos_warning"]
        
        # Calcular nivel de riesgo
        score_riesgo = criticos * 10 + altos * 5 + warnings * 2
        
        if score_riesgo >= 50:
            nivel = "CRÍTICO"
            color = "#DC3545"
            progreso = 100
        elif score_riesgo >= 30:
            nivel = "ALTO"
            color = "#FD7E14"
            progreso = 75
        elif score_riesgo >= 15:
            nivel = "MEDIO"
            color = "#FFC107"
            progreso = 50
        else:
            nivel = "BAJO"
            color = "#28A745"
            progreso = 25
            
        self.label_nivel_riesgo.setText(nivel)
        self.label_nivel_riesgo.setStyleSheet(f"""
            font-size: 24px; font-weight: bold; 
            color: white; background-color: {color}; 
            padding: 10px; border-radius: 8px;
        """)
        
        self.progreso_riesgo.setValue(progreso)
        
    def _procesar_alerta_critica(self, severidad: str, mensaje: str):
        """Procesa una alerta crítica"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        texto_alerta = f"[{timestamp}] {severidad}: {mensaje}"
        
        item = QListWidgetItem(texto_alerta)
        if severidad == "CRITICAL":
            item.setBackground(QColor("#FFCDD2"))
        else:
            item.setBackground(QColor("#FFE0B2"))
            
        self.lista_alertas_criticas.insertItem(0, item)
        
        # Mantener máximo 50 alertas
        if self.lista_alertas_criticas.count() > 50:
            self.lista_alertas_criticas.takeItem(self.lista_alertas_criticas.count() - 1)
            
        self.eventos_criticos.append({
            "timestamp": datetime.now(),
            "severidad": severidad,
            "mensaje": mensaje
        })
        
        self.logger.warning(f"Alerta crítica: {texto_alerta}")
        
    def _actualizar_correlacion(self, evento: Dict[str, Any]):
        """Actualiza el análisis de correlación"""
        # Análisis básico de patrones
        patrones_detectados = []
        
        # Buscar patrones de login fallidos
        if evento["tipo"] == "login_fallido":
            patrones_detectados.append("🔒 Múltiples intentos de login fallido detectados")
            
        # Buscar patrones de escalación
        if evento["tipo"] == "escalacion_privilegios":
            patrones_detectados.append("⬆️ Patrón de escalación de privilegios activo")
            
        # Buscar patrones de red
        if evento["tipo"] == "conexion_red" and "192.168.1" not in evento["ip_origen"]:
            patrones_detectados.append("🌐 Conexión desde IP externa detectada")
            
        if patrones_detectados:
            texto_actual = self.texto_correlacion.toPlainText()
            nuevo_texto = f"[{datetime.now().strftime('%H:%M:%S')}] " + "\n".join(patrones_detectados)
            
            if "Esperando eventos" in texto_actual:
                self.texto_correlacion.setPlainText(nuevo_texto)
            else:
                self.texto_correlacion.setPlainText(f"{nuevo_texto}\n\n{texto_actual}")
                
    def closeEvent(self, event):
        """Maneja el cierre del widget"""
        if self.monitor_eventos.isRunning():
            self.monitor_eventos.detener()
            self.monitor_eventos.wait()
        event.accept()
