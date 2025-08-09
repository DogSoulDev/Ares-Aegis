#!/usr/bin/env python3
"""
Vista Constructor de Wordlists para Ares Aegis
Sistema avanzado para gestión, edición y creación de wordlists
"""

from ares_aegis.utils.utils_imports_comunes import (
    tk, ttk, messagebox, filedialog, logging, os, time, threading
)
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
from datetime import datetime
from pathlib import Path


class VistaConstructorWordlists:
    """
    Constructor de Wordlists Avanzado para Ares Aegis
    
    Características:
    - Gestión completa de wordlists existentes
    - Edición y modificación de listas
    - Exportación a archivos
    - Importación desde archivos
    - Interfaz moderna y funcional
    """
    
    def __init__(self, contenedor_padre, controlador, colores):
        """Inicializar vista del constructor de wordlists"""
        self.contenedor_padre = contenedor_padre
        self.controlador = controlador
        self.colores = colores
        
        # Configurar logging básico
        self.logger = logging.getLogger(__name__)
        
        # Estado de la aplicación
        self.frame_principal = None
        self.wordlists_disponibles = []
        self.lista_seleccionada = None
        self.palabras_actuales = []
        
        # Configurar directorio de wordlists
        self.directorio_wordlists = Path("data/wordlists")
        self.directorio_wordlists.mkdir(parents=True, exist_ok=True)
        
        # Colores básicos si no se proporcionan
        if not hasattr(colores, 'fondo_primario'):
            self._configurar_colores_basicos()
    
    def _configurar_colores_basicos(self):
        """Configurar colores básicos si no se proporcionan"""
        class ColoresBasicos:
            fondo_primario = "#0D1117"
            fondo_secundario = "#21262D"
            fondo_terciario = "#30363D"
            texto_primario = "#F0F6FC"
            texto_secundario = "#8B949E"
            acento_primario = "#00FF41"
            acento_secundario = "#367BF0"
            borde = "#30363D"
            
        self.colores = ColoresBasicos()
    
    def mostrar_informacion(self):
        """Mostrar información de ayuda sobre el Constructor de Wordlists"""
        info_text = """ CONSTRUCTOR DE WORDLISTS AVANZADO - ARSENAL DIGITAL

 FUNCIONALIDADES PRINCIPALES:
• Gestión integral y profesional de wordlists especializadas
• Edición avanzada de listas existentes con herramientas inteligentes
• Creación personalizada de diccionarios desde cero con algoritmos
• Importación masiva desde archivos externos con validación automática
• Exportación optimizada para herramientas de pentesting especializadas

[TARGET] HERRAMIENTAS DE CONSTRUCCIÓN INTELIGENTE:
• Generador automático de mutaciones con reglas personalizables
• Combinador inteligente de múltiples wordlists con deduplicación
• Filtrado avanzado por longitud, complejidad y patrones específicos
• Análisis estadístico de efectividad de diccionarios existentes

[TOOL] PROCESO DE CONSTRUCCIÓN PROFESIONAL:
1. Selecciona wordlists base de nuestra biblioteca especializada
2. Aplica mutaciones inteligentes (mayúsculas, números, símbolos)
3. Combina múltiples listas con algoritmos de optimización
4. Filtra resultados según criterios específicos del objetivo
5. Exporta en formatos compatibles con herramientas de hacking ético

 GESTIÓN AVANZADA DE ARCHIVOS:
• Importación masiva: Carga simultánea de múltiples archivos .txt
• Exportación optimizada: Formatos compatibles con Hydra, John, Hashcat
• Edición en tiempo real: Modificación instantánea con vista previa
• Creación desde cero: Generadores automáticos basados en patrones

 ALGORITMOS DE GENERACIÓN ESPECIALIZADOS:
• Mutaciones linguïsticas: l33t speak, inversiones, sustituciones
• Generación por patrones: fechas, nombres, combinaciones lógicas
• Análisis de frecuencia: palabras más comunes según contexto
• Generación probabilística: basada en estadísticas de contraseñas reales

[TARGET] CASOS DE USO PROFESIONALES EN CIBERSEGURIDAD:
• Auditorías de contraseñas con diccionarios especializados por sector
• Pentesting dirigido con wordlists personalizadas para cada objetivo
• Investigación forense con diccionarios específicos del sospechoso
• Red Team Operations con listas de reconocimiento OSINT avanzado

[STATS] WORDLISTS ESPECIALIZADAS INCLUIDAS:
• Contraseñas comunes: Top 500 passwords más utilizadas globalmente
• Directorios web: Rutas comunes de aplicaciones y frameworks
• Subdominios: Patrones de naming empresarial y tecnológico
• Usuarios comunes: Nombres de usuario estándar por plataforma
• API endpoints: Rutas comunes de servicios web y microservicios

 ANÁLISIS Y OPTIMIZACIÓN INTELIGENTE:
• Análisis de efectividad: Estadísticas de éxito por tipo de wordlist
• Optimización automática: Reordenamiento por probabilidad de éxito
• Detección de duplicados: Eliminación inteligente con preservación de variantes
• Análisis de entropía: Medición de complejidad y diversidad de diccionarios

 GENERACIÓN BASADA EN INTELIGENCIA:
• OSINT integration: Generación basada en información recopilada del objetivo
• Social engineering: Wordlists basadas en información personal conocida
• Análisis de patrones: Identificación de esquemas de naming organizacionales
• Machine learning: Predicción de contraseñas basada en comportamientos históricos

 CARACTERÍSTICAS AVANZADAS:
• Multi-threading: Procesamiento paralelo de wordlists masivas
• Memory optimization: Manejo eficiente de diccionarios de millones de entradas
• Progress tracking: Seguimiento detallado del progreso de generación
• Validation engine: Verificación automática de calidad de wordlists

 CONSIDERACIONES ÉTICAS Y LEGALES:
• Uso exclusivo para auditorías autorizadas y hacking ético
• Documentación obligatoria de pruebas de penetración legítimas
• Respeto absoluto a términos de servicio y marcos legales
• Responsabilidad profesional en el uso de herramientas de ciberseguridad

[LOCK] INTEGRACIÓN CON HERRAMIENTAS PROFESIONALES:
• Hydra: Formato optimizado para ataques de fuerza bruta en servicios
• John the Ripper: Wordlists especializadas para cracking de hashes
• Hashcat: Diccionarios optimizados para GPU cracking avanzado
• Burp Suite: Listas personalizadas para fuzzing de aplicaciones web
• Nmap: Wordlists para enumeración de servicios y directorios

 OPTIMIZADO PARA KALI LINUX:
• Integración nativa con distribuciones de pentesting especializadas
• Compatibilidad completa con herramientas OSINT y reconnaissance
• Sincronización automática con SecLists y repositorios especializados
• Integración con frameworks de automatización como AutoRecon y Amass"""
        
        messagebox.showinfo("Información - Constructor de Wordlists", info_text)
    
    def crear_vista(self, area_contenido=None):
        """Crear la vista principal del constructor de wordlists"""
        try:
            self.logger.info("Creando vista Constructor de Wordlists...")
            
            # Limpiar contenedor
            for widget in self.contenedor_padre.winfo_children():
                widget.destroy()
            
            # Frame principal con padding estandarizado
            self.frame_principal = tk.Frame(
                self.contenedor_padre,
                bg=self.colores.fondo_primario
            )
            self.frame_principal.pack(fill='both', expand=True, padx=20, pady=10)
            
            # Configurar grid
            self.frame_principal.grid_rowconfigure(1, weight=1)
            self.frame_principal.grid_columnconfigure(1, weight=1)
            
            # Crear header
            self._crear_header()
            
            # Crear contenido principal
            self._crear_contenido_principal()
            
            # Cargar wordlists disponibles
            self._cargar_wordlists()
            
            self.logger.info("Vista Constructor de Wordlists creada exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error creando vista: {e}")
            self._mostrar_error(f"Error creando la vista: {e}")
    
    def _crear_header(self):
        """Crear el header de la vista"""
        header_frame = tk.Frame(
            self.frame_principal,
            bg=self.colores.fondo_secundario,
            height=80
        )
        header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        header_frame.grid_propagate(False)
        
        # Título
        titulo = tk.Label(
            header_frame,
            text="[TOOL] Constructor de Wordlists Avanzado",
            font=('Consolas', 16, 'bold'),
            bg=self.colores.fondo_secundario,
            fg=self.colores.texto_primario
        )
        titulo.pack(side='left', padx=20, pady=20)
        
        # Botón de información
        btn_info = tk.Button(
            header_frame,
            text=" Info",
            font=('Consolas', 10),
            bg=self.colores.acento_secundario,
            fg='white',
            command=self.mostrar_informacion,
            relief='flat',
            padx=15,
            pady=5
        )
        btn_info.pack(side='right', padx=20, pady=20)
    
    def _crear_contenido_principal(self):
        """Crear el contenido principal con panel izquierdo y derecho"""
        # Panel izquierdo - Lista de wordlists
        self._crear_panel_izquierdo()
        
        # Panel derecho - Editor y controles
        self._crear_panel_derecho()
    
    def _crear_panel_izquierdo(self):
        """Crear panel izquierdo con lista de wordlists"""
        # Frame izquierdo
        left_frame = tk.Frame(
            self.frame_principal,
            bg=self.colores.fondo_secundario,
            width=300
        )
        left_frame.grid(row=1, column=0, sticky='nsew', padx=(0, 5))
        left_frame.grid_propagate(False)
        
        # Título del panel
        titulo_lista = tk.Label(
            left_frame,
            text=" Wordlists Disponibles",
            font=('Consolas', 12, 'bold'),
            bg=self.colores.fondo_secundario,
            fg=self.colores.texto_primario
        )
        titulo_lista.pack(pady=10)
        
        # Frame para la lista con scrollbar
        lista_frame = tk.Frame(left_frame, bg=self.colores.fondo_secundario)
        lista_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Listbox con scrollbar
        scrollbar_lista = tk.Scrollbar(lista_frame)
        scrollbar_lista.pack(side='right', fill='y')
        
        self.listbox_wordlists = tk.Listbox(
            lista_frame,
            font=('Consolas', 10),
            bg=self.colores.fondo_terciario,
            fg=self.colores.texto_primario,
            selectbackground=self.colores.acento_primario,
            yscrollcommand=scrollbar_lista.set,
            relief='flat'
        )
        self.listbox_wordlists.pack(side='left', fill='both', expand=True)
        scrollbar_lista.config(command=self.listbox_wordlists.yview)
        
        # Bind para selección
        self.listbox_wordlists.bind('<<ListboxSelect>>', self._on_lista_seleccionada)
        
        # Botones de gestión
        botones_frame = tk.Frame(left_frame, bg=self.colores.fondo_secundario)
        botones_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Botón crear nueva lista
        btn_nueva = tk.Button(
            botones_frame,
            text=" Nueva Lista",
            font=('Consolas', 9),
            bg=self.colores.acento_primario,
            fg='black',
            command=self._crear_nueva_lista,
            relief='flat',
            padx=10,
            pady=5
        )
        btn_nueva.pack(fill='x', pady=2)
        
        # Botón importar
        btn_importar = tk.Button(
            botones_frame,
            text=" Importar",
            font=('Consolas', 9),
            bg=self.colores.acento_secundario,
            fg='white',
            command=self._importar_wordlist,
            relief='flat',
            padx=10,
            pady=5
        )
        btn_importar.pack(fill='x', pady=2)
    
    def _crear_panel_derecho(self):
        """Crear panel derecho con editor y controles"""
        # Frame derecho
        right_frame = tk.Frame(
            self.frame_principal,
            bg=self.colores.fondo_secundario
        )
        right_frame.grid(row=1, column=1, sticky='nsew', padx=(5, 0))
        
        # Título del editor
        titulo_editor = tk.Label(
            right_frame,
            text=" Editor de Wordlist",
            font=('Consolas', 12, 'bold'),
            bg=self.colores.fondo_secundario,
            fg=self.colores.texto_primario
        )
        titulo_editor.pack(pady=10)
        
        # Info de lista seleccionada
        self.label_info = tk.Label(
            right_frame,
            text="Selecciona una wordlist para editar",
            font=('Consolas', 10),
            bg=self.colores.fondo_secundario,
            fg=self.colores.texto_secundario
        )
        self.label_info.pack(pady=(0, 10))
        
        # Frame para el editor
        editor_frame = tk.Frame(right_frame, bg=self.colores.fondo_secundario)
        editor_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Text widget con scrollbar para editar
        scrollbar_editor = tk.Scrollbar(editor_frame)
        scrollbar_editor.pack(side='right', fill='y')
        
        self.text_editor = tk.Text(
            editor_frame,
            font=('Consolas', 10),
            bg=self.colores.fondo_terciario,
            fg=self.colores.texto_primario,
            insertbackground=self.colores.texto_primario,
            yscrollcommand=scrollbar_editor.set,
            relief='flat',
            state='disabled'
        )
        self.text_editor.pack(side='left', fill='both', expand=True)
        scrollbar_editor.config(command=self.text_editor.yview)
        
        # Frame para controles del editor
        controles_frame = tk.Frame(right_frame, bg=self.colores.fondo_secundario)
        controles_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Botón editar
        self.btn_editar = tk.Button(
            controles_frame,
            text=" Editar Lista",
            font=('Consolas', 10),
            bg=self.colores.acento_primario,
            fg='black',
            command=self._toggle_editar,
            relief='flat',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.btn_editar.pack(side='left', padx=(0, 5))
        
        # Botón guardar
        self.btn_guardar = tk.Button(
            controles_frame,
            text=" Guardar",
            font=('Consolas', 10),
            bg=self.colores.acento_secundario,
            fg='white',
            command=self._guardar_lista,
            relief='flat',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.btn_guardar.pack(side='left', padx=5)
        
        # Botón exportar
        self.btn_exportar = tk.Button(
            controles_frame,
            text=" Exportar",
            font=('Consolas', 10),
            bg='#28a745',
            fg='white',
            command=self._exportar_lista,
            relief='flat',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.btn_exportar.pack(side='right')
    
    def _cargar_wordlists(self):
        """Cargar wordlists disponibles"""
        try:
            # Limpiar lista
            self.listbox_wordlists.delete(0, 'end')
            self.wordlists_disponibles = []
            
            # Obtener wordlists del controlador
            if hasattr(self.controlador, 'constructor_wordlists'):
                listas = self.controlador.constructor_wordlists.obtener_nombres_listas_base()
                
                for nombre in listas:
                    self.listbox_wordlists.insert('end', nombre)
                    self.wordlists_disponibles.append(nombre)
                
                self.logger.info(f"Cargadas {len(listas)} wordlists")
            
        except Exception as e:
            self.logger.error(f"Error cargando wordlists: {e}")
    
    def _on_lista_seleccionada(self, event):
        """Manejar selección de lista"""
        try:
            selection = self.listbox_wordlists.curselection()
            if selection:
                index = selection[0]
                nombre_lista = self.wordlists_disponibles[index]
                self._cargar_lista_en_editor(nombre_lista)
                
        except Exception as e:
            self.logger.error(f"Error en selección: {e}")
    
    def _cargar_lista_en_editor(self, nombre_lista):
        """Cargar lista seleccionada en el editor"""
        try:
            self.lista_seleccionada = nombre_lista
            
            # Obtener palabras de la lista
            if hasattr(self.controlador, 'constructor_wordlists'):
                listas = self.controlador.constructor_wordlists.obtener_listas_base()
                self.palabras_actuales = listas.get(nombre_lista, [])
                
                # Actualizar editor
                self.text_editor.config(state='normal')
                self.text_editor.delete('1.0', 'end')
                
                for palabra in self.palabras_actuales:
                    self.text_editor.insert('end', palabra + '\n')
                
                self.text_editor.config(state='disabled')
                
                # Actualizar info
                self.label_info.config(
                    text=f"Lista: {nombre_lista} ({len(self.palabras_actuales)} palabras)"
                )
                
                # Habilitar botones
                self.btn_editar.config(state='normal')
                self.btn_exportar.config(state='normal')
                
        except Exception as e:
            self.logger.error(f"Error cargando lista en editor: {e}")
    
    def _toggle_editar(self):
        """Alternar modo de edición"""
        if self.text_editor.cget('state') == 'disabled':
            # Habilitar edición
            self.text_editor.config(state='normal')
            self.btn_editar.config(text=" Cancelar", bg='#dc3545')
            self.btn_guardar.config(state='normal')
        else:
            # Deshabilitar edición
            self.text_editor.config(state='disabled')
            self.btn_editar.config(text=" Editar Lista", bg=self.colores.acento_primario)
            self.btn_guardar.config(state='disabled')
            
            # Recargar contenido original
            if self.lista_seleccionada:
                self._cargar_lista_en_editor(self.lista_seleccionada)
    
    def _guardar_lista(self):
        """Guardar cambios en la lista"""
        try:
            if not self.lista_seleccionada:
                return
                
            # Obtener contenido del editor
            contenido = self.text_editor.get('1.0', 'end-1c')
            palabras = [linea.strip() for linea in contenido.split('\n') if linea.strip()]
            
            # Guardar usando el controlador
            if hasattr(self.controlador, 'constructor_wordlists'):
                success = self.controlador.constructor_wordlists.crear_lista_base(
                    self.lista_seleccionada, palabras
                )
                
                if success:
                    messagebox.showinfo("Éxito", "Lista guardada correctamente")
                    self.palabras_actuales = palabras
                    
                    # Actualizar info
                    self.label_info.config(
                        text=f"Lista: {self.lista_seleccionada} ({len(palabras)} palabras)"
                    )
                    
                    # Salir del modo edición
                    self._toggle_editar()
                else:
                    messagebox.showerror("Error", "Error guardando la lista")
            
        except Exception as e:
            self.logger.error(f"Error guardando lista: {e}")
            messagebox.showerror("Error", f"Error guardando: {e}")
    
    def _exportar_lista(self):
        """Exportar lista a archivo"""
        try:
            if not self.lista_seleccionada:
                messagebox.showwarning("Advertencia", "No hay lista seleccionada para exportar")
                return
                
            # Obtener palabras actuales desde el editor o desde el modelo
            palabras_a_exportar = []
            
            # Si estamos en modo edición, obtener del editor
            if self.text_editor.cget('state') == 'normal':
                contenido = self.text_editor.get('1.0', 'end-1c')
                palabras_a_exportar = [linea.strip() for linea in contenido.split('\n') if linea.strip()]
            else:
                # Si no estamos editando, obtener del modelo
                if hasattr(self.controlador, 'constructor_wordlists'):
                    listas = self.controlador.constructor_wordlists.obtener_listas_base()
                    palabras_a_exportar = listas.get(self.lista_seleccionada, [])
                else:
                    palabras_a_exportar = self.palabras_actuales
            
            if not palabras_a_exportar:
                messagebox.showwarning("Advertencia", "La lista está vacía")
                return
                
            # Abrir diálogo para guardar archivo
            archivo = filedialog.asksaveasfilename(
                title="Exportar Wordlist",
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=f"{self.lista_seleccionada}.txt"
            )
            
            if archivo:
                with open(archivo, 'w', encoding='utf-8') as f:
                    for palabra in palabras_a_exportar:
                        f.write(palabra + '\n')
                
                messagebox.showinfo("Éxito", f"Lista exportada exitosamente:\n{archivo}\n\nPalabras exportadas: {len(palabras_a_exportar)}")
                self.logger.info(f"Lista '{self.lista_seleccionada}' exportada a: {archivo}")
                
        except Exception as e:
            self.logger.error(f"Error exportando lista: {e}")
            messagebox.showerror("Error", f"Error exportando la lista:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def _importar_wordlist(self):
        """Importar wordlist desde archivo"""
        try:
            archivo = filedialog.askopenfilename(
                title="Importar Wordlist",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )
            
            if archivo:
                # Leer archivo
                with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                    palabras = [linea.strip() for linea in f if linea.strip()]
                
                if not palabras:
                    messagebox.showwarning("Advertencia", "El archivo está vacío o no contiene palabras válidas")
                    return
                
                # Solicitar nombre para la nueva lista
                from tkinter import simpledialog
                nombre = simpledialog.askstring(
                    "Nombre de Lista",
                    "Introduce un nombre para la wordlist:",
                    initialvalue=Path(archivo).stem
                )
                
                if nombre:
                    # Crear lista
                    if hasattr(self.controlador, 'constructor_wordlists'):
                        success = self.controlador.constructor_wordlists.crear_lista_base(nombre, palabras)
                        
                        if success:
                            messagebox.showinfo("Éxito", f"Wordlist '{nombre}' importada correctamente\n{len(palabras)} palabras")
                            self._cargar_wordlists()  # Recargar lista
                        else:
                            messagebox.showerror("Error", "Error creando la lista")
                
        except Exception as e:
            self.logger.error(f"Error importando wordlist: {e}")
            messagebox.showerror("Error", f"Error importando: {e}")
    
    def _crear_nueva_lista(self):
        """Crear nueva wordlist vacía"""
        try:
            from tkinter import simpledialog
            nombre = simpledialog.askstring(
                "Nueva Wordlist",
                "Introduce un nombre para la nueva wordlist:"
            )
            
            if nombre:
                # Crear lista vacía
                if hasattr(self.controlador, 'constructor_wordlists'):
                    success = self.controlador.constructor_wordlists.crear_lista_base(nombre, [])
                    
                    if success:
                        messagebox.showinfo("Éxito", f"Wordlist '{nombre}' creada correctamente")
                        self._cargar_wordlists()  # Recargar lista
                    else:
                        messagebox.showerror("Error", "Error creando la lista")
                
        except Exception as e:
            self.logger.error(f"Error creando nueva lista: {e}")
            messagebox.showerror("Error", f"Error creando: {e}")
    
    def _mostrar_error(self, mensaje):
        """Mostrar mensaje de error"""
        messagebox.showerror("Error - Constructor de Wordlists", mensaje)
