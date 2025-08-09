from ares_aegis.utils.utils_imports_comunes import (
    tk, ttk, messagebox, filedialog, logging, os, time, threading
)
import subprocess
import re
from ares_aegis.vista.componentes_ui.emoticonos_mitologicos import EmoticonosMitologicos
from ares_aegis.vista.componentes_ui.sistema_ayuda import SistemaAyuda
from ares_aegis.vista.componentes_ui.vista_base import VistaBase
from ares_aegis.vista.componentes_ui.metricas_tiempo_real import MetricasTiempoReal


class VistaMonitor(VistaBase):
    
    def __init__(self, contenedor_padre, controlador, colores):
        super().__init__(contenedor_padre, controlador, colores)
        
        # Variables específicas del monitor
        self.monitoreo_activo = False
        self.hilo_monitoreo = None
        self.resultados_text = None
        self.sistema_ayuda = SistemaAyuda(colores)
        
        # Inicializar componentes auxiliares
        self.metricas_tiempo_real = MetricasTiempoReal(controlador, self._callback_metricas)
        
    def _get_estado_inicial(self):
        return " DETENIDO"
        
    def _get_titulo_ventana(self):
        return "MONITOR DEL SISTEMA - SUPERVISIÓN INTEGRAL"
        
    def _get_descripcion_funcionalidades(self):
        return """ FUNCIONALIDADES:
• Monitoreo en tiempo real del sistema
• Análisis de procesos y servicios
• Supervisión de recursos (CPU, RAM, Red, Disco)
• Detección de actividad sospechosa

 HERRAMIENTAS:
• ps aux: Listado de procesos
• netstat: Conexiones de red
• lsof: Archivos abiertos
• htop: Monitor de recursos
• ss: Estado de conexiones

[TARGET] MÉTRICAS:
• Uso de CPU por proceso
• Consumo de memoria
• Conexiones de red activas
• Archivos y puertos abiertos

[STATS] ESTADOS:
•  NORMAL: Actividad estándar
•  ADVERTENCIA: Uso elevado de recursos
•  CRÍTICO: Actividad sospechosa
•  ERROR: Problema del sistema

 USO:
• Monitoreo periódico para líneas base
• Revisar procesos con consumo anómalo
• Verificar conexiones inusuales
• Analizar archivos abiertos sospechosos"""
        
    def _callback_metricas(self, metricas):
        """Callback para actualizar métricas en la interfaz"""
        if hasattr(self, 'estado_label'):
            estado = self._determinar_estado_sistema(metricas)
            self.actualizar_estado(estado)
    
    def _determinar_estado_sistema(self, metricas):
        """Determinar estado del sistema basado en métricas"""
        if not metricas:
            return " ERROR"
        
        cpu_uso = metricas.get('cpu_percent', 0)
        mem_uso = metricas.get('memory_percent', 0)
        
        if cpu_uso > 90 or mem_uso > 95:
            return " CRÍTICO"
        elif cpu_uso > 70 or mem_uso > 80:
            return " ADVERTENCIA"
        else:
            return " NORMAL"

    def crear_vista(self, area_contenido=None):
        """Crear la vista del monitor usando componentes modulares"""
        self.limpiar_vista()
        
        # Frame principal usando vista base
        self._crear_frame_principal()
        
        # Header simplificado
        self._crear_header_monitor_simple()
        
        # Panel de control unificado
        self._crear_panel_control_simple()
        
        # Contenido principal con terminal integrado
        self._crear_contenido_con_terminal()
        
    def _crear_header_monitor_simple(self):
        """Crear header simplificado del monitor"""
        header_frame = tk.Frame(self.frame_principal, bg=self.colores.negro_carbono, height=80)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Título principal
        titulo_label = tk.Label(header_frame,
                               text=f" {EmoticonosMitologicos.ARGOS} MONITOR DEL SISTEMA",
                               font=('Consolas', 18, 'bold'),
                               fg=self.colores.verde_terminal,
                               bg=self.colores.negro_carbono)
        titulo_label.pack(expand=True)
        
    def _crear_panel_control_simple(self):
        """Crear panel de control simplificado"""
        control_frame = tk.Frame(self.frame_principal, bg=self.colores.fondo_terciario, height=60)
        control_frame.pack(fill='x', pady=(0, 10))
        control_frame.pack_propagate(False)
        
        # Estado del monitor
        self.estado_label = tk.Label(control_frame,
                                    textvariable=self.estado_var,
                                    font=('Consolas', 12, 'bold'),
                                    fg=self.colores.rojo_critico,
                                    bg=self.colores.fondo_terciario)
        self.estado_label.pack(side='left', padx=20, pady=15)
        
        # Botones de control
        self.btn_iniciar = tk.Button(control_frame,
                                   text=" Iniciar Monitor",
                                   font=('Consolas', 10),
                                   bg=self.colores.verde_terminal,
                                   fg=self.colores.negro_carbono,
                                   command=self._iniciar_monitoreo_completo,
                                   relief='flat',
                                   padx=15)
        self.btn_iniciar.pack(side='left', padx=10, pady=15)
        
        self.btn_detener = tk.Button(control_frame,
                                   text="⏹ Detener Monitor",
                                   font=('Consolas', 10),
                                   bg=self.colores.rojo_critico,
                                   fg=self.colores.blanco_hueso,
                                   command=self._detener_monitoreo_completo,
                                   relief='flat',
                                   padx=15,
                                   state='disabled')
        self.btn_detener.pack(side='left', padx=10, pady=15)
        
        # Botón de info usando clase base
        info_button = tk.Button(control_frame,
                               text=" Info",
                               font=('Consolas', 10),
                               bg=self.colores.cyan_brillante,
                               fg=self.colores.negro_carbono,
                               command=self.mostrar_informacion,
                               relief='flat',
                               padx=15)
        info_button.pack(side='right', padx=20, pady=15)
        
    def _crear_contenido_con_terminal(self):
        """Crear contenido principal con terminal integrado"""
        contenido_frame = tk.Frame(self.frame_principal, bg=self.colores.fondo_secundario)
        contenido_frame.pack(fill='both', expand=True)
        
        # Panel de métricas en tiempo real (parte superior)
        metricas_frame = tk.Frame(contenido_frame, bg=self.colores.fondo_terciario, height=150)
        metricas_frame.pack(fill='x', padx=10, pady=(0, 10))
        metricas_frame.pack_propagate(False)
        
        tk.Label(metricas_frame,
                text="[STATS] MÉTRICAS DEL SISTEMA",
                font=('Consolas', 12, 'bold'),
                fg=self.colores.cyan_brillante,
                bg=self.colores.fondo_terciario).pack(pady=10)
        
        self.metricas_text = tk.Text(metricas_frame,
                                   height=6,
                                   font=('Consolas', 9),
                                   bg=self.colores.negro_carbono,
                                   fg=self.colores.verde_terminal,
                                   wrap='word',
                                   state='disabled')
        self.metricas_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Terminal integrado (parte inferior)
        terminal_frame = tk.Frame(contenido_frame, bg=self.colores.negro_carbono)
        terminal_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Crear terminal simplificado
        self._crear_terminal_monitor(terminal_frame)
        
    def _crear_terminal_monitor(self, parent):
        """Crear terminal simplificado para monitoreo"""
        tk.Label(parent,
                text=" TERMINAL DE MONITOREO",
                font=('Consolas', 12, 'bold'),
                fg=self.colores.cyan_brillante,
                bg=self.colores.negro_carbono).pack(pady=10)
        
        self.resultados_text = tk.Text(parent,
                                     height=20,
                                     font=('Consolas', 9),
                                     bg=self.colores.negro_carbono,
                                     fg=self.colores.verde_terminal,
                                     wrap='word',
                                     state='disabled')
        self.resultados_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar para el terminal
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.resultados_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.resultados_text.configure(yscrollcommand=scrollbar.set)
        
    def _iniciar_monitoreo_completo(self):
        """Iniciar monitoreo completo del sistema"""
        if not self.monitoreo_activo:
            self.monitoreo_activo = True
            self.actualizar_estado(" ACTIVO")
            
            # Iniciar métricas en tiempo real
            self.metricas_tiempo_real.iniciar()
            
            # Iniciar hilo de monitoreo principal
            self.hilo_monitoreo = threading.Thread(
                target=self._ejecutar_monitoreo_principal,
                daemon=True,
                name="MonitoreoSistema"
            )
            self.hilo_monitoreo.start()
            
            # Actualizar botones
            self.btn_iniciar.config(state='disabled')
            self.btn_detener.config(state='normal')
            
            self.logger.info("Monitor del sistema iniciado")
            self._agregar_resultado(" Monitor del sistema iniciado - Supervisión activa")
    
    def _detener_monitoreo_completo(self):
        """Detener monitoreo completo del sistema"""
        self.monitoreo_activo = False
        self.actualizar_estado(" DETENIDO")
        
        # Detener métricas
        self.metricas_tiempo_real.detener()
        
        # Actualizar botones
        self.btn_iniciar.config(state='normal')
        self.btn_detener.config(state='disabled')
        
        self.logger.info("Monitor del sistema detenido")
        self._agregar_resultado(" Monitor del sistema detenido")
        
    def _ejecutar_monitoreo_principal(self):
        """Hilo principal de monitoreo del sistema"""
        while self.monitoreo_activo:
            try:
                self._monitoreo_kali_optimizado()
                time.sleep(5)
            except Exception as e:
                self.logger.error(f"Error en monitoreo principal: {e}")
                time.sleep(3)
                
    def _monitoreo_kali_optimizado(self):
        """Monitoreo optimizado para Kali Linux"""
        try:
            # Procesos con mayor uso de CPU
            result_cpu = subprocess.run(['ps', 'aux', '--sort=-%cpu'], 
                                      capture_output=True, text=True, timeout=10)
            if result_cpu.returncode == 0:
                lines = result_cpu.stdout.split('\n')[:6]  # Top 5 procesos
                self._agregar_resultado(" TOP PROCESOS CPU:")
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 11:
                            pid, user, cpu, mem = parts[1], parts[0], parts[2], parts[3]
                            comando = ' '.join(parts[10:])[:30]
                            self._agregar_resultado(f"  PID {pid}: {comando} (CPU: {cpu}%, MEM: {mem}%)")
            
            # Conexiones de red activas
            result_net = subprocess.run(['ss', '-tuln'], 
                                      capture_output=True, text=True, timeout=10)
            if result_net.returncode == 0:
                lines = result_net.stdout.split('\n')
                tcp_count = len([l for l in lines if 'tcp' in l.lower()])
                udp_count = len([l for l in lines if 'udp' in l.lower()])
                self._agregar_resultado(f" CONEXIONES: TCP:{tcp_count} UDP:{udp_count}")
                
        except subprocess.TimeoutExpired:
            self._agregar_resultado(" Timeout en comando de monitoreo")
        except Exception as e:
            self._agregar_resultado(f"[ERROR] Error en monitoreo: {str(e)}")
            
    def _agregar_resultado(self, texto):
        """Agregar resultado al terminal de monitoreo"""
        if self.resultados_text:
            self.resultados_text.config(state='normal')
            timestamp = time.strftime("[%H:%M:%S]")
            self.resultados_text.insert('end', f"{timestamp} {texto}\n")
            self.resultados_text.see('end')
            self.resultados_text.config(state='disabled')
        
    def destruir_vista(self):
        """Limpiar recursos al destruir la vista"""
        try:
            self.monitoreo_activo = False
            self.metricas_tiempo_real.detener()
            if self.hilo_monitoreo and self.hilo_monitoreo.is_alive():
                self.hilo_monitoreo.join(timeout=1)
            self.limpiar_vista()
            self.logger.info("Vista Monitor destruida")
        except Exception as e:
            self.logger.error(f"Error destruyendo vista Monitor: {e}")
