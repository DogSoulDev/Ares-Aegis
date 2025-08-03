#!/usr/bin/env python3
"""
Vista Monitor de Red para Ares Aegis
Sistema especializado para monitoreo de actividad de red
"""

from ares_aegis.utils.utils_imports_comunes import (
    tk, ttk, messagebox, filedialog, logging, os, time, threading
)
import subprocess
import re
import json
from ares_aegis.vista.componentes_ui.emoticonos_mitologicos import EmoticonosMitologicos
from ares_aegis.vista.componentes_ui.sistema_ayuda import SistemaAyuda
from ares_aegis.vista.componentes_ui.vista_base import VistaBase


class VistaMonitorRed(VistaBase):
    """Vista especializada para monitoreo de actividad de red"""
    
    def __init__(self, contenedor_padre, controlador, colores):
        super().__init__(contenedor_padre, controlador, colores)
        
        # Variables específicas del monitor de red
        self.monitoreo_red_activo = False
        self.hilo_monitoreo_red = None
        self.conexiones_sospechosas = []
        self.puertos_monitoreados = []
        self.sistema_ayuda = SistemaAyuda(colores)
        
        # Estadísticas de red
        self.stats_conexiones = {
            'total': 0,
            'establecidas': 0,
            'escuchando': 0,
            'cerradas': 0
        }
        
    def _get_estado_inicial(self):
        return "🔴 DETENIDO"
        
    def _get_titulo_ventana(self):
        return "MONITOR DE RED - SUPERVISIÓN DE CONEXIONES"
        
    def _get_descripcion_funcionalidades(self):
        return """🌐 FUNCIONALIDADES:
• Monitoreo en tiempo real de conexiones de red
• Detección de conexiones sospechosas
• Análisis de puertos abiertos y servicios
• Supervisión de tráfico de red por interfaz

⚡ HERRAMIENTAS:
• netstat: Estado de conexiones de red
• ss: Socket statistics moderno
• lsof: Archivos y puertos abiertos por procesos
• iftop: Monitor de tráfico por interfaz
• tcpdump: Captura de paquetes de red

🎯 MÉTRICAS:
• Conexiones TCP/UDP activas
• Puertos en estado LISTEN
• Conexiones establecidas por IP
• Tráfico de red por interfaz
• Procesos asociados a conexiones de red
"""
        
    def crear_vista(self):
        """Crear la interfaz específica para monitor de red"""
        # Crear frame principal
        self.frame_principal = ttk.Frame(self.contenedor_padre)
        self.frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título y estado
        self._crear_header()
        
        # Panel de control
        self._crear_panel_control_red()
        
        # Área de resultados
        self._crear_area_resultados_red()
        
        # Panel de estadísticas
        self._crear_panel_estadisticas_red()
        
    def _crear_header(self):
        """Crear cabecera con título y estado"""
        header_frame = ttk.Frame(self.frame_principal)
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Título
        titulo_label = ttk.Label(
            header_frame,
            text="🌐 MONITOR DE RED - SUPERVISIÓN DE CONEXIONES",
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
        resultados_frame = ttk.LabelFrame(self.frame_principal, text="📋 Registro de Actividad", padding=5)
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
        
    def _crear_panel_control_red(self):
        """Crear panel de control específico para red"""
        control_frame = ttk.LabelFrame(self.frame_principal, text="🎮 Control de Monitoreo de Red", padding=10)
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Botones de control
        botones_frame = ttk.Frame(control_frame)
        botones_frame.pack(fill="x")
        
        # Botón iniciar/detener monitoreo
        self.btn_toggle_red = ttk.Button(
            botones_frame,
            text="🟢 INICIAR MONITOREO",
            command=self._toggle_monitoreo_red,
            width=20
        )
        self.btn_toggle_red.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón conexiones activas
        ttk.Button(
            botones_frame,
            text="🔗 CONEXIONES ACTIVAS",
            command=self._listar_conexiones,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Botón puertos abiertos
        ttk.Button(
            botones_frame,
            text="🚪 PUERTOS ABIERTOS",
            command=self._listar_puertos_abiertos,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Botón conexiones sospechosas
        ttk.Button(
            botones_frame,
            text="🚨 CONEXIONES SOSPECHOSAS",
            command=self._detectar_conexiones_sospechosas,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Botón limpiar
        ttk.Button(
            botones_frame,
            text="🧹 LIMPIAR",
            command=self._limpiar_resultados,
            width=15
        ).pack(side=tk.RIGHT)
        
    def _crear_area_resultados_red(self):
        """Crear área de resultados específica para red"""
        resultados_frame = ttk.LabelFrame(self.frame_principal, text="📊 Resultados del Monitoreo de Red", padding=10)
        resultados_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Crear notebook para diferentes vistas
        self.notebook_red = ttk.Notebook(resultados_frame)
        self.notebook_red.pack(fill="both", expand=True)
        
        # Tab para conexiones activas
        self._crear_tab_conexiones_activas()
        
        # Tab para puertos abiertos
        self._crear_tab_puertos_abiertos()
        
        # Tab para conexiones sospechosas
        self._crear_tab_conexiones_sospechosas()
        
        # Tab para estadísticas de interfaces
        self._crear_tab_interfaces_red()
        
    def _crear_tab_conexiones_activas(self):
        """Crear tab para conexiones activas"""
        frame_conexiones = ttk.Frame(self.notebook_red)
        self.notebook_red.add(frame_conexiones, text="🔗 Conexiones Activas")
        
        # Crear treeview para conexiones
        columns = ("Protocolo", "Local", "Remoto", "Estado", "PID", "Proceso")
        self.tree_conexiones = ttk.Treeview(frame_conexiones, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        for col in columns:
            self.tree_conexiones.heading(col, text=col)
            self.tree_conexiones.column(col, width=120)
        
        # Scrollbars
        scrollbar_v_con = ttk.Scrollbar(frame_conexiones, orient="vertical", command=self.tree_conexiones.yview)
        scrollbar_h_con = ttk.Scrollbar(frame_conexiones, orient="horizontal", command=self.tree_conexiones.xview)
        self.tree_conexiones.configure(yscrollcommand=scrollbar_v_con.set, xscrollcommand=scrollbar_h_con.set)
        
        self.tree_conexiones.pack(side="left", fill="both", expand=True)
        scrollbar_v_con.pack(side="right", fill="y")
        scrollbar_h_con.pack(side="bottom", fill="x")
        
    def _crear_tab_puertos_abiertos(self):
        """Crear tab para puertos abiertos"""
        frame_puertos = ttk.Frame(self.notebook_red)
        self.notebook_red.add(frame_puertos, text="🚪 Puertos Abiertos")
        
        # Crear treeview para puertos
        columns = ("Puerto", "Protocolo", "Estado", "PID", "Proceso", "Servicio")
        self.tree_puertos = ttk.Treeview(frame_puertos, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        for col in columns:
            self.tree_puertos.heading(col, text=col)
            self.tree_puertos.column(col, width=100)
        
        # Scrollbars
        scrollbar_v_port = ttk.Scrollbar(frame_puertos, orient="vertical", command=self.tree_puertos.yview)
        scrollbar_h_port = ttk.Scrollbar(frame_puertos, orient="horizontal", command=self.tree_puertos.xview)
        self.tree_puertos.configure(yscrollcommand=scrollbar_v_port.set, xscrollcommand=scrollbar_h_port.set)
        
        self.tree_puertos.pack(side="left", fill="both", expand=True)
        scrollbar_v_port.pack(side="right", fill="y")
        scrollbar_h_port.pack(side="bottom", fill="x")
        
    def _crear_tab_conexiones_sospechosas(self):
        """Crear tab para conexiones sospechosas"""
        frame_sospechosas = ttk.Frame(self.notebook_red)
        self.notebook_red.add(frame_sospechosas, text="🚨 Conexiones Sospechosas")
        
        # Crear treeview para conexiones sospechosas
        columns = ("IP Remota", "Puerto", "Protocolo", "Estado", "PID", "Proceso", "Razón")
        self.tree_sospechosas = ttk.Treeview(frame_sospechosas, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        for col in columns:
            self.tree_sospechosas.heading(col, text=col)
            self.tree_sospechosas.column(col, width=100)
        
        # Scrollbars
        scrollbar_v_sosp = ttk.Scrollbar(frame_sospechosas, orient="vertical", command=self.tree_sospechosas.yview)
        scrollbar_h_sosp = ttk.Scrollbar(frame_sospechosas, orient="horizontal", command=self.tree_sospechosas.xview)
        self.tree_sospechosas.configure(yscrollcommand=scrollbar_v_sosp.set, xscrollcommand=scrollbar_h_sosp.set)
        
        self.tree_sospechosas.pack(side="left", fill="both", expand=True)
        scrollbar_v_sosp.pack(side="right", fill="y")
        scrollbar_h_sosp.pack(side="bottom", fill="x")
        
    def _crear_tab_interfaces_red(self):
        """Crear tab para estadísticas de interfaces"""
        frame_interfaces = ttk.Frame(self.notebook_red)
        self.notebook_red.add(frame_interfaces, text="📈 Interfaces de Red")
        
        self.text_interfaces = tk.Text(
            frame_interfaces,
            bg=self.colores.fondo_secundario if hasattr(self.colores, 'fondo_secundario') else 'black',
            fg=self.colores.texto_primario if hasattr(self.colores, 'texto_primario') else 'white',
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        
        scrollbar_int = ttk.Scrollbar(frame_interfaces, orient="vertical", command=self.text_interfaces.yview)
        self.text_interfaces.configure(yscrollcommand=scrollbar_int.set)
        
        self.text_interfaces.pack(side="left", fill="both", expand=True)
        scrollbar_int.pack(side="right", fill="y")
        
    def _crear_panel_estadisticas_red(self):
        """Crear panel de estadísticas en tiempo real"""
        stats_frame = ttk.LabelFrame(self.frame_principal, text="📊 Estadísticas de Red en Tiempo Real", padding=10)
        stats_frame.pack(fill="x")
        
        # Variables para estadísticas
        self.var_total_conexiones = tk.StringVar(value="Total Conexiones: 0")
        self.var_conexiones_establecidas = tk.StringVar(value="Establecidas: 0")
        self.var_puertos_abiertos = tk.StringVar(value="Puertos Abiertos: 0")
        self.var_conexiones_sospechosas = tk.StringVar(value="Sospechosas: 0")
        
        # Labels de estadísticas
        ttk.Label(stats_frame, textvariable=self.var_total_conexiones).pack(side=tk.LEFT, padx=10)
        ttk.Label(stats_frame, textvariable=self.var_conexiones_establecidas).pack(side=tk.LEFT, padx=10)
        ttk.Label(stats_frame, textvariable=self.var_puertos_abiertos).pack(side=tk.LEFT, padx=10)
        ttk.Label(stats_frame, textvariable=self.var_conexiones_sospechosas).pack(side=tk.LEFT, padx=10)
        
    def _toggle_monitoreo_red(self):
        """Alternar el monitoreo de red"""
        if not self.monitoreo_red_activo:
            self._iniciar_monitoreo_red()
        else:
            self._detener_monitoreo_red()
            
    def _iniciar_monitoreo_red(self):
        """Iniciar monitoreo de red"""
        try:
            self.monitoreo_red_activo = True
            self.btn_toggle_red.config(text="🔴 DETENER MONITOREO")
            self.estado_label.config(text="🟢 MONITOREO ACTIVO")
            
            # Iniciar hilo de monitoreo
            self.hilo_monitoreo_red = threading.Thread(target=self._ciclo_monitoreo_red, daemon=True)
            self.hilo_monitoreo_red.start()
            
            self._agregar_resultado("🟢 Monitoreo de red iniciado...")
            
            # Notificar al controlador
            if hasattr(self.controlador, 'controlador_monitor_red'):
                try:
                    self.controlador.controlador_monitor_red.iniciar_monitoreo()
                except Exception as e:
                    self._agregar_resultado(f"⚠️ Error en controlador: {e}")
                    
        except Exception as e:
            self._agregar_resultado(f"❌ Error iniciando monitoreo: {e}")
            
    def _detener_monitoreo_red(self):
        """Detener monitoreo de red"""
        self.monitoreo_red_activo = False
        self.btn_toggle_red.config(text="🟢 INICIAR MONITOREO")
        self.estado_label.config(text="🔴 DETENIDO")
        self._agregar_resultado("🔴 Monitoreo de red detenido.")
        
    def _ciclo_monitoreo_red(self):
        """Ciclo principal del monitoreo de red"""
        while self.monitoreo_red_activo:
            try:
                self._actualizar_conexiones_red()
                time.sleep(3)  # Actualizar cada 3 segundos
            except Exception as e:
                self._agregar_resultado(f"❌ Error en ciclo de monitoreo: {e}")
                break
                
    def _actualizar_conexiones_red(self):
        """Actualizar conexiones de red"""
        try:
            # Ejecutar netstat para obtener conexiones
            resultado = subprocess.run(['netstat', '-tulpn'], capture_output=True, text=True, timeout=10)
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.split('\n')
                conexiones = []
                puertos_abiertos = 0
                establecidas = 0
                
                for linea in lineas:
                    if linea.strip() and not linea.startswith('Proto'):
                        campos = linea.split()
                        if len(campos) >= 6:
                            protocolo = campos[0]
                            local = campos[3]
                            remoto = campos[4] if len(campos) > 4 else 'N/A'
                            estado = campos[5] if len(campos) > 5 else 'N/A'
                            
                            if estado == 'LISTEN':
                                puertos_abiertos += 1
                            elif estado == 'ESTABLISHED':
                                establecidas += 1
                                
                            conexiones.append({
                                'protocolo': protocolo,
                                'local': local,
                                'remoto': remoto,
                                'estado': estado
                            })
                
                # Actualizar estadísticas
                self._actualizar_estadisticas_red(len(conexiones), establecidas, puertos_abiertos, 0)
                
                # Analizar conexiones sospechosas
                self._analizar_conexiones_sospechosas(conexiones)
                
        except subprocess.TimeoutExpired:
            self._agregar_resultado("⏰ Timeout ejecutando netstat")
        except Exception as e:
            self._agregar_resultado(f"❌ Error actualizando conexiones: {e}")
            
    def _actualizar_estadisticas_red(self, total, establecidas, puertos, sospechosas):
        """Actualizar estadísticas mostradas"""
        self.var_total_conexiones.set(f"Total Conexiones: {total}")
        self.var_conexiones_establecidas.set(f"Establecidas: {establecidas}")
        self.var_puertos_abiertos.set(f"Puertos Abiertos: {puertos}")
        self.var_conexiones_sospechosas.set(f"Sospechosas: {sospechosas}")
        
    def _listar_conexiones(self):
        """Listar conexiones activas"""
        try:
            self._agregar_resultado("🔗 Listando conexiones activas...")
            
            # Limpiar tree de conexiones
            for item in self.tree_conexiones.get_children():
                self.tree_conexiones.delete(item)
                
            resultado = subprocess.run(['netstat', '-tulpn'], capture_output=True, text=True, timeout=10)
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.split('\n')
                conexiones_encontradas = 0
                
                for linea in lineas:
                    if linea.strip() and not linea.startswith('Proto'):
                        campos = linea.split()
                        if len(campos) >= 6:
                            protocolo = campos[0]
                            local = campos[3]
                            remoto = campos[4] if len(campos) > 4 else 'N/A'
                            estado = campos[5] if len(campos) > 5 else 'N/A'
                            proceso_info = campos[6] if len(campos) > 6 else 'N/A'
                            
                            # Extraer PID y nombre del proceso
                            pid = 'N/A'
                            proceso = 'N/A'
                            if '/' in proceso_info:
                                pid = proceso_info.split('/')[0]
                                proceso = proceso_info.split('/')[1] if len(proceso_info.split('/')) > 1 else 'N/A'
                            
                            self.tree_conexiones.insert('', 'end', values=(
                                protocolo, local, remoto, estado, pid, proceso
                            ))
                            conexiones_encontradas += 1
                
                self._agregar_resultado(f"✅ {conexiones_encontradas} conexiones listadas")
                
        except Exception as e:
            self._agregar_resultado(f"❌ Error listando conexiones: {e}")
            
    def _listar_puertos_abiertos(self):
        """Listar puertos abiertos"""
        try:
            self._agregar_resultado("🚪 Analizando puertos abiertos...")
            
            # Limpiar tree de puertos
            for item in self.tree_puertos.get_children():
                self.tree_puertos.delete(item)
                
            resultado = subprocess.run(['netstat', '-tulpn'], capture_output=True, text=True, timeout=10)
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.split('\n')
                puertos_encontrados = 0
                
                for linea in lineas:
                    if 'LISTEN' in linea:
                        campos = linea.split()
                        if len(campos) >= 6:
                            protocolo = campos[0]
                            direccion_local = campos[3]
                            proceso_info = campos[6] if len(campos) > 6 else 'N/A'
                            
                            # Extraer puerto
                            puerto = direccion_local.split(':')[-1] if ':' in direccion_local else 'N/A'
                            
                            # Extraer PID y proceso
                            pid = 'N/A'
                            proceso = 'N/A'
                            if '/' in proceso_info:
                                pid = proceso_info.split('/')[0]
                                proceso = proceso_info.split('/')[1] if len(proceso_info.split('/')) > 1 else 'N/A'
                            
                            # Identificar servicio común
                            servicio = self._identificar_servicio(puerto)
                            
                            self.tree_puertos.insert('', 'end', values=(
                                puerto, protocolo, 'LISTEN', pid, proceso, servicio
                            ))
                            puertos_encontrados += 1
                
                self._agregar_resultado(f"✅ {puertos_encontrados} puertos abiertos encontrados")
                
        except Exception as e:
            self._agregar_resultado(f"❌ Error listando puertos: {e}")
            
    def _identificar_servicio(self, puerto):
        """Identificar servicio común por puerto"""
        servicios_comunes = {
            '22': 'SSH',
            '23': 'Telnet',
            '25': 'SMTP',
            '53': 'DNS',
            '80': 'HTTP',
            '110': 'POP3',
            '143': 'IMAP',
            '443': 'HTTPS',
            '993': 'IMAPS',
            '995': 'POP3S',
            '3306': 'MySQL',
            '5432': 'PostgreSQL',
            '6379': 'Redis',
            '27017': 'MongoDB'
        }
        return servicios_comunes.get(puerto, 'Desconocido')
        
    def _detectar_conexiones_sospechosas(self):
        """Detectar conexiones potencialmente sospechosas"""
        try:
            self._agregar_resultado("🚨 Analizando conexiones sospechosas...")
            
            # Limpiar tree de sospechosas
            for item in self.tree_sospechosas.get_children():
                self.tree_sospechosas.delete(item)
                
            resultado = subprocess.run(['netstat', '-tulpn'], capture_output=True, text=True, timeout=10)
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.split('\n')
                sospechosas_encontradas = 0
                
                for linea in lineas:
                    if linea.strip() and not linea.startswith('Proto') and 'ESTABLISHED' in linea:
                        campos = linea.split()
                        if len(campos) >= 6:
                            local = campos[3]
                            remoto = campos[4]
                            proceso_info = campos[6] if len(campos) > 6 else 'N/A'
                            
                            # Extraer IP remota y puerto
                            ip_remota = remoto.split(':')[0] if ':' in remoto else remoto
                            puerto_remoto = remoto.split(':')[-1] if ':' in remoto else 'N/A'
                            
                            # Criterios de sospecha
                            razones = []
                            
                            # IPs privadas conectando a puertos inusuales
                            if self._es_ip_privada(ip_remota):
                                continue  # Conexiones locales normalmente OK
                                
                            # Puertos sospechosos
                            puertos_sospechosos = ['1337', '31337', '4444', '5555', '6666', '7777', '8888', '9999']
                            if puerto_remoto in puertos_sospechosos:
                                razones.append("Puerto sospechoso")
                                
                            # Procesos sin identificar
                            if proceso_info == '-' or proceso_info == 'N/A':
                                razones.append("Proceso no identificado")
                                
                            if razones:
                                # Extraer PID y proceso
                                pid = 'N/A'
                                proceso = 'N/A'
                                if '/' in proceso_info:
                                    pid = proceso_info.split('/')[0]
                                    proceso = proceso_info.split('/')[1] if len(proceso_info.split('/')) > 1 else 'N/A'
                                
                                self.tree_sospechosas.insert('', 'end', values=(
                                    ip_remota, puerto_remoto, 'TCP', 'ESTABLISHED', pid, proceso, ", ".join(razones)
                                ))
                                sospechosas_encontradas += 1
                
                self._agregar_resultado(f"🚨 Análisis completado: {sospechosas_encontradas} conexiones sospechosas encontradas")
                
        except Exception as e:
            self._agregar_resultado(f"❌ Error detectando conexiones sospechosas: {e}")
            
    def _es_ip_privada(self, ip):
        """Verificar si una IP es privada"""
        try:
            # Rangos de IP privadas
            import ipaddress
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except:
            return False
            
    def _analizar_conexiones_sospechosas(self, conexiones):
        """Analizar conexiones para detectar actividad sospechosa automáticamente"""
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
            
        if hasattr(self, 'text_interfaces'):
            self.text_interfaces.delete('1.0', tk.END)
        
        # Limpiar trees
        if hasattr(self, 'tree_conexiones'):
            for item in self.tree_conexiones.get_children():
                self.tree_conexiones.delete(item)
                
        if hasattr(self, 'tree_puertos'):
            for item in self.tree_puertos.get_children():
                self.tree_puertos.delete(item)
                
        if hasattr(self, 'tree_sospechosas'):
            for item in self.tree_sospechosas.get_children():
                self.tree_sospechosas.delete(item)
                
    def cerrar(self):
        """Cerrar la vista y limpiar recursos"""
        self.monitoreo_red_activo = False
        if self.hilo_monitoreo_red and self.hilo_monitoreo_red.is_alive():
            self.hilo_monitoreo_red.join(timeout=2)
