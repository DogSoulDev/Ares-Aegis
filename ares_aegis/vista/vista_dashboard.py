#!/usr/bin/env python3
"""
Vista Dashboard para Ares Aegis
Tablero principal con métricas en tiempo real
"""

from ares_aegis.utils.utils_imports_comunes import (
    tk, ttk, messagebox, filedialog, logging, os, time, threading
)
from ares_aegis.vista.componentes_ui.emoticonos_mitologicos import EmoticonosMitologicos
from ares_aegis.vista.componentes_ui.terminal_integrado import TerminalIntegrado
from ares_aegis.vista.componentes_ui.sistema_ayuda import SistemaAyuda


class VistaDashboard:
    """Vista del dashboard principal con métricas en tiempo real"""
    
    def __init__(self, contenedor_padre, controlador, colores):
        self.contenedor_padre = contenedor_padre
        self.controlador = controlador
        self.colores = colores
        self.logger = logging.getLogger(__name__)
        self.frame_principal = None
        self.metricas_widgets = {}
        self.estadisticas_widgets = {}  # Para las estadísticas en tiempo real
        
        # Sistema de ayuda
        self.sistema_ayuda = SistemaAyuda(colores)
        self.start_time = time.time()
        self._tiempo_activo = True  # Flag para controlar actualizaciones de tiempo
        self.imagen_principal = None  # Para almacenar la imagen principal
        
        # Terminal integrado
        self.terminal_integrado = None
        
    def mostrar_informacion(self):
        """Mostrar información de ayuda sobre el Dashboard"""
        
        info_text = """🛡️ DASHBOARD - CENTRO DE COMANDO

📊 FUNCIONALIDADES PRINCIPALES:
• Monitoreo en tiempo real del sistema
• Métricas de seguridad centralizadas
• Terminal integrado para comandos directos
• Visión general del estado de Ares Aegis

⚡ PANELES DISPONIBLES:
• Métricas Principales: CPU, RAM, Red, Disco
• Actividad Reciente: Últimas acciones y alertas
• Estado del Sistema: Servicios y procesos activos
• Terminal Integrado: Ejecución de comandos directos

🎯 INFORMACIÓN EN TIEMPO REAL:
• Uso de recursos del sistema (CPU, memoria, red)
• Alertas de seguridad activas e historial
• Tiempo de actividad y estabilidad del sistema
• Estadísticas de red y procesos en ejecución

🔧 ACCIONES DISPONIBLES:
• Actualización automática de métricas cada 5 segundos
• Ejecución de comandos desde terminal integrado
• Navegación rápida a otros módulos del sistema
• Monitoreo continuo del estado de seguridad

💡 CONSEJOS DE USO:
• Mantén el dashboard abierto para supervisión continua
• Utiliza el terminal integrado para comandos rápidos
• Revisa regularmente las alertas de actividad reciente
• Monitorea el uso de recursos para detectar anomalías
• Las métricas se actualizan automáticamente sin intervención

🎮 CONTROLES DISPONIBLES:
• Botón de información para acceder a esta ayuda
• Acceso directo al terminal del sistema
• Enlaces rápidos a todas las funcionalidades de Ares Aegis
• Panel de control centralizado para gestión integral

🔐 OPTIMIZADO PARA KALI LINUX:
• Integración completa con herramientas nativas de Kali
• Comandos específicos de pentesting y auditoría
• Monitoreo adaptado a entornos de ciberseguridad
• Interface diseñada para profesionales de seguridad"""
        
        messagebox.showinfo("Información - Dashboard Centro de Comando", info_text)
        
    def crear_vista(self, area_contenido=None):
        """Crear vista dashboard estilo centralita profesional"""
        self._limpiar_contenedor()
        
        # Frame principal con padding estandarizado
        self.frame_principal = tk.Frame(self.contenedor_padre, bg=self.colores.fondo_secundario)
        self.frame_principal.pack(fill='both', expand=True, padx=20, pady=10)
        
        # === HEADER DE LA CENTRALITA ===
        self._crear_header_command_center()
        
        # === CONTENIDO PRINCIPAL CON GRID PROFESIONAL ===
        contenido_frame = tk.Frame(self.frame_principal, bg=self.colores.fondo_secundario)
        contenido_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Configurar grid responsive
        contenido_frame.grid_rowconfigure(0, weight=0)  # Métricas principales
        contenido_frame.grid_rowconfigure(1, weight=1)  # Área principal con imagen y métricas laterales
        contenido_frame.grid_rowconfigure(2, weight=1)  # Terminal integrado
        contenido_frame.grid_columnconfigure(0, weight=1)  # Panel izquierdo (Actividad)
        contenido_frame.grid_columnconfigure(1, weight=2)  # Panel central (Imagen)
        contenido_frame.grid_columnconfigure(2, weight=1)  # Panel derecho (Estado Sistema)
        
        # === MÉTRICAS PRINCIPALES ===
        self._crear_panel_metricas_principales(contenido_frame)
        
        # === PANEL IZQUIERDO: ACTIVIDAD RECIENTE ===
        self._crear_panel_actividad(contenido_frame)
        
        # === PANEL CENTRAL: IMAGEN PRINCIPAL ===
        self._crear_panel_imagen_central(contenido_frame)
        
        # === PANEL DERECHO: ESTADO DEL SISTEMA ===
        self._crear_panel_estado_sistema(contenido_frame)
        
        # === TERMINAL INTEGRADO ===
        self._crear_panel_terminal(contenido_frame)
        
        self.logger.info("Dashboard Centralita creado exitosamente")
    
    def _crear_header_command_center(self):
        """Crear header estilo centralita profesional"""
        header_frame = tk.Frame(self.frame_principal, 
                              bg=self.colores.negro_carbono, 
                              height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Configurar grid del header
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        header_frame.grid_columnconfigure(2, weight=0)
        header_frame.grid_columnconfigure(3, weight=0)
        
        # === TÍTULO PRINCIPAL ===
        titulo_frame = tk.Frame(header_frame, bg=self.colores.negro_carbono)
        titulo_frame.grid(row=0, column=0, sticky="nsw", padx=30, pady=20)
        
        tk.Label(titulo_frame,
                text="◢ CENTRO DE COMANDO",
                font=('Consolas', 20, 'bold'),
                fg=self.colores.verde_terminal,
                bg=self.colores.negro_carbono).pack(anchor='w')
        
        tk.Label(titulo_frame,
                text="CENTRO DE CONTROL Y MONITOREO",
                font=('Consolas', 10),
                fg=self.colores.gris_platino,
                bg=self.colores.negro_carbono).pack(anchor='w', pady=(2, 0))
        
        # === TIEMPO REAL ===
        tiempo_frame = tk.Frame(header_frame, bg=self.colores.negro_carbono)
        tiempo_frame.grid(row=0, column=1, sticky="ns", padx=20, pady=20)
        
        self.tiempo_label = tk.Label(tiempo_frame,
                                   text=time.strftime("%H:%M:%S"),
                                   font=('Consolas', 16, 'bold'),
                                   fg=self.colores.cyan_brillante,
                                   bg=self.colores.negro_carbono)
        self.tiempo_label.pack()
        
        tk.Label(tiempo_frame,
                text=time.strftime("%Y-%m-%d"),
                font=('Consolas', 9),
                fg=self.colores.gris_platino,
                bg=self.colores.negro_carbono).pack()
        
        # === STATUS GENERAL ===
        status_frame = tk.Frame(header_frame, bg=self.colores.negro_carbono)
        status_frame.grid(row=0, column=2, sticky="nse", padx=30, pady=20)
        
        tk.Label(status_frame,
                text="● OPERATIVO",
                font=('Consolas', 12, 'bold'),
                fg=self.colores.verde_terminal,
                bg=self.colores.negro_carbono).pack(anchor='e')
        
        tk.Label(status_frame,
                text="TODOS LOS SISTEMAS NOMINALES",
                font=('Consolas', 8),
                fg=self.colores.gris_platino,
                bg=self.colores.negro_carbono).pack(anchor='e')
        
        # === BOTÓN DE INFORMACIÓN ===
        info_frame = tk.Frame(header_frame, bg=self.colores.negro_carbono)
        info_frame.grid(row=0, column=3, sticky="nse", padx=20, pady=20)
        
        tk.Button(info_frame,
                 text="❓ Info",
                 font=('Consolas', 10),
                 bg=self.colores.verde_terminal,
                 fg=self.colores.negro_carbono,
                 command=self.mostrar_informacion,
                 relief='flat',
                 padx=10,
                 pady=5).pack()
        
        # Actualizar tiempo cada segundo
        self._actualizar_tiempo()
        
        # Iniciar actualización de métricas cada 3 segundos
        self._actualizar_metricas_tiempo_real()
    
    def _crear_panel_imagen_central(self, parent):
        """Crear panel central con la imagen principal de Ares Aegis"""
        imagen_frame = tk.Frame(parent, bg=self.colores.fondo_secundario)
        imagen_frame.grid(row=1, column=1, sticky="nsew", padx=20, pady=10)
        
        try:
            # Construir la ruta a la imagen
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            imagen_path = os.path.join(base_dir, "recursos", "AresAegis.png")
            
            if os.path.exists(imagen_path):
                # Cargar imagen
                self.imagen_principal = tk.PhotoImage(file=imagen_path)
                
                # Redimensionar si es necesario (ajustar tamaño)
                width_original = self.imagen_principal.width()
                height_original = self.imagen_principal.height()
                max_width = 350
                
                if width_original > max_width:
                    factor = max(1, width_original // max_width)
                    self.imagen_principal = self.imagen_principal.subsample(factor)
                
                # Mostrar imagen centrada
                label_imagen = tk.Label(imagen_frame, 
                                      image=self.imagen_principal,
                                      bg=self.colores.fondo_secundario)
                label_imagen.pack(expand=True, anchor='center')
                
                self.logger.info(f"🖼️ Imagen principal cargada desde: {imagen_path}")
            else:
                self.logger.warning(f"No se encontró la imagen principal en: {imagen_path}")
                # Mostrar texto alternativo
                texto_label = tk.Label(imagen_frame,
                        text="🛡️ ARES AEGIS\nSISTEMA DE CIBERSEGURIDAD",
                        font=('Consolas', 16, 'bold'),
                        fg=self.colores.verde_terminal,
                        bg=self.colores.fondo_secundario,
                        justify='center')
                texto_label.pack(expand=True, anchor='center')
                
        except Exception as e:
            self.logger.error(f"Error cargando imagen principal: {e}")
            # Mostrar texto alternativo en caso de error
            texto_label = tk.Label(imagen_frame,
                    text="🛡️ ARES AEGIS\nSISTEMA DE CIBERSEGURIDAD",
                    font=('Consolas', 16, 'bold'),
                    fg=self.colores.verde_terminal,
                    bg=self.colores.fondo_secundario,
                    justify='center')
            texto_label.pack(expand=True, anchor='center')
    
    def _crear_panel_metricas_principales(self, parent):
        """Crear panel de métricas principales estilo SOC"""
        metricas_container = tk.Frame(parent, bg=self.colores.fondo_secundario)
        metricas_container.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        
        # Grid de métricas - DATOS EN TIEMPO REAL
        self.metricas_data = [
            ("USO DE CPU", "0%", self.colores.verde_terminal, "Carga del sistema en tiempo real"),
            ("MEMORIA", "0%", self.colores.amarillo_medio, "Uso de memoria en tiempo real"),
            ("AMENAZAS", "0", self.colores.verde_terminal, "Amenazas detectadas hoy"),
            ("ESCANEADOS", "0", self.colores.cyan_brillante, "Archivos procesados hoy"),
            ("CUARENTENA", "0", self.colores.naranja_alto, "Archivos en cuarentena"),
            ("TIEMPO ACTIVO", self._calcular_uptime(), self.colores.verde_esmeralda, "Tiempo operativo del sistema")
        ]
        
        # Crear tarjetas de métricas
        for i, (titulo, valor, color, descripcion) in enumerate(self.metricas_data):
            col = i % 3
            row = i // 3
            
            # Tarjeta individual
            tarjeta = tk.Frame(metricas_container, 
                             bg=self.colores.gris_pizarra, 
                             relief='flat', 
                             bd=1)
            tarjeta.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            metricas_container.grid_columnconfigure(col, weight=1)
            
            # Contenido de la tarjeta
            tk.Label(tarjeta,
                    text=titulo,
                    font=('Consolas', 10, 'bold'),
                    fg=self.colores.gris_platino,
                    bg=self.colores.gris_pizarra).pack(pady=(15, 5))
            
            valor_label = tk.Label(tarjeta,
                                  text=valor,
                                  font=('Consolas', 24, 'bold'),
                                  fg=color,
                                  bg=self.colores.gris_pizarra)
            valor_label.pack(pady=5)
            
            tk.Label(tarjeta,
                    text=descripcion,
                    font=('Consolas', 8),
                    fg=self.colores.gris_platino,
                    bg=self.colores.gris_pizarra,
                    wraplength=150,
                    justify='center').pack(pady=(5, 15))
            
            # Guardar referencia para actualizaciones
            metrica_key = titulo.lower().replace(' ', '_')
            if metrica_key == "uso_de_cpu":
                self.metricas_widgets['cpu_usage'] = valor_label
            elif metrica_key == "memoria":
                self.metricas_widgets['memory'] = valor_label
            elif metrica_key == "amenazas":
                self.metricas_widgets['threats'] = valor_label
            elif metrica_key == "escaneados":
                self.metricas_widgets['scanned'] = valor_label
            elif metrica_key == "cuarentena":
                self.metricas_widgets['quarantine'] = valor_label
            else:
                self.metricas_widgets[metrica_key] = valor_label
    
    def _crear_panel_actividad(self, parent):
        """Crear panel de actividad reciente con icono para limpiar"""
        actividad_frame = tk.LabelFrame(parent,
                                      text="",  # Vacío porque crearemos un header personalizado
                                      bg=self.colores.fondo_secundario,
                                      fg=self.colores.cyan_brillante,
                                      font=('Consolas', 12, 'bold'),
                                      relief='flat',
                                      bd=1)
        actividad_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        
        # Header personalizado con título e icono de limpiar
        header_frame = tk.Frame(actividad_frame, bg=self.colores.fondo_secundario)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(header_frame,
                text="📊 ACTIVIDAD RECIENTE",
                font=('Consolas', 12, 'bold'),
                fg=self.colores.cyan_brillante,
                bg=self.colores.fondo_secundario).pack(side='left')
        
        # Botón limpiar actividad
        btn_limpiar_actividad = tk.Button(header_frame,
                                        text="🗑️",
                                        font=('Consolas', 12),
                                        fg=self.colores.naranja_alto,
                                        bg=self.colores.fondo_terciario,
                                        relief='flat',
                                        cursor='hand2',
                                        width=3,
                                        command=self._limpiar_actividad)
        btn_limpiar_actividad.pack(side='right', padx=5)
        
        # Lista de actividades con scroll
        self.lista_actividad_frame = tk.Frame(actividad_frame, bg=self.colores.negro_carbono)
        self.lista_actividad_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Inicializar actividades
        self._cargar_actividades_iniciales()
    
    def _cargar_actividades_iniciales(self):
        """Cargar actividades iniciales en el panel"""
        actividades = [
            ("12:34:56", "Escaneo del sistema completado", "INFO", self.colores.cyan_brillante),
            ("12:33:21", "Firmas de amenazas actualizadas", "ÉXITO", self.colores.verde_terminal),
            ("12:32:15", "Archivo en cuarentena: malware.bin", "ADVERTENCIA", self.colores.amarillo_medio),
            ("12:30:44", "Monitor de red iniciado", "INFO", self.colores.cyan_brillante),
            ("12:29:33", "Respaldo del sistema completado", "ÉXITO", self.colores.verde_terminal),
            ("12:28:12", "Configuración actualizada", "INFO", self.colores.cyan_brillante),
            ("12:27:08", "Uso de memoria incrementado", "ADVERTENCIA", self.colores.amarillo_medio),
            ("12:26:01", "Escaneo de puertos detectado", "ALERTA", self.colores.naranja_alto)
        ]
        
        for tiempo, mensaje, tipo, color in actividades:
            self._agregar_actividad(tiempo, mensaje, tipo, color)
    
    def _agregar_actividad(self, tiempo, mensaje, tipo, color):
        """Agregar una actividad al panel"""
        actividad_row = tk.Frame(self.lista_actividad_frame, bg=self.colores.negro_carbono)
        actividad_row.pack(fill='x', pady=2)
        
        # Tiempo
        tk.Label(actividad_row,
                text=tiempo,
                font=('Consolas', 8, 'bold'),
                fg=self.colores.gris_platino,
                bg=self.colores.negro_carbono,
                width=8).pack(side='left')
        
        # Tipo
        tk.Label(actividad_row,
                text=f"[{tipo}]",
                font=('Consolas', 8, 'bold'),
                fg=color,
                bg=self.colores.negro_carbono,
                width=10).pack(side='left', padx=5)
        
        # Mensaje
        tk.Label(actividad_row,
                text=mensaje,
                font=('Consolas', 8),
                fg=self.colores.blanco_hueso,
                bg=self.colores.negro_carbono,
                anchor='w',
                wraplength=200).pack(side='left', fill='x', expand=True)
    
    def _limpiar_actividad(self):
        """Limpiar todas las actividades y comenzar de nuevo"""
        # Limpiar widget
        for widget in self.lista_actividad_frame.winfo_children():
            widget.destroy()
        
        # Agregar mensaje de reinicio
        reinicio_time = time.strftime("%H:%M:%S")
        self._agregar_actividad(reinicio_time, "Panel de actividad reiniciado", "SISTEMA", self.colores.verde_esmeralda)
        
        self.logger.info("Panel de actividad limpiado y reiniciado")
    
    def _crear_panel_estado_sistema(self, parent):
        """Crear panel de estado del sistema con icono para limpiar"""
        estado_frame = tk.LabelFrame(parent,
                                   text="",  # Vacío porque crearemos un header personalizado
                                   bg=self.colores.fondo_secundario,
                                   fg=self.colores.verde_terminal,
                                   font=('Consolas', 12, 'bold'),
                                   relief='flat',
                                   bd=1)
        estado_frame.grid(row=1, column=2, sticky="nsew", padx=(10, 0), pady=(0, 10))
        
        # Header personalizado con título e icono de limpiar
        header_frame = tk.Frame(estado_frame, bg=self.colores.fondo_secundario)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(header_frame,
                text="⚡ ESTADO DEL SISTEMA",
                font=('Consolas', 12, 'bold'),
                fg=self.colores.verde_terminal,
                bg=self.colores.fondo_secundario).pack(side='left')
        
        # Botón reiniciar estado
        btn_reiniciar_estado = tk.Button(header_frame,
                                       text="🔄",
                                       font=('Consolas', 12),
                                       fg=self.colores.cyan_brillante,
                                       bg=self.colores.fondo_terciario,
                                       relief='flat',
                                       cursor='hand2',
                                       width=3,
                                       command=self._reiniciar_estado_sistema)
        btn_reiniciar_estado.pack(side='right', padx=5)
        
        # Contenido del estado
        self.contenido_estado = tk.Frame(estado_frame, bg=self.colores.negro_carbono)
        self.contenido_estado.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Cargar estado inicial
        self._cargar_estado_inicial()
    
    def _cargar_estado_inicial(self):
        """Cargar estado inicial del sistema"""
        # === MÓDULOS DEL SISTEMA ===
        tk.Label(self.contenido_estado,
                text="ESTADO DE MÓDULOS",
                font=('Consolas', 10, 'bold'),
                fg=self.colores.cyan_brillante,
                bg=self.colores.negro_carbono).pack(anchor='w', pady=(0, 10))
        
        modulos = [
            ("Motor de Escaneo", True),
            ("Monitor de Red", True),
            ("Monitor de Archivos", True),
            ("Detección de Amenazas", True),
            ("Sistema de Cuarentena", True),
            ("Generador de Reportes", True)
        ]
        
        for nombre, activo in modulos:
            self._agregar_modulo_estado(nombre, activo)
        
        # === ESTADÍSTICAS RÁPIDAS ===
        tk.Label(self.contenido_estado,
                text="ESTADÍSTICAS RÁPIDAS",
                font=('Consolas', 10, 'bold'),
                fg=self.colores.cyan_brillante,
                bg=self.colores.negro_carbono).pack(anchor='w', pady=(20, 10))
        
        # Inicializar estadísticas en tiempo real (empiezan en 0)
        self.estadisticas_widgets = {}
        estadisticas_iniciales = [
            ("Procesos Monitoreados", "0"),
            ("Conexiones Activas", "0"),
            ("Archivos Vigilados", "0"),
            ("Último Escaneo", "Nunca")
        ]
        
        for nombre, valor in estadisticas_iniciales:
            widget_valor = self._agregar_estadistica(nombre, valor)
            # Guardar referencia para actualizaciones
            key = nombre.lower().replace(' ', '_').replace('ú', 'u')
            self.estadisticas_widgets[key] = widget_valor
    
    def _agregar_modulo_estado(self, nombre, activo):
        """Agregar un módulo al estado del sistema"""
        modulo_row = tk.Frame(self.contenido_estado, bg=self.colores.negro_carbono)
        modulo_row.pack(fill='x', pady=2)
        
        # Indicador
        indicador = "●" if activo else "○"
        color = self.colores.verde_terminal if activo else self.colores.rojo_critico
        
        tk.Label(modulo_row,
                text=indicador,
                font=('Consolas', 10, 'bold'),
                fg=color,
                bg=self.colores.negro_carbono).pack(side='left')
        
        tk.Label(modulo_row,
                text=nombre,
                font=('Consolas', 8),
                fg=self.colores.blanco_hueso,
                bg=self.colores.negro_carbono,
                anchor='w').pack(side='left', padx=(10, 0), fill='x', expand=True)
    
    def _agregar_estadistica(self, nombre, valor):
        """Agregar una estadística al panel y retornar el widget del valor para actualizaciones"""
        stat_row = tk.Frame(self.contenido_estado, bg=self.colores.negro_carbono)
        stat_row.pack(fill='x', pady=2)
        
        tk.Label(stat_row,
                text=f"{nombre}:",
                font=('Consolas', 8),
                fg=self.colores.gris_platino,
                bg=self.colores.negro_carbono,
                anchor='w').pack(side='left')
        
        valor_widget = tk.Label(stat_row,
                               text=valor,
                               font=('Consolas', 8, 'bold'),
                               fg=self.colores.verde_esmeralda,
                               bg=self.colores.negro_carbono,
                               anchor='e')
        valor_widget.pack(side='right')
        
        return valor_widget
    
    def _reiniciar_estado_sistema(self):
        """Reiniciar el estado del sistema y las estadísticas"""
        # Limpiar contenido
        for widget in self.contenido_estado.winfo_children():
            widget.destroy()
        
        # Limpiar referencias de estadísticas
        self.estadisticas_widgets.clear()
        
        # Recargar estado inicial (todo en 0)
        self._cargar_estado_inicial()
        
        self.logger.info("Estado del sistema y estadísticas reiniciados")
    
    def _crear_panel_terminal(self, parent):
        """Crear panel del terminal integrado"""
        terminal_frame = tk.LabelFrame(parent,
                                     text=f"💻 {EmoticonosMitologicos.HERMES} TERMINAL INTEGRADO",
                                     bg=self.colores.fondo_secundario,
                                     fg=self.colores.acento_primario,
                                     font=('Consolas', 12, 'bold'),
                                     relief='flat',
                                     bd=1)
        terminal_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(20, 0))
        
        # Crear instancia del terminal
        try:
            self.terminal_integrado = TerminalIntegrado(terminal_frame, self.colores)
            terminal_widget = self.terminal_integrado.crear_terminal_widget()
            terminal_widget.pack(fill='both', expand=True, padx=10, pady=10)
            
            self.logger.info("Terminal integrado creado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error creando terminal integrado: {e}")
            
            # Mostrar mensaje de error en caso de fallo
            error_label = tk.Label(terminal_frame,
                                 text=f"⚠️ Error: Terminal no disponible en este sistema\n{str(e)}",
                                 font=('Consolas', 10),
                                 fg=self.colores.error,
                                 bg=self.colores.fondo_secundario,
                                 justify='center')
            error_label.pack(expand=True, fill='both', padx=20, pady=20)
        
    def _actualizar_tiempo(self):
        """Actualizar el tiempo en tiempo real"""
        if not self._tiempo_activo:
            return
            
        if hasattr(self, 'tiempo_label') and self.tiempo_label.winfo_exists():
            try:
                self.tiempo_label.configure(text=time.strftime("%H:%M:%S"))
                self.tiempo_label.after(1000, self._actualizar_tiempo)
            except tk.TclError:
                # Widget ha sido destruido, detener actualizaciones
                self._tiempo_activo = False
    
    def _calcular_uptime(self):
        """Calcular tiempo de actividad"""
        uptime_seconds = time.time() - self.start_time
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    
    def _limpiar_contenedor(self):
        """Limpiar el contenedor padre de forma segura"""
        try:
            for widget in self.contenedor_padre.winfo_children():
                try:
                    widget.destroy()
                except tk.TclError:
                    # Widget ya destruido, continuar
                    pass
        except tk.TclError:
            # Contenedor padre ya destruido
            pass
    
    def actualizar_metricas(self, metricas):
        """Actualizar métricas en tiempo real"""
        if not self.metricas_widgets or not metricas:
            return
        
        try:
            # Actualizar widgets de métricas de forma segura
            if 'cpu_usage' in self.metricas_widgets and 'cpu_percent' in metricas:
                if self.metricas_widgets['cpu_usage'].winfo_exists():
                    self.metricas_widgets['cpu_usage'].configure(
                        text=f"{metricas['cpu_percent']:.1f}%"
                    )
            
            if 'memory' in self.metricas_widgets and 'memoria_percent' in metricas:
                if self.metricas_widgets['memory'].winfo_exists():
                    self.metricas_widgets['memory'].configure(
                        text=f"{metricas['memoria_percent']:.1f}%"
                    )
            
            if 'threats' in self.metricas_widgets and 'amenazas_detectadas' in metricas:
                if self.metricas_widgets['threats'].winfo_exists():
                    self.metricas_widgets['threats'].configure(
                        text=str(metricas['amenazas_detectadas'])
                    )
            
            if 'scanned' in self.metricas_widgets and 'archivos_escaneados' in metricas:
                if self.metricas_widgets['scanned'].winfo_exists():
                    self.metricas_widgets['scanned'].configure(
                        text=str(metricas['archivos_escaneados'])
                    )
            
            if 'quarantine' in self.metricas_widgets and 'archivos_cuarentena' in metricas:
                if self.metricas_widgets['quarantine'].winfo_exists():
                    self.metricas_widgets['quarantine'].configure(
                        text=str(metricas['archivos_cuarentena'])
                    )
                    
        except (tk.TclError, AttributeError, KeyError) as e:
            self.logger.error(f"Error actualizando métricas: {e}")
        except Exception as e:
            self.logger.error(f"Error inesperado actualizando métricas: {e}")
    
    def destruir_vista(self):
        """Destruir la vista y limpiar recursos"""
        self._tiempo_activo = False  # Detener actualizaciones de tiempo
        self.metricas_widgets.clear()  # Limpiar referencias de widgets
        self._limpiar_contenedor()  # Limpiar contenedor
    
    def _actualizar_metricas_tiempo_real(self):
        """Actualizar métricas del sistema en tiempo real"""
        if not self._tiempo_activo or not self.metricas_widgets:
            return
        
        try:
            # Obtener métricas reales del controlador
            if hasattr(self.controlador, 'obtener_estado_sistema'):
                estado = self.controlador.obtener_estado_sistema()
                recursos = estado.get('recursos_sistema', {})
                metricas_base = estado.get('metricas', {})
                
                # Actualizar CPU
                if 'cpu_usage' in self.metricas_widgets:
                    cpu_val = recursos.get('cpu_percent', 0)
                    if self.metricas_widgets['cpu_usage'].winfo_exists():
                        self.metricas_widgets['cpu_usage'].configure(text=f"{cpu_val:.1f}%")
                
                # Actualizar Memoria
                if 'memory' in self.metricas_widgets:
                    mem_val = recursos.get('memoria_percent', 0)
                    if self.metricas_widgets['memory'].winfo_exists():
                        self.metricas_widgets['memory'].configure(text=f"{mem_val:.1f}%")
                
                # Actualizar Amenazas
                if 'threats' in self.metricas_widgets:
                    threats_val = metricas_base.get('amenazas_detectadas', 0)
                    if self.metricas_widgets['threats'].winfo_exists():
                        self.metricas_widgets['threats'].configure(text=str(threats_val))
                
                # Actualizar Escaneados
                if 'scanned' in self.metricas_widgets:
                    scanned_val = metricas_base.get('archivos_escaneados', 0)
                    if self.metricas_widgets['scanned'].winfo_exists():
                        self.metricas_widgets['scanned'].configure(text=f"{scanned_val:,}")
                
                # Actualizar Cuarentena
                if 'quarantine' in self.metricas_widgets:
                    quarantine_val = metricas_base.get('archivos_cuarentena', 0)
                    if self.metricas_widgets['quarantine'].winfo_exists():
                        self.metricas_widgets['quarantine'].configure(text=str(quarantine_val))
                
                # === ACTUALIZAR ESTADÍSTICAS RÁPIDAS ===
                self._actualizar_estadisticas_rapidas(estado)
                        
            # Programar próxima actualización en 3 segundos
            if self._tiempo_activo and self.frame_principal:
                self.frame_principal.after(3000, self._actualizar_metricas_tiempo_real)
                
        except Exception as e:
            self.logger.error(f"Error actualizando métricas en tiempo real: {e}")
            # Reintentar en 5 segundos si hay error
            if self._tiempo_activo and self.frame_principal:
                self.frame_principal.after(5000, self._actualizar_metricas_tiempo_real)
    
    def _actualizar_estadisticas_rapidas(self, estado):
        """Actualizar las estadísticas rápidas en tiempo real"""
        if not self.estadisticas_widgets:
            return
        
        try:
            metricas = estado.get('metricas', {})
            recursos = estado.get('recursos_sistema', {})
            
            # Actualizar Procesos Monitoreados
            if 'procesos_monitoreados' in self.estadisticas_widgets:
                procesos = recursos.get('procesos_activos', 0)
                if self.estadisticas_widgets['procesos_monitoreados'].winfo_exists():
                    self.estadisticas_widgets['procesos_monitoreados'].configure(text=str(procesos))
            
            # Actualizar Conexiones Activas  
            if 'conexiones_activas' in self.estadisticas_widgets:
                conexiones = recursos.get('conexiones_red', 0)
                if self.estadisticas_widgets['conexiones_activas'].winfo_exists():
                    self.estadisticas_widgets['conexiones_activas'].configure(text=str(conexiones))
            
            # Actualizar Archivos Vigilados
            if 'archivos_vigilados' in self.estadisticas_widgets:
                archivos = metricas.get('archivos_monitoreados', 0)
                if self.estadisticas_widgets['archivos_vigilados'].winfo_exists():
                    if archivos > 0:
                        self.estadisticas_widgets['archivos_vigilados'].configure(text=f"{archivos:,}")
                    else:
                        self.estadisticas_widgets['archivos_vigilados'].configure(text="0")
            
            # Actualizar Último Escaneo
            if 'ultimo_escaneo' in self.estadisticas_widgets:
                ultimo_escaneo = metricas.get('ultimo_escaneo', None)
                if self.estadisticas_widgets['ultimo_escaneo'].winfo_exists():
                    if ultimo_escaneo:
                        self.estadisticas_widgets['ultimo_escaneo'].configure(text=ultimo_escaneo)
                    else:
                        self.estadisticas_widgets['ultimo_escaneo'].configure(text="Nunca")
                        
        except Exception as e:
            self.logger.error(f"Error actualizando estadísticas rápidas: {e}")
    
    def actualizar_estadistica_evento(self, tipo_evento, valor=None):
        """Actualizar estadística específica cuando ocurre un evento"""
        try:
            current_time = time.strftime("%H:%M:%S")
            
            if tipo_evento == "escaneo_completado":
                # Actualizar último escaneo
                if 'ultimo_escaneo' in self.estadisticas_widgets:
                    if self.estadisticas_widgets['ultimo_escaneo'].winfo_exists():
                        self.estadisticas_widgets['ultimo_escaneo'].configure(text=current_time)
                
                # Agregar actividad al panel
                self._agregar_actividad(current_time, "Escaneo del sistema completado", "ÉXITO", self.colores.verde_terminal)
            
            elif tipo_evento == "archivo_monitoreado":
                # Incrementar archivos vigilados
                if 'archivos_vigilados' in self.estadisticas_widgets:
                    if self.estadisticas_widgets['archivos_vigilados'].winfo_exists():
                        try:
                            current_text = self.estadisticas_widgets['archivos_vigilados'].cget('text')
                            current_val = int(current_text.replace(',', '')) if current_text != "0" else 0
                            new_val = current_val + (valor if valor else 1)
                            self.estadisticas_widgets['archivos_vigilados'].configure(text=f"{new_val:,}")
                        except (ValueError, AttributeError):
                            self.estadisticas_widgets['archivos_vigilados'].configure(text="1")
            
            elif tipo_evento == "conexion_detectada":
                # Actualizar conexiones activas
                if 'conexiones_activas' in self.estadisticas_widgets:
                    if self.estadisticas_widgets['conexiones_activas'].winfo_exists():
                        if valor:
                            self.estadisticas_widgets['conexiones_activas'].configure(text=str(valor))
                        else:
                            try:
                                current_text = self.estadisticas_widgets['conexiones_activas'].cget('text')
                                current_val = int(current_text) if current_text != "0" else 0
                                self.estadisticas_widgets['conexiones_activas'].configure(text=str(current_val + 1))
                            except (ValueError, AttributeError):
                                self.estadisticas_widgets['conexiones_activas'].configure(text="1")
            
            elif tipo_evento == "proceso_monitoreado":
                # Actualizar procesos monitoreados
                if 'procesos_monitoreados' in self.estadisticas_widgets:
                    if self.estadisticas_widgets['procesos_monitoreados'].winfo_exists():
                        if valor:
                            self.estadisticas_widgets['procesos_monitoreados'].configure(text=str(valor))
                        else:
                            try:
                                current_text = self.estadisticas_widgets['procesos_monitoreados'].cget('text')
                                current_val = int(current_text) if current_text != "0" else 0
                                self.estadisticas_widgets['procesos_monitoreados'].configure(text=str(current_val + 1))
                            except (ValueError, AttributeError):
                                self.estadisticas_widgets['procesos_monitoreados'].configure(text="1")
                                
        except Exception as e:
            self.logger.error(f"Error actualizando estadística por evento {tipo_evento}: {e}")
    
    def agregar_actividad_usuario(self, mensaje, tipo="INFO"):
        """Método público para agregar actividades desde otros módulos"""
        try:
            current_time = time.strftime("%H:%M:%S")
            
            # Mapear tipos a colores
            colores_tipo = {
                "INFO": self.colores.cyan_brillante,
                "ÉXITO": self.colores.verde_terminal,
                "ADVERTENCIA": self.colores.amarillo_medio,
                "ALERTA": self.colores.naranja_alto,
                "ERROR": self.colores.rojo_critico,
                "SISTEMA": self.colores.verde_esmeralda
            }
            
            color = colores_tipo.get(tipo.upper(), self.colores.cyan_brillante)
            self._agregar_actividad(current_time, mensaje, tipo, color)
            
        except Exception as e:
            self.logger.error(f"Error agregando actividad de usuario: {e}")
    
    def incrementar_estadistica(self, tipo_estadistica, incremento=1):
        """Método público para incrementar estadísticas específicas"""
        try:
            if tipo_estadistica == "archivos_vigilados":
                self.actualizar_estadistica_evento("archivo_monitoreado", incremento)
            elif tipo_estadistica == "conexiones_activas":
                self.actualizar_estadistica_evento("conexion_detectada", incremento)
            elif tipo_estadistica == "procesos_monitoreados":
                self.actualizar_estadistica_evento("proceso_monitoreado", incremento)
                
        except Exception as e:
            self.logger.error(f"Error incrementando estadística {tipo_estadistica}: {e}")
    
    def marcar_ultimo_escaneo(self):
        """Método público para marcar el tiempo del último escaneo"""
        self.actualizar_estadistica_evento("escaneo_completado")
