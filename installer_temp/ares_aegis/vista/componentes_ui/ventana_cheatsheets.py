#!/usr/bin/env python3
"""
Ventana de Cheatsheets para Ares Aegis
Ventana modal mejorada para mostrar hojas de trucos
"""

import tkinter as tk
from tkinter import ttk
from .colores_kali import ColoresKaliLinux


class VentanaCheatsheets:
    """Ventana modal mejorada para mostrar cheatsheets con funcionalidades avanzadas"""
    
    def __init__(self, parent, contenido, titulo="Cheatsheet"):
        self.parent = parent
        self.contenido = contenido
        self.titulo = titulo
        self.ventana = None
        
        # Colores estilo Kali Linux
        self.colores = ColoresKaliLinux()
        
    def mostrar(self):
        """Mostrar ventana modal de cheatsheet"""
        if self.ventana and tk.Toplevel.winfo_exists(self.ventana):
            self.ventana.lift()
            return
        
        self.ventana = tk.Toplevel(self.parent)
        self.ventana.title(f"📚 {self.titulo} - Escudo Divino de Ciberseguridad")
        self.ventana.geometry("1200x800")
        self.ventana.configure(bg=self.colores.fondo_primario)
        
        # Hacer ventana modal
        self.ventana.transient(self.parent)
        self.ventana.grab_set()
        
        # Centrar ventana
        self._centrar_ventana()
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Configurar cierre
        self.ventana.protocol("WM_DELETE_WINDOW", self._cerrar)
    
    def _centrar_ventana(self):
        """Centrar ventana en pantalla"""
        self.ventana.update_idletasks()
        width = 1200
        height = 800
        x = (self.ventana.winfo_screenwidth() // 2) - (width // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (height // 2)
        self.ventana.geometry(f"{width}x{height}+{x}+{y}")
    
    def _crear_interfaz(self):
        """Crear interfaz de la ventana de cheatsheet"""
        # Header con título mejorado
        header_frame = tk.Frame(self.ventana, bg=self.colores.fondo_secundario, height=70)
        header_frame.pack(fill='x', padx=15, pady=15)
        header_frame.pack_propagate(False)
        
        # Título centrado con mejor diseño
        title_frame = tk.Frame(header_frame, bg=self.colores.fondo_secundario)
        title_frame.pack(expand=True, fill='both')
        
        tk.Label(title_frame,
                text=f"📚 {self.titulo}",
                font=('Consolas', 18, 'bold'),
                fg=self.colores.acento_primario,
                bg=self.colores.fondo_secundario).pack(anchor='center', expand=True)
        
        # Frame principal con notebook para categorías
        main_frame = tk.Frame(self.ventana, bg=self.colores.fondo_primario)
        main_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        if isinstance(self.contenido, dict) and 'categorias' in self.contenido:
            # Crear notebook para categorías JSON
            self._crear_interfaz_categorias(main_frame)
        else:
            # Mostrar contenido simple
            self._crear_interfaz_simple(main_frame)
        
        # Footer con controles
        self._crear_footer()
    
    def _crear_interfaz_categorias(self, parent):
        """Crear interfaz con categorías para cheatsheets JSON con estilo mejorado"""
        # Configurar estilo del notebook
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilos personalizados para Kali
        style.configure('Kali.TNotebook', 
                       background=self.colores.fondo_primario,
                       borderwidth=0)
        style.configure('Kali.TNotebook.Tab',
                       background=self.colores.fondo_terciario,
                       foreground=self.colores.texto_primario,
                       padding=[20, 10],
                       focuscolor='none')
        style.map('Kali.TNotebook.Tab',
                 background=[('selected', self.colores.acento_primario),
                           ('active', self.colores.fondo_hover)])
        
        # Crear notebook
        self.notebook = ttk.Notebook(parent, style='Kali.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # Agregar pestañas por categoría
        for cat_key, categoria in self.contenido['categorias'].items():
            self._crear_tab_categoria(cat_key, categoria)
    
    def _crear_tab_categoria(self, cat_key, categoria):
        """Crear pestaña para una categoría específica"""
        # Frame para la categoría
        tab_frame = tk.Frame(self.notebook, bg=self.colores.fondo_primario)
        
        # Título de la categoría en la pestaña
        titulo_tab = categoria.get('titulo', cat_key).replace('🔍 ', '').replace('🛡️ ', '').replace('⚔️ ', '')
        self.notebook.add(tab_frame, text=f" {titulo_tab} ")
        
        # Contenido scrollable
        canvas = tk.Canvas(tab_frame, bg=self.colores.fondo_primario, highlightthickness=0)
        scrollbar = tk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colores.fondo_primario)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título y descripción de la categoría
        tk.Label(scrollable_frame,
                text=categoria.get('titulo', cat_key),
                font=('Consolas', 14, 'bold'),
                fg=self.colores.acento_primario,
                bg=self.colores.fondo_primario).pack(anchor='w', padx=20, pady=(20, 5))
        
        tk.Label(scrollable_frame,
                text=categoria.get('descripcion', ''),
                font=('Consolas', 10),
                fg=self.colores.texto_secundario,
                bg=self.colores.fondo_primario,
                wraplength=900,
                justify='left').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Mostrar herramientas
        herramientas = categoria.get('herramientas', {})
        for herr_key, herramienta in herramientas.items():
            self._mostrar_herramienta(scrollable_frame, herr_key, herramienta)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def _mostrar_herramienta(self, parent, nombre, herramienta):
        """Mostrar información de una herramienta específica"""
        # Frame para la herramienta
        herr_frame = tk.Frame(parent, bg=self.colores.fondo_secundario, relief="groove", bd=1)
        herr_frame.pack(fill='x', padx=20, pady=10)
        
        # Nombre de la herramienta
        tk.Label(herr_frame,
                text=f"🔧 {nombre.upper()}",
                font=('Consolas', 12, 'bold'),
                fg=self.colores.acento_secundario,
                bg=self.colores.fondo_secundario).pack(anchor='w', padx=15, pady=(10, 5))
        
        # Descripción
        descripcion = herramienta.get('descripcion', '')
        if descripcion:
            tk.Label(herr_frame,
                    text=descripcion,
                    font=('Consolas', 9),
                    fg=self.colores.texto_terciario,
                    bg=self.colores.fondo_secundario,
                    wraplength=850,
                    justify='left').pack(anchor='w', padx=15, pady=(0, 10))
        
        # Comandos
        comandos = herramienta.get('comandos', [])
        for i, comando in enumerate(comandos):
            self._mostrar_comando(herr_frame, comando, i+1)
    
    def _mostrar_comando(self, parent, comando, numero):
        """Mostrar un comando específico con diseño mejorado"""
        cmd_frame = tk.Frame(parent, bg=self.colores.fondo_primario, relief="solid", bd=1)
        cmd_frame.pack(fill='x', padx=15, pady=8)
        
        # Descripción del comando
        desc = comando.get('descripcion', '')
        if desc:
            desc_label = tk.Label(cmd_frame,
                                text=f"💡 {desc}",
                                font=('Consolas', 10, 'bold'),
                                fg=self.colores.acento_terciario,
                                bg=self.colores.fondo_primario)
            desc_label.pack(anchor='w', padx=12, pady=(10, 5))
        
        # Comando principal con mejor formato
        cmd_text = comando.get('comando', '')
        if cmd_text:
            cmd_bg = tk.Frame(cmd_frame, bg=self.colores.fondo_terciario, relief="sunken", bd=1)
            cmd_bg.pack(fill='x', padx=12, pady=5)
            
            cmd_label = tk.Label(cmd_bg,
                               text=f"$ {cmd_text}",
                               font=('Consolas', 11, 'bold'),
                               fg=self.colores.exito,
                               bg=self.colores.fondo_terciario,
                               justify='left')
            cmd_label.pack(anchor='w', padx=12, pady=8)
        
        # Ejemplo (solo si es diferente del comando)
        ejemplo = comando.get('ejemplo', '')
        if ejemplo and ejemplo != cmd_text:
            tk.Label(cmd_frame,
                    text=f"📋 Ejemplo: {ejemplo}",
                    font=('Consolas', 9),
                    fg=self.colores.info,
                    bg=self.colores.fondo_primario).pack(anchor='w', padx=12, pady=(0, 10))
    
    def _crear_interfaz_simple(self, parent):
        """Crear interfaz simple para contenido de texto"""
        # Frame con scroll para texto
        text_frame = tk.Frame(parent, bg=self.colores.fondo_primario)
        text_frame.pack(fill='both', expand=True)
        
        # Text widget con scrollbar
        self.text_widget = tk.Text(text_frame,
                                  bg=self.colores.fondo_secundario,
                                  fg=self.colores.texto_primario,
                                  font=('Consolas', 11),
                                  wrap='word',
                                  padx=20,
                                  pady=20,
                                  insertbackground=self.colores.acento_primario)
        
        scrollbar = tk.Scrollbar(text_frame, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Insertar contenido
        if isinstance(self.contenido, str):
            self.text_widget.insert('1.0', self.contenido)
        else:
            self.text_widget.insert('1.0', str(self.contenido))
        
        self.text_widget.configure(state='disabled')
        
        # Pack widgets
        self.text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def _crear_footer(self):
        """Crear footer con controles mejorados"""
        footer = tk.Frame(self.ventana, bg=self.colores.fondo_secundario, height=60)
        footer.pack(fill='x', padx=15, pady=(0, 15))
        footer.pack_propagate(False)
        
        # Información de ayuda
        tk.Label(footer,
                text="💡 Usa Ctrl+C para copiar • Rueda del mouse para scroll",
                font=('Consolas', 9),
                fg=self.colores.texto_terciario,
                bg=self.colores.fondo_secundario).pack(side='left', padx=20, pady=20)
        
        # Botón cerrar mejorado
        btn_cerrar = tk.Button(footer,
                              text="✕ Cerrar",
                              font=('Consolas', 10, 'bold'),
                              bg=self.colores.error,
                              fg=self.colores.texto_primario,
                              relief="flat",
                              bd=0,
                              padx=20,
                              command=self._cerrar)
        btn_cerrar.pack(side='right', padx=20, pady=15)
        
        # Efectos hover
        def on_enter(e):
            btn_cerrar.configure(bg=self.colores.advertencia)
        def on_leave(e):
            btn_cerrar.configure(bg=self.colores.error)
        
        btn_cerrar.bind("<Enter>", on_enter)
        btn_cerrar.bind("<Leave>", on_leave)
    
    def _cerrar(self):
        """Cerrar ventana"""
        if self.ventana:
            self.ventana.grab_release()
            self.ventana.destroy()
            self.ventana = None
