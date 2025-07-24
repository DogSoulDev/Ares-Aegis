#!/usr/bin/env python3
"""
Vista Monitor para Ares Aegis
Interfaz del módulo de monitoreo del sistema optimizado para Kali Linux
"""

import tkinter as tk
import threading
import logging
import subprocess
import time
import os
from ..componentes_ui.emoticonos_mitologicos import EmoticonosMitologicos
from ..componentes_ui.sistema_ayuda import SistemaAyuda


class VistaMonitor:
    """Vista del monitor del sistema optimizada para Kali Linux"""
    
    def __init__(self, contenedor_padre, controlador, colores):
        self.contenedor_padre = contenedor_padre
        self.controlador = controlador
        self.colores = colores
        self.logger = logging.getLogger(__name__)
        
        # Variables de control
        self.monitoreo_activo = False
        self.hilo_monitoreo = None
        self.resultados_text = None
        self.estado_var = None
        
        # Sistema de ayuda
        self.sistema_ayuda = SistemaAyuda(colores)
        
    def mostrar_informacion(self):
        """Mostrar información de ayuda sobre el Monitor del Sistema"""
        from tkinter import messagebox
        
        info_text = """🛡️ MONITOR DEL SISTEMA - INFORMACIÓN

🔱 FUNCIONALIDADES PRINCIPALES:
• Monitoreo en tiempo real del sistema
• Análisis de procesos y servicios
• Supervisión de recursos (CPU, RAM, Red)
• Detección de actividad sospechosa

⚡ HERRAMIENTAS INCLUIDAS:
• ps aux: Listado completo de procesos
• netstat: Conexiones de red activas  
• lsof: Archivos abiertos por procesos
• htop: Monitor interactivo de recursos
• ss: Estado de conexiones de red

🎯 MONITOREO AVANZADO:
• Uso de CPU por proceso
• Consumo de memoria RAM
• Conexiones de red activas
• Archivos y puertos abiertos
• Procesos que consumen más recursos

🔧 COMANDOS DISPONIBLES:
• Análisis de procesos sospechosos
• Revisión de conexiones de red
• Monitoreo de archivos del sistema
• Detección de procesos ocultos
• Análisis de carga del sistema

⚠️ OPTIMIZADO PARA KALI LINUX:
• Integración con herramientas nativas
• Comandos específicos de pentesting
• Detección de rootkits y malware
• Análisis forense del sistema

📊 INTERPRETACIÓN DE DATOS:
• 🟢 NORMAL: Actividad estándar del sistema
• 🟡 ADVERTENCIA: Uso elevado de recursos
• 🔴 CRÍTICO: Actividad sospechosa detectada
• ⚫ ERROR: No se pudo obtener información

💡 CONSEJOS DE USO:
• Ejecuta monitoreo periódicamente
• Revisa procesos con alta CPU/RAM
• Verifica conexiones de red inusuales
• Analiza archivos abiertos por procesos"""
        
        messagebox.showinfo("Información - Monitor del Sistema", info_text)
        
    def crear_vista(self, area_contenido=None):
        """Crear la vista del monitor con diseño responsive"""
        self._limpiar_contenedor()
        
        # Frame principal con grid responsive
        self.frame_principal = tk.Frame(self.contenedor_padre, bg=self.colores.fondo_secundario)
        self.frame_principal.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Configurar grid responsive con mejores proporciones
        self.frame_principal.grid_rowconfigure(0, weight=0)  # Header fijo
        self.frame_principal.grid_rowconfigure(1, weight=0)  # Controles fijos
        self.frame_principal.grid_rowconfigure(2, weight=1)  # Resultados expandibles
        self.frame_principal.grid_columnconfigure(0, weight=1)
        
        # Header
        self._crear_header_monitor(self.frame_principal)
        
        # Panel de control
        self._crear_panel_control(self.frame_principal)
        
        # Área de resultados
        self._crear_area_resultados(self.frame_principal)
        
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
            self.resultados_text.config(state='normal')
            self.resultados_text.insert(tk.END, f"{texto}\\n")
            self.resultados_text.see(tk.END)
            self.resultados_text.config(state='disabled')
        except:
            pass  # Widget ya destruido
    
    def _ejecutar_monitoreo_hilo(self):
        """Ejecutar monitoreo REAL en hilo separado usando herramientas nativas de Kali Linux"""
        try:
            import time
            
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
            import time
            import subprocess
            import os
            
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
                            self._agregar_resultado(f"🚨 {EmoticonosMitologicos.HYDRA} CPU crítico: {cpu_usage:.1f}%")
                        elif cpu_usage > 50:
                            self._agregar_resultado(f"⚠️ {EmoticonosMitologicos.ADVERTENCIA} CPU alto: {cpu_usage:.1f}%")
                        else:
                            self._agregar_resultado(f"✅ {EmoticonosMitologicos.ESCUDO} CPU normal: {cpu_usage:.1f}%")
                    except Exception:
                        # Fallback usando top (solo en Linux)
                        try:
                            import platform
                            if platform.system() == 'Linux':
                                result = subprocess.run(['top', '-bn1'], capture_output=True, text=True, timeout=5)
                                for line in result.stdout.split('\\n'):
                                    if 'Cpu(s):' in line:
                                        cpu_info = line.strip()
                                        self._agregar_resultado(f"📊 {EmoticonosMitologicos.CRISTAL} {cpu_info}")
                                        break
                        except Exception:
                            pass
                    
                    # === MONITOREAR MEMORIA ===
                    try:
                        with open('/proc/meminfo', 'r') as f:
                            meminfo = f.readlines()
                        
                        mem_total = mem_free = mem_available = 0
                        for line in meminfo:
                            if line.startswith('MemTotal:'):
                                mem_total = int(line.split()[1])
                            elif line.startswith('MemFree:'):
                                mem_free = int(line.split()[1])
                            elif line.startswith('MemAvailable:'):
                                mem_available = int(line.split()[1])
                        
                        if mem_total > 0:
                            mem_used_percent = ((mem_total - mem_available) / mem_total) * 100
                            if mem_used_percent > 85:
                                self._agregar_resultado(f"🚨 {EmoticonosMitologicos.HYDRA} Memoria crítica: {mem_used_percent:.1f}%")
                            elif mem_used_percent > 70:
                                self._agregar_resultado(f"⚠️ {EmoticonosMitologicos.ADVERTENCIA} Memoria alta: {mem_used_percent:.1f}%")
                            else:
                                self._agregar_resultado(f"🧠 {EmoticonosMitologicos.ATHENA} Memoria: {mem_used_percent:.1f}%")
                    except Exception:
                        pass
                    
                    # === MONITOREAR PROCESOS SOSPECHOSOS ===
                    try:
                        result = subprocess.run(['ps', 'aux', '--sort=-pcpu'], capture_output=True, text=True, timeout=10)
                        lines = result.stdout.split('\\n')[1:6]  # Top 5 procesos por CPU
                        
                        for line in lines:
                            if line.strip():
                                parts = line.split()
                                if len(parts) >= 11:
                                    user = parts[0]
                                    pid = parts[1]
                                    cpu = parts[2]
                                    mem = parts[3]
                                    command = ' '.join(parts[10:])[:25]
                                    
                                    try:
                                        cpu_val = float(cpu)
                                        if cpu_val > 50:
                                            self._agregar_resultado(f"🔥 {EmoticonosMitologicos.ARES} Alto CPU: {command} (PID:{pid}, CPU:{cpu}%)")
                                        elif cpu_val > 20:
                                            self._agregar_resultado(f"🔍 {EmoticonosMitologicos.ARGOS} {user}: {command} (CPU:{cpu}%, MEM:{mem}%)")
                                    except ValueError:
                                        pass
                    except Exception:
                        pass
                    
                    # === MONITOREAR RED ===
                    try:
                        # Usar el monitor de red mejorado
                        if hasattr(self.controlador, 'monitor_red') and self.controlador.monitor_red:
                            estadisticas_red = self.controlador.monitor_red.obtener_estadisticas()
                            if estadisticas_red:
                                conexiones = estadisticas_red.get('conexiones_activas', 0)
                                if conexiones > 50:
                                    self._agregar_resultado(f"🌐 {EmoticonosMitologicos.HERMES} Muchas conexiones: {conexiones}")
                                else:
                                    self._agregar_resultado(f"🌐 {EmoticonosMitologicos.HERMES} Conexiones activas: {conexiones}")
                                
                                # Verificar conexiones sospechosas
                                sospechosas = estadisticas_red.get('conexiones_sospechosas', 0)
                                if sospechosas > 0:
                                    self._agregar_resultado(f"🚨 {EmoticonosMitologicos.HYDRA} Conexiones sospechosas: {sospechosas}")
                        else:
                            # Fallback: usar netstat
                            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, timeout=5)
                            established_count = result.stdout.count('ESTABLISHED')
                            self._agregar_resultado(f"🌐 {EmoticonosMitologicos.HERMES} Conexiones establecidas: {established_count}")
                    except Exception:
                        pass
                    
                    # === VERIFICAR PROCESOS MALICIOSOS ===
                    self._verificar_procesos_maliciosos()
                    
                    # === VERIFICAR PUERTOS SOSPECHOSOS ===
                    try:
                        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True, timeout=5)
                        puertos_sospechosos = [1234, 4444, 5555, 6666, 31337, 12345]
                        
                        for puerto in puertos_sospechosos:
                            if f":{puerto} " in result.stdout:
                                self._agregar_resultado(f"🚨 {EmoticonosMitologicos.HYDRA} Puerto sospechoso abierto: {puerto}")
                    except Exception:
                        pass
                    
                    # === VERIFICAR INTEGRIDAD DEL SISTEMA ===
                    self._verificar_integridad_sistema()
                    
                    # Pausa antes del siguiente ciclo
                    time.sleep(8)
                    
                except Exception as e:
                    self.logger.warning(f"Error en ciclo de monitoreo: {e}")
                    time.sleep(3)
                    
        except Exception as e:
            self.logger.error(f"Error en monitoreo Kali Linux: {e}")
            self._monitoreo_fallback()
    
    def _monitoreo_fallback(self):
        """Monitoreo fallback básico usando solo herramientas nativas de Kali Linux"""
        import time
        import subprocess
        import os
        
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
        import os
        
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
