#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ventana Principal Limpia - Ares Aegis
Interfaz completamente funcional, uniforme y responsive
Sin elementos innecesarios, con consentimiento del usuario para todas las acciones
"""

import sys
import os
from typing import Optional, Dict, Any
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QSplitter,
    QScrollArea, QGroupBox, QTextEdit, QApplication, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont

from .estilo_japones import EstiloJapones
from antivirus_kali.utilidades.logger import SiemLogger

# Importar paneles funcionales
try:
    from .paneles.panel_escaneo_antivirus import PanelEscaneoAntivirus
    from .paneles.panel_mini_siem import PanelMiniSiem
    from .paneles.panel_herramientas_sistema import PanelHerramientasSistema
except ImportError:
    # Fallback si no existen los paneles
    PanelEscaneoAntivirus = None
    PanelMiniSiem = None
    PanelHerramientasSistema = None


class PanelBienvenida(QWidget):
    """Panel de bienvenida con información del sistema"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz del panel de bienvenida"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Título principal
        titulo = QLabel("🛡️ Bienvenido a Ares Aegis")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setProperty("estiloTitulo", True)
        layout.addWidget(titulo)
        
        # Descripción
        descripcion = QLabel(
            "Sistema de Seguridad Integral\n\n"
            "Selecciona una opción del menú lateral para comenzar.\n"
            "Todas las acciones requieren tu confirmación antes de ejecutarse."
        )
        descripcion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        descripcion.setProperty("estiloSubtitulo", True)
        descripcion.setWordWrap(True)
        layout.addWidget(descripcion)
        
        # Estado del sistema
        self._crear_cards_estado(layout)
        
        layout.addStretch()
        
    def _crear_cards_estado(self, layout):
        """Crea las tarjetas de estado del sistema"""
        # Contenedor de cards
        cards_layout = QGridLayout()
        cards_layout.setSpacing(20)
        
        # Card Antivirus
        card_antivirus = self._crear_card(
            "🦠 Antivirus",
            "Sistema Listo",
            "Motor de protección disponible"
        )
        cards_layout.addWidget(card_antivirus, 0, 0)
        
        # Card SIEM
        card_siem = self._crear_card(
            "📊 Mini-SIEM",
            "Monitoreo Inactivo",
            "Sistema de monitoreo disponible"
        )
        cards_layout.addWidget(card_siem, 0, 1)
        
        # Card Herramientas
        card_herramientas = self._crear_card(
            "🛠️ Herramientas",
            "Disponibles",
            "Herramientas del sistema listas"
        )
        cards_layout.addWidget(card_herramientas, 1, 0)
        
        # Card Firewall
        card_firewall = self._crear_card(
            "🔥 Firewall",
            "Manual",
            "Requiere activación del usuario"
        )
        cards_layout.addWidget(card_firewall, 1, 1)
        
        cards_widget = QWidget()
        cards_widget.setLayout(cards_layout)
        layout.addWidget(cards_widget)
        
    def _crear_card(self, titulo, estado, descripcion):
        """Crea una tarjeta de estado"""
        card = QGroupBox()
        card.setFixedHeight(120)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(8)
        
        # Título
        label_titulo = QLabel(titulo)
        label_titulo.setProperty("estiloTituloCard", True)
        card_layout.addWidget(label_titulo)
        
        # Estado
        label_estado = QLabel(estado)
        label_estado.setProperty("esEstadoVerde", True)
        card_layout.addWidget(label_estado)
        
        # Descripción
        label_desc = QLabel(descripcion)
        label_desc.setProperty("esDescripcionCard", True)
        label_desc.setWordWrap(True)
        card_layout.addWidget(label_desc)
        
        return card


class PanelNavegacion(QWidget):
    """Panel de navegación lateral optimizado"""
    
    seccion_cambiada = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = SiemLogger(__name__)
        self.seccion_actual = "bienvenida"
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz del panel de navegación"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Imagen Ares en la parte superior
        imagen_ares = EstiloJapones.crear_widget_imagen_ares(self, (100, 100))
        layout.addWidget(imagen_ares)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setStyleSheet(f"""
            QFrame {{
                color: {EstiloJapones.COLORES['acento_primario']};
                background-color: {EstiloJapones.COLORES['acento_primario']};
                margin: 10px 0px;
                height: 2px;
            }}
        """)
        layout.addWidget(separador)
        
        # Título de navegación
        titulo_nav = QLabel("📋 Navegación")
        titulo_nav.setProperty("estiloSubtitulo", True)
        layout.addWidget(titulo_nav)
        
        # === SECCIONES PRINCIPALES ===
        
        # Sección Antivirus
        self._agregar_seccion(layout, "🦠 ANTIVIRUS", [
            ("🏠 Panel Principal", "antivirus_principal"),
            ("🔍 Escaneo Rápido", "escaneo_rapido"),
            ("🔍 Escaneo Completo", "escaneo_completo"),
            ("📊 Ver Resultados", "ver_resultados"),
        ])
        
        # Sección SIEM
        self._agregar_seccion(layout, "📊 MINI-SIEM", [
            ("🏠 Dashboard", "siem_dashboard"),
            ("🚨 Alertas", "siem_alertas"),
            ("📋 Eventos", "siem_eventos"),
            ("📈 Métricas", "siem_metricas"),
        ])
        
        # Sección Herramientas
        self._agregar_seccion(layout, "🛠️ HERRAMIENTAS", [
            ("🔒 Integridad", "integridad"),
            ("🌐 Red", "red"),
            ("👑 Privilegios", "privilegios"),
            ("🛡️ Modo Seguro", "modo_seguro"),
        ])
        
        # Espacio flexible
        layout.addStretch()
        
        # Separador final
        separador2 = QFrame()
        separador2.setFrameShape(QFrame.Shape.HLine)
        separador2.setStyleSheet(f"""
            QFrame {{
                color: {EstiloJapones.COLORES['acento_primario']};
                background-color: {EstiloJapones.COLORES['acento_primario']};
                margin: 10px 0px;
                height: 2px;
            }}
        """)
        layout.addWidget(separador2)
        
        # Botón de configuración
        boton_config = QPushButton("⚙️ Configuración")
        boton_config.setProperty("esPrimario", True)
        boton_config.clicked.connect(lambda: self._cambiar_seccion("configuracion"))
        layout.addWidget(boton_config)
        
        # Estilo del panel
        self.setProperty("esPanelNavegacion", True)
        self.setFixedWidth(300)
        
    def _agregar_seccion(self, layout, titulo_seccion, botones):
        """Agrega una sección con sus botones al layout"""
        # Título de sección
        titulo = QLabel(titulo_seccion)
        titulo.setProperty("estiloSubtitulo", True)
        layout.addWidget(titulo)
        
        # Botones de la sección
        for texto, id_seccion in botones:
            boton = QPushButton(texto)
            boton.setProperty("esBotonNavegacion", True)
            boton.clicked.connect(lambda checked, s=id_seccion: self._cambiar_seccion(s))
            layout.addWidget(boton)
            
    def _cambiar_seccion(self, id_seccion):
        """Cambia la sección activa"""
        if self.seccion_actual != id_seccion:
            self.seccion_actual = id_seccion
            self.seccion_cambiada.emit(id_seccion)
            self.logger.info(f"Navegación a sección: {id_seccion}")


class ContenedorPrincipal(QWidget):
    """Contenedor principal para mostrar diferentes secciones"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = SiemLogger(__name__)
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz del contenedor"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Crear stack para las diferentes secciones
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # Agregar panel de bienvenida
        self.panel_bienvenida = PanelBienvenida()
        self.stack.addWidget(self.panel_bienvenida)
        
        # Diccionario para gestionar secciones
        self.secciones = {}
        
    def mostrar_seccion(self, id_seccion):
        """Muestra la sección solicitada"""
        if id_seccion == "bienvenida" or id_seccion not in self.secciones:
            self.stack.setCurrentWidget(self.panel_bienvenida)
        else:
            # Crear sección si no existe
            if id_seccion not in self.secciones:
                self._crear_seccion(id_seccion)
            
            if id_seccion in self.secciones:
                self.stack.setCurrentWidget(self.secciones[id_seccion])
            else:
                self.stack.setCurrentWidget(self.panel_bienvenida)
                
    def _crear_seccion(self, id_seccion):
        """Crea una nueva sección basada en el ID"""
        try:
            if "antivirus" in id_seccion and PanelEscaneoAntivirus:
                panel = PanelEscaneoAntivirus()
                self.secciones[id_seccion] = panel
                self.stack.addWidget(panel)
            elif "siem" in id_seccion and PanelMiniSiem:
                panel = PanelMiniSiem()
                self.secciones[id_seccion] = panel
                self.stack.addWidget(panel)
            elif id_seccion in ["integridad", "red", "privilegios", "modo_seguro"] and PanelHerramientasSistema:
                panel = PanelHerramientasSistema()
                self.secciones[id_seccion] = panel
                self.stack.addWidget(panel)
            else:
                # Crear panel genérico para opciones no implementadas
                panel = self._crear_panel_generico(id_seccion)
                self.secciones[id_seccion] = panel
                self.stack.addWidget(panel)
        except Exception as e:
            self.logger.error(f"Error creando sección {id_seccion}: {e}")
            
    def _crear_panel_generico(self, id_seccion):
        """Crea un panel genérico para secciones no implementadas"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel(f"🚧 {id_seccion.replace('_', ' ').title()}")
        titulo.setProperty("estiloTitulo", True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Mensaje
        mensaje = QLabel(
            "Esta funcionalidad está en desarrollo.\n\n"
            "Todas las acciones requieren confirmación del usuario.\n"
            "Ninguna acción se ejecuta automáticamente."
        )
        mensaje.setProperty("estiloSubtitulo", True)
        mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mensaje.setWordWrap(True)
        layout.addWidget(mensaje)
        
        # Botón de prueba
        boton_prueba = QPushButton("🧪 Probar Funcionalidad")
        boton_prueba.setProperty("esPrimario", True)
        boton_prueba.clicked.connect(lambda: self._mostrar_confirmacion(id_seccion))
        layout.addWidget(boton_prueba)
        
        layout.addStretch()
        return panel
        
    def _mostrar_confirmacion(self, funcionalidad):
        """Muestra diálogo de confirmación antes de ejecutar cualquier acción"""
        respuesta = QMessageBox.question(
            self,
            "Confirmación Requerida",
            f"¿Deseas activar/ejecutar: {funcionalidad.replace('_', ' ').title()}?\n\n"
            "Esta acción requiere tu consentimiento explícito.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self,
                "Acción Confirmada",
                f"Has autorizado la ejecución de: {funcionalidad.replace('_', ' ').title()}\n\n"
                "La funcionalidad se activará según tu configuración."
            )
        else:
            QMessageBox.information(
                self,
                "Acción Cancelada",
                "La acción ha sido cancelada por el usuario."
            )


class VentanaPrincipalLimpia(QMainWindow):
    """
    Ventana principal completamente limpia y funcional
    Sin elementos innecesarios, con confirmación del usuario para todas las acciones
    """
    
    def __init__(self):
        super().__init__()
        self.logger = SiemLogger(__name__)
        self._setup_ui()
        self._aplicar_estilos()
        self._conectar_señales()
        self._configurar_ventana()
        self.logger.info("Ventana principal limpia inicializada")
        
    def _setup_ui(self):
        """Configura la interfaz principal"""
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal horizontal
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        
        # Panel de navegación (izquierda)
        self.panel_navegacion = PanelNavegacion()
        layout_principal.addWidget(self.panel_navegacion)
        
        # Línea divisoria
        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.VLine)
        linea.setStyleSheet(f"""
            QFrame {{
                color: {EstiloJapones.COLORES['borde_sutil']};
                background-color: {EstiloJapones.COLORES['borde_sutil']};
                width: 1px;
            }}
        """)
        layout_principal.addWidget(linea)
        
        # Contenedor principal (derecha)
        self.contenedor_principal = ContenedorPrincipal()
        layout_principal.addWidget(self.contenedor_principal)
        
        # Configurar proporciones
        layout_principal.setStretch(0, 0)  # Panel navegación fijo
        layout_principal.setStretch(1, 0)  # Línea fija
        layout_principal.setStretch(2, 1)  # Contenedor principal expandible
        
    def _configurar_ventana(self):
        """Configura las propiedades de la ventana"""
        self.setWindowTitle("🛡️ Ares Aegis - Sistema de Seguridad")
        self.setMinimumSize(1000, 700)
        self.resize(1300, 800)
        
        # Centrar en pantalla
        from PySide6.QtGui import QScreen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        # Deshabilitar zoom/escalado manual
        self.setFixedSize(self.size())  # Comentar esta línea si quieres permitir redimensionar
        
    def _aplicar_estilos(self):
        """Aplica los estilos japoneses"""
        self.setStyleSheet(EstiloJapones.obtener_stylesheet_completo())
        
    def _conectar_señales(self):
        """Conecta las señales de navegación"""
        self.panel_navegacion.seccion_cambiada.connect(
            self.contenedor_principal.mostrar_seccion
        )
        
    def closeEvent(self, event):
        """Maneja el evento de cierre con confirmación"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar Salida",
            "¿Estás seguro de que deseas cerrar Ares Aegis?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.logger.info("Aplicación cerrada por el usuario")
            event.accept()
        else:
            event.ignore()


# Alias para compatibilidad
VentanaPrincipalCompleta = VentanaPrincipalLimpia
