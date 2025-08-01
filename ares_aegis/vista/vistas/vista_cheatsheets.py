#!/usr/bin/env python3
"""
Vista CheatSheets para Ares Aegis
Dashboard completo de gestión de hojas de trucos para estudiantes de ciberseguridad

Creado por DogSoulDev
Versión: 4.0.0 - Vista Especializada
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import logging
import os
from pathlib import Path
import threading
from datetime import datetime

from ..componentes_ui.sistema_ayuda import SistemaAyuda


class VistaCheatsheets:
    """Vista especializada para gestión de CheatSheets de ciberseguridad"""
    
    def __init__(self, contenedor_padre, controlador, colores):
        self.contenedor_padre = contenedor_padre
        self.controlador = controlador
        self.colores = colores
        self.logger = logging.getLogger(__name__)
        self.frame_principal = None
        
        # Inicializar datos inmediatamente
        self.cheatsheets_data = {}
        self.cheatsheet_actual = None
        self.categoria_actual = "todas"
        
        # Widgets principales inicializados correctamente
        self.tree_cheatsheets = None  # Se inicializa en _crear_panel_lateral
        self.text_contenido = None  # Se inicializa en _crear_panel_contenido
        self.search_var = tk.StringVar()  # Inicializada con valor por defecto
        self.categoria_var = tk.StringVar(value="todas")  # Inicializada con valor por defecto
        
        # Sistema de ayuda
        self.sistema_ayuda = SistemaAyuda(colores)
        
        # Configurar rutas de manera más robusta
        self._configurar_rutas_cheatsheets()
        
        self.logger.info("Vista CheatSheets inicializada")
    
    def _configurar_rutas_cheatsheets(self):
        """Configurar rutas de cheatsheets de manera robusta"""
        from pathlib import Path
        
        # Obtener directorio base del proyecto
        try:
            # Intentar desde la ubicación actual del archivo
            current_file = Path(__file__).resolve()
            base_dir = current_file.parents[3]  # Subir 3 niveles desde ares_aegis/vista/vistas/
            self.ruta_cheatsheets = base_dir / "recursos" / "cheatsheets"
            
            # Si no existe, intentar desde directorio de trabajo
            if not self.ruta_cheatsheets.exists():
                base_dir = Path.cwd()
                self.ruta_cheatsheets = base_dir / "recursos" / "cheatsheets"
                
            # Crear directorio si no existe
            self.ruta_cheatsheets.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Ruta de cheatsheets configurada: {self.ruta_cheatsheets}")
            
        except Exception as e:
            self.logger.warning(f"Error configurando ruta de cheatsheets: {e}")
            # Fallback a directorio de trabajo actual
            self.ruta_cheatsheets = Path.cwd() / "recursos" / "cheatsheets"
            self.ruta_cheatsheets.mkdir(parents=True, exist_ok=True)
        
    def mostrar_informacion(self):
        """Mostrar información de ayuda sobre las CheatSheets"""
        info_text = """🛡️ CHEATSHEETS DE CIBERSEGURIDAD - INFORMACIÓN

📚 FUNCIONALIDADES PRINCIPALES:
• Biblioteca completa de hojas de trucos
• Comandos y técnicas de pentesting
• Referencias rápidas para auditorías
• Guías paso a paso para estudiantes

⚡ CATEGORÍAS DISPONIBLES:
• Reconnaissance: Recopilación de información
• Exploitation: Técnicas de explotación
• Post-Exploitation: Mantenimiento de acceso
• Network: Análisis y ataques de red
• Web: Seguridad de aplicaciones web
• Forensics: Análisis forense digital

🎯 HERRAMIENTAS INCLUIDAS:
• Nmap: Escaneo de puertos y servicios
• Metasploit: Framework de explotación
• Burp Suite: Análisis de aplicaciones web
• Wireshark: Análisis de tráfico de red
• John the Ripper: Cracking de contraseñas
• Hashcat: Recuperación de contraseñas

🔧 FUNCIONES AVANZADAS:
• Búsqueda inteligente por comando
• Filtrado por categoría y herramienta
• Favoritos para acceso rápido
• Exportación de cheatsheets
• Creación de cheatsheets personalizadas

⚠️ PARA ESTUDIANTES DE ETHICAL HACKING:
• Comandos explicados paso a paso
• Ejemplos prácticos de uso
• Contexto de cuándo usar cada técnica
• Referencias a documentación oficial
• Tips y trucos de profesionales

📊 CONTENIDO ESTRUCTURADO:
• Sintaxis completa de comandos
• Parámetros más utilizados
• Ejemplos de uso real
• Casos de estudio prácticos
• Troubleshooting común

💡 CASOS DE USO:
• Preparación para certificaciones (CEH, OSCP)
• Consulta rápida durante pentests
• Aprendizaje de nuevas herramientas
• Referencia durante auditorías
• Estudio y práctica personal

🔐 METODOLOGÍAS INCLUIDAS:
• OWASP Testing Guide
• NIST Cybersecurity Framework
• PTES (Penetration Testing Execution Standard)
• OSSTMM (Open Source Security Testing)
• Kill Chain Methodology

📋 NOTA EDUCATIVA:
Estas herramientas son para uso educativo y auditorías autorizadas únicamente.
Siempre obtén permiso antes de realizar pruebas de penetración."""
        
        messagebox.showinfo("Información - CheatSheets de Ciberseguridad", info_text)
        
        self.logger.info("Vista CheatSheets inicializada")
    
    def crear_vista(self, area_contenido=None):
        """Crear la vista principal de CheatSheets"""
        self._limpiar_contenedor()
        
        # Frame principal con padding estandarizado
        self.frame_principal = tk.Frame(self.contenedor_padre, bg=self.colores.fondo_secundario)
        self.frame_principal.pack(fill='both', expand=True, padx=20, pady=10)
        
        # === HEADER ===
        self._crear_header()
        
        # === CONTENIDO PRINCIPAL ===
        contenido_frame = tk.Frame(self.frame_principal, bg=self.colores.fondo_secundario)
        contenido_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Configurar grid
        contenido_frame.grid_rowconfigure(0, weight=1)
        contenido_frame.grid_columnconfigure(0, weight=1)  # Panel izquierdo
        contenido_frame.grid_columnconfigure(1, weight=2)  # Panel derecho
        
        # === PANEL IZQUIERDO: LISTA DE CHEATSHEETS ===
        self._crear_panel_lista(contenido_frame)
        
        # === PANEL DERECHO: CONTENIDO Y EDITOR ===
        self._crear_panel_contenido(contenido_frame)
        
        # Cargar cheatsheets disponibles
        self._cargar_cheatsheets()
        
        self.logger.info("Vista CheatSheets creada exitosamente")
    
    def _crear_header(self):
        """Crear header de la vista"""
        header_frame = tk.Frame(self.frame_principal, 
                              bg=self.colores.negro_carbono, 
                              height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Título
        titulo_frame = tk.Frame(header_frame, bg=self.colores.negro_carbono)
        titulo_frame.pack(side='left', padx=30, pady=20)
        
        tk.Label(titulo_frame,
                text="📚 GESTOR DE CHEATSHEETS",
                font=('Consolas', 20, 'bold'),
                fg=self.colores.verde_terminal,
                bg=self.colores.negro_carbono).pack(anchor='w')
        
        tk.Label(titulo_frame,
                text="HOJAS DE TRUCOS PARA CIBERSEGURIDAD",
                font=('Consolas', 10),
                fg=self.colores.gris_platino,
                bg=self.colores.negro_carbono).pack(anchor='w', pady=(2, 0))
        
        # Botones de acción
        botones_frame = tk.Frame(header_frame, bg=self.colores.negro_carbono)
        botones_frame.pack(side='right', padx=30, pady=20)
        
        # Botón nuevo cheatsheet
        btn_nuevo = tk.Button(botones_frame,
                            text="➕ NUEVO",
                            font=('Consolas', 10, 'bold'),
                            fg=self.colores.negro_carbono,
                            bg=self.colores.verde_terminal,
                            relief='flat',
                            cursor='hand2',
                            padx=18,
                            pady=8,
                            command=self._nuevo_cheatsheet)
        btn_nuevo.pack(side='left', padx=(0, 12))
        
        # Botón importar
        btn_importar = tk.Button(botones_frame,
                               text="📁 IMPORTAR",
                               font=('Consolas', 10, 'bold'),
                               fg=self.colores.blanco_hueso,
                               bg=self.colores.cyan_brillante,
                               relief='flat',
                               cursor='hand2',
                               padx=18,
                               pady=8,
                               command=self._importar_cheatsheet)
        btn_importar.pack(side='left', padx=(0, 12))
        
        # Botón exportar
        btn_exportar = tk.Button(botones_frame,
                               text="💾 EXPORTAR",
                               font=('Consolas', 10, 'bold'),
                               fg=self.colores.negro_carbono,
                               bg=self.colores.amarillo_medio,
                               relief='flat',
                               cursor='hand2',
                               padx=18,
                               pady=8,
                               command=self._exportar_cheatsheet)
        btn_exportar.pack(side='left', padx=(0, 12))
        
        # Botón de información
        btn_info = tk.Button(botones_frame,
                           text="❓ Info",
                           font=('Consolas', 10, 'bold'),
                           fg='white',
                           bg=self.colores.cyan_brillante,
                           relief='flat',
                           cursor='hand2',
                           padx=15,
                           pady=8,
                           command=self.mostrar_informacion)
        btn_info.pack(side='left')
    
    def _crear_panel_lista(self, parent):
        """Crear panel izquierdo con lista de cheatsheets"""
        lista_frame = tk.LabelFrame(parent,
                                  text="🗂️ CHEATSHEETS DISPONIBLES",
                                  bg=self.colores.fondo_secundario,
                                  fg=self.colores.verde_terminal,
                                  font=('Consolas', 12, 'bold'),
                                  relief='flat',
                                  bd=1)
        lista_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        
        # === FILTROS Y BÚSQUEDA ===
        filtros_frame = tk.Frame(lista_frame, bg=self.colores.fondo_secundario)
        filtros_frame.pack(fill='x', padx=10, pady=10)
        
        # Búsqueda
        tk.Label(filtros_frame,
                text="🔍 Buscar:",
                font=('Consolas', 10, 'bold'),
                fg=self.colores.cyan_brillante,
                bg=self.colores.fondo_secundario).pack(anchor='w')
        
        self.search_var = tk.StringVar()
        entry_buscar = tk.Entry(filtros_frame,
                              textvariable=self.search_var,
                              font=('Consolas', 10),
                              bg=self.colores.negro_carbono,
                              fg=self.colores.blanco_hueso,
                              insertbackground=self.colores.verde_terminal,
                              relief='flat',
                              bd=5)
        entry_buscar.pack(fill='x', pady=(5, 10))
        entry_buscar.bind('<KeyRelease>', self._filtrar_cheatsheets)
        
        # Categorías
        tk.Label(filtros_frame,
                text="📑 Categoría:",
                font=('Consolas', 10, 'bold'),
                fg=self.colores.cyan_brillante,
                bg=self.colores.fondo_secundario).pack(anchor='w')
        
        self.categoria_var = tk.StringVar(value="todas")
        combo_categoria = ttk.Combobox(filtros_frame,
                                     textvariable=self.categoria_var,
                                     values=self._obtener_categorias(),
                                     font=('Consolas', 10),
                                     state='readonly')
        combo_categoria.pack(fill='x', pady=(5, 0))
        combo_categoria.bind('<<ComboboxSelected>>', self._filtrar_cheatsheets)
        
        # === LISTA DE CHEATSHEETS ===
        tree_frame = tk.Frame(lista_frame, bg=self.colores.fondo_secundario)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=(10, 10))
        
        # Configurar TreeView
        columns = ("nombre", "categoria", "nivel")
        self.tree_cheatsheets = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree_cheatsheets.heading("nombre", text="📋 Nombre")
        self.tree_cheatsheets.heading("categoria", text="📂 Categoría") 
        self.tree_cheatsheets.heading("nivel", text="⚡ Nivel")
        
        self.tree_cheatsheets.column("nombre", width=200, minwidth=150)
        self.tree_cheatsheets.column("categoria", width=120, minwidth=100)
        self.tree_cheatsheets.column("nivel", width=80, minwidth=70)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_cheatsheets.yview)
        self.tree_cheatsheets.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.tree_cheatsheets.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Eventos
        self.tree_cheatsheets.bind('<<TreeviewSelect>>', self._seleccionar_cheatsheet)
        self.tree_cheatsheets.bind('<Double-1>', self._editar_cheatsheet)
        
        # === BOTONES DE GESTIÓN ===
        botones_lista_frame = tk.Frame(lista_frame, bg=self.colores.fondo_secundario)
        botones_lista_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Configurar grid para centrar botones
        botones_lista_frame.grid_columnconfigure(0, weight=1)
        botones_lista_frame.grid_columnconfigure(1, weight=1)
        botones_lista_frame.grid_columnconfigure(2, weight=1)
        
        # Frame contenedor para botones centrados
        botones_container = tk.Frame(botones_lista_frame, bg=self.colores.fondo_secundario)
        botones_container.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        btn_editar = tk.Button(botones_container,
                             text="✏️ EDITAR",
                             font=('Consolas', 9, 'bold'),
                             fg=self.colores.negro_carbono,
                             bg=self.colores.cyan_brillante,
                             relief='flat',
                             cursor='hand2',
                             padx=12,
                             pady=6,
                             command=self._editar_cheatsheet)
        btn_editar.pack(side='left', padx=(0, 8), pady=2, fill='x', expand=True)
        
        btn_eliminar = tk.Button(botones_container,
                               text="🗑️ ELIMINAR",
                               font=('Consolas', 9, 'bold'),
                               fg=self.colores.blanco_hueso,
                               bg=self.colores.rojo_critico,
                               relief='flat',
                               cursor='hand2',
                               padx=12,
                               pady=6,
                               command=self._eliminar_cheatsheet)
        btn_eliminar.pack(side='left', padx=(4, 8), pady=2, fill='x', expand=True)
        
        btn_duplicar = tk.Button(botones_container,
                               text="📄 DUPLICAR",
                               font=('Consolas', 9, 'bold'),
                               fg=self.colores.negro_carbono,
                               bg=self.colores.amarillo_medio,
                               relief='flat',
                               cursor='hand2',
                               padx=12,
                               pady=6,
                               command=self._duplicar_cheatsheet)
        btn_duplicar.pack(side='left', padx=(4, 0), pady=2, fill='x', expand=True)
    
    def _crear_panel_contenido(self, parent):
        """Crear panel derecho con contenido del cheatsheet"""
        contenido_frame = tk.LabelFrame(parent,
                                      text="📖 CONTENIDO DEL CHEATSHEET",
                                      bg=self.colores.fondo_secundario,
                                      fg=self.colores.verde_terminal,
                                      font=('Consolas', 12, 'bold'),
                                      relief='flat',
                                      bd=1)
        contenido_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        
        # === INFORMACIÓN DEL CHEATSHEET ===
        info_frame = tk.Frame(contenido_frame, bg=self.colores.fondo_secundario)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        # Título del cheatsheet actual
        self.titulo_label = tk.Label(info_frame,
                                   text="Selecciona un CheatSheet para ver su contenido",
                                   font=('Consolas', 14, 'bold'),
                                   fg=self.colores.cyan_brillante,
                                   bg=self.colores.fondo_secundario)
        self.titulo_label.pack(anchor='w')
        
        # Descripción
        self.descripcion_label = tk.Label(info_frame,
                                        text="",
                                        font=('Consolas', 10),
                                        fg=self.colores.gris_platino,
                                        bg=self.colores.fondo_secundario,
                                        wraplength=600,
                                        justify='left')
        self.descripcion_label.pack(anchor='w', pady=(5, 0))
        
        # === CONTENIDO ===
        contenido_inner_frame = tk.Frame(contenido_frame, bg=self.colores.fondo_secundario)
        contenido_inner_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Frame para el contenido con scroll
        text_frame = tk.Frame(contenido_inner_frame, bg=self.colores.negro_carbono)
        text_frame.pack(fill='both', expand=True)
        
        # Texto con scrollbar
        self.text_contenido = tk.Text(text_frame,
                                    font=('Consolas', 10),
                                    bg=self.colores.negro_carbono,
                                    fg=self.colores.blanco_hueso,
                                    insertbackground=self.colores.verde_terminal,
                                    selectbackground=self.colores.verde_terminal,
                                    selectforeground=self.colores.negro_carbono,
                                    relief='flat',
                                    bd=10,
                                    wrap='word',
                                    state='disabled')
        
        scrollbar_text = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_contenido.yview)
        self.text_contenido.configure(yscrollcommand=scrollbar_text.set)
        
        self.text_contenido.pack(side="left", fill="both", expand=True)
        scrollbar_text.pack(side="right", fill="y")
        
        # === BOTONES DE ACCIÓN ===
        acciones_frame = tk.Frame(contenido_frame, bg=self.colores.fondo_secundario)
        acciones_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Configurar grid para distribución uniforme
        acciones_frame.grid_columnconfigure(0, weight=1)
        acciones_frame.grid_columnconfigure(1, weight=1)
        acciones_frame.grid_columnconfigure(2, weight=1)
        
        # Container para centrar botones
        botones_acciones = tk.Frame(acciones_frame, bg=self.colores.fondo_secundario)
        botones_acciones.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5)
        
        btn_copiar = tk.Button(botones_acciones,
                             text="📋 COPIAR TODO",
                             font=('Consolas', 10, 'bold'),
                             fg=self.colores.negro_carbono,
                             bg=self.colores.verde_terminal,
                             relief='flat',
                             cursor='hand2',
                             padx=15,
                             pady=8,
                             command=self._copiar_contenido)
        btn_copiar.pack(side='left', padx=(0, 10), pady=5, fill='x', expand=True)
        
        btn_guardar = tk.Button(botones_acciones,
                              text="💾 GUARDAR CAMBIOS",
                              font=('Consolas', 10, 'bold'),
                              fg=self.colores.blanco_hueso,
                              bg=self.colores.cyan_brillante,
                              relief='flat',
                              cursor='hand2',
                              padx=15,
                              pady=8,
                              command=self._guardar_cambios)
        btn_guardar.pack(side='left', padx=(5, 10), pady=5, fill='x', expand=True)
        
        btn_recargar = tk.Button(botones_acciones,
                               text="🔄 RECARGAR",
                               font=('Consolas', 10, 'bold'),
                               fg=self.colores.negro_carbono,
                               bg=self.colores.amarillo_medio,
                               relief='flat',
                               cursor='hand2',
                               padx=15,
                               pady=8,
                               command=self._recargar_cheatsheet)
        btn_recargar.pack(side='left', padx=(5, 0), pady=5, fill='x', expand=True)
        
        # Configurar tags para sintaxis destacada
        self._configurar_tags_sintaxis()
    
    def _configurar_tags_sintaxis(self):
        """Configurar tags para destacar sintaxis en el texto"""
        # Tags para diferentes elementos
        if self.text_contenido:
            self.text_contenido.tag_configure("comando", 
                                            foreground=self.colores.verde_terminal, 
                                            font=('Consolas', 10, 'bold'))
            self.text_contenido.tag_configure("descripcion", 
                                            foreground=self.colores.cyan_brillante)
            self.text_contenido.tag_configure("ejemplo", 
                                            foreground=self.colores.amarillo_medio,
                                            font=('Consolas', 10, 'italic'))
            self.text_contenido.tag_configure("categoria", 
                                            foreground=self.colores.verde_esmeralda,
                                            font=('Consolas', 12, 'bold'))
            self.text_contenido.tag_configure("herramienta", 
                                            foreground=self.colores.naranja_alto,
                                            font=('Consolas', 11, 'bold'))
        else:
            self.logger.warning("text_contenido no inicializado, omitiendo configuración de tags")
    
    def _obtener_categorias(self):
        """Obtener lista de categorías disponibles"""
        categorias_base = [
            "todas",
            "reconocimiento", 
            "vulnerabilidades",
            "explotacion",
            "post_explotacion",
            "forense",
            "wireless",
            "steganografia",
            "redes",
            "web",
            "reversing",
            "criptografia"
        ]
        return categorias_base
    
    def _cargar_cheatsheets(self):
        """Cargar todos los cheatsheets disponibles"""
        try:
            # Limpiar datos anteriores
            self.cheatsheets_data.clear()
            
            self.logger.info(f"Cargando cheatsheets desde: {self.ruta_cheatsheets}")
            
            # Verificar que el directorio existe
            if not self.ruta_cheatsheets.exists():
                self.logger.warning(f"Directorio de cheatsheets no existe: {self.ruta_cheatsheets}")
                messagebox.showwarning("Advertencia", "Directorio de cheatsheets no encontrado. Se creará uno vacío.")
                self.ruta_cheatsheets.mkdir(parents=True, exist_ok=True)
                return
            
            # Cargar índice
            archivo_indice = self.ruta_cheatsheets / "indice.json"
            if archivo_indice.exists():
                with open(archivo_indice, 'r', encoding='utf-8') as f:
                    indice = json.load(f)
                
                for nombre, info in indice.get("cheatsheets", {}).items():
                    # Verificar que el archivo del cheatsheet existe
                    archivo_cheatsheet = self.ruta_cheatsheets / info.get("archivo", f"{nombre}.json")
                    if archivo_cheatsheet.exists():
                        self.cheatsheets_data[nombre] = info
                        self.logger.debug(f"Cheatsheet cargado: {nombre}")
                    else:
                        self.logger.warning(f"Archivo de cheatsheet no encontrado: {archivo_cheatsheet}")
            else:
                self.logger.warning(f"Archivo índice no encontrado: {archivo_indice}")
                # Buscar archivos JSON en el directorio y crear índice básico
                self._crear_indice_automatico()
            
            # Actualizar TreeView
            self._actualizar_lista()
            
            self.logger.info(f"Cargados {len(self.cheatsheets_data)} cheatsheets exitosamente")
            
            # Si no hay cheatsheets, mostrar mensaje informativo
            if not self.cheatsheets_data:
                self._mostrar_mensaje_sin_cheatsheets()
            
        except Exception as e:
            self.logger.error(f"Error cargando cheatsheets: {e}")
            messagebox.showerror("Error", f"Error cargando cheatsheets:\n{str(e)}")
    
    def _crear_indice_automatico(self):
        """Crear índice automático basado en archivos JSON encontrados"""
        try:
            archivos_json = list(self.ruta_cheatsheets.glob("*.json"))
            
            for archivo in archivos_json:
                if archivo.name == "indice.json":
                    continue
                    
                nombre = archivo.stem
                self.cheatsheets_data[nombre] = {
                    "archivo": archivo.name,
                    "titulo": f"📚 {nombre.replace('_', ' ').title()}",
                    "descripcion": f"Cheatsheet de {nombre}",
                    "categoria": "general",
                    "nivel": "intermedio",
                    "tags": [nombre]
                }
                
            self.logger.info(f"Índice automático creado con {len(self.cheatsheets_data)} archivos")
            
        except Exception as e:
            self.logger.error(f"Error creando índice automático: {e}")
    
    def _mostrar_mensaje_sin_cheatsheets(self):
        """Mostrar mensaje cuando no hay cheatsheets disponibles"""
        if hasattr(self, 'text_contenido') and self.text_contenido:
            self.text_contenido.config(state='normal')
            self.text_contenido.delete('1.0', tk.END)
            mensaje = """📚 NO HAY CHEATSHEETS DISPONIBLES

🔍 SOLUCIONES POSIBLES:

1. Verificar que los archivos estén en:
   {ruta}

2. Los cheatsheets deben estar en formato JSON

3. Debe existir un archivo 'indice.json' con la estructura:
   {{
     "cheatsheets": {{
       "nombre": {{
         "archivo": "nombre.json",
         "titulo": "Título",
         "categoria": "categoria",
         "nivel": "nivel"
       }}
     }}
   }}

4. Contactar al administrador para restaurar los archivos

💡 NOTA: Los cheatsheets son esenciales para el funcionamiento
completo de Ares Aegis en entornos educativos.""".format(ruta=self.ruta_cheatsheets)
            
            self.text_contenido.insert('1.0', mensaje)
            self.text_contenido.config(state='disabled')
    
    def _actualizar_lista(self):
        """Actualizar la lista de cheatsheets en el TreeView"""
        if not self.tree_cheatsheets:
            self.logger.warning("tree_cheatsheets no inicializado, omitiendo actualización de lista")
            return
            
        # Limpiar TreeView
        for item in self.tree_cheatsheets.get_children():
            self.tree_cheatsheets.delete(item)
        
        # Agregar cheatsheets
        for nombre, info in self.cheatsheets_data.items():
            titulo = info.get('titulo', nombre)
            categoria = info.get('categoria', 'general')
            nivel = info.get('nivel', 'intermedio')
            
            self.tree_cheatsheets.insert('', 'end', iid=nombre, values=(titulo, categoria, nivel))
    
    def _filtrar_cheatsheets(self, event=None):
        """Filtrar cheatsheets según búsqueda y categoría"""
        if not self.tree_cheatsheets:
            self.logger.warning("tree_cheatsheets no inicializado, omitiendo filtrado")
            return
            
        busqueda = self.search_var.get().lower()
        categoria = self.categoria_var.get()
        
        # Limpiar TreeView
        for item in self.tree_cheatsheets.get_children():
            self.tree_cheatsheets.delete(item)
        
        # Filtrar y agregar
        for nombre, info in self.cheatsheets_data.items():
            titulo = info.get('titulo', nombre).lower()
            cat_info = info.get('categoria', 'general')
            nivel = info.get('nivel', 'intermedio')
            
            # Filtro de búsqueda
            if busqueda and busqueda not in titulo and busqueda not in nombre.lower():
                continue
            
            # Filtro de categoría
            if categoria != "todas" and cat_info != categoria:
                continue
            
            # Agregar al TreeView
            self.tree_cheatsheets.insert('', 'end', iid=nombre, 
                                       values=(info.get('titulo', nombre), cat_info, nivel))
    
    def _seleccionar_cheatsheet(self, event=None):
        """Manejar selección de cheatsheet"""
        if not self.tree_cheatsheets:
            self.logger.warning("tree_cheatsheets no inicializado, omitiendo selección")
            return
            
        seleccion = self.tree_cheatsheets.selection()
        if seleccion:
            nombre = seleccion[0]
            self._cargar_contenido_cheatsheet(nombre)
    
    def _cargar_contenido_cheatsheet(self, nombre):
        """Cargar y mostrar contenido de un cheatsheet"""
        try:
            info = self.cheatsheets_data.get(nombre)
            if not info:
                return
            
            # Actualizar información
            self.titulo_label.configure(text=info.get('titulo', nombre))
            self.descripcion_label.configure(text=info.get('descripcion', ''))
            
            # Cargar archivo
            archivo = info.get('archivo', f"{nombre}.json")
            ruta_archivo = os.path.join(self.ruta_cheatsheets, archivo)
            
            if os.path.exists(ruta_archivo):
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    contenido = json.load(f)
                
                # Formatear y mostrar contenido
                texto_formateado = self._formatear_contenido(contenido)
                
                if self.text_contenido:
                    self.text_contenido.configure(state='normal')
                    self.text_contenido.delete(1.0, tk.END)
                    self.text_contenido.insert(1.0, texto_formateado)
                    
                    # Aplicar formato
                    self._aplicar_formato_sintaxis()
                    
                    self.text_contenido.configure(state='disabled')
                else:
                    self.logger.warning("text_contenido no inicializado, omitiendo carga de contenido")
                
                self.cheatsheet_actual = nombre
                
            else:
                if self.text_contenido:
                    self.text_contenido.configure(state='normal')
                    self.text_contenido.delete(1.0, tk.END)
                    self.text_contenido.insert(1.0, f"⚠️ Archivo no encontrado: {archivo}")
                    self.text_contenido.configure(state='disabled')
                else:
                    self.logger.warning("text_contenido no inicializado, omitiendo mensaje de error")
                
        except Exception as e:
            self.logger.error(f"Error cargando contenido de {nombre}: {e}")
            if self.text_contenido:
                self.text_contenido.configure(state='normal')
                self.text_contenido.delete(1.0, tk.END)
                self.text_contenido.insert(1.0, f"❌ Error cargando contenido:\n{str(e)}")
                self.text_contenido.configure(state='disabled')
            else:
                self.logger.warning("text_contenido no inicializado, omitiendo mensaje de error")
    
    def _formatear_contenido(self, contenido):
        """Formatear contenido JSON a texto legible"""
        texto = ""
        
        # Metadatos
        if 'metadatos' in contenido:
            meta = contenido['metadatos']
            texto += f"📋 {meta.get('descripcion', 'CheatSheet')}\n"
            texto += f"👤 Autor: {meta.get('autor', 'Desconocido')}\n"
            texto += f"📅 Versión: {meta.get('version', '1.0.0')}\n"
            texto += f"📆 Actualizado: {meta.get('fecha_actualizacion', 'N/A')}\n"
            texto += "="*80 + "\n\n"
        
        # Categorías y herramientas
        if 'categorias' in contenido:
            for cat_nombre, categoria in contenido['categorias'].items():
                texto += f"🏷️ {categoria.get('titulo', cat_nombre.upper())}\n"
                texto += f"📝 {categoria.get('descripcion', '')}\n"
                texto += "-"*60 + "\n\n"
                
                # Herramientas en la categoría
                if 'herramientas' in categoria:
                    for herr_nombre, herramienta in categoria['herramientas'].items():
                        texto += f"🔧 {herr_nombre.upper()}\n"
                        texto += f"   {herramienta.get('descripcion', '')}\n\n"
                        
                        # Comandos
                        if 'comandos' in herramienta:
                            for cmd in herramienta['comandos']:
                                texto += f"   💾 {cmd.get('comando', '')}\n"
                                texto += f"      📋 {cmd.get('descripcion', '')}\n"
                                if 'ejemplo' in cmd:
                                    texto += f"      💡 Ejemplo: {cmd['ejemplo']}\n"
                                texto += "\n"
                        
                        texto += "\n"
                
                texto += "\n"
        
        return texto
    
    def _aplicar_formato_sintaxis(self):
        """Aplicar formato de sintaxis al contenido"""
        if not self.text_contenido:
            self.logger.warning("text_contenido no inicializado, omitiendo formato de sintaxis")
            return
            
        contenido = self.text_contenido.get(1.0, tk.END)
        lines = contenido.split('\n')
        
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            line_end = f"{i+1}.end"
            
            if line.startswith("🏷️"):
                self.text_contenido.tag_add("categoria", line_start, line_end)
            elif line.startswith("🔧"):
                self.text_contenido.tag_add("herramienta", line_start, line_end)
            elif line.strip().startswith("💾"):
                self.text_contenido.tag_add("comando", line_start, line_end)
            elif line.strip().startswith("📋"):
                self.text_contenido.tag_add("descripcion", line_start, line_end)
            elif line.strip().startswith("💡"):
                self.text_contenido.tag_add("ejemplo", line_start, line_end)
    
    def _copiar_contenido(self):
        """Copiar contenido actual al portapapeles"""
        try:
            if not self.text_contenido:
                messagebox.showwarning("Error", "Vista no inicializada correctamente")
                return
                
            contenido = self.text_contenido.get(1.0, tk.END)
            self.text_contenido.clipboard_clear()
            self.text_contenido.clipboard_append(contenido)
            messagebox.showinfo("Copiado", "📋 Contenido copiado al portapapeles")
            
        except Exception as e:
            self.logger.error(f"Error copiando contenido: {e}")
            messagebox.showerror("Error", f"Error copiando contenido:\n{str(e)}")
    
    def _nuevo_cheatsheet(self):
        """Crear nuevo cheatsheet"""
        # TODO: Implementar editor de cheatsheet
        messagebox.showinfo("Próximamente", "🚧 Función en desarrollo")
    
    def _importar_cheatsheet(self):
        """Importar cheatsheet desde archivo"""
        # TODO: Implementar importación
        messagebox.showinfo("Próximamente", "🚧 Función en desarrollo")
    
    def _exportar_cheatsheet(self):
        """Exportar cheatsheet actual"""
        # TODO: Implementar exportación
        messagebox.showinfo("Próximamente", "🚧 Función en desarrollo")
    
    def _editar_cheatsheet(self, event=None):
        """Editar cheatsheet seleccionado"""
        # TODO: Implementar editor
        messagebox.showinfo("Próximamente", "🚧 Función en desarrollo")
    
    def _eliminar_cheatsheet(self):
        """Eliminar cheatsheet seleccionado"""
        # TODO: Implementar eliminación
        messagebox.showinfo("Próximamente", "🚧 Función en desarrollo")
    
    def _duplicar_cheatsheet(self):
        """Duplicar cheatsheet seleccionado"""
        # TODO: Implementar duplicación
        messagebox.showinfo("Próximamente", "🚧 Función en desarrollo")
    
    def _guardar_cambios(self):
        """Guardar cambios en el cheatsheet actual"""
        # TODO: Implementar guardado
        messagebox.showinfo("Próximamente", "🚧 Función en desarrollo")
    
    def _recargar_cheatsheet(self):
        """Recargar cheatsheet actual"""
        if self.cheatsheet_actual:
            self._cargar_contenido_cheatsheet(self.cheatsheet_actual)
            messagebox.showinfo("Recargado", "🔄 CheatSheet recargado")
    
    def _limpiar_contenedor(self):
        """Limpiar el contenedor padre de forma segura"""
        try:
            for widget in self.contenedor_padre.winfo_children():
                try:
                    widget.destroy()
                except tk.TclError:
                    pass
        except tk.TclError:
            pass
    
    def destruir_vista(self):
        """Limpiar recursos al destruir la vista"""
        try:
            self.cheatsheets_data.clear()
            self._limpiar_contenedor()
            self.logger.info("Vista CheatSheets destruida")
        except Exception as e:
            self.logger.error(f"Error destruyendo vista CheatSheets: {e}")
