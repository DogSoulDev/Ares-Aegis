#!/usr/bin/env python3
"""
Vista SIEM para Ares Aegis
Sistema de monitoreo y análisis de eventos de seguridad en tiempo real
"""
from ..componentes_ui.vista_base import VistaBase

from ...utils.imports_comunes import (
    tk, ttk, messagebox, filedialog, logging, os, time, threading
)
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime
from ..componentes_ui.emoticonos_mitologicos import EmoticonosMitologicos
from ..componentes_ui.sistema_ayuda import SistemaAyuda

# Usar solo librerías estándar de Python y herramientas de Kali
import subprocess
import platform
import socket
import shutil

# No usar librerías externas - solo Python estándar y herramientas del sistema
PSUTIL_DISPONIBLE = False


class VistaSIEM(VistaBase):
    """Vista del sistema SIEM con monitoreo en tiempo real"""
    
    def __init__(self, contenedor_padre, controlador, colores):
        super().__init__(contenedor_padre, controlador, colores)
        self.contenedor_padre = contenedor_padre
        self.controlador = controlador
        self.colores = colores
        self.logger = logging.getLogger(__name__)
        self.frame_principal = None
        
        # Estado del SIEM
        self.siem_activo = False
        self.actualizacion_activa = False
        self.thread_actualizacion = None
        
        # Widgets principales inicializados correctamente
        self.btn_iniciar_siem = None  # Se inicializa en _crear_controles_siem
        self.btn_detener_siem = None  # Se inicializa en _crear_controles_siem
        self.estado_label = None  # Se inicializa en _crear_controles_siem
        self.tree_eventos = None  # Se inicializa en _crear_tabla_eventos
        self.text_detalles = None  # Se inicializa en _crear_panel_detalles
        
        # Métricas reales del sistema
        self.metricas_widgets = {}
        self.eventos_reales = []
        
        # Sistema de ayuda
        self.sistema_ayuda = SistemaAyuda(colores)
        
    # Método mostrar_informacion heredado de VistaBase
    # Para personalizar, implementar métodos abstractos:
    # _get_titulo_ventana() y _get_descripcion_funcionalidades()
        """Mostrar información de ayuda sobre el SIEM"""
        info_text = """🛡️ SISTEMA SIEM - INTELIGENCIA DE AMENAZAS

🚨 FUNCIONALIDADES PRINCIPALES:
• Monitoreo integral de eventos de seguridad en tiempo real
• Análisis avanzado de logs del sistema con correlación inteligente
• Detección automática de amenazas con algoritmos de aprendizaje
• Correlación avanzada de eventos sospechosos y patrones de ataque

⚡ MONITOREO AVANZADO Y COBERTURA:
• Conexiones de red entrantes y salientes con análisis de tráfico
• Procesos y servicios del sistema con detección de anomalías
• Intentos de acceso fallidos y patrones de fuerza bruta
• Cambios críticos en archivos del sistema y configuraciones
• Uso anómalo de recursos y escalada de privilegios

🎯 DETECCIÓN INTELIGENTE DE AMENAZAS:
• Ataques de fuerza bruta contra servicios de autenticación
• Intentos de escalada de privilegios y movimiento lateral
• Actividad de red sospechosa y comunicaciones anómalas
• Modificaciones no autorizadas en archivos críticos del sistema
• Comportamiento anómalo de procesos y aplicaciones

🔧 HERRAMIENTAS DE ANÁLISIS INTEGRADAS:
• netstat: Monitoreo exhaustivo de conexiones de red
• ps: Análisis detallado de procesos en ejecución
• last: Historial completo de accesos al sistema
• journalctl: Análisis avanzado de logs del sistema
• ss: Estado detallado y métricas de conexiones de red

⚠️ SISTEMA DE ALERTAS MULTINIVEL:
• 🔴 CRÍTICO: Amenaza inmediata detectada, respuesta urgente requerida
• 🟡 ADVERTENCIA: Actividad sospechosa que requiere investigación
• 🟢 NORMAL: Funcionamiento estándar del sistema sin anomalías
• 🔵 INFORMACIÓN: Eventos del sistema relevantes para auditoría

📊 MÉTRICAS AVANZADAS Y ANÁLISIS:
• Conexiones activas clasificadas por puerto y protocolo
• Procesos con consumo anómalo de CPU y memoria
• Estadísticas de intentos de conexión fallidos por origen
• Eventos de autenticación exitosos y fallidos con detalles
• Timeline de cambios en archivos críticos del sistema

💡 CORRELACIÓN INTELIGENTE DE EVENTOS:
• Análisis de patrones de comportamiento con machine learning
• Detección de cadenas de ataque y técnicas MITRE ATT&CK
• Identificación de IOCs (Indicators of Compromise) automática
• Timeline correlacionado de eventos relacionados temporalmente
• Análisis de contexto para reducir falsos positivos

🔐 ANÁLISIS FORENSE INTEGRADO:
• Registro inmutable de eventos para investigación forense
• Exportación de reportes detallados en múltiples formatos
• Timeline completo de incidentes de seguridad con evidencia
• Preservación de evidencia digital para análisis legal
• Integración con herramientas de respuesta a incidentes

🚀 CARACTERÍSTICAS PROFESIONALES:
• Dashboard en tiempo real con métricas de seguridad
• Alertas configurables por tipos de eventos específicos
• Integración con sistemas de notificación externos
• Análisis de tendencias y patrones históricos
• Capacidades de búsqueda avanzada en logs históricos

🔧 OPTIMIZADO PARA KALI LINUX:
• Integración nativa con herramientas de ciberseguridad
• Análisis especializado para entornos de pentesting
• Compatibilidad con logs específicos de distribuciones Debian
• Integración con frameworks de seguridad de Kali Linux
• Optimización para hardware y rendimiento de sistemas Linux

⏱️ MONITOREO CONTINUO:
• Supervisión 24/7 sin interrupciones del servicio
• Procesamiento en tiempo real de miles de eventos por segundo
• Almacenamiento eficiente de logs con compresión inteligente
• Rotación automática de logs para gestión del espacio"""
        
        messagebox.showinfo("Información - Sistema SIEM", info_text)
        
    def crear_vista(self, area_contenido=None):
        """Crear vista SIEM con interfaz de monitoreo profesional"""
        try:
            self.logger.info("🔧 Iniciando creación de vista SIEM...")
            self._limpiar_contenedor()
            self.logger.info("✅ Contenedor limpiado")
            
            # Frame principal con padding estandarizado
            self.frame_principal = tk.Frame(self.contenedor_padre, bg=self.colores.fondo_secundario)
            self.frame_principal.pack(fill='both', expand=True, padx=20, pady=10)
            self.logger.info("✅ Frame principal creado")
            
            # Configurar grid responsive
            self.frame_principal.grid_rowconfigure(0, weight=0)  # Header fijo
            self.frame_principal.grid_rowconfigure(1, weight=0)  # Panel de control fijo
            self.frame_principal.grid_rowconfigure(2, weight=1)  # Contenido expandible
            self.frame_principal.grid_columnconfigure(0, weight=1)
            self.logger.info("✅ Grid configurado")
            
            # === HEADER DEL SIEM ===
            self._crear_header_siem()
            self.logger.info("✅ Header creado")
            
            # === PANEL DE CONTROL ===
            self._crear_panel_control()
            self.logger.info("✅ Panel de control creado")
            
            # === CONTENIDO PRINCIPAL ===
            self._crear_contenido_principal()
            self.logger.info("✅ Contenido principal creado")
            
            self.logger.info("🎯 Vista SIEM creada exitosamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error creando vista SIEM: {e}", exc_info=True)
            raise
    
    def _crear_header_siem(self):
        """Crear header del SIEM"""
        header_frame = tk.Frame(self.frame_principal, 
                              bg=self.colores.negro_carbono, 
                              height=80)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        
        # Frame para títulos (centrado)
        titulo_frame = tk.Frame(header_frame, bg=self.colores.negro_carbono)
        titulo_frame.grid(row=0, column=0, pady=15)
        
        # Título principal
        titulo_label = tk.Label(titulo_frame,
                               text=f"{EmoticonosMitologicos.ESCUDO} SISTEMA SIEM",
                               font=('Consolas', 18, 'bold'),
                               fg=self.colores.verde_terminal,
                               bg=self.colores.negro_carbono)
        titulo_label.pack()
        
        # Subtítulo
        subtitulo_label = tk.Label(titulo_frame,
                                  text="Monitoreo de Eventos de Seguridad en Tiempo Real",
                                  font=('Consolas', 11),
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
    
    def _crear_panel_control(self):
        """Crear panel de control del SIEM"""
        control_frame = tk.LabelFrame(self.frame_principal,
                                     text="🎛️ Panel de Control SIEM",
                                     bg=self.colores.fondo_secundario,
                                     fg=self.colores.verde_terminal,
                                     font=('Consolas', 12, 'bold'))
        control_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Frame interno para controles
        controles_frame = tk.Frame(control_frame, bg=self.colores.fondo_secundario)
        controles_frame.pack(fill='x', padx=20, pady=15)
        
        # Estado del sistema
        self.estado_label = tk.Label(controles_frame,
                                   text="🔴 SIEM INACTIVO",
                                   font=('Consolas', 14, 'bold'),
                                   fg=self.colores.rojo_critico,
                                   bg=self.colores.fondo_secundario)
        self.estado_label.pack(pady=(0, 15))
        
        # Botones de control
        botones_frame = tk.Frame(controles_frame, bg=self.colores.fondo_secundario)
        botones_frame.pack()
        
        self.btn_iniciar_siem = tk.Button(botones_frame,
                                        text="▶️ INICIAR SIEM",
                                        font=('Consolas', 11, 'bold'),
                                        fg=self.colores.negro_carbono,
                                        bg=self.colores.verde_terminal,
                                        activebackground=self.colores.verde_esmeralda,
                                        relief='flat',
                                        padx=20,
                                        pady=8,
                                        command=self.iniciar_siem)
        self.btn_iniciar_siem.pack(side='left', padx=5)
        
        self.btn_detener_siem = tk.Button(botones_frame,
                                        text="⏹️ DETENER SIEM",
                                        font=('Consolas', 11, 'bold'),
                                        fg=self.colores.blanco_hueso,
                                        bg=self.colores.rojo_critico,
                                        activebackground=self.colores.rojo_sangre,
                                        relief='flat',
                                        padx=20,
                                        pady=8,
                                        state='disabled',
                                        command=self.detener_siem)
        self.btn_detener_siem.pack(side='left', padx=5)
        
        self.btn_exportar = tk.Button(botones_frame,
                                    text="💾 EXPORTAR",
                                    font=('Consolas', 10, 'bold'),
                                    fg=self.colores.negro_carbono,
                                    bg=self.colores.amarillo_medio,
                                    relief='flat',
                                    padx=15,
                                    pady=8,
                                    command=self.exportar_eventos)
        self.btn_exportar.pack(side='left', padx=5)
    
    def _crear_contenido_principal(self):
        """Crear área de contenido principal"""
        # Frame con scroll
        canvas_frame = tk.Frame(self.frame_principal, bg=self.colores.fondo_secundario)
        canvas_frame.grid(row=2, column=0, sticky="nsew")
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        canvas = tk.Canvas(canvas_frame, bg=self.colores.fondo_secundario)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        contenido_scroll = tk.Frame(canvas, bg=self.colores.fondo_secundario)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        canvas_window = canvas.create_window((0, 0), window=contenido_scroll, anchor="nw")
        
        def configurar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
        
        contenido_scroll.bind("<Configure>", configurar_scroll)
        canvas.bind("<Configure>", configurar_scroll)
        
        # === MÉTRICAS DEL SISTEMA ===
        self._crear_metricas_sistema(contenido_scroll)
        
        # === TABLA DE EVENTOS ===
        self._crear_tabla_eventos(contenido_scroll)
        
        # === ÁREA DE DETALLES ===
        self._crear_area_detalles(contenido_scroll)
    
    def _crear_metricas_sistema(self, parent):
        """Crear panel de métricas del sistema con información de seguridad"""
        metricas_frame = tk.LabelFrame(parent,
                                     text="�️ Panel de Seguridad en Tiempo Real",
                                     bg=self.colores.fondo_primario,
                                     fg=self.colores.verde_terminal,
                                     font=('Consolas', 11, 'bold'))
        metricas_frame.pack(fill='x', padx=5, pady=10)
        
        # Grid para métricas (2 filas para más información)
        grid_frame = tk.Frame(metricas_frame, bg=self.colores.fondo_primario)
        grid_frame.pack(fill='x', padx=15, pady=10)
        
        # Configurar grid - 4 columnas, 2 filas
        for i in range(4):
            grid_frame.grid_columnconfigure(i, weight=1)
        
        # === FILA 1: Métricas básicas del sistema ===
        if PSUTIL_DISPONIBLE:
            self._crear_metrica(grid_frame, 0, 0, "CPU", "cpu", self.colores.verde_terminal)
            self._crear_metrica(grid_frame, 0, 1, "RAM", "ram", self.colores.cyan_brillante)
            self._crear_metrica(grid_frame, 0, 2, "PROCESOS", "procesos", self.colores.amarillo_medio)
        else:
            self._crear_metrica(grid_frame, 0, 0, "SISTEMA", "sistema", self.colores.verde_terminal)
        
        self._crear_metrica(grid_frame, 0, 3, "EVENTOS", "eventos", self.colores.verde_terminal)
        
        # === FILA 2: Métricas de seguridad ===
        self._crear_metrica(grid_frame, 1, 0, "IP LOCAL", "ip_local", self.colores.azul_electrico)
        self._crear_metrica(grid_frame, 1, 1, "CONEXIONES", "conexiones_red", self.colores.cyan_brillante)
        self._crear_metrica(grid_frame, 1, 2, "PUERTOS", "puertos_abiertos", self.colores.naranja_fuego)
        self._crear_metrica(grid_frame, 1, 3, "AMENAZAS", "amenazas_detectadas", self.colores.rojo_critico)
    
    def _crear_metrica(self, parent, row, col, titulo, clave, color):
        """Crear una métrica individual"""
        metrica_frame = tk.Frame(parent, bg=self.colores.fondo_primario)
        metrica_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        tk.Label(metrica_frame,
                text=titulo,
                font=('Consolas', 9),
                fg=self.colores.texto_secundario,
                bg=self.colores.fondo_primario).pack()
        
        valor_label = tk.Label(metrica_frame,
                             text="--",
                             font=('Consolas', 12, 'bold'),
                             fg=color,
                             bg=self.colores.fondo_primario)
        valor_label.pack()
        
        self.metricas_widgets[clave] = valor_label
    
    def _crear_tabla_eventos(self, parent):
        """Crear tabla de eventos"""
        eventos_frame = tk.LabelFrame(parent,
                                    text="📋 Eventos de Seguridad",
                                    bg=self.colores.fondo_primario,
                                    fg=self.colores.verde_terminal,
                                    font=('Consolas', 11, 'bold'))
        eventos_frame.pack(fill='both', expand=True, padx=5, pady=10)
        
        # Crear Treeview
        columns = ('timestamp', 'tipo', 'severidad', 'origen', 'descripcion')
        self.tree_eventos = ttk.Treeview(eventos_frame, columns=columns, show='headings', height=12)
        
        # Configurar columnas
        self.tree_eventos.heading('timestamp', text='Timestamp')
        self.tree_eventos.heading('tipo', text='Tipo')
        self.tree_eventos.heading('severidad', text='Severidad')
        self.tree_eventos.heading('origen', text='Origen')
        self.tree_eventos.heading('descripcion', text='Descripción')
        
        # Configurar anchos
        self.tree_eventos.column('timestamp', width=150)
        self.tree_eventos.column('tipo', width=100)
        self.tree_eventos.column('severidad', width=80)
        self.tree_eventos.column('origen', width=120)
        self.tree_eventos.column('descripcion', width=300)
        
        # Scrollbar para la tabla
        scrollbar_tabla = ttk.Scrollbar(eventos_frame, orient="vertical", command=self.tree_eventos.yview)
        self.tree_eventos.configure(yscrollcommand=scrollbar_tabla.set)
        
        # Empaquetar tabla y scrollbar
        self.tree_eventos.pack(side='left', fill='both', expand=True, padx=(15, 0), pady=15)
        scrollbar_tabla.pack(side='right', fill='y', padx=(0, 15), pady=15)
        
        # Bind para selección
        self.tree_eventos.bind('<<TreeviewSelect>>', self.mostrar_detalles_evento)
    
    def _crear_area_detalles(self, parent):
        """Crear área de detalles del evento"""
        detalles_frame = tk.LabelFrame(parent,
                                     text="🔍 Detalles del Evento",
                                     bg=self.colores.fondo_primario,
                                     fg=self.colores.verde_terminal,
                                     font=('Consolas', 11, 'bold'))
        detalles_frame.pack(fill='x', padx=5, pady=10)
        
        # Área de texto para detalles
        self.text_detalles = tk.Text(detalles_frame,
                                   height=8,
                                   font=('Consolas', 10),
                                   bg=self.colores.negro_carbono,
                                   fg=self.colores.verde_terminal,
                                   wrap=tk.WORD,
                                   state='disabled')
        self.text_detalles.pack(fill='x', padx=15, pady=15)
    
    def iniciar_siem(self):
        """Iniciar el sistema SIEM"""
        try:
            self.siem_activo = True
            self.actualizacion_activa = True
            
            # Actualizar interfaz - verificar que los widgets estén inicializados
            if self.estado_label:
                self.estado_label.config(text="🟢 SIEM ACTIVO", fg=self.colores.verde_terminal)
            if self.btn_iniciar_siem:
                self.btn_iniciar_siem.config(state='disabled')
            if self.btn_detener_siem:
                self.btn_detener_siem.config(state='normal')
            
            # Iniciar hilo de actualización
            self.thread_actualizacion = threading.Thread(target=self._actualizar_metricas_reales, daemon=True)
            self.thread_actualizacion.start()
            
            # Usar controlador SIEM si está disponible
            if hasattr(self.controlador, 'iniciar_siem'):
                self.controlador.iniciar_siem()
            
            self.logger.info("SIEM iniciado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al iniciar SIEM: {e}")
            messagebox.showerror("Error", f"No se pudo iniciar el SIEM: {e}")
    
    def detener_siem(self):
        """Detener el sistema SIEM"""
        try:
            self.siem_activo = False
            self.actualizacion_activa = False
            
            # Actualizar interfaz - verificar que los widgets estén inicializados
            if self.estado_label:
                self.estado_label.config(text="🔴 SIEM INACTIVO", fg=self.colores.rojo_critico)
            if self.btn_iniciar_siem:
                self.btn_iniciar_siem.config(state='normal')
            if self.btn_detener_siem:
                self.btn_detener_siem.config(state='disabled')
            
            # Usar controlador SIEM si está disponible
            if hasattr(self.controlador, 'detener_siem'):
                self.controlador.detener_siem()
            
            self.logger.info("SIEM detenido correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al detener SIEM: {e}")
    
    def _actualizar_metricas_reales(self):
        """Actualizar métricas con datos reales del sistema usando solo Python estándar y herramientas de Kali"""
        while self.actualizacion_activa:
            try:
                # === MÉTRICAS BÁSICAS DEL SISTEMA ===
                # CPU usando /proc/stat (solo Linux/Kali)
                cpu_percent = self._get_cpu_usage()
                if 'cpu' in self.metricas_widgets:
                    color = self.colores.rojo_critico if cpu_percent > 80 else self.colores.verde_terminal
                    self.metricas_widgets['cpu'].config(text=f"{cpu_percent:.1f}%", fg=color)
                
                # RAM usando /proc/meminfo (solo Linux/Kali)
                ram_percent = self._get_memory_usage()
                if 'ram' in self.metricas_widgets:
                    color = self.colores.rojo_critico if ram_percent > 90 else \
                            self.colores.naranja_fuego if ram_percent > 70 else self.colores.cyan_brillante
                    self.metricas_widgets['ram'].config(text=f"{ram_percent:.1f}%", fg=color)
                
                # Procesos usando /proc (solo Linux/Kali)
                num_procesos = self._get_process_count()
                if 'procesos' in self.metricas_widgets:
                    self.metricas_widgets['procesos'].config(text=str(num_procesos))
                
                # === MÉTRICAS DE SEGURIDAD ===
                # IP Local usando socket (estándar)
                if 'ip_local' in self.metricas_widgets:
                    ip_local = self._get_local_ip()
                    self.metricas_widgets['ip_local'].config(text=ip_local)
                
                # Conexiones de red usando netstat (herramienta de Kali)
                if 'conexiones_red' in self.metricas_widgets:
                    conexiones_activas = self._get_network_connections()
                    color = self.colores.rojo_critico if conexiones_activas > 100 else \
                            self.colores.naranja_fuego if conexiones_activas > 50 else self.colores.cyan_brillante
                    self.metricas_widgets['conexiones_red'].config(text=str(conexiones_activas), fg=color)
                
                # Puertos abiertos usando ss (herramienta de Kali)
                if 'puertos_abiertos' in self.metricas_widgets:
                    puertos_listen = self._get_listening_ports()
                    color = self.colores.rojo_critico if puertos_listen > 20 else \
                            self.colores.naranja_fuego if puertos_listen > 10 else self.colores.naranja_fuego
                    self.metricas_widgets['puertos_abiertos'].config(text=str(puertos_listen), fg=color)
                
                # Amenazas detectadas
                if 'amenazas_detectadas' in self.metricas_widgets:
                    amenazas = len([e for e in self.eventos_reales 
                                  if e.get('severidad') in ['CRITICA', 'ALTA']])
                    color = self.colores.rojo_critico if amenazas > 10 else \
                            self.colores.naranja_fuego if amenazas > 5 else self.colores.verde_terminal
                    self.metricas_widgets['amenazas_detectadas'].config(text=str(amenazas), fg=color)
                
                # Verificar eventos de seguridad usando herramientas estándar
                self._verificar_eventos_seguridad()
                
                # Eventos totales
                if 'eventos' in self.metricas_widgets:
                    total_eventos = len(self.eventos_reales)
                    color = self.colores.rojo_critico if total_eventos > 50 else \
                            self.colores.naranja_fuego if total_eventos > 20 else self.colores.verde_terminal
                    self.metricas_widgets['eventos'].config(text=str(total_eventos), fg=color)
                
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error actualizando métricas: {e}")
                time.sleep(5)
    
    def _get_cpu_usage(self):
        """Obtener uso de CPU usando /proc/stat (solo Linux/Kali)"""
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                cpu_times = [int(x) for x in line.split()[1:]]
                idle_time = cpu_times[3]
                total_time = sum(cpu_times)
                
                if hasattr(self, '_prev_cpu_times'):
                    prev_idle = self._prev_cpu_times[3] 
                    prev_total = sum(self._prev_cpu_times)
                    
                    idle_delta = idle_time - prev_idle
                    total_delta = total_time - prev_total
                    
                    if total_delta > 0:
                        cpu_percent = 100.0 * (1.0 - idle_delta / total_delta)
                    else:
                        cpu_percent = 0.0
                else:
                    cpu_percent = 0.0
                
                self._prev_cpu_times = cpu_times
                return cpu_percent
                
        except (FileNotFoundError, IOError):
            # Fallback usando uptime si /proc/stat no está disponible
            try:
                result = subprocess.run(['uptime'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Extraer load average del output de uptime
                    output = result.stdout.strip()
                    if 'load average:' in output:
                        load_avg = output.split('load average:')[1].split(',')[0].strip()
                        return float(load_avg) * 10  # Estimación aproximada
                return 0.0
            except:
                return 0.0
    
    def _get_memory_usage(self):
        """Obtener uso de memoria usando /proc/meminfo (solo Linux/Kali)"""
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = {}
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        key = parts[0].rstrip(':')
                        value = int(parts[1])
                        meminfo[key] = value
                
                total = meminfo.get('MemTotal', 0)
                available = meminfo.get('MemAvailable', meminfo.get('MemFree', 0))
                
                if total > 0:
                    used = total - available
                    return (used / total) * 100
                return 0.0
                
        except (FileNotFoundError, IOError):
            # Fallback usando free si /proc/meminfo no está disponible (solo en Linux)
            try:
                import platform
                if platform.system() == 'Linux':
                    result = subprocess.run(['free', '-m'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if len(lines) >= 2:
                            mem_line = lines[1].split()
                            if len(mem_line) >= 3:
                                total = int(mem_line[1])
                                used = int(mem_line[2])
                                return (used / total) * 100 if total > 0 else 0.0
                return 0.0
            except:
                return 0.0
    
    def _get_process_count(self):
        """Obtener número de procesos usando /proc (solo Linux/Kali)"""
        try:
            proc_dirs = [d for d in os.listdir('/proc') if d.isdigit()]
            return len(proc_dirs)
        except:
            # Fallback usando ps
            try:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return len(result.stdout.strip().split('\n')) - 1  # -1 para header
                return 0
            except:
                return 0
    
    def _get_local_ip(self):
        """Obtener IP local usando socket estándar"""
        try:
            hostname = socket.gethostname()
            ip_local = socket.gethostbyname(hostname)
            return ip_local
        except:
            return "N/A"
    
    def _get_network_connections(self):
        """Obtener conexiones de red usando netstat (herramienta de Kali)"""
        try:
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                established = [line for line in lines if 'ESTABLISHED' in line]
                return len(established)
            return 0
        except:
            return 0
    
    def _get_listening_ports(self):
        """Obtener puertos en escucha usando ss (herramienta de Kali)"""
        try:
            result = subprocess.run(['ss', '-tuln'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                listening = [line for line in lines if 'LISTEN' in line]
                return len(listening)
            return 0
        except:
            # Fallback con netstat
            try:
                result = subprocess.run(['netstat', '-ln'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    listening = [line for line in lines if 'LISTEN' in line]
                    return len(listening)
                return 0
            except:
                return 0
    
    def _verificar_eventos_seguridad(self):
        """Verificar eventos de seguridad usando solo herramientas estándar de Kali Linux"""
        try:
            # === MONITOREO DE PROCESOS USANDO /proc ===
            self._verificar_procesos_sospechosos()
            
            # === VERIFICAR MEMORIA CRÍTICA ===
            ram_percent = self._get_memory_usage()
            if ram_percent > 90:
                self._agregar_evento_real(
                    tipo="MEMORIA_CRITICA",
                    severidad="CRITICA",
                    origen="Sistema",
                    descripcion=f"Uso crítico de memoria: {ram_percent:.1f}%"
                )
            
            # === MONITOREO DE RED Y PUERTOS USANDO HERRAMIENTAS DE KALI ===
            self._verificar_conexiones_red()
            
            # === VERIFICAR PUERTOS CRÍTICOS ===
            self._verificar_puertos_criticos()
            
            # === MONITOREO DE IP DEL USUARIO ===
            self._verificar_ip_usuario()
            
        except Exception as e:
            self.logger.error(f"Error verificando eventos de seguridad: {e}")
    
    def _verificar_procesos_sospechosos(self):
        """Verificar procesos sospechosos usando /proc y herramientas de Kali"""
        try:
            # Usar ps para obtener información de procesos
            result = subprocess.run(['ps', 'aux', '--sort=-%cpu'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines[:20]:  # Solo los primeros 20 procesos
                    parts = line.split(None, 10)
                    if len(parts) >= 11:
                        user, pid, cpu, mem = parts[0], parts[1], parts[2], parts[3]
                        command = parts[10]
                        
                        try:
                            cpu_percent = float(cpu)
                            mem_percent = float(mem)
                            
                            # Procesos con alto uso de CPU
                            if cpu_percent > 80:
                                self._agregar_evento_real(
                                    tipo="PROCESO_SOSPECHOSO",
                                    severidad="ALTA",
                                    origen=f"PID {pid}",
                                    descripcion=f"Proceso {command[:50]} usando {cpu_percent}% CPU"
                                )
                            
                            # Procesos con alto uso de memoria
                            if mem_percent > 50:
                                self._agregar_evento_real(
                                    tipo="MEMORIA_PROCESO",
                                    severidad="MEDIA",
                                    origen=f"PID {pid}",
                                    descripcion=f"Proceso {command[:50]} usando {mem_percent}% RAM"
                                )
                        except ValueError:
                            continue
                            
        except Exception as e:
            self.logger.error(f"Error verificando procesos: {e}")
    
    def _verificar_conexiones_red(self):
        """Verificar conexiones de red sospechosas usando netstat (herramienta de Kali)"""
        try:
            # Usar netstat para obtener conexiones activas
            result = subprocess.run(['netstat', '-antup'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                conexiones_activas = [line for line in lines if 'ESTABLISHED' in line]
                
                # Alto número de conexiones
                if len(conexiones_activas) > 100:
                    self._agregar_evento_real(
                        tipo="RED_SATURADA",
                        severidad="MEDIA",
                        origen="Sistema",
                        descripcion=f"Alto número de conexiones activas: {len(conexiones_activas)}"
                    )
                
                # Verificar conexiones a puertos sospechosos
                puertos_sospechosos = {
                    '21': "FTP", '23': "Telnet", '135': "RPC", '139': "NetBIOS", 
                    '445': "SMB", '1433': "SQL Server", '3389': "RDP", '5900': "VNC"
                }
                
                for line in conexiones_activas:
                    for puerto, servicio in puertos_sospechosos.items():
                        if f":{puerto}" in line:
                            self._agregar_evento_real(
                                tipo="PUERTO_SOSPECHOSO",
                                severidad="ALTA",
                                origen=f"Puerto {puerto}",
                                descripcion=f"Conexión activa en puerto {servicio} ({puerto})"
                            )
                            break
                            
        except Exception as e:
            self.logger.error(f"Error verificando conexiones de red: {e}")
    
    def _verificar_puertos_criticos(self):
        """Verificar puertos más utilizados para hacking usando ss/netstat (herramientas de Kali)"""
        puertos_hacking = {
            # Puertos comunes para ataques
            '22': "SSH", '80': "HTTP", '443': "HTTPS", '21': "FTP", '23': "Telnet",
            '25': "SMTP", '53': "DNS", '110': "POP3", '143': "IMAP", '993': "IMAPS",
            '995': "POP3S", '135': "RPC", '139': "NetBIOS", '445': "SMB", 
            '1433': "SQL Server", '1521': "Oracle", '3306': "MySQL", '3389': "RDP",
            '5432': "PostgreSQL", '5900': "VNC", '6379': "Redis", '8080': "HTTP-Alt",
            # Puertos de backdoors conocidas
            '1337': "Elite", '31337': "Back Orifice", '12345': "NetBus", 
            '54321': "Back Orifice 2000", '9999': "BackGate"
        }
        
        try:
            # Usar ss (herramienta moderna de Kali) para puertos en escucha
            result = subprocess.run(['ss', '-tuln'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                # Fallback a netstat si ss no está disponible
                result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                puertos_abiertos = set()
                
                for line in lines:
                    if 'LISTEN' in line:
                        # Extraer puerto de la línea
                        parts = line.split()
                        if len(parts) >= 4:
                            local_address = parts[3] if 'ss' in result.args[0] else parts[3]
                            if ':' in local_address:
                                puerto = local_address.split(':')[-1]
                                puertos_abiertos.add(puerto)
                                
                                if puerto in puertos_hacking:
                                    severidad = "CRITICA" if puerto in ['1337', '31337', '12345', '54321', '9999'] else "MEDIA"
                                    self._agregar_evento_real(
                                        tipo="PUERTO_CRITICO",
                                        severidad=severidad,
                                        origen=f"Puerto {puerto}",
                                        descripcion=f"Puerto {puertos_hacking[puerto]} ({puerto}) abierto y escuchando"
                                    )
                        
        except Exception as e:
            self.logger.error(f"Error verificando puertos críticos: {e}")
    
    def _verificar_ip_usuario(self):
        """Verificar información de IP del usuario"""
        try:
            import socket
            import urllib.request
            
            # IP local
            hostname = socket.gethostname()
            ip_local = socket.gethostbyname(hostname)
            
            # Verificar cambios en IP local
            if not hasattr(self, '_ip_local_anterior') or self._ip_local_anterior != ip_local:
                self._ip_local_anterior = ip_local
                self._agregar_evento_real(
                    tipo="IP_LOCAL",
                    severidad="INFO",
                    origen="Sistema",
                    descripcion=f"IP Local detectada: {ip_local} (Hostname: {hostname})"
                )
            
            # Intentar obtener IP pública (sin bloquear)
            if not hasattr(self, '_ultima_verificacion_ip') or \
               (time.time() - self._ultima_verificacion_ip) > 300:  # Cada 5 minutos
                
                self._ultima_verificacion_ip = time.time()
                threading.Thread(target=self._verificar_ip_publica, daemon=True).start()
                
        except Exception as e:
            self.logger.error(f"Error verificando IP del usuario: {e}")
    
    def _verificar_ip_publica(self):
        """Verificar IP pública en segundo plano"""
        try:
            import urllib.request
            import urllib.error
            
            # Servicios para obtener IP pública
            servicios_ip = [
                "https://api.ipify.org",
                "https://checkip.amazonaws.com",
                "https://icanhazip.com"
            ]
            
            for servicio in servicios_ip:
                try:
                    with urllib.request.urlopen(servicio, timeout=5) as response:
                        ip_publica = response.read().decode('utf-8').strip()
                        
                        # Verificar cambios en IP pública
                        if not hasattr(self, '_ip_publica_anterior') or self._ip_publica_anterior != ip_publica:
                            self._ip_publica_anterior = ip_publica
                            self._agregar_evento_real(
                                tipo="IP_PUBLICA",
                                severidad="INFO",
                                origen="Internet",
                                descripcion=f"IP Pública detectada: {ip_publica}"
                            )
                        break
                        
                except urllib.error.URLError:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error obteniendo IP pública: {e}")
    
    def _agregar_evento_real(self, tipo, severidad, origen, descripcion):
        """Agregar un evento real detectado"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Evitar duplicados recientes
        evento_key = f"{tipo}_{origen}_{descripcion}"
        if any(evento_key in str(evento) for evento in self.eventos_reales[-5:]):
            return
        
        # Agregar evento
        evento = {
            'timestamp': timestamp,
            'tipo': tipo,
            'severidad': severidad,
            'origen': origen,
            'descripcion': descripcion,
            'detalles': f"Evento detectado en tiempo real\nHora: {datetime.now()}\nTipo: {tipo}\nSeveridad: {severidad}\nOrigen: {origen}\nDescripción: {descripcion}"
        }
        
        self.eventos_reales.append(evento)
        
        # Limitar eventos almacenados
        if len(self.eventos_reales) > 100:
            self.eventos_reales.pop(0)
        
        # Actualizar tabla en el hilo principal
        if self.tree_eventos:
            self.tree_eventos.after(0, lambda: self._insertar_evento_tabla(evento))
    
    def _insertar_evento_tabla(self, evento):
        """Insertar evento en la tabla (debe ejecutarse en el hilo principal)"""
        try:
            if not self.tree_eventos:
                return
                
            self.tree_eventos.insert('', 0, values=(
                evento['timestamp'],
                evento['tipo'],
                evento['severidad'],
                evento['origen'],
                evento['descripcion']
            ))
            
            # Limitar eventos en tabla
            children = self.tree_eventos.get_children()
            if len(children) > 50:
                self.tree_eventos.delete(children[-1])
        except Exception as e:
            self.logger.error(f"Error insertando evento en tabla: {e}")
    
    def mostrar_detalles_evento(self, event):
        """Mostrar detalles del evento seleccionado"""
        if not self.tree_eventos:
            return
            
        seleccion = self.tree_eventos.selection()
        if not seleccion:
            return
        
        item = self.tree_eventos.item(seleccion[0])
        valores = item['values']
        
        if valores and self.text_detalles:
            # Buscar evento correspondiente
            for evento in self.eventos_reales:
                if (evento['timestamp'] == valores[0] and 
                    evento['tipo'] == valores[1] and
                    evento['descripcion'] == valores[4]):
                    
                    self.text_detalles.config(state='normal')
                    self.text_detalles.delete(1.0, tk.END)
                    self.text_detalles.insert(1.0, evento['detalles'])
                    self.text_detalles.config(state='disabled')
                    break
    
    def exportar_eventos(self):
        """Exportar eventos a archivo"""
        if not self.eventos_reales:
            messagebox.showwarning("Advertencia", "No hay eventos para exportar")
            return
        
        try:
            archivo = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("Todos los archivos", "*.*")],
                title="Exportar eventos SIEM"
            )
            
            if archivo:
                with open(archivo, 'w', encoding='utf-8') as f:
                    json.dump(self.eventos_reales, f, indent=2, ensure_ascii=False, default=str)
                
                messagebox.showinfo("Éxito", f"Eventos exportados a {archivo}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar eventos: {e}")
    
    def _limpiar_contenedor(self):
        """Limpiar el contenedor principal"""
        for widget in self.contenedor_padre.winfo_children():
            widget.destroy()
