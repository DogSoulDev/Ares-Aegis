#!/usr/bin/env python3
"""
Vista de Configuración para Ares Aegis
Configuración de temas, preferencias y opciones del sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from ..utils.temas_kali import TEMAS_DISPONIBLES, obtener_tema, aplicar_tema_a_widget
from ..utils.ayuda_logging import configurar_logger_modulo


class VistaConfiguracion:
    """Vista de configuración del sistema"""
    
    def __init__(self, contenedor, controlador_principal=None):
        self.contenedor = contenedor
        self.controlador = controlador_principal
        self.logger = configurar_logger_modulo('vista_configuracion')
        self.ventana_config = None
        self.tema_actual = obtener_tema('kali_original')
        
        # Cargar configuración actual
        self.cargar_configuracion()
        
    def cargar_configuracion(self):
        """Cargar configuración desde archivo"""
        try:
            config_path = os.path.join('configuracion', 'ares_aegis_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    tema_nombre = config.get('tema', 'kali_original')
                    self.tema_actual = obtener_tema(tema_nombre)
        except Exception as e:
            self.logger.warning(f"Error cargando configuración: {e}")
    
    def crear_vista(self, area_contenido=None):
        """Crear vista integrada de configuración"""
        try:
            # Limpiar contenedor
            for widget in self.contenedor.winfo_children():
                widget.destroy()
            
            # Frame principal
            frame_principal = tk.Frame(
                self.contenedor,
                bg=self.tema_actual['bg_principal']
            )
            frame_principal.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Header con título e info
            header_frame = tk.Frame(
                frame_principal,
                bg=self.tema_actual['bg_secundario'],
                height=80
            )
            header_frame.pack(fill='x', pady=(0, 20))
            header_frame.pack_propagate(False)
            
            # Título
            titulo = tk.Label(
                header_frame,
                text="⚙️ Configuración del Sistema",
                font=('Consolas', 16, 'bold'),
                bg=self.tema_actual['bg_secundario'],
                fg=self.tema_actual['texto_principal']
            )
            titulo.pack(side='left', padx=20, pady=20)
            
            # Botón de información
            btn_info = tk.Button(
                header_frame,
                text="ℹ️ Info",
                font=('Consolas', 10),
                bg=self.tema_actual['acento_secundario'],
                fg='white',
                command=self.mostrar_informacion,
                relief='flat',
                padx=15,
                pady=5
            )
            btn_info.pack(side='right', padx=20, pady=20)
            
            # Contenido de configuración
            self._crear_contenido_configuracion(frame_principal)
            
            self.logger.info("Vista de configuración creada exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error creando vista de configuración: {e}")
    
    def _crear_contenido_configuracion(self, parent):
        """Crear el contenido principal de configuración"""
        # Notebook para pestañas
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)
        
        # Pestaña de Temas
        self._crear_pestana_temas(notebook)
        
        # Pestaña de Sistema
        self._crear_pestana_sistema(notebook)
        
        # Pestaña de Avanzado
        self._crear_pestana_avanzado(notebook)
    
    def _crear_pestana_temas(self, notebook):
        """Crear pestaña de configuración de temas"""
        tema_frame = tk.Frame(notebook, bg=self.tema_actual['bg_principal'])
        notebook.add(tema_frame, text="🎨 Temas")
        
        # Título de sección
        tk.Label(
            tema_frame,
            text="Seleccionar Tema de Interfaz",
            font=('Consolas', 14, 'bold'),
            bg=self.tema_actual['bg_principal'],
            fg=self.tema_actual['texto_principal']
        ).pack(pady=20)
        
        # Variable para tema seleccionado
        self.tema_var = tk.StringVar(value='kali_original')
        
        # Frame para botones de temas
        temas_frame = tk.Frame(tema_frame, bg=self.tema_actual['bg_principal'])
        temas_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Crear botones para cada tema
        for i, (tema_id, tema_info) in enumerate(TEMAS_DISPONIBLES.items()):
            tema_btn = tk.Radiobutton(
                temas_frame,
                text=f"🎨 {tema_info['nombre']}",
                variable=self.tema_var,
                value=tema_id,
                font=('Consolas', 12),
                bg=self.tema_actual['bg_principal'],
                fg=self.tema_actual['texto_principal'],
                selectcolor=self.tema_actual['bg_secundario'],
                activebackground=self.tema_actual['bg_secundario'],
                command=lambda: self._preview_tema()
            )
            tema_btn.pack(anchor='w', pady=8, padx=20)
        
        # Botón aplicar tema
        btn_aplicar = tk.Button(
            tema_frame,
            text="✅ Aplicar Tema",
            font=('Consolas', 12, 'bold'),
            bg=self.tema_actual['acento_primario'],
            fg='black',
            command=self._aplicar_tema,
            relief='flat',
            padx=20,
            pady=10
        )
        btn_aplicar.pack(pady=20)
    
    def _crear_pestana_sistema(self, notebook):
        """Crear pestaña de configuración del sistema"""
        sistema_frame = tk.Frame(notebook, bg=self.tema_actual['bg_principal'])
        notebook.add(sistema_frame, text="🔧 Sistema")
        
        tk.Label(
            sistema_frame,
            text="Configuración del Sistema",
            font=('Consolas', 14, 'bold'),
            bg=self.tema_actual['bg_principal'],
            fg=self.tema_actual['texto_principal']
        ).pack(pady=20)
        
        # Opciones de sistema
        opciones_frame = tk.Frame(sistema_frame, bg=self.tema_actual['bg_principal'])
        opciones_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Ejemplo de opciones
        tk.Checkbutton(
            opciones_frame,
            text="🔄 Actualizaciones automáticas",
            font=('Consolas', 11),
            bg=self.tema_actual['bg_principal'],
            fg=self.tema_actual['texto_principal'],
            selectcolor=self.tema_actual['bg_secundario']
        ).pack(anchor='w', pady=5)
        
        tk.Checkbutton(
            opciones_frame,
            text="📊 Métricas en tiempo real",
            font=('Consolas', 11),
            bg=self.tema_actual['bg_principal'],
            fg=self.tema_actual['texto_principal'],
            selectcolor=self.tema_actual['bg_secundario']
        ).pack(anchor='w', pady=5)
    
    def _crear_pestana_avanzado(self, notebook):
        """Crear pestaña de configuración avanzada"""
        avanzado_frame = tk.Frame(notebook, bg=self.tema_actual['bg_principal'])
        notebook.add(avanzado_frame, text="⚙️ Avanzado")
        
        tk.Label(
            avanzado_frame,
            text="Configuración Avanzada",
            font=('Consolas', 14, 'bold'),
            bg=self.tema_actual['bg_principal'],
            fg=self.tema_actual['texto_principal']
        ).pack(pady=20)
        
        # Información de versión y estado
        info_frame = tk.Frame(avanzado_frame, bg=self.tema_actual['bg_principal'])
        info_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        tk.Label(
            info_frame,
            text="📋 Información del Sistema:",
            font=('Consolas', 12, 'bold'),
            bg=self.tema_actual['bg_principal'],
            fg=self.tema_actual['texto_principal']
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            info_frame,
            text="• Versión: Ares Aegis v4.0",
            font=('Consolas', 10),
            bg=self.tema_actual['bg_principal'],
            fg=self.tema_actual['texto_secundario']
        ).pack(anchor='w', pady=2)
        
        tk.Label(
            info_frame,
            text="• Plataforma: Kali Linux Optimizado",
            font=('Consolas', 10),
            bg=self.tema_actual['bg_principal'],
            fg=self.tema_actual['texto_secundario']
        ).pack(anchor='w', pady=2)
    
    def _preview_tema(self):
        """Vista previa del tema seleccionado"""
        tema_seleccionado = self.tema_var.get()
        self.tema_actual = obtener_tema(tema_seleccionado)
    
    def _aplicar_tema(self):
        """Aplicar el tema seleccionado"""
        try:
            tema_seleccionado = self.tema_var.get()
            if self.guardar_configuracion(tema_seleccionado):
                messagebox.showinfo("Éxito", "Tema aplicado correctamente.\nReinicia la aplicación para ver todos los cambios.")
                self.logger.info(f"Tema cambiado a: {tema_seleccionado}")
            else:
                messagebox.showerror("Error", "Error al guardar la configuración del tema")
        except Exception as e:
            self.logger.error(f"Error aplicando tema: {e}")
            messagebox.showerror("Error", f"Error aplicando tema: {e}")
    
    def mostrar_informacion(self):
        """Mostrar información sobre la configuración"""
        info_text = """
🔧 CONFIGURACIÓN DEL SISTEMA

📋 Información:
• Permite personalizar la apariencia de Ares Aegis
• Configura preferencias del sistema
• Gestiona temas y colores de la interfaz

🎨 Temas Disponibles:
• Kali Original: Tema clásico de Kali Linux
• Kali Dark: Versión oscura optimizada
• Kali Neon: Estilo moderno con acentos neón
• Corporate: Tema profesional para entornos empresariales

⚙️ Configuración del Sistema:
• Actualizaciones automáticas
• Métricas en tiempo real
• Configuraciones avanzadas

💡 Consejos:
• Los cambios de tema requieren reinicio
• Guarda la configuración antes de cerrar
• Usa el tema que mejor se adapte a tu entorno
        """
        
        messagebox.showinfo("Información - Configuración", info_text.strip())
            
    def guardar_configuracion(self, tema_nombre):
        """Guardar configuración a archivo"""
        try:
            config_path = os.path.join('configuracion', 'ares_aegis_config.json')
            
            # Cargar configuración existente
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # Actualizar tema
            config['tema'] = tema_nombre
            
            # Guardar
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Configuración guardada: tema {tema_nombre}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando configuración: {e}")
            return False
    
    def mostrar_configuracion(self):
        """Mostrar ventana de configuración"""
        if self.ventana_config and self.ventana_config.winfo_exists():
            self.ventana_config.lift()
            return
            
        # Crear ventana de configuración
        self.ventana_config = tk.Toplevel()
        self.ventana_config.title("⚙️ Configuración - Ares Aegis")
        self.ventana_config.geometry("1000x750")  # Aumentado de 800x600 a 1000x750
        self.ventana_config.minsize(900, 650)     # Tamaño mínimo
        self.ventana_config.transient()
        self.ventana_config.grab_set()
        
        # Aplicar tema actual
        self.ventana_config.configure(bg=self.tema_actual['bg_principal'])
        
        # Frame principal con padding aumentado
        main_frame = tk.Frame(self.ventana_config, bg=self.tema_actual['bg_principal'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=25)  # Aumentado padding
        
        # Título con tamaño de fuente aumentado
        titulo = tk.Label(
            main_frame,
            text="⚙️ Configuración del Sistema",
            font=('Consolas', 18, 'bold'),  # Aumentado de 16 a 18
            bg=self.tema_actual['bg_principal'],
            fg=self.tema_actual['texto_principal']
        )
        titulo.pack(pady=(0, 25))  # Aumentado padding inferior
        
        # Notebook para pestañas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Pestaña de Temas
        self.crear_pestaña_temas(notebook)
        
        # Pestaña de General
        self.crear_pestaña_general(notebook)
        
        # Botones de acción
        self.crear_botones_accion(main_frame)
        
        # Centrar ventana
        self.centrar_ventana()
        
    def crear_pestaña_temas(self, notebook):
        """Crear pestaña de configuración de temas"""
        frame_temas = tk.Frame(notebook, bg=self.tema_actual['bg_secundario'])
        notebook.add(frame_temas, text="🎨 Temas")
        
        # Título de sección
        titulo_temas = tk.Label(
            frame_temas,
            text="🎨 Selecciona tu Tema de Kali Linux",
            font=('Consolas', 14, 'bold'),
            bg=self.tema_actual['bg_secundario'],
            fg=self.tema_actual['texto_principal']
        )
        titulo_temas.pack(pady=20)
        
        # Variable para tema seleccionado
        self.tema_seleccionado = tk.StringVar(value='kali_original')
        
        # Frame para los temas
        temas_frame = tk.Frame(frame_temas, bg=self.tema_actual['bg_secundario'])
        temas_frame.pack(fill='both', expand=True, padx=20)
        
        # Crear botones para cada tema
        row = 0
        col = 0
        for tema_id, tema_info in TEMAS_DISPONIBLES.items():
            # Frame del tema
            tema_frame = tk.Frame(
                temas_frame,
                bg=tema_info['bg_principal'],
                relief='raised',
                bd=2
            )
            tema_frame.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
            
            # Nombre del tema
            nombre_label = tk.Label(
                tema_frame,
                text=tema_info['nombre'],
                font=('Consolas', 12, 'bold'),
                bg=tema_info['bg_principal'],
                fg=tema_info['texto_principal']
            )
            nombre_label.pack(pady=5)
            
            # Preview de colores
            colores_frame = tk.Frame(tema_frame, bg=tema_info['bg_principal'])
            colores_frame.pack(pady=5)
            
            # Muestras de color
            for i, color in enumerate([tema_info['acento_primario'], tema_info['acento_secundario'], tema_info['success']]):
                color_sample = tk.Label(
                    colores_frame,
                    text="███",
                    font=('Consolas', 8),
                    bg=tema_info['bg_principal'],
                    fg=color
                )
                color_sample.pack(side='left', padx=2)
            
            # Botón para seleccionar
            btn_seleccionar = tk.Button(
                tema_frame,
                text="Aplicar Tema",
                font=('Consolas', 10),
                bg=tema_info['acento_primario'],
                fg=tema_info['bg_principal'],
                command=lambda t_id=tema_id: self.aplicar_tema(t_id)
            )
            btn_seleccionar.pack(pady=5)
            
            col += 1
            if col > 2:  # 3 columnas
                col = 0
                row += 1
        
        # Configurar grid
        for i in range(3):
            temas_frame.grid_columnconfigure(i, weight=1)
            
    def crear_pestaña_general(self, notebook):
        """Crear pestaña de configuración general"""
        frame_general = tk.Frame(notebook, bg=self.tema_actual['bg_secundario'])
        notebook.add(frame_general, text="⚙️ General")
        
        # Información del sistema
        info_frame = tk.LabelFrame(
            frame_general,
            text="📋 Información del Sistema",
            font=('Consolas', 12, 'bold'),
            bg=self.tema_actual['bg_secundario'],
            fg=self.tema_actual['texto_principal']
        )
        info_frame.pack(fill='x', padx=20, pady=20)
        
        # Información
        info_text = tk.Text(
            info_frame,
            height=10,
            font=('Consolas', 10),
            bg=self.tema_actual['bg_terciario'],
            fg=self.tema_actual['texto_principal'],
            wrap='word'
        )
        info_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Insertar información
        info_content = """🛡️ ARES AEGIS v4.0 - Suite de Ciberseguridad

📋 Características:
• Sistema SIEM en tiempo real
• Constructor de wordlists avanzado
• Monitor de red y procesos
• Auditoría de autenticación PAM
• Escaneador de vulnerabilidades
• Sistema de cuarentena

🔧 Tecnología:
• Python Standard Library únicamente
• Optimizado para Kali Linux
• Sin dependencias externas
• Interfaz nativa tkinter

🎨 Personalización:
• 5 temas de Kali Linux disponibles
• Interfaz completamente personalizable
• Colores oficiales de Kali Linux"""
        
        info_text.insert('1.0', info_content)
        info_text.config(state='disabled')
        
    def crear_botones_accion(self, parent):
        """Crear botones de acción"""
        botones_frame = tk.Frame(parent, bg=self.tema_actual['bg_principal'])
        botones_frame.pack(side='bottom', fill='x', pady=(20, 0))
        
        # Botón Ayuda
        btn_ayuda = tk.Button(
            botones_frame,
            text="❓ Ayuda",
            font=('Consolas', 10),
            bg=self.tema_actual['acento_secundario'],
            fg=self.tema_actual['bg_principal'],
            command=self.mostrar_ayuda
        )
        btn_ayuda.pack(side='left', padx=(0, 10))
        
        # Botón Cerrar
        btn_cerrar = tk.Button(
            botones_frame,
            text="✖️ Cerrar",
            font=('Consolas', 10),
            bg=self.tema_actual['error'],
            fg='white',
            command=self.cerrar_configuracion
        )
        btn_cerrar.pack(side='right')
        
    def aplicar_tema(self, tema_id):
        """Aplicar un tema específico"""
        try:
            # Guardar configuración
            if self.guardar_configuracion(tema_id):
                # Actualizar tema actual
                self.tema_actual = obtener_tema(tema_id)
                
                # Mostrar mensaje de confirmación
                messagebox.showinfo(
                    "Tema Aplicado",
                    f"Tema '{TEMAS_DISPONIBLES[tema_id]['nombre']}' aplicado correctamente.\n\n"
                    "Reinicia Ares Aegis para ver todos los cambios."
                )
                
                # Cerrar ventana de configuración
                self.cerrar_configuracion()
                
        except Exception as e:
            self.logger.error(f"Error aplicando tema: {e}")
            messagebox.showerror("Error", f"Error aplicando tema: {e}")
            
    def mostrar_ayuda(self):
        """Mostrar ayuda de configuración"""
        ayuda_text = """🛡️ AYUDA DE CONFIGURACIÓN

🎨 TEMAS:
• Kali Original: Tema clásico verde y negro
• Dragon: Tema rojo inspirado en Kali Dragon
• Purple Haze: Tema púrpura para pentesting
• Blue Steel: Tema azul profesional
• Matrix: Tema verde Matrix clásico

⚙️ CONFIGURACIÓN:
• Los cambios se guardan automáticamente
• Reinicia la aplicación para ver todos los cambios
• La configuración se almacena en configuracion/

🔧 SOLUCIÓN DE PROBLEMAS:
• Si un tema no se aplica correctamente, reinicia la aplicación
• La configuración se guarda en formato JSON
• Los temas están optimizados para Kali Linux"""
        
        messagebox.showinfo("Ayuda - Configuración", ayuda_text)
        
    def cerrar_configuracion(self):
        """Cerrar ventana de configuración"""
        if self.ventana_config:
            self.ventana_config.destroy()
            self.ventana_config = None
            
    def centrar_ventana(self):
        """Centrar la ventana en la pantalla"""
        if self.ventana_config:
            self.ventana_config.update_idletasks()
            x = (self.ventana_config.winfo_screenwidth() // 2) - (800 // 2)
            y = (self.ventana_config.winfo_screenheight() // 2) - (600 // 2)
            self.ventana_config.geometry(f"800x600+{x}+{y}")
            
    def mostrar_informacion(self):
        """Mostrar información de configuración"""
        info_text = """⚙️ CONFIGURACIÓN DEL SISTEMA

🎨 GESTIÓN DE TEMAS:
• Selecciona entre 5 temas de Kali Linux
• Cambia colores de toda la interfaz
• Configuración persistente

📋 OPCIONES DISPONIBLES:
• Temas visuales personalizados
• Información del sistema
• Ayuda integrada

🔧 CONFIGURACIÓN:
• Los cambios se aplican inmediatamente
• Configuración guardada automáticamente
• Compatible con Kali Linux"""
        
        messagebox.showinfo("Información - Configuración", info_text)
