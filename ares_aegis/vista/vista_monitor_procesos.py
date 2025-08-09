#!/usr/bin/env python3
"""
Vista Monitor de Procesos para Ares Aegis
Sistema especializado para monitoreo de procesos del sistema
"""

from ares_aegis.utils.utils_imports_comunes import (
    tk, ttk, messagebox, filedialog, logging, os, time, threading
)
import subprocess
import re
from ares_aegis.vista.componentes_ui.emoticonos_mitologicos import EmoticonosMitologicos
from ares_aegis.vista.componentes_ui.sistema_ayuda import SistemaAyuda
from ares_aegis.vista.componentes_ui.vista_base import VistaBase


class VistaMonitorProcesos(VistaBase):
    """Vista especializada para monitoreo de procesos del sistema"""
    
    def __init__(self, contenedor_padre, controlador, colores):
        super().__init__(contenedor_padre, controlador, colores)
        
        # Variables específicas del monitor de procesos
        self.monitoreo_procesos_activo = False
        self.hilo_monitoreo_procesos = None
        self.procesos_sospechosos = []
        self.sistema_ayuda = SistemaAyuda(colores)
        
    def _get_estado_inicial(self):
        return " DETENIDO"
        
    def _get_titulo_ventana(self):
        return "MONITOR DE PROCESOS - SUPERVISIÓN DE ACTIVIDAD"
        
    def _get_descripcion_funcionalidades(self):
        return """ FUNCIONALIDADES:
• Monitoreo en tiempo real de procesos
• Detección de procesos sospechosos
• Análisis de consumo de recursos por proceso
• Supervisión de procesos críticos del sistema

 HERRAMIENTAS:
• ps aux: Listado detallado de procesos
• top: Procesos por consumo de CPU
• htop: Monitor interactivo de procesos
• pgrep: Búsqueda de procesos por nombre
• kill: Terminación de procesos

[TARGET] MÉTRICAS:
• PID y PPID de procesos
• Uso de CPU por proceso
• Consumo de memoria por proceso
• Estado de procesos (running, sleeping, zombie)
• Tiempo de ejecución de procesos
"""
        
    def crear_vista(self):
        """Crear la interfaz específica para monitor de procesos"""
        # Crear frame principal
        self.frame_principal = ttk.Frame(self.contenedor_padre)
        self.frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título y estado
        self._crear_header()
        
        # Panel de control
        self._crear_panel_control_procesos()
        
        # Área de resultados
        self._crear_area_resultados_procesos()
        
        # Panel de estadísticas
        self._crear_panel_estadisticas_procesos()
        
    def _crear_header(self):
        """Crear cabecera con título y estado"""
        header_frame = ttk.Frame(self.frame_principal)
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Título
        titulo_label = ttk.Label(
            header_frame,
            text=" MONITOR DE PROCESOS - SUPERVISIÓN DE ACTIVIDAD",
            font=("Hack", 14, "bold")
        )
        titulo_label.pack(side=tk.LEFT)
        
        # Estado
        self.estado_label = ttk.Label(
            header_frame,
            text=self._get_estado_inicial(),
            font=("Hack", 12, "bold")
        )
        self.estado_label.pack(side=tk.RIGHT)
        
        # Crear área de resultados general
        self._crear_area_resultados_general()
        
    def _crear_area_resultados_general(self):
        """Crear área de resultados general para mensajes"""
        resultados_frame = ttk.LabelFrame(self.frame_principal, text=" Registro de Actividad", padding=5)
        resultados_frame.pack(fill="x", pady=(0, 10))
        
        self.resultados_text = tk.Text(
            resultados_frame,
            height=4,
            bg=self.colores.fondo_secundario if hasattr(self.colores, 'fondo_secundario') else 'black',
            fg=self.colores.texto_primario if hasattr(self.colores, 'texto_primario') else 'white',
            font=("Consolas", 9),
            wrap=tk.WORD,
            state='disabled'
        )
        
        scrollbar_resultados = ttk.Scrollbar(resultados_frame, orient="vertical", command=self.resultados_text.yview)
        self.resultados_text.configure(yscrollcommand=scrollbar_resultados.set)
        
        self.resultados_text.pack(side="left", fill="both", expand=True)
        scrollbar_resultados.pack(side="right", fill="y")
        
    def _crear_panel_control_procesos(self):
        """Crear panel de control específico para procesos"""
        control_frame = ttk.LabelFrame(self.frame_principal, text=" Control de Monitoreo de Procesos", padding=10)
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Botones de control
        botones_frame = ttk.Frame(control_frame)
        botones_frame.pack(fill="x")
        
        # Botón iniciar/detener monitoreo
        self.btn_toggle_procesos = ttk.Button(
            botones_frame,
            text=" INICIAR MONITOREO",
            command=self._toggle_monitoreo_procesos,
            width=20
        )
        self.btn_toggle_procesos.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón listar procesos
        ttk.Button(
            botones_frame,
            text=" LISTAR PROCESOS",
            command=self._listar_procesos,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Botón procesos sospechosos
        ttk.Button(
            botones_frame,
            text=" PROCESOS SOSPECHOSOS",
            command=self._detectar_procesos_sospechosos,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Botón limpiar
        ttk.Button(
            botones_frame,
            text="[CLEAN] LIMPIAR",
            command=self._limpiar_resultados,
            width=15
        ).pack(side=tk.RIGHT)
        
    def _crear_area_resultados_procesos(self):
        """Crear área de resultados específica para procesos"""
        resultados_frame = ttk.LabelFrame(self.frame_principal, text="[STATS] Resultados del Monitoreo de Procesos", padding=10)
        resultados_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Crear notebook para diferentes vistas
        self.notebook_procesos = ttk.Notebook(resultados_frame)
        self.notebook_procesos.pack(fill="both", expand=True)
        
        # Tab para procesos generales
        self._crear_tab_procesos_generales()
        
        # Tab para procesos sospechosos
        self._crear_tab_procesos_sospechosos()
        
        # Tab para estadísticas detalladas
        self._crear_tab_estadisticas_procesos()
        
    def _crear_tab_procesos_generales(self):
        """Crear tab para procesos generales"""
        frame_generales = ttk.Frame(self.notebook_procesos)
        self.notebook_procesos.add(frame_generales, text="[REFRESH] Procesos Activos")
        
        # Crear text widget con scroll
        text_frame = ttk.Frame(frame_generales)
        text_frame.pack(fill="both", expand=True)
        
        self.text_procesos_generales = tk.Text(
            text_frame,
            bg=self.colores.fondo_secundario,
            fg=self.colores.texto_primario,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_procesos_generales.yview)
        self.text_procesos_generales.configure(yscrollcommand=scrollbar.set)
        
        self.text_procesos_generales.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def _crear_tab_procesos_sospechosos(self):
        """Crear tab para procesos sospechosos"""
        frame_sospechosos = ttk.Frame(self.notebook_procesos)
        self.notebook_procesos.add(frame_sospechosos, text=" Procesos Sospechosos")
        
        # Crear treeview para procesos sospechosos
        columns = ("PID", "Proceso", "CPU%", "MEM%", "Comando", "Razón")
        self.tree_sospechosos = ttk.Treeview(frame_sospechosos, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        for col in columns:
            self.tree_sospechosos.heading(col, text=col)
            self.tree_sospechosos.column(col, width=100)
        
        # Scrollbars para el treeview
        scrollbar_v = ttk.Scrollbar(frame_sospechosos, orient="vertical", command=self.tree_sospechosos.yview)
        scrollbar_h = ttk.Scrollbar(frame_sospechosos, orient="horizontal", command=self.tree_sospechosos.xview)
        self.tree_sospechosos.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.tree_sospechosos.pack(side="left", fill="both", expand=True)
        scrollbar_v.pack(side="right", fill="y")
        scrollbar_h.pack(side="bottom", fill="x")
        
    def _crear_tab_estadisticas_procesos(self):
        """Crear tab para estadísticas de procesos"""
        frame_stats = ttk.Frame(self.notebook_procesos)
        self.notebook_procesos.add(frame_stats, text=" Estadísticas")
        
        self.text_stats_procesos = tk.Text(
            frame_stats,
            bg=self.colores.fondo_secundario,
            fg=self.colores.texto_primario,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.text_stats_procesos.pack(fill="both", expand=True)
        
    def _crear_panel_estadisticas_procesos(self):
        """Crear panel de estadísticas en tiempo real"""
        stats_frame = ttk.LabelFrame(self.frame_principal, text="[STATS] Estadísticas en Tiempo Real", padding=10)
        stats_frame.pack(fill="x")
        
        # Variables para estadísticas
        self.var_total_procesos = tk.StringVar(value="Total Procesos: 0")
        self.var_procesos_activos = tk.StringVar(value="Activos: 0")
        self.var_procesos_zombie = tk.StringVar(value="Zombie: 0")
        self.var_cpu_promedio = tk.StringVar(value="CPU Promedio: 0%")
        
        # Labels de estadísticas
        ttk.Label(stats_frame, textvariable=self.var_total_procesos).pack(side=tk.LEFT, padx=10)
        ttk.Label(stats_frame, textvariable=self.var_procesos_activos).pack(side=tk.LEFT, padx=10)
        ttk.Label(stats_frame, textvariable=self.var_procesos_zombie).pack(side=tk.LEFT, padx=10)
        ttk.Label(stats_frame, textvariable=self.var_cpu_promedio).pack(side=tk.LEFT, padx=10)
        
    def _toggle_monitoreo_procesos(self):
        """Alternar el monitoreo de procesos"""
        if not self.monitoreo_procesos_activo:
            self._iniciar_monitoreo_procesos()
        else:
            self._detener_monitoreo_procesos()
            
    def _iniciar_monitoreo_procesos(self):
        """Iniciar monitoreo de procesos"""
        try:
            self.monitoreo_procesos_activo = True
            self.btn_toggle_procesos.config(text=" DETENER MONITOREO")
            self.estado_label.config(text=" MONITOREO ACTIVO")
            
            # Iniciar hilo de monitoreo
            self.hilo_monitoreo_procesos = threading.Thread(target=self._ciclo_monitoreo_procesos, daemon=True)
            self.hilo_monitoreo_procesos.start()
            
            self._agregar_resultado(" Monitoreo de procesos iniciado...")
            
            # Notificar al controlador
            if hasattr(self.controlador, 'controlador_monitor_procesos'):
                try:
                    self.controlador.controlador_monitor_procesos.iniciar_monitoreo()
                except Exception as e:
                    self._agregar_resultado(f" Error en controlador: {e}")
                    
        except Exception as e:
            self._agregar_resultado(f"[ERROR] Error iniciando monitoreo: {e}")
            
    def _detener_monitoreo_procesos(self):
        """Detener monitoreo de procesos"""
        self.monitoreo_procesos_activo = False
        self.btn_toggle_procesos.config(text=" INICIAR MONITOREO")
        self.estado_label.config(text=" DETENIDO")
        self._agregar_resultado(" Monitoreo de procesos detenido.")
        
    def _ciclo_monitoreo_procesos(self):
        """Ciclo principal del monitoreo de procesos"""
        while self.monitoreo_procesos_activo:
            try:
                self._actualizar_procesos()
                time.sleep(5)  # Actualizar cada 5 segundos
            except Exception as e:
                self._agregar_resultado(f"[ERROR] Error en ciclo de monitoreo: {e}")
                break
                
    def _actualizar_procesos(self):
        """Actualizar lista de procesos"""
        try:
            # Ejecutar ps aux para obtener procesos
            resultado = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
            
            if resultado.returncode == 0:
                procesos = resultado.stdout.split('\n')[1:]  # Saltar header
                procesos_activos = []
                cpu_total = 0
                procesos_zombie = 0
                
                for proceso in procesos:
                    if proceso.strip():
                        campos = proceso.split(None, 10)
                        if len(campos) >= 11:
                            try:
                                cpu_uso = float(campos[2])
                                cpu_total += cpu_uso
                                
                                estado = campos[7]
                                if 'Z' in estado:
                                    procesos_zombie += 1
                                    
                                procesos_activos.append({
                                    'pid': campos[1],
                                    'usuario': campos[0],
                                    'cpu': campos[2],
                                    'memoria': campos[3],
                                    'comando': campos[10] if len(campos) > 10 else 'N/A'
                                })
                            except (ValueError, IndexError):
                                continue
                
                # Actualizar estadísticas
                self._actualizar_estadisticas_procesos(len(procesos_activos), len(procesos_activos), procesos_zombie, cpu_total/len(procesos_activos) if procesos_activos else 0)
                
                # Detectar procesos sospechosos automáticamente
                self._analizar_procesos_sospechosos(procesos_activos)
                
        except subprocess.TimeoutExpired:
            self._agregar_resultado("⏰ Timeout ejecutando ps aux")
        except Exception as e:
            self._agregar_resultado(f"[ERROR] Error actualizando procesos: {e}")
            
    def _actualizar_estadisticas_procesos(self, total, activos, zombie, cpu_promedio):
        """Actualizar estadísticas mostradas"""
        self.var_total_procesos.set(f"Total Procesos: {total}")
        self.var_procesos_activos.set(f"Activos: {activos}")
        self.var_procesos_zombie.set(f"Zombie: {zombie}")
        self.var_cpu_promedio.set(f"CPU Promedio: {cpu_promedio:.1f}%")
        
    def _listar_procesos(self):
        """Listar todos los procesos del sistema"""
        try:
            self._agregar_resultado(" Listando procesos del sistema...")
            
            resultado = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
            
            if resultado.returncode == 0:
                self.text_procesos_generales.delete('1.0', tk.END)
                self.text_procesos_generales.insert('1.0', resultado.stdout)
                self._agregar_resultado("[OK] Lista de procesos actualizada")
            else:
                self._agregar_resultado(f"[ERROR] Error ejecutando ps aux: {resultado.stderr}")
                
        except subprocess.TimeoutExpired:
            self._agregar_resultado("⏰ Timeout ejecutando ps aux")
        except Exception as e:
            self._agregar_resultado(f"[ERROR] Error listando procesos: {e}")
            
    def _detectar_procesos_sospechosos(self):
        """Detectar procesos potencialmente sospechosos"""
        try:
            self._agregar_resultado(" Analizando procesos sospechosos...")
            
            # Limpiar tree de sospechosos
            for item in self.tree_sospechosos.get_children():
                self.tree_sospechosos.delete(item)
            
            resultado = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
            
            if resultado.returncode == 0:
                procesos = resultado.stdout.split('\n')[1:]
                sospechosos_encontrados = 0
                
                for proceso in procesos:
                    if proceso.strip():
                        campos = proceso.split(None, 10)
                        if len(campos) >= 11:
                            try:
                                pid = campos[1]
                                cpu = float(campos[2])
                                memoria = float(campos[3])
                                comando = campos[10] if len(campos) > 10 else 'N/A'
                                
                                # Criterios de sospecha
                                razones = []
                                
                                if cpu > 90:
                                    razones.append("CPU muy alto")
                                if memoria > 80:
                                    razones.append("Memoria muy alta")
                                if any(term in comando.lower() for term in ['nc', 'netcat', 'ncat', 'socat']):
                                    razones.append("Herramienta de red sospechosa")
                                if comando.startswith('/tmp/') or comando.startswith('/var/tmp/'):
                                    razones.append("Ejecutándose desde tmp")
                                
                                if razones:
                                    self.tree_sospechosos.insert('', 'end', values=(
                                        pid, campos[0], f"{cpu}%", f"{memoria}%", comando[:50], ", ".join(razones)
                                    ))
                                    sospechosos_encontrados += 1
                                    
                            except (ValueError, IndexError):
                                continue
                
                self._agregar_resultado(f" Análisis completado: {sospechosos_encontrados} procesos sospechosos encontrados")
                
        except Exception as e:
            self._agregar_resultado(f"[ERROR] Error detectando procesos sospechosos: {e}")
            
    def _analizar_procesos_sospechosos(self, procesos):
        """Analizar procesos para detectar actividad sospechosa"""
        # Esta función se llama automáticamente durante el monitoreo
        pass
        
    def _agregar_resultado(self, mensaje):
        """Agregar resultado al área de texto principal"""
        timestamp = time.strftime("%H:%M:%S")
        mensaje_con_timestamp = f"[{timestamp}] {mensaje}\n"
        
        if hasattr(self, 'resultados_text') and self.resultados_text:
            self.resultados_text.config(state='normal')
            self.resultados_text.insert(tk.END, mensaje_con_timestamp)
            self.resultados_text.see(tk.END)
            self.resultados_text.config(state='disabled')
        
    def _limpiar_resultados(self):
        """Limpiar todas las áreas de resultados"""
        if hasattr(self, 'resultados_text') and self.resultados_text:
            self.resultados_text.config(state='normal')
            self.resultados_text.delete('1.0', tk.END)
            self.resultados_text.config(state='disabled')
            
        if hasattr(self, 'text_procesos_generales'):
            self.text_procesos_generales.delete('1.0', tk.END)
        if hasattr(self, 'text_stats_procesos'):
            self.text_stats_procesos.delete('1.0', tk.END)
        
        # Limpiar tree de sospechosos
        if hasattr(self, 'tree_sospechosos'):
            for item in self.tree_sospechosos.get_children():
                self.tree_sospechosos.delete(item)
                
    def cerrar(self):
        """Cerrar la vista y limpiar recursos"""
        self.monitoreo_procesos_activo = False
        if self.hilo_monitoreo_procesos and self.hilo_monitoreo_procesos.is_alive():
            self.hilo_monitoreo_procesos.join(timeout=2)
