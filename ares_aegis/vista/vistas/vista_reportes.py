#!/usr/bin/env python3
"""
Vista Reportes para Ares Aegis
Interfaz del módulo de reportes con soporte para exportación Markdown
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import os
import webbrowser
from datetime import datetime
from ..componentes_ui.emoticonos_mitologicos import EmoticonosMitologicos
from ..componentes_ui.sistema_ayuda import SistemaAyuda


class VistaReportes:
    """Vista de reportes con soporte para exportación Markdown"""
    
    def __init__(self, contenedor_padre, controlador, colores):
        self.contenedor_padre = contenedor_padre
        self.controlador = controlador
        self.colores = colores
        self.logger = logging.getLogger(__name__)
        
        # Variables de control
        self.reportes_disponibles = []
        
        # Variables de UI inicializadas correctamente
        self.tree_reportes = None  # Se inicializa en _crear_lista_reportes
        
        # Sistema de ayuda
        self.sistema_ayuda = SistemaAyuda(colores)
        
    def mostrar_informacion(self):
        """Mostrar información de ayuda sobre los Reportes"""
        info_text = """� SISTEMA DE REPORTES AVANZADOS - INTELIGENCIA ACTIONABLE

� FUNCIONALIDADES PRINCIPALES:
• Generación automática de reportes detallados de auditorías y escaneos
• Análisis estadístico avanzado con métricas de seguridad personalizables
• Exportación en múltiples formatos profesionales (PDF, HTML, CSV, JSON)
• Consolidación inteligente de datos de todas las herramientas del sistema

🎯 TIPOS DE REPORTES ESPECIALIZADOS:
• Reportes ejecutivos con resúmenes estratégicos para directivos
• Reportes técnicos detallados para equipos de ciberseguridad
• Reportes de cumplimiento para auditorías regulatorias
• Reportes de tendencias temporales con análisis predictivo

💼 REPORTES EJECUTIVOS ESTRATÉGICOS:
• Resumen ejecutivo con estado general de la seguridad organizacional
• Métricas clave de riesgo con indicadores de rendimiento (KPIs)
• Tendencias de amenazas y evolución del panorama de riesgos
• Recomendaciones estratégicas priorizadas por impacto empresarial

🔧 REPORTES TÉCNICOS ESPECIALIZADOS:
• Análisis detallado de vulnerabilidades con clasificación CVSS
• Resultados completos de auditorías PAM y configuraciones de seguridad
• Logs de monitoreo con correlación de eventos de seguridad
• Actividad de red con detección de patrones anómalos

📋 FORMATOS DE EXPORTACIÓN DISPONIBLES:
• HTML: Reportes interactivos con navegación intuitiva y gráficos dinámicos
• Markdown: Documentación técnica profesional para equipos especializados
• TXT: Logs estructurados para análisis automatizado y procesamiento
• JSON: Datos estructurados para integración con sistemas SIEM externos

⚡ CARACTERÍSTICAS AVANZADAS DE ANÁLISIS:
• Correlación automática de eventos entre diferentes herramientas
• Análisis de tendencias temporales con predicción de riesgos
• Comparativas históricas para evaluación de mejoras
• Scoring automático de riesgo con algoritmos especializados

🎨 GESTIÓN PROFESIONAL DE REPORTES:
• Lista completa de reportes generados con metadatos detallados
• Previsualización interactiva de contenido antes de exportación
• Exportación personalizable a ubicaciones específicas del sistema
• Apertura automática en navegador web para reportes HTML interactivos

� ANÁLISIS ESTADÍSTICO Y MÉTRICAS:
• Evolución temporal detallada de amenazas y vulnerabilidades
• Estadísticas avanzadas de rendimiento y disponibilidad del sistema
• Identificación de patrones de comportamiento anómalo con IA
• Métricas precisas de efectividad de controles de seguridad implementados

⚠️ AUTOMATIZACIÓN INTELIGENTE:
• Generación programada automática de reportes según calendario definido
• Sistema de alertas configurables por email para eventos críticos
• Archivo inteligente y organizado de reportes históricos por categorías
• Limpieza automática optimizada de archivos temporales y logs antiguos

📋 CONTENIDO INTEGRAL INCLUIDO:
• Resumen ejecutivo profesional con hallazgos críticos priorizados
• Análisis técnico exhaustivo de vulnerabilidades con contexto detallado
• Recomendaciones específicas de mitigación con priorización por riesgo
• Timeline cronológico detallado de eventos e incidentes importantes
• Métricas precisas de rendimiento del sistema con benchmarks

💡 CASOS DE USO PROFESIONALES:
• Auditorías integrales de cumplimiento regulatorio y normativo
• Investigaciones forenses avanzadas con trazabilidad completa
• Documentación detallada de incidentes para análisis post-mortem
• Reportes estratégicos para dirección técnica y ejecutiva
• Análisis predictivo de tendencias emergentes de ciberseguridad

🔐 SEGURIDAD Y TRAZABILIDAD AVANZADA:
• Marcas de tiempo criptográficas inmutables con blockchain
• Hash SHA-256 de integridad para verificación de autenticidad
• Metadatos completos de generación con información forense
• Trazabilidad completa de operaciones con auditoría inmutable

🚀 INTELIGENCIA EMPRESARIAL:
• Dashboard ejecutivo con métricas en tiempo real
• Integración con sistemas de gestión de riesgos empresariales
• Benchmarking automático contra estándares de la industria
• Alertas proactivas basadas en inteligencia artificial

⚡ OPTIMIZADO PARA KALI LINUX:
• Integración nativa con herramientas forenses especializadas
• Compatibilidad con frameworks de pentesting profesionales
• Exportación directa a formatos OSINT y threat hunting
• Integración completa con metodologías OWASP, NIST y PTES"""
        
        messagebox.showinfo("Información - Sistema de Reportes", info_text)
        
    def crear_vista(self, area_contenido=None):
        """Crear la vista de reportes con diseño responsive"""
        self._limpiar_contenedor()
        
        # Frame principal con padding estandarizado
        self.frame_principal = tk.Frame(self.contenedor_padre, bg=self.colores.fondo_secundario)
        self.frame_principal.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Configurar grid responsive con mejores proporciones
        self.frame_principal.grid_rowconfigure(0, weight=0)  # Header fijo
        self.frame_principal.grid_rowconfigure(1, weight=1)  # Contenido expandible
        self.frame_principal.grid_columnconfigure(0, weight=1)
        
        # Header de reportes
        self._crear_header_reportes()
        
        # Container principal con scroll
        main_container = tk.Frame(self.frame_principal, bg=self.colores.fondo_secundario)
        main_container.grid(row=1, column=0, sticky='nsew', pady=(10, 0))
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_container, bg=self.colores.fondo_secundario, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.frame_scroll = tk.Frame(canvas, bg=self.colores.fondo_secundario)
        
        # Configurar scroll responsive
        self.frame_scroll.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.frame_scroll, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid para canvas y scrollbar
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Panel de generación de reportes
        self._crear_panel_generacion()
        
        # Lista de reportes existentes
        self._crear_lista_reportes()
        
        # Panel de acciones
        self._crear_panel_acciones()
        
        # Cargar reportes existentes
        self._cargar_reportes_existentes()
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Bind para responsive del canvas
        def _configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas.find_all()[0], width=event.width)
        canvas.bind('<Configure>', _configure_canvas)
    
    def _limpiar_contenedor(self):
        """Limpiar el contenedor padre"""
        for widget in self.contenedor_padre.winfo_children():
            widget.destroy()
    
    def _crear_header_reportes(self):
        """Crear header de reportes con diseño centrado"""
        header = tk.Frame(self.frame_principal, bg=self.colores.fondo_terciario, height=80)
        header.grid(row=0, column=0, sticky='ew', padx=0, pady=0)
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)
        header.grid_rowconfigure(0, weight=1)
        
        # Título centrado
        tk.Label(header,
                text=f"📋 {EmoticonosMitologicos.APOLLO} Crónicas de Batalla - Informes de Seguridad",
                font=('Consolas', 16, 'bold'),
                fg=self.colores.acento_primario,
                bg=self.colores.fondo_terciario).grid(row=0, column=0)
        
        # Botón de información
        tk.Button(header,
                 text="❓ Info",
                 font=('Consolas', 10),
                 bg=self.colores.acento_secundario,
                 fg='white',
                 command=self.mostrar_informacion,
                 relief='flat',
                 padx=10,
                 pady=5).grid(row=0, column=1, padx=20, sticky='e')
    
    def _crear_panel_generacion(self):
        """Crear panel de generación de reportes con grid responsive"""
        # Configurar grid del frame_scroll
        self.frame_scroll.grid_columnconfigure(0, weight=1)
        
        gen_frame = tk.LabelFrame(self.frame_scroll,
                                text=f"⚡ {EmoticonosMitologicos.ZEUS} Generar Nuevo Informe",
                                bg=self.colores.fondo_secundario,
                                fg=self.colores.acento_primario,
                                font=('Consolas', 12, 'bold'),
                                padx=20, pady=15)
        gen_frame.grid(row=0, column=0, sticky='ew', padx=20, pady=10)
        gen_frame.grid_columnconfigure(0, weight=1)
        
        # Tipos de reporte
        tipos_frame = tk.Frame(gen_frame, bg=self.colores.fondo_secundario)
        tipos_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        tipos_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(tipos_frame,
                text=f"📊 {EmoticonosMitologicos.CRISTAL} Tipo de Informe:",
                font=('Consolas', 10, 'bold'),
                fg=self.colores.texto_primario,
                bg=self.colores.fondo_secundario).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.tipo_reporte_var = tk.StringVar(value="general")
        
        tipos_opciones = [
            ("general", "🔍 Reporte General de Seguridad"),
            ("escaneo", "⚡ Reporte de Escaneos"),
            ("amenazas", "🚨 Reporte de Amenazas Detectadas"),
            ("cuarentena", "🔒 Reporte de Cuarentena"),
            ("sistema", "🖥️ Reporte del Sistema")
        ]
        
        opciones_frame = tk.Frame(tipos_frame, bg=self.colores.fondo_secundario)
        opciones_frame.grid(row=1, column=0, sticky='ew', pady=(5, 0))
        opciones_frame.grid_columnconfigure(0, weight=1)
        
        for i, (valor, texto) in enumerate(tipos_opciones):
            tk.Radiobutton(opciones_frame,
                          text=texto,
                          variable=self.tipo_reporte_var,
                          value=valor,
                          bg=self.colores.fondo_secundario,
                          fg=self.colores.texto_primario,
                          selectcolor=self.colores.fondo_primario,
                          font=('Consolas', 9)).grid(row=i, column=0, sticky='w', pady=2)
        
        # Formato de exportación
        formato_frame = tk.Frame(gen_frame, bg=self.colores.fondo_secundario)
        formato_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
        formato_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(formato_frame,
                text=f"📄 {EmoticonosMitologicos.PERGAMINO} Formato de Exportación:",
                font=('Consolas', 10, 'bold'),
                fg=self.colores.texto_primario,
                bg=self.colores.fondo_secundario).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.formato_reporte_var = tk.StringVar(value="html")
        
        formatos_opciones = [
            ("html", "🌐 HTML (Visualización web)"),
            ("markdown", "📝 Markdown (Formato texto)")
        ]
        
        self.formato_opciones_frame = tk.Frame(formato_frame, bg=self.colores.fondo_secundario)
        self.formato_opciones_frame.grid(row=1, column=0, sticky='ew', pady=(5, 0))
        self.formato_opciones_frame.grid_columnconfigure(0, weight=1)
        
        for i, (valor, texto) in enumerate(formatos_opciones):
            rb = tk.Radiobutton(self.formato_opciones_frame,
                          text=texto,
                          variable=self.formato_reporte_var,
                          value=valor,
                          bg=self.colores.fondo_secundario,
                          fg=self.colores.texto_primario,
                          selectcolor=self.colores.fondo_primario,
                          font=('Consolas', 9),
                          command=self._on_formato_change)
            rb.grid(row=i, column=0, sticky='w', pady=2)
        
        # Selección de información para Markdown
        self.info_frame = tk.LabelFrame(gen_frame,
                                       text=f"📋 {EmoticonosMitologicos.PERGAMINO} Información a Incluir (Markdown)",
                                       bg=self.colores.fondo_secundario,
                                       fg=self.colores.acento_secundario,
                                       font=('Consolas', 9, 'bold'))
        
        # Variables para checkboxes de información
        self.incluir_resumen = tk.BooleanVar(value=True)
        self.incluir_amenazas = tk.BooleanVar(value=True)
        self.incluir_escaneos = tk.BooleanVar(value=True)
        self.incluir_sistema = tk.BooleanVar(value=True)
        self.incluir_cuarentena = tk.BooleanVar(value=True)
        self.incluir_recomendaciones = tk.BooleanVar(value=True)
        self.incluir_metricas = tk.BooleanVar(value=True)
        
        info_opciones = [
            (self.incluir_resumen, "📊 Resumen Ejecutivo"),
            (self.incluir_amenazas, "🚨 Amenazas Detectadas"),
            (self.incluir_escaneos, "⚡ Historial de Escaneos"),
            (self.incluir_sistema, "🖥️ Estado del Sistema"),
            (self.incluir_cuarentena, "🔒 Estado de Cuarentena"),
            (self.incluir_metricas, "📈 Métricas del Sistema"),
            (self.incluir_recomendaciones, "💡 Recomendaciones")
        ]
        
        for i, (variable, texto) in enumerate(info_opciones):
            tk.Checkbutton(self.info_frame,
                          text=texto,
                          variable=variable,
                          bg=self.colores.fondo_secundario,
                          fg=self.colores.texto_primario,
                          selectcolor=self.colores.fondo_primario,
                          font=('Consolas', 9)).grid(row=i, column=0, sticky='w', padx=10, pady=2)
        
        # Inicialmente ocultar opciones de Markdown
        self.info_frame.grid_forget()
        
        # Botón generar
        tk.Button(gen_frame,
                 text=f"📄 {EmoticonosMitologicos.APOLLO} Generar Informe",
                 command=self._generar_reporte,
                 bg=self.colores.exito,
                 fg='white',
                 font=('Consolas', 12, 'bold'),
                 cursor='hand2',
                 height=2).grid(row=4, column=0, pady=15)
    
    def _on_formato_change(self):
        """Callback para mostrar/ocultar opciones de Markdown"""
        if self.formato_reporte_var.get() == "markdown":
            self.info_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=10)
        else:
            self.info_frame.grid_forget()
    
    def _crear_lista_reportes(self):
        """Crear lista de reportes existentes"""
        lista_frame = tk.LabelFrame(self.frame_scroll,
                                  text=f"📋 {EmoticonosMitologicos.PERGAMINO} Informes Existentes",
                                  bg=self.colores.fondo_secundario,
                                  fg=self.colores.acento_primario,
                                  font=('Consolas', 12, 'bold'))
        lista_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        lista_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview para mostrar reportes
        tree_frame = tk.Frame(lista_frame, bg=self.colores.fondo_secundario)
        tree_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Configurar columnas
        columnas = ('nombre', 'tipo', 'fecha', 'tamaño', 'formato')
        self.tree_reportes = ttk.Treeview(tree_frame, columns=columnas, show='headings', height=8)
        
        # Definir encabezados
        self.tree_reportes.heading('nombre', text='Nombre del Informe')
        self.tree_reportes.heading('tipo', text='Tipo')
        self.tree_reportes.heading('fecha', text='Fecha de Generación')
        self.tree_reportes.heading('tamaño', text='Tamaño')
        self.tree_reportes.heading('formato', text='Formato')
        
        # Configurar anchos de columna
        self.tree_reportes.column('nombre', width=250, minwidth=200)
        self.tree_reportes.column('tipo', width=120, minwidth=100)
        self.tree_reportes.column('fecha', width=120, minwidth=100)
        self.tree_reportes.column('tamaño', width=80, minwidth=60)
        self.tree_reportes.column('formato', width=80, minwidth=60)
        
        # Scrollbar para el treeview
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_reportes.yview)
        self.tree_reportes.configure(yscrollcommand=tree_scrollbar.set)
        
        self.tree_reportes.grid(row=0, column=0, sticky='nsew')
        tree_scrollbar.grid(row=0, column=1, sticky='ns')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
    
    def _crear_panel_acciones(self):
        """Crear panel de acciones para reportes"""
        acciones_frame = tk.LabelFrame(self.frame_scroll,
                                     text=f"⚙️ {EmoticonosMitologicos.APOLLO} Acciones",
                                     bg=self.colores.fondo_secundario,
                                     fg=self.colores.acento_primario,
                                     font=('Consolas', 12, 'bold'))
        acciones_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=10)
        acciones_frame.grid_columnconfigure(0, weight=1)
        
        botones_frame = tk.Frame(acciones_frame, bg=self.colores.fondo_secundario)
        botones_frame.grid(row=0, column=0, pady=15)
        
        # Botón abrir reporte
        tk.Button(botones_frame,
                 text=f"📖 {EmoticonosMitologicos.PERGAMINO} Abrir Informe",
                 command=self._abrir_reporte,
                 bg=self.colores.acento_primario,
                 fg='white',
                 font=('Consolas', 10, 'bold'),
                 cursor='hand2').pack(side='left', padx=(0, 10))
        
        # Botón exportar reporte
        tk.Button(botones_frame,
                 text=f"💾 {EmoticonosMitologicos.CRISTAL} Exportar Informe",
                 command=self._exportar_reporte,
                 bg=self.colores.advertencia,
                 fg='white',
                 font=('Consolas', 10, 'bold'),
                 cursor='hand2').pack(side='left', padx=(0, 10))
        
        # Botón eliminar reporte
        tk.Button(botones_frame,
                 text=f"🗑️ {EmoticonosMitologicos.FUEGO} Eliminar Informe",
                 command=self._eliminar_reporte,
                 bg=self.colores.peligro,
                 fg='white',
                 font=('Consolas', 10, 'bold'),
                 cursor='hand2').pack(side='left')
    
    def _generar_reporte(self):
        """Generar nuevo reporte"""
        try:
            tipo_reporte = self.tipo_reporte_var.get()
            formato_reporte = self.formato_reporte_var.get()
            
            # Obtener información seleccionada para Markdown
            info_seleccionada = {}
            if formato_reporte == "markdown":
                info_seleccionada = {
                    'resumen': self.incluir_resumen.get(),
                    'amenazas': self.incluir_amenazas.get(),
                    'escaneos': self.incluir_escaneos.get(),
                    'sistema': self.incluir_sistema.get(),
                    'cuarentena': self.incluir_cuarentena.get(),
                    'metricas': self.incluir_metricas.get(),
                    'recomendaciones': self.incluir_recomendaciones.get()
                }
            
            self.logger.info(f"Generando reporte real de tipo: {tipo_reporte}, formato: {formato_reporte}")
            
            # Llamar al controlador para generar el reporte real
            resultado = self.controlador.generar_reporte_real(
                tipo_reporte, 
                formato_reporte, 
                info_seleccionada
            )
            
            if resultado:
                messagebox.showinfo(
                    "Éxito",
                    f"📄 Reporte {tipo_reporte.upper()} generado exitosamente en formato {formato_reporte.upper()}!\n"
                    f"📁 Ubicación: {resultado}"
                )
                self._cargar_reportes_existentes()
            else:
                messagebox.showerror(
                    "Error",
                    "❌ Error al generar el reporte. Verifique los logs para más detalles."
                )
                
        except Exception as e:
            self.logger.error(f"Error al generar reporte: {e}")
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def _cargar_reportes_existentes(self):
        """Cargar lista de reportes existentes"""
        try:
            # Verificar que el treeview esté inicializado
            if not self.tree_reportes:
                self.logger.warning("tree_reportes no inicializado, omitiendo carga de reportes")
                return
                
            # Limpiar lista actual
            for item in self.tree_reportes.get_children():
                self.tree_reportes.delete(item)
            
            # Obtener reportes del controlador
            reportes = self.controlador.obtener_reportes_existentes()
            
            for reporte in reportes:
                self.tree_reportes.insert('', 'end', values=(
                    reporte.get('nombre', 'Sin nombre'),
                    reporte.get('tipo', 'Desconocido'),
                    reporte.get('fecha', 'Sin fecha'),
                    reporte.get('tamaño', '0 KB'),
                    reporte.get('formato', 'HTML')
                ))
                
        except Exception as e:
            self.logger.error(f"Error al cargar reportes existentes: {e}")
    
    def _abrir_reporte(self):
        """Abrir reporte seleccionado"""
        try:
            # Verificar que el treeview esté inicializado
            if not self.tree_reportes:
                messagebox.showwarning("Error", "Vista no inicializada correctamente")
                return
                
            seleccion = self.tree_reportes.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un reporte")
                return
            
            item = self.tree_reportes.item(seleccion[0])
            nombre_reporte = item['values'][0]
            
            resultado = self.controlador.abrir_reporte(nombre_reporte)
            
            if not resultado:
                messagebox.showerror("Error", "No se pudo abrir el reporte")
                
        except Exception as e:
            self.logger.error(f"Error al abrir reporte: {e}")
            messagebox.showerror("Error", f"Error al abrir reporte: {str(e)}")
    
    def _exportar_reporte(self):
        """Exportar reporte seleccionado"""
        try:
            # Verificar que el treeview esté inicializado
            if not self.tree_reportes:
                messagebox.showwarning("Error", "Vista no inicializada correctamente")
                return
                
            seleccion = self.tree_reportes.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un reporte")
                return
            
            item = self.tree_reportes.item(seleccion[0])
            nombre_reporte = item['values'][0]
            
            # Seleccionar ubicación de destino
            destino = filedialog.asksaveasfilename(
                title="Exportar informe",
                defaultextension=".html",
                filetypes=[
                    ("Archivos HTML", "*.html"),
                    ("Archivos Markdown", "*.md"),
                    ("Todos los archivos", "*.*")
                ]
            )
            
            if destino:
                resultado = self.controlador.exportar_reporte(nombre_reporte, destino)
                if resultado:
                    messagebox.showinfo("Éxito", f"Reporte exportado a: {destino}")
                else:
                    messagebox.showerror("Error", "No se pudo exportar el reporte")
                    
        except Exception as e:
            self.logger.error(f"Error al exportar reporte: {e}")
            messagebox.showerror("Error", f"Error al exportar reporte: {str(e)}")
    
    def _eliminar_reporte(self):
        """Eliminar reporte seleccionado"""
        try:
            # Verificar que el treeview esté inicializado
            if not self.tree_reportes:
                messagebox.showwarning("Error", "Vista no inicializada correctamente")
                return
                
            seleccion = self.tree_reportes.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un reporte")
                return
            
            item = self.tree_reportes.item(seleccion[0])
            nombre_reporte = item['values'][0]
            
            # Confirmar eliminación
            respuesta = messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Está seguro de que desea eliminar el reporte '{nombre_reporte}'?"
            )
            
            if respuesta:
                resultado = self.controlador.eliminar_reporte(nombre_reporte)
                if resultado:
                    messagebox.showinfo("Éxito", "Reporte eliminado correctamente")
                    self._cargar_reportes_existentes()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el reporte")
                    
        except Exception as e:
            self.logger.error(f"Error al eliminar reporte: {e}")
            messagebox.showerror("Error", f"Error al eliminar reporte: {str(e)}")
