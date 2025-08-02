#!/usr/bin/env python3
"""
Vista de Auditoría PAM para Ares Aegis
====================================

Vista especializada para mostrar y gestionar auditorías de autenticación PAM.
Proporciona una interfaz profesional para ejecutar auditorías y visualizar resultados.

Desarrollado exclusivamente para Kali Linux con estilo terminal profesional.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
import threading
from ..componentes_ui.emoticonos_mitologicos import EmoticonosMitologicos
from ..componentes_ui.sistema_ayuda import SistemaAyuda
from ..componentes_ui.colores_kali import ColoresKaliLinux
from datetime import datetime
from typing import Dict, Any, Optional


class VistaAuditoriaPAM:
    """
    Vista especializada para auditorías de autenticación PAM.
    
    Funcionalidades:
    - Ejecutar auditorías PAM completas
    - Ejecutar auditorías de sistema completas 
    - Visualizar resultados en tiempo real
    - Mostrar recomendaciones de seguridad
    - Generar reportes de auditoría
    """
    
    def __init__(self, contenedor_padre, controlador, colores):
        """
        Inicializa la vista de auditoría PAM.
        
        Args:
            contenedor_padre: Contenedor principal donde se creará la vista
            controlador: Instancia del controlador 
            colores: Esquema de colores
        """
        self.contenedor_padre = contenedor_padre
        self.controlador = controlador
        self.colores = colores
        self.logger = logging.getLogger(__name__)
        
        # Componentes UI
        self.emoticonos = EmoticonosMitologicos()
        
        # Sistema de ayuda
        self.sistema_ayuda = SistemaAyuda(colores)
        
        # Estado de la vista
        self.auditoria_en_progreso = False
        self.ultimo_resultado = None
        
        # Referencias a widgets inicializadas correctamente
        self.contenedor = None  # Se inicializa en crear_vista
        self.area_resultados = None  # Se inicializa en _crear_area_resultados
        self.area_log = None  # Se inicializa en _crear_area_log
        self.btn_auditoria_pam = None  # Se inicializa en _crear_panel_control
        self.btn_auditoria_completa = None  # Se inicializa en _crear_panel_control
        self.btn_cancelar = None  # Se inicializa en _crear_panel_control
        self.label_estado = None  # Se inicializa en _crear_panel_control
        self.progress_bar = None  # Se inicializa en _crear_panel_control
        
        # Control de auditoría
        self.auditoria_activa = False
        self.thread_auditoria = None
        
        # Sistema de ayuda
        self.sistema_ayuda = SistemaAyuda(self.colores)
        
    def mostrar_informacion(self):
        """Mostrar información de ayuda sobre la Auditoría PAM"""
        info_text = """🛡️ AUDITORÍA PAM - SISTEMA DE AUTENTICACIÓN

🔐 FUNCIONALIDADES PRINCIPALES:
• Auditoría completa del sistema PAM (Pluggable Authentication Modules)
• Análisis exhaustivo de configuraciones de autenticación
• Verificación de políticas de contraseñas y seguridad
• Detección proactiva de vulnerabilidades de autenticación

⚡ MÓDULOS AUDITADOS:
• Configuración PAM del sistema (/etc/pam.d/)
• Políticas de contraseñas (pam_pwquality)
• Módulos de autenticación activos y su estado
• Configuraciones de sudo y su para escalada de privilegios
• Análisis de todos los archivos en /etc/pam.d/

🎯 ANÁLISIS DE SEGURIDAD:
• Evaluación de la fortaleza de políticas de contraseñas
• Verificación de configuraciones de bloqueo de cuentas
• Detección de módulos de autenticación obsoletos o inseguros
• Identificación de configuraciones inseguras o mal configuradas
• Verificación del cumplimiento con estándares de seguridad

🔧 TIPOS DE AUDITORÍA:
• Auditoría PAM: Análisis específico del sistema de autenticación
• Auditoría Completa: Análisis integral del sistema incluyendo PAM
• Verificación en tiempo real del estado de configuraciones
• Generación automática de reportes detallados

⚠️ DETECCIÓN DE VULNERABILIDADES:
• Configuraciones PAM potencialmente inseguras
• Políticas de contraseñas débiles o inadecuadas
• Módulos PAM desactualizados con vulnerabilidades conocidas
• Configuraciones de sudo peligrosas que permiten escalada
• Accesos privilegiados sin restricciones adecuadas

📊 RESULTADOS DETALLADOS:
• Estado individual de cada módulo PAM
• Análisis detallado de configuraciones críticas
• Recomendaciones específicas de mejora para cada hallazgo
• Clasificación de nivel de riesgo por hallazgo detectado
• Pasos detallados de mitigación recomendados

💡 RECOMENDACIONES INCLUIDAS:
• Fortalecimiento de políticas de contraseñas según mejores prácticas
• Configuraciones PAM más seguras y actualizadas
• Implementación de autenticación multifactor (MFA)
• Mejores prácticas de configuración sudo y su
• Monitoreo continuo de eventos de autenticación

🔐 ESPECÍFICO PARA KALI LINUX:
• Análisis adaptado a distribuciones basadas en Debian
• Verificación de módulos PAM específicos de Kali Linux
• Integración con herramientas de auditoría nativas
• Optimización para entornos de pentesting y seguridad
• Compatibilidad completa con el ecosistema de Kali Linux

🚀 CÓMO UTILIZAR:
1. Selecciona el tipo de auditoría deseada (PAM o Completa)
2. Haz clic en el botón correspondiente para iniciar
3. Observa el progreso en tiempo real en el panel de logs
4. Revisa los resultados detallados en el panel de resultados
5. Implementa las recomendaciones de seguridad sugeridas

⏱️ FUNCIONES DE CONTROL:
• Botón Cancelar: Detiene la auditoría en progreso de forma segura
• Progreso en tiempo real: Visualización del estado actual
• Logs detallados: Seguimiento paso a paso del proceso"""
        
        messagebox.showinfo("Información - Auditoría PAM", info_text)
        
    def crear_vista(self, area_contenido=None):
        """
        Crea la vista completa de auditoría PAM.
        
        Args:
            area_contenido: Área de contenido opcional (para compatibilidad)
        """
        # Limpiar contenedor padre
        for widget in self.contenedor_padre.winfo_children():
            widget.destroy()
        
        # Frame principal con padding estandarizado
        self.frame_principal = tk.Frame(self.contenedor_padre, bg=self.colores.fondo_secundario)
        self.frame_principal.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Configurar grid con mejores proporciones
        self.frame_principal.grid_rowconfigure(0, weight=0)  # Header fijo
        self.frame_principal.grid_rowconfigure(1, weight=1)  # Área principal expandible
        self.frame_principal.grid_rowconfigure(2, weight=0)  # Barra estado fija
        self.frame_principal.grid_columnconfigure(0, weight=1)
        
        # Crear componentes
        self._crear_cabecera()
        self._crear_area_principal()
        self._crear_barra_estado()
        
        self.logger.info("Vista de Auditoría PAM creada exitosamente")
        
    def _crear_cabecera(self):
        """Crea la cabecera con título y controles principales."""
        cabecera = tk.Frame(self.frame_principal, bg=self.colores.negro_carbono, height=90)
        cabecera.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        cabecera.grid_propagate(False)
        cabecera.grid_columnconfigure(0, weight=0)
        cabecera.grid_columnconfigure(1, weight=1)
        cabecera.grid_columnconfigure(2, weight=0)
        
        # Título principal
        titulo_frame = tk.Frame(cabecera, bg=self.colores.negro_carbono)
        titulo_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        tk.Label(titulo_frame,
                text="🔐 AUDITORÍA DE AUTENTICACIÓN PAM",
                font=('Consolas', 16, 'bold'),
                fg=self.colores.naranja_fuego,
                bg=self.colores.negro_carbono).pack(anchor='w')
        
        tk.Label(titulo_frame,
                text="Sistema Avanzado de Análisis de Configuración de Autenticación",
                font=('Consolas', 10),
                fg=self.colores.gris_platino,
                bg=self.colores.negro_carbono).pack(anchor='w')
        
        # Botones de acción principales
        botones_frame = tk.Frame(cabecera, bg=self.colores.negro_carbono)
        botones_frame.grid(row=0, column=1, sticky="e", padx=20, pady=10)
        
        # Botón de información
        tk.Button(cabecera,
                 text="❓ Info",
                 font=('Consolas', 10),
                 bg=self.colores.naranja_fuego,
                 fg=self.colores.negro_carbono,
                 command=self.mostrar_informacion,
                 relief='flat',
                 padx=10,
                 pady=5).grid(row=0, column=2, padx=20, sticky='e')
        
        self.btn_auditoria_pam = tk.Button(botones_frame,
                                          text="🔍 AUDITORÍA PAM",
                                          command=self._ejecutar_auditoria_pam,
                                          bg=self.colores.azul_electrico,
                                          fg=self.colores.texto_primario,
                                          font=('Consolas', 11, 'bold'),
                                          relief='flat',
                                          padx=20, pady=8,
                                          cursor='hand2')
        self.btn_auditoria_pam.pack(side='left', padx=(0, 10))
        
        self.btn_auditoria_completa = tk.Button(botones_frame,
                                               text="🛡️ AUDITORÍA COMPLETA",
                                               command=self._ejecutar_auditoria_completa,
                                               bg=self.colores.rojo_critico,
                                               fg=self.colores.texto_primario,
                                               font=('Consolas', 11, 'bold'),
                                               relief='flat',
                                               padx=20, pady=8,
                                               cursor='hand2')
        self.btn_auditoria_completa.pack(side='left', padx=(0, 10))
        
        # Botón de cancelar auditoría
        self.btn_cancelar = tk.Button(botones_frame,
                                     text="❌ CANCELAR",
                                     command=self._cancelar_auditoria,
                                     bg=self.colores.gris_hierro,
                                     fg=self.colores.texto_primario,
                                     font=('Consolas', 11, 'bold'),
                                     relief='flat',
                                     padx=20, pady=8,
                                     cursor='hand2',
                                     state='disabled')
        self.btn_cancelar.pack(side='left')
        
        # Efectos hover
        self._agregar_efecto_hover(self.btn_auditoria_pam, self.colores.azul_electrico)
        self._agregar_efecto_hover(self.btn_auditoria_completa, self.colores.rojo_critico)
        self._agregar_efecto_hover(self.btn_cancelar, self.colores.gris_hierro)
    
    def _crear_area_principal(self):
        """Crea el área principal con paneles de resultados y logs."""
        area_principal = tk.Frame(self.frame_principal, bg=self.colores.fondo_secundario)
        area_principal.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configurar grid para layout responsive
        area_principal.grid_rowconfigure(0, weight=1)
        area_principal.grid_columnconfigure(0, weight=1)
        area_principal.grid_columnconfigure(1, weight=1)
        
        # Panel izquierdo: Resultados de auditoría
        self._crear_panel_resultados(area_principal)
        
        # Panel derecho: Logs y estado
        self._crear_panel_logs(area_principal)
    
    def _crear_panel_resultados(self, padre):
        """Crea el panel de resultados de auditoría."""
        panel_resultados = tk.LabelFrame(padre,
                                        text="📊 RESULTADOS DE AUDITORÍA",
                                        bg=self.colores.gris_pizarra,
                                        fg=self.colores.cyan_brillante,
                                        font=('Consolas', 12, 'bold'),
                                        relief='flat',
                                        bd=2)
        panel_resultados.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
        
        # Configurar scrollbar
        canvas = tk.Canvas(panel_resultados, bg=self.colores.gris_pizarra, highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(panel_resultados, orient="vertical", command=canvas.yview)
        self.area_resultados = tk.Frame(canvas, bg=self.colores.gris_pizarra)
        
        canvas.configure(yscrollcommand=scrollbar_y.set)
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar_y.pack(side="right", fill="y")
        
        canvas_window = canvas.create_window((0, 0), window=self.area_resultados, anchor="nw")
        
        # Configurar scroll dinámico
        def _configurar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
        
        self.area_resultados.bind("<Configure>", _configurar_scroll)
        canvas.bind("<Configure>", _configurar_scroll)
        
        # Mostrar mensaje inicial
        self._mostrar_mensaje_inicial()
    
    def _crear_panel_logs(self, padre):
        """Crea el panel de logs y estado."""
        panel_logs = tk.LabelFrame(padre,
                                  text="📝 LOGS DE AUDITORÍA",
                                  bg=self.colores.gris_pizarra,
                                  fg=self.colores.amarillo_medio,
                                  font=('Consolas', 12, 'bold'),
                                  relief='flat',
                                  bd=2)
        panel_logs.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
        
        # Configurar grid
        panel_logs.grid_rowconfigure(0, weight=1)
        panel_logs.grid_columnconfigure(0, weight=1)
        
        # Área de texto para logs
        self.area_log = scrolledtext.ScrolledText(panel_logs,
                                                 bg=self.colores.negro_carbono,
                                                 fg=self.colores.verde_terminal,
                                                 font=('Consolas', 9),
                                                 wrap=tk.WORD,
                                                 height=25,
                                                 state=tk.DISABLED)
        self.area_log.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configurar colores para diferentes tipos de mensajes
        self.area_log.tag_configure("INFO", foreground=self.colores.cyan_brillante)
        self.area_log.tag_configure("WARNING", foreground=self.colores.amarillo_medio)
        self.area_log.tag_configure("ERROR", foreground=self.colores.rojo_critico)
        self.area_log.tag_configure("SUCCESS", foreground=self.colores.verde_terminal)
        self.area_log.tag_configure("CRITICAL", foreground=self.colores.naranja_fuego, font=('Consolas', 9, 'bold'))
        
        # Mensaje inicial
        self._agregar_log("Sistema de auditoría PAM inicializado", "INFO")
        self._agregar_log("Listo para ejecutar auditorías de seguridad", "SUCCESS")
    
    def _crear_barra_estado(self):
        """Crea la barra de estado inferior."""
        barra_estado = tk.Frame(self.frame_principal, bg=self.colores.negro_carbono, height=40)
        barra_estado.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        barra_estado.grid_propagate(False)
        barra_estado.grid_columnconfigure(1, weight=1)
        
        # Estado actual
        self.label_estado = tk.Label(barra_estado,
                                    text="💤 Sistema en espera - Listo para auditoría",
                                    font=('Consolas', 10),
                                    fg=self.colores.gris_platino,
                                    bg=self.colores.negro_carbono)
        self.label_estado.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(barra_estado,
                                           mode='indeterminate',
                                           length=200)
        self.progress_bar.grid(row=0, column=1, sticky="e", padx=20, pady=10)
    
    def _mostrar_mensaje_inicial(self):
        """Muestra mensaje inicial en el área de resultados."""
        mensaje_frame = tk.Frame(self.area_resultados, bg=self.colores.gris_pizarra)
        mensaje_frame.pack(fill='both', expand=True, padx=20, pady=50)
        
        tk.Label(mensaje_frame,
                text="🔐 SISTEMA DE AUDITORÍA PAM",
                font=('Consolas', 18, 'bold'),
                fg=self.colores.naranja_fuego,
                bg=self.colores.gris_pizarra).pack(pady=20)
        
        tk.Label(mensaje_frame,
                text="Selecciona una opción de auditoría para comenzar:",
                font=('Consolas', 12),
                fg=self.colores.texto_primario,
                bg=self.colores.gris_pizarra).pack(pady=10)
        
        # Información sobre tipos de auditoría
        info_frame = tk.Frame(mensaje_frame, bg=self.colores.gris_hierro, relief='flat', bd=1)
        info_frame.pack(fill='x', pady=20, padx=40)
        
        auditorias_info = [
            ("🔍 AUDITORÍA PAM", "Analiza configuración de autenticación PAM"),
            ("🛡️ AUDITORÍA COMPLETA", "Analiza PAM + sistema + servicios expuestos")
        ]
        
        for titulo, descripcion in auditorias_info:
            item_frame = tk.Frame(info_frame, bg=self.colores.gris_hierro)
            item_frame.pack(fill='x', padx=15, pady=10)
            
            tk.Label(item_frame,
                    text=titulo,
                    font=('Consolas', 11, 'bold'),
                    fg=self.colores.cyan_brillante,
                    bg=self.colores.gris_hierro).pack(anchor='w')
            
            tk.Label(item_frame,
                    text=descripcion,
                    font=('Consolas', 9),
                    fg=self.colores.gris_platino,
                    bg=self.colores.gris_hierro).pack(anchor='w', padx=20)
    
    def _ejecutar_auditoria_pam(self):
        """Ejecuta auditoría PAM exclusiva."""
        if self.auditoria_activa:
            messagebox.showwarning("Auditoría en Progreso", 
                                 "Ya hay una auditoría en ejecución. Espera a que termine.")
            return
        
        self._iniciar_auditoria("PAM")
        
        # Ejecutar en hilo separado
        self.thread_auditoria = threading.Thread(target=self._ejecutar_auditoria_pam_hilo, daemon=True)
        self.thread_auditoria.start()
    
    def _ejecutar_auditoria_completa(self):
        """Ejecuta auditoría completa del sistema."""
        if self.auditoria_activa:
            messagebox.showwarning("Auditoría en Progreso", 
                                 "Ya hay una auditoría en ejecución. Espera a que termine.")
            return
        
        self._iniciar_auditoria("COMPLETA")
        
        # Ejecutar en hilo separado
        self.thread_auditoria = threading.Thread(target=self._ejecutar_auditoria_completa_hilo, daemon=True)
        self.thread_auditoria.start()
    
    def _cancelar_auditoria(self):
        """Cancela la auditoría en progreso."""
        if not self.auditoria_activa:
            return
            
        respuesta = messagebox.askyesno("Cancelar Auditoría", 
                                       "¿Estás seguro de que quieres cancelar la auditoría en progreso?")
        if respuesta:
            self.auditoria_activa = False
            
            # Esperar a que el hilo termine si está ejecutándose
            if self.thread_auditoria and self.thread_auditoria.is_alive():
                self._agregar_log("⏳ Esperando finalización del hilo de auditoría...", "INFO")
                # No hacemos join() para evitar bloquear la UI, solo marcamos como inactiva
            
            self._finalizar_auditoria()
            self._agregar_log("❌ Auditoría cancelada por el usuario", "ERROR")
            messagebox.showinfo("Auditoría Cancelada", "La auditoría ha sido cancelada exitosamente.")
    
    def _iniciar_auditoria(self, tipo):
        """Configura la interfaz para inicio de auditoría."""
        self.auditoria_activa = True
        
        # Verificar que los widgets estén inicializados individualmente
        if not self.btn_auditoria_pam:
            self.logger.warning("btn_auditoria_pam no inicializado")
            return
        if not self.btn_auditoria_completa:
            self.logger.warning("btn_auditoria_completa no inicializado")
            return
        if not self.btn_cancelar:
            self.logger.warning("btn_cancelar no inicializado")
            return
        if not self.progress_bar:
            self.logger.warning("progress_bar no inicializado")
            return
        if not self.label_estado:
            self.logger.warning("label_estado no inicializado")
            return
        
        # Deshabilitar botones de auditoría y habilitar cancelar
        self.btn_auditoria_pam.config(state='disabled')
        self.btn_auditoria_completa.config(state='disabled')
        
        # Habilitar botón de cancelar
        if self.btn_cancelar:
            self.btn_cancelar.config(state='normal', bg=self.colores.rojo_critico)
        
        # Activar barra de progreso
        self.progress_bar.start(10)
        
        # Actualizar estado
        self.label_estado.config(text=f"🔥 Ejecutando auditoría {tipo}...", 
                                fg=self.colores.naranja_fuego)
        
        # Limpiar resultados anteriores
        self._limpiar_area_resultados()
        
        # Log inicial
        self._agregar_log(f"Iniciando auditoría {tipo}...", "INFO")
    
    def _ejecutar_auditoria_pam_hilo(self):
        """Ejecuta auditoría PAM en hilo separado."""
        try:
            if not self.auditoria_activa:
                return
                
            self._agregar_log("🔐 Iniciando auditoría específica de PAM...", "INFO")
            self._agregar_log("📋 Analizando configuraciones de autenticación...", "INFO")
            
            if not self.auditoria_activa:
                return
            
            import time
            time.sleep(0.3)
            self._agregar_log("🔍 Verificando módulos PAM del sistema...", "INFO")
            
            if not self.auditoria_activa:
                return
            
            time.sleep(0.3)
            self._agregar_log("🔧 Analizando políticas de contraseñas...", "INFO")
            time.sleep(0.3)
            self._agregar_log("🛡️ Verificando configuraciones de seguridad...", "INFO")
                
            resultado = self.controlador.iniciar_auditoria_pam()
            
            if not self.auditoria_activa:
                return
            
            if resultado.get('exito', False):
                self._agregar_log("✅ Auditoría PAM completada exitosamente", "SUCCESS")
                self._mostrar_resultados_pam(resultado)
            else:
                error = resultado.get('error', 'Error desconocido')
                self._agregar_log(f"❌ Error en auditoría PAM: {error}", "ERROR")
                self._mostrar_error(error)
                
        except Exception as e:
            if self.auditoria_activa:
                self._agregar_log(f"💥 Excepción durante auditoría PAM: {e}", "ERROR")
                self._mostrar_error(str(e))
        finally:
            if self.auditoria_activa:
                self._finalizar_auditoria()
    
    def _ejecutar_auditoria_completa_hilo(self):
        """Ejecuta auditoría completa en hilo separado."""
        try:
            if not self.auditoria_activa:
                return
                
            self._agregar_log("Iniciando auditoría completa del sistema...", "INFO")
            
            if not self.auditoria_activa:
                return
                
            resultado = self.controlador.iniciar_auditoria_completa()
            
            if not self.auditoria_activa:
                return
            
            if resultado.get('exito', False):
                self._agregar_log("Auditoría completa exitosa", "SUCCESS")
                self._mostrar_resultados_completos(resultado)
            else:
                error = resultado.get('error', 'Error desconocido')
                self._agregar_log(f"Error en auditoría completa: {error}", "ERROR")
                self._mostrar_error(error)
                
        except Exception as e:
            if self.auditoria_activa:
                self._agregar_log(f"Excepción durante auditoría completa: {e}", "ERROR")
                self._mostrar_error(str(e))
        finally:
            if self.auditoria_activa:
                self._finalizar_auditoria()
    
    def _mostrar_resultados_pam(self, resultado):
        """Muestra los resultados de auditoría PAM."""
        self.frame_principal.after(0, lambda: self._mostrar_resultados_pam_ui(resultado))
    
    def _mostrar_resultados_completos(self, resultado):
        """Muestra los resultados de auditoría completa."""
        self.frame_principal.after(0, lambda: self._mostrar_resultados_completos_ui(resultado))
    
    def _mostrar_resultados_pam_ui(self, resultado):
        """Muestra resultados PAM en la UI."""
        # Resumen principal
        resumen_frame = tk.Frame(self.area_resultados, bg=self.colores.gris_hierro, relief='solid', bd=1)
        resumen_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(resumen_frame,
                text="🔐 RESULTADOS AUDITORÍA PAM",
                font=('Consolas', 14, 'bold'),
                fg=self.colores.naranja_fuego,
                bg=self.colores.gris_hierro).pack(pady=10)
        
        # Estadísticas generales
        stats_frame = tk.Frame(resumen_frame, bg=self.colores.gris_hierro)
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        clasificacion = resultado.get('clasificacion', {})
        stats = [
            ("Total de Hallazgos", resultado.get('total_hallazgos', 0), self.colores.texto_primario),
            ("Críticos", clasificacion.get('criticos', 0), self.colores.rojo_critico),
            ("Altos", clasificacion.get('altos', 0), self.colores.naranja_fuego),
            ("Medios", clasificacion.get('medios', 0), self.colores.amarillo_medio),
            ("Bajos", clasificacion.get('bajos', 0), self.colores.verde_terminal)
        ]
        
        for nombre, valor, color in stats:
            stat_row = tk.Frame(stats_frame, bg=self.colores.gris_hierro)
            stat_row.pack(fill='x', pady=2)
            
            tk.Label(stat_row, text=f"{nombre}:", font=('Consolas', 10), 
                    fg=self.colores.gris_platino, bg=self.colores.gris_hierro).pack(side='left')
            
            tk.Label(stat_row, text=str(valor), font=('Consolas', 10, 'bold'), 
                    fg=color, bg=self.colores.gris_hierro).pack(side='right')
        
        # Hallazgos detallados
        if resultado.get('hallazgos_detallados'):
            self._mostrar_hallazgos_detallados(resultado['hallazgos_detallados'])
    
    def _mostrar_resultados_completos_ui(self, resultado):
        """Muestra resultados de auditoría completa en la UI."""
        # Resumen ejecutivo
        resumen_frame = tk.Frame(self.area_resultados, bg=self.colores.gris_hierro, relief='solid', bd=1)
        resumen_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(resumen_frame,
                text="🛡️ AUDITORÍA COMPLETA DE SEGURIDAD",
                font=('Consolas', 14, 'bold'),
                fg=self.colores.naranja_fuego,
                bg=self.colores.gris_hierro).pack(pady=10)
        
        # Resumen ejecutivo
        if resultado.get('resumen_ejecutivo'):
            resumen_text = tk.Text(resumen_frame, height=6, bg=self.colores.negro_carbono,
                                 fg=self.colores.texto_primario, font=('Consolas', 9),
                                 wrap=tk.WORD, state=tk.DISABLED)
            resumen_text.pack(fill='x', padx=20, pady=10)
            
            resumen_text.config(state=tk.NORMAL)
            resumen_text.insert(tk.END, resultado['resumen_ejecutivo'])
            resumen_text.config(state=tk.DISABLED)
        
        # Métricas principales
        metricas_frame = tk.Frame(resumen_frame, bg=self.colores.gris_hierro)
        metricas_frame.pack(fill='x', padx=20, pady=10)
        
        metricas = [
            ("Duración", f"{resultado.get('duracion_segundos', 0):.1f}s", self.colores.cyan_brillante),
            ("Total Hallazgos", resultado.get('total_hallazgos', 0), self.colores.texto_primario),
            ("Críticos", resultado.get('hallazgos_criticos', 0), self.colores.rojo_critico),
            ("Altos", resultado.get('hallazgos_altos', 0), self.colores.naranja_fuego)
        ]
        
        for nombre, valor, color in metricas:
            metrica_row = tk.Frame(metricas_frame, bg=self.colores.gris_hierro)
            metrica_row.pack(fill='x', pady=2)
            
            tk.Label(metrica_row, text=f"{nombre}:", font=('Consolas', 10), 
                    fg=self.colores.gris_platino, bg=self.colores.gris_hierro).pack(side='left')
            
            tk.Label(metrica_row, text=str(valor), font=('Consolas', 10, 'bold'), 
                    fg=color, bg=self.colores.gris_hierro).pack(side='right')
        
        # Recomendaciones
        if resultado.get('recomendaciones'):
            self._mostrar_recomendaciones(resultado['recomendaciones'])
    
    def _mostrar_hallazgos_detallados(self, hallazgos):
        """Muestra hallazgos detallados."""
        hallazgos_frame = tk.LabelFrame(self.area_resultados,
                                       text="📋 HALLAZGOS DETALLADOS",
                                       bg=self.colores.gris_pizarra,
                                       fg=self.colores.cyan_brillante,
                                       font=('Consolas', 11, 'bold'))
        hallazgos_frame.pack(fill='x', padx=10, pady=10)
        
        for i, hallazgo in enumerate(hallazgos[:10]):  # Mostrar solo los primeros 10
            hallazgo_item = tk.Frame(hallazgos_frame, bg=self.colores.gris_hierro, relief='flat', bd=1)
            hallazgo_item.pack(fill='x', padx=10, pady=5)
            
            # Color según prioridad
            color_prioridad = {
                'CRITICA': self.colores.rojo_critico,
                'ALTA': self.colores.naranja_fuego,
                'MEDIA': self.colores.amarillo_medio,
                'BAJA': self.colores.verde_terminal
            }.get(hallazgo.get('prioridad', 'MEDIA'), self.colores.texto_primario)
            
            # Tipo y prioridad
            header = tk.Frame(hallazgo_item, bg=self.colores.gris_hierro)
            header.pack(fill='x', padx=10, pady=5)
            
            tk.Label(header, text=f"[{hallazgo.get('tipo', 'General')}]",
                    font=('Consolas', 9, 'bold'), fg=self.colores.cyan_brillante,
                    bg=self.colores.gris_hierro).pack(side='left')
            
            tk.Label(header, text=hallazgo.get('prioridad', 'MEDIA'),
                    font=('Consolas', 9, 'bold'), fg=color_prioridad,
                    bg=self.colores.gris_hierro).pack(side='right')
            
            # Descripción
            tk.Label(hallazgo_item, text=hallazgo.get('descripcion', 'Sin descripción'),
                    font=('Consolas', 9), fg=self.colores.texto_primario,
                    bg=self.colores.gris_hierro, wraplength=600, justify='left').pack(
                    fill='x', padx=10, pady=2)
            
            # Archivo afectado
            if hallazgo.get('archivo_afectado'):
                tk.Label(hallazgo_item, text=f"Archivo: {hallazgo['archivo_afectado']}",
                        font=('Consolas', 8), fg=self.colores.gris_platino,
                        bg=self.colores.gris_hierro).pack(fill='x', padx=10, pady=2)
            
            # Recomendación
            if hallazgo.get('recomendacion'):
                tk.Label(hallazgo_item, text=f"💡 {hallazgo['recomendacion']}",
                        font=('Consolas', 8), fg=self.colores.amarillo_medio,
                        bg=self.colores.gris_hierro, wraplength=600, justify='left').pack(
                        fill='x', padx=10, pady=2)
    
    def _mostrar_recomendaciones(self, recomendaciones):
        """Muestra recomendaciones de seguridad."""
        rec_frame = tk.LabelFrame(self.area_resultados,
                                 text="💡 RECOMENDACIONES PRIORITARIAS",
                                 bg=self.colores.gris_pizarra,
                                 fg=self.colores.amarillo_medio,
                                 font=('Consolas', 11, 'bold'))
        rec_frame.pack(fill='x', padx=10, pady=10)
        
        for recomendacion in recomendaciones:
            rec_item = tk.Frame(rec_frame, bg=self.colores.gris_hierro)
            rec_item.pack(fill='x', padx=10, pady=3)
            
            tk.Label(rec_item, text="•", font=('Consolas', 10, 'bold'),
                    fg=self.colores.amarillo_medio, bg=self.colores.gris_hierro).pack(side='left')
            
            tk.Label(rec_item, text=recomendacion, font=('Consolas', 9),
                    fg=self.colores.texto_primario, bg=self.colores.gris_hierro,
                    wraplength=600, justify='left').pack(side='left', fill='x', expand=True, padx=10)
    
    def _mostrar_error(self, error_msg):
        """Muestra mensaje de error."""
        self.frame_principal.after(0, lambda: self._mostrar_error_ui(error_msg))
    
    def _mostrar_error_ui(self, error_msg):
        """Muestra error en la UI."""
        error_frame = tk.Frame(self.area_resultados, bg=self.colores.rojo_critico, relief='solid', bd=2)
        error_frame.pack(fill='x', padx=10, pady=20)
        
        tk.Label(error_frame,
                text="❌ ERROR EN AUDITORÍA",
                font=('Consolas', 14, 'bold'),
                fg=self.colores.texto_primario,
                bg=self.colores.rojo_critico).pack(pady=10)
        
        tk.Label(error_frame,
                text=error_msg,
                font=('Consolas', 10),
                fg=self.colores.texto_primario,
                bg=self.colores.rojo_critico,
                wraplength=600).pack(padx=20, pady=10)
    
    def _finalizar_auditoria(self):
        """Finaliza la auditoría y restaura la interfaz."""
        if self.contenedor:
            self.contenedor.after(0, self._finalizar_auditoria_ui)
        else:
            self.logger.warning("Contenedor no inicializado, llamando directamente _finalizar_auditoria_ui")
            self._finalizar_auditoria_ui()
    
    def _finalizar_auditoria_ui(self):
        """Finaliza auditoría en UI thread."""
        self.auditoria_activa = False
        
        # Verificar que los widgets estén inicializados individualmente
        if self.btn_auditoria_pam:
            self.btn_auditoria_pam.config(state='normal')
        if self.btn_auditoria_completa:
            self.btn_auditoria_completa.config(state='normal')
        
        # Deshabilitar botón de cancelar
        if self.btn_cancelar:
            self.btn_cancelar.config(state='disabled', bg=self.colores.gris_hierro)
        
        # Detener barra de progreso
        if self.progress_bar:
            self.progress_bar.stop()
        
        # Actualizar estado
        if self.label_estado:
            self.label_estado.config(text="✅ Auditoría completada - Sistema listo", 
                                    fg=self.colores.verde_terminal)
        
        self._agregar_log("Auditoría finalizada", "SUCCESS")
    
    def _limpiar_area_resultados(self):
        """Limpia el área de resultados."""
        if not self.area_resultados:
            self.logger.warning("area_resultados no inicializada, omitiendo limpieza")
            return
            
        for widget in self.area_resultados.winfo_children():
            widget.destroy()
    
    def _agregar_log(self, mensaje, tipo="INFO"):
        """Agrega mensaje al área de logs."""
        def agregar():
            if not self.area_log:
                self.logger.warning("area_log no inicializada, omitiendo mensaje de log")
                return
                
            timestamp = datetime.now().strftime("%H:%M:%S")
            linea = f"[{timestamp}] {mensaje}\n"
            
            self.area_log.config(state=tk.NORMAL)
            self.area_log.insert(tk.END, linea, tipo)
            self.area_log.see(tk.END)
            self.area_log.config(state=tk.DISABLED)
        
        if self.contenedor:
            self.contenedor.after(0, agregar)
        else:
            self.logger.warning("Contenedor no inicializado, omitiendo log")
    
    def _agregar_efecto_hover(self, boton, color_original):
        """Agrega efectos hover a un botón."""
        def on_enter(e):
            boton.config(bg=self._color_mas_claro(color_original))
        
        def on_leave(e):
            boton.config(bg=color_original)
        
        boton.bind("<Enter>", on_enter)
        boton.bind("<Leave>", on_leave)
    
    def _color_mas_claro(self, color):
        """Retorna una versión más clara de un color."""
        return {
            self.colores.azul_electrico: "#4A90E2",
            self.colores.rojo_critico: "#E74C3C"
        }.get(color, color)
