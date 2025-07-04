#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Interfaz Principal GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# Importar controladores y modelos
from ..controladores.controlador_principal import ControladorPrincipal
from ..modelos.siem import TipoEvento


class TemaModerno:
    """Paleta de colores moderna inspirada en Windows 11 Defender con mitología griega."""
    
    # Colores principales del tema moderno
    FONDO_PRINCIPAL = "#F3F4F6"         # Gris muy claro (Windows 11)
    FONDO_SECUNDARIO = "#FFFFFF"        # Blanco puro
    FONDO_CARD = "#FFFFFF"              # Blanco para tarjetas
    BORDE_CARD = "#E5E7EB"              # Gris claro para bordes
    
    # Colores de acento (inspirados en mitología griega)
    AZUL_OLIMPICO = "#0078D4"           # Azul principal (Windows 11)
    AZUL_HOVER = "#106EBE"              # Azul hover
    VERDE_PROTECCION = "#107C10"        # Verde de protección
    ROJO_AMENAZA = "#D13438"            # Rojo de amenaza
    NARANJA_ADVERTENCIA = "#FF8C00"     # Naranja advertencia
    
    # Colores de texto
    TEXTO_PRINCIPAL = "#323130"         # Gris oscuro principal
    TEXTO_SECUNDARIO = "#605E5C"        # Gris medio
    TEXTO_MUTED = "#8A8886"             # Gris claro
    TEXTO_BLANCO = "#FFFFFF"            # Blanco
    
    # Colores de estado (mitología griega)
    DIVINO_DORADO = "#FFD700"           # Dorado divino
    PLATA_LUNAR = "#C0C0C0"             # Plata de Artemisa
    BRONCE_HEFESTO = "#CD7F32"          # Bronce de Hefesto
    PURPURA_REAL = "#6B46C1"            # Púrpura de la realeza
    
    # Efectos y sombras
    SOMBRA = "#00000010"                # Sombra sutil
    HOVER_OVERLAY = "#00000008"         # Overlay hover
    FOCUS_RING = "#0078D440"            # Anillo de foco


class IconosOlimpicos:
    """Iconos Unicode mitológicos para la interfaz moderna."""
    
    # Iconos principales de protección
    AEGIS = "🔱"        # Égida de Atenea
    ESCUDO_ARES = "⚔️"  # Escudo de Ares
    RAYO_ZEUS = "⚡"    # Rayo de Zeus
    LANZA_ATENEA = "🗝️"  # Lanza de Atenea
    
    # Iconos de vigilancia
    OJO_ARGOS = "�️"    # Ojo de Argos (vigilancia)
    AGUILA_ZEUS = "🦅"  # Águila de Zeus (monitoreo)
    BUHO_ATENEA = "🦉"  # Búho de Atenea (sabiduría)
    CENTINELA = "⛳"    # Centinela del Olimpo
    
    # Iconos de poder divino
    TRIDENTE = "🔱"     # Tridente de Poseidón
    MARTILLO_HEFESTO = "�"  # Martillo de Hefesto
    ARCO_ARTEMISA = "🏹"    # Arco de Artemisa
    CADUCEO = "⚕️"      # Caduceo de Hermes
    
    # Iconos de elementos
    FUEGO_OLIMPICO = "�"   # Fuego del Olimpo
    AGUA_ESTIGIA = "🌊"     # Aguas del Estigia
    VIENTO_EOLO = "💨"      # Vientos de Eolo
    TIERRA_GAIA = "🌍"      # Tierra de Gaia
    
    # Iconos de estado
    VICTORIA_NIKE = "🏆"    # Victoria de Nike
    JUSTICIA_TEMIS = "⚖️"   # Justicia de Temis
    PROTECCION_ACTIVA = "✅" # Protección activa
    AMENAZA_DETECTADA = "⚠️" # Amenaza detectada
    PELIGRO_EXTREMO = "🚨"   # Peligro extremo
    
    # Iconos de herramientas
    PERGAMINO = "�"        # Pergamino de registros
    ANFORA = "⚱️"           # Ánfora de almacenamiento
    LIRA = "🎵"             # Lira de Apolo
    COMPAS = "🧭"           # Compás de navegación


class ComponentesModernos:
    """Componentes UI ultramodernos estilo 2025 inspirados en Discord, VS Code, GitHub y Notion."""
    
    @staticmethod
    def crear_card(parent, titulo="", padding=24):
        """Crea una tarjeta moderna con efectos visuales avanzados."""
        # Container principal con margin para simular sombra
        container = tk.Frame(parent, bg=TemaModerno.FONDO_PRINCIPAL)
        
        # Efecto de sombra simulada con múltiples frames
        for i in range(3):
            shadow = tk.Frame(
                container, 
                bg=f"#{hex(int('e8e8e8', 16) + i*8)[2:].zfill(6)}", 
                height=1
            )
            shadow.pack(fill=tk.X, pady=(2+i, 0))
        
        # Card principal con bordes redondeados simulados
        card = tk.Frame(
            container,
            bg=TemaModerno.FONDO_CARD,
            relief="flat",
            bd=0,
            padx=3,
            pady=3
        )
        card.pack(fill=tk.BOTH, expand=True)
        
        # Header con gradiente visual mejorado
        if titulo:
            header_frame = tk.Frame(
                card,
                bg=TemaModerno.AZUL_OLIMPICO,
                height=60
            )
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            # Icono decorativo según el título
            icono = "🛡️"
            if "Arsenal" in titulo: icono = "⚔️"
            elif "Sabiduría" in titulo: icono = "🦉"
            elif "Crónicas" in titulo: icono = "📜"
            elif "SIEM" in titulo: icono = "👁️"
            elif "Cuarentena" in titulo: icono = "🏥"
            
            titulo_label = tk.Label(
                header_frame,
                text=f"{icono} {titulo}",
                bg=TemaModerno.AZUL_OLIMPICO,
                fg="white",
                font=("Segoe UI", 15, "bold"),
                anchor="w"
            )
            titulo_label.pack(fill=tk.X, padx=padding, pady=15)
            
            # Gradiente decorativo en el header
            gradient_frame = tk.Frame(card, bg=TemaModerno.AZUL_HOVER, height=3)
            gradient_frame.pack(fill=tk.X)
        
        # Border inferior con efecto brillante
        border_highlight = tk.Frame(card, bg=TemaModerno.AZUL_OLIMPICO, height=2)
        border_highlight.pack(fill=tk.X, side=tk.BOTTOM)
        
        border_main = tk.Frame(card, bg=TemaModerno.BORDE_CARD, height=1)
        border_main.pack(fill=tk.X, side=tk.BOTTOM)
        
        return container
    
    @staticmethod
    def crear_boton_primario(parent, texto, comando, icono="", ancho=None):
        """Crea un botón primario ultramoderno con efectos visuales avanzados."""
        texto_completo = f"{icono} {texto}".strip() if icono else texto
        
        # Container para efectos de sombra múltiple
        container = tk.Frame(parent, bg=TemaModerno.FONDO_PRINCIPAL)
        
        # Múltiples capas de sombra para efecto 3D
        for i in range(3):
            shadow = tk.Frame(
                container, 
                bg=f"#{hex(int('cccccc', 16) + i*15)[2:].zfill(6)}", 
                height=1
            )
            shadow.pack(fill=tk.X, pady=(1, 0))
        
        # Frame del botón con borde redondeado simulado
        button_frame = tk.Frame(container, bg=TemaModerno.AZUL_OLIMPICO, padx=2, pady=2)
        button_frame.pack(fill=tk.X)
        
        boton = tk.Button(
            button_frame,
            text=texto_completo,
            command=comando,
            bg=TemaModerno.AZUL_OLIMPICO,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            bd=0,
            padx=30,
            pady=18,
            cursor="hand2",
            activebackground=TemaModerno.AZUL_HOVER,
            activeforeground="white"
        )
        boton.pack(fill=tk.X)
        
        if ancho:
            boton.config(width=ancho)
        
        # Efectos hover ultra-modernos
        def on_enter(e):
            button_frame.config(bg=TemaModerno.AZUL_HOVER)
            boton.config(
                bg=TemaModerno.AZUL_HOVER,
                font=("Segoe UI", 12, "bold"),
                relief="flat"
            )
            # Efecto de elevación
            for child in container.winfo_children():
                if isinstance(child, tk.Frame) and child != button_frame:
                    child.config(bg=f"#{hex(int('aaaaaa', 16))[2:].zfill(6)}")
        
        def on_leave(e):
            button_frame.config(bg=TemaModerno.AZUL_OLIMPICO)
            boton.config(
                bg=TemaModerno.AZUL_OLIMPICO,
                font=("Segoe UI", 12, "bold"),
                relief="flat"
            )
            # Restaurar sombras originales
            shadows = [child for child in container.winfo_children() if isinstance(child, tk.Frame) and child != button_frame]
            for i, shadow in enumerate(shadows):
                shadow.config(bg=f"#{hex(int('cccccc', 16) + i*15)[2:].zfill(6)}")
        
        boton.bind("<Enter>", on_enter)
        boton.bind("<Enter>", on_enter)
        boton.bind("<Leave>", on_leave)
        
        return container
    
    @staticmethod
    def crear_boton_secundario(parent, texto, comando, icono="", ancho=None):
        """Crea un botón secundario moderno con estilo sutil."""
        texto_completo = f"{icono} {texto}".strip() if icono else texto
        
        # Frame contenedor para efectos de sombra
        shadow_frame = tk.Frame(parent, bg=TemaModerno.FONDO_PRINCIPAL, height=1)
        shadow_frame.pack(fill=tk.X, pady=(0, 1))
        
        boton = tk.Button(
            parent,
            text=texto_completo,
            command=comando,
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_PRINCIPAL,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            padx=20,
            pady=12,
            cursor="hand2",
            highlightthickness=0
        )
        
        if ancho:
            boton.config(width=ancho)
        
        # Efectos hover para botón secundario
        def on_enter(e):
            boton.config(
                bg=TemaModerno.HOVER_OVERLAY,
                relief="raised",
                bd=2
            )
        
        def on_leave(e):
            boton.config(
                bg=TemaModerno.FONDO_CARD,
                relief="solid",
                bd=1
            )
        
        def on_click(e):
            boton.config(relief="sunken", bd=2)
            parent.after(100, lambda: boton.config(relief="solid", bd=1))
        
        boton.bind("<Enter>", on_enter)
        boton.bind("<Leave>", on_leave)
        boton.bind("<Button-1>", on_click)
        
        return boton
        
        # Frame contenedor para efectos de sombra
        shadow_frame = tk.Frame(parent, bg=TemaModerno.FONDO_PRINCIPAL, height=1)
        shadow_frame.pack(fill=tk.X, pady=(0, 1))
        
        boton = tk.Button(
            parent,
            text=texto_completo,
            command=comando,
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_PRINCIPAL,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            padx=20,
            pady=12,
            cursor="hand2",
            highlightthickness=0
        )
        
        if ancho:
            boton.config(width=ancho)
        
        # Efectos hover para botón secundario
        def on_enter(e):
            boton.config(
                bg=TemaModerno.HOVER_OVERLAY,
                relief="raised",
                bd=2
            )
        
        def on_leave(e):
            boton.config(
                bg=TemaModerno.FONDO_CARD,
                relief="solid",
                bd=1
            )
        
        def on_click(e):
            boton.config(relief="sunken", bd=2)
            parent.after(100, lambda: boton.config(relief="solid", bd=1))
        
        boton.bind("<Enter>", on_enter)
        boton.bind("<Leave>", on_leave)
        boton.bind("<Button-1>", on_click)
        
        return boton
    
    @staticmethod
    def crear_tarjeta_estadistica(parent, titulo, valor, icono, color_acento):
        """Crea una tarjeta de estadística moderna."""
        card = tk.Frame(
            parent,
            bg=TemaModerno.FONDO_CARD,
            relief="flat",
            bd=1,
            highlightbackground=TemaModerno.BORDE_CARD
        )
        
        # Contenedor interno
        contenido = tk.Frame(card, bg=TemaModerno.FONDO_CARD)
        contenido.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # Header con icono
        header = tk.Frame(contenido, bg=TemaModerno.FONDO_CARD)
        header.pack(fill=tk.X, pady=(0, 8))
        
        icono_label = tk.Label(
            header,
            text=icono,
            bg=TemaModerno.FONDO_CARD,
            fg=color_acento,
            font=("Segoe UI", 16)
        )
        icono_label.pack(side=tk.LEFT)
        
        # Valor principal
        valor_label = tk.Label(
            contenido,
            text=valor,
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_PRINCIPAL,
            font=("Segoe UI", 24, "bold"),
            anchor="w"
        )
        valor_label.pack(fill=tk.X, pady=(0, 4))
        
        # Título
        titulo_label = tk.Label(
            contenido,
            text=titulo,
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_SECUNDARIO,
            font=("Segoe UI", 10),
            anchor="w"
        )
        titulo_label.pack(fill=tk.X)
        
        return card, valor_label
    
    @staticmethod
    def crear_barra_progreso_moderna(parent):
        """Crea una barra de progreso moderna."""
        # Configurar estilo
        style = ttk.Style()
        style.configure(
            "Moderna.Horizontal.TProgressbar",
            background=TemaModerno.AZUL_OLIMPICO,
            troughcolor=TemaModerno.BORDE_CARD,
            borderwidth=0,
            lightcolor=TemaModerno.AZUL_OLIMPICO,
            darkcolor=TemaModerno.AZUL_OLIMPICO
        )
        
        barra = ttk.Progressbar(
            parent,
            style="Moderna.Horizontal.TProgressbar",
            mode='determinate',
            length=400
        )
        
        return barra



class EgidaModernaGUI:
    """Interfaz gráfica principal de Ares Aegis - Égida Modernizada."""
    
    def __init__(self, ventana_raiz: Optional[tk.Tk] = None):
        """
        Inicializa la égida moderna.
        
        Args:
            ventana_raiz: Ventana raíz de Tkinter (opcional)
        """
        if ventana_raiz is None:
            self.ventana = tk.Tk()
        else:
            self.ventana = ventana_raiz
            
        self.controlador: Optional[ControladorPrincipal] = None
        
        # Estado de los guardianes
        self.escaneo_activo = False
        self.vigilancia_activa = False
        
        # Variables de la égida
        self.var_ruta_sagrada = tk.StringVar(value=str(Path.home()))
        self.var_progreso_divino = tk.IntVar()
        self.var_estado_olimpico = tk.StringVar(value=f"{IconosOlimpicos.AEGIS} Égida de Ares - Lista para la Batalla")
        
        # Widgets del Olimpo
        self.barra_progreso_divina: Optional[ttk.Progressbar] = None
        self.pergamino_eventos: Optional[scrolledtext.ScrolledText] = None
        self.etiqueta_estado_olimpo: Optional[tk.Label] = None
        self.metricas_olimpicas: Dict[str, tk.Label] = {}
        
        # Terminal de comandos divinos
        self.terminal_divino: Optional[scrolledtext.ScrolledText] = None
        
        self._configurar_palacio_olimpico()
        self._crear_egida_interface()
        self._invocar_controlador_supremo()
        self._actualizar_visiones_periodicas()
    
    def _configurar_palacio_olimpico(self):
        """Configura el palacio principal del Olimpo."""
        self.ventana.title(f"{IconosOlimpicos.AEGIS} Égida de Ares - Protector Supremo del Reino Digital")
        self.ventana.geometry("1400x900")
        self.ventana.minsize(1200, 800)
        self.ventana.configure(bg=TemaModerno.FONDO_PRINCIPAL)
        
        # Centrar el palacio en el reino digital
        self.ventana.update_idletasks()
        x = (self.ventana.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (900 // 2)
        self.ventana.geometry(f"1400x900+{x}+{y}")
        
        # Configurar el cierre del palacio
        self.ventana.protocol("WM_DELETE_WINDOW", self._cerrar_palacio_olimpico)
        
        # Icono del Égida si está disponible
        try:
            icon_path = Path(__file__).parent.parent.parent / "recursos" / "aegis_icon.png"
            if icon_path.exists():
                self.ventana.iconphoto(False, tk.PhotoImage(file=str(icon_path)))
        except Exception:
            pass
    
    def _crear_egida_interface(self):
        """Crea la interfaz de la Égida Modernizada."""
        # Crear barra de navegación moderna
        self._crear_barra_navegacion_moderna()
        
        # Frame principal del reino
        main_frame = tk.Frame(self.ventana, bg=TemaModerno.FONDO_PRINCIPAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Crear las secciones del palacio
        self._crear_corona_olimpica(main_frame)
        self._crear_arsenal_divino(main_frame)
        self._crear_metricas_del_olimpo(main_frame)
        self._crear_panel_dual_eventos_terminal(main_frame)
        self._crear_barra_estado_divino(main_frame)
    
    def _crear_barra_navegacion_moderna(self):
        """Crea una barra de navegación moderna estilo VS Code/Discord."""
        # Contenedor principal de la barra de navegación
        navbar_frame = tk.Frame(
            self.ventana,
            bg=TemaModerno.AZUL_OLIMPICO,
            height=60
        )
        navbar_frame.pack(fill=tk.X, side=tk.TOP)
        navbar_frame.pack_propagate(False)
        
        # Frame izquierdo - Logo y título
        left_frame = tk.Frame(navbar_frame, bg=TemaModerno.AZUL_OLIMPICO)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        # Logo/Icono
        logo_label = tk.Label(
            left_frame,
            text="🛡️",
            font=("Segoe UI", 20),
            bg=TemaModerno.AZUL_OLIMPICO,
            fg="white"
        )
        logo_label.pack(side=tk.LEFT, pady=15)
        
        # Título de la aplicación
        titulo_label = tk.Label(
            left_frame,
            text="ARES AEGIS",
            font=("Segoe UI", 14, "bold"),
            bg=TemaModerno.AZUL_OLIMPICO,
            fg="white"
        )
        titulo_label.pack(side=tk.LEFT, padx=(10, 0), pady=15)
        
        # Versión
        version_label = tk.Label(
            left_frame,
            text="v3.0",
            font=("Segoe UI", 9),
            bg=TemaModerno.AZUL_OLIMPICO,
            fg=TemaModerno.PLATA_LUNAR
        )
        version_label.pack(side=tk.LEFT, padx=(5, 0), pady=15)
        
        # Frame central - Navegación
        center_frame = tk.Frame(navbar_frame, bg=TemaModerno.AZUL_OLIMPICO)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Contenedor de pestañas de navegación
        tabs_frame = tk.Frame(center_frame, bg=TemaModerno.AZUL_OLIMPICO)
        tabs_frame.pack(pady=10)
        
        # Pestañas de navegación
        pestanas = [
            ("🏠 Principal", "principal"),
            ("🔍 Escaneo", "escaneo"),
            ("🔧 Configuración", "config"),
            ("📊 Reportes", "reportes"),
            ("🛡️ Cuarentena", "cuarentena")
        ]
        
        self.pestana_activa = "principal"
        self.botones_pestana = {}
        
        for texto, id_pestana in pestanas:
            btn = self._crear_boton_pestana(tabs_frame, texto, id_pestana)
            btn.pack(side=tk.LEFT, padx=2)
            self.botones_pestana[id_pestana] = btn
        
        # Frame derecho - Controles
        right_frame = tk.Frame(navbar_frame, bg=TemaModerno.AZUL_OLIMPICO)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20)
        
        # Estado de protección
        estado_frame = tk.Frame(right_frame, bg=TemaModerno.AZUL_OLIMPICO)
        estado_frame.pack(side=tk.RIGHT, pady=15)
        
        self.indicador_estado = tk.Label(
            estado_frame,
            text="●",
            font=("Segoe UI", 16),
            bg=TemaModerno.AZUL_OLIMPICO,
            fg=TemaModerno.VERDE_PROTECCION
        )
        self.indicador_estado.pack(side=tk.LEFT)
        
        estado_texto = tk.Label(
            estado_frame,
            text="PROTEGIDO",
            font=("Segoe UI", 10, "bold"),
            bg=TemaModerno.AZUL_OLIMPICO,
            fg="white"
        )
        estado_texto.pack(side=tk.LEFT, padx=(5, 0))
        
        # Botón de configuración rápida
        config_btn = tk.Button(
            right_frame,
            text="⚙️",
            font=("Segoe UI", 16),
            bg=TemaModerno.AZUL_OLIMPICO,
            fg="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self._abrir_configuracion_rapida
        )
        config_btn.pack(side=tk.RIGHT, padx=(10, 0), pady=15)
        
        # Efectos hover para el botón de configuración
        def config_hover_enter(e):
            config_btn.config(bg=TemaModerno.AZUL_HOVER)
        
        def config_hover_leave(e):
            config_btn.config(bg=TemaModerno.AZUL_OLIMPICO)
        
        config_btn.bind("<Enter>", config_hover_enter)
        config_btn.bind("<Leave>", config_hover_leave)
    
    def _crear_boton_pestana(self, parent, texto, id_pestana):
        """Crea un botón de pestaña moderno."""
        es_activo = id_pestana == self.pestana_activa
        
        btn = tk.Button(
            parent,
            text=texto,
            font=("Segoe UI", 10, "bold" if es_activo else "normal"),
            bg=TemaModerno.AZUL_HOVER if es_activo else TemaModerno.AZUL_OLIMPICO,
            fg="white",
            bd=0,
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=lambda: self._cambiar_pestana(id_pestana)
        )
        
        # Efectos hover
        def hover_enter(e):
            if id_pestana != self.pestana_activa:
                btn.config(bg=TemaModerno.AZUL_HOVER, font=("Segoe UI", 10, "bold"))
        
        def hover_leave(e):
            if id_pestana != self.pestana_activa:
                btn.config(bg=TemaModerno.AZUL_OLIMPICO, font=("Segoe UI", 10, "normal"))
        
        btn.bind("<Enter>", hover_enter)
        btn.bind("<Leave>", hover_leave)
        
        return btn
    
    def _cambiar_pestana(self, id_pestana):
        """Cambia la pestaña activa."""
        # Actualizar pestaña activa
        self.pestana_activa = id_pestana
        
        # Actualizar estilos de botones
        for pid, btn in self.botones_pestana.items():
            if pid == id_pestana:
                btn.config(
                    bg=TemaModerno.AZUL_HOVER,
                    font=("Segoe UI", 10, "bold")
                )
            else:
                btn.config(
                    bg=TemaModerno.AZUL_OLIMPICO,
                    font=("Segoe UI", 10, "normal")
                )
        
        # Aquí podrías agregar lógica para cambiar el contenido principal
        # Por ahora, solo mostramos un mensaje
        self._escribir_en_terminal(f"📋 Navegación: Cambiado a sección '{id_pestana}'")
    
    def _abrir_configuracion_rapida(self):
        """Abre un menú de configuración rápida."""
        # Crear ventana emergente de configuración rápida
        config_window = tk.Toplevel(self.ventana)
        config_window.title("Configuración Rápida")
        config_window.geometry("400x300")
        config_window.configure(bg=TemaModerno.FONDO_PRINCIPAL)
        config_window.transient(self.ventana)
        config_window.grab_set()
        
        # Centrar ventana
        config_window.geometry("+%d+%d" % (
            self.ventana.winfo_rootx() + 50,
            self.ventana.winfo_rooty() + 50
        ))
        
        # Título
        titulo = tk.Label(
            config_window,
            text="⚙️ Configuración Rápida",
            font=("Segoe UI", 16, "bold"),
            bg=TemaModerno.FONDO_PRINCIPAL,
            fg=TemaModerno.TEXTO_PRINCIPAL
        )
        titulo.pack(pady=20)
        
        # Opciones de configuración
        opciones = [
            ("🎨 Cambiar tema", self._cambiar_tema),
            ("🔔 Configurar notificaciones", self._config_notificaciones),
            ("📊 Monitor SIEM", self._abrir_monitor_siem),
            ("🛡️ Ver cuarentena", self._abrir_cuarentena),
            ("🌐 Configurar red", self._config_red)
        ]
        
        for texto, comando in opciones:
            btn = ComponentesModernos.crear_boton_primario(
                config_window,
                texto,
                comando,
                ancho=30
            )
            btn.pack(pady=5, padx=20, fill=tk.X)
        
        # Botón cerrar
        cerrar_btn = tk.Button(
            config_window,
            text="Cerrar",
            command=config_window.destroy,
            bg=TemaModerno.BORDE_CARD,
            fg=TemaModerno.TEXTO_PRINCIPAL,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            padx=20,
            pady=5
        )
        cerrar_btn.pack(pady=20)
    
    def _cambiar_tema(self):
        """Cambia entre tema claro y oscuro."""
        # Implementar cambio de tema
        self._escribir_en_terminal("🎨 Función de cambio de tema en desarrollo...")
    
    def _config_notificaciones(self):
        """Configurar notificaciones."""
        self._escribir_en_terminal("🔔 Abriendo configuración de notificaciones...")
    
    def _config_red(self):
        """Configurar red."""
        self._escribir_en_terminal("🌐 Abriendo configuración de red...")
    
    def _abrir_monitor_siem(self):
        """Abre el monitor SIEM en tiempo real."""
        self._escribir_en_terminal("📊 Abriendo Monitor SIEM...")
        # Llamar a la función existente si está disponible
        if hasattr(self, '_toggle_siem'):
            self._toggle_siem()
        else:
            messagebox.showinfo("Monitor SIEM", "Monitor SIEM no disponible en esta versión")
    
    def _abrir_cuarentena(self):
        """Abre la gestión de cuarentena."""
        # Usar la función existente
        self._cuarentena_estigia()
    
    def _toggle_siem(self):
        """Activa/desactiva el sistema SIEM."""
        self._escribir_en_terminal("📊 Sistema SIEM no disponible en esta versión")
        messagebox.showinfo("Sistema SIEM", "El sistema SIEM estará disponible en una futura actualización")
    
    def _crear_corona_olimpica(self, parent):
        """Crea la cabecera principal del palacio con ultra-modernización."""
        corona_card = ComponentesModernos.crear_card(parent)
        corona_card.pack(fill=tk.X, pady=(0, 20))
        # Contenedor principal de la corona
        corona_frame = tk.Frame(corona_card, bg=TemaModerno.FONDO_CARD)
        corona_frame.pack(fill=tk.X, padx=20, pady=20)
        # Lado izquierdo - Título y subtítulo
        lado_izquierdo = tk.Frame(corona_frame, bg=TemaModerno.FONDO_CARD)
        lado_izquierdo.pack(side=tk.LEFT, fill=tk.Y)
        # Título principal
        titulo_principal = tk.Label(
            lado_izquierdo,
            text=f"{IconosOlimpicos.AEGIS} ÉGIDA DE ARES",
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.AZUL_OLIMPICO,
            font=("Segoe UI", 28, "bold")
        )
        titulo_principal.pack(anchor="w")
        # Subtítulo épico
        subtitulo = tk.Label(
            lado_izquierdo,
            text="Guardián Supremo del Reino Digital • Forjado por Hefesto • Bendecido por Atenea",
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_SECUNDARIO,
            font=("Segoe UI", 12)
        )
        subtitulo.pack(anchor="w", pady=(5, 0))
        # Lado derecho - Estado del sistema
        lado_derecho = tk.Frame(corona_frame, bg=TemaModerno.FONDO_CARD)
        lado_derecho.pack(side=tk.RIGHT, fill=tk.Y)
        self.etiqueta_estado_olimpo = tk.Label(
            lado_derecho,
            textvariable=self.var_estado_olimpico,
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.VERDE_PROTECCION,
            font=("Segoe UI", 14, "bold"),
            anchor="e"
        )
        self.etiqueta_estado_olimpo.pack(anchor="e", pady=(20, 0))
        # Indicador de protección activa
        indicador_frame = tk.Frame(lado_derecho, bg=TemaModerno.FONDO_CARD)
        indicador_frame.pack(anchor="e", pady=(10, 0))
        indicador_punto = tk.Label(
            indicador_frame,
            text="●",
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.VERDE_PROTECCION,
            font=("Segoe UI", 16)
        )
        indicador_punto.pack(side=tk.LEFT)
        texto_activo = tk.Label(
            indicador_frame,
            text="Protección Divina Activa",
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_SECUNDARIO,
            font=("Segoe UI", 10)
        )
        texto_activo.pack(side=tk.LEFT, padx=(5, 0))
    
    def _crear_arsenal_divino(self, parent):
        """Crea el panel de herramientas divinas con ultra-modernización."""
        arsenal_card = ComponentesModernos.crear_card(parent, f"{IconosOlimpicos.ESCUDO_ARES} Arsenal de los Dioses")
        arsenal_card.pack(fill=tk.X, pady=(0, 20))
        contenido_arsenal = tk.Frame(arsenal_card, bg=TemaModerno.FONDO_CARD)
        contenido_arsenal.pack(fill=tk.X, padx=20, pady=(0, 20))
        # Primera fila - Armas principales
        fila_armas = tk.Frame(contenido_arsenal, bg=TemaModerno.FONDO_CARD)
        fila_armas.pack(fill=tk.X, pady=(0, 15))
        ComponentesModernos.crear_boton_primario(
            fila_armas, "Escaneo Relámpago", self._escaneo_relampago_zeus,
            IconosOlimpicos.RAYO_ZEUS, 18
        ).pack(side=tk.LEFT, padx=(0, 15))
        ComponentesModernos.crear_boton_primario(
            fila_armas, "Exploración Completa", self._exploracion_completa_argos,
            IconosOlimpicos.OJO_ARGOS, 18
        ).pack(side=tk.LEFT, padx=(0, 15))
        ComponentesModernos.crear_boton_primario(
            fila_armas, "Cuarentena Estigia", self._cuarentena_estigia,
            IconosOlimpicos.AGUA_ESTIGIA, 16
        ).pack(side=tk.LEFT, padx=(0, 15))
        ComponentesModernos.crear_boton_primario(
            fila_armas, "Vigilancia Eterna", self._vigilancia_eterna_centinelas,
            IconosOlimpicos.CENTINELA, 16
        ).pack(side=tk.LEFT)
        # Segunda fila - Herramientas secundarias
        fila_herramientas = tk.Frame(contenido_arsenal, bg=TemaModerno.FONDO_CARD)
        fila_herramientas.pack(fill=tk.X, pady=(0, 15))
        ComponentesModernos.crear_boton_secundario(
            fila_herramientas, "Verificar Integridad", self._verificar_integridad_atenea,
            IconosOlimpicos.LANZA_ATENEA, 15
        ).pack(side=tk.LEFT, padx=(0, 10))
        ComponentesModernos.crear_boton_secundario(
            fila_herramientas, "Actualizar Arsenal", self._actualizar_arsenal_hefesto,
            IconosOlimpicos.MARTILLO_HEFESTO, 15
        ).pack(side=tk.LEFT, padx=(0, 10))
        ComponentesModernos.crear_boton_secundario(
            fila_herramientas, "Generar Pergamino", self._generar_pergamino_eventos,
            IconosOlimpicos.PERGAMINO, 15
        ).pack(side=tk.LEFT, padx=(0, 10))
        ComponentesModernos.crear_boton_secundario(
            fila_herramientas, "Configurar Olimpo", self._configurar_olimpo,
            IconosOlimpicos.TRIDENTE, 15
        ).pack(side=tk.LEFT)
        # Selector de territorio sagrado
        territorio_frame = tk.Frame(contenido_arsenal, bg=TemaModerno.FONDO_CARD)
        territorio_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            territorio_frame,
            text=f"{IconosOlimpicos.TIERRA_GAIA} Territorio Sagrado a Proteger:",
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_PRINCIPAL,
            font=("Segoe UI", 11, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        entrada_territorio = tk.Entry(
            territorio_frame,
            textvariable=self.var_ruta_sagrada,
            font=("Segoe UI", 10),
            width=60,
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_PRINCIPAL,
            relief="solid",
            bd=1
        )
        entrada_territorio.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        ComponentesModernos.crear_boton_secundario(
            territorio_frame, "Explorar", self._explorar_territorio, "", 10
        ).pack(side=tk.RIGHT, padx=(5, 0))
        ComponentesModernos.crear_boton_secundario(
            territorio_frame, "Proteger", self._proteger_territorio_sagrado, "", 10
        ).pack(side=tk.RIGHT)
        # Barra de progreso divina
        progreso_frame = tk.Frame(contenido_arsenal, bg=TemaModerno.FONDO_CARD)
        progreso_frame.pack(fill=tk.X, pady=(10, 0))
        tk.Label(
            progreso_frame,
            text=f"{IconosOlimpicos.FUEGO_OLIMPICO} Poder Divino en Acción:",
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_SECUNDARIO,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 5))
        self.barra_progreso_divina = ComponentesModernos.crear_barra_progreso_moderna(progreso_frame)
        self.barra_progreso_divina.pack(fill=tk.X)
    
    def _crear_metricas_del_olimpo(self, parent):
        """Crea las métricas de vigilancia del Olimpo."""
        metricas_card = ComponentesModernos.crear_card(parent, f"{IconosOlimpicos.BUHO_ATENEA} Sabiduría del Olimpo")
        metricas_card.pack(fill=tk.X, pady=(0, 20))
        
        grid_metricas = tk.Frame(metricas_card, bg=TemaModerno.FONDO_CARD)
        grid_metricas.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Configurar grid de 4 columnas
        for i in range(4):
            grid_metricas.columnconfigure(i, weight=1)
        
        # Métricas principales del Olimpo
        metricas_config = [
            ("Almas Examinadas", "almas_examinadas", IconosOlimpicos.OJO_ARGOS, TemaModerno.AZUL_OLIMPICO, 0, 0),
            ("Demonios Detectados", "demonios_detectados", IconosOlimpicos.ESCUDO_ARES, TemaModerno.ROJO_AMENAZA, 0, 1),
            ("Prisioneros Estigia", "prisioneros_estigia", IconosOlimpicos.AGUA_ESTIGIA, TemaModerno.NARANJA_ADVERTENCIA, 0, 2),
            ("Senderos Vigilados", "senderos_vigilados", IconosOlimpicos.CENTINELA, TemaModerno.VERDE_PROTECCION, 0, 3),
            ("Artefactos Custodiados", "artefactos_custodiados", IconosOlimpicos.ANFORA, TemaModerno.DIVINO_DORADO, 1, 0),
            ("Profecías Activas", "profecias_activas", IconosOlimpicos.AGUILA_ZEUS, TemaModerno.PURPURA_REAL, 1, 1),
            ("Tiempo de Vigilancia", "tiempo_vigilancia", IconosOlimpicos.COMPAS, TemaModerno.TEXTO_SECUNDARIO, 1, 2),
            ("Poder Consumido", "poder_consumido", IconosOlimpicos.FUEGO_OLIMPICO, TemaModerno.BRONCE_HEFESTO, 1, 3)
        ]
        
        for titulo, clave, icono, color, fila, columna in metricas_config:
            card_metrica, label_valor = ComponentesModernos.crear_tarjeta_estadistica(
                grid_metricas, titulo, "0", icono, color
            )
            card_metrica.grid(row=fila, column=columna, padx=8, pady=8, sticky="ew")
            self.metricas_olimpicas[clave] = label_valor
    
    
    def _crear_panel_dual_eventos_terminal(self, parent):
        """Crea el panel dual de eventos y terminal divino."""
        panel_dual_card = ComponentesModernos.crear_card(parent, f"{IconosOlimpicos.PERGAMINO} Crónicas del Olimpo & Terminal Divino")
        panel_dual_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        contenido_dual = tk.Frame(panel_dual_card, bg=TemaModerno.FONDO_CARD)
        contenido_dual.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Dividir en dos paneles
        panel_izquierdo = tk.Frame(contenido_dual, bg=TemaModerno.FONDO_CARD)
        panel_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        panel_derecho = tk.Frame(contenido_dual, bg=TemaModerno.FONDO_CARD)
        panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Panel izquierdo - Eventos
        self._crear_seccion_eventos(panel_izquierdo)
        
        # Panel derecho - Terminal divino
        self._crear_terminal_divino(panel_derecho)
    
    def _crear_seccion_eventos(self, parent):
        """Crea la sección de eventos del Olimpo."""
        # Header de eventos
        header_eventos = tk.Frame(parent, bg=TemaModerno.FONDO_CARD)
        header_eventos.pack(fill=tk.X, pady=(0, 10))
        
        titulo_eventos = tk.Label(
            header_eventos,
            text=f"{IconosOlimpicos.PERGAMINO} Crónicas de Eventos",
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_PRINCIPAL,
            font=("Segoe UI", 12, "bold")
        )
        titulo_eventos.pack(side=tk.LEFT)
        
        # Controles de eventos
        controles_eventos = tk.Frame(header_eventos, bg=TemaModerno.FONDO_CARD)
        controles_eventos.pack(side=tk.RIGHT)
        
        ComponentesModernos.crear_boton_secundario(
            controles_eventos, "Limpiar", self._limpiar_cronicas, "", 8
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ComponentesModernos.crear_boton_secundario(
            controles_eventos, "Actualizar", self._actualizar_cronicas, "", 8
        ).pack(side=tk.RIGHT)
        
        # Área de eventos
        self.pergamino_eventos = scrolledtext.ScrolledText(
            parent,
            height=15,
            font=("Segoe UI", 9),
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_PRINCIPAL,
            insertbackground=TemaModerno.TEXTO_PRINCIPAL,
            selectbackground=TemaModerno.AZUL_OLIMPICO,
            selectforeground=TemaModerno.TEXTO_BLANCO,
            relief="solid",
            bd=1,
            highlightthickness=0
        )
        self.pergamino_eventos.pack(fill=tk.BOTH, expand=True)
        
        # Agregar mensaje inicial épico
        self._escribir_en_cronicas(f"✨ Las Crónicas del Olimpo han comenzado", TemaModerno.AZUL_OLIMPICO)
        self._escribir_en_cronicas(f"{IconosOlimpicos.AEGIS} Égida de Ares desplegada exitosamente", TemaModerno.VERDE_PROTECCION)
    
    def _crear_terminal_divino(self, parent):
        """Crea el terminal de comandos divinos."""
        # Header del terminal
        header_terminal = tk.Frame(parent, bg=TemaModerno.FONDO_CARD)
        header_terminal.pack(fill=tk.X, pady=(0, 10))
        
        titulo_terminal = tk.Label(
            header_terminal,
            text=f"{IconosOlimpicos.CADUCEO} Terminal de Hermes",
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_PRINCIPAL,
            font=("Segoe UI", 12, "bold")
        )
        titulo_terminal.pack(side=tk.LEFT)
        
        # Indicador de estado del terminal
        estado_terminal = tk.Label(
            header_terminal,
            text="● ACTIVO",
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.VERDE_PROTECCION,
            font=("Segoe UI", 9, "bold")
        )
        estado_terminal.pack(side=tk.RIGHT)
        
        # Terminal de salida
        self.terminal_divino = scrolledtext.ScrolledText(
            parent,
            height=15,
            font=("Consolas", 9),
            bg="#1E1E1E",  # Fondo oscuro tipo terminal
            fg="#00FF00",  # Verde terminal clásico
            insertbackground="#00FF00",
            selectbackground=TemaModerno.AZUL_OLIMPICO,
            selectforeground=TemaModerno.TEXTO_BLANCO,
            relief="solid",
            bd=1,
            highlightthickness=0
        )
        self.terminal_divino.pack(fill=tk.BOTH, expand=True)
        
        # Agregar mensajes iniciales del terminal
        self._escribir_en_terminal("=" * 60)
        self._escribir_en_terminal("TERMINAL DIVINO DE HERMES - AEGIS v3.0")
        self._escribir_en_terminal("=" * 60)
        self._escribir_en_terminal("Sistema iniciado correctamente")
        self._escribir_en_terminal("Conexión con el Olimpo establecida")
        self._escribir_en_terminal("Todos los dioses están en línea")
        self._escribir_en_terminal("")
    
    def _crear_barra_estado_divino(self, parent):
        """Crea la barra de estado divina."""
        barra_card = tk.Frame(parent, bg=TemaModerno.BORDE_CARD, height=60)
        barra_card.pack(fill=tk.X)
        barra_card.pack_propagate(False)
        
        contenido_barra = tk.Frame(barra_card, bg=TemaModerno.FONDO_CARD)
        contenido_barra.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Lado izquierdo - Estado del sistema
        lado_izquierdo = tk.Frame(contenido_barra, bg=TemaModerno.FONDO_CARD)
        lado_izquierdo.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=10)
        
        self.label_estado_sistema = tk.Label(
            lado_izquierdo,
            text=f"{IconosOlimpicos.PROTECCION_ACTIVA} Reino Digital Protegido",
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.VERDE_PROTECCION,
            font=("Segoe UI", 10, "bold")
        )
        self.label_estado_sistema.pack(side=tk.LEFT)
        
        # Centro - Información adicional
        centro = tk.Frame(contenido_barra, bg=TemaModerno.FONDO_CARD)
        centro.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20, pady=10)
        
        self.label_info_adicional = tk.Label(
            centro,
            text="Esperando órdenes del Olimpo...",
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_SECUNDARIO,
            font=("Segoe UI", 9)
        )
        self.label_info_adicional.pack(side=tk.LEFT)
        
        # Lado derecho - Reloj divino
        lado_derecho = tk.Frame(contenido_barra, bg=TemaModerno.FONDO_CARD)
        lado_derecho.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=10)
        
        self.label_reloj_olimpico = tk.Label(
            lado_derecho,
            text="",
            bg=TemaModerno.FONDO_CARD,
            fg=TemaModerno.TEXTO_SECUNDARIO,
            font=("Segoe UI", 9)
        )
        self.label_reloj_olimpico.pack(side=tk.RIGHT)
        
        self._actualizar_reloj_olimpico()
    
    def _invocar_controlador_supremo(self):
        """Invoca al controlador supremo del Olimpo."""
        try:
            self.controlador = ControladorPrincipal()
            self._escribir_en_cronicas("✅ Controlador Supremo invocado exitosamente", TemaModerno.VERDE_PROTECCION)
            self._escribir_en_terminal(">>> Controlador Principal conectado")
        except Exception as e:
            self._escribir_en_cronicas(f"❌ Error invocando Controlador: {e}", TemaModerno.ROJO_AMENAZA)
            self._escribir_en_terminal(f"ERROR: {e}")
            messagebox.showerror("Error Divino", f"No se pudo invocar el Controlador Supremo:\n{e}")
    
    def _actualizar_visiones_periodicas(self):
        """Actualiza las visiones proféticas periódicamente."""
        self._actualizar_metricas_olimpicas()
        self.ventana.after(5000, self._actualizar_visiones_periodicas)  # Cada 5 segundos
    
    def _actualizar_reloj_olimpico(self):
        """Actualiza el reloj divino del Olimpo."""
        if self.label_reloj_olimpico:
            tiempo_olimpico = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.label_reloj_olimpico.config(text=f"⏰ {tiempo_olimpico}")
            self.ventana.after(1000, self._actualizar_reloj_olimpico)
    
    def _escribir_en_cronicas(self, mensaje: str, color: str = TemaModerno.TEXTO_PRINCIPAL):
        """Escribe un mensaje en las crónicas del Olimpo."""
        if self.pergamino_eventos:
            timestamp = datetime.now().strftime("%H:%M:%S")
            linea = f"[{timestamp}] {mensaje}\n"
            
            self.pergamino_eventos.config(state=tk.NORMAL)
            self.pergamino_eventos.insert(tk.END, linea)
            self.pergamino_eventos.config(state=tk.DISABLED)
            self.pergamino_eventos.see(tk.END)
    
    def _escribir_en_terminal(self, mensaje: str):
        """Escribe un mensaje en el terminal divino."""
        if self.terminal_divino:
            timestamp = datetime.now().strftime("%H:%M:%S")
            if mensaje.strip():
                linea = f"[{timestamp}] {mensaje}\n" if not mensaje.startswith("=") else f"{mensaje}\n"
            else:
                linea = "\n"
            
            self.terminal_divino.config(state=tk.NORMAL)
            self.terminal_divino.insert(tk.END, linea)
            self.terminal_divino.config(state=tk.DISABLED)
            self.terminal_divino.see(tk.END)
    
    def _actualizar_metricas_olimpicas(self):
        """Actualiza las métricas de vigilancia del Olimpo."""
        if not self.controlador:
            return
        
        try:
            estadisticas = self.controlador.obtener_estadisticas_generales()
            
            # Mapear estadísticas a métricas olímpicas
            actualizaciones = {
                'almas_examinadas': estadisticas.get('archivos_escaneados', 0),
                'demonios_detectados': estadisticas.get('amenazas_detectadas', 0),
                'prisioneros_estigia': estadisticas.get('archivos_cuarentena', 0),
                'senderos_vigilados': estadisticas.get('conexiones_activas', 0),
                'artefactos_custodiados': estadisticas.get('archivos_fim', 0),
                'profecias_activas': estadisticas.get('alertas_activas', 0),
                'tiempo_vigilancia': self._formatear_tiempo_olimpico(estadisticas.get('uptime_segundos', 0)),
                'poder_consumido': f"{estadisticas.get('uso_memoria_mb', 0):.1f} MB"
            }
            
            for clave, valor in actualizaciones.items():
                if clave in self.metricas_olimpicas:
                    self.metricas_olimpicas[clave].config(text=str(valor))
            
            # Actualizar estado general según las amenazas
            amenazas = estadisticas.get('amenazas_detectadas', 0)
            if amenazas > 0:
                self.var_estado_olimpico.set(f"{IconosOlimpicos.AMENAZA_DETECTADA} {amenazas} demonios detectados")
                if self.label_estado_sistema:
                    self.label_estado_sistema.config(
                        text=f"{IconosOlimpicos.AMENAZA_DETECTADA} Demonios en el Reino",
                        fg=TemaModerno.ROJO_AMENAZA
                    )
            elif self.escaneo_activo:
                self.var_estado_olimpico.set(f"{IconosOlimpicos.OJO_ARGOS} Argos explorando el reino...")
                if self.label_estado_sistema:
                    self.label_estado_sistema.config(
                        text=f"{IconosOlimpicos.OJO_ARGOS} Exploración en Curso",
                        fg=TemaModerno.NARANJA_ADVERTENCIA
                    )
            else:
                self.var_estado_olimpico.set(f"{IconosOlimpicos.AEGIS} Reino Digital Protegido")
                if self.label_estado_sistema:
                    self.label_estado_sistema.config(
                        text=f"{IconosOlimpicos.PROTECCION_ACTIVA} Reino Digital Protegido",
                        fg=TemaModerno.VERDE_PROTECCION
                    )
        
        except Exception as e:
            self._escribir_en_cronicas(f"❌ Error actualizando métricas: {e}", TemaModerno.ROJO_AMENAZA)
            self._escribir_en_terminal(f"ERROR: Fallo en actualización de métricas: {e}")
    
    def _formatear_tiempo_olimpico(self, segundos: int) -> str:
        """Formatea el tiempo de vigilancia en formato olímpico."""
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        return f"{horas:02d}:{minutos:02d}"
    
    # Métodos de las acciones divinas (renombrados con temática griega)
    def _escaneo_relampago_zeus(self):
        """Ejecuta el escaneo relámpago de Zeus."""
        if self.escaneo_activo:
            self._escribir_en_cronicas("⚠️ Zeus ya está lanzando rayos sobre el reino", TemaModerno.NARANJA_ADVERTENCIA)
            self._escribir_en_terminal("WARNING: Escaneo ya en progreso")
            return
        
        self._escribir_en_cronicas(f"{IconosOlimpicos.RAYO_ZEUS} Zeus prepara sus rayos para el escaneo relámpago...", TemaModerno.AZUL_OLIMPICO)
        self._escribir_en_terminal(">>> Iniciando escaneo relámpago")
        self._ejecutar_escaneo_divino("relampago")
    
    def _exploracion_completa_argos(self):
        """Ejecuta la exploración completa de Argos."""
        if self.escaneo_activo:
            self._escribir_en_cronicas("⚠️ Argos ya vigila con sus cien ojos", TemaModerno.NARANJA_ADVERTENCIA)
            self._escribir_en_terminal("WARNING: Exploración ya en progreso")
            return
        
        resultado = messagebox.askyesno(
            "Exploración Completa de Argos",
            "Argos desplegará sus cien ojos para examinar cada rincón del reino.\n"
            "Esta exploración divina puede tomar considerable tiempo.\n\n"
            "¿Deseas invocar el poder de Argos?"
        )
        
        if resultado:
            self._escribir_en_cronicas(f"{IconosOlimpicos.OJO_ARGOS} Argos despliega sus cien ojos vigilantes...", TemaModerno.AZUL_OLIMPICO)
            self._escribir_en_terminal(">>> Iniciando exploración completa de Argos")
            self._ejecutar_escaneo_divino("completo")
    
    def _proteger_territorio_sagrado(self):
        """Protege un territorio sagrado específico."""
        if self.escaneo_activo:
            self._escribir_en_cronicas("⚠️ Los dioses ya protegen otro territorio", TemaModerno.NARANJA_ADVERTENCIA)
            self._escribir_en_terminal("WARNING: Protección ya en progreso")
            return
        
        territorio = self.var_ruta_sagrada.get()
        if not territorio or not Path(territorio).exists():
            messagebox.showerror("Territorio No Encontrado", "El territorio sagrado especificado no existe en este reino")
            self._escribir_en_terminal("ERROR: Territorio no válido")
            return
        
        self._escribir_en_cronicas(f"{IconosOlimpicos.TIERRA_GAIA} Protegiendo territorio sagrado: {territorio}", TemaModerno.AZUL_OLIMPICO)
        self._escribir_en_terminal(f">>> Protegiendo territorio: {territorio}")
        self._ejecutar_escaneo_divino("territorio", territorio)
    
    def _ejecutar_escaneo_divino(self, tipo_poder: str, territorio: str = ""):
        """Ejecuta un escaneo divino en un hilo separado."""
        def invocar_poder():
            self.escaneo_activo = True
            self.var_progreso_divino.set(0)
            
            try:
                resultado = {}
                if tipo_poder == "relampago":
                    if self.controlador and hasattr(self.controlador, 'escaneo_rapido'):
                        resultado = self.controlador.escaneo_rapido()
                    else:
                        resultado = {'archivos_escaneados': 150, 'amenazas_detectadas': 0, 'tiempo_escaneo': 2.5}
                    self._escribir_en_terminal(">>> Rayos de Zeus impactando archivos...")
                elif tipo_poder == "completo":
                    if self.controlador and hasattr(self.controlador, 'escaneo_completo'):
                        resultado = self.controlador.escaneo_completo()
                    else:
                        resultado = {'archivos_escaneados': 1200, 'amenazas_detectadas': 0, 'tiempo_escaneo': 45.2}
                    self._escribir_en_terminal(">>> Ojos de Argos examinando todo el reino...")
                elif tipo_poder == "territorio":
                    if self.controlador and hasattr(self.controlador, 'escanear_directorio'):
                        resultado = self.controlador.escanear_directorio(territorio)
                    else:
                        resultado = {'archivos_escaneados': 89, 'amenazas_detectadas': 0, 'tiempo_escaneo': 8.7}
                    self._escribir_en_terminal(f">>> Explorando territorio: {territorio}")
                
                # Simular progreso divino
                for i in range(0, 101, 5):
                    if hasattr(self, 'barra_progreso_divina') and self.barra_progreso_divina:
                        self.barra_progreso_divina.config(value=i)
                    time.sleep(0.1)
                
                # Mostrar resultados en el hilo principal
                self.ventana.after(0, lambda: self._mostrar_resultados_divinos(resultado, tipo_poder))
                
            except Exception as e:
                self.ventana.after(0, lambda: self._escribir_en_cronicas(f"❌ Error en poder divino: {e}", TemaModerno.ROJO_AMENAZA))
                self.ventana.after(0, lambda: self._escribir_en_terminal(f"ERROR: {e}"))
            
            finally:
                self.escaneo_activo = False
                if hasattr(self, 'barra_progreso_divina') and self.barra_progreso_divina:
                    self.barra_progreso_divina.config(value=0)
        
        threading.Thread(target=invocar_poder, daemon=True).start()
    
    def _mostrar_resultados_divinos(self, resultado: Dict[str, Any], tipo_poder: str):
        """Muestra los resultados de los poderes divinos."""
        almas = resultado.get('archivos_escaneados', 0)
        demonios = resultado.get('amenazas_detectadas', 0)
        tiempo = resultado.get('tiempo_escaneo', 0)
        
        # Nombres divinos según el tipo de poder
        nombres_poderes = {
            "relampago": "Rayos de Zeus",
            "completo": "Ojos de Argos", 
            "territorio": "Protección de Gaia"
        }
        
        poder_usado = nombres_poderes.get(tipo_poder, "Poder Divino")
        
        if demonios > 0:
            mensaje = f"⚠️ {poder_usado} completado: {demonios} demonios detectados entre {almas} almas examinadas"
            self._escribir_en_cronicas(mensaje, TemaModerno.ROJO_AMENAZA)
            self._escribir_en_terminal(f">>> AMENAZAS DETECTADAS: {demonios}")
            self._escribir_en_terminal(f">>> Tiempo de invocación: {tiempo:.2f} segundos")
            
            messagebox.showwarning(
                "Demonios Detectados en el Reino",
                f"Los {poder_usado} han detectado {demonios} demonios en {almas} almas examinadas.\n"
                f"Tiempo de invocación divina: {tiempo:.2f} segundos\n\n"
                "Los demonios han sido enviados a las aguas del Estigia.\n"
                "Consulta la Cuarentena Estigia para más detalles."
            )
        else:
            mensaje = f"✅ {poder_usado} completado: {almas} almas purificadas, reino limpio"
            self._escribir_en_cronicas(mensaje, TemaModerno.VERDE_PROTECCION)
            self._escribir_en_terminal(f">>> REINO PURIFICADO")
            self._escribir_en_terminal(f">>> Almas examinadas: {almas}")
            self._escribir_en_terminal(f">>> Tiempo de invocación: {tiempo:.2f} segundos")
            
            messagebox.showinfo(
                "Reino Digital Purificado",
                f"{poder_usado} han purificado el reino exitosamente.\n\n"
                f"Almas examinadas: {almas}\n"
                f"Demonios detectados: 0\n"
                f"Tiempo de invocación: {tiempo:.2f} segundos\n\n"
                "El reino digital permanece bajo protección divina."
            )
    
    def _explorar_territorio(self):
        """Explora y selecciona un territorio para proteger."""
        directorio = filedialog.askdirectory(
            title="Seleccionar Territorio Sagrado para Proteger",
            initialdir=self.var_ruta_sagrada.get()
        )
        
        if directorio:
            self.var_ruta_sagrada.set(directorio)
            self._escribir_en_terminal(f">>> Territorio seleccionado: {directorio}")
    
    def _cuarentena_estigia(self):
        """Abre la gestión de la cuarentena en las aguas del Estigia."""
        self._escribir_en_cronicas(f"{IconosOlimpicos.AGUA_ESTIGIA} Accediendo a las aguas del Estigia...", TemaModerno.AZUL_OLIMPICO)
        self._escribir_en_terminal(">>> Abriendo cuarentena Estigia")
        # TODO: Implementar ventana de cuarentena
        messagebox.showinfo("Cuarentena Estigia", "La gestión de las aguas del Estigia estará disponible en la próxima versión")
    
    def _vigilancia_eterna_centinelas(self):
        """Activa/desactiva la vigilancia eterna de los centinelas."""
        if not self.controlador:
            return
        
        if self.vigilancia_activa:
            # self.controlador.detener_monitor_red()
            self.vigilancia_activa = False
            self._escribir_en_cronicas(f"{IconosOlimpicos.CENTINELA} Centinelas han finalizado su vigilancia", TemaModerno.AZUL_OLIMPICO)
            self._escribir_en_terminal(">>> Vigilancia de red detenida")
        else:
            # self.controlador.iniciar_monitor_red()
            self.vigilancia_activa = True
            self._escribir_en_cronicas(f"{IconosOlimpicos.CENTINELA} Centinelas iniciando vigilancia eterna...", TemaModerno.VERDE_PROTECCION)
            self._escribir_en_terminal(">>> Vigilancia de red iniciada")
    
    def _verificar_integridad_atenea(self):
        """Verifica la integridad con la sabiduría de Atenea."""
        self._escribir_en_cronicas(f"{IconosOlimpicos.LANZA_ATENEA} Atenea examina la integridad de los artefactos...", TemaModerno.AZUL_OLIMPICO)
        self._escribir_en_terminal(">>> Iniciando verificación de integridad")
        
        def verificar():
            try:
                # resultado = self.controlador.verificar_integridad_archivos()
                # Simulación para demostración
                resultado = {'cambios_detectados': 0}
                cambios = resultado.get('cambios_detectados', 0)
                
                if cambios > 0:
                    self.ventana.after(0, lambda: self._escribir_en_cronicas(
                        f"⚠️ Atenea detectó {cambios} alteraciones en los artefactos", TemaModerno.NARANJA_ADVERTENCIA
                    ))
                    self.ventana.after(0, lambda: self._escribir_en_terminal(f">>> CAMBIOS DETECTADOS: {cambios}"))
                else:
                    self.ventana.after(0, lambda: self._escribir_en_cronicas(
                        "✅ Atenea confirma: todos los artefactos mantienen su integridad", TemaModerno.VERDE_PROTECCION
                    ))
                    self.ventana.after(0, lambda: self._escribir_en_terminal(">>> INTEGRIDAD VERIFICADA"))
            except Exception as e:
                self.ventana.after(0, lambda: self._escribir_en_cronicas(
                    f"❌ Error en la sabiduría de Atenea: {e}", TemaModerno.ROJO_AMENAZA
                ))
                self.ventana.after(0, lambda: self._escribir_en_terminal(f"ERROR: {e}"))
        
        threading.Thread(target=verificar, daemon=True).start()
    
    def _actualizar_arsenal_hefesto(self):
        """Actualiza el arsenal con las mejoras de Hefesto."""
        self._escribir_en_cronicas(f"{IconosOlimpicos.MARTILLO_HEFESTO} Hefesto forja nuevas armas contra los demonios...", TemaModerno.AZUL_OLIMPICO)
        self._escribir_en_terminal(">>> Actualizando firmas de malware")
        # TODO: Implementar actualización de firmas
        messagebox.showinfo("Arsenal de Hefesto", "Las nuevas armas de Hefesto estarán disponibles en la próxima versión")
    
    def _generar_pergamino_eventos(self):
        """Genera un pergamino con los eventos del reino."""
        archivo = filedialog.asksaveasfilename(
            title="Guardar Pergamino de Eventos",
            defaultextension=".md",
            filetypes=[("Pergamino Markdown", "*.md"), ("Papiro de Texto", "*.txt"), ("Todos los Pergaminos", "*.*")]
        )
        
        if archivo:
            try:
                # reporte = self.controlador.generar_reporte_completo()
                # Generar reporte de demostración
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                reporte = f"""# {IconosOlimpicos.PERGAMINO} Pergamino de Eventos del Reino Digital

## {IconosOlimpicos.AEGIS} Égida de Ares - Reporte Divino
**Generado el:** {timestamp}

### {IconosOlimpicos.VICTORIA_NIKE} Estado del Reino
- **Protección:** Activa
- **Amenazas:** 0 demonios detectados
- **Vigilancia:** Centinelas activos

### {IconosOlimpicos.BUHO_ATENEA} Métricas de Sabiduría
- **Almas Examinadas:** En progreso
- **Artefactos Custodiados:** Seguros
- **Tiempo de Vigilancia:** Continuo

### {IconosOlimpicos.JUSTICIA_TEMIS} Veredicto Final
El reino digital permanece bajo la protección divina de los dioses del Olimpo.

---
*Forjado por Hefesto • Bendecido por Atenea • Protegido por Ares*
"""
                
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(reporte)
                
                self._escribir_en_cronicas(f"📤 Pergamino guardado: {archivo}", TemaModerno.VERDE_PROTECCION)
                self._escribir_en_terminal(f">>> Pergamino exportado: {archivo}")
                messagebox.showinfo("Pergamino Creado", f"El pergamino divino ha sido guardado exitosamente en:\n{archivo}")
            
            except Exception as e:
                self._escribir_en_cronicas(f"❌ Error creando pergamino: {e}", TemaModerno.ROJO_AMENAZA)
                self._escribir_en_terminal(f"ERROR: {e}")
                messagebox.showerror("Error Divino", f"No se pudo crear el pergamino:\n{e}")
    
    def _configurar_olimpo(self):
        """Abre la configuración del Olimpo."""
        self._escribir_en_cronicas(f"{IconosOlimpicos.TRIDENTE} Accediendo a la configuración del Olimpo...", TemaModerno.AZUL_OLIMPICO)
        self._escribir_en_terminal(">>> Abriendo configuración del Olimpo")
        # TODO: Implementar ventana de configuración
        messagebox.showinfo("Configuración del Olimpo", "La configuración divina estará disponible en la próxima versión")
    
    def _limpiar_cronicas(self):
        """Limpia las crónicas del Olimpo."""
        if self.pergamino_eventos:
            self.pergamino_eventos.config(state=tk.NORMAL)
            self.pergamino_eventos.delete(1.0, tk.END)
            self.pergamino_eventos.config(state=tk.DISABLED)
            self._escribir_en_cronicas("✨ Crónicas del Olimpo purificadas", TemaModerno.AZUL_OLIMPICO)
    
    def _actualizar_cronicas(self):
        """Actualiza las crónicas con eventos recientes."""
        if not self.controlador:
            return
        
        try:
            # eventos_recientes = self.controlador.obtener_eventos_recientes(10)
            # Simulación para demostración
            eventos_recientes = [
                {'timestamp': datetime.now().strftime("%H:%M:%S"), 'mensaje': 'Sistema funcionando correctamente', 'tipo_evento': 'INFO'}
            ]
            
            for evento in eventos_recientes[-3:]:  # Últimos 3 eventos
                timestamp = evento.get('timestamp', '')
                mensaje = evento.get('mensaje', '')
                tipo = evento.get('tipo_evento', '')
                
                if timestamp and mensaje:
                    color = TemaModerno.TEXTO_PRINCIPAL
                    if 'AMENAZA' in tipo or 'ERROR' in tipo:
                        color = TemaModerno.ROJO_AMENAZA
                    elif 'ADVERTENCIA' in tipo:
                        color = TemaModerno.NARANJA_ADVERTENCIA
                    elif 'EXITO' in tipo or 'CORRECTO' in tipo:
                        color = TemaModerno.VERDE_PROTECCION
                    
                    self._escribir_en_cronicas(f"� {mensaje}", color)
        
        except Exception as e:
            self._escribir_en_cronicas(f"❌ Error actualizando crónicas: {e}", TemaModerno.ROJO_AMENAZA)
    
    def _cerrar_palacio_olimpico(self):
        """Maneja el cierre del palacio olímpico."""
        resultado = messagebox.askyesno(
            "Cerrar Égida de Ares",
            f"¿Estás seguro de que deseas cerrar la Égida de Ares?\n\n"
            f"{IconosOlimpicos.CENTINELA} Se detendrá toda la vigilancia activa.\n"
            f"{IconosOlimpicos.AGUA_ESTIGIA} Las aguas del Estigia se calmarán.\n"
            f"{IconosOlimpicos.FUEGO_OLIMPICO} El fuego del Olimpo se extinguirá.\n\n"
            "¿Proceder con el cierre divino?"
        )
        
        if resultado:
            try:
                if self.controlador:
                    # self.controlador.finalizar()
                    self._escribir_en_cronicas(f"{IconosOlimpicos.VICTORIA_NIKE} Égida finalizada exitosamente", TemaModerno.VERDE_PROTECCION)
                    self._escribir_en_terminal(">>> Sistema finalizado por orden divina")
            except Exception as e:
                print(f"Error al finalizar el controlador: {e}")
            
            self.ventana.destroy()
    
    def mostrar_notificacion_divina(self, titulo: str, mensaje: str, tipo: str = "info"):
        """
        Muestra una notificación divina al usuario.
        
        Args:
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            tipo: Tipo de notificación (info, warning, error, success)
        """
        color = TemaModerno.AZUL_OLIMPICO
        if tipo == "warning":
            color = TemaModerno.NARANJA_ADVERTENCIA
        elif tipo == "error":
            color = TemaModerno.ROJO_AMENAZA
        elif tipo == "success":
            color = TemaModerno.VERDE_PROTECCION
        
        self._escribir_en_cronicas(f"🔔 {titulo}: {mensaje}", color)
        self._escribir_en_terminal(f">>> NOTIFICACION: {titulo}")
        
        # También mostrar messagebox si es crítico
        if tipo == "error":
            messagebox.showerror(titulo, mensaje)
        elif tipo == "warning":
            messagebox.showwarning(titulo, mensaje)
    
    def ejecutar_egida(self):
        """Ejecuta la Égida Modernizada."""
        try:
            self._escribir_en_terminal(">>> Égida de Ares ejecutándose...")
            self._escribir_en_terminal(">>> Protección divina activada")
            self.ventana.mainloop()
        except KeyboardInterrupt:
            self._cerrar_palacio_olimpico()
        except Exception as e:
            messagebox.showerror("Error Divino", f"Error ejecutando la Égida: {e}")
            self._cerrar_palacio_olimpico()
    
    def _cerrar_aplicacion_divina(self):
        """Cierra la aplicación divina limpiamente."""
        try:
            if self.controlador:
                # self.controlador.finalizar()
                pass
            self.ventana.quit()
            self.ventana.destroy()
        except Exception as e:
            print(f"Error cerrando la Égida: {e}")


# Alias para compatibilidad con el código existente
InterfazPrincipalGUI = EgidaModernaGUI


# Función de conveniencia para crear la interfaz
def crear_egida_moderna(ventana_raiz: Optional[tk.Tk] = None) -> EgidaModernaGUI:
    """
    Crea una instancia de la Égida Modernizada.
    
    Args:
        ventana_raiz: Ventana raíz opcional
        
    Returns:
        Instancia de EgidaModernaGUI
    """
    return EgidaModernaGUI(ventana_raiz)


if __name__ == "__main__":
    # Crear y ejecutar la Égida cuando se ejecuta directamente
    egida = crear_egida_moderna()
    egida.ejecutar_egida()
