#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ventana Principal Completa - Ares Aegis
Interfaz unificada que muestra todas las funcionalidades del antivirus y Mini-SIEM
Separación clara entre módulos, navegación intuitiva y acceso a todas las opciones
"""

import sys
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QSplitter,
    QScrollArea, QGroupBox, QProgressBar, QTextEdit, QApplication,
    QTabWidget, QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox, QCheckBox,
    QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
    QLineEdit, QSlider, QToolBar, QStatusBar, QMenuBar, QMenu
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QFont, QPixmap, QMovie, QAction

from .estilo_japones import EstiloJapones
from antivirus_kali.utilidades.logger import SiemLogger

# Importar paneles especializados
from .paneles.panel_escaneo_antivirus import PanelEscaneoAntivirus
from .paneles.panel_mini_siem import PanelMiniSiem
from .paneles.panel_herramientas_sistema import PanelHerramientasSistema

class PanelNavegacion(QWidget):
    """Panel de navegación lateral con todas las funcionalidades"""
    
    # Señales de navegación
    seccion_cambiada = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = SiemLogger(__name__)
        self.seccion_actual = None
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz del panel de navegación"""
        layout = QVBoxLayout(self)
        layout.setSpacing(EstiloJapones.ESPACIADO['mini'])
        layout.setContentsMargins(EstiloJapones.ESPACIADO['normal'], EstiloJapones.ESPACIADO['normal'],
                                 EstiloJapones.ESPACIADO['normal'], EstiloJapones.ESPACIADO['normal'])
        
        # Agregar imagen Ares en la parte superior
        imagen_ares = EstiloJapones.crear_widget_imagen_ares(self, (120, 120))
        layout.addWidget(imagen_ares)
        
        # Separador después de la imagen
        separador_imagen = QFrame()
        separador_imagen.setFrameShape(QFrame.Shape.HLine)
        separador_imagen.setProperty("esSeparador", "true")
        layout.addWidget(separador_imagen)
        
        # Logo y título
        titulo_app = QLabel("🛡️ ARES AEGIS")
        titulo_app.setAlignment(Qt.AlignmentFlag.AlignCenter)
        EstiloJapones.aplicar_fuente_personalizada(
            titulo_app, 
            EstiloJapones.TIPOGRAFIA['tamaño_titulo_principal'],
            EstiloJapones.TIPOGRAFIA['peso_negrita']
        )
        titulo_app.setProperty("estiloTituloPrincipal", "true")
        layout.addWidget(titulo_app)
        
        # Subtítulo
        subtitulo = QLabel("Sistema de Seguridad Avanzado")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setProperty("estiloSubtitulo", "true")
        layout.addWidget(subtitulo)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setProperty("esSeparador", "true")
        layout.addWidget(separador)
        
        # Sección ANTIVIRUS
        self._crear_seccion_antivirus(layout)
        
        # Separador
        separador2 = QFrame()
        separador2.setFrameShape(QFrame.Shape.HLine)
        separador2.setProperty("esSeparador", "true")
        layout.addWidget(separador2)
        
        # Sección MINI-SIEM
        self._crear_seccion_siem(layout)
        
        # Separador
        separador3 = QFrame()
        separador3.setFrameShape(QFrame.Shape.HLine)
        separador3.setProperty("esSeparador", "true")
        layout.addWidget(separador3)
        
        # Sección HERRAMIENTAS
        self._crear_seccion_herramientas(layout)
        
        # Espaciador al final
        layout.addStretch()
        
        # Botón de configuración global
        btn_configuracion = self._crear_boton_navegacion("⚙️ Configuración Global", "configuracion")
        btn_configuracion.setProperty("esConfiguracion", "true")
        layout.addWidget(btn_configuracion)
        
        # Estilo del panel
        self.setProperty("esPanelNavegacion", "true")
        self.setFixedWidth(320)  # Aumentar un poco el ancho para acomodar la imagen
        
    def _crear_seccion_antivirus(self, layout):
        """Crea la sección de antivirus en el panel de navegación"""
        # Título de sección
        titulo_antivirus = QLabel("🦠 MÓDULO ANTIVIRUS")
        titulo_antivirus.setProperty("estiloTituloSeccion", "true")
        layout.addWidget(titulo_antivirus)
        
        # Botones de antivirus
        botones_antivirus = [
            ("🏠 Panel Principal", "antivirus_principal"),
            ("🔍 Escaneo Rápido", "escaneo_rapido"),
            ("🔍 Escaneo Completo", "escaneo_completo"),
            ("🎯 Escaneo Personalizado", "escaneo_personalizado"),
            ("📊 Motor ClamAV", "motor_clamav"),
            ("🧬 Motor YARA", "motor_yara"),
            ("🔐 Verificación Hash", "verificacion_hash"),
            ("🕵️ Detección Rootkits", "deteccion_rootkits"),
            ("🗃️ Cuarentena", "cuarentena"),
            ("📈 Estadísticas", "estadisticas_antivirus"),
            ("📄 Informes", "informes_antivirus")
        ]
        
        for texto, id_seccion in botones_antivirus:
            btn = self._crear_boton_navegacion(texto, id_seccion)
            layout.addWidget(btn)
            
    def _crear_seccion_siem(self, layout):
        """Crea la sección de Mini-SIEM en el panel de navegación"""
        # Título de sección
        titulo_siem = QLabel("📊 MÓDULO MINI-SIEM")
        titulo_siem.setProperty("estiloTituloSeccion", "true")
        layout.addWidget(titulo_siem)
        
        # Botones de SIEM
        botones_siem = [
            ("🏠 Dashboard SIEM", "siem_dashboard"),
            ("🚨 Alertas en Tiempo Real", "siem_alertas"),
            ("📋 Eventos de Seguridad", "siem_eventos"),
            ("🔗 Correlación de Eventos", "siem_correlacion"),
            ("📊 Análisis de Logs", "siem_logs"),
            ("🌐 Monitor de Red", "siem_red"),
            ("👥 Actividad de Usuarios", "siem_usuarios"),
            ("🔍 Análisis Forense", "siem_forense"),
            ("⚡ Respuesta Automática", "siem_respuesta"),
            ("📈 Métricas y KPIs", "siem_metricas"),
            ("📄 Informes SIEM", "informes_siem")
        ]
        
        for texto, id_seccion in botones_siem:
            btn = self._crear_boton_navegacion(texto, id_seccion)
            layout.addWidget(btn)
            
    def _crear_seccion_herramientas(self, layout):
        """Crea la sección de herramientas en el panel de navegación"""
        # Título de sección
        titulo_herramientas = QLabel("🛠️ HERRAMIENTAS")
        titulo_herramientas.setProperty("estiloTituloSeccion", "true")
        layout.addWidget(titulo_herramientas)
        
        # Botones de herramientas
        botones_herramientas = [
            ("🔒 Verificación Integridad", "integridad"),
            ("🌐 Análisis de Red", "analisis_red"),
            ("👑 Monitor Privilegios", "privilegios"),
            ("🚩 Gestión IOCs", "gestion_iocs"),
            ("🛡️ Modo Seguro", "modo_seguro"),
            ("💻 Escaneo Sistema", "escaneo_sistema"),
            ("📊 Estado Sistema", "estado_sistema"),
            ("🔄 Actualizaciones", "actualizaciones")
        ]
        
        for texto, id_seccion in botones_herramientas:
            btn = self._crear_boton_navegacion(texto, id_seccion)
            layout.addWidget(btn)
            
    def _crear_boton_navegacion(self, texto: str, id_seccion: str) -> QPushButton:
        """Crea un botón de navegación"""
        btn = QPushButton(texto)
        btn.setProperty("esBotonNavegacion", "true")
        btn.setMinimumHeight(40)
        btn.clicked.connect(lambda: self._cambiar_seccion(id_seccion))
        
        # Alineación a la izquierda
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 15px;
            }
        """)
        
        return btn
        
    def _cambiar_seccion(self, id_seccion: str):
        """Cambia la sección activa"""
        if self.seccion_actual != id_seccion:
            self.seccion_actual = id_seccion
            self.seccion_cambiada.emit(id_seccion)
            self.logger.info(f"Navegación a sección: {id_seccion}")


class PanelEstadoGeneral(QWidget):
    """Panel que muestra el estado general del sistema"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = SiemLogger(__name__)
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz del panel"""
        layout = QVBoxLayout(self)
        layout.setSpacing(EstiloJapones.ESPACIADO['normal'])
        
        # Título
        titulo = QLabel("📊 Estado General del Sistema")
        titulo.setProperty("estiloTitulo", "true")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Grid de estados
        grid_layout = QGridLayout()
        grid_layout.setSpacing(EstiloJapones.ESPACIADO['normal'])
        
        # Crear cards de estado
        self.card_antivirus = self._crear_card_estado(
            "🛡️ Antivirus", "Activo", "Verde", "Protección en tiempo real activada"
        )
        self.card_siem = self._crear_card_estado(
            "📊 Mini-SIEM", "Monitoreando", "Verde", "Analizando eventos de seguridad"
        )
        self.card_red = self._crear_card_estado(
            "🌐 Red", "Segura", "Verde", "Sin amenazas detectadas"
        )
        self.card_sistema = self._crear_card_estado(
            "💻 Sistema", "Estable", "Verde", "Rendimiento óptimo"
        )
        
        # Añadir al grid
        grid_layout.addWidget(self.card_antivirus, 0, 0)
        grid_layout.addWidget(self.card_siem, 0, 1)
        grid_layout.addWidget(self.card_red, 1, 0)
        grid_layout.addWidget(self.card_sistema, 1, 1)
        
        layout.addLayout(grid_layout)
        
        # Panel de estadísticas rápidas
        self._crear_panel_estadisticas(layout)
        
    def _crear_card_estado(self, titulo: str, estado: str, color: str, descripcion: str) -> QGroupBox:
        """Crea una card de estado"""
        card = QGroupBox()
        card.setProperty("esCardEstado", "true")
        
        layout = QVBoxLayout(card)
        layout.setSpacing(EstiloJapones.ESPACIADO['mini'])
        
        # Título
        label_titulo = QLabel(titulo)
        label_titulo.setProperty("estiloTituloCard", "true")
        layout.addWidget(label_titulo)
        
        # Estado
        label_estado = QLabel(estado)
        label_estado.setProperty("esEstadoVerde" if color == "Verde" else "esEstadoRojo", "true")
        layout.addWidget(label_estado)
        
        # Descripción
        label_desc = QLabel(descripcion)
        label_desc.setProperty("esDescripcionCard", "true")
        label_desc.setWordWrap(True)
        layout.addWidget(label_desc)
        
        return card
        
    def _crear_panel_estadisticas(self, layout):
        """Crea el panel de estadísticas rápidas"""
        grupo_stats = QGroupBox("📈 Estadísticas Rápidas")
        grupo_stats.setProperty("esPanelEstadisticas", "true")
        
        layout_stats = QGridLayout(grupo_stats)
        layout_stats.setSpacing(EstiloJapones.ESPACIADO['normal'])
        
        # Estadísticas
        stats = [
            ("Archivos Escaneados Hoy", "1,247"),
            ("Amenazas Detectadas", "0"),
            ("Eventos SIEM", "156"),
            ("Última Actualización", "Hace 2 horas")
        ]
        
        for i, (label_text, value_text) in enumerate(stats):
            row = i // 2
            col = (i % 2) * 2
            
            label = QLabel(label_text + ":")
            label.setProperty("esLabelEstadistica", "true")
            layout_stats.addWidget(label, row, col)
            
            value = QLabel(value_text)
            value.setProperty("esValorEstadistica", "true")
            layout_stats.addWidget(value, row, col + 1)
            
        layout.addWidget(grupo_stats)


class PanelAccionesRapidas(QWidget):
    """Panel con acciones rápidas principales"""
    
    # Señales
    accion_solicitada = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = SiemLogger(__name__)
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz del panel"""
        layout = QVBoxLayout(self)
        layout.setSpacing(EstiloJapones.ESPACIADO['normal'])
        
        # Título
        titulo = QLabel("⚡ Acciones Rápidas")
        titulo.setProperty("estiloTitulo", "true")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Grid de acciones
        grid_layout = QGridLayout()
        grid_layout.setSpacing(EstiloJapones.ESPACIADO['normal'])
        
        # Botones de acción rápida
        acciones = [
            ("🔍 Escaneo Rápido", "escaneo_rapido", True),
            ("🚨 Ver Alertas", "ver_alertas", False),
            ("🔄 Actualizar", "actualizar", False),
            ("📊 Ver Dashboard", "dashboard", False),
            ("🛡️ Modo Seguro", "modo_seguro", False),
            ("📈 Estadísticas", "estadisticas", False)
        ]
        
        for i, (texto, accion, es_primario) in enumerate(acciones):
            btn = QPushButton(texto)
            btn.setMinimumHeight(50)
            
            if es_primario:
                btn.setProperty("esPrimario", "true")
            else:
                btn.setProperty("esSecundario", "true")
                
            btn.clicked.connect(lambda checked, a=accion: self.accion_solicitada.emit(a))
            
            row = i // 2
            col = i % 2
            grid_layout.addWidget(btn, row, col)
            
        layout.addLayout(grid_layout)


class ContenedorPrincipal(QWidget):
    """Contenedor principal que maneja las diferentes secciones"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = SiemLogger(__name__)
        self.secciones = {}
        self._setup_ui()
        self._crear_secciones()
        
    def _setup_ui(self):
        """Configura la interfaz del contenedor"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Stack widget para cambiar entre secciones
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
    def _crear_secciones(self):
        """Crea todas las secciones disponibles"""
        # Sección principal (dashboard)
        self._crear_seccion_principal()
        
        # Secciones de antivirus
        self._crear_secciones_antivirus()
        
        # Secciones de SIEM
        self._crear_secciones_siem()
        
        # Secciones de herramientas
        self._crear_secciones_herramientas()
        
    def _crear_seccion_principal(self):
        """Crea la sección principal/dashboard"""
        seccion = QWidget()
        layout = QVBoxLayout(seccion)
        
        # Scroll area para el contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        contenido = QWidget()
        layout_contenido = QVBoxLayout(contenido)
        
        # Panel de estado general
        panel_estado = PanelEstadoGeneral()
        layout_contenido.addWidget(panel_estado)
        
        # Panel de acciones rápidas
        panel_acciones = PanelAccionesRapidas()
        layout_contenido.addWidget(panel_acciones)
        
        scroll.setWidget(contenido)
        layout.addWidget(scroll)
        
        self.secciones["principal"] = seccion
        self.stack.addWidget(seccion)
        
    def _crear_secciones_antivirus(self):
        """Crea las secciones del módulo antivirus"""
        secciones_antivirus = [
            "antivirus_principal", "escaneo_rapido", "escaneo_completo", 
            "escaneo_personalizado", "motor_clamav", "motor_yara",
            "verificacion_hash", "deteccion_rootkits", "cuarentena",
            "estadisticas_antivirus", "informes_antivirus"
        ]
        
        for id_seccion in secciones_antivirus:
            seccion = self._crear_seccion_generica(id_seccion)
            self.secciones[id_seccion] = seccion
            self.stack.addWidget(seccion)
            
    def _crear_secciones_siem(self):
        """Crea las secciones del módulo Mini-SIEM"""
        secciones_siem = [
            "siem_dashboard", "siem_alertas", "siem_eventos",
            "siem_correlacion", "siem_logs", "siem_red",
            "siem_usuarios", "siem_forense", "siem_respuesta",
            "siem_metricas", "informes_siem"
        ]
        
        for id_seccion in secciones_siem:
            seccion = self._crear_seccion_generica(id_seccion)
            self.secciones[id_seccion] = seccion
            self.stack.addWidget(seccion)
            
    def _crear_secciones_herramientas(self):
        """Crea las secciones de herramientas"""
        secciones_herramientas = [
            "integridad", "analisis_red", "privilegios",
            "gestion_iocs", "modo_seguro", "escaneo_sistema",
            "estado_sistema", "actualizaciones", "configuracion"
        ]
        
        for id_seccion in secciones_herramientas:
            seccion = self._crear_seccion_generica(id_seccion)
            self.secciones[id_seccion] = seccion
            self.stack.addWidget(seccion)
            
    def _crear_seccion_generica(self, id_seccion: str) -> QWidget:
        """Crea una sección genérica basada en el ID"""
        seccion = QWidget()
        layout = QVBoxLayout(seccion)
        
        # Título de la sección
        titulo = self._obtener_titulo_seccion(id_seccion)
        label_titulo = QLabel(titulo)
        label_titulo.setProperty("estiloTitulo", "true")
        label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_titulo)
        
        # Contenido específico de la sección
        contenido = self._crear_contenido_seccion(id_seccion)
        layout.addWidget(contenido)
        
        return seccion
        
    def _obtener_titulo_seccion(self, id_seccion: str) -> str:
        """Obtiene el título de una sección"""
        titulos = {
            # Antivirus
            "antivirus_principal": "🦠 Panel Principal - Módulo Antivirus",
            "escaneo_rapido": "🔍 Escaneo Rápido",
            "escaneo_completo": "🔍 Escaneo Completo del Sistema",
            "escaneo_personalizado": "🎯 Escaneo Personalizado",
            "motor_clamav": "📊 Motor ClamAV",
            "motor_yara": "🧬 Motor YARA",
            "verificacion_hash": "🔐 Verificación de Hash",
            "deteccion_rootkits": "🕵️ Detección de Rootkits",
            "cuarentena": "🗃️ Gestión de Cuarentena",
            "estadisticas_antivirus": "📈 Estadísticas del Antivirus",
            "informes_antivirus": "📄 Informes del Antivirus",
            
            # SIEM
            "siem_dashboard": "📊 Dashboard Mini-SIEM",
            "siem_alertas": "🚨 Alertas en Tiempo Real",
            "siem_eventos": "📋 Eventos de Seguridad",
            "siem_correlacion": "🔗 Correlación de Eventos",
            "siem_logs": "📊 Análisis de Logs",
            "siem_red": "🌐 Monitor de Red SIEM",
            "siem_usuarios": "👥 Actividad de Usuarios",
            "siem_forense": "🔍 Análisis Forense",
            "siem_respuesta": "⚡ Respuesta Automática",
            "siem_metricas": "📈 Métricas y KPIs",
            "informes_siem": "📄 Informes SIEM",
            
            # Herramientas
            "integridad": "🔒 Verificación de Integridad",
            "analisis_red": "🌐 Análisis de Red",
            "privilegios": "👑 Monitor de Privilegios",
            "gestion_iocs": "🚩 Gestión de IOCs",
            "modo_seguro": "🛡️ Modo Seguro",
            "escaneo_sistema": "💻 Escaneo del Sistema",
            "estado_sistema": "📊 Estado del Sistema",
            "actualizaciones": "🔄 Actualizaciones",
            "configuracion": "⚙️ Configuración Global"
        }
        
        return titulos.get(id_seccion, f"📋 {id_seccion.replace('_', ' ').title()}")
        
    def _crear_contenido_seccion(self, id_seccion: str) -> QWidget:
        """Crea el contenido específico de cada sección"""
        # Usar paneles especializados para secciones principales
        if id_seccion in ["antivirus_principal", "escaneo_rapido", "escaneo_completo", "escaneo_personalizado"]:
            return PanelEscaneoAntivirus()
        elif id_seccion in ["siem_dashboard", "siem_alertas", "siem_eventos"]:
            return PanelMiniSiem()
        elif id_seccion in ["herramientas_sistema", "analisis_red", "optimizacion"]:
            return PanelHerramientasSistema()
        
        # Para otras secciones, usar contenido genérico
        contenido = QScrollArea()
        contenido.setWidgetResizable(True)
        contenido.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        widget_contenido = QWidget()
        layout = QVBoxLayout(widget_contenido)
        
        # Crear contenido específico según la sección
        if id_seccion.startswith("antivirus_") or id_seccion in ["motor_clamav", "motor_yara"]:
            self._crear_contenido_antivirus(layout, id_seccion)
        elif id_seccion.startswith("siem_"):
            self._crear_contenido_siem(layout, id_seccion)
        elif id_seccion.startswith("motor_"):
            self._crear_contenido_motor(layout, id_seccion)
        else:
            self._crear_contenido_herramienta(layout, id_seccion)
            
        contenido.setWidget(widget_contenido)
        return contenido
        
    def _crear_contenido_antivirus(self, layout, id_seccion: str):
        """Crea contenido específico para secciones de antivirus"""
        if id_seccion == "antivirus_principal":
            # Panel principal del antivirus
            layout.addWidget(QLabel("🛡️ Estado de Protección: ACTIVO"))
            layout.addWidget(QLabel("📅 Última actualización: " + datetime.now().strftime("%Y-%m-%d %H:%M")))
            
            # Botones de acción
            btn_escaneo = QPushButton("🔍 Iniciar Escaneo Rápido")
            btn_escaneo.setProperty("esPrimario", "true")
            layout.addWidget(btn_escaneo)
            
            btn_config = QPushButton("⚙️ Configurar Protección")
            layout.addWidget(btn_config)
            
        elif "escaneo" in id_seccion:
            # Controles de escaneo
            grupo_config = QGroupBox("⚙️ Configuración de Escaneo")
            layout_config = QFormLayout(grupo_config)
            
            layout_config.addRow("Directorio objetivo:", QLineEdit("/home"))
            layout_config.addRow("Profundidad máxima:", QSpinBox())
            layout_config.addRow("Incluir archivos ocultos:", QCheckBox())
            layout_config.addRow("Usar cache:", QCheckBox())
            
            layout.addWidget(grupo_config)
            
            # Botón de inicio
            btn_iniciar = QPushButton(f"🚀 Iniciar {id_seccion.replace('_', ' ').title()}")
            btn_iniciar.setProperty("esPrimario", "true")
            btn_iniciar.setMinimumHeight(50)
            layout.addWidget(btn_iniciar)
            
        # Área de resultados común
        grupo_resultados = QGroupBox("📊 Resultados")
        layout_resultados = QVBoxLayout(grupo_resultados)
        
        tabla_resultados = QTableWidget(0, 4)
        tabla_resultados.setHorizontalHeaderLabels(["Archivo", "Estado", "Amenaza", "Acción"])
        layout_resultados.addWidget(tabla_resultados)
        
        layout.addWidget(grupo_resultados)
        
    def _crear_contenido_siem(self, layout, id_seccion: str):
        """Crea contenido específico para secciones de SIEM"""
        if id_seccion == "siem_dashboard":
            # Dashboard principal del SIEM
            grid_layout = QGridLayout()
            
            # Métricas principales
            metricas = [
                ("📊 Eventos Hoy", "1,247"),
                ("🚨 Alertas Activas", "3"),
                ("⚠️ Incidentes Críticos", "0"),
                ("🌐 Conexiones Monitoreadas", "156")
            ]
            
            for i, (titulo, valor) in enumerate(metricas):
                card = QGroupBox(titulo)
                card_layout = QVBoxLayout(card)
                label_valor = QLabel(valor)
                label_valor.setProperty("esValorMetrica", "true")
                label_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
                card_layout.addWidget(label_valor)
                
                row = i // 2
                col = i % 2
                grid_layout.addWidget(card, row, col)
                
            layout.addLayout(grid_layout)
            
        elif id_seccion == "siem_alertas":
            # Lista de alertas
            lista_alertas = QListWidget()
            
            # Alertas de ejemplo
            alertas_ejemplo = [
                "🔴 CRÍTICO: Intento de acceso no autorizado detectado",
                "🟡 ADVERTENCIA: Tráfico anómalo en puerto 443",
                "🟢 INFO: Actualización de base de datos completada",
                "🟡 ADVERTENCIA: Múltiples intentos de login fallidos"
            ]
            
            for alerta in alertas_ejemplo:
                item = QListWidgetItem(alerta)
                lista_alertas.addItem(item)
                
            layout.addWidget(lista_alertas)
            
        elif id_seccion == "siem_eventos":
            # Tabla de eventos
            tabla_eventos = QTableWidget(0, 6)
            tabla_eventos.setHorizontalHeaderLabels([
                "Timestamp", "Severidad", "Fuente", "Evento", "IP", "Usuario"
            ])
            layout.addWidget(tabla_eventos)
            
        # Controles comunes
        grupo_controles = QGroupBox("🎛️ Controles")
        layout_controles = QHBoxLayout(grupo_controles)
        
        layout_controles.addWidget(QPushButton("▶️ Iniciar Monitoreo"))
        layout_controles.addWidget(QPushButton("⏸️ Pausar"))
        layout_controles.addWidget(QPushButton("🔄 Actualizar"))
        layout_controles.addWidget(QPushButton("📊 Exportar"))
        
        layout.addWidget(grupo_controles)
        
    def _crear_contenido_motor(self, layout, id_seccion: str):
        """Crea contenido específico para motores de escaneo"""
        # Estado del motor
        grupo_estado = QGroupBox(f"📊 Estado del {id_seccion.replace('motor_', '').upper()}")
        layout_estado = QFormLayout(grupo_estado)
        
        layout_estado.addRow("Estado:", QLabel("✅ Activo"))
        layout_estado.addRow("Versión:", QLabel("1.0.0"))
        layout_estado.addRow("Última actualización:", QLabel("Hace 2 horas"))
        layout_estado.addRow("Reglas cargadas:", QLabel("15,234"))
        
        layout.addWidget(grupo_estado)
        
        # Configuración del motor
        grupo_config = QGroupBox("⚙️ Configuración")
        layout_config = QFormLayout(grupo_config)
        
        layout_config.addRow("Nivel de sensibilidad:", QSlider(Qt.Orientation.Horizontal))
        layout_config.addRow("Usar cache:", QCheckBox())
        layout_config.addRow("Timeout (seg):", QSpinBox())
        
        layout.addWidget(grupo_config)
        
        # Botones de acción
        grupo_acciones = QGroupBox("🎬 Acciones")
        layout_acciones = QHBoxLayout(grupo_acciones)
        
        layout_acciones.addWidget(QPushButton("🔄 Actualizar Reglas"))
        layout_acciones.addWidget(QPushButton("🧪 Probar Motor"))
        layout_acciones.addWidget(QPushButton("📊 Ver Estadísticas"))
        
        layout.addWidget(grupo_acciones)
        
    def _crear_contenido_herramienta(self, layout, id_seccion: str):
        """Crea contenido específico para herramientas del sistema"""
        # Descripción de la herramienta
        descripciones = {
            "integridad": "Verifica la integridad de archivos críticos del sistema",
            "analisis_red": "Analiza el tráfico de red y detecta anomalías",
            "privilegios": "Monitorea procesos con privilegios elevados",
            "gestion_iocs": "Gestiona indicadores de compromiso (IOCs)",
            "modo_seguro": "Activa el modo de seguridad para pentesting",
            "escaneo_sistema": "Escanea el sistema operativo en busca de amenazas",
            "estado_sistema": "Muestra el estado general del sistema",
            "actualizaciones": "Gestiona las actualizaciones del sistema",
            "configuracion": "Configuración global de la aplicación"
        }
        
        desc = descripciones.get(id_seccion, "Herramienta del sistema")
        label_desc = QLabel(f"📋 {desc}")
        label_desc.setWordWrap(True)
        layout.addWidget(label_desc)
        
        # Controles específicos
        grupo_controles = QGroupBox("🎛️ Controles")
        layout_controles = QVBoxLayout(grupo_controles)
        
        if id_seccion == "configuracion":
            # Panel de configuración global
            tabs_config = QTabWidget()
            
            # Tab General
            tab_general = QWidget()
            layout_general = QFormLayout(tab_general)
            layout_general.addRow("Idioma:", QComboBox())
            layout_general.addRow("Tema:", QComboBox())
            layout_general.addRow("Notificaciones:", QCheckBox())
            tabs_config.addTab(tab_general, "General")
            
            # Tab Antivirus
            tab_antivirus = QWidget()
            layout_antivirus = QFormLayout(tab_antivirus)
            layout_antivirus.addRow("Protección en tiempo real:", QCheckBox())
            layout_antivirus.addRow("Escaneo automático:", QCheckBox())
            layout_antivirus.addRow("Cuarentena automática:", QCheckBox())
            tabs_config.addTab(tab_antivirus, "Antivirus")
            
            # Tab SIEM
            tab_siem = QWidget()
            layout_siem = QFormLayout(tab_siem)
            layout_siem.addRow("Monitoreo activo:", QCheckBox())
            layout_siem.addRow("Retención de logs (días):", QSpinBox())
            layout_siem.addRow("Alertas de escritorio:", QCheckBox())
            tabs_config.addTab(tab_siem, "SIEM")
            
            layout_controles.addWidget(tabs_config)
        else:
            # Botón de ejecutar genérico
            btn_ejecutar = QPushButton(f"🚀 Ejecutar {id_seccion.replace('_', ' ').title()}")
            btn_ejecutar.setProperty("esPrimario", "true")
            btn_ejecutar.setMinimumHeight(50)
            layout_controles.addWidget(btn_ejecutar)
            
        layout.addWidget(grupo_controles)
        
        # Área de resultados
        grupo_resultados = QGroupBox("📊 Resultados")
        layout_resultados = QVBoxLayout(grupo_resultados)
        
        text_resultados = QTextEdit()
        text_resultados.setPlainText("Los resultados aparecerán aquí...")
        text_resultados.setMaximumHeight(200)
        layout_resultados.addWidget(text_resultados)
        
        layout.addWidget(grupo_resultados)
        
    def cambiar_seccion(self, id_seccion: str):
        """Cambia a la sección especificada"""
        if id_seccion == "principal" or id_seccion not in self.secciones:
            self.stack.setCurrentIndex(0)  # Sección principal
        else:
            seccion_widget = self.secciones[id_seccion]
            self.stack.setCurrentWidget(seccion_widget)
            
        self.logger.info(f"Cambio a sección: {id_seccion}")


class VentanaPrincipalCompleta(QMainWindow):
    """
    Ventana principal completa que muestra todas las funcionalidades
    de Ares Aegis con separación clara entre Antivirus y Mini-SIEM
    """
    
    def __init__(self):
        super().__init__()
        self.logger = SiemLogger(__name__)
        self._setup_ui()
        self._aplicar_estilos()
        self._conectar_señales()
        self.logger.info("Ventana principal completa inicializada")
        
    def _setup_ui(self):
        """Configura la interfaz principal"""
        # Configuración de la ventana
        self.setWindowTitle("🛡️ Ares Aegis - Sistema de Seguridad Avanzado")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout_principal.addWidget(splitter)
        
        # Panel de navegación (izquierda)
        self.panel_navegacion = PanelNavegacion()
        splitter.addWidget(self.panel_navegacion)
        
        # Contenedor principal (derecha)
        self.contenedor_principal = ContenedorPrincipal()
        splitter.addWidget(self.contenedor_principal)
        
        # Configurar proporciones del splitter
        splitter.setSizes([280, 1120])
        splitter.setCollapsible(0, False)  # No permitir colapsar navegación
        
        # Configurar barra de menú
        self._setup_menu_bar()
        
        # Configurar barra de herramientas
        self._setup_toolbar()
        
        # Configurar barra de estado
        self._setup_status_bar()
        
    def _setup_menu_bar(self):
        """Configura la barra de menú"""
        menubar = self.menuBar()
        
        # Menú Archivo
        menu_archivo = menubar.addMenu("📁 Archivo")
        menu_archivo.addAction("🔍 Nuevo Escaneo", self._nuevo_escaneo)
        menu_archivo.addAction("📄 Abrir Informe", self._abrir_informe)
        menu_archivo.addSeparator()
        menu_archivo.addAction("🚪 Salir", self.close)
        
        # Menú Antivirus
        menu_antivirus = menubar.addMenu("🦠 Antivirus")
        menu_antivirus.addAction("🔍 Escaneo Rápido", self._escaneo_rapido)
        menu_antivirus.addAction("🔍 Escaneo Completo", self._escaneo_completo)
        menu_antivirus.addAction("🗃️ Ver Cuarentena", self._ver_cuarentena)
        menu_antivirus.addAction("🔄 Actualizar Definiciones", self._actualizar_definiciones)
        
        # Menú SIEM
        menu_siem = menubar.addMenu("📊 SIEM")
        menu_siem.addAction("📊 Dashboard", self._siem_dashboard)
        menu_siem.addAction("🚨 Ver Alertas", self._ver_alertas)
        menu_siem.addAction("📋 Eventos", self._ver_eventos)
        menu_siem.addAction("📈 Métricas", self._ver_metricas)
        
        # Menú Herramientas
        menu_herramientas = menubar.addMenu("🛠️ Herramientas")
        menu_herramientas.addAction("🔒 Verificar Integridad", self._verificar_integridad)
        menu_herramientas.addAction("🌐 Análisis de Red", self._analisis_red)
        menu_herramientas.addAction("👑 Monitor Privilegios", self._monitor_privilegios)
        menu_herramientas.addAction("🛡️ Modo Seguro", self._modo_seguro)
        
        # Menú Ayuda
        menu_ayuda = menubar.addMenu("❓ Ayuda")
        menu_ayuda.addAction("📖 Manual de Usuario", self._manual_usuario)
        menu_ayuda.addAction("🆘 Soporte Técnico", self._soporte_tecnico)
        menu_ayuda.addAction("ℹ️ Acerca de", self._acerca_de)
        
    def _setup_toolbar(self):
        """Configura la barra de herramientas"""
        toolbar = QToolBar("Herramientas Principales")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        
        # Acciones principales
        toolbar.addAction("🔍", self._escaneo_rapido).setToolTip("Escaneo Rápido")
        toolbar.addAction("🛡️", self._proteccion_tiempo_real).setToolTip("Protección Tiempo Real")
        toolbar.addAction("📊", self._siem_dashboard).setToolTip("Dashboard SIEM")
        toolbar.addAction("🚨", self._ver_alertas).setToolTip("Ver Alertas")
        toolbar.addSeparator()
        toolbar.addAction("🔄", self._actualizar_todo).setToolTip("Actualizar Todo")
        toolbar.addAction("⚙️", self._configuracion).setToolTip("Configuración")
        
    def _setup_status_bar(self):
        """Configura la barra de estado"""
        status_bar = self.statusBar()
        status_bar.showMessage("🛡️ Ares Aegis iniciado correctamente - Sistema protegido")
        
        # Widgets adicionales en la barra de estado
        self.label_estado_av = QLabel("🟢 Antivirus: Activo")
        self.label_estado_siem = QLabel("🟢 SIEM: Monitoreando")
        self.label_ultima_act = QLabel(f"🕐 Actualizado: {datetime.now().strftime('%H:%M')}")
        
        status_bar.addPermanentWidget(self.label_estado_av)
        status_bar.addPermanentWidget(self.label_estado_siem)
        status_bar.addPermanentWidget(self.label_ultima_act)
        
    def _aplicar_estilos(self):
        """Aplica los estilos japoneses a la ventana"""
        # Aplicar estilo completo
        self.setStyleSheet(EstiloJapones.obtener_stylesheet_completo())
        
        # Configurar fuente principal
        EstiloJapones.aplicar_fuente_personalizada(self)
        
    def _conectar_señales(self):
        """Conecta las señales de los componentes"""
        # Señal de navegación
        self.panel_navegacion.seccion_cambiada.connect(
            self.contenedor_principal.cambiar_seccion
        )
        
    # Métodos de menú y toolbar
    def _nuevo_escaneo(self):
        self.panel_navegacion.seccion_cambiada.emit("escaneo_personalizado")
        
    def _abrir_informe(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Abrir Informe", "", "Archivos PDF (*.pdf);;Todos los archivos (*)"
        )
        if archivo:
            self.logger.info(f"Abriendo informe: {archivo}")
            
    def _escaneo_rapido(self):
        self.panel_navegacion.seccion_cambiada.emit("escaneo_rapido")
        
    def _escaneo_completo(self):
        self.panel_navegacion.seccion_cambiada.emit("escaneo_completo")
        
    def _ver_cuarentena(self):
        self.panel_navegacion.seccion_cambiada.emit("cuarentena")
        
    def _actualizar_definiciones(self):
        self.panel_navegacion.seccion_cambiada.emit("actualizaciones")
        
    def _siem_dashboard(self):
        self.panel_navegacion.seccion_cambiada.emit("siem_dashboard")
        
    def _ver_alertas(self):
        self.panel_navegacion.seccion_cambiada.emit("siem_alertas")
        
    def _ver_eventos(self):
        self.panel_navegacion.seccion_cambiada.emit("siem_eventos")
        
    def _ver_metricas(self):
        self.panel_navegacion.seccion_cambiada.emit("siem_metricas")
        
    def _verificar_integridad(self):
        self.panel_navegacion.seccion_cambiada.emit("integridad")
        
    def _analisis_red(self):
        self.panel_navegacion.seccion_cambiada.emit("analisis_red")
        
    def _monitor_privilegios(self):
        self.panel_navegacion.seccion_cambiada.emit("privilegios")
        
    def _modo_seguro(self):
        self.panel_navegacion.seccion_cambiada.emit("modo_seguro")
        
    def _proteccion_tiempo_real(self):
        self.panel_navegacion.seccion_cambiada.emit("antivirus_principal")
        
    def _actualizar_todo(self):
        self.statusBar().showMessage("🔄 Actualizando sistema...")
        QTimer.singleShot(2000, lambda: self.statusBar().showMessage("✅ Sistema actualizado"))
        
    def _configuracion(self):
        self.panel_navegacion.seccion_cambiada.emit("configuracion")
        
    def _manual_usuario(self):
        QMessageBox.information(self, "Manual de Usuario", 
                              "📖 El manual de usuario se abrirá en el navegador web.")
        
    def _soporte_tecnico(self):
        QMessageBox.information(self, "Soporte Técnico", 
                              "🆘 Para soporte técnico, contacte a: soporte@ares-aegis.com")
        
    def _acerca_de(self):
        QMessageBox.about(self, "Acerca de Ares Aegis", 
                         """
🛡️ <b>Ares Aegis</b><br>
Sistema de Seguridad Avanzado con Mini-SIEM<br><br>
<b>Versión:</b> 2.0<br>
<b>Desarrollado por:</b> Equipo Ares Aegis<br>
<b>Licencia:</b> MIT<br><br>
Sistema completo de protección antivirus y monitoreo de seguridad
con capacidades SIEM integradas.
                         """)
        
    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        respuesta = QMessageBox.question(
            self, "Confirmar Salida",
            "¿Está seguro de que desea salir de Ares Aegis?\n\n"
            "Esto desactivará la protección en tiempo real.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.logger.info("Cerrando aplicación")
            event.accept()
        else:
            event.ignore()


# Función para lanzar la interfaz completa
def main():
    """Función principal para probar la interfaz completa"""
    app = QApplication(sys.argv)
    
    # Configurar aplicación
    app.setApplicationName("Ares Aegis")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Ares Aegis Security")
    
    # Crear y mostrar ventana
    ventana = VentanaPrincipalCompleta()
    ventana.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
