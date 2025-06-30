#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ventana Principal Minimalista - Estilo Japonés
Una interfaz limpia, elegante y funcional para Ares-Aegis
"""

import sys
import asyncio
from typing import Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QSplitter,
    QScrollArea, QGroupBox, QProgressBar, QTextEdit, QApplication
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QSize
from PySide6.QtGui import QIcon, QFont, QPixmap, QMovie

from .estilo_japones import EstiloJapones
from antivirus_kali.utilidades.logger import SiemLogger

class ComponenteEstado(QWidget):
    """Componente para mostrar estado del sistema de forma minimalista"""
    
    def __init__(self, titulo: str, valor: str = "Inicializando...", parent=None):
        super().__init__(parent)
        self.logger = SiemLogger(__name__)
        self._setup_ui(titulo, valor)
        
    def _setup_ui(self, titulo: str, valor: str):
        """Configura la interfaz del componente"""
        layout = QVBoxLayout(self)
        layout.setSpacing(EstiloJapones.ESPACIADO['mini'])
        layout.setContentsMargins(
            EstiloJapones.ESPACIADO['normal'], 
            EstiloJapones.ESPACIADO['pequeño'],
            EstiloJapones.ESPACIADO['normal'], 
            EstiloJapones.ESPACIADO['pequeño']
        )
        
        # Título
        self.label_titulo = QLabel(titulo)
        self.label_titulo.setProperty("estiloSubtitulo", "true")
        layout.addWidget(self.label_titulo)
        
        # Valor
        self.label_valor = QLabel(valor)
        EstiloJapones.aplicar_fuente_personalizada(
            self.label_valor, 
            EstiloJapones.TIPOGRAFIA['tamaño_titulo_seccion'],
            EstiloJapones.TIPOGRAFIA['peso_medio']
        )
        layout.addWidget(self.label_valor)
        
        # Estilo del contenedor
        self.setProperty("esPanelPrincipal", "true")
        EstiloJapones.aplicar_sombra_sutil(self)
        
    def actualizar_valor(self, nuevo_valor: str, color: Optional[str] = None):
        """Actualiza el valor mostrado"""
        self.label_valor.setText(nuevo_valor)
        if color:
            self.label_valor.setStyleSheet(f"color: {color};")


class PanelAccionRapida(QWidget):
    """Panel con acciones rápidas principales"""
    
    # Señales
    escaneo_rapido_solicitado = Signal()
    escaneo_completo_solicitado = Signal()
    actualizacion_solicitada = Signal()
    configuracion_solicitada = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = SiemLogger(__name__)
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz del panel"""
        layout = QGridLayout(self)
        layout.setSpacing(EstiloJapones.ESPACIADO['normal'])
        layout.setContentsMargins(EstiloJapones.ESPACIADO['normal'], EstiloJapones.ESPACIADO['normal'], 
                                 EstiloJapones.ESPACIADO['normal'], EstiloJapones.ESPACIADO['normal'])
        
        # Título del panel
        titulo = QLabel("Acciones Principales")
        titulo.setProperty("estiloTitulo", "true")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo, 0, 0, 1, 2)
        
        # Botón de escaneo rápido (principal)
        self.btn_escaneo_rapido = QPushButton("🔍 Escaneo Rápido")
        self.btn_escaneo_rapido.setProperty("esPrimario", "true")
        self.btn_escaneo_rapido.setMinimumHeight(60)
        EstiloJapones.aplicar_fuente_personalizada(
            self.btn_escaneo_rapido,
            EstiloJapones.TIPOGRAFIA['tamaño_titulo_seccion']
        )
        self.btn_escaneo_rapido.clicked.connect(self.escaneo_rapido_solicitado.emit)
        layout.addWidget(self.btn_escaneo_rapido, 1, 0, 1, 2)
        
        # Botones secundarios
        self.btn_escaneo_completo = QPushButton("🔍 Escaneo Completo")
        self.btn_escaneo_completo.setMinimumHeight(45)
        self.btn_escaneo_completo.clicked.connect(self.escaneo_completo_solicitado.emit)
        layout.addWidget(self.btn_escaneo_completo, 2, 0)
        
        self.btn_actualizar = QPushButton("🔄 Actualizar")
        self.btn_actualizar.setMinimumHeight(45)
        self.btn_actualizar.clicked.connect(self.actualizacion_solicitada.emit)
        layout.addWidget(self.btn_actualizar, 2, 1)
        
        self.btn_configuracion = QPushButton("⚙️ Configuración")
        self.btn_configuracion.setMinimumHeight(45)
        self.btn_configuracion.clicked.connect(self.configuracion_solicitada.emit)
        layout.addWidget(self.btn_configuracion, 3, 0, 1, 2)
        
        # Estilo del panel
        self.setProperty("esPanelPrincipal", "true")
        EstiloJapones.aplicar_sombra_sutil(self)


class PanelEstadoSistema(QWidget):
    """Panel que muestra el estado general del sistema"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = SiemLogger(__name__)
        self._setup_ui()
        self._timer_actualizacion = QTimer()
        self._timer_actualizacion.timeout.connect(self._actualizar_estados)
        self._timer_actualizacion.start(5000)  # Actualizar cada 5 segundos
        
    def _setup_ui(self):
        """Configura la interfaz del panel"""
        layout = QVBoxLayout(self)
        layout.setSpacing(EstiloJapones.ESPACIADO['normal'])
        layout.setContentsMargins(EstiloJapones.ESPACIADO['normal'], EstiloJapones.ESPACIADO['normal'],
                                 EstiloJapones.ESPACIADO['normal'], EstiloJapones.ESPACIADO['normal'])
        
        # Título
        titulo = QLabel("Estado del Sistema")
        titulo.setProperty("estiloTitulo", "true")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Grid de estados
        grid_layout = QGridLayout()
        grid_layout.setSpacing(EstiloJapones.ESPACIADO['pequeño'])
        
        # Componentes de estado
        self.estado_proteccion = ComponenteEstado("Protección", "🛡️ Activa")
        self.estado_base_datos = ComponenteEstado("Base de Datos", "📊 Actualizada")
        self.estado_sistema = ComponenteEstado("Sistema", "💚 Seguro")
        self.estado_red = ComponenteEstado("Red", "🌐 Monitoreada")
        
        # Añadir al grid
        grid_layout.addWidget(self.estado_proteccion, 0, 0)
        grid_layout.addWidget(self.estado_base_datos, 0, 1)
        grid_layout.addWidget(self.estado_sistema, 1, 0)
        grid_layout.addWidget(self.estado_red, 1, 1)
        
        layout.addLayout(grid_layout)
        
        # Barra de progreso general
        self.progreso_general = QProgressBar()
        self.progreso_general.setRange(0, 100)
        self.progreso_general.setValue(85)
        self.progreso_general.setFormat("Nivel de Seguridad: %p%")
        layout.addWidget(self.progreso_general)
        
        # Estilo del panel
        self.setProperty("esPanelPrincipal", "true")
        EstiloJapones.aplicar_sombra_sutil(self)
        
    def _actualizar_estados(self):
        """Actualiza los estados del sistema"""
        try:
            # Aquí se conectaría con los sistemas reales
            # Por ahora, simulamos estados
            import random
            
            estados_proteccion = ["🛡️ Activa", "⚠️ Alerta", "✅ Protegida"]
            estados_bd = ["📊 Actualizada", "🔄 Actualizando", "⚠️ Pendiente"]
            estados_sistema = ["💚 Seguro", "⚠️ Revisar", "🔴 Amenaza"]
            estados_red = ["🌐 Monitoreada", "📡 Analizando", "🔒 Bloqueada"]
            
            self.estado_proteccion.actualizar_valor(random.choice(estados_proteccion))
            self.estado_base_datos.actualizar_valor(random.choice(estados_bd))
            self.estado_sistema.actualizar_valor(random.choice(estados_sistema))
            self.estado_red.actualizar_valor(random.choice(estados_red))
            
            # Actualizar progreso
            nuevo_valor = random.randint(70, 100)
            self.progreso_general.setValue(nuevo_valor)
            
        except Exception as e:
            self.logger.error(f"Error actualizando estados: {e}")


class PanelActividad(QWidget):
    """Panel que muestra la actividad reciente del sistema"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = SiemLogger(__name__)
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz del panel"""
        layout = QVBoxLayout(self)
        layout.setSpacing(EstiloJapones.ESPACIADO['normal'])
        layout.setContentsMargins(EstiloJapones.ESPACIADO['normal'], EstiloJapones.ESPACIADO['normal'],
                                 EstiloJapones.ESPACIADO['normal'], EstiloJapones.ESPACIADO['normal'])
        
        # Título
        titulo = QLabel("Actividad Reciente")
        titulo.setProperty("estiloTitulo", "true")
        layout.addWidget(titulo)
        
        # Área de texto para mostrar actividad
        self.texto_actividad = QTextEdit()
        self.texto_actividad.setReadOnly(True)
        self.texto_actividad.setMaximumHeight(200)
        
        # Contenido inicial
        actividad_inicial = """
🔍 Escaneo rápido completado - Sin amenazas detectadas
🔄 Base de datos actualizada correctamente
🛡️ Sistema de protección en tiempo real activado
🌐 Monitor de red iniciado
📊 Análisis de integridad completado
        """.strip()
        
        self.texto_actividad.setPlainText(actividad_inicial)
        layout.addWidget(self.texto_actividad)
        
        # Botón para limpiar actividad
        self.btn_limpiar = QPushButton("🗑️ Limpiar Registro")
        self.btn_limpiar.clicked.connect(self._limpiar_actividad)
        layout.addWidget(self.btn_limpiar)
        
        # Estilo del panel
        self.setProperty("esPanelPrincipal", "true")
        EstiloJapones.aplicar_sombra_sutil(self)
        
    def agregar_actividad(self, mensaje: str):
        """Añade una nueva entrada de actividad"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        entrada = f"[{timestamp}] {mensaje}"
        
        self.texto_actividad.append(entrada)
        
        # Mantener solo las últimas 10 entradas
        contenido = self.texto_actividad.toPlainText()
        lineas = contenido.split('\n')
        if len(lineas) > 10:
            self.texto_actividad.setPlainText('\n'.join(lineas[-10:]))
            
    def _limpiar_actividad(self):
        """Limpia el registro de actividad"""
        self.texto_actividad.clear()
        self.agregar_actividad("📝 Registro de actividad limpiado")


class VentanaPrincipalMinimalista(QMainWindow):
    """
    Ventana principal con diseño japonés minimalista.
    Enfoque en simplicidad, funcionalidad y elegancia.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = SiemLogger(__name__)
        self._setup_ui()
        self._aplicar_estilos()
        self._conectar_señales()
        self.logger.info("Ventana principal minimalista inicializada")
        
    def _setup_ui(self):
        """Configura la interfaz principal"""
        # Configuración de la ventana
        self.setWindowTitle("Ares-Aegis - Antivirus de Seguridad")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal - horizontal con splitter
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(EstiloJapones.ESPACIADO['normal'], EstiloJapones.ESPACIADO['normal'],
                                          EstiloJapones.ESPACIADO['normal'], EstiloJapones.ESPACIADO['normal'])
        layout_principal.setSpacing(EstiloJapones.ESPACIADO['normal'])
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout_principal.addWidget(splitter)
        
        # Panel izquierdo - acciones principales
        self.panel_acciones = PanelAccionRapida()
        self.panel_acciones.setMaximumWidth(350)
        self.panel_acciones.setMinimumWidth(300)
        splitter.addWidget(self.panel_acciones)
        
        # Panel derecho - información del sistema
        widget_derecho = QWidget()
        layout_derecho = QVBoxLayout(widget_derecho)
        layout_derecho.setSpacing(EstiloJapones.ESPACIADO['normal'])
        
        # Panel de estado del sistema
        self.panel_estado = PanelEstadoSistema()
        layout_derecho.addWidget(self.panel_estado)
        
        # Panel de actividad
        self.panel_actividad = PanelActividad()
        layout_derecho.addWidget(self.panel_actividad)
        
        splitter.addWidget(widget_derecho)
        
        # Configurar proporciones del splitter
        splitter.setSizes([350, 650])
        
        # Barra de estado minimalista
        self._setup_barra_estado()
        
    def _setup_barra_estado(self):
        """Configura la barra de estado"""
        barra_estado = self.statusBar()
        barra_estado.showMessage("Ares-Aegis iniciado correctamente")
        
        # Estilo de la barra de estado
        barra_estado.setStyleSheet(f"""
        QStatusBar {{
            background-color: {EstiloJapones.COLORES['fondo_secundario']};
            border-top: 1px solid {EstiloJapones.COLORES['borde_sutil']};
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_texto_pequeño']}px;
            color: {EstiloJapones.COLORES['texto_secundario']};
        }}
        """)
        
    def _aplicar_estilos(self):
        """Aplica los estilos japoneses a la ventana"""
        # Aplicar estilo completo
        self.setStyleSheet(EstiloJapones.obtener_stylesheet_completo())
        
        # Configurar fuente principal
        EstiloJapones.aplicar_fuente_personalizada(self)
        
    def _conectar_señales(self):
        """Conecta las señales de los componentes"""
        # Señales del panel de acciones
        self.panel_acciones.escaneo_rapido_solicitado.connect(self._ejecutar_escaneo_rapido)
        self.panel_acciones.escaneo_completo_solicitado.connect(self._ejecutar_escaneo_completo)
        self.panel_acciones.actualizacion_solicitada.connect(self._ejecutar_actualizacion)
        self.panel_acciones.configuracion_solicitada.connect(self._abrir_configuracion)
        
    def _ejecutar_escaneo_rapido(self):
        """Ejecuta un escaneo rápido"""
        self.logger.info("Iniciando escaneo rápido")
        self.panel_actividad.agregar_actividad("🔍 Iniciando escaneo rápido...")
        self.statusBar().showMessage("Realizando escaneo rápido...")
        
        # Simular escaneo (en la implementación real, esto sería asíncrono)
        QTimer.singleShot(3000, self._finalizar_escaneo_rapido)
        
    def _finalizar_escaneo_rapido(self):
        """Finaliza el escaneo rápido"""
        self.panel_actividad.agregar_actividad("✅ Escaneo rápido completado - Sin amenazas")
        self.statusBar().showMessage("Escaneo rápido completado")
        
    def _ejecutar_escaneo_completo(self):
        """Ejecuta un escaneo completo"""
        self.logger.info("Iniciando escaneo completo")
        self.panel_actividad.agregar_actividad("🔍 Iniciando escaneo completo del sistema...")
        self.statusBar().showMessage("Realizando escaneo completo...")
        
    def _ejecutar_actualizacion(self):
        """Ejecuta actualización de base de datos"""
        self.logger.info("Iniciando actualización")
        self.panel_actividad.agregar_actividad("🔄 Actualizando base de datos de amenazas...")
        self.statusBar().showMessage("Actualizando base de datos...")
        
    def _abrir_configuracion(self):
        """Abre la ventana de configuración"""
        self.logger.info("Abriendo configuración")
        self.panel_actividad.agregar_actividad("⚙️ Accediendo a configuración del sistema")
        self.statusBar().showMessage("Configuración del sistema")
        
    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        self.logger.info("Cerrando ventana principal")
        event.accept()


# Función para lanzar la interfaz
def main():
    """Función principal para probar la interfaz"""
    app = QApplication(sys.argv)
    
    # Configurar aplicación
    app.setApplicationName("Ares-Aegis")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Ares-Aegis Security")
    
    # Crear y mostrar ventana
    ventana = VentanaPrincipalMinimalista()
    ventana.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
