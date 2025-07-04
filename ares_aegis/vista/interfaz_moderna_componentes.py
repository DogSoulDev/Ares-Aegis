#!/usr/bin/env python3
"""
Componentes UI Modernos para Ares Aegis
Sistema de Componentes Reutilizables con UX/UI Profesional

🎨 COMPONENTES Y TEMAS
"""

import tkinter as tk
from tkinter import ttk
import logging

class ComponentesModernos:
    """Biblioteca de componentes UI modernos reutilizables"""
    
    # 🎨 PALETA DE COLORES MODERNA
    COLORES = {
        "primario": "#1a73e8",
        "primario_hover": "#1557b0",
        "secundario": "#6c757d", 
        "secundario_hover": "#545b62",
        "exito": "#00c851",
        "exito_hover": "#00a843",
        "peligro": "#dc3545",
        "peligro_hover": "#c82333",
        "advertencia": "#ffc107",
        "advertencia_hover": "#e0a800",
        "info": "#17a2b8",
        "info_hover": "#138496",
        
        # Fondos
        "bg_principal": "#0d1421",
        "bg_secundario": "#16213e",
        "bg_card": "#1a202c",
        "bg_card_hover": "#2d3748",
        
        # Textos
        "texto_primario": "#ffffff",
        "texto_secundario": "#8a92b2",
        "texto_muted": "#4a5568",
        
        # Bordes
        "borde_principal": "#2d3748",
        "borde_hover": "#4a5568",
        
        # Estados
        "activo": "#00c851",
        "inactivo": "#dc3545",
        "advertencia_estado": "#ffc107",
        "procesando": "#1a73e8"
    }
    
    @staticmethod
    def crear_card_moderna(parent, titulo="", descripcion="", bg=None):
        """Crear una card moderna con bordes redondeados simulados"""
        if bg is None:
            bg = ComponentesModernos.COLORES["bg_card"]
            
        # Container principal con padding
        card_container = tk.Frame(parent, bg=parent.cget('bg'))
        
        # Card principal
        card_frame = tk.Frame(card_container, bg=bg, relief="flat", bd=0)
        card_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Header de la card si se proporciona título
        if titulo:
            header_frame = tk.Frame(card_frame, bg=bg)
            header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            title_label = tk.Label(
                header_frame,
                text=titulo,
                font=("Segoe UI", 14, "bold"),
                bg=bg,
                fg=ComponentesModernos.COLORES["texto_primario"]
            )
            title_label.pack(side="left")
            
            if descripcion:
                desc_label = tk.Label(
                    header_frame,
                    text=descripcion,
                    font=("Segoe UI", 10),
                    bg=bg,
                    fg=ComponentesModernos.COLORES["texto_secundario"]
                )
                desc_label.pack(side="right")
        
        # Content área
        content_frame = tk.Frame(card_frame, bg=bg)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        return card_container, content_frame
    
    @staticmethod
    def crear_boton_moderno(parent, texto, comando, estilo="primario", tamaño="normal"):
        """Crear botón con estilo moderno"""
        colores = ComponentesModernos.COLORES
        
        estilos = {
            "primario": {"bg": colores["primario"], "fg": colores["texto_primario"], "hover": colores["primario_hover"]},
            "secundario": {"bg": colores["secundario"], "fg": colores["texto_primario"], "hover": colores["secundario_hover"]},
            "exito": {"bg": colores["exito"], "fg": colores["texto_primario"], "hover": colores["exito_hover"]},
            "peligro": {"bg": colores["peligro"], "fg": colores["texto_primario"], "hover": colores["peligro_hover"]},
            "advertencia": {"bg": colores["advertencia"], "fg": "#212529", "hover": colores["advertencia_hover"]},
            "info": {"bg": colores["info"], "fg": colores["texto_primario"], "hover": colores["info_hover"]},
            "outline": {"bg": colores["bg_secundario"], "fg": colores["primario"], "hover": colores["bg_card_hover"]}
        }
        
        tamaños = {
            "pequeño": {"font": ("Segoe UI", 9, "bold"), "padx": 12, "pady": 6},
            "normal": {"font": ("Segoe UI", 10, "bold"), "padx": 20, "pady": 10},
            "grande": {"font": ("Segoe UI", 12, "bold"), "padx": 30, "pady": 15}
        }
        
        estilo_actual = estilos.get(estilo, estilos["primario"])
        tamaño_actual = tamaños.get(tamaño, tamaños["normal"])
        
        btn = tk.Button(
            parent,
            text=texto,
            command=comando,
            bg=estilo_actual["bg"],
            fg=estilo_actual["fg"],
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            **tamaño_actual
        )
        
        # Efectos hover
        def on_enter(e):
            btn.config(bg=estilo_actual["hover"])
        
        def on_leave(e):
            btn.config(bg=estilo_actual["bg"])
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    @staticmethod
    def crear_metrica_card(parent, titulo, valor, icono, color=None, cambio=None):
        """Crear card de métrica estilo dashboard"""
        if color is None:
            color = ComponentesModernos.COLORES["primario"]
            
        card_container, content = ComponentesModernos.crear_card_moderna(parent)
        
        # Layout de la métrica
        metric_frame = tk.Frame(content, bg=content.cget('bg'))
        metric_frame.pack(fill="both", expand=True)
        
        # Icono y valor principal
        top_frame = tk.Frame(metric_frame, bg=content.cget('bg'))
        top_frame.pack(fill="x", pady=(0, 10))
        
        icon_label = tk.Label(
            top_frame,
            text=icono,
            font=("Arial", 24),
            bg=content.cget('bg'),
            fg=color
        )
        icon_label.pack(side="left")
        
        value_label = tk.Label(
            top_frame,
            text=valor,
            font=("Segoe UI", 24, "bold"),
            bg=content.cget('bg'),
            fg=ComponentesModernos.COLORES["texto_primario"]
        )
        value_label.pack(side="right")
        
        # Título
        title_label = tk.Label(
            metric_frame,
            text=titulo,
            font=("Segoe UI", 11),
            bg=content.cget('bg'),
            fg=ComponentesModernos.COLORES["texto_secundario"]
        )
        title_label.pack(anchor="w")
        
        # Cambio/tendencia
        if cambio:
            change_color = ComponentesModernos.COLORES["exito"] if cambio.startswith("+") else ComponentesModernos.COLORES["peligro"]
            change_label = tk.Label(
                metric_frame,
                text=f"↗ {cambio} desde ayer" if cambio.startswith("+") else f"↘ {cambio} desde ayer",
                font=("Segoe UI", 9),
                bg=content.cget('bg'),
                fg=change_color
            )
            change_label.pack(anchor="w", pady=(5, 0))
        
        return card_container
    
    @staticmethod
    def crear_input_moderno(parent, placeholder="", tipo="texto", bg=None):
        """Crear input moderno con placeholder"""
        if bg is None:
            bg = ComponentesModernos.COLORES["bg_card"]
        
        # Container del input
        input_container = tk.Frame(parent, bg=bg)
        
        # Crear widget según tipo
        if tipo == "texto":
            input_widget = tk.Entry(
                input_container,
                bg=ComponentesModernos.COLORES["bg_secundario"],
                fg=ComponentesModernos.COLORES["texto_primario"],
                insertbackground=ComponentesModernos.COLORES["primario"],
                font=("Segoe UI", 11),
                relief="flat",
                borderwidth=1,
                bd=0
            )
        else:  # texto_multilinea
            input_widget = tk.Text(
                input_container,
                bg=ComponentesModernos.COLORES["bg_secundario"],
                fg=ComponentesModernos.COLORES["texto_primario"],
                insertbackground=ComponentesModernos.COLORES["primario"],
                font=("Segoe UI", 11),
                relief="flat",
                borderwidth=1,
                bd=0,
                wrap="word"
            )
        
        input_widget.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Placeholder effect solo para Entry
        if placeholder and tipo == "texto" and isinstance(input_widget, tk.Entry):
            def add_placeholder():
                current_value = input_widget.get()
                if current_value == "":
                    input_widget.insert(0, placeholder)
                    input_widget.config(fg=ComponentesModernos.COLORES["texto_muted"])
            
            def remove_placeholder(event):
                current_value = input_widget.get()
                if current_value == placeholder:
                    input_widget.delete(0, "end")
                    input_widget.config(fg=ComponentesModernos.COLORES["texto_primario"])
            
            def readd_placeholder(event):
                current_value = input_widget.get()
                if current_value == "":
                    add_placeholder()
            
            input_widget.bind("<FocusIn>", remove_placeholder)
            input_widget.bind("<FocusOut>", readd_placeholder)
            add_placeholder()
        
        return input_container, input_widget
    
    @staticmethod
    def crear_lista_moderna(parent, items=[], on_select=None):
        """Crear lista moderna con scrollbar"""
        # Frame container
        list_frame = tk.Frame(parent, bg=parent.cget('bg'))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Listbox
        listbox = tk.Listbox(
            list_frame,
            bg=ComponentesModernos.COLORES["bg_secundario"],
            fg=ComponentesModernos.COLORES["texto_primario"],
            selectbackground=ComponentesModernos.COLORES["primario"],
            font=("Segoe UI", 10),
            yscrollcommand=scrollbar.set,
            relief="flat",
            borderwidth=0,
            activestyle="none"
        )
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Cargar items
        for item in items:
            listbox.insert(tk.END, item)
        
        # Evento de selección
        if on_select:
            listbox.bind("<<ListboxSelect>>", on_select)
        
        return list_frame, listbox
    
    @staticmethod
    def crear_progress_moderna(parent, valor=0, maximo=100, texto=""):
        """Crear barra de progreso moderna"""
        # Container
        progress_container = tk.Frame(parent, bg=parent.cget('bg'))
        
        # Variable para el label de texto
        texto_label = None
        
        # Texto de progreso
        if texto:
            texto_label = tk.Label(
                progress_container,
                text=texto,
                font=("Segoe UI", 10),
                bg=parent.cget('bg'),
                fg=ComponentesModernos.COLORES["texto_secundario"]
            )
            texto_label.pack(anchor="w", pady=(0, 5))
        
        # Frame de la barra
        bar_frame = tk.Frame(
            progress_container,
            bg=ComponentesModernos.COLORES["bg_secundario"],
            height=8,
            relief="flat",
            bd=0
        )
        bar_frame.pack(fill="x", pady=2)
        bar_frame.pack_propagate(False)
        
        # Barra de progreso
        porcentaje = (valor / maximo) * 100 if maximo > 0 else 0
        progress_bar = tk.Frame(
            bar_frame,
            bg=ComponentesModernos.COLORES["primario"],
            height=8
        )
        progress_bar.place(x=0, y=0, relwidth=porcentaje/100, relheight=1)
        
        # Función para actualizar
        def actualizar_progreso(nuevo_valor, nuevo_texto=""):
            nonlocal porcentaje
            porcentaje = (nuevo_valor / maximo) * 100 if maximo > 0 else 0
            progress_bar.place(relwidth=max(0, min(1, porcentaje/100)))
            if nuevo_texto and texto_label is not None:
                texto_label.config(text=nuevo_texto)
        
        return progress_container, actualizar_progreso
    
    @staticmethod
    def crear_toggle_switch(parent, texto="", inicial=False, callback=None):
        """Crear switch/toggle moderno"""
        # Container
        toggle_container = tk.Frame(parent, bg=parent.cget('bg'))
        
        # Variable de estado
        estado = tk.BooleanVar(value=inicial)
        
        # Label del texto
        if texto:
            texto_label = tk.Label(
                toggle_container,
                text=texto,
                font=("Segoe UI", 11),
                bg=parent.cget('bg'),
                fg=ComponentesModernos.COLORES["texto_primario"]
            )
            texto_label.pack(side="left", padx=(0, 15))
        
        # Frame del switch
        switch_frame = tk.Frame(
            toggle_container,
            bg=ComponentesModernos.COLORES["exito"] if inicial else ComponentesModernos.COLORES["bg_secundario"],
            width=50,
            height=25,
            relief="flat",
            bd=0
        )
        switch_frame.pack(side="right")
        switch_frame.pack_propagate(False)
        
        # Circulo del switch
        circulo = tk.Frame(
            switch_frame,
            bg=ComponentesModernos.COLORES["texto_primario"],
            width=21,
            height=21,
            relief="flat",
            bd=0
        )
        circulo.place(x=27 if inicial else 2, y=2)
        
        def toggle():
            nuevo_estado = not estado.get()
            estado.set(nuevo_estado)
            
            # Actualizar colores
            color_bg = ComponentesModernos.COLORES["exito"] if nuevo_estado else ComponentesModernos.COLORES["bg_secundario"]
            switch_frame.config(bg=color_bg)
            
            # Animar posición del círculo
            nueva_x = 27 if nuevo_estado else 2
            circulo.place(x=nueva_x)
            
            # Callback
            if callback:
                callback(nuevo_estado)
        
        # Bind clicks
        switch_frame.bind("<Button-1>", lambda e: toggle())
        circulo.bind("<Button-1>", lambda e: toggle())
        
        return toggle_container, estado, toggle
    
    @staticmethod
    def crear_badge(parent, texto, color="primario"):
        """Crear badge/etiqueta moderna"""
        colores = ComponentesModernos.COLORES
        
        color_map = {
            "primario": colores["primario"],
            "exito": colores["exito"],
            "peligro": colores["peligro"],
            "advertencia": colores["advertencia"],
            "info": colores["info"],
            "secundario": colores["secundario"]
        }
        
        bg_color = color_map.get(color, colores["primario"])
        
        badge = tk.Label(
            parent,
            text=texto,
            font=("Segoe UI", 8, "bold"),
            bg=bg_color,
            fg=colores["texto_primario"],
            padx=8,
            pady=2
        )
        
        return badge
    
    @staticmethod
    def crear_separador(parent, orientacion="horizontal"):
        """Crear separador visual"""
        if orientacion == "horizontal":
            separador = tk.Frame(
                parent,
                bg=ComponentesModernos.COLORES["borde_principal"],
                height=1
            )
            separador.pack(fill="x", pady=10)
        else:
            separador = tk.Frame(
                parent,
                bg=ComponentesModernos.COLORES["borde_principal"],
                width=1
            )
            separador.pack(fill="y", padx=10)
        
        return separador


class TemasModernos:
    """Gestión de temas para la interfaz"""
    
    @staticmethod
    def aplicar_tema_oscuro():
        """Aplicar tema oscuro"""
        # Actualizar colores del tema oscuro
        ComponentesModernos.COLORES.update({
            "bg_principal": "#0d1421",
            "bg_secundario": "#16213e", 
            "bg_card": "#1a202c",
            "bg_card_hover": "#2d3748",
            "texto_primario": "#ffffff",
            "texto_secundario": "#8a92b2",
            "texto_muted": "#4a5568"
        })
    
    @staticmethod
    def aplicar_tema_claro():
        """Aplicar tema claro"""
        # Actualizar colores del tema claro
        ComponentesModernos.COLORES.update({
            "bg_principal": "#ffffff",
            "bg_secundario": "#f8f9fa",
            "bg_card": "#ffffff",
            "bg_card_hover": "#f8f9fa", 
            "texto_primario": "#212529",
            "texto_secundario": "#6c757d",
            "texto_muted": "#adb5bd"
        })
    
    @staticmethod
    def obtener_configuracion_ttk_style():
        """Obtener configuración de estilos TTK"""
        style = ttk.Style()
        
        # Configurar tema oscuro para TTK
        style.theme_use('clam')
        
        # Scrollbar
        style.configure(
            "Vertical.TScrollbar",
            background=ComponentesModernos.COLORES["bg_secundario"],
            troughcolor=ComponentesModernos.COLORES["bg_principal"],
            borderwidth=0,
            arrowcolor=ComponentesModernos.COLORES["texto_secundario"],
            darkcolor=ComponentesModernos.COLORES["bg_secundario"],
            lightcolor=ComponentesModernos.COLORES["bg_secundario"]
        )
        
        # Progressbar
        style.configure(
            "TProgressbar",
            background=ComponentesModernos.COLORES["primario"],
            troughcolor=ComponentesModernos.COLORES["bg_secundario"],
            borderwidth=0,
            lightcolor=ComponentesModernos.COLORES["primario"],
            darkcolor=ComponentesModernos.COLORES["primario"]
        )
        
        # Notebook
        style.configure(
            "TNotebook",
            background=ComponentesModernos.COLORES["bg_principal"],
            borderwidth=0
        )
        
        style.configure(
            "TNotebook.Tab",
            background=ComponentesModernos.COLORES["bg_secundario"],
            foreground=ComponentesModernos.COLORES["texto_secundario"],
            padding=[20, 10],
            borderwidth=0
        )
        
        style.map(
            "TNotebook.Tab",
            background=[("selected", ComponentesModernos.COLORES["primario"])],
            foreground=[("selected", ComponentesModernos.COLORES["texto_primario"])]
        )
        
        return style


# Inicializar tema por defecto
TemasModernos.aplicar_tema_oscuro()
