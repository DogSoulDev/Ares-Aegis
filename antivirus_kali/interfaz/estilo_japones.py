#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estilo Japonés Minimalista para Ares-Aegis
Inspirado en los principios de diseño japonés: Ma (espacio), Kanso (simplicidad), Koko (austeridad)
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette

class EstiloJapones:
    """
    Clase que define el estilo visual japonés minimalista.
    Basado en principios de diseño japonés como Ma, Kanso y Koko.
    """
    
    # Paleta de colores cálidos inspirada en el diseño japonés tradicional
    COLORES = {
        # Tonos base cálidos - inspirados en madera, papel y té
        'fondo_principal': '#FFF8E7',  # Papel washi crema cálido
        'fondo_secundario': '#F5F0E0',  # Madera de cerezo claro
        'fondo_panel': '#FFFBF0',  # Papel shoji cálido
        'fondo_activo': '#FCF4E6',  # Tono activo suave
        
        # Tonos de acento cálidos - inspirados en la naturaleza japonesa
        'acento_primario': '#8B4513',  # Marrón madera oscura
        'acento_secundario': '#D2691E',  # Naranja terracota
        'acento_terciario': '#CD853F',  # Dorado arena
        'acento_hover': '#A0522D',  # Marrón siena
        
        # Estados y feedback con tonos cálidos
        'exito': '#228B22',  # Verde bosque
        'advertencia': '#FF8C00',  # Naranja oscuro
        'error': '#B22222',  # Rojo fuego
        'info': '#4682B4',  # Azul acero
        
        # Textos con mejor contraste
        'texto_primario': '#2F1B14',  # Marrón muy oscuro
        'texto_secundario': '#5D4037',  # Marrón medio
        'texto_terciario': '#8D6E63',  # Marrón claro
        'texto_inverso': '#FFFBF0',  # Crema para fondos oscuros
        'texto_enlace': '#8B4513',  # Marrón para enlaces
        
        # Bordes y separadores cálidos
        'borde_sutil': '#E6D7C3',  # Borde muy sutil beige
        'borde_normal': '#D7CCC8',  # Borde normal cálido
        'borde_activo': '#8B4513',  # Marrón cuando está activo
        'borde_hover': '#A0522D',  # Borde al pasar el mouse
        
        # Sombras cálidas y sutiles
        'sombra_suave': 'rgba(139, 69, 19, 0.08)',  # Sombra marrón muy suave
        'sombra_media': 'rgba(139, 69, 19, 0.15)',  # Sombra marrón media
        'sombra_intensa': 'rgba(139, 69, 19, 0.25)', # Sombra marrón intensa
        
        # Gradientes cálidos
        'gradiente_principal': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFF8E7, stop:1 #F5F0E0)',
        'gradiente_panel': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFFBF0, stop:1 #FCF4E6)'
    }
    
    # Tipografía - limpia y legible
    TIPOGRAFIA = {
        'familia_principal': 'Noto Sans, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        'familia_monospace': 'JetBrains Mono, "SF Mono", Monaco, Inconsolata, "Fira Code", monospace',
        
        'tamaño_titulo_principal': 24,
        'tamaño_titulo_seccion': 18,
        'tamaño_texto_normal': 13,
        'tamaño_texto_pequeño': 11,
        'tamaño_texto_mini': 9,
        
        'peso_normal': 400,
        'peso_medio': 500,
        'peso_negrita': 600,
    }
    
    # Espaciado uniforme y consistente - principio japonés "Ma" (espacio negativo)
    ESPACIADO = {
        'mini': 8,      # 8px - espaciado mínimo uniforme
        'pequeño': 12,  # 12px - separación básica
        'normal': 16,   # 16px - espaciado estándar
        'medio': 20,    # 20px - espaciado medio
        'grande': 24,   # 24px - espaciado amplio
        'xl': 32,       # 32px - espaciado extra grande
        'xxl': 48,      # 48px - espaciado máximo
        
        # Espaciado específico unificado
        'margen_contenedor': 16,    # Margen uniforme del contenedor
        'padding_panel': 16,        # Padding interno uniforme de paneles
        'separacion_secciones': 20, # Separación uniforme entre secciones
        'altura_minima_boton': 36,  # Altura mínima uniforme para botones
        'altura_minima_input': 32,  # Altura mínima uniforme para inputs
        'ancho_sidebar': 300,       # Ancho fijo del sidebar
    }
    
    # Bordes redondeados - sutiles y naturales con mejor definición
    RADIO_BORDE = {
        'sutil': 6,      # 6px - bordes muy suaves
        'normal': 10,    # 10px - bordes estándar
        'medio': 16,     # 16px - bordes medianos
        'grande': 24,    # 24px - bordes prominentes
        'circular': '50%' # Para elementos circulares
    }
    
    # Responsive breakpoints para diferentes tamaños de pantalla
    BREAKPOINTS = {
        'mobile': 480,   # Móviles
        'tablet': 768,   # Tablets
        'desktop': 1024, # Desktop estándar
        'large': 1440,   # Pantallas grandes
        'xlarge': 1920,  # Pantallas extra grandes
    }
    
    # Tamaños responsive
    RESPONSIVE = {
        'sidebar_width_min': 200,  # Ancho mínimo sidebar
        'sidebar_width_max': 280,  # Ancho máximo sidebar
        'content_min_width': 400,  # Ancho mínimo contenido
        'panel_min_height': 400,   # Altura mínima paneles
    }
    
    @staticmethod
    def obtener_stylesheet_ventana_principal():
        """Estilo para la ventana principal"""
        return f"""
        QMainWindow {{
            background-color: {EstiloJapones.COLORES['fondo_principal']};
            color: {EstiloJapones.COLORES['texto_primario']};
            font-family: {EstiloJapones.TIPOGRAFIA['familia_principal']};
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_texto_normal']}px;
        }}
        """
    
    @staticmethod
    def obtener_stylesheet_panel():
        """Estilo para paneles principales"""
        return f"""
        QWidget {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 1px solid {EstiloJapones.COLORES['borde_sutil']};
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            margin: {EstiloJapones.ESPACIADO['pequeño']}px;
            padding: {EstiloJapones.ESPACIADO['normal']}px;
        }}
        """
    
    @staticmethod
    def obtener_stylesheet_boton():
        """Estilo para botones - minimalista y elegante"""
        return f"""
        QPushButton {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 1px solid {EstiloJapones.COLORES['borde_normal']};
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            color: {EstiloJapones.COLORES['texto_primario']};
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_medio']};
            padding: {EstiloJapones.ESPACIADO['pequeño']}px {EstiloJapones.ESPACIADO['normal']}px;
            min-height: 32px;
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_texto_normal']}px;
        }}
        
        QPushButton:hover {{
            background-color: {EstiloJapones.COLORES['fondo_secundario']};
            border-color: {EstiloJapones.COLORES['acento_primario']};
        }}
        
        QPushButton:pressed {{
            background-color: {EstiloJapones.COLORES['acento_primario']};
            color: {EstiloJapones.COLORES['texto_inverso']};
        }}
        
        QPushButton:disabled {{
            background-color: {EstiloJapones.COLORES['fondo_secundario']};
            color: {EstiloJapones.COLORES['texto_terciario']};
            border-color: {EstiloJapones.COLORES['borde_sutil']};
        }}
        """
    
    @staticmethod
    def obtener_stylesheet_boton_primario():
        """Estilo para botones principales (acciones importantes)"""
        return f"""
        QPushButton {{
            background-color: {EstiloJapones.COLORES['acento_primario']};
            border: none;
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            color: {EstiloJapones.COLORES['texto_inverso']};
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_medio']};
            padding: {EstiloJapones.ESPACIADO['pequeño']}px {EstiloJapones.ESPACIADO['normal']}px;
            min-height: 32px;
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_texto_normal']}px;
        }}
        
        QPushButton:hover {{
            background-color: #1B5E20;
        }}
        
        QPushButton:pressed {{
            background-color: #0D4B13;
        }}
        
        QPushButton:disabled {{
            background-color: {EstiloJapones.COLORES['texto_terciario']};
        }}
        """
    
    @staticmethod
    def obtener_stylesheet_input():
        """Estilo para campos de entrada"""
        return f"""
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 1px solid {EstiloJapones.COLORES['borde_normal']};
            border-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
            color: {EstiloJapones.COLORES['texto_primario']};
            padding: {EstiloJapones.ESPACIADO['pequeño']}px;
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_texto_normal']}px;
            selection-background-color: {EstiloJapones.COLORES['acento_primario']};
            selection-color: {EstiloJapones.COLORES['texto_inverso']};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {EstiloJapones.COLORES['acento_primario']};
            outline: none;
        }}
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {EstiloJapones.COLORES['fondo_secundario']};
            color: {EstiloJapones.COLORES['texto_terciario']};
        }}
        """
    
    @staticmethod
    def obtener_stylesheet_label():
        """Estilo para etiquetas"""
        return f"""
        QLabel {{
            color: {EstiloJapones.COLORES['texto_primario']};
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_texto_normal']}px;
            background: transparent;
            border: none;
        }}
        
        QLabel[estiloTitulo="true"] {{
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_titulo_seccion']}px;
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_medio']};
            color: {EstiloJapones.COLORES['acento_secundario']};
            margin-bottom: {EstiloJapones.ESPACIADO['pequeño']}px;
        }}
        
        QLabel[estiloSubtitulo="true"] {{
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_texto_normal']}px;
            color: {EstiloJapones.COLORES['texto_secundario']};
            margin-bottom: {EstiloJapones.ESPACIADO['mini']}px;
        }}
        """
    
    @staticmethod
    def obtener_stylesheet_lista():
        """Estilo para listas y tablas"""
        return f"""
        QListWidget, QTableWidget, QTreeWidget {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 1px solid {EstiloJapones.COLORES['borde_sutil']};
            border-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
            alternate-background-color: {EstiloJapones.COLORES['fondo_secundario']};
            gridline-color: {EstiloJapones.COLORES['borde_sutil']};
            selection-background-color: {EstiloJapones.COLORES['acento_primario']};
            selection-color: {EstiloJapones.COLORES['texto_inverso']};
        }}
        
        QListWidget::item, QTableWidget::item, QTreeWidget::item {{
            padding: {EstiloJapones.ESPACIADO['pequeño']}px;
            border: none;
        }}
        
        QListWidget::item:hover, QTableWidget::item:hover, QTreeWidget::item:hover {{
            background-color: {EstiloJapones.COLORES['fondo_secundario']};
        }}
        
        QHeaderView::section {{
            background-color: {EstiloJapones.COLORES['fondo_secundario']};
            color: {EstiloJapones.COLORES['texto_primario']};
            padding: {EstiloJapones.ESPACIADO['pequeño']}px;
            border: none;
            border-bottom: 1px solid {EstiloJapones.COLORES['borde_normal']};
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_medio']};
        }}
        """
    
    @staticmethod
    def obtener_stylesheet_scroll():
        """Estilo para barras de desplazamiento"""
        return f"""
        QScrollBar:vertical {{
            background: {EstiloJapones.COLORES['fondo_secundario']};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background: {EstiloJapones.COLORES['borde_normal']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {EstiloJapones.COLORES['acento_secundario']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background: {EstiloJapones.COLORES['fondo_secundario']};
            height: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {EstiloJapones.COLORES['borde_normal']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {EstiloJapones.COLORES['acento_secundario']};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        """
    
    @staticmethod
    def obtener_stylesheet_tabs():
        """Estilo para pestañas"""
        return f"""
        QTabWidget::pane {{
            border: 1px solid {EstiloJapones.COLORES['borde_sutil']};
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            background-color: {EstiloJapones.COLORES['fondo_panel']};
        }}
        
        QTabBar::tab {{
            background-color: {EstiloJapones.COLORES['fondo_secundario']};
            border: 1px solid {EstiloJapones.COLORES['borde_sutil']};
            padding: {EstiloJapones.ESPACIADO['pequeño']}px {EstiloJapones.ESPACIADO['normal']}px;
            margin-right: 2px;
            border-top-left-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
            border-top-right-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border-bottom-color: {EstiloJapones.COLORES['fondo_panel']};
            color: {EstiloJapones.COLORES['acento_primario']};
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_medio']};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {EstiloJapones.COLORES['fondo_principal']};
        }}
        """
    
    @staticmethod
    def obtener_stylesheet_progress():
        """Estilo para barras de progreso"""
        return f"""
        QProgressBar {{
            background-color: {EstiloJapones.COLORES['fondo_secundario']};
            border: 1px solid {EstiloJapones.COLORES['borde_sutil']};
            border-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
            text-align: center;
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_texto_pequeño']}px;
            color: {EstiloJapones.COLORES['texto_primario']};
        }}
        
        QProgressBar::chunk {{
            background-color: {EstiloJapones.COLORES['acento_primario']};
            border-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
        }}
        """
    
    @staticmethod
    def obtener_stylesheet_completo() -> str:
        """
        Obtiene el stylesheet completo con todos los estilos japoneses cálidos y responsive.
        Incluye estilos optimizados para todos los componentes de la interfaz.
        """
        return f"""
        /* === ESTILO JAPONÉS CÁLIDO Y RESPONSIVE === */
        
        /* Configuración base de la aplicación con espaciado uniforme */
        QMainWindow {{
            background: {EstiloJapones.COLORES['gradiente_principal']};
            color: {EstiloJapones.COLORES['texto_primario']};
            font-family: {EstiloJapones.TIPOGRAFIA['familia_principal']};
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_texto_normal']}px;
            margin: 0;
            padding: 0;
        }}
        
        /* Widgets base con espaciado uniforme */
        QWidget {{
            background-color: transparent;
            color: {EstiloJapones.COLORES['texto_primario']};
            font-family: {EstiloJapones.TIPOGRAFIA['familia_principal']};
            margin: 0;
            padding: {EstiloJapones.ESPACIADO['mini']}px;
        }}
        
        /* === PANEL DE NAVEGACIÓN CON ESPACIADO UNIFORME === */
        QWidget[esPanelNavegacion="true"] {{
            background: {EstiloJapones.COLORES['gradiente_panel']};
            border-right: 2px solid {EstiloJapones.COLORES['acento_primario']};
            padding: {EstiloJapones.ESPACIADO['padding_panel']}px;
            margin: 0;
            min-width: {EstiloJapones.ESPACIADO['ancho_sidebar']}px;
            max-width: {EstiloJapones.ESPACIADO['ancho_sidebar']}px;
        }}
        
        /* Títulos con espaciado uniforme mejorado */
        QLabel[estiloTitulo="true"] {{
            color: {EstiloJapones.COLORES['acento_primario']};
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_negrita']};
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_titulo_principal']}px;
            padding: {EstiloJapones.ESPACIADO['normal']}px;
            margin: {EstiloJapones.ESPACIADO['pequeño']}px 0;
            background-color: {EstiloJapones.COLORES['fondo_activo']};
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            border-left: 3px solid {EstiloJapones.COLORES['acento_primario']};
        }}
        
        QLabel[estiloSubtitulo="true"] {{
            color: {EstiloJapones.COLORES['acento_secundario']};
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_medio']};
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_titulo_seccion']}px;
            padding: {EstiloJapones.ESPACIADO['pequeño']}px {EstiloJapones.ESPACIADO['normal']}px;
            margin: {EstiloJapones.ESPACIADO['mini']}px 0;
            background-color: {EstiloJapones.COLORES['fondo_secundario']};
            border-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
        }}
        
        /* === BOTONES CON ESPACIADO UNIFORME === */
        QPushButton {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 2px solid {EstiloJapones.COLORES['borde_normal']};
            color: {EstiloJapones.COLORES['texto_primario']};
            padding: {EstiloJapones.ESPACIADO['pequeño']}px {EstiloJapones.ESPACIADO['normal']}px;
            margin: {EstiloJapones.ESPACIADO['mini']}px;
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_texto_normal']}px;
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_medio']};
            min-height: {EstiloJapones.ESPACIADO['altura_minima_boton']}px;
        }}
        
        QPushButton:hover {{
            background-color: {EstiloJapones.COLORES['fondo_activo']};
            border-color: {EstiloJapones.COLORES['acento_hover']};
            color: {EstiloJapones.COLORES['acento_primario']};
        }}
        
        QPushButton:pressed {{
            background-color: {EstiloJapones.COLORES['acento_primario']};
            color: {EstiloJapones.COLORES['texto_inverso']};
            border-color: {EstiloJapones.COLORES['acento_primario']};
        }}
        
        QPushButton[esPrimario="true"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {EstiloJapones.COLORES['acento_primario']}, 
                stop:1 {EstiloJapones.COLORES['acento_hover']});
            color: {EstiloJapones.COLORES['texto_inverso']};
            border: none;
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_negrita']};
            min-height: {EstiloJapones.ESPACIADO['altura_minima_boton'] + 6}px;
        }}
        
        QPushButton[esPrimario="true"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {EstiloJapones.COLORES['acento_hover']}, 
                stop:1 {EstiloJapones.COLORES['acento_primario']});
        }}
        
        /* Botones de navegación */
        QPushButton[esBotonNavegacion="true"] {{
            background-color: transparent;
            border: none;
            color: {EstiloJapones.COLORES['texto_primario']};
            text-align: left;
            padding: {EstiloJapones.ESPACIADO['pequeño']}px {EstiloJapones.ESPACIADO['normal']}px;
            margin: {EstiloJapones.ESPACIADO['mini']}px;
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_texto_normal']}px;
            min-height: {EstiloJapones.ESPACIADO['altura_minima_boton']}px;
        }}
        
        QPushButton[esBotonNavegacion="true"]:hover {{
            background-color: {EstiloJapones.COLORES['fondo_activo']};
            color: {EstiloJapones.COLORES['acento_primario']};
            border-left: 4px solid {EstiloJapones.COLORES['acento_primario']};
        }}
        
        QPushButton[esBotonNavegacion="true"]:pressed {{
            background-color: {EstiloJapones.COLORES['acento_primario']};
            color: {EstiloJapones.COLORES['texto_inverso']};
        }}
        
        /* === PANELES Y CONTENEDORES RESPONSIVE === */
        QGroupBox {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 2px solid {EstiloJapones.COLORES['borde_sutil']};
            border-radius: {EstiloJapones.RADIO_BORDE['medio']}px;
            margin: {EstiloJapones.ESPACIADO['pequeño']}px;
            padding: {EstiloJapones.ESPACIADO['padding_panel']}px;
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_medio']};
            color: {EstiloJapones.COLORES['texto_primario']};
            min-height: 200px;
        }}
        
        QGroupBox::title {{
            background-color: {EstiloJapones.COLORES['fondo_activo']};
            color: {EstiloJapones.COLORES['acento_primario']};
            padding: {EstiloJapones.ESPACIADO['mini']}px {EstiloJapones.ESPACIADO['pequeño']}px;
            border-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
            margin-left: {EstiloJapones.ESPACIADO['pequeño']}px;
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_negrita']};
        }}
        
        QFrame {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 1px solid {EstiloJapones.COLORES['borde_sutil']};
            border-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
            padding: {EstiloJapones.ESPACIADO['pequeño']}px;
            margin: {EstiloJapones.ESPACIADO['mini']}px;
        }}
        
        /* === INPUTS Y FORMS MEJORADOS === */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 2px solid {EstiloJapones.COLORES['borde_normal']};
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            padding: {EstiloJapones.ESPACIADO['pequeño']}px;
            margin: {EstiloJapones.ESPACIADO['mini']}px;
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_texto_normal']}px;
            color: {EstiloJapones.COLORES['texto_primario']};
            selection-background-color: {EstiloJapones.COLORES['acento_terciario']};
            min-height: {EstiloJapones.ESPACIADO['altura_minima_boton'] - 10}px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {EstiloJapones.COLORES['acento_primario']};
            background-color: {EstiloJapones.COLORES['fondo_activo']};
        }}
        
        QComboBox {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 2px solid {EstiloJapones.COLORES['borde_normal']};
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            padding: {EstiloJapones.ESPACIADO['pequeño']}px;
            margin: {EstiloJapones.ESPACIADO['mini']}px;
            min-height: {EstiloJapones.ESPACIADO['altura_minima_boton'] - 10}px;
            min-width: 150px;
        }}
        
        QComboBox:hover {{
            border-color: {EstiloJapones.COLORES['acento_hover']};
            background-color: {EstiloJapones.COLORES['fondo_activo']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            background-color: {EstiloJapones.COLORES['acento_primario']};
            border-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {EstiloJapones.COLORES['texto_inverso']};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 2px solid {EstiloJapones.COLORES['borde_normal']};
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            selection-background-color: {EstiloJapones.COLORES['acento_terciario']};
            padding: {EstiloJapones.ESPACIADO['mini']}px;
        }}
        
        QSpinBox, QDoubleSpinBox {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 2px solid {EstiloJapones.COLORES['borde_normal']};
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            padding: {EstiloJapones.ESPACIADO['pequeño']}px;
            margin: {EstiloJapones.ESPACIADO['mini']}px;
            min-height: {EstiloJapones.ESPACIADO['altura_minima_boton'] - 10}px;
        }}
        
        QCheckBox, QRadioButton {{
            color: {EstiloJapones.COLORES['texto_primario']};
            padding: {EstiloJapones.ESPACIADO['mini']}px;
            margin: {EstiloJapones.ESPACIADO['mini']}px;
            spacing: {EstiloJapones.ESPACIADO['pequeño']}px;
        }}
        
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {EstiloJapones.COLORES['borde_normal']};
            border-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
            background-color: {EstiloJapones.COLORES['fondo_panel']};
        }}
        
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background-color: {EstiloJapones.COLORES['acento_primario']};
            border-color: {EstiloJapones.COLORES['acento_primario']};
        }}
        
        QCheckBox::indicator:checked {{
            image: none;
            background-color: {EstiloJapones.COLORES['acento_primario']};
        }}
        
        QRadioButton::indicator:checked {{
            background: radial-gradient(circle, {EstiloJapones.COLORES['acento_primario']} 30%, 
                                      transparent 31%);
        }}
        
        /* === TABLAS Y LISTAS RESPONSIVE === */
        QTableWidget, QListWidget, QTreeWidget {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 2px solid {EstiloJapones.COLORES['borde_sutil']};
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            alternate-background-color: {EstiloJapones.COLORES['fondo_secundario']};
            gridline-color: {EstiloJapones.COLORES['borde_sutil']};
            selection-background-color: {EstiloJapones.COLORES['acento_terciario']};
            selection-color: {EstiloJapones.COLORES['texto_primario']};
            margin: {EstiloJapones.ESPACIADO['pequeño']}px;
            padding: {EstiloJapones.ESPACIADO['mini']}px;
        }}
        
        QTableWidget::item, QListWidget::item, QTreeWidget::item {{
            padding: {EstiloJapones.ESPACIADO['pequeño']}px;
            border: none;
            min-height: {EstiloJapones.ESPACIADO['altura_minima_boton'] - 20}px;
        }}
        
        QTableWidget::item:hover, QListWidget::item:hover, QTreeWidget::item:hover {{
            background-color: {EstiloJapones.COLORES['fondo_activo']};
            color: {EstiloJapones.COLORES['acento_primario']};
        }}
        
        QHeaderView::section {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {EstiloJapones.COLORES['acento_secundario']}, 
                stop:1 {EstiloJapones.COLORES['acento_terciario']});
            color: {EstiloJapones.COLORES['texto_inverso']};
            padding: {EstiloJapones.ESPACIADO['pequeño']}px;
            border: none;
            border-bottom: 2px solid {EstiloJapones.COLORES['acento_primario']};
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_negrita']};
            min-height: {EstiloJapones.ESPACIADO['altura_minima_boton']}px;
        }}
        
        /* === BARRAS DE PROGRESO === */
        QProgressBar {{
            background-color: {EstiloJapones.COLORES['fondo_secundario']};
            border: 2px solid {EstiloJapones.COLORES['borde_normal']};
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            text-align: center;
            padding: {EstiloJapones.ESPACIADO['mini']}px;
            margin: {EstiloJapones.ESPACIADO['pequeño']}px;
            min-height: {EstiloJapones.ESPACIADO['altura_minima_boton'] - 20}px;
            color: {EstiloJapones.COLORES['texto_primario']};
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_medio']};
        }}
        
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {EstiloJapones.COLORES['acento_primario']}, 
                stop:1 {EstiloJapones.COLORES['acento_terciario']});
            border-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
        }}
        
        /* === SLIDERS === */
        QSlider::groove:horizontal {{
            background-color: {EstiloJapones.COLORES['fondo_secundario']};
            height: 8px;
            border-radius: 4px;
            margin: {EstiloJapones.ESPACIADO['pequeño']}px 0;
        }}
        
        QSlider::handle:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {EstiloJapones.COLORES['acento_primario']}, 
                stop:1 {EstiloJapones.COLORES['acento_hover']});
            border: 2px solid {EstiloJapones.COLORES['borde_normal']};
            width: 20px;
            margin: -8px 0;
            border-radius: 12px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {EstiloJapones.COLORES['acento_hover']}, 
                stop:1 {EstiloJapones.COLORES['acento_primario']});
        }}
        
        /* === SCROLLBARS RESPONSIVE === */
        QScrollBar:vertical {{
            background-color: {EstiloJapones.COLORES['fondo_secundario']};
            width: 16px;
            border-radius: 8px;
            margin: 0;
            border: 1px solid {EstiloJapones.COLORES['borde_sutil']};
        }}
        
        QScrollBar::handle:vertical {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {EstiloJapones.COLORES['acento_primario']}, 
                stop:1 {EstiloJapones.COLORES['acento_terciario']});
            border-radius: 7px;
            min-height: 30px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {EstiloJapones.COLORES['acento_hover']}, 
                stop:1 {EstiloJapones.COLORES['acento_primario']});
        }}
        
        QScrollBar:horizontal {{
            background-color: {EstiloJapones.COLORES['fondo_secundario']};
            height: 16px;
            border-radius: 8px;
            margin: 0;
            border: 1px solid {EstiloJapones.COLORES['borde_sutil']};
        }}
        
        QScrollBar::handle:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {EstiloJapones.COLORES['acento_primario']}, 
                stop:1 {EstiloJapones.COLORES['acento_terciario']});
            border-radius: 7px;
            min-width: 30px;
            margin: 2px;
        }}
        
        QScrollBar::add-line, QScrollBar::sub-line {{
            background: none;
            border: none;
        }}
        
        /* === TABS RESPONSIVE === */
        QTabWidget::pane {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 2px solid {EstiloJapones.COLORES['borde_sutil']};
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            padding: {EstiloJapones.ESPACIADO['padding_panel']}px;
            margin: {EstiloJapones.ESPACIADO['mini']}px;
        }}
        
        QTabBar::tab {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {EstiloJapones.COLORES['fondo_secundario']}, 
                stop:1 {EstiloJapones.COLORES['fondo_panel']});
            border: 2px solid {EstiloJapones.COLORES['borde_normal']};
            border-bottom: none;
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px {EstiloJapones.RADIO_BORDE['normal']}px 0 0;
            padding: {EstiloJapones.ESPACIADO['pequeño']}px {EstiloJapones.ESPACIADO['normal']}px;
            margin: {EstiloJapones.ESPACIADO['mini']}px;
            color: {EstiloJapones.COLORES['texto_secundario']};
            min-height: {EstiloJapones.ESPACIADO['altura_minima_boton'] - 10}px;
        }}
        
        QTabBar::tab:selected {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {EstiloJapones.COLORES['acento_primario']}, 
                stop:1 {EstiloJapones.COLORES['acento_terciario']});
            color: {EstiloJapones.COLORES['texto_inverso']};
            border-color: {EstiloJapones.COLORES['acento_primario']};
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_negrita']};
        }}
        
        QTabBar::tab:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {EstiloJapones.COLORES['fondo_activo']}, 
                stop:1 {EstiloJapones.COLORES['fondo_secundario']});
            color: {EstiloJapones.COLORES['acento_primario']};
        }}
        
        /* === SPLITTERS RESPONSIVE === */
        QSplitter::handle {{
            background-color: {EstiloJapones.COLORES['acento_primario']};
            margin: 2px;
        }}
        
        QSplitter::handle:horizontal {{
            width: 6px;
            border-radius: 3px;
        }}
        
        QSplitter::handle:vertical {{
            height: 6px;
            border-radius: 3px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {EstiloJapones.COLORES['acento_hover']};
        }}
        
        /* === MENU Y TOOLBAR === */
        QMenuBar {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {EstiloJapones.COLORES['acento_primario']}, 
                stop:1 {EstiloJapones.COLORES['acento_hover']});
            color: {EstiloJapones.COLORES['texto_inverso']};
            padding: {EstiloJapones.ESPACIADO['mini']}px;
            spacing: {EstiloJapones.ESPACIADO['pequeño']}px;
        }}
        
        QMenuBar::item {{
            background: transparent;
            padding: {EstiloJapones.ESPACIADO['pequeño']}px {EstiloJapones.ESPACIADO['normal']}px;
            border-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {EstiloJapones.COLORES['acento_hover']};
        }}
        
        QMenu {{
            background-color: {EstiloJapones.COLORES['fondo_panel']};
            border: 2px solid {EstiloJapones.COLORES['borde_normal']};
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            padding: {EstiloJapones.ESPACIADO['mini']}px;
        }}
        
        QMenu::item {{
            padding: {EstiloJapones.ESPACIADO['pequeño']}px {EstiloJapones.ESPACIADO['normal']}px;
            border-radius: {EstiloJapones.RADIO_BORDE['sutil']}px;
            margin: {EstiloJapones.ESPACIADO['mini']}px;
        }}
        
        QMenu::item:selected {{
            background-color: {EstiloJapones.COLORES['acento_terciario']};
            color: {EstiloJapones.COLORES['texto_primario']};
        }}
        
        QToolBar {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {EstiloJapones.COLORES['fondo_activo']}, 
                stop:1 {EstiloJapones.COLORES['fondo_secundario']});
            border: none;
            border-bottom: 2px solid {EstiloJapones.COLORES['acento_primario']};
            padding: {EstiloJapones.ESPACIADO['pequeño']}px;
            spacing: {EstiloJapones.ESPACIADO['pequeño']}px;
        }}
        
        QStatusBar {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {EstiloJapones.COLORES['fondo_secundario']}, 
                stop:1 {EstiloJapones.COLORES['fondo_activo']});
            border-top: 2px solid {EstiloJapones.COLORES['acento_primario']};
            padding: {EstiloJapones.ESPACIADO['pequeño']}px;
            color: {EstiloJapones.COLORES['texto_secundario']};
        }}
        
        /* === ELEMENTOS ESPECIALES === */
        QLabel[esValorEstadistica="true"] {{
            color: {EstiloJapones.COLORES['acento_primario']};
            font-weight: {EstiloJapones.TIPOGRAFIA['peso_negrita']};
            font-size: {EstiloJapones.TIPOGRAFIA['tamaño_titulo_seccion']}px;
            background-color: {EstiloJapones.COLORES['fondo_activo']};
            padding: {EstiloJapones.ESPACIADO['pequeño']}px;
            border-radius: {EstiloJapones.RADIO_BORDE['normal']}px;
            border: 2px solid {EstiloJapones.COLORES['acento_terciario']};
        }}
        
        /* === RESPONSIVIDAD === */
        /* Para pantallas pequeñas */
        @media (max-width: {EstiloJapones.BREAKPOINTS['tablet']}px) {{
            QWidget[esPanelNavegacion="true"] {{
                min-width: 200px;
                max-width: 200px;
            }}
            
            QPushButton {{
                min-height: {EstiloJapones.ESPACIADO['altura_minima_boton'] + 6}px;
                font-size: {EstiloJapones.TIPOGRAFIA['tamaño_texto_normal'] + 1}px;
            }}
        }}
        
        /* === ANIMACIONES SUTILES === */
        * {{
            transition: all 0.3s ease-in-out;
        }}
        """
    
    @staticmethod
    def aplicar_fuente_personalizada(widget, tamaño=None, peso=None):
        """Aplica fuente personalizada a un widget"""
        from PySide6.QtGui import QFont
        
        fuente = QFont(EstiloJapones.TIPOGRAFIA['familia_principal'])
        
        if tamaño:
            fuente.setPointSize(tamaño)
        else:
            fuente.setPointSize(EstiloJapones.TIPOGRAFIA['tamaño_texto_normal'])
            
        if peso:
            # Convertir peso numérico a QFont.Weight
            if peso == 400:
                fuente.setWeight(QFont.Weight.Normal)
            elif peso == 500:
                fuente.setWeight(QFont.Weight.Medium)
            elif peso == 600:
                fuente.setWeight(QFont.Weight.DemiBold)
            elif peso == 700:
                fuente.setWeight(QFont.Weight.Bold)
            else:
                fuente.setWeight(QFont.Weight.Normal)
        else:
            fuente.setWeight(QFont.Weight.Normal)
            
        widget.setFont(fuente)
    
    @staticmethod
    def obtener_ruta_imagen_ares():
        """Obtiene la ruta de la imagen Ares.jpeg"""
        import os
        ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(ruta_base, "recursos", "Ares.jpeg")
    
    @staticmethod
    def crear_widget_imagen_ares(parent=None, tamaño=(150, 150)):
        """Crea un widget con la imagen Ares integrada en el diseño japonés"""
        from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout
        from PySide6.QtGui import QPixmap
        from PySide6.QtCore import Qt
        
        # Contenedor principal con estilo japonés
        contenedor = QFrame(parent)
        contenedor.setObjectName("contenedorImagenAres")
        contenedor.setStyleSheet(f"""
            QFrame#contenedorImagenAres {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {EstiloJapones.COLORES['fondo_activo']}, 
                    stop:1 {EstiloJapones.COLORES['fondo_panel']});
                border: 2px solid {EstiloJapones.COLORES['acento_primario']};
                border-radius: {EstiloJapones.RADIO_BORDE['medio']}px;
                padding: {EstiloJapones.ESPACIADO['normal']}px;
                margin: {EstiloJapones.ESPACIADO['pequeño']}px;
            }}
        """)
        
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(EstiloJapones.ESPACIADO['pequeño'], 
                                EstiloJapones.ESPACIADO['pequeño'],
                                EstiloJapones.ESPACIADO['pequeño'], 
                                EstiloJapones.ESPACIADO['pequeño'])
        
        # Label para la imagen
        label_imagen = QLabel()
        label_imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        try:
            ruta_imagen = EstiloJapones.obtener_ruta_imagen_ares()
            pixmap = QPixmap(ruta_imagen)
            if not pixmap.isNull():
                pixmap_escalado = pixmap.scaled(tamaño[0], tamaño[1], 
                                              Qt.AspectRatioMode.KeepAspectRatio, 
                                              Qt.TransformationMode.SmoothTransformation)
                label_imagen.setPixmap(pixmap_escalado)
            else:
                # Imagen placeholder si no se encuentra la imagen
                label_imagen.setText("🛡️ ARES AEGIS 🛡️")
                label_imagen.setStyleSheet(f"""
                    QLabel {{
                        color: {EstiloJapones.COLORES['acento_primario']};
                        font-size: {EstiloJapones.TIPOGRAFIA['tamaño_titulo_principal']}px;
                        font-weight: {EstiloJapones.TIPOGRAFIA['peso_negrita']};
                        background-color: transparent;
                        border: none;
                        padding: {EstiloJapones.ESPACIADO['normal']}px;
                    }}
                """)
        except Exception:
            # Fallback en caso de error
            label_imagen.setText("⚔️ ARES AEGIS ⚔️")
            label_imagen.setStyleSheet(f"""
                QLabel {{
                    color: {EstiloJapones.COLORES['acento_primario']};
                    font-size: {EstiloJapones.TIPOGRAFIA['tamaño_titulo_principal']}px;
                    font-weight: {EstiloJapones.TIPOGRAFIA['peso_negrita']};
                    background-color: transparent;
                    border: none;
                    padding: {EstiloJapones.ESPACIADO['normal']}px;
                }}
            """)
        
        layout.addWidget(label_imagen)
        
        # Título debajo de la imagen
        titulo = QLabel("ARES AEGIS")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet(f"""
            QLabel {{
                color: {EstiloJapones.COLORES['acento_primario']};
                font-size: {EstiloJapones.TIPOGRAFIA['tamaño_titulo_seccion']}px;
                font-weight: {EstiloJapones.TIPOGRAFIA['peso_negrita']};
                background-color: transparent;
                border: none;
                margin-top: {EstiloJapones.ESPACIADO['mini']}px;
            }}
        """)
        layout.addWidget(titulo)
        
        # Aplicar sombra sutil
        EstiloJapones.aplicar_sombra_sutil(contenedor)
        
        return contenedor
    
    @staticmethod
    def aplicar_sombra_sutil(widget):
        """Aplica sombra sutil a un widget"""
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor
        
        efecto = QGraphicsDropShadowEffect()
        efecto.setBlurRadius(10)
        efecto.setXOffset(0)
        efecto.setYOffset(2)
        efecto.setColor(QColor(0, 0, 0, 25))  # Sombra muy sutil
        widget.setGraphicsEffect(efecto)
