#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Sistema de Temas Modernos
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, List, Tuple, Callable, Union


class TemaClaro:
    FONDO_PRINCIPAL = "#FAFBFC"
    FONDO_SECUNDARIO = "#FFFFFF"
    FONDO_CARD = "#FFFFFF"
    BORDE = "#E1E4E8"
    
    PRIMARIO = "#0366D6"
    PRIMARIO_HOVER = "#0258C7"
    SECUNDARIO = "#6F42C1"
    
    EXITO = "#28A745"
    ADVERTENCIA = "#FFC107"
    ERROR = "#DC3545"                  # Rojo error
    INFO = "#17A2B8"                   # Azul info
    
    # Texto
    TEXTO_PRINCIPAL = "#24292E"        # Gris oscuro
    TEXTO_SECUNDARIO = "#586069"       # Gris medio
    TEXTO_MUTED = "#959DA5"            # Gris claro
    TEXTO_LINK = "#0366D6"             # Azul enlace
    
    # Efectos
    SOMBRA_SUAVE = "#E1E4E8"
    SOMBRA_MEDIA = "#D1D5DA"
    SOMBRA_FUERTE = "#BDC3C7"
    
    # Gradientes
    GRADIENTE_PRIMARIO = ["#0366D6", "#0258C7"]
    GRADIENTE_SECUNDARIO = ["#6F42C1", "#5A32A3"]
    GRADIENTE_EXITO = ["#28A745", "#20923C"]


class TemaOscuro:
    """Tema oscuro moderno inspirado en Discord, VS Code y GitHub Dark."""
    
    # Colores base
    FONDO_PRINCIPAL = "#0D1117"        # Negro GitHub Dark
    FONDO_SECUNDARIO = "#161B22"       # Gris muy oscuro
    FONDO_CARD = "#21262D"             # Gris oscuro para tarjetas
    BORDE = "#30363D"                  # Gris para bordes
    
    # Colores de acento
    PRIMARIO = "#5865F2"               # Azul Discord
    PRIMARIO_HOVER = "#4752C4"         # Azul hover
    SECUNDARIO = "#7289DA"             # Azul claro Discord
    
    # Estados
    EXITO = "#57F287"                  # Verde Discord
    ADVERTENCIA = "#FEE75C"            # Amarillo Discord
    ERROR = "#ED4245"                  # Rojo Discord
    INFO = "#5865F2"                   # Azul Discord
    
    # Texto
    TEXTO_PRINCIPAL = "#F0F6FC"        # Blanco GitHub Dark
    TEXTO_SECUNDARIO = "#8B949E"       # Gris claro
    TEXTO_MUTED = "#6E7681"            # Gris medio
    TEXTO_LINK = "#58A6FF"             # Azul claro
    
    # Efectos
    SOMBRA_SUAVE = "#0D1117"
    SOMBRA_MEDIA = "#010409"
    SOMBRA_FUERTE = "#000000"
    
    # Gradientes
    GRADIENTE_PRIMARIO = ["#5865F2", "#4752C4"]
    GRADIENTE_SECUNDARIO = ["#7289DA", "#5B6DCF"]
    GRADIENTE_EXITO = ["#57F287", "#3DDD78"]


class ComponentesModernos:
    """Componentes de interfaz ultra-modernos con efectos avanzados."""
    
    @staticmethod
    def crear_card_ultra_moderna(parent: tk.Widget, titulo: str = "", padding: int = 20) -> tuple[tk.Frame, tk.Frame]:
        """Crea una tarjeta ultra-moderna con efectos de sombra y gradientes.
        
        Returns:
            tuple: (shadow_container, content_frame)
        """
        # Contenedor principal con efecto de sombra
        shadow_container = tk.Frame(parent, bg=TemaClaro.SOMBRA_SUAVE, bd=0, relief="flat")
        
        # Capa de sombra media
        shadow_layer = tk.Frame(shadow_container, bg=TemaClaro.SOMBRA_MEDIA, bd=0, relief="flat")
        shadow_layer.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Tarjeta principal
        card = tk.Frame(
            shadow_layer,
            bg=TemaClaro.FONDO_CARD,
            bd=0,
            relief="flat",
            highlightbackground=TemaClaro.BORDE,
            highlightthickness=1
        )
        card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Contenido de la tarjeta
        content_frame = tk.Frame(card, bg=TemaClaro.FONDO_CARD)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
        
        if titulo:
            titulo_label = tk.Label(
                content_frame,
                text=titulo,
                font=("Segoe UI", 14, "bold"),
                bg=TemaClaro.FONDO_CARD,
                fg=TemaClaro.TEXTO_PRINCIPAL
            )
            titulo_label.pack(anchor="w", pady=(0, 10))
        
        # Efectos hover para la tarjeta
        def card_hover_enter(e):
            card.config(highlightbackground=TemaClaro.PRIMARIO)
            shadow_layer.config(bg=TemaClaro.SOMBRA_FUERTE)
        
        def card_hover_leave(e):
            card.config(highlightbackground=TemaClaro.BORDE)
            shadow_layer.config(bg=TemaClaro.SOMBRA_MEDIA)
        
        card.bind("<Enter>", card_hover_enter)
        card.bind("<Leave>", card_hover_leave)
        
        return shadow_container, content_frame
    
    @staticmethod
    def crear_boton_ultra_moderno(
        parent: tk.Widget,
        texto: str,
        comando: Callable,
        estilo: str = "primario",
        icono: str = "",
        ancho: Optional[int] = None
    ) -> tk.Frame:
        """Crea un botón ultra-moderno con efectos avanzados."""
        
        # Definir colores según el estilo
        if estilo == "primario":
            color_normal = TemaClaro.PRIMARIO
            color_hover = TemaClaro.PRIMARIO_HOVER
            color_texto = "#FFFFFF"
        elif estilo == "secundario":
            color_normal = TemaClaro.SECUNDARIO
            color_hover = "#5A32A3"
            color_texto = "#FFFFFF"
        elif estilo == "exito":
            color_normal = TemaClaro.EXITO
            color_hover = "#20923C"
            color_texto = "#FFFFFF"
        elif estilo == "peligro":
            color_normal = TemaClaro.ERROR
            color_hover = "#C82333"
            color_texto = "#FFFFFF"
        else:  # outline
            color_normal = TemaClaro.FONDO_CARD
            color_hover = TemaClaro.FONDO_PRINCIPAL
            color_texto = TemaClaro.TEXTO_PRINCIPAL
        
        # Contenedor con sombra
        button_container = tk.Frame(parent, bg=TemaClaro.SOMBRA_SUAVE, bd=0, relief="flat")
        
        # Capa de sombra
        shadow_frame = tk.Frame(button_container, bg=TemaClaro.SOMBRA_MEDIA, bd=0, relief="flat")
        shadow_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Texto completo del botón
        texto_completo = f"{icono} {texto}".strip()
        
        # Botón principal
        boton = tk.Button(
            shadow_frame,
            text=texto_completo,
            command=comando,
            bg=color_normal,
            fg=color_texto,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=25,
            pady=12,
            cursor="hand2",
            activebackground=color_hover,
            activeforeground=color_texto
        )
        boton.pack(fill=tk.BOTH, expand=True)
        
        if ancho:
            boton.config(width=ancho)
        
        # Efectos de animación avanzados
        def boton_hover_enter(e):
            boton.config(bg=color_hover, font=("Segoe UI", 11, "bold"))
            shadow_frame.config(bg=TemaClaro.SOMBRA_FUERTE)
            # Efecto de elevación
            button_container.pack_configure(padx=0, pady=0)
        
        def boton_hover_leave(e):
            boton.config(bg=color_normal, font=("Segoe UI", 11, "bold"))
            shadow_frame.config(bg=TemaClaro.SOMBRA_MEDIA)
            button_container.pack_configure(padx=1, pady=1)
        
        def boton_click(e):
            # Efecto de click
            boton.config(bg=color_hover)
            parent.after(100, lambda: boton.config(bg=color_normal))
        
        boton.bind("<Enter>", boton_hover_enter)
        boton.bind("<Leave>", boton_hover_leave)
        boton.bind("<Button-1>", boton_click)
        
        return button_container
    
    @staticmethod
    def crear_campo_entrada_moderno(
        parent: tk.Widget,
        placeholder: str = "",
        es_password: bool = False,
        ancho: int = 30
    ) -> tk.Frame:
        """Crea un campo de entrada moderno con efectos."""
        
        # Contenedor con borde
        entry_container = tk.Frame(
            parent,
            bg=TemaClaro.BORDE,
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground=TemaClaro.BORDE
        )
        
        # Campo de entrada
        entry = tk.Entry(
            entry_container,
            font=("Segoe UI", 11),
            bg=TemaClaro.FONDO_CARD,
            fg=TemaClaro.TEXTO_PRINCIPAL,
            bd=0,
            relief="flat",
            insertbackground=TemaClaro.PRIMARIO,
            selectbackground=TemaClaro.PRIMARIO,
            selectforeground="#FFFFFF",
            width=ancho,
            show="*" if es_password else ""
        )
        entry.pack(padx=1, pady=1)
        
        # Placeholder
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=TemaClaro.TEXTO_MUTED)
            
            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg=TemaClaro.TEXTO_PRINCIPAL)
            
            def on_focus_out(e):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg=TemaClaro.TEXTO_MUTED)
            
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
        
        # Efectos hover y focus
        def entry_focus_in(e):
            entry_container.config(highlightbackground=TemaClaro.PRIMARIO)
        
        def entry_focus_out(e):
            entry_container.config(highlightbackground=TemaClaro.BORDE)
        
        entry.bind("<FocusIn>", entry_focus_in)
        entry.bind("<FocusOut>", entry_focus_out)
        
        return entry_container
    
    @staticmethod
    def crear_progress_bar_moderna(
        parent: tk.Widget,
        valor_inicial: int = 0,
        valor_maximo: int = 100
    ) -> tk.Frame:
        """Crea una barra de progreso moderna."""
        
        # Estilo personalizado para la barra de progreso
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores modernos
        style.configure(
            "Moderna.Horizontal.TProgressbar",
            background=TemaClaro.PRIMARIO,
            troughcolor=TemaClaro.FONDO_PRINCIPAL,
            borderwidth=0,
            lightcolor=TemaClaro.PRIMARIO,
            darkcolor=TemaClaro.PRIMARIO
        )
        
        # Contenedor con sombra
        progress_container = tk.Frame(parent, bg=TemaClaro.SOMBRA_SUAVE, bd=0, relief="flat")
        
        # Barra de progreso
        progress = ttk.Progressbar(
            progress_container,
            style="Moderna.Horizontal.TProgressbar",
            mode='determinate',
            value=valor_inicial,
            maximum=valor_maximo
        )
        progress.pack(fill=tk.X, padx=1, pady=1)
        
        return progress_container
    
    @staticmethod
    def crear_tooltip_moderno(widget: tk.Widget, texto: str):
        """Crea un tooltip moderno para un widget."""
        
        def mostrar_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.configure(bg=TemaOscuro.FONDO_CARD)
            
            label = tk.Label(
                tooltip,
                text=texto,
                font=("Segoe UI", 9),
                bg=TemaOscuro.FONDO_CARD,
                fg=TemaOscuro.TEXTO_PRINCIPAL,
                padx=8,
                pady=4,
                relief="flat",
                bd=1,
                borderwidth=1
            )
            label.pack()
            
            # Posicionar tooltip
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.geometry(f"+{x}+{y}")
            
            # Auto-ocultar después de 3 segundos
            tooltip.after(3000, tooltip.destroy)
        
        widget.bind("<Enter>", mostrar_tooltip)


class EfectosAnimacion:
    """Clase para manejar efectos de animación modernos."""
    
    @staticmethod
    def animar_fade_in(widget: tk.Widget, duracion: int = 500):
        """Animación fade in para un widget."""
        alpha = 0.0
        increment = 1.0 / (duracion / 50)  # 50ms intervals
        
        def fade():
            nonlocal alpha
            if alpha < 1.0:
                alpha += increment
                # Simular transparencia cambiando colores
                widget.after(50, fade)
        
        fade()
    
    @staticmethod
    def animar_slide_in(widget: tk.Widget, direccion: str = "left", duracion: int = 300):
        """Animación slide in para un widget."""
        if direccion == "left":
            start_x = -widget.winfo_reqwidth()
            end_x = 0
        elif direccion == "right":
            start_x = widget.winfo_reqwidth()
            end_x = 0
        else:
            return
        
        frames = duracion // 20  # 20ms intervals
        increment = (end_x - start_x) / frames
        current_x = start_x
        
        def slide():
            nonlocal current_x
            if abs(current_x - end_x) > abs(increment):
                current_x += increment
                widget.place(x=current_x)
                widget.after(20, slide)
            else:
                widget.place(x=end_x)
        
        slide()
    
    @staticmethod
    def pulso_color(widget: tk.Widget, color_inicio: str, color_fin: str, duracion: int = 1000):
        """Efecto de pulso de color."""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        
        rgb_inicio = hex_to_rgb(color_inicio)
        rgb_fin = hex_to_rgb(color_fin)
        
        frames = duracion // 50  # 50ms intervals
        
        def interpolar(frame):
            if frame > frames:
                return
            
            # Interpolación lineal
            factor = frame / frames
            r = rgb_inicio[0] + (rgb_fin[0] - rgb_inicio[0]) * factor
            g = rgb_inicio[1] + (rgb_fin[1] - rgb_inicio[1]) * factor
            b = rgb_inicio[2] + (rgb_fin[2] - rgb_inicio[2]) * factor
            
            color_actual = rgb_to_hex((r, g, b))
            
            try:
                widget.config(bg=color_actual)
            except:
                pass
            
            widget.after(50, lambda: interpolar(frame + 1))
        
        interpolar(0)


# Configuración global de temas
TEMA_ACTUAL = "claro"

def obtener_tema_actual():
    """Obtiene el tema actual."""
    return TemaClaro if TEMA_ACTUAL == "claro" else TemaOscuro

def cambiar_tema(nuevo_tema: str):
    """Cambia el tema global."""
    global TEMA_ACTUAL
    TEMA_ACTUAL = nuevo_tema

def aplicar_tema_widget(widget: tk.Widget, tipo_widget: str = "frame"):
    """Aplica el tema actual a un widget."""
    tema = obtener_tema_actual()
    
    if tipo_widget == "frame":
        widget.config(bg=tema.FONDO_PRINCIPAL)
    elif tipo_widget == "label":
        widget.config(bg=tema.FONDO_PRINCIPAL, fg=tema.TEXTO_PRINCIPAL)
    elif tipo_widget == "button":
        widget.config(bg=tema.PRIMARIO, fg="#FFFFFF")
    elif tipo_widget == "entry":
        widget.config(bg=tema.FONDO_CARD, fg=tema.TEXTO_PRINCIPAL)
