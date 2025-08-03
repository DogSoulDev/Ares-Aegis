#!/usr/bin/env python3
"""
Vista Monitor para Ares Aegis
Interfaz del módulo de monitoreo del sistema optimizado para Kali Linux
"""
from ..componentes_ui.vista_base import VistaBase

from ...utils.imports_comunes import (
    tk, ttk, messagebox, filedialog, logging, os, time, threading
)
import subprocess
import re
from ..componentes_ui.emoticonos_mitologicos import EmoticonosMitologicos
from ..componentes_ui.sistema_ayuda import SistemaAyuda


class VistaMonitor(VistaBase):
    """Vista del monitor del sistema optimizada para Kali Linux"""
    
    def __init__(self, contenedor_padre, controlador, colores):
        super().__init__(contenedor_padre, controlador, colores)
        self.contenedor_padre = contenedor_padre
        self.controlador = controlador
        self.colores = colores
        self.logger = logging.getLogger(__name__)
        
        # Variables de control
        self.monitoreo_activo = False
        self.hilo_monitoreo = None
        
        # Variables de UI inicializadas correctamente
        self.resultados_text = None  # Se inicializa en _crear_area_resultados
        self.estado_var = tk.StringVar(value="🔴 DETENIDO")  # Inicializada con valor por defecto
        
        # Sistema de ayuda
        self.sistema_ayuda = SistemaAyuda(colores)
        
    # Método mostrar_informacion heredado de VistaBase
    # Para personalizar, implementar métodos abstractos:
    # _get_titulo_ventana() y _get_descripcion_funcionalidades()
        """Mostrar información de ayuda sobre el Monitor del Sistema"""
        
        info_text = """🛡️ MONITOR DEL SISTEMA - SUPERVISIÓN INTEGRAL

🔱 FUNCIONALIDADES PRINCIPALES:
• Monitoreo en tiempo real de todos los aspectos del sistema
• Análisis detallado de procesos y servicios en ejecución
• Supervisión avanzada de recursos (CPU, RAM, Red, Disco)
• Detección proactiva de actividad sospechosa y anomalías

⚡ HERRAMIENTAS DE ANÁLISIS INTEGRADAS:
• ps aux: Listado completo y detallado de todos los procesos
• netstat: Conexiones de red activas y puertos en escucha
• lsof: Archivos abiertos por procesos y descriptores de archivo
• htop: Monitor interactivo de recursos con gráficos en tiempo real
• ss: Estado avanzado de conexiones y sockets de red

🎯 MONITOREO AVANZADO Y MÉTRICAS:
• Uso detallado de CPU por proceso y núcleo
• Consumo de memoria RAM física y virtual por aplicación
• Conexiones de red entrantes y salientes con detalles
• Archivos y puertos abiertos con información de procesos
• Identificación de procesos que consumen más recursos

🔧 COMANDOS Y HERRAMIENTAS DISPONIBLES:
• Análisis forense de procesos sospechosos en tiempo real
• Revisión exhaustiva de conexiones de red activas
• Monitoreo continuo de archivos críticos del sistema
• Detección avanzada de procesos ocultos o rootkits
• Análisis de carga del sistema y cuellos de botella

⚠️ OPTIMIZADO ESPECÍFICAMENTE PARA KALI LINUX:
• Integración completa con herramientas nativas de Kali
• Comandos específicos de pentesting y auditoría de seguridad
• Detección especializada de rootkits y malware avanzado
• Análisis forense del sistema con herramientas profesionales
• Compatibilidad total con el ecosistema de ciberseguridad

📊 INTERPRETACIÓN AVANZADA DE DATOS:
• 🟢 NORMAL: Actividad estándar del sistema sin anomalías
• 🟡 ADVERTENCIA: Uso elevado de recursos que requiere atención
• 🔴 CRÍTICO: Actividad sospechosa detectada, investigación necesaria
• ⚫ ERROR: No se pudo obtener información, posible problema del sistema

💡 CONSEJOS PROFESIONALES DE USO:
• Ejecuta monitoreo periódicamente para establecer líneas base
• Revisa procesos con consumo anómalo de CPU o RAM
• Verifica conexiones de red inusuales o no autorizadas
• Analiza archivos abiertos por procesos sospechosos
• Documenta patrones normales para detectar desviaciones

🚀 FUNCIONALIDADES AVANZADAS:
• Actualización automática de métricas en tiempo real
• Filtrado inteligente de procesos por criterios específicos
• Exportación de datos de monitoreo para análisis posterior
• Alertas configurables para condiciones específicas
• Integración con sistemas de logging y SIEM

🔐 CASOS DE USO EN CIBERSEGURIDAD:
• Investigación forense de incidentes de seguridad
• Detección de actividad maliciosa en el sistema
• Monitoreo de procesos durante pruebas de penetración
• Análisis de rendimiento durante auditorías de seguridad
• Verificación de la integridad del sistema post-compromiso"""
        
        messagebox.showinfo("Información - Monitor del Sistema", info_text)
        
    def crear_vista(self, area_contenido=None):
        """Crear la vista del monitor dividida en Sistema y Red"""
        self._limpiar_contenedor()
        
        # Frame principal con padding estandarizado
        self.frame_principal = tk.Frame(self.contenedor_padre, bg=self.colores.fondo_secundario)
        self.frame_principal.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Configurar grid responsive
        self.frame_principal.grid_rowconfigure(0, weight=0)  # Header fijo
        self.frame_principal.grid_rowconfigure(1, weight=0)  # Controles fijos
        self.frame_principal.grid_rowconfigure(2, weight=1)  # Contenido principal expandible
        self.frame_principal.grid_columnconfigure(0, weight=1)
        
        # Header
        self._crear_header_monitor_dual(self.frame_principal)
        
        # Panel de control global
        self._crear_panel_control_dual(self.frame_principal)
        
        # Contenido principal dividido
        self._crear_contenido_dual(self.frame_principal)
        
    def _crear_header_monitor_dual(self, parent):
        """Crear header del monitor dual"""
        header_frame = tk.Frame(parent, bg=self.colores.negro_carbono, height=100)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        
        # Frame para títulos (centrado)
        titulo_frame = tk.Frame(header_frame, bg=self.colores.negro_carbono)
        titulo_frame.grid(row=0, column=0, pady=20)
        
        # Título principal
        titulo_label = tk.Label(titulo_frame,
                               text=f"🔱 {EmoticonosMitologicos.ARGOS} MONITOR DUAL DEL SISTEMA",
                               font=('Consolas', 20, 'bold'),
                               fg=self.colores.verde_terminal,
                               bg=self.colores.negro_carbono)
        titulo_label.pack()
        
        # Subtítulo
        subtitulo_label = tk.Label(titulo_frame,
                                  text="MONITOREO EN TIEMPO REAL • SISTEMA & RED",
                                  font=('Consolas', 10),
                                  fg=self.colores.gris_platino,
                                  bg=self.colores.negro_carbono)
        subtitulo_label.pack(pady=(5, 0))
        
        # Botón de información
        info_button = tk.Button(header_frame,
                               text="❓ Info",
                               font=('Consolas', 10),
                               bg=self.colores.verde_terminal,
                               fg=self.colores.negro_carbono,
                               command=self.mostrar_informacion,
                               relief='flat',
                               padx=15,
                               pady=8)
        info_button.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        
    def _crear_panel_control_dual(self, parent):
        """Crear panel de control dual"""
        control_frame = tk.Frame(parent, bg=self.colores.fondo_secundario)
        control_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)
        
        # Estado global
        estado_frame = tk.Frame(control_frame, bg=self.colores.fondo_terciario, relief='flat', bd=1)
        estado_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        tk.Label(estado_frame,
                text="ESTADO DEL MONITOR",
                font=('Consolas', 10, 'bold'),
                fg=self.colores.cyan_brillante,
                bg=self.colores.fondo_terciario).pack(pady=5)
        
        self.estado_label = tk.Label(estado_frame,
                                    textvariable=self.estado_var,
                                    font=('Consolas', 12, 'bold'),
                                    fg=self.colores.rojo_critico,
                                    bg=self.colores.fondo_terciario)
        self.estado_label.pack(pady=5)
        
        # Controles Sistema
        sistema_control_frame = tk.Frame(control_frame, bg=self.colores.fondo_terciario, relief='flat', bd=1)
        sistema_control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        tk.Label(sistema_control_frame,
                text="🖥️ MONITOR SISTEMA",
                font=('Consolas', 10, 'bold'),
                fg=self.colores.verde_terminal,
                bg=self.colores.fondo_terciario).pack(pady=5)
        
        self.btn_iniciar_sistema = tk.Button(sistema_control_frame,
                                           text="▶️ Iniciar Sistema",
                                           font=('Consolas', 9),
                                           bg=self.colores.verde_terminal,
                                           fg=self.colores.negro_carbono,
                                           command=self._iniciar_monitoreo_sistema,
                                           relief='flat',
                                           padx=10)
        self.btn_iniciar_sistema.pack(pady=2)
        
        self.btn_detener_sistema = tk.Button(sistema_control_frame,
                                           text="⏹️ Detener Sistema",
                                           font=('Consolas', 9),
                                           bg=self.colores.rojo_critico,
                                           fg=self.colores.blanco_hueso,
                                           command=self._detener_monitoreo_sistema,
                                           relief='flat',
                                           padx=10,
                                           state='disabled')
        self.btn_detener_sistema.pack(pady=2)
        
        # Controles Red
        red_control_frame = tk.Frame(control_frame, bg=self.colores.fondo_terciario, relief='flat', bd=1)
        red_control_frame.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        tk.Label(red_control_frame,
                text="🌐 MONITOR RED",
                font=('Consolas', 10, 'bold'),
                fg=self.colores.cyan_brillante,
                bg=self.colores.fondo_terciario).pack(pady=5)
        
        self.btn_iniciar_red = tk.Button(red_control_frame,
                                        text="▶️ Iniciar Red",
                                        font=('Consolas', 9),
                                        bg=self.colores.cyan_brillante,
                                        fg=self.colores.negro_carbono,
                                        command=self._iniciar_monitoreo_red,
                                        relief='flat',
                                        padx=10)
        self.btn_iniciar_red.pack(pady=2)
        
        self.btn_detener_red = tk.Button(red_control_frame,
                                        text="⏹️ Detener Red",
                                        font=('Consolas', 9),
                                        bg=self.colores.rojo_critico,
                                        fg=self.colores.blanco_hueso,
                                        command=self._detener_monitoreo_red,
                                        relief='flat',
                                        padx=10,
                                        state='disabled')
        self.btn_detener_red.pack(pady=2)
        
    def _crear_contenido_dual(self, parent):
        """Crear contenido dual dividido"""
        contenido_frame = tk.Frame(parent, bg=self.colores.fondo_secundario)
        contenido_frame.grid(row=2, column=0, sticky="nsew")
        contenido_frame.grid_rowconfigure(0, weight=1)
        contenido_frame.grid_columnconfigure(0, weight=1)
        contenido_frame.grid_columnconfigure(1, weight=1)
        
        # Panel Sistema (Izquierdo)
        self._crear_panel_sistema(contenido_frame)
        
        # Panel Red (Derecho)
        self._crear_panel_red(contenido_frame)
        
    def _crear_panel_sistema(self, parent):
        """Crear panel de monitoreo del sistema"""
        sistema_frame = tk.LabelFrame(parent,
                                     text="🖥️ MONITOREO DEL SISTEMA",
                                     font=('Consolas', 12, 'bold'),
                                     fg=self.colores.verde_terminal,
                                     bg=self.colores.fondo_secundario,
                                     relief='flat',
                                     bd=2)
        sistema_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        # Notebook para pestañas del sistema
        self.notebook_sistema = ttk.Notebook(sistema_frame)
        self.notebook_sistema.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña Procesos
        self.frame_procesos = tk.Frame(self.notebook_sistema, bg=self.colores.negro_carbono)
        self.notebook_sistema.add(self.frame_procesos, text="📊 Procesos")
        
        # Pestaña Recursos
        self.frame_recursos = tk.Frame(self.notebook_sistema, bg=self.colores.negro_carbono)
        self.notebook_sistema.add(self.frame_recursos, text="⚡ Recursos")
        
        # Pestaña Archivos
        self.frame_archivos = tk.Frame(self.notebook_sistema, bg=self.colores.negro_carbono)
        self.notebook_sistema.add(self.frame_archivos, text="📁 Archivos")
        
        # Crear contenido de pestañas del sistema
        self._crear_contenido_procesos()
        self._crear_contenido_recursos()
        self._crear_contenido_archivos()
        
    def _crear_panel_red(self, parent):
        """Crear panel de monitoreo de red"""
        red_frame = tk.LabelFrame(parent,
                                 text="🌐 MONITOREO DE RED",
                                 font=('Consolas', 12, 'bold'),
                                 fg=self.colores.cyan_brillante,
                                 bg=self.colores.fondo_secundario,
                                 relief='flat',
                                 bd=2)
        red_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        
        # Notebook para pestañas de red
        self.notebook_red = ttk.Notebook(red_frame)
        self.notebook_red.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña Conexiones
        self.frame_conexiones = tk.Frame(self.notebook_red, bg=self.colores.negro_carbono)
        self.notebook_red.add(self.frame_conexiones, text="🔗 Conexiones")
        
        # Pestaña Interfaces
        self.frame_interfaces = tk.Frame(self.notebook_red, bg=self.colores.negro_carbono)
        self.notebook_red.add(self.frame_interfaces, text="🔌 Interfaces")
        
        # Pestaña Tráfico
        self.frame_trafico = tk.Frame(self.notebook_red, bg=self.colores.negro_carbono)
        self.notebook_red.add(self.frame_trafico, text="📊 Tráfico")
        
        # Pestaña Seguridad
        self.frame_seguridad_red = tk.Frame(self.notebook_red, bg=self.colores.negro_carbono)
        self.notebook_red.add(self.frame_seguridad_red, text="🛡️ Seguridad")
        
        # Crear contenido de pestañas de red
        self._crear_contenido_conexiones()
        self._crear_contenido_interfaces()
        self._crear_contenido_trafico()
        self._crear_contenido_seguridad_red()
        
    def _limpiar_contenedor(self):
        """Limpiar el contenedor padre"""
        for widget in self.contenedor_padre.winfo_children():
            widget.destroy()
            
    def _crear_header_monitor(self, parent):
        """Crear header del monitor"""
        header_frame = tk.Frame(parent, bg=self.colores.negro_carbono, height=100)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        
        # Frame para títulos (centrado)
        titulo_frame = tk.Frame(header_frame, bg=self.colores.negro_carbono)
        titulo_frame.grid(row=0, column=0, pady=20)
        
        # Título principal
        titulo_label = tk.Label(titulo_frame,
                               text=f"🔱 {EmoticonosMitologicos.ARGOS} MONITOR DEL SISTEMA",
                               font=('Consolas', 20, 'bold'),
                               fg=self.colores.verde_terminal,
                               bg=self.colores.negro_carbono)
        titulo_label.pack()
        
        # Subtítulo
        subtitulo_label = tk.Label(titulo_frame,
                                  text="🐉 OPTIMIZADO PARA KALI LINUX",
                                  font=('Consolas', 12),
                                  fg=self.colores.cyan_brillante,
                                  bg=self.colores.negro_carbono)
        subtitulo_label.pack()
        
        # Botón de información
        tk.Button(header_frame,
                 text="❓ Info",
                 font=('Consolas', 10),
                 bg=self.colores.verde_terminal,
                 fg=self.colores.negro_carbono,
                 command=self.mostrar_informacion,
                 relief='flat',
                 padx=10,
                 pady=5).grid(row=0, column=1, padx=20, sticky='ne')
        
    def _crear_panel_control(self, parent):
        """Crear panel de control con botones"""
        control_frame = tk.LabelFrame(parent,
                                     text=f"🎛️ Panel de Control",
                                     bg=self.colores.fondo_secundario,
                                     fg=self.colores.verde_terminal,
                                     font=('Consolas', 12, 'bold'))
        control_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Frame interno para botones
        botones_frame = tk.Frame(control_frame, bg=self.colores.fondo_secundario)
        botones_frame.pack(fill='x', padx=20, pady=15)
        
        # Configurar grid para centrar botones
        for i in range(4):
            botones_frame.grid_columnconfigure(i, weight=1)
        
        # Estado del monitoreo
        self.estado_var = tk.StringVar(value="🔴 DETENIDO")
        estado_label = tk.Label(botones_frame,
                              textvariable=self.estado_var,
                              font=('Consolas', 14, 'bold'),
                              fg=self.colores.rojo_critico,
                              bg=self.colores.fondo_secundario)
        estado_label.grid(row=0, column=0, columnspan=4, pady=(0, 15))
        
        # Botones de control
        btn_iniciar = tk.Button(botones_frame,
                               text=f"▶️ INICIAR",
                               font=('Consolas', 11, 'bold'),
                               fg=self.colores.negro_carbono,
                               bg=self.colores.verde_terminal,
                               relief='flat',
                               cursor='hand2',
                               padx=20,
                               pady=8,
                               command=self._iniciar_monitoreo)
        btn_iniciar.grid(row=1, column=0, padx=5, sticky="ew")
        
        btn_detener = tk.Button(botones_frame,
                               text=f"⏹️ DETENER",
                               font=('Consolas', 11, 'bold'),
                               fg=self.colores.blanco_hueso,
                               bg=self.colores.rojo_critico,
                               relief='flat',
                               cursor='hand2',
                               padx=20,
                               pady=8,
                               command=self._detener_monitoreo)
        btn_detener.grid(row=1, column=1, padx=5, sticky="ew")
        
        btn_limpiar = tk.Button(botones_frame,
                               text=f"🧹 LIMPIAR",
                               font=('Consolas', 11, 'bold'),
                               fg=self.colores.negro_carbono,
                               bg=self.colores.amarillo_medio,
                               relief='flat',
                               cursor='hand2',
                               padx=20,
                               pady=8,
                               command=self._limpiar_resultados)
        btn_limpiar.grid(row=1, column=2, padx=5, sticky="ew")
        
        btn_reporte = tk.Button(botones_frame,
                               text=f"📊 REPORTE",
                               font=('Consolas', 11, 'bold'),
                               fg=self.colores.blanco_hueso,
                               bg=self.colores.cyan_brillante,
                               relief='flat',
                               cursor='hand2',
                               padx=20,
                               pady=8,
                               command=self._generar_reporte)
        btn_reporte.grid(row=1, column=3, padx=5, sticky="ew")
        
    def _crear_area_resultados(self, parent):
        """Crear área de resultados con scroll"""
        resultados_frame = tk.LabelFrame(parent,
                                        text=f"📋 Resultados de la Monitorización",
                                        bg=self.colores.fondo_secundario,
                                        fg=self.colores.verde_terminal,
                                        font=('Consolas', 12, 'bold'))
        resultados_frame.grid(row=2, column=0, sticky="nsew")
        
        # Frame interno con scroll
        texto_frame = tk.Frame(resultados_frame, bg=self.colores.negro_carbono)
        texto_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Text widget con scrollbar
        self.resultados_text = tk.Text(texto_frame,
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
        
        scrollbar = tk.Scrollbar(texto_frame, orient="vertical", command=self.resultados_text.yview)
        self.resultados_text.configure(yscrollcommand=scrollbar.set)
        
        self.resultados_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mensaje inicial
        self._agregar_resultado(f"🔱 {EmoticonosMitologicos.ARGOS} Monitor de Sistema Ares Aegis inicializado")
        self._agregar_resultado(f"🐉 Optimizado para Kali Linux - Usando herramientas nativas")
        self._agregar_resultado(f"⚡ Presiona INICIAR para comenzar el monitoreo en tiempo real")
        
    def _iniciar_monitoreo(self):
        """Iniciar el monitoreo del sistema"""
        if not self.monitoreo_activo:
            self.monitoreo_activo = True
            self.estado_var.set("🟢 MONITOREANDO")
            
            # Cambiar color del estado
            for widget in self.contenedor_padre.winfo_children():
                if hasattr(widget, 'winfo_children'):
                    self._actualizar_color_estado(widget, self.colores.verde_terminal)
            
            self._agregar_resultado(f"\\n🚀 {EmoticonosMitologicos.ARES} INICIANDO MONITOREO AVANZADO...")
            
            # Iniciar hilo de monitoreo
            self.hilo_monitoreo = threading.Thread(target=self._ejecutar_monitoreo_hilo)
            self.hilo_monitoreo.daemon = True
            self.hilo_monitoreo.start()
            
            self.logger.info("Monitor del sistema iniciado")
            
    def _detener_monitoreo(self):
        """Detener el monitoreo del sistema"""
        if self.monitoreo_activo:
            self.monitoreo_activo = False
            self.estado_var.set("🔴 DETENIDO")
            
            # Cambiar color del estado
            for widget in self.contenedor_padre.winfo_children():
                if hasattr(widget, 'winfo_children'):
                    self._actualizar_color_estado(widget, self.colores.rojo_critico)
            
            self._agregar_resultado(f"\\n⏹️ {EmoticonosMitologicos.ESCUDO} Monitoreo detenido por el usuario")
            
            self.logger.info("Monitor del sistema detenido")
    
    def _actualizar_color_estado(self, widget, color):
        """Actualizar color del estado recursivamente"""
        try:
            if hasattr(widget, 'config') and str(widget['text']).startswith(('🟢', '🔴')):
                widget.config(fg=color)
        except:
            pass
        
        try:
            for child in widget.winfo_children():
                self._actualizar_color_estado(child, color)
        except:
            pass
    
    def _limpiar_resultados(self):
        """Limpiar el área de resultados"""
        try:
            # Verificar que el widget esté inicializado
            if not self.resultados_text:
                self.logger.warning("resultados_text no inicializado, omitiendo limpieza")
                return
                
            self.resultados_text.config(state='normal')
            self.resultados_text.delete(1.0, tk.END)
            self.resultados_text.config(state='disabled')
            
            # Mensaje inicial
            self._agregar_resultado(f"🧹 {EmoticonosMitologicos.CRISTAL} Resultados limpiados")
            
        except Exception as e:
            self.logger.error(f"Error limpiando resultados: {e}")
    
    def _generar_reporte(self):
        """Generar reporte del sistema"""
        try:
            self._agregar_resultado(f"\\n📊 {EmoticonosMitologicos.PERGAMINO} GENERANDO REPORTE DEL SISTEMA...")
            
            # Obtener información del sistema
            self._agregar_resultado(f"🖥️ Sistema: {self._obtener_info_sistema()}")
            self._agregar_resultado(f"💾 Memoria: {self._obtener_info_memoria()}")
            self._agregar_resultado(f"🔥 CPU: {self._obtener_info_cpu()}")
            self._agregar_resultado(f"🌐 Red: {self._obtener_info_red()}")
            self._agregar_resultado(f"🔒 Seguridad: {self._verificar_estado_seguridad()}")
            
            if hasattr(self.controlador, 'monitor_red'):
                estadisticas = self.controlador.monitor_red.obtener_estadisticas()
                conexiones = estadisticas.get('conexiones_activas', 0)
                sospechosas = estadisticas.get('conexiones_sospechosas', 0)
                self._agregar_resultado(f"🌐 Conexiones activas: {conexiones}")
                if sospechosas > 0:
                    self._agregar_resultado(f"⚠️ Conexiones sospechosas: {sospechosas}")
            
            self._agregar_resultado(f"✅ {EmoticonosMitologicos.ESCUDO} Reporte completado")
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            self._agregar_resultado(f"❌ Error generando reporte: {str(e)}")
    
    def _agregar_resultado(self, texto):
        """Agregar resultado al área de texto de forma segura"""
        try:
            # Usar after para actualizar desde el hilo principal
            self.contenedor_padre.after(0, self._actualizar_texto, texto)
        except:
            pass  # Widget ya destruido
    
    def _actualizar_texto(self, texto):
        """Actualizar texto en el widget de resultados"""
        try:
            # Verificar que el widget esté inicializado
            if not self.resultados_text:
                self.logger.warning("resultados_text no inicializado, omitiendo actualización de texto")
                return
                
            self.resultados_text.config(state='normal')
            self.resultados_text.insert(tk.END, f"{texto}\\n")
            self.resultados_text.see(tk.END)
            self.resultados_text.config(state='disabled')
        except Exception as e:
            self.logger.error(f"Error actualizando texto: {e}")
            pass  # Widget ya destruido
    
    def _ejecutar_monitoreo_hilo(self):
        """Ejecutar monitoreo REAL en hilo separado usando herramientas nativas de Kali Linux"""
        try:
            
            # Usar herramientas nativas de Kali Linux
            self._agregar_resultado(f"✅ {EmoticonosMitologicos.ARGOS} Monitoreo REAL iniciado con herramientas nativas de Kali")
            self._monitoreo_real_kali_linux()
                
            # Finalizar monitoreo
            self.contenedor_padre.after(0, self._finalizar_monitoreo)
            
        except Exception as e:
            self.logger.error(f"Error en monitoreo: {e}")
            self._agregar_resultado(f"❌ {EmoticonosMitologicos.FALLIDO} Error en monitoreo: {str(e)}")
            self.contenedor_padre.after(0, self._finalizar_monitoreo)
    
    def _monitoreo_real_kali_linux(self):
        """Monitoreo real usando herramientas nativas de Kali Linux"""
        try:
            while self.monitoreo_activo:
                try:
                    # === MONITOREAR CPU ===
                    try:
                        # Usar /proc/stat para obtener info de CPU
                        with open('/proc/stat', 'r') as f:
                            cpu_line = f.readline()
                            cpu_values = [int(x) for x in cpu_line.split()[1:]]
                            idle_time = cpu_values[3]
                            total_time = sum(cpu_values)
                            cpu_usage = 100 - (idle_time * 100 / total_time)
                            
                        if cpu_usage > 80:
                            self._agregar_resultado(f"⚠️ Alto uso de CPU: {cpu_usage:.1f}%")
                            
                    except Exception as e:
                        self.logger.warning(f"Error monitoreando CPU: {e}")
                    
                    # === MONITOREAR MEMORIA ===
                    try:
                        with open('/proc/meminfo', 'r') as f:
                            meminfo = f.read()
                        
                        total_match = re.search(r'MemTotal:\s+(\d+)', meminfo)
                        free_match = re.search(r'MemFree:\s+(\d+)', meminfo)
                        
                        if total_match and free_match:
                            total_kb = int(total_match.group(1))
                            free_kb = int(free_match.group(1))
                            used_percent = ((total_kb - free_kb) / total_kb) * 100
                            
                            if used_percent > 90:
                                self._agregar_resultado(f"⚠️ Alto uso de memoria: {used_percent:.1f}%")
                                
                    except Exception as e:
                        self.logger.warning(f"Error monitoreando memoria: {e}")
                    
                    # === VERIFICAR PROCESOS SOSPECHOSOS ===
                    self._verificar_procesos_maliciosos()
                    
                    # Pausa antes del siguiente ciclo
                    time.sleep(8)
                    
                except Exception as e:
                    self.logger.warning(f"Error en ciclo de monitoreo: {e}")
                    time.sleep(3)
                    
        except Exception as e:
            self.logger.error(f"Error en monitoreo Kali Linux: {e}")
            self._monitoreo_fallback()
    
    # === MÉTODOS PARA MONITOREO DUAL ===
    
    def _iniciar_monitoreo_sistema(self):
        """Iniciar monitoreo del sistema"""
        self.monitoreo_activo = True
        self.estado_var.set("🟢 SISTEMA ACTIVO")
        self.btn_iniciar_sistema.configure(state='disabled')
        self.btn_detener_sistema.configure(state='normal')
        
        # Iniciar hilo de monitoreo del sistema
        self.hilo_monitoreo = threading.Thread(target=self._ciclo_monitoreo_sistema, daemon=True)
        self.hilo_monitoreo.start()
        
        self.logger.info("🖥️ Monitoreo del sistema iniciado")
    
    def _detener_monitoreo_sistema(self):
        """Detener monitoreo del sistema"""
        self.monitoreo_activo = False
        self.estado_var.set("🔴 SISTEMA DETENIDO")
        self.btn_iniciar_sistema.configure(state='normal')
        self.btn_detener_sistema.configure(state='disabled')
        
        self.logger.info("🛑 Monitoreo del sistema detenido")
    
    def _iniciar_monitoreo_red(self):
        """Iniciar monitoreo de red"""
        if hasattr(self.controlador, 'monitor_red'):
            self.controlador.monitor_red.iniciar_monitoreo()
            self.btn_iniciar_red.configure(state='disabled')
            self.btn_detener_red.configure(state='normal')
            
            # Iniciar actualización de datos de red
            self._actualizar_datos_red()
            
            self.logger.info("🌐 Monitoreo de red iniciado")
        else:
            self.logger.warning("Monitor de red no disponible")
    
    def _detener_monitoreo_red(self):
        """Detener monitoreo de red"""
        if hasattr(self.controlador, 'monitor_red'):
            self.controlador.monitor_red.detener_monitoreo()
            self.btn_iniciar_red.configure(state='normal')
            self.btn_detener_red.configure(state='disabled')
            
            self.logger.info("🛑 Monitoreo de red detenido")
    
    def _ciclo_monitoreo_sistema(self):
        """Ciclo principal de monitoreo del sistema"""
        while self.monitoreo_activo:
            try:
                # Actualizar procesos
                self._actualizar_procesos()
                
                # Actualizar recursos
                self._actualizar_recursos()
                
                # Actualizar archivos
                self._actualizar_archivos()
                
                time.sleep(5)  # Actualizar cada 5 segundos
                
            except Exception as e:
                self.logger.error(f"Error en ciclo de monitoreo del sistema: {e}")
                time.sleep(3)
    
    def _actualizar_datos_red(self):
        """Actualizar datos de red en tiempo real"""
        if hasattr(self.controlador, 'monitor_red') and self.controlador.monitor_red.monitoreando:
            try:
                # Obtener información completa del sistema de red
                info_red = self.controlador.monitor_red.obtener_informacion_sistema_completa()
                
                # Actualizar interfaces
                self._actualizar_interfaces(info_red.get('interfaces', []))
                
                # Actualizar conexiones
                self._actualizar_conexiones_ui(info_red.get('conexiones_activas_detalladas', []))
                
                # Actualizar tráfico
                self._actualizar_trafico_ui(info_red.get('estadisticas_trafico', {}))
                
                # Actualizar seguridad de red
                self._actualizar_seguridad_red_ui(info_red)
                
                # Programar próxima actualización
                self.frame_principal.after(3000, self._actualizar_datos_red)
                
            except Exception as e:
                self.logger.error(f"Error actualizando datos de red: {e}")
    
    # === MÉTODOS PARA CREAR CONTENIDO DE PESTAÑAS DEL SISTEMA ===
    
    def _crear_contenido_procesos(self):
        """Crear contenido de la pestaña de procesos"""
        # Frame con scroll para procesos
        canvas_procesos = tk.Canvas(self.frame_procesos, bg=self.colores.negro_carbono)
        scrollbar_procesos = ttk.Scrollbar(self.frame_procesos, orient="vertical", command=canvas_procesos.yview)
        scrollable_frame_procesos = tk.Frame(canvas_procesos, bg=self.colores.negro_carbono)
        
        scrollable_frame_procesos.bind(
            "<Configure>",
            lambda e: canvas_procesos.configure(scrollregion=canvas_procesos.bbox("all"))
        )
        
        canvas_procesos.create_window((0, 0), window=scrollable_frame_procesos, anchor="nw")
        canvas_procesos.configure(yscrollcommand=scrollbar_procesos.set)
        
        canvas_procesos.pack(side="left", fill="both", expand=True)
        scrollbar_procesos.pack(side="right", fill="y")
        
        # Header de procesos
        header_procesos = tk.Frame(scrollable_frame_procesos, bg=self.colores.fondo_terciario)
        header_procesos.pack(fill='x', pady=5, padx=5)
        
        tk.Label(header_procesos, text="PID", font=('Consolas', 9, 'bold'), 
                fg=self.colores.cyan_brillante, bg=self.colores.fondo_terciario, width=8).pack(side='left')
        tk.Label(header_procesos, text="PROCESO", font=('Consolas', 9, 'bold'), 
                fg=self.colores.cyan_brillante, bg=self.colores.fondo_terciario, width=20).pack(side='left')
        tk.Label(header_procesos, text="CPU%", font=('Consolas', 9, 'bold'), 
                fg=self.colores.cyan_brillante, bg=self.colores.fondo_terciario, width=8).pack(side='left')
        tk.Label(header_procesos, text="MEM%", font=('Consolas', 9, 'bold'), 
                fg=self.colores.cyan_brillante, bg=self.colores.fondo_terciario, width=8).pack(side='left')
        
        self.contenido_procesos = scrollable_frame_procesos
    
    def _crear_contenido_recursos(self):
        """Crear contenido de la pestaña de recursos"""
        # Información de CPU
        cpu_frame = tk.LabelFrame(self.frame_recursos, text="💻 CPU", 
                                 font=('Consolas', 10, 'bold'), fg=self.colores.verde_terminal,
                                 bg=self.colores.negro_carbono)
        cpu_frame.pack(fill='x', padx=10, pady=5)
        
        self.cpu_info_label = tk.Label(cpu_frame, text="Cargando...", 
                                      font=('Consolas', 9), fg=self.colores.blanco_hueso,
                                      bg=self.colores.negro_carbono, justify='left')
        self.cpu_info_label.pack(anchor='w', padx=10, pady=5)
        
        # Información de Memoria
        mem_frame = tk.LabelFrame(self.frame_recursos, text="🧠 MEMORIA", 
                                 font=('Consolas', 10, 'bold'), fg=self.colores.amarillo_medio,
                                 bg=self.colores.negro_carbono)
        mem_frame.pack(fill='x', padx=10, pady=5)
        
        self.mem_info_label = tk.Label(mem_frame, text="Cargando...", 
                                      font=('Consolas', 9), fg=self.colores.blanco_hueso,
                                      bg=self.colores.negro_carbono, justify='left')
        self.mem_info_label.pack(anchor='w', padx=10, pady=5)
        
        # Información de Disco
        disk_frame = tk.LabelFrame(self.frame_recursos, text="💾 DISCO", 
                                  font=('Consolas', 10, 'bold'), fg=self.colores.cyan_brillante,
                                  bg=self.colores.negro_carbono)
        disk_frame.pack(fill='x', padx=10, pady=5)
        
        self.disk_info_label = tk.Label(disk_frame, text="Cargando...", 
                                       font=('Consolas', 9), fg=self.colores.blanco_hueso,
                                       bg=self.colores.negro_carbono, justify='left')
        self.disk_info_label.pack(anchor='w', padx=10, pady=5)
    
    def _crear_contenido_archivos(self):
        """Crear contenido de la pestaña de archivos"""
        # Frame con scroll para archivos monitoreados
        canvas_archivos = tk.Canvas(self.frame_archivos, bg=self.colores.negro_carbono)
        scrollbar_archivos = ttk.Scrollbar(self.frame_archivos, orient="vertical", command=canvas_archivos.yview)
        scrollable_frame_archivos = tk.Frame(canvas_archivos, bg=self.colores.negro_carbono)
        
        scrollable_frame_archivos.bind(
            "<Configure>",
            lambda e: canvas_archivos.configure(scrollregion=canvas_archivos.bbox("all"))
        )
        
        canvas_archivos.create_window((0, 0), window=scrollable_frame_archivos, anchor="nw")
        canvas_archivos.configure(yscrollcommand=scrollbar_archivos.set)
        
        canvas_archivos.pack(side="left", fill="both", expand=True)
        scrollbar_archivos.pack(side="right", fill="y")
        
        # Controles de archivos
        control_archivos = tk.Frame(scrollable_frame_archivos, bg=self.colores.fondo_terciario)
        control_archivos.pack(fill='x', padx=5, pady=5)
        
        tk.Label(control_archivos, text="📁 ARCHIVOS Y DIRECTORIOS MONITOREADOS",
                font=('Consolas', 10, 'bold'), fg=self.colores.verde_terminal,
                bg=self.colores.fondo_terciario).pack()
        
        self.contenido_archivos = scrollable_frame_archivos
    
    # === MÉTODOS PARA CREAR CONTENIDO DE PESTAÑAS DE RED ===
    
    def _crear_contenido_conexiones(self):
        """Crear contenido de la pestaña de conexiones"""
        # Frame con scroll para conexiones
        canvas_conexiones = tk.Canvas(self.frame_conexiones, bg=self.colores.negro_carbono)
        scrollbar_conexiones = ttk.Scrollbar(self.frame_conexiones, orient="vertical", command=canvas_conexiones.yview)
        scrollable_frame_conexiones = tk.Frame(canvas_conexiones, bg=self.colores.negro_carbono)
        
        scrollable_frame_conexiones.bind(
            "<Configure>",
            lambda e: canvas_conexiones.configure(scrollregion=canvas_conexiones.bbox("all"))
        )
        
        canvas_conexiones.create_window((0, 0), window=scrollable_frame_conexiones, anchor="nw")
        canvas_conexiones.configure(yscrollcommand=scrollbar_conexiones.set)
        
        canvas_conexiones.pack(side="left", fill="both", expand=True)
        scrollbar_conexiones.pack(side="right", fill="y")
        
        # Header de conexiones
        header_conexiones = tk.Frame(scrollable_frame_conexiones, bg=self.colores.fondo_terciario)
        header_conexiones.pack(fill='x', pady=5, padx=5)
        
        tk.Label(header_conexiones, text="PROTOCOLO", font=('Consolas', 9, 'bold'), 
                fg=self.colores.cyan_brillante, bg=self.colores.fondo_terciario, width=10).pack(side='left')
        tk.Label(header_conexiones, text="LOCAL", font=('Consolas', 9, 'bold'), 
                fg=self.colores.cyan_brillante, bg=self.colores.fondo_terciario, width=20).pack(side='left')
        tk.Label(header_conexiones, text="REMOTO", font=('Consolas', 9, 'bold'), 
                fg=self.colores.cyan_brillante, bg=self.colores.fondo_terciario, width=20).pack(side='left')
        tk.Label(header_conexiones, text="ESTADO", font=('Consolas', 9, 'bold'), 
                fg=self.colores.cyan_brillante, bg=self.colores.fondo_terciario, width=12).pack(side='left')
        
        self.contenido_conexiones = scrollable_frame_conexiones
    
    def _crear_contenido_interfaces(self):
        """Crear contenido de la pestaña de interfaces"""
        # Frame con scroll para interfaces
        canvas_interfaces = tk.Canvas(self.frame_interfaces, bg=self.colores.negro_carbono)
        scrollbar_interfaces = ttk.Scrollbar(self.frame_interfaces, orient="vertical", command=canvas_interfaces.yview)
        scrollable_frame_interfaces = tk.Frame(canvas_interfaces, bg=self.colores.negro_carbono)
        
        scrollable_frame_interfaces.bind(
            "<Configure>",
            lambda e: canvas_interfaces.configure(scrollregion=canvas_interfaces.bbox("all"))
        )
        
        canvas_interfaces.create_window((0, 0), window=scrollable_frame_interfaces, anchor="nw")
        canvas_interfaces.configure(yscrollcommand=scrollbar_interfaces.set)
        
        canvas_interfaces.pack(side="left", fill="both", expand=True)
        scrollbar_interfaces.pack(side="right", fill="y")
        
        self.contenido_interfaces = scrollable_frame_interfaces
    
    def _crear_contenido_trafico(self):
        """Crear contenido de la pestaña de tráfico"""
        # Frame con scroll para tráfico
        canvas_trafico = tk.Canvas(self.frame_trafico, bg=self.colores.negro_carbono)
        scrollbar_trafico = ttk.Scrollbar(self.frame_trafico, orient="vertical", command=canvas_trafico.yview)
        scrollable_frame_trafico = tk.Frame(canvas_trafico, bg=self.colores.negro_carbono)
        
        scrollable_frame_trafico.bind(
            "<Configure>",
            lambda e: canvas_trafico.configure(scrollregion=canvas_trafico.bbox("all"))
        )
        
        canvas_trafico.create_window((0, 0), window=scrollable_frame_trafico, anchor="nw")
        canvas_trafico.configure(yscrollcommand=scrollbar_trafico.set)
        
        canvas_trafico.pack(side="left", fill="both", expand=True)
        scrollbar_trafico.pack(side="right", fill="y")
        
        self.contenido_trafico = scrollable_frame_trafico
    
    def _crear_contenido_seguridad_red(self):
        """Crear contenido de la pestaña de seguridad de red"""
        # Frame con scroll para seguridad
        canvas_seguridad = tk.Canvas(self.frame_seguridad_red, bg=self.colores.negro_carbono)
        scrollbar_seguridad = ttk.Scrollbar(self.frame_seguridad_red, orient="vertical", command=canvas_seguridad.yview)
        scrollable_frame_seguridad = tk.Frame(canvas_seguridad, bg=self.colores.negro_carbono)
        
        scrollable_frame_seguridad.bind(
            "<Configure>",
            lambda e: canvas_seguridad.configure(scrollregion=canvas_seguridad.bbox("all"))
        )
        
        canvas_seguridad.create_window((0, 0), window=scrollable_frame_seguridad, anchor="nw")
        canvas_seguridad.configure(yscrollcommand=scrollbar_seguridad.set)
        
        canvas_seguridad.pack(side="left", fill="both", expand=True)
        scrollbar_seguridad.pack(side="right", fill="y")
        
        self.contenido_seguridad_red = scrollable_frame_seguridad
    
    # === MÉTODOS DE ACTUALIZACIÓN EN TIEMPO REAL ===
    
    def _actualizar_procesos(self):
        """Actualizar lista de procesos en tiempo real"""
        try:
            # Limpiar contenido anterior
            for widget in self.contenido_procesos.winfo_children():
                if widget != self.contenido_procesos.winfo_children()[0]:  # Mantener header
                    widget.destroy()
            
            # Obtener procesos usando ps
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:11]  # Primeros 10 procesos
                
                for i, line in enumerate(lines):
                    parts = line.split(None, 10)
                    if len(parts) >= 11:
                        proceso_frame = tk.Frame(self.contenido_procesos, bg=self.colores.negro_carbono)
                        proceso_frame.pack(fill='x', pady=1, padx=5)
                        
                        # Color alternado
                        bg_color = self.colores.gris_pizarra if i % 2 == 0 else self.colores.negro_carbono
                        
                        tk.Label(proceso_frame, text=parts[1][:7], font=('Consolas', 8), 
                                fg=self.colores.blanco_hueso, bg=bg_color, width=8).pack(side='left')
                        tk.Label(proceso_frame, text=parts[10][:18], font=('Consolas', 8), 
                                fg=self.colores.verde_terminal, bg=bg_color, width=20).pack(side='left')
                        tk.Label(proceso_frame, text=parts[2][:6], font=('Consolas', 8), 
                                fg=self.colores.amarillo_medio, bg=bg_color, width=8).pack(side='left')
                        tk.Label(proceso_frame, text=parts[3][:6], font=('Consolas', 8), 
                                fg=self.colores.cyan_brillante, bg=bg_color, width=8).pack(side='left')
                        
        except Exception as e:
            self.logger.error(f"Error actualizando procesos: {e}")
    
    def _actualizar_recursos(self):
        """Actualizar información de recursos del sistema"""
        try:
            # CPU Info
            with open('/proc/loadavg', 'r') as f:
                load_avg = f.read().strip().split()[:3]
            cpu_info = f"Load Average: {' '.join(load_avg)}\nCores: {os.cpu_count()}"
            self.cpu_info_label.configure(text=cpu_info)
            
            # Memory Info
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            total_match = re.search(r'MemTotal:\s+(\d+)', meminfo)
            free_match = re.search(r'MemFree:\s+(\d+)', meminfo)
            available_match = re.search(r'MemAvailable:\s+(\d+)', meminfo)
            
            if total_match and free_match:
                total_kb = int(total_match.group(1))
                free_kb = int(free_match.group(1))
                available_kb = int(available_match.group(1)) if available_match else free_kb
                used_kb = total_kb - free_kb
                
                total_gb = total_kb / 1024 / 1024
                used_gb = used_kb / 1024 / 1024
                available_gb = available_kb / 1024 / 1024
                
                mem_info = f"Total: {total_gb:.1f} GB\nUsada: {used_gb:.1f} GB\nDisponible: {available_gb:.1f} GB"
                self.mem_info_label.configure(text=mem_info)
            
            # Disk Info
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        disk_info = f"Tamaño: {parts[1]}\nUsado: {parts[2]}\nDisponible: {parts[3]}\nUso: {parts[4]}"
                        self.disk_info_label.configure(text=disk_info)
                        
        except Exception as e:
            self.logger.error(f"Error actualizando recursos: {e}")
    
    def _actualizar_archivos(self):
        """Actualizar archivos monitoreados"""
        try:
            # Limpiar contenido anterior (excepto controles)
            for widget in self.contenido_archivos.winfo_children():
                if len(self.contenido_archivos.winfo_children()) > 1:
                    widget.destroy()
            
            # Agregar archivos importantes del sistema
            archivos_importantes = [
                '/etc/passwd', '/etc/shadow', '/etc/hosts', '/etc/fstab',
                '/var/log/auth.log', '/var/log/syslog', '/etc/sudoers'
            ]
            
            for archivo in archivos_importantes:
                if os.path.exists(archivo):
                    archivo_frame = tk.Frame(self.contenido_archivos, bg=self.colores.negro_carbono)
                    archivo_frame.pack(fill='x', pady=2, padx=5)
                    
                    stat_info = os.stat(archivo)
                    size_mb = stat_info.st_size / 1024 / 1024
                    mod_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(stat_info.st_mtime))
                    
                    tk.Label(archivo_frame, text="📄", font=('Consolas', 10), 
                            fg=self.colores.verde_terminal, bg=self.colores.negro_carbono).pack(side='left')
                    tk.Label(archivo_frame, text=archivo, font=('Consolas', 8), 
                            fg=self.colores.blanco_hueso, bg=self.colores.negro_carbono).pack(side='left', padx=(5,0))
                    tk.Label(archivo_frame, text=f"{size_mb:.2f}MB | {mod_time}", font=('Consolas', 8), 
                            fg=self.colores.gris_platino, bg=self.colores.negro_carbono).pack(side='right')
                            
        except Exception as e:
            self.logger.error(f"Error actualizando archivos: {e}")
    
    def _actualizar_interfaces(self, interfaces):
        """Actualizar información de interfaces de red"""
        try:
            # Limpiar contenido anterior
            for widget in self.contenido_interfaces.winfo_children():
                widget.destroy()
            
            for interface in interfaces:
                iface_frame = tk.LabelFrame(self.contenido_interfaces, 
                                          text=f"🔌 {interface.get('nombre', 'N/A')}",
                                          font=('Consolas', 10, 'bold'), 
                                          fg=self.colores.cyan_brillante,
                                          bg=self.colores.negro_carbono)
                iface_frame.pack(fill='x', padx=5, pady=5)
                
                estado = interface.get('estado', 'DOWN')
                estado_color = self.colores.verde_terminal if estado == 'UP' else self.colores.rojo_critico
                
                info_text = f"Estado: {estado}\n"
                if interface.get('ips'):
                    info_text += f"IPs: {', '.join(interface['ips'])}\n"
                if interface.get('mac'):
                    info_text += f"MAC: {interface['mac']}\n"
                
                tk.Label(iface_frame, text=info_text, font=('Consolas', 9), 
                        fg=estado_color, bg=self.colores.negro_carbono, justify='left').pack(anchor='w', padx=10, pady=5)
                        
        except Exception as e:
            self.logger.error(f"Error actualizando interfaces: {e}")
    
    def _actualizar_conexiones_ui(self, conexiones):
        """Actualizar conexiones en la interfaz"""
        try:
            # Limpiar contenido anterior (excepto header)
            for widget in self.contenido_conexiones.winfo_children():
                if widget != self.contenido_conexiones.winfo_children()[0]:  # Mantener header
                    widget.destroy()
            
            for i, conn in enumerate(conexiones[:20]):  # Mostrar máximo 20
                conn_frame = tk.Frame(self.contenido_conexiones, bg=self.colores.negro_carbono)
                conn_frame.pack(fill='x', pady=1, padx=5)
                
                bg_color = self.colores.gris_pizarra if i % 2 == 0 else self.colores.negro_carbono
                
                tk.Label(conn_frame, text=conn.get('protocolo', 'N/A')[:9], font=('Consolas', 8), 
                        fg=self.colores.cyan_brillante, bg=bg_color, width=10).pack(side='left')
                tk.Label(conn_frame, text=conn.get('local_addr', 'N/A')[:19], font=('Consolas', 8), 
                        fg=self.colores.verde_terminal, bg=bg_color, width=20).pack(side='left')
                tk.Label(conn_frame, text=conn.get('peer_addr', 'N/A')[:19], font=('Consolas', 8), 
                        fg=self.colores.amarillo_medio, bg=bg_color, width=20).pack(side='left')
                tk.Label(conn_frame, text=conn.get('estado', 'N/A')[:11], font=('Consolas', 8), 
                        fg=self.colores.blanco_hueso, bg=bg_color, width=12).pack(side='left')
                        
        except Exception as e:
            self.logger.error(f"Error actualizando conexiones UI: {e}")
    
    def _actualizar_trafico_ui(self, estadisticas_trafico):
        """Actualizar estadísticas de tráfico en la interfaz"""
        try:
            # Limpiar contenido anterior
            for widget in self.contenido_trafico.winfo_children():
                widget.destroy()
            
            for interface, stats in estadisticas_trafico.items():
                if interface != 'lo':  # Saltar loopback
                    trafico_frame = tk.LabelFrame(self.contenido_trafico, 
                                                text=f"📊 {interface}",
                                                font=('Consolas', 10, 'bold'), 
                                                fg=self.colores.verde_terminal,
                                                bg=self.colores.negro_carbono)
                    trafico_frame.pack(fill='x', padx=5, pady=5)
                    
                    rx_bytes = stats.get('bytes_rx', 0)
                    tx_bytes = stats.get('bytes_tx', 0)
                    rx_packets = stats.get('packets_rx', 0)
                    tx_packets = stats.get('packets_tx', 0)
                    
                    info_text = f"📥 RX: {self._formatear_bytes(rx_bytes)} ({rx_packets:,} paquetes)\n"
                    info_text += f"📤 TX: {self._formatear_bytes(tx_bytes)} ({tx_packets:,} paquetes)"
                    
                    tk.Label(trafico_frame, text=info_text, font=('Consolas', 9), 
                            fg=self.colores.blanco_hueso, bg=self.colores.negro_carbono, justify='left').pack(anchor='w', padx=10, pady=5)
                            
        except Exception as e:
            self.logger.error(f"Error actualizando tráfico UI: {e}")
    
    def _actualizar_seguridad_red_ui(self, info_red):
        """Actualizar información de seguridad de red"""
        try:
            # Limpiar contenido anterior
            for widget in self.contenido_seguridad_red.winfo_children():
                widget.destroy()
            
            # Información de firewall
            firewall_info = info_red.get('firewall_status', {})
            if firewall_info:
                fw_frame = tk.LabelFrame(self.contenido_seguridad_red, 
                                       text="🛡️ FIREWALL",
                                       font=('Consolas', 10, 'bold'), 
                                       fg=self.colores.rojo_critico,
                                       bg=self.colores.negro_carbono)
                fw_frame.pack(fill='x', padx=5, pady=5)
                
                fw_text = ""
                if 'iptables' in firewall_info:
                    fw_text += f"iptables: {'Activo' if firewall_info['iptables']['activo'] else 'Inactivo'}\n"
                    fw_text += f"Reglas: {firewall_info['iptables'].get('reglas', 0)}\n"
                
                if 'ufw' in firewall_info:
                    fw_text += f"UFW: {firewall_info['ufw']['estado']}\n"
                
                tk.Label(fw_frame, text=fw_text, font=('Consolas', 9), 
                        fg=self.colores.blanco_hueso, bg=self.colores.negro_carbono, justify='left').pack(anchor='w', padx=10, pady=5)
            
            # Puertos en escucha
            puertos_escucha = info_red.get('puertos_escucha', [])
            if puertos_escucha:
                puertos_frame = tk.LabelFrame(self.contenido_seguridad_red, 
                                            text="🔓 PUERTOS EN ESCUCHA",
                                            font=('Consolas', 10, 'bold'), 
                                            fg=self.colores.amarillo_medio,
                                            bg=self.colores.negro_carbono)
                puertos_frame.pack(fill='x', padx=5, pady=5)
                
                for puerto in puertos_escucha[:10]:  # Mostrar máximo 10
                    puerto_text = f"Puerto {puerto.get('puerto', 'N/A')} ({puerto.get('protocolo', 'N/A')}) - {puerto.get('servicio', 'Desconocido')}"
                    tk.Label(puertos_frame, text=puerto_text, font=('Consolas', 8), 
                            fg=self.colores.blanco_hueso, bg=self.colores.negro_carbono).pack(anchor='w', padx=10, pady=2)
                            
        except Exception as e:
            self.logger.error(f"Error actualizando seguridad de red UI: {e}")
    
    def _formatear_bytes(self, bytes_count):
        """Formatear bytes en unidades legibles"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} PB"
    
    def _monitoreo_fallback(self):
        """Monitoreo fallback básico usando solo herramientas nativas de Kali Linux"""
        import subprocess
        
        while self.monitoreo_activo:
            try:
                # Monitorear usando comandos básicos de Kali Linux
                
                # Obtener información de load average
                try:
                    with open('/proc/loadavg', 'r') as f:
                        load_avg = f.read().split()[0]
                        self._agregar_resultado(f"📊 {EmoticonosMitologicos.CRISTAL} Load Average: {load_avg}")
                except Exception:
                    pass
                
                # Obtener procesos básicos usando ps
                try:
                    result = subprocess.run(['ps', 'aux', '--sort=-pcpu'], capture_output=True, text=True, timeout=10)
                    lines = result.stdout.split('\\n')[1:4]  # Primeros 3 procesos
                    for line in lines:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 11:
                                user = parts[0]
                                pid = parts[1]
                                cpu = parts[2]
                                command = ' '.join(parts[10:])[:30]
                                self._agregar_resultado(f"🔍 {EmoticonosMitologicos.ARGOS} {user} PID:{pid} CPU:{cpu}% {command}")
                except Exception:
                    pass
                
                # Verificar archivos de sistema importantes
                self._verificar_integridad_sistema()
                
                time.sleep(15)  # Pausa más larga para monitoreo básico
                
            except Exception as e:
                self.logger.warning(f"Error en monitoreo fallback: {e}")
                time.sleep(5)
    
    def _verificar_procesos_maliciosos(self):
        """Verificar procesos potencialmente maliciosos usando herramientas nativas"""
        try:
            import subprocess
            
            # Lista de nombres de procesos sospechosos
            procesos_sospechosos = [
                'bitcoin', 'miner', 'cryptonight', 'xmrig', 'malware',
                'keylogger', 'backdoor', 'rootkit', 'trojan', 'virus',
                'nc.openbsd', 'socat', 'reverse_shell', 'bind_shell'
            ]
            
            # Usar ps para obtener lista de procesos
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
            
            for line in result.stdout.split('\\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 11:
                        pid = parts[1]
                        command_full = ' '.join(parts[10:])
                        command_name = parts[10].split('/')[-1].lower()
                        
                        # Verificar nombres sospechosos
                        for sospechoso in procesos_sospechosos:
                            if sospechoso in command_name or sospechoso in command_full.lower():
                                self._agregar_resultado(f"🚨 {EmoticonosMitologicos.HYDRA} PROCESO SOSPECHOSO: {command_name} (PID: {pid})")
                                self._agregar_resultado(f"📋 {EmoticonosMitologicos.PERGAMINO} Comando: {command_full[:60]}...")
                                
                                # Registrar en SIEM si está disponible
                                if hasattr(self.controlador, 'siem') and self.controlador.siem:
                                    self.controlador.siem.registrar_evento({
                                        'tipo': 'proceso_sospechoso',
                                        'comando': command_full,
                                        'pid': pid,
                                        'severidad': 'alta'
                                    })
                                
        except Exception as e:
            self.logger.warning(f"Error verificando procesos: {e}")
    
    def _verificar_integridad_sistema(self):
        """Verificar integridad básica del sistema Kali Linux"""
        
        # Verificar archivos críticos del sistema Kali Linux
        archivos_criticos = [
            '/bin/bash',
            '/usr/bin/ls',
            '/etc/passwd',
            '/usr/bin/nmap',
            '/usr/bin/metasploit',
            '/usr/bin/aircrack-ng'
        ]
        
        archivos_faltantes = []
        for archivo in archivos_criticos:
            if not os.path.exists(archivo):
                archivos_faltantes.append(archivo)
        
        if archivos_faltantes:
            self._agregar_resultado(f"⚠️ {EmoticonosMitologicos.ADVERTENCIA} Archivos críticos faltantes: {len(archivos_faltantes)}")
            for archivo in archivos_faltantes[:3]:  # Mostrar solo los primeros 3
                self._agregar_resultado(f"❌ Faltante: {archivo}")
        else:
            self._agregar_resultado(f"✅ {EmoticonosMitologicos.ESCUDO} Integridad del sistema OK")
    
    def _finalizar_monitoreo(self):
        """Finalizar el monitoreo de forma segura"""
        try:
            self.monitoreo_activo = False
            self.estado_var.set("🔴 DETENIDO")
            self._agregar_resultado(f"\\n🏁 {EmoticonosMitologicos.ESCUDO} Monitoreo finalizado")
        except:
            pass
    
    def _obtener_info_sistema(self):
        """Obtener información básica del sistema"""
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME'):
                        return line.split('=')[1].strip().strip('"')
            return "Linux"
        except:
            return "Desconocido"
    
    def _obtener_info_memoria(self):
        """Obtener información de memoria"""
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                if line.startswith('MemTotal:'):
                    total_kb = int(line.split()[1])
                    total_gb = total_kb / 1024 / 1024
                    return f"{total_gb:.1f} GB"
            return "Desconocido"
        except:
            return "Error"
    
    def _obtener_info_cpu(self):
        """Obtener información de CPU"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                lines = f.readlines()
            
            model_name = "Desconocido"
            cpu_count = 0
            
            for line in lines:
                if line.startswith('model name'):
                    model_name = line.split(':')[1].strip()
                elif line.startswith('processor'):
                    cpu_count += 1
            
            return f"{cpu_count} cores - {model_name[:30]}..."
        except:
            return "Error"
    
    def _obtener_info_red(self):
        """Obtener información básica de red"""
        try:
            result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True, timeout=5)
            interfaces = []
            
            for line in result.stdout.split('\\n'):
                if 'inet ' in line and '127.0.0.1' not in line:
                    ip_match = line.split('inet ')[1].split('/')[0]
                    interfaces.append(ip_match)
            
            return f"{len(interfaces)} interfaces activas"
        except:
            return "Error"
    
    def _verificar_estado_seguridad(self):
        """Verificar estado básico de seguridad"""
        try:
            # Verificar si hay procesos de seguridad corriendo
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
            
            procesos_seguridad = ['ufw', 'iptables', 'fail2ban', 'clamav']
            activos = []
            
            for proceso in procesos_seguridad:
                if proceso in result.stdout:
                    activos.append(proceso)
            
            return f"{len(activos)} servicios de seguridad activos"
        except:
            return "Error"
    
    def destruir_vista(self):
        """Limpiar recursos al destruir la vista"""
        try:
            self.monitoreo_activo = False
            if self.hilo_monitoreo and self.hilo_monitoreo.is_alive():
                self.hilo_monitoreo.join(timeout=1)
            self._limpiar_contenedor()
            self.logger.info("Vista Monitor destruida")
        except Exception as e:
            self.logger.error(f"Error destruyendo vista Monitor: {e}")
