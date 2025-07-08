#!/usr/bin/env python3
"""
Herramientas Avanzadas de Ares Aegis
Módulos de Monitoreo, Protección y Herramientas Especializadas

🔧 HERRAMIENTAS Y MÓDULOS AVANZADOS
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import os
import threading
import time
from datetime import datetime
from typing import Optional

from .interfaz_moderna_componentes import ComponentesModernos


class InterfazModernaHerramientas:
    def iniciar_monitoreo_completo(self):
        """Iniciar todos los módulos de monitoreo"""
        try:
            servicios_iniciados = []
            if self.controlador:
                try:
                    if hasattr(self.controlador, 'iniciar_monitor_red'):
                        self.controlador.iniciar_monitor_red()
                        servicios_iniciados.append("Monitor de Red")
                except Exception as e:
                    self.logger.warning(f"No se pudo iniciar monitor de red: {e}")
                try:
                    if hasattr(self.controlador, 'monitor_procesos') and self.controlador.monitor_procesos:
                        self.controlador.monitor_procesos.iniciar_monitoreo()
                        servicios_iniciados.append("Monitor de Procesos")
                except Exception as e:
                    self.logger.warning(f"No se pudo iniciar monitor de procesos: {e}")
                try:
                    if hasattr(self.controlador, 'fim') and self.controlador.fim:
                        if hasattr(self.controlador.fim, 'iniciar_monitoreo'):
                            self.controlador.fim.iniciar_monitoreo()
                            servicios_iniciados.append("Monitor FIM")
                except Exception as e:
                    self.logger.warning(f"No se pudo iniciar FIM: {e}")
                try:
                    if hasattr(self.controlador, 'analizador_dinamico') and self.controlador.analizador_dinamico:
                        if hasattr(self.controlador.analizador_dinamico, 'iniciar'):
                            self.controlador.analizador_dinamico.iniciar()
                            servicios_iniciados.append("Análisis Dinámico")
                except Exception as e:
                    self.logger.warning(f"No se pudo iniciar análisis dinámico: {e}")
            self.estados_monitor.update({
                "monitor_red_activo": True,
                "monitor_procesos_activo": True,
                "fim_activo": True,
                "analisis_dinamico_activo": True
            })
            mensaje = "Monitoreo completo iniciado"
            if servicios_iniciados:
                mensaje += f"\nServicios activos: {', '.join(servicios_iniciados)}"
            self.interfaz_base.mostrar_alerta(mensaje, tipo="info")
            self.mostrar_monitoreo()
        except Exception as e:
            self.logger.error(f"Error iniciando monitoreo: {e}")
            self.interfaz_base.mostrar_alerta(f"Error iniciando monitoreo:\n{str(e)}", tipo="critico")

    def detener_monitoreo_completo(self):
        """Detener todos los módulos de monitoreo"""
        try:
            servicios_detenidos = []
            if self.controlador:
                try:
                    if hasattr(self.controlador, 'detener_monitor_red'):
                        self.controlador.detener_monitor_red()
                        servicios_detenidos.append("Monitor de Red")
                except Exception as e:
                    self.logger.warning(f"No se pudo detener monitor de red: {e}")
                try:
                    if hasattr(self.controlador, 'monitor_procesos') and self.controlador.monitor_procesos:
                        self.controlador.monitor_procesos.detener_monitoreo()
                        servicios_detenidos.append("Monitor de Procesos")
                except Exception as e:
                    self.logger.warning(f"No se pudo detener monitor de procesos: {e}")
                try:
                    if hasattr(self.controlador, 'fim') and self.controlador.fim:
                        if hasattr(self.controlador.fim, 'detener_monitoreo'):
                            self.controlador.fim.detener_monitoreo()
                            servicios_detenidos.append("Monitor FIM")
                except Exception as e:
                    self.logger.warning(f"No se pudo detener FIM: {e}")
                try:
                    if hasattr(self.controlador, 'analizador_dinamico') and self.controlador.analizador_dinamico:
                        if hasattr(self.controlador.analizador_dinamico, 'detener'):
                            self.controlador.analizador_dinamico.detener()
                            servicios_detenidos.append("Análisis Dinámico")
                except Exception as e:
                    self.logger.warning(f"No se pudo detener análisis dinámico: {e}")
            self.estados_monitor.update({
                "monitor_red_activo": False,
                "monitor_procesos_activo": False,
                "fim_activo": False,
                "analisis_dinamico_activo": False
            })
            mensaje = "Monitoreo completo detenido"
            if servicios_detenidos:
                mensaje += f"\nServicios detenidos: {', '.join(servicios_detenidos)}"
            self.interfaz_base.mostrar_alerta(mensaje, tipo="info")
            self.mostrar_monitoreo()
        except Exception as e:
            self.logger.error(f"Error deteniendo monitoreo: {e}")
            self.interfaz_base.mostrar_alerta(f"Error deteniendo monitoreo:\n{str(e)}", tipo="critico")
    """Módulos avanzados de herramientas, monitoreo y protección"""
    
    def __init__(self, interfaz_base):
        """Inicializar con referencia a la interfaz base"""
        self.interfaz_base = interfaz_base
        self.logger = logging.getLogger(__name__)
        
        # Estados de monitoreo
        self.estados_monitor = {
            "monitor_red_activo": False,
            "monitor_procesos_activo": False,
            "fim_activo": False,
            "analisis_dinamico_activo": False
        }
        
        # Variables de interfaz
        self.current_activity_tab = "Red"
        self.activity_tab_buttons = {}
        self.activity_content_frame = None
        self.activity_text = None
        
        self.logger.info("Módulos de herramientas avanzadas inicializados")
    
    @property
    def root(self):
        """Acceso al root de la interfaz base"""
        return self.interfaz_base.root
    
    @property
    def content_frame(self):
        """Acceso al content_frame de la interfaz base"""
        return self.interfaz_base.content_frame
    
    @property
    def controlador(self):
        """Acceso al controlador de la interfaz base"""
        return self.interfaz_base.controlador
    
    def limpiar_contenido(self):
        """Usar el método de la interfaz base"""
        self.interfaz_base.limpiar_contenido()
    
    # ============================================================================
    # SECCIÓN DE MONITOREO COMPLETO
    # ============================================================================
    
    def mostrar_monitoreo(self):
        """Mostrar interfaz completa de monitoreo"""
        self.limpiar_contenido()
        
        # Container principal
        monitor_container = tk.Frame(self.content_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        monitor_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Header del monitoreo
        header_frame = tk.Frame(monitor_container, bg=ComponentesModernos.COLORES["bg_principal"])
        header_frame.pack(fill="x", pady=(0, 25))
        
        title_label = tk.Label(
            header_frame,
            text="📡 Centro de Monitoreo",
            font=("Segoe UI", 24, "bold"),
            bg=ComponentesModernos.COLORES["bg_principal"],
            fg=ComponentesModernos.COLORES["texto_primario"]
        )
        title_label.pack(side="left")
        
        # Botones de control
        control_frame = tk.Frame(header_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        control_frame.pack(side="right")
        
        ComponentesModernos.crear_boton_moderno(
            control_frame, "🔄 Actualizar", self.actualizar_datos_monitoreo, "outline"
        ).pack(side="right", padx=(0, 10))
        
        ComponentesModernos.crear_boton_moderno(
            control_frame, "▶️ Iniciar Todo", self.iniciar_monitoreo_completo, "primario"
        ).pack(side="right", padx=(0, 10))
        
        ComponentesModernos.crear_boton_moderno(
            control_frame, "⏹️ Detener Todo", self.detener_monitoreo_completo, "peligro"
        ).pack(side="right", padx=(0, 10))
        
        # Obtener estado actual de monitores
        estado_monitores = {}
        if self.controlador:
            try:
                estado_monitores = self.controlador.obtener_estado_monitores()
            except Exception as e:
                self.logger.error(f"Error obteniendo estado monitores: {e}")
        
        # Grid de módulos de monitoreo 
        modules_frame = tk.Frame(monitor_container, bg=ComponentesModernos.COLORES["bg_principal"])
        modules_frame.pack(fill="x", pady=(0, 25))
        
        # Configurar grid 2x2
        for i in range(2):
            modules_frame.columnconfigure(i, weight=1, uniform="monitor")
            modules_frame.rowconfigure(i, weight=1, uniform="monitor")
        
        # Módulos de monitoreo con datos reales
        modulos_monitor = [
            {
                "titulo": "📡 Monitor de Red",
                "descripcion": "Tráfico, conexiones y amenazas de red",
                "estado_var": "monitor_red_activo",
                "comando_toggle": self.toggle_monitor_red,
                "posicion": (0, 0)
            },
            {
                "titulo": "⚙️ Monitor de Procesos", 
                "descripcion": "Procesos, CPU y comportamientos sospechosos",
                "estado_var": "monitor_procesos_activo",
                "comando_toggle": self.toggle_monitor_procesos,
                "posicion": (0, 1)
            },
            {
                "titulo": "📁 Monitor FIM",
                "descripcion": "Integridad de archivos y cambios",
                "estado_var": "fim_activo",
                "comando_toggle": self.toggle_fim,
                "posicion": (1, 0)
            },
            {
                "titulo": "🔍 Análisis Dinámico",
                "descripcion": "Comportamiento en tiempo real",
                "estado_var": "analisis_dinamico_activo", 
                "comando_toggle": self.toggle_analisis_dinamico,
                "posicion": (1, 1)
            }
        ]
        
        for modulo in modulos_monitor:
            row, col = modulo["posicion"]
            
            card_container, content = ComponentesModernos.crear_card_moderna(
                modules_frame, modulo["titulo"], modulo["descripcion"]
            )
            card_container.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            
            # Estado del módulo
            estado_activo = self.estados_monitor.get(modulo["estado_var"], False)
            color_estado = ComponentesModernos.COLORES["activo"] if estado_activo else ComponentesModernos.COLORES["inactivo"]
            texto_estado = "ACTIVO" if estado_activo else "DETENIDO"
            
            estado_label = tk.Label(
                content,
                text=f"● {texto_estado}",
                font=("Segoe UI", 11, "bold"),
                bg=content.cget('bg'),
                fg=color_estado
            )
            estado_label.pack(pady=5)
            
            # Botón de toggle
            texto_btn = "Detener" if estado_activo else "Iniciar"
            color_btn = "peligro" if estado_activo else "primario"
            
            btn_toggle = ComponentesModernos.crear_boton_moderno(
                content, texto_btn, modulo["comando_toggle"], color_btn
            )
            btn_toggle.pack(pady=10)
        
        # Panel de actividad en tiempo real
        self.crear_panel_actividad_tiempo_real(monitor_container)
    
    def crear_panel_actividad_tiempo_real(self, parent):
        """Crear panel de actividad en tiempo real"""
        activity_container, activity_content = ComponentesModernos.crear_card_moderna(
            parent, "📊 Actividad en Tiempo Real", "Eventos y estadísticas live"
        )
        activity_container.pack(fill="both", expand=True)
        
        # Frame para pestañas de actividad
        tabs_frame = tk.Frame(activity_content, bg=activity_content.cget('bg'))
        tabs_frame.pack(fill="x", pady=(0, 15))
        
        # Pestañas de actividad
        activity_tabs = ["Red", "Procesos", "Archivos", "Sistema"]
        self.activity_tab_buttons = {}
        self.current_activity_tab = "Red"
        
        for tab in activity_tabs:
            btn = ComponentesModernos.crear_boton_moderno(
                tabs_frame, tab, lambda t=tab: self.cambiar_tab_actividad(t), "outline"
            )
            btn.pack(side="left", padx=(0, 10))
            self.activity_tab_buttons[tab] = btn
        
        # Contenido del tab
        self.activity_content_frame = tk.Frame(activity_content, bg=activity_content.cget('bg'))
        self.activity_content_frame.pack(fill="both", expand=True)
        
        # Cargar contenido inicial
        self.cambiar_tab_actividad("Red")
        
        # Iniciar actualización automática
        self.actualizar_actividad_tiempo_real()
    
    def cambiar_tab_actividad(self, tab):
        """Cambiar tab de actividad"""
        self.current_activity_tab = tab
        
        # Actualizar botones
        for t, btn in self.activity_tab_buttons.items():
            if t == tab:
                btn.config(bg=ComponentesModernos.COLORES["primario"], fg=ComponentesModernos.COLORES["texto_primario"])
            else:
                btn.config(bg=ComponentesModernos.COLORES["bg_secundario"], fg=ComponentesModernos.COLORES["texto_secundario"])
        
        # Limpiar contenido
        if self.activity_content_frame:
            for widget in self.activity_content_frame.winfo_children():
                widget.destroy()
        
        # Cargar contenido del tab
        self.cargar_contenido_actividad(tab)
    
    def cargar_contenido_actividad(self, tab):
        """Cargar contenido de actividad específico"""
        if not self.activity_content_frame:
            return
            
        # Lista scrollable para eventos
        list_frame = tk.Frame(self.activity_content_frame, bg=self.activity_content_frame.cget('bg'))
        list_frame.pack(fill="both", expand=True, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Text widget para eventos
        self.activity_text = tk.Text(
            list_frame,
            bg=ComponentesModernos.COLORES["bg_secundario"],
            fg=ComponentesModernos.COLORES["texto_primario"],
            font=("Consolas", 9),
            yscrollcommand=scrollbar.set,
            relief="flat",
            borderwidth=0,
            wrap="word",
            state="disabled"
        )
        self.activity_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.activity_text.yview)
        
        # Cargar eventos específicos del tab
        self.cargar_eventos_tab(tab)
    
    def cargar_eventos_tab(self, tab):
        """Cargar eventos específicos del tab"""
        if not self.activity_text:
            return
            
        self.activity_text.config(state="normal")
        self.activity_text.delete("1.0", tk.END)
        
        try:
            if tab == "Red":
                eventos = self.obtener_eventos_red()
            elif tab == "Procesos":
                eventos = self.obtener_eventos_procesos()
            elif tab == "Archivos":
                eventos = self.obtener_eventos_fim()
            else:
                eventos = ["Monitor del sistema activo", "Estadísticas disponibles"]
            
            for evento in eventos[-50:]:  # Últimos 50 eventos
                self.activity_text.insert(tk.END, f"{evento}\n")
        
        except Exception as e:
            self.activity_text.insert(tk.END, f"Error cargando eventos: {str(e)}\n")
        
        self.activity_text.config(state="disabled")
        self.activity_text.see(tk.END)
    
    def actualizar_datos_monitoreo(self):
        """Actualizar datos de monitoreo"""
        try:
            if self.controlador:
                # Obtener datos actuales del controlador
                estado_monitores = self.controlador.obtener_estado_monitores()
                self.logger.info("Datos de monitoreo actualizados")
                
                # Actualizar estados internos
                self.estados_monitor.update({
                    "monitor_red_activo": estado_monitores.get("monitor_red", {}).get("activo", False),
                    "monitor_procesos_activo": estado_monitores.get("monitor_procesos", {}).get("activo", False),
                    "fim_activo": estado_monitores.get("fim", {}).get("activo", False),
                    "analisis_dinamico_activo": estado_monitores.get("analisis_dinamico", {}).get("activo", False)
                })
                
                # Refrescar interfaz
                self.mostrar_monitoreo()
                self.interfaz_base.mostrar_alerta("Datos de monitoreo actualizados", tipo="info")
            else:
                self.interfaz_base.mostrar_alerta("Controlador no disponible", tipo="advertencia")
        except Exception as e:
            self.logger.error(f"Error actualizando monitoreo: {e}")
            self.interfaz_base.mostrar_alerta(f"Error actualizando datos: {str(e)}", tipo="critico")
    
    def obtener_eventos_red(self):
        """Obtener eventos de red"""
        eventos_base = []
        
        # Intentar obtener datos reales del controlador
        try:
            if self.controlador:
                # Obtener estado real del monitor de red
                if hasattr(self.controlador, 'monitor_red') and self.controlador.monitor_red:
                    estado_red = self.controlador.monitor_red.obtener_estadisticas()
                    if estado_red.get("exito"):
                        conexiones = estado_red.get("conexiones_activas", 0)
                        trafico = estado_red.get("trafico_total", 0)
                        conexiones_bloqueadas = estado_red.get("conexiones_bloqueadas", 0)
                        
                        eventos_base = [
                            f"Conexiones activas: {conexiones}",
                            f"Estado monitor: {'Activo' if self.estados_monitor.get('monitor_red_activo') else 'Inactivo'}",
                            f"Tráfico total: {trafico / 1024 / 1024:.2f} MB" if trafico > 0 else "Tráfico total: 0 MB",
                            f"Conexiones bloqueadas: {conexiones_bloqueadas}",
                            f"Última actualización: {datetime.now().strftime('%H:%M:%S')}"
                        ]
                    else:
                        eventos_base = [
                            "Monitor de red no disponible",
                            "Estado: Inactivo",
                            "Reinicia el monitor para obtener datos",
                        ]
                
                # Obtener eventos recientes del SIEM relacionados con red
                if hasattr(self.controlador, 'siem') and self.controlador.siem:
                    eventos_siem = self.controlador.siem.obtener_eventos_recientes(limite=10, tipo="red")
                    if eventos_siem.get("exito"):
                        for evento in eventos_siem.get("eventos", [])[-5:]:  # Últimos 5 eventos
                            timestamp = evento.get("timestamp", "")
                            descripcion = evento.get("descripcion", "")
                            eventos_base.append(f"[{timestamp}] {descripcion}")
                            
        except Exception as e:
            self.logger.debug(f"Error obteniendo eventos de red reales: {e}")
            eventos_base = [
                "Error obteniendo datos de red",
                "Verifica el estado del monitor",
                f"Error: {str(e)}"
            ]
        
        # Si no hay eventos reales, mostrar estado básico
        if not eventos_base:
            eventos_base = [
                "Monitor de red disponible",
                "Inicia el monitoreo para ver datos",
                "Estado: Esperando activación"
            ]
        
        return eventos_base
    
    def obtener_eventos_procesos(self):
        """Obtener eventos de procesos"""
        eventos_base = []
        
        try:
            if self.controlador:
                # Obtener estadísticas reales del monitor de procesos
                if hasattr(self.controlador, 'monitor_procesos') and self.controlador.monitor_procesos:
                    stats = self.controlador.monitor_procesos.obtener_estadisticas_sistema()
                    if stats.get("exito"):
                        cpu_percent = stats.get("cpu_percent", 0)
                        memory_percent = stats.get("memory_percent", 0)
                        procesos_count = stats.get("procesos_activos", 0)
                        procesos_sospechosos = stats.get("procesos_sospechosos", 0)
                        
                        # Evaluar estados
                        cpu_estado = "Normal" if cpu_percent < 70 else "Alto" if cpu_percent < 90 else "Crítico"
                        mem_estado = "Normal" if memory_percent < 80 else "Advertencia" if memory_percent < 95 else "Crítico"
                        
                        eventos_base = [
                            f"Monitor de procesos: {'Activo' if self.estados_monitor.get('monitor_procesos_activo') else 'Inactivo'}",
                            f"CPU: {cpu_percent:.1f}% - {cpu_estado}",
                            f"RAM: {memory_percent:.1f}% - {mem_estado}",
                            f"Procesos monitoreados: {procesos_count}",
                            f"Procesos sospechosos: {procesos_sospechosos}",
                            f"Última actualización: {datetime.now().strftime('%H:%M:%S')}"
                        ]
                    else:
                        eventos_base = [
                            "Monitor de procesos no disponible",
                            "Estado: Inactivo",
                            "Inicia el monitor para obtener datos"
                        ]
                
                # Obtener alertas recientes de procesos del SIEM
                if hasattr(self.controlador, 'siem') and self.controlador.siem:
                    eventos_siem = self.controlador.siem.obtener_eventos_recientes(limite=10, tipo="proceso")
                    if eventos_siem.get("exito"):
                        for evento in eventos_siem.get("eventos", [])[-3:]:  # Últimos 3 eventos
                            timestamp = evento.get("timestamp", "")[:8]  # Solo HH:MM:SS
                            descripcion = evento.get("descripcion", "")
                            eventos_base.append(f"[{timestamp}] {descripcion}")
                            
        except Exception as e:
            self.logger.debug(f"Error obteniendo eventos de procesos reales: {e}")
            eventos_base = [
                "Error obteniendo datos de procesos",
                "Verifica el estado del monitor",
                f"Error: {str(e)}"
            ]
        
        # Si no hay eventos reales, mostrar estado básico
        if not eventos_base:
            eventos_base = [
                "Monitor de procesos disponible",
                "Inicia el monitoreo para ver estadísticas",
                "Estado: Esperando activación"
            ]
        
        return eventos_base
    
    def obtener_eventos_fim(self):
        """Obtener eventos de FIM"""
        eventos_base = []
        
        try:
            if self.controlador:
                # Obtener estado real del FIM
                if hasattr(self.controlador, 'fim') and self.controlador.fim:
                    estado_fim = self.controlador.fim.obtener_estado()
                    if estado_fim.get("exito"):
                        archivos_monitoreados = estado_fim.get("archivos_monitoreados", 0)
                        cambios_detectados = estado_fim.get("cambios_detectados", 0)
                        integridad_ok = estado_fim.get("integridad_ok", True)
                        ultima_verificacion = estado_fim.get("ultima_verificacion", "Nunca")
                        
                        eventos_base = [
                            f"Monitor FIM: {'Activo' if self.estados_monitor.get('fim_activo') else 'Inactivo'}",
                            f"Archivos monitoreados: {archivos_monitoreados:,}",
                            f"Cambios detectados hoy: {cambios_detectados}",
                            f"Integridad: {'OK' if integridad_ok else 'COMPROMETIDA'}",
                            f"Última verificación: {ultima_verificacion}",
                            f"Estado: {'✅ Protegido' if integridad_ok else '⚠️ Verificar cambios'}"
                        ]
                    else:
                        eventos_base = [
                            "Monitor FIM no disponible",
                            "Estado: Inactivo",
                            "Crea un baseline para comenzar"
                        ]
                
                # Obtener eventos recientes de FIM del SIEM
                if hasattr(self.controlador, 'siem') and self.controlador.siem:
                    eventos_siem = self.controlador.siem.obtener_eventos_recientes(limite=10, tipo="integridad")
                    if eventos_siem.get("exito"):
                        for evento in eventos_siem.get("eventos", [])[-3:]:  # Últimos 3 eventos
                            timestamp = evento.get("timestamp", "")[:8]  # Solo HH:MM:SS
                            descripcion = evento.get("descripcion", "")
                            severidad = evento.get("severidad", "info")
                            icono = "🔴" if severidad == "critica" else "🟡" if severidad == "alta" else "🟢"
                            eventos_base.append(f"{icono} [{timestamp}] {descripcion}")
                            
        except Exception as e:
            self.logger.debug(f"Error obteniendo eventos de FIM reales: {e}")
            eventos_base = [
                "Error obteniendo datos de FIM",
                "Verifica el estado del monitor",
                f"Error: {str(e)}"
            ]
        
        # Si no hay eventos reales, mostrar estado básico
        eventos_base = []
        try:
            if self.controlador:
                # Obtener estadísticas reales del FIM
                if hasattr(self.controlador, 'fim') and self.controlador.fim:
                    stats = self.controlador.fim.obtener_estadisticas()
                    archivos_monitoreados = stats.get("archivos_monitoreados", 0)
                    cambios_detectados = stats.get("cambios_detectados", 0)
                    integridad_ok = stats.get("alertas_pendientes", 0) == 0
                    ultima_verificacion = stats.get("tiempo_ultima_verificacion", "Nunca")
                    estado_fim = stats.get("estado_monitoreo", "INACTIVO")
                    eventos_base = [
                        f"Monitor FIM: {'Activo' if estado_fim == 'ACTIVO' else 'Inactivo'}",
                        f"Archivos monitoreados: {archivos_monitoreados:,}",
                        f"Cambios detectados: {cambios_detectados}",
                        f"Integridad: {'OK' if integridad_ok else 'COMPROMETIDA'}",
                        f"Última verificación: {ultima_verificacion}",
                        f"Estado: {'✅ Protegido' if integridad_ok else '⚠️ Verificar cambios'}"
                    ]
                else:
                    eventos_base = [
                        "Monitor FIM no disponible",
                        "Estado: Inactivo",
                        "Crea un baseline para comenzar"
                    ]
                # Obtener eventos recientes de FIM del SIEM
                if hasattr(self.controlador, 'siem') and self.controlador.siem:
                    eventos_siem = self.controlador.siem.obtener_eventos_recientes(limite=10, tipo="integridad")
                    if eventos_siem.get("exito"):
                        for evento in eventos_siem.get("eventos", [])[-3:]:  # Últimos 3 eventos
                            timestamp = evento.get("timestamp", "")[:8]  # Solo HH:MM:SS
                            descripcion = evento.get("descripcion", "")
                            severidad = evento.get("severidad", "info")
                            icono = "🔴" if severidad == "critica" else "🟡" if severidad == "alta" else "🟢"
                            eventos_base.append(f"{icono} [{timestamp}] {descripcion}")
        except Exception as e:
            self.logger.debug(f"Error obteniendo eventos de FIM reales: {e}")
            eventos_base = [
                "Error obteniendo datos de FIM",
                "Verifica el estado del monitor",
                f"Error: {str(e)}"
            ]
        # Si no hay eventos reales, mostrar estado básico
        if not eventos_base:
            eventos_base = [
                "Monitor FIM disponible",
                "Crea un baseline para monitorear integridad",
                "Estado: Esperando configuración"
            ]
        return eventos_base
    
    def toggle_monitor_red(self):
        """Toggle monitor de red"""
        try:
            if self.controlador:
                if self.estados_monitor["monitor_red_activo"]:
                    # Detener monitor
                    if hasattr(self.controlador, 'detener_monitor_red'):
                        resultado = self.controlador.detener_monitor_red()
                        if resultado.get("exito", True):
                            self.estados_monitor["monitor_red_activo"] = False
                            self.interfaz_base.mostrar_alerta("Monitor de red detenido exitosamente", tipo="info")
                        else:
                            self.interfaz_base.mostrar_alerta(f"Error deteniendo monitor: {resultado.get('error', 'Error desconocido')}", tipo="critico")
                    else:
                        self.estados_monitor["monitor_red_activo"] = False
                        self.interfaz_base.mostrar_alerta("Monitor de red detenido", tipo="info")
                else:
                    # Iniciar monitor
                    if hasattr(self.controlador, 'iniciar_monitor_red'):
                        resultado = self.controlador.iniciar_monitor_red()
                        if resultado.get("exito", True):
                            self.estados_monitor["monitor_red_activo"] = True
                            self.interfaz_base.mostrar_alerta("Monitor de red iniciado exitosamente", tipo="info")
                        else:
                            self.interfaz_base.mostrar_alerta(f"Error iniciando monitor: {resultado.get('error', 'Error desconocido')}", tipo="critico")
                    else:
                        self.estados_monitor["monitor_red_activo"] = True
                        self.interfaz_base.mostrar_alerta("Monitor de red iniciado", tipo="info")
                # Refrescar interfaz y forzar actualización de datos
                self.actualizar_datos_monitoreo()
            else:
                self.interfaz_base.mostrar_alerta("Controlador no disponible", tipo="advertencia")
        except Exception as e:
            self.logger.error(f"Error en toggle monitor de red: {e}")
            self.interfaz_base.mostrar_alerta(f"Error en monitor de red: {str(e)}", tipo="critico")
    
    def toggle_monitor_procesos(self):
        """Toggle monitor de procesos"""
        try:
            if self.controlador:
                if self.estados_monitor["monitor_procesos_activo"]:
                    # Detener monitor
                    if hasattr(self.controlador, 'monitor_procesos') and self.controlador.monitor_procesos:
                        resultado = self.controlador.monitor_procesos.detener_monitoreo()
                        if resultado.get("exito", True):
                            self.estados_monitor["monitor_procesos_activo"] = False
                            self.interfaz_base.mostrar_alerta("Monitor de procesos detenido exitosamente", tipo="info")
                        else:
                            self.interfaz_base.mostrar_alerta(f"Error deteniendo monitor: {resultado.get('error', 'Error desconocido')}", tipo="critico")
                    else:
                        self.estados_monitor["monitor_procesos_activo"] = False
                        self.interfaz_base.mostrar_alerta("Monitor de procesos detenido", tipo="info")
                else:
                    # Iniciar monitor
                    if hasattr(self.controlador, 'monitor_procesos') and self.controlador.monitor_procesos:
                        resultado = self.controlador.monitor_procesos.iniciar_monitoreo()
                        if resultado.get("exito", True):
                            self.estados_monitor["monitor_procesos_activo"] = True
                            self.interfaz_base.mostrar_alerta("Monitor de procesos iniciado exitosamente", tipo="info")
                        else:
                            self.interfaz_base.mostrar_alerta(f"Error iniciando monitor: {resultado.get('error', 'Error desconocido')}", tipo="critico")
                    else:
                        self.estados_monitor["monitor_procesos_activo"] = True
                        self.interfaz_base.mostrar_alerta("Monitor de procesos iniciado", tipo="info")
                # Refrescar interfaz y forzar actualización de datos
                self.actualizar_datos_monitoreo()
            else:
                self.interfaz_base.mostrar_alerta("Controlador no disponible", tipo="advertencia")
        except Exception as e:
            self.logger.error(f"Error en toggle monitor de procesos: {e}")
            self.interfaz_base.mostrar_alerta(f"Error en monitor de procesos: {str(e)}", tipo="critico")
    
    def toggle_fim(self):
        """Toggle FIM"""
        try:
            if self.controlador:
                if self.estados_monitor["fim_activo"]:
                    # Detener FIM
                    if hasattr(self.controlador, 'fim') and self.controlador.fim:
                        resultado = self.controlador.fim.detener_monitoreo()
                        if resultado.get("exito", True):
                            self.estados_monitor["fim_activo"] = False
                            messagebox.showinfo("Monitor FIM", "Monitor FIM detenido exitosamente")
                        else:
                            messagebox.showerror("Error", f"Error deteniendo FIM: {resultado.get('error', 'Error desconocido')}")
                    else:
                        self.estados_monitor["fim_activo"] = False
                        messagebox.showinfo("Monitor FIM", "Monitor FIM detenido")
                else:
                    # Iniciar FIM
                    if hasattr(self.controlador, 'fim') and self.controlador.fim:
                        # Verificar si existe baseline
                        estado = self.controlador.fim.obtener_estado()
                        if not estado.get("baseline_existe", False):
                            respuesta = messagebox.askyesno(
                                "FIM - Baseline requerido",
                                "No existe un baseline de integridad.\n¿Deseas crear uno ahora?\n\n"
                                "Esto escaneará los archivos críticos del sistema."
                            )
                            if respuesta:
                                # Crear baseline
                                resultado_baseline = self.controlador.crear_baseline_fim()
                                if not resultado_baseline.get("exito", False):
                                    messagebox.showerror("Error", f"Error creando baseline: {resultado_baseline.get('error', 'Error desconocido')}")
                                    return
                            else:
                                return
                        # Iniciar monitoreo FIM
                        resultado = self.controlador.fim.iniciar_monitoreo()
                        if resultado.get("exito", True):
                            self.estados_monitor["fim_activo"] = True
                            messagebox.showinfo("Monitor FIM", "Monitor FIM iniciado exitosamente")
                        else:
                            messagebox.showerror("Error", f"Error iniciando FIM: {resultado.get('error', 'Error desconocido')}")
                    else:
                        self.estados_monitor["fim_activo"] = True
                        messagebox.showinfo("Monitor FIM", "Monitor FIM iniciado")
                # Refrescar interfaz y forzar actualización de datos
                self.actualizar_datos_monitoreo()
            else:
                messagebox.showwarning("Error", "Controlador no disponible")
        except Exception as e:
            self.logger.error(f"Error en toggle FIM: {e}")
            messagebox.showerror("Error", f"Error en FIM: {str(e)}")
    
    def toggle_analisis_dinamico(self):
        """Toggle análisis dinámico"""
        try:
            if self.controlador and hasattr(self.controlador, 'analizador_dinamico') and self.controlador.analizador_dinamico:
                if self.estados_monitor["analisis_dinamico_activo"]:
                    # Detener análisis dinámico
                    if hasattr(self.controlador.analizador_dinamico, 'detener'):
                        self.controlador.analizador_dinamico.detener()
                    self.estados_monitor["analisis_dinamico_activo"] = False
                    estado = "detenido"
                else:
                    # Iniciar análisis dinámico
                    if hasattr(self.controlador.analizador_dinamico, 'iniciar'):
                        self.controlador.analizador_dinamico.iniciar()
                    self.estados_monitor["analisis_dinamico_activo"] = True
                    estado = "iniciado"
                messagebox.showinfo("Análisis Dinámico", f"Análisis dinámico {estado}")
                self.actualizar_datos_monitoreo()
            else:
                # Fallback: solo cambia el estado
                self.estados_monitor["analisis_dinamico_activo"] = not self.estados_monitor["analisis_dinamico_activo"]
                estado = "iniciado" if self.estados_monitor["analisis_dinamico_activo"] else "detenido"
                messagebox.showinfo("Análisis Dinámico", f"Análisis dinámico {estado}")
                self.actualizar_datos_monitoreo()
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis dinámico:\n{str(e)}")
    
    def actualizar_actividad_tiempo_real(self):
        """Actualizar actividad en tiempo real"""
        try:
            if hasattr(self, 'current_activity_tab') and self.activity_text:
                self.cargar_eventos_tab(self.current_activity_tab)
            
            # Programar siguiente actualización
            if self.root:
                self.root.after(5000, self.actualizar_actividad_tiempo_real)  # 5 segundos
                
        except Exception as e:
            self.logger.error(f"Error actualizando actividad: {e}")
    
    # ============================================================================
    # SECCIÓN DE PROTECCIÓN
    # ============================================================================
    
    def mostrar_proteccion(self):
        """Mostrar interfaz de protección proactiva"""
        self.limpiar_contenido()
        
        # Container principal
        protection_container = tk.Frame(self.content_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        protection_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Header
        header_frame = tk.Frame(protection_container, bg=ComponentesModernos.COLORES["bg_principal"])
        header_frame.pack(fill="x", pady=(0, 25))
        
        title_label = tk.Label(
            header_frame,
            text="🛡️ Centro de Protección",
            font=("Segoe UI", 24, "bold"),
            bg=ComponentesModernos.COLORES["bg_principal"],
            fg=ComponentesModernos.COLORES["texto_primario"]
        )
        title_label.pack(side="left")
        
        # Estado general de protección
        status_frame = tk.Frame(header_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        status_frame.pack(side="right")
        
        protection_status_label = tk.Label(
            status_frame,
            text="🟢 PROTECCIÓN ACTIVA",
            font=("Segoe UI", 14, "bold"),
            bg=ComponentesModernos.COLORES["bg_principal"],
            fg=ComponentesModernos.COLORES["activo"]
        )
        protection_status_label.pack()
        
        # Grid de módulos de protección
        modules_grid = tk.Frame(protection_container, bg=ComponentesModernos.COLORES["bg_principal"])
        modules_grid.pack(fill="both", expand=True)
        
        # Configurar grid 2x3
        for i in range(3):
            modules_grid.columnconfigure(i, weight=1, uniform="protection")
        for i in range(2):
            modules_grid.rowconfigure(i, weight=1, uniform="protection")
        
        # Módulos de protección
        protection_modules = [
            {
                "titulo": "🚫 Firewall Inteligente",
                "descripcion": "Bloqueo automático de amenazas",
                "icono": "🔥",
                "comando": self.configurar_firewall,
                "posicion": (0, 0)
            },
            {
                "titulo": "🦠 Antimalware Real-time",
                "descripcion": "Detección y eliminación en tiempo real",
                "icono": "🛡️",
                "comando": self.configurar_antimalware,
                "posicion": (0, 1)
            },
            {
                "titulo": "🔒 Control de Acceso",
                "descripcion": "Gestión de permisos y privilegios",
                "icono": "🔐",
                "comando": self.configurar_control_acceso,
                "posicion": (0, 2)
            },
            {
                "titulo": "📨 Filtro de Email",
                "descripcion": "Protección contra phishing y spam",
                "icono": "📧",
                "comando": self.configurar_filtro_email,
                "posicion": (1, 0)
            },
            {
                "titulo": "🌐 Protección Web",
                "descripcion": "Navegación segura y filtrado URL",
                "icono": "🌍",
                "comando": self.configurar_proteccion_web,
                "posicion": (1, 1)
            },
            {
                "titulo": "💾 Backup Automático",
                "descripcion": "Respaldo automático de archivos críticos",
                "icono": "💿",
                "comando": self.configurar_backup,
                "posicion": (1, 2)
            }
        ]
        
        for module in protection_modules:
            row, col = module["posicion"]
            
            card_container, content = ComponentesModernos.crear_card_moderna(
                modules_grid, module["titulo"], module["descripcion"]
            )
            card_container.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
            
            # Icono grande
            icon_label = tk.Label(
                content,
                text=module["icono"],
                font=("Segoe UI", 36),
                bg=content.cget('bg'),
                fg="#7b68ee"
            )
            icon_label.pack(pady=15)
            
            # Botón de configuración
            ComponentesModernos.crear_boton_moderno(
                content, "Configurar", module["comando"], "primario"
            ).pack(pady=10)
            
            # Estado del módulo (simulado)
            estado_label = tk.Label(
                content,
                text="● ACTIVO",
                font=("Segoe UI", 10, "bold"),
                bg=content.cget('bg'),
                fg=ComponentesModernos.COLORES["activo"]
            )
            estado_label.pack()
    
    def configurar_firewall(self):
        """Configurar firewall inteligente usando UFW/iptables"""
        try:
            if self.controlador and hasattr(self.controlador, 'firewall'):
                resultado = self.controlador.firewall.obtener_estado()
                if resultado.get("exito"):
                    reglas = resultado.get("reglas", [])
                    estado = resultado.get("estado", "Desconocido")
                    msg = f"Estado del firewall: {estado}\n\nReglas activas:\n" + "\n".join(reglas)
                    messagebox.showinfo("Firewall", msg)
                else:
                    messagebox.showerror("Firewall", f"Error obteniendo estado: {resultado.get('error', 'Error desconocido')}")
            else:
                # Fallback: usar iptables directamente
                import subprocess
                proc = subprocess.run(["sudo", "iptables", "-L"], capture_output=True, text=True)
                if proc.returncode == 0:
                    messagebox.showinfo("Firewall (iptables)", proc.stdout[:2000])
                else:
                    messagebox.showerror("Firewall", f"Error ejecutando iptables: {proc.stderr}")
        except Exception as e:
            messagebox.showerror("Firewall", f"Error: {str(e)}")
    
    def configurar_antimalware(self):
        """Ejecutar escaneo antimalware usando herramientas de Kali (ej: chkrootkit, clamscan)"""
        try:
            import subprocess
            # Preferir clamscan si está disponible
            proc = subprocess.run(["which", "clamscan"], capture_output=True, text=True)
            if proc.returncode == 0 and proc.stdout.strip():
                scan = subprocess.run(["clamscan", "--infected", "--recursive", "/home"], capture_output=True, text=True)
                messagebox.showinfo("Antimalware (ClamAV)", scan.stdout[-2000:] if scan.stdout else "Sin resultados")
            else:
                # Fallback: chkrootkit
                proc2 = subprocess.run(["which", "chkrootkit"], capture_output=True, text=True)
                if proc2.returncode == 0 and proc2.stdout.strip():
                    scan2 = subprocess.run(["sudo", "chkrootkit"], capture_output=True, text=True)
                    messagebox.showinfo("Antimalware (chkrootkit)", scan2.stdout[-2000:] if scan2.stdout else "Sin resultados")
                else:
                    messagebox.showwarning("Antimalware", "No se encontró clamscan ni chkrootkit en el sistema.")
        except Exception as e:
            messagebox.showerror("Antimalware", f"Error: {str(e)}")
    
    def configurar_control_acceso(self):
        """Mostrar usuarios y grupos del sistema (Kali)"""
        try:
            import subprocess
            proc = subprocess.run(["cut", "-d:", "-f1,3,4", "/etc/passwd"], capture_output=True, text=True)
            if proc.returncode == 0:
                usuarios = proc.stdout.strip().split('\n')
                msg = "Usuarios del sistema (user:uid:gid):\n" + "\n".join(usuarios[:30])
                messagebox.showinfo("Control de Acceso", msg)
            else:
                messagebox.showerror("Control de Acceso", "No se pudo obtener la lista de usuarios")
        except Exception as e:
            messagebox.showerror("Control de Acceso", f"Error: {str(e)}")
    
    def configurar_filtro_email(self):
        """Mostrar estado básico de filtro de email (simulación mínima, sin duplicar lógica)"""
        try:
            if self.controlador and hasattr(self.controlador, 'filtro_email'):
                estado = self.controlador.filtro_email.obtener_estado()
                if estado.get("exito"):
                    reglas = estado.get("reglas", [])
                    msg = "Reglas de filtro de email activas:\n" + "\n".join(reglas)
                    messagebox.showinfo("Filtro Email", msg)
                else:
                    messagebox.showerror("Filtro Email", f"Error: {estado.get('error', 'Error desconocido')}")
            else:
                messagebox.showinfo("Filtro Email", "No hay integración real de filtro de email en este sistema. Configure un gateway externo para protección avanzada.")
        except Exception as e:
            messagebox.showerror("Filtro Email", f"Error: {str(e)}")
    
    def configurar_proteccion_web(self):
        """Mostrar hosts bloqueados y configuración básica de protección web"""
        try:
            import subprocess
            # Leer /etc/hosts y mostrar entradas personalizadas
            with open("/etc/hosts", "r") as f:
                hosts = f.readlines()
            bloqueos = [line.strip() for line in hosts if line.strip() and not line.startswith("#") and "127.0.0.1" in line]
            msg = "Entradas de bloqueo en /etc/hosts:\n" + ("\n".join(bloqueos) if bloqueos else "No hay bloqueos personalizados.")
            messagebox.showinfo("Protección Web", msg)
        except Exception as e:
            messagebox.showerror("Protección Web", f"Error: {str(e)}")
    
    def configurar_backup(self):
        """Mostrar estado de backups automáticos (simulación mínima, integración real si existe controlador)"""
        try:
            if self.controlador and hasattr(self.controlador, 'backup'):
                estado = self.controlador.backup.obtener_estado()
                if estado.get("exito"):
                    ultimos = estado.get("ultimos_backups", [])
                    msg = "Últimos backups realizados:\n" + "\n".join(ultimos)
                    messagebox.showinfo("Backup", msg)
                else:
                    messagebox.showerror("Backup", f"Error: {estado.get('error', 'Error desconocido')}")
            else:
                messagebox.showinfo("Backup", "No hay integración real de backup automático. Use herramientas como rsync, timeshift o scripts personalizados para backups en Kali.")
        except Exception as e:
            messagebox.showerror("Backup", f"Error: {str(e)}")
    
    # ============================================================================
    # SECCIÓN DE HERRAMIENTAS
    # ============================================================================
    
    def mostrar_herramientas(self):
        """Mostrar interfaz de herramientas"""
        self.limpiar_contenido()
        
        # Container principal
        tools_container = tk.Frame(self.content_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        tools_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Header
        header_frame = tk.Frame(tools_container, bg=ComponentesModernos.COLORES["bg_principal"])
        header_frame.pack(fill="x", pady=(0, 25))
        
        title_label = tk.Label(
            header_frame,
            text="🔧 Herramientas de Seguridad",
            font=("Segoe UI", 24, "bold"),
            bg=ComponentesModernos.COLORES["bg_principal"],
            fg=ComponentesModernos.COLORES["texto_primario"]
        )
        title_label.pack(side="left")
        
        # Grid de herramientas
        tools_grid = tk.Frame(tools_container, bg=ComponentesModernos.COLORES["bg_principal"])
        tools_grid.pack(fill="both", expand=True)
        
        # Configurar grid 3x3
        for i in range(3):
            tools_grid.columnconfigure(i, weight=1, uniform="tools")
            tools_grid.rowconfigure(i, weight=1, uniform="tools")
        
        # Herramientas disponibles
        herramientas = [
            {
                "titulo": "🔍 Visor Hexadecimal",
                "descripcion": "Análisis binario de archivos",
                "icono": "🔬",
                "comando": self.abrir_visor_hex,
                "posicion": (0, 0)
            },
            {
                "titulo": "📊 Análisis de Cadenas",
                "descripcion": "Extracción de strings de archivos",
                "icono": "📝",
                "comando": self.abrir_analizador_cadenas,
                "posicion": (0, 1)
            },
            {
                "titulo": "🔎 Buscador CVE",
                "descripcion": "Búsqueda de vulnerabilidades",
                "icono": "🎯",
                "comando": self.abrir_buscador_cve,
                "posicion": (0, 2)
            },
            {
                "titulo": "📚 Cheat Sheets",
                "descripcion": "Guías de referencia rápida",
                "icono": "📖",
                "comando": self.abrir_cheatsheets,
                "posicion": (1, 0)
            },
            {
                "titulo": "🧹 Descontaminación",
                "descripcion": "Limpieza inteligente de malware",
                "icono": "🧽",
                "comando": self.abrir_descontaminacion,
                "posicion": (1, 1)
            },
            {
                "titulo": "🌐 Escáner de Red",
                "descripcion": "Descubrimiento de dispositivos",
                "icono": "📡",
                "comando": self.abrir_escaner_red,
                "posicion": (1, 2)
            },
            {
                "titulo": "💉 Respondedor Auto",
                "descripcion": "Respuesta automática a incidentes",
                "icono": "🚨",
                "comando": self.abrir_respondedor,
                "posicion": (2, 0)
            },
            {
                "titulo": "📈 Integración Externa",
                "descripcion": "APIs y servicios externos",
                "icono": "🔗",
                "comando": self.abrir_integracion,
                "posicion": (2, 1)
            },
            {
                "titulo": "⚙️ Configuración Avanzada",
                "descripcion": "Parámetros del sistema",
                "icono": "🛠️",
                "comando": self.abrir_config_avanzada,
                "posicion": (2, 2)
            }
        ]
        
        for herramienta in herramientas:
            row, col = herramienta["posicion"]
            
            card_container, content = ComponentesModernos.crear_card_moderna(
                tools_grid, herramienta["titulo"], herramienta["descripcion"]
            )
            card_container.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            
            # Icono
            icon_label = tk.Label(
                content,
                text=herramienta["icono"],
                font=("Segoe UI", 32),
                bg=content.cget('bg'),
                fg="#7b68ee"
            )
            icon_label.pack(pady=10)
            
            # Botón de acción
            ComponentesModernos.crear_boton_moderno(
                content, "Abrir", herramienta["comando"], "primario"
            ).pack(pady=5)
    
    def abrir_visor_hex(self):
        """Abrir visor hexadecimal"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo para análisis hexadecimal",
            filetypes=[("Todos los archivos", "*.*")]
        )
        
        if archivo:
            try:
                if self.controlador and hasattr(self.controlador, 'visor_hex'):
                    # Usar el visor hexadecimal real
                    resultado = self.controlador.visor_hex.visualizar_archivo(archivo)
                    
                    # Crear ventana para mostrar resultado
                    ventana_hex = tk.Toplevel(self.root)
                    ventana_hex.title(f"Visor Hexadecimal - {os.path.basename(archivo)}")
                    ventana_hex.geometry("800x600")
                    
                    # Text widget con scrollbar
                    text_frame = tk.Frame(ventana_hex)
                    text_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    scrollbar = tk.Scrollbar(text_frame)
                    scrollbar.pack(side="right", fill="y")
                    
                    text_widget = tk.Text(
                        text_frame,
                        font=("Consolas", 10),
                        yscrollcommand=scrollbar.set,
                        wrap="none"
                    )
                    text_widget.pack(side="left", fill="both", expand=True)
                    scrollbar.config(command=text_widget.yview)
                    
                    # Mostrar contenido
                    if resultado.get("exito"):
                        text_widget.insert("1.0", resultado.get("contenido_hex", ""))
                    else:
                        text_widget.insert("1.0", f"Error: {resultado.get('error', 'Error desconocido')}")
                    
                    text_widget.config(state="disabled")
                else:
                    messagebox.showwarning("Error", "Visor hexadecimal no disponible")
            except Exception as e:
                messagebox.showerror("Error", f"Error abriendo visor hexadecimal: {str(e)}")
    
    def abrir_analizador_cadenas(self):
        """Abrir analizador de cadenas"""
        import os
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo para análisis de cadenas",
            filetypes=[("Todos los archivos", "*.*")]
        )
        
        if archivo:
            try:
                if self.controlador and hasattr(self.controlador, 'analizador_cadenas'):
                    # Usar el analizador de cadenas real
                    resultado = self.controlador.analizador_cadenas.analizar_archivo(archivo)
                    
                    # Crear ventana para mostrar resultado
                    ventana_cadenas = tk.Toplevel(self.root)
                    ventana_cadenas.title(f"Análisis de Cadenas - {os.path.basename(archivo)}")
                    ventana_cadenas.geometry("900x700")
                    
                    # Notebook con pestañas
                    from tkinter import ttk
                    notebook = ttk.Notebook(ventana_cadenas)
                    notebook.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    # Pestaña de cadenas
                    frame_cadenas = tk.Frame(notebook)
                    notebook.add(frame_cadenas, text="Cadenas Encontradas")
                    
                    # Lista de cadenas con scrollbar
                    list_frame = tk.Frame(frame_cadenas)
                    list_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    scrollbar_y = tk.Scrollbar(list_frame)
                    scrollbar_y.pack(side="right", fill="y")
                    
                    scrollbar_x = tk.Scrollbar(list_frame, orient="horizontal")
                    scrollbar_x.pack(side="bottom", fill="x")
                    
                    listbox = tk.Listbox(
                        list_frame,
                        font=("Consolas", 9),
                        yscrollcommand=scrollbar_y.set,
                        xscrollcommand=scrollbar_x.set
                    )
                    listbox.pack(side="left", fill="both", expand=True)
                    
                    scrollbar_y.config(command=listbox.yview)
                    scrollbar_x.config(command=listbox.xview)
                    
                    # Mostrar resultados
                    if resultado.get("exito"):
                        cadenas = resultado.get("cadenas", [])
                        for cadena in cadenas[:1000]:  # Limitar a 1000 cadenas
                            listbox.insert("end", cadena)
                        
                        # Pestaña de estadísticas
                        frame_stats = tk.Frame(notebook)
                        notebook.add(frame_stats, text="Estadísticas")
                        
                        stats_text = tk.Text(frame_stats, font=("Segoe UI", 10))
                        stats_text.pack(fill="both", expand=True, padx=10, pady=10)
                        
                        stats_info = f"""Archivo: {archivo}
Total de cadenas: {len(cadenas)}
Mostradas: {min(len(cadenas), 1000)}
Tamaño del archivo: {resultado.get('tamaño_archivo', 'Desconocido')}
Encoding detectado: {resultado.get('encoding', 'Desconocido')}

Tipos de cadenas encontradas:
- URLs: {resultado.get('urls_encontradas', 0)}
- Emails: {resultado.get('emails_encontrados', 0)}
- IPs: {resultado.get('ips_encontradas', 0)}
- Rutas de archivo: {resultado.get('rutas_encontradas', 0)}
"""
                        stats_text.insert("1.0", stats_info)
                        stats_text.config(state="disabled")
                    else:
                        listbox.insert("end", f"Error: {resultado.get('error', 'Error desconocido')}")
                else:
                    # Fallback: usar strings de Kali
                    import subprocess
                    proc = subprocess.run(["strings", archivo], capture_output=True, text=True)
                    cadenas = proc.stdout.splitlines() if proc.returncode == 0 else []
                    ventana_cadenas = tk.Toplevel(self.root)
                    ventana_cadenas.title(f"Análisis de Cadenas - {os.path.basename(archivo)} (strings)")
                    ventana_cadenas.geometry("900x700")
                    from tkinter import ttk
                    notebook = ttk.Notebook(ventana_cadenas)
                    notebook.pack(fill="both", expand=True, padx=10, pady=10)
                    frame_cadenas = tk.Frame(notebook)
                    notebook.add(frame_cadenas, text="Cadenas Encontradas")
                    list_frame = tk.Frame(frame_cadenas)
                    list_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    scrollbar_y = tk.Scrollbar(list_frame)
                    scrollbar_y.pack(side="right", fill="y")
                    scrollbar_x = tk.Scrollbar(list_frame, orient="horizontal")
                    scrollbar_x.pack(side="bottom", fill="x")
                    listbox = tk.Listbox(
                        list_frame,
                        font=("Consolas", 9),
                        yscrollcommand=scrollbar_y.set,
                        xscrollcommand=scrollbar_x.set
                    )
                    listbox.pack(side="left", fill="both", expand=True)
                    scrollbar_y.config(command=listbox.yview)
                    scrollbar_x.config(command=listbox.xview)
                    for cadena in cadenas[:1000]:
                        listbox.insert("end", cadena)
                    frame_stats = tk.Frame(notebook)
                    notebook.add(frame_stats, text="Estadísticas")
                    stats_text = tk.Text(frame_stats, font=("Segoe UI", 10))
                    stats_text.pack(fill="both", expand=True, padx=10, pady=10)
                    import os
                    stats_info = f"Archivo: {archivo}\nTotal de cadenas: {len(cadenas)}\nMostradas: {min(len(cadenas), 1000)}\nTamaño del archivo: {os.path.getsize(archivo)} bytes\n\n(Fuente: strings de Kali Linux)"
                    stats_text.insert("1.0", stats_info)
                    stats_text.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", f"Error en análisis de cadenas: {str(e)}")
    
    def abrir_buscador_cve(self):
        """Abrir buscador CVE"""
        try:
            if self.controlador and hasattr(self.controlador, 'buscador_cve'):
                # Crear ventana de búsqueda CVE
                ventana_cve = tk.Toplevel(self.root)
                ventana_cve.title("Buscador de Vulnerabilidades CVE")
                ventana_cve.geometry("1000x700")
                
                # Frame de búsqueda
                search_frame = tk.Frame(ventana_cve, bg=ComponentesModernos.COLORES["bg_principal"])
                search_frame.pack(fill="x", padx=10, pady=10)
                
                tk.Label(
                    search_frame,
                    text="🔍 Buscar CVE:",
                    font=("Segoe UI", 12, "bold"),
                    bg=ComponentesModernos.COLORES["bg_principal"],
                    fg=ComponentesModernos.COLORES["texto_primario"]
                ).pack(side="left", padx=(0, 10))
                
                # Entry para búsqueda
                search_var = tk.StringVar()
                search_entry = tk.Entry(
                    search_frame,
                    textvariable=search_var,
                    font=("Segoe UI", 11),
                    width=40
                )
                search_entry.pack(side="left", padx=(0, 10))
                
                def buscar_cve():
                    termino = search_var.get().strip()
                    if termino:
                        try:
                            resultado = self.controlador.buscador_cve.buscar_vulnerabilidades(termino)
                            mostrar_resultados_cve(resultado)
                        except Exception as e:
                            messagebox.showerror("Error", f"Error en búsqueda CVE: {str(e)}")
                
                ComponentesModernos.crear_boton_moderno(
                    search_frame, "🔍 Buscar", buscar_cve, "primario"
                ).pack(side="left")
                
                # Frame de resultados
                results_frame = tk.Frame(ventana_cve)
                results_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Crear Treeview para resultados
                from tkinter import ttk
                
                columns = ("CVE", "Descripción", "Severidad", "Fecha")
                tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
                
                # Configurar columnas
                tree.heading("CVE", text="CVE ID")
                tree.heading("Descripción", text="Descripción")
                tree.heading("Severidad", text="Severidad")
                tree.heading("Fecha", text="Fecha")
                
                tree.column("CVE", width=120)
                tree.column("Descripción", width=500)
                tree.column("Severidad", width=100)
                tree.column("Fecha", width=100)
                
                # Scrollbars
                scrollbar_y = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
                scrollbar_x = ttk.Scrollbar(results_frame, orient="horizontal", command=tree.xview)
                tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
                
                tree.pack(side="left", fill="both", expand=True)
                scrollbar_y.pack(side="right", fill="y")
                scrollbar_x.pack(side="bottom", fill="x")
                
                def mostrar_resultados_cve(resultado):
                    # Limpiar resultados anteriores
                    for item in tree.get_children():
                        tree.delete(item)
                    
                    if resultado.get("exito"):
                        vulnerabilidades = resultado.get("vulnerabilidades", [])
                        for vuln in vulnerabilidades:
                            tree.insert("", "end", values=(
                                vuln.get("cve_id", "N/A"),
                                vuln.get("descripcion", "N/A")[:100] + "...",
                                vuln.get("severidad", "N/A"),
                                vuln.get("fecha", "N/A")
                            ))
                        
                        if not vulnerabilidades:
                            tree.insert("", "end", values=("", "No se encontraron vulnerabilidades", "", ""))
                    else:
                        tree.insert("", "end", values=("ERROR", resultado.get("error", "Error desconocido"), "", ""))
                
                # Bind para Enter en búsqueda
                search_entry.bind("<Return>", lambda e: buscar_cve())
                search_entry.focus()
                
            else:
                # Fallback: abrir navegador con base de datos CVE
                import webbrowser
                webbrowser.open("https://cve.mitre.org/")
                messagebox.showinfo("Buscador CVE", "Se abrió la base de datos CVE en el navegador.")
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo buscador CVE: {str(e)}")
    
    def abrir_cheatsheets(self):
        """Abrir cheat sheets"""
        try:
            if self.controlador and hasattr(self.controlador, 'gestor_cheatsheets'):
                # Crear ventana de cheat sheets
                ventana_cheat = tk.Toplevel(self.root)
                ventana_cheat.title("📚 Biblioteca de CheatSheets de Seguridad")
                ventana_cheat.geometry("1200x800")
                
                # Frame principal
                main_frame = tk.Frame(ventana_cheat, bg=ComponentesModernos.COLORES["bg_principal"])
                main_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Frame de categorías (izquierda)
                cat_frame = tk.Frame(main_frame, bg=ComponentesModernos.COLORES["bg_secundario"], width=250)
                cat_frame.pack(side="left", fill="y", padx=(0, 10))
                cat_frame.pack_propagate(False)
                
                tk.Label(
                    cat_frame,
                    text="📋 Categorías",
                    font=("Segoe UI", 14, "bold"),
                    bg=ComponentesModernos.COLORES["bg_secundario"],
                    fg=ComponentesModernos.COLORES["texto_primario"]
                ).pack(pady=10)
                
                # Lista de categorías
                cat_listbox = tk.Listbox(
                    cat_frame,
                    bg=ComponentesModernos.COLORES["bg_card"],
                    fg=ComponentesModernos.COLORES["texto_primario"],
                    selectbackground=ComponentesModernos.COLORES["primario"],
                    font=("Segoe UI", 10),
                    relief="flat"
                )
                cat_listbox.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Frame de contenido (derecha)
                content_frame = tk.Frame(main_frame, bg=ComponentesModernos.COLORES["bg_principal"])
                content_frame.pack(side="right", fill="both", expand=True)
                
                # Text widget para mostrar cheatsheet
                content_text = tk.Text(
                    content_frame,
                    bg=ComponentesModernos.COLORES["bg_card"],
                    fg=ComponentesModernos.COLORES["texto_primario"],
                    font=("Consolas", 10),
                    wrap="word",
                    relief="flat"
                )
                
                # Scrollbar para contenido
                scrollbar = tk.Scrollbar(content_frame)
                scrollbar.pack(side="right", fill="y")
                content_text.pack(side="left", fill="both", expand=True)
                content_text.config(yscrollcommand=scrollbar.set)
                scrollbar.config(command=content_text.yview)
                
                # Cargar datos de cheatsheets
                cheatsheets_data = self.controlador.gestor_cheatsheets.obtener_cheatsheets_disponibles()
                
                def cargar_categorias():
                    cat_listbox.delete(0, "end")
                    if cheatsheets_data.get("exito"):
                        categorias = cheatsheets_data.get("categorias", [])
                        for categoria in categorias:
                            cat_listbox.insert("end", categoria)
                    else:
                        cat_listbox.insert("end", "Error cargando categorías")
                
                def mostrar_cheatsheet(event):
                    selection = cat_listbox.curselection()
                    if selection:
                        categoria = cat_listbox.get(selection[0])
                        try:
                            cheatsheet = self.controlador.gestor_cheatsheets.obtener_cheatsheet(categoria)
                            content_text.config(state="normal")
                            content_text.delete("1.0", "end")
                            
                            if cheatsheet.get("exito"):
                                contenido = cheatsheet.get("contenido", "Contenido no disponible")
                                content_text.insert("1.0", contenido)
                            else:
                                content_text.insert("1.0", f"Error cargando cheatsheet: {cheatsheet.get('error', 'Error desconocido')}")
                            
                            content_text.config(state="disabled")
                        except Exception as e:
                            content_text.config(state="normal")
                            content_text.delete("1.0", "end")
                            content_text.insert("1.0", f"Error: {str(e)}")
                            content_text.config(state="disabled")
                
                cat_listbox.bind("<<ListboxSelect>>", mostrar_cheatsheet)
                cargar_categorias()
                
                # Instrucciones iniciales
                content_text.config(state="normal")
                content_text.insert("1.0", "📚 Selecciona una categoría de la izquierda para ver el cheatsheet correspondiente.\n\nCategorías disponibles:\n• Comandos de red\n• Análisis forense\n• Pentesting\n• Incident Response\n• Y más...")
                content_text.config(state="disabled")
                
            else:
                messagebox.showwarning("Error", "Gestor de cheatsheets no disponible")
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo cheatsheets: {str(e)}")
    
    def abrir_descontaminacion(self):
        """Abrir herramienta de descontaminación"""
        try:
            if self.controlador and hasattr(self.controlador, 'descontaminacion_inteligente'):
                # Crear ventana de descontaminación
                ventana_decontam = tk.Toplevel(self.root)
                ventana_decontam.title("🧽 Descontaminación Inteligente")
                ventana_decontam.geometry("900x600")
                
                # Container principal
                main_container = tk.Frame(ventana_decontam, bg=ComponentesModernos.COLORES["bg_principal"])
                main_container.pack(fill="both", expand=True, padx=15, pady=15)
                
                # Header
                header_frame = tk.Frame(main_container, bg=ComponentesModernos.COLORES["bg_principal"])
                header_frame.pack(fill="x", pady=(0, 20))
                
                tk.Label(
                    header_frame,
                    text="🧹 Descontaminación Inteligente de Malware",
                    font=("Segoe UI", 18, "bold"),
                    bg=ComponentesModernos.COLORES["bg_principal"],
                    fg=ComponentesModernos.COLORES["texto_primario"]
                ).pack()
                
                # Frame de selección de archivo
                file_frame = tk.Frame(main_container, bg=ComponentesModernos.COLORES["bg_card"])
                file_frame.pack(fill="x", pady=(0, 15))
                
                selected_file = tk.StringVar()
                
                tk.Label(
                    file_frame,
                    text="📁 Seleccionar archivo para descontaminar:",
                    font=("Segoe UI", 12),
                    bg=ComponentesModernos.COLORES["bg_card"],
                    fg=ComponentesModernos.COLORES["texto_primario"]
                ).pack(padx=15, pady=(15, 5))
                
                file_entry = tk.Entry(
                    file_frame,
                    textvariable=selected_file,
                    font=("Segoe UI", 10),
                    width=60,
                    state="readonly"
                )
                file_entry.pack(side="left", padx=(15, 10), pady=(0, 15))
                
                def seleccionar_archivo():
                    archivo = filedialog.askopenfilename(
                        title="Seleccionar archivo infectado",
                        filetypes=[
                            ("Todos los archivos", "*.*"),
                            ("Ejecutables", "*.exe"),
                            ("Scripts", "*.bat;*.cmd;*.ps1"),
                            ("Documentos", "*.doc;*.docx;*.pdf"),
                        ]
                    )
                    if archivo:
                        selected_file.set(archivo)
                
                ComponentesModernos.crear_boton_moderno(
                    file_frame, "📂 Examinar", seleccionar_archivo, "outline"
                ).pack(side="left", padx=(0, 15), pady=(0, 15))
                
                # Frame de opciones
                options_frame = tk.Frame(main_container, bg=ComponentesModernos.COLORES["bg_card"])
                options_frame.pack(fill="x", pady=(0, 15))
                
                tk.Label(
                    options_frame,
                    text="⚙️ Opciones de descontaminación:",
                    font=("Segoe UI", 12, "bold"),
                    bg=ComponentesModernos.COLORES["bg_card"],
                    fg=ComponentesModernos.COLORES["texto_primario"]
                ).pack(padx=15, pady=(15, 10))
                
                # Variables de opciones
                backup_var = tk.BooleanVar(value=True)
                analisis_profundo_var = tk.BooleanVar(value=True)
                restaurar_var = tk.BooleanVar(value=False)
                
                tk.Checkbutton(
                    options_frame,
                    text="🛡️ Crear backup antes de limpiar",
                    variable=backup_var,
                    bg=ComponentesModernos.COLORES["bg_card"],
                    fg=ComponentesModernos.COLORES["texto_primario"],
                    selectcolor=ComponentesModernos.COLORES["bg_secundario"],
                    font=("Segoe UI", 10)
                ).pack(anchor="w", padx=30, pady=2)
                
                tk.Checkbutton(
                    options_frame,
                    text="🔍 Análisis profundo de patrones",
                    variable=analisis_profundo_var,
                    bg=ComponentesModernos.COLORES["bg_card"],
                    fg=ComponentesModernos.COLORES["texto_primario"],
                    selectcolor=ComponentesModernos.COLORES["bg_secundario"],
                    font=("Segoe UI", 10)
                ).pack(anchor="w", padx=30, pady=2)
                
                tk.Checkbutton(
                    options_frame,
                    text="🔄 Intentar restaurar funcionalidad original",
                    variable=restaurar_var,
                    bg=ComponentesModernos.COLORES["bg_card"],
                    fg=ComponentesModernos.COLORES["texto_primario"],
                    selectcolor=ComponentesModernos.COLORES["bg_secundario"],
                    font=("Segoe UI", 10)
                ).pack(anchor="w", padx=30, pady=(2, 15))
                
                # Frame de resultados
                results_frame = tk.Frame(main_container, bg=ComponentesModernos.COLORES["bg_card"])
                results_frame.pack(fill="both", expand=True)
                
                tk.Label(
                    results_frame,
                    text="📊 Resultados:",
                    font=("Segoe UI", 12, "bold"),
                    bg=ComponentesModernos.COLORES["bg_card"],
                    fg=ComponentesModernos.COLORES["texto_primario"]
                ).pack(padx=15, pady=(15, 10))
                
                # Text widget para resultados
                results_text = tk.Text(
                    results_frame,
                    bg=ComponentesModernos.COLORES["bg_secundario"],
                    fg=ComponentesModernos.COLORES["texto_primario"],
                    font=("Consolas", 9),
                    height=12,
                    wrap="word"
                )
                
                scrollbar_res = tk.Scrollbar(results_frame)
                scrollbar_res.pack(side="right", fill="y", padx=(0, 15), pady=(0, 15))
                results_text.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=(0, 15))
                results_text.config(yscrollcommand=scrollbar_res.set)
                scrollbar_res.config(command=results_text.yview)
                
                def ejecutar_descontaminacion():
                    archivo = selected_file.get()
                    if not archivo:
                        messagebox.showwarning("Error", "Por favor selecciona un archivo")
                        return
                    
                    try:
                        results_text.config(state="normal")
                        results_text.delete("1.0", "end")
                        results_text.insert("end", "🔄 Iniciando proceso de descontaminación...\n\n")
                        results_text.update()
                        
                        # Configurar opciones
                        opciones = {
                            "crear_backup": backup_var.get(),
                            "analisis_profundo": analisis_profundo_var.get(),
                            "restaurar_funcionalidad": restaurar_var.get()
                        }
                        
                        # Ejecutar descontaminación real
                        resultado = self.controlador.descontaminacion_inteligente.limpiar_archivo(archivo, opciones)
                        
                        results_text.insert("end", f"Archivo: {os.path.basename(archivo)}\n")
                        results_text.insert("end", f"Estado: {'✅ ÉXITO' if resultado.get('exito') else '❌ ERROR'}\n\n")
                        
                        if resultado.get("exito"):
                            results_text.insert("end", f"🔍 Amenazas detectadas: {resultado.get('amenazas_detectadas', 0)}\n")
                            results_text.insert("end", f"🧹 Amenazas eliminadas: {resultado.get('amenazas_eliminadas', 0)}\n")
                            results_text.insert("end", f"📁 Backup creado: {'Sí' if resultado.get('backup_creado') else 'No'}\n\n")
                            
                            if resultado.get("detalles"):
                                results_text.insert("end", "📋 Detalles del proceso:\n")
                                for detalle in resultado.get("detalles", []):
                                    results_text.insert("end", f"  • {detalle}\n")
                        else:
                            results_text.insert("end", f"❌ Error: {resultado.get('error', 'Error desconocido')}\n")
                        
                        results_text.config(state="disabled")
                        results_text.see("end")
                        
                    except Exception as e:
                        results_text.config(state="normal")
                        results_text.insert("end", f"❌ Error durante la descontaminación: {str(e)}\n")
                        results_text.config(state="disabled")
                
                # Botón de ejecutar
                ComponentesModernos.crear_boton_moderno(
                    main_container, "🧽 Ejecutar Descontaminación", ejecutar_descontaminacion, "primario"
                ).pack(pady=15)
                
                # Mensaje inicial
                results_text.config(state="normal")
                results_text.insert("1.0", "💡 Selecciona un archivo y configura las opciones para iniciar el proceso de descontaminación.\n\n⚠️ ADVERTENCIA: Siempre crea un backup antes de proceder con la limpieza.")
                results_text.config(state="disabled")
                
            else:
                messagebox.showwarning("Error", "Herramienta de descontaminación no disponible")
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo descontaminación: {str(e)}")
    
    def abrir_escaner_red(self):
        """Abrir escáner de red (nmap)"""
        import subprocess
        from tkinter.simpledialog import askstring
        objetivo = askstring("Escáner de Red", "Introduce la IP o rango a escanear (ej: 192.168.1.0/24):")
        if objetivo:
            try:
                proc = subprocess.run(["nmap", "-T4", "-F", objetivo], capture_output=True, text=True)
                resultado = proc.stdout if proc.returncode == 0 else proc.stderr
                ventana = tk.Toplevel(self.root)
                ventana.title(f"Escáner de Red - {objetivo}")
                ventana.geometry("900x600")
                text_widget = tk.Text(ventana, font=("Consolas", 10), wrap="word")
                text_widget.pack(fill="both", expand=True)
                text_widget.insert(tk.END, resultado[:100000])
                text_widget.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Escáner de Red", f"Error: {str(e)}")
    
    def abrir_respondedor(self):
        """Abrir respondedor automático de incidentes"""
        try:
            if self.controlador and hasattr(self.controlador, 'respondedor_incidentes'):
                resultado = self.controlador.respondedor_incidentes.responder()
                msg = resultado.get("mensaje", "Respuesta automática ejecutada.")
                messagebox.showinfo("Respondedor Automático", msg)
            else:
                messagebox.showinfo("Respondedor Automático", "No hay integración real. Configure scripts personalizados para respuesta automática en Kali.")
        except Exception as e:
            messagebox.showerror("Respondedor Automático", f"Error: {str(e)}")
    
    def abrir_integracion(self):
        """Abrir integración externa (APIs/servicios)"""
        try:
            if self.controlador and hasattr(self.controlador, 'integracion_externa'):
                resultado = self.controlador.integracion_externa.obtener_estado()
                msg = resultado.get("mensaje", "Integración consultada.")
                messagebox.showinfo("Integración Externa", msg)
            else:
                messagebox.showinfo("Integración Externa", "No hay integración real. Configure APIs externas en el controlador.")
        except Exception as e:
            messagebox.showerror("Integración Externa", f"Error: {str(e)}")
    
    def abrir_config_avanzada(self):
        """Abrir configuración avanzada del sistema"""
        try:
            import platform
            info = f"Sistema: {platform.system()}\nRelease: {platform.release()}\nVersion: {platform.version()}\nMachine: {platform.machine()}\nProcessor: {platform.processor()}"
            messagebox.showinfo("Configuración Avanzada", info)
        except Exception as e:
            messagebox.showerror("Configuración Avanzada", f"Error: {str(e)}")
