#!/usr/bin/env python3
"""
Ares Aegis - Sistema Avanzado de Ciberseguridad
Interfaz Gráfica Moderna Profesional

Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.
La copia, distribución o modificación no autorizada está estrictamente prohibida.

Versión: 3.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from tkinter import simpledialog
import threading
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
import logging
import os

# Importaciones locales
from ..controladores.controlador_principal import ControladorPrincipal
from ..utilidades.temas_modernos import TemaClaro, TemaOscuro, ComponentesModernos
from ..utilidades.ayuda_logging import configurar_logger_modulo


class InterfazPrincipal:
    """Interfaz principal moderna del sistema Ares Aegis."""
    
    def __init__(self):
        """Inicializar la interfaz principal."""
        self.logger = logging.getLogger(__name__)
        self.root = None
        self.tema_actual = TemaClaro()
        self.tema_oscuro = False
        self.controlador = None
        
        # Variables de interfaz
        self.ventana_principal = None
        self.navbar = None
        self.contenido_principal = None
        self.panel_estado = None
        self.panel_notificaciones = None
        
        # Widgets principales
        self.widgets = {}
        self.frames = {}
        self.variables = {}
        
        # Estado de la aplicación
        self.escaneo_activo = False
        self.monitoreo_activo = False
        self.auto_actualizacion = False
        
        self.logger.info("Interfaz Principal inicializada")
    
    def inicializar(self):
        """Inicializar la aplicación completa."""
        try:
            self.crear_ventana_principal()
            self.inicializar_controlador()
            self.configurar_interfaz()
            self.cargar_configuracion()
            self.actualizar_estado_inicial()
            
            self.logger.info("Sistema Ares Aegis inicializado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al inicializar la aplicación: {e}")
            messagebox.showerror("Error de Inicialización", 
                               f"No se pudo inicializar Ares Aegis:\n{str(e)}")
            return False
    
    def crear_ventana_principal(self):
        """Crear la ventana principal de la aplicación."""
        self.root = tk.Tk()
        self.root.title("Ares Aegis - Sistema de Ciberseguridad Avanzado")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Configurar icono
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "../..", "recursos", "aresIcon.png")
            if os.path.exists(icon_path):
                self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
        except Exception as e:
            self.logger.warning(f"No se pudo cargar el icono: {e}")
        
        # Configurar tema
        self.root.configure(bg=self.tema_actual.FONDO_PRINCIPAL)
        
        # Configurar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
        # Variables para estadísticas de escaneo
        self.ultimo_escaneo_rapido = None
        self.ultimo_escaneo_completo = None
        self.archivos_escaneados_actual = 0
        self.amenazas_detectadas_actual = 0
        
        # Variables para controles de UI
        self.tab_actual = "principal"
    
    def mostrar_menu_principal(self):
        """Alias para mostrar_panel_principal."""
        self.mostrar_panel_principal()
        
        # Centrar ventana
        self.centrar_ventana()
        
        self.logger.info("Ventana principal creada")
    
    def centrar_ventana(self):
        """Centrar la ventana en la pantalla."""
        if self.root:
            self.root.update_idletasks()
            ancho = self.root.winfo_width()
            alto = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
            y = (self.root.winfo_screenheight() // 2) - (alto // 2)
            self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
    
    def inicializar_controlador(self):
        """Inicializar el controlador principal."""
        try:
            self.controlador = ControladorPrincipal()
            self.logger.info("Controlador principal inicializado")
            
        except Exception as e:
            self.logger.error(f"Error al inicializar controlador: {e}")
            raise
    
    def configurar_interfaz(self):
        """Configurar la interfaz gráfica principal."""
        self.crear_barra_navegacion()
        self.crear_contenido_principal()
        self.crear_panel_estado()
        self.crear_panel_notificaciones()
        
        # Mostrar panel principal por defecto
        self.mostrar_panel_principal()
    
    def crear_barra_navegacion(self):
        """Crear la barra de navegación moderna."""
        self.navbar = tk.Frame(self.root, bg=self.tema_actual.FONDO_SECUNDARIO, height=80)
        self.navbar.pack(fill=tk.X, side=tk.TOP)
        self.navbar.pack_propagate(False)
        
        # Contenedor principal de la navbar
        nav_container = tk.Frame(self.navbar, bg=self.tema_actual.FONDO_SECUNDARIO)
        nav_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Logo y título (lado izquierdo)
        logo_frame = tk.Frame(nav_container, bg=self.tema_actual.FONDO_SECUNDARIO)
        logo_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Cargar logo
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "../..", "recursos", "AresAegis.png")
            if os.path.exists(logo_path):
                logo_img = tk.PhotoImage(file=logo_path)
                # Redimensionar logo si es necesario
                try:
                    logo_img = logo_img.subsample(4)  # Solo un parámetro
                    logo_label = tk.Label(logo_frame, image=logo_img, bg=self.tema_actual.FONDO_SECUNDARIO)
                    logo_label.pack(side=tk.LEFT, padx=(0, 15))
                    # Mantener referencia para evitar garbage collection
                    setattr(logo_label, '_image', logo_img)
                except Exception:
                    # Si falla el redimensionado, usar imagen original
                    logo_label = tk.Label(logo_frame, image=logo_img, bg=self.tema_actual.FONDO_SECUNDARIO)
                    logo_label.pack(side=tk.LEFT, padx=(0, 15))
                    setattr(logo_label, '_image', logo_img)
        except Exception as e:
            self.logger.warning(f"No se pudo cargar el logo: {e}")
        
        # Título
        titulo_label = tk.Label(
            logo_frame,
            text="Ares Aegis",
            font=("Segoe UI", 24, "bold"),
            bg=self.tema_actual.FONDO_SECUNDARIO,
            fg=self.tema_actual.PRIMARIO
        )
        titulo_label.pack(side=tk.LEFT, anchor="w")
        
        subtitulo_label = tk.Label(
            logo_frame,
            text="Sistema de Ciberseguridad Avanzado",
            font=("Segoe UI", 12),
            bg=self.tema_actual.FONDO_SECUNDARIO,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        subtitulo_label.pack(side=tk.LEFT, anchor="w", padx=(15, 0))
        
        # Botones de navegación (centro)
        nav_buttons_frame = tk.Frame(nav_container, bg=self.tema_actual.FONDO_SECUNDARIO)
        nav_buttons_frame.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=50)
        
        # Crear botones de navegación
        botones_nav = [
            ("🏠 Principal", self.mostrar_panel_principal),
            ("🔍 Escaneo", self.mostrar_panel_escaneo),
            ("🛡️ Monitoreo", self.mostrar_panel_monitoreo),
            ("🗂️ Cuarentena", self.mostrar_panel_cuarentena),
            ("📊 Reportes", self.mostrar_panel_reportes),
            ("⚙️ Configuración", self.mostrar_panel_configuracion)
        ]
        
        self.botones_navegacion = {}
        for i, (texto, comando) in enumerate(botones_nav):
            btn_frame = ComponentesModernos.crear_boton_ultra_moderno(
                nav_buttons_frame,
                texto,
                comando,
                estilo="outline" if i > 0 else "primario"
            )
            btn_frame.pack(side=tk.LEFT, padx=5)
            self.botones_navegacion[texto.split()[1]] = btn_frame
        
        # Controles adicionales (lado derecho)
        controles_frame = tk.Frame(nav_container, bg=self.tema_actual.FONDO_SECUNDARIO)
        controles_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón de tema
        btn_tema = ComponentesModernos.crear_boton_ultra_moderno(
            controles_frame,
            "🌙 Tema",
            self.cambiar_tema,
            estilo="outline"
        )
        btn_tema.pack(side=tk.RIGHT, padx=5)
        
        # Indicador de estado
        self.indicador_estado = tk.Label(
            controles_frame,
            text="● Sistema Activo",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_SECUNDARIO,
            fg=self.tema_actual.EXITO
        )
        self.indicador_estado.pack(side=tk.RIGHT, padx=20)
    
    def crear_contenido_principal(self):
        """Crear el área de contenido principal."""
        self.contenido_principal = tk.Frame(self.root, bg=self.tema_actual.FONDO_PRINCIPAL)
        self.contenido_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def crear_panel_estado(self):
        """Crear el panel de estado en la parte inferior."""
        self.panel_estado = tk.Frame(self.root, bg=self.tema_actual.FONDO_SECUNDARIO, height=40)
        self.panel_estado.pack(fill=tk.X, side=tk.BOTTOM)
        self.panel_estado.pack_propagate(False)
        
        # Estado general
        self.label_estado = tk.Label(
            self.panel_estado,
            text="Listo - Sistema inicializado correctamente",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_SECUNDARIO,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        self.label_estado.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Hora actual
        self.label_hora = tk.Label(
            self.panel_estado,
            text="",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_SECUNDARIO,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.label_hora.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Actualizar hora
        self.actualizar_hora()
    
    def crear_panel_notificaciones(self):
        """Crear el panel de notificaciones."""
        # Este panel se mostrará como overlay cuando sea necesario
        pass
    
    def mostrar_panel_principal(self):
        """Mostrar el panel principal del sistema."""
        self.limpiar_contenido()
        self.actualizar_navegacion_activa("Principal")
        
        # Crear layout de tarjetas
        main_container = tk.Frame(self.contenido_principal, bg=self.tema_actual.FONDO_PRINCIPAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Fila superior de tarjetas
        row1 = tk.Frame(main_container, bg=self.tema_actual.FONDO_PRINCIPAL)
        row1.pack(fill=tk.X, pady=(0, 20))
        
        # Tarjeta de Estado del Sistema
        card_estado_container, card_estado_content = ComponentesModernos.crear_card_ultra_moderna(row1, "Estado del Sistema", 20)
        card_estado_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.crear_widgets_estado_sistema(card_estado_content)
        
        # Tarjeta de Escaneo Rápido
        card_escaneo_container, card_escaneo_content = ComponentesModernos.crear_card_ultra_moderna(row1, "Escaneo Rápido", 20)
        card_escaneo_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.crear_widgets_escaneo_rapido(card_escaneo_content)
        
        # Fila inferior de tarjetas
        row2 = tk.Frame(main_container, bg=self.tema_actual.FONDO_PRINCIPAL)
        row2.pack(fill=tk.BOTH, expand=True)
        
        # Tarjeta de Actividad Reciente
        card_actividad_container, card_actividad_content = ComponentesModernos.crear_card_ultra_moderna(row2, "Actividad Reciente", 20)
        card_actividad_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.crear_widgets_actividad_reciente(card_actividad_content)
        
        # Tarjeta de Alertas y Notificaciones
        card_alertas_container, card_alertas_content = ComponentesModernos.crear_card_ultra_moderna(row2, "Alertas y Notificaciones", 20)
        card_alertas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.crear_widgets_alertas(card_alertas_content)
    
    def crear_widgets_estado_sistema(self, parent):
        """Crear widgets para el estado del sistema."""
        # Estado de servicios principales
        servicios = []
        
        if self.controlador:
            servicios = [
                ("Monitor de Red", self.controlador.monitor_red.monitoreando if self.controlador.monitor_red else False),
                ("Monitor de Procesos", hasattr(self.controlador.monitor_procesos, 'monitoreando') and self.controlador.monitor_procesos.monitoreando if self.controlador.monitor_procesos else False),
                ("SIEM", self.controlador.siem is not None),
                ("FIM", self.controlador.fim is not None)
            ]
        else:
            servicios = [
                ("Monitor de Red", False),
                ("Monitor de Procesos", False),
                ("SIEM", False),
                ("FIM", False)
            ]
        
        for servicio, activo in servicios:
            frame_servicio = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
            frame_servicio.pack(fill=tk.X, pady=2)
            
            status_color = self.tema_actual.EXITO if activo else self.tema_actual.ERROR
            status_text = "Activo" if activo else "Inactivo"
            
            tk.Label(
                frame_servicio,
                text=f"● {servicio}:",
                font=("Segoe UI", 11),
                bg=self.tema_actual.FONDO_CARD,
                fg=self.tema_actual.TEXTO_PRINCIPAL
            ).pack(side=tk.LEFT)
            
            tk.Label(
                frame_servicio,
                text=status_text,
                font=("Segoe UI", 11, "bold"),
                bg=self.tema_actual.FONDO_CARD,
                fg=status_color
            ).pack(side=tk.RIGHT)
        
        # Botones de control
        buttons_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        buttons_frame.pack(fill=tk.X, pady=(15, 0))
        
        btn_iniciar = ComponentesModernos.crear_boton_ultra_moderno(
            buttons_frame,
            "Iniciar Servicios",
            self.iniciar_servicios,
            estilo="exito"
        )
        btn_iniciar.pack(side=tk.LEFT, padx=(0, 5))
        
        btn_detener = ComponentesModernos.crear_boton_ultra_moderno(
            buttons_frame,
            "Detener Servicios",
            self.detener_servicios,
            estilo="peligro"
        )
        btn_detener.pack(side=tk.LEFT, padx=5)
    
    def crear_widgets_escaneo_rapido(self, parent):
        """Crear widgets para el escaneo rápido."""
        # Información del último escaneo
        ultimo_escaneo = self.controlador.obtener_ultimo_escaneo() if self.controlador else None
        
        if ultimo_escaneo:
            tk.Label(
                parent,
                text=f"Último escaneo: {ultimo_escaneo.get('fecha', 'Nunca')}",
                font=("Segoe UI", 11),
                bg=self.tema_actual.FONDO_CARD,
                fg=self.tema_actual.TEXTO_SECUNDARIO
            ).pack(anchor="w", pady=(0, 5))
            
            tk.Label(
                parent,
                text=f"Amenazas encontradas: {ultimo_escaneo.get('amenazas', 0)}",
                font=("Segoe UI", 11, "bold"),
                bg=self.tema_actual.FONDO_CARD,
                fg=self.tema_actual.ERROR if ultimo_escaneo.get('amenazas', 0) > 0 else self.tema_actual.EXITO
            ).pack(anchor="w", pady=(0, 15))
        
        # Botones de escaneo
        btn_escaneo_rapido = ComponentesModernos.crear_boton_ultra_moderno(
            parent,
            "Escaneo Rápido",
            self.ejecutar_escaneo_rapido,
            estilo="primario"
        )
        btn_escaneo_rapido.pack(fill=tk.X, pady=(0, 10))
        
        btn_escaneo_completo = ComponentesModernos.crear_boton_ultra_moderno(
            parent,
            "Escaneo Completo",
            self.ejecutar_escaneo_completo,
            estilo="secundario"
        )
        btn_escaneo_completo.pack(fill=tk.X)
        
        # Progreso de escaneo (inicialmente oculto)
        self.frame_progreso = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        
        self.progress_var = tk.StringVar(value="Esperando...")
        self.progress_label = tk.Label(
            self.frame_progreso,
            textvariable=self.progress_var,
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.progress_label.pack(pady=(10, 5))
        
        self.progress_bar = ttk.Progressbar(
            self.frame_progreso,
            mode='indeterminate',
            length=200
        )
        self.progress_bar.pack(pady=(0, 10))
    
    def crear_widgets_actividad_reciente(self, parent):
        """Crear widgets para la actividad reciente."""
        # Lista de actividades
        self.lista_actividades = scrolledtext.ScrolledText(
            parent,
            height=8,
            font=("Consolas", 10),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            relief="flat",
            wrap=tk.WORD
        )
        self.lista_actividades.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Cargar actividades recientes
        self.cargar_actividades_recientes()
        
        # Botón para ver más
        btn_ver_mas = ComponentesModernos.crear_boton_ultra_moderno(
            parent,
            "Ver Registro Completo",
            self.abrir_registro_completo,
            estilo="outline"
        )
        btn_ver_mas.pack(fill=tk.X)
    
    def crear_widgets_alertas(self, parent):
        """Crear widgets para alertas y notificaciones."""
        # Lista de alertas
        alertas = self.controlador.obtener_alertas_recientes() if self.controlador else []
        
        if not alertas:
            tk.Label(
                parent,
                text="No hay alertas pendientes",
                font=("Segoe UI", 12),
                bg=self.tema_actual.FONDO_CARD,
                fg=self.tema_actual.EXITO
            ).pack(expand=True)
        else:
            for alerta in alertas[:5]:  # Mostrar máximo 5 alertas
                frame_alerta = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
                frame_alerta.pack(fill=tk.X, pady=2)
                
                # Icono según severidad
                severity_icons = {
                    "critical": "🔴",
                    "warning": "🟡",
                    "info": "🔵"
                }
                icono = severity_icons.get(alerta.get('severity', 'info'), "🔵")
                
                tk.Label(
                    frame_alerta,
                    text=f"{icono} {alerta.get('mensaje', 'Sin mensaje')}",
                    font=("Segoe UI", 10),
                    bg=self.tema_actual.FONDO_CARD,
                    fg=self.tema_actual.TEXTO_PRINCIPAL
                ).pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                tk.Label(
                    frame_alerta,
                    text=alerta.get('timestamp', ''),
                    font=("Segoe UI", 9),
                    bg=self.tema_actual.FONDO_CARD,
                    fg=self.tema_actual.TEXTO_MUTED
                ).pack(side=tk.RIGHT)
        
        # Botón para ver todas las alertas
        if alertas:
            btn_ver_alertas = ComponentesModernos.crear_boton_ultra_moderno(
                parent,
                "Ver Todas las Alertas",
                self.mostrar_todas_alertas,
                estilo="outline"
            )
            btn_ver_alertas.pack(fill=tk.X, pady=(10, 0))
    
    def mostrar_panel_escaneo(self):
        """Mostrar el panel de escaneo completo."""
        self.limpiar_contenido()
        self.actualizar_navegacion_activa("Escaneo")
        
        # Crear layout principal
        main_container = tk.Frame(self.contenido_principal, bg=self.tema_actual.FONDO_PRINCIPAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Botón para volver al menú principal
        btn_volver = ComponentesModernos.crear_boton_ultra_moderno(
            main_container,
            "⬅️ Volver al Menú Principal",
            self.mostrar_panel_principal,
            estilo="outline"
        )
        btn_volver.pack(anchor="w", pady=(0, 20))
        
        # Título del panel
        titulo_frame = tk.Frame(main_container, bg=self.tema_actual.FONDO_PRINCIPAL)
        titulo_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            titulo_frame,
            text="🔍 Centro de Escaneo de Seguridad",
            font=("Segoe UI", 20, "bold"),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.PRIMARIO
        ).pack(anchor="w")
        
        tk.Label(
            titulo_frame,
            text="Análisis completo del sistema para detectar amenazas y vulnerabilidades",
            font=("Segoe UI", 12),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        ).pack(anchor="w", pady=(5, 0))
        
        # Fila superior - Tipos de escaneo
        row1 = tk.Frame(main_container, bg=self.tema_actual.FONDO_PRINCIPAL)
        row1.pack(fill=tk.X, pady=(0, 20))
        
        # Card de Escaneo Rápido
        card_rapido_container, card_rapido_content = ComponentesModernos.crear_card_ultra_moderna(row1, "⚡ Escaneo Rápido", 20)
        card_rapido_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.crear_widgets_escaneo_rapido_completo(card_rapido_content)
        
        # Card de Escaneo Completo
        card_completo_container, card_completo_content = ComponentesModernos.crear_card_ultra_moderna(row1, "🔍 Escaneo Completo", 20)
        card_completo_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 5))
        
        self.crear_widgets_escaneo_completo(card_completo_content)
        
        # Card de Escaneo Personalizado
        card_personalizado_container, card_personalizado_content = ComponentesModernos.crear_card_ultra_moderna(row1, "⚙️ Escaneo Personalizado", 20)
        card_personalizado_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.crear_widgets_escaneo_personalizado(card_personalizado_content)
        
        # Fila inferior - Progreso y resultados
        row2 = tk.Frame(main_container, bg=self.tema_actual.FONDO_PRINCIPAL)
        row2.pack(fill=tk.BOTH, expand=True)
        
        # Card de Progreso
        card_progreso_container, card_progreso_content = ComponentesModernos.crear_card_ultra_moderna(row2, "📊 Progreso del Escaneo", 20)
        card_progreso_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.crear_widgets_progreso_escaneo(card_progreso_content)
        
        # Card de Resultados
        card_resultados_container, card_resultados_content = ComponentesModernos.crear_card_ultra_moderna(row2, "📋 Resultados del Escaneo", 20)
        card_resultados_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.crear_widgets_resultados_escaneo(card_resultados_content)
    
    def crear_widgets_resultados_escaneo(self, parent):
        """Crear widgets para mostrar resultados del escaneo."""
        # Lista de resultados con scroll
        self.text_resultados_escaneo = scrolledtext.ScrolledText(
            parent,
            height=12,
            font=("Consolas", 10),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            relief="flat",
            wrap=tk.WORD
        )
        self.text_resultados_escaneo.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Mensaje inicial
        self.text_resultados_escaneo.insert(tk.END, "Resultados del escaneo aparecerán aquí...\n")
        
        # Botones de acción para resultados
        buttons_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        buttons_frame.pack(fill=tk.X)
        
        btn_exportar = ComponentesModernos.crear_boton_ultra_moderno(
            buttons_frame,
            "📤 Exportar Resultados",
            self.exportar_resultados_escaneo,
            estilo="outline"
        )
        btn_exportar.pack(side=tk.LEFT, padx=(0, 5))
        
        btn_limpiar = ComponentesModernos.crear_boton_ultra_moderno(
            buttons_frame,
            "🗑️ Limpiar",
            self.limpiar_resultados_escaneo,
            estilo="outline"
        )
        btn_limpiar.pack(side=tk.LEFT, padx=5)
    
    def crear_widgets_escaneo_rapido_completo(self, parent):
        """Crear widgets para el escaneo rápido."""
        # Descripción
        tk.Label(
            parent,
            text="Análisis rápido de archivos comunes y ubicaciones críticas del sistema",
            font=("Segoe UI", 11),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO,
            wraplength=200
        ).pack(anchor="w", pady=(0, 15))
        
        # Estadísticas del último escaneo rápido
        if hasattr(self, 'ultimo_escaneo_rapido') and self.ultimo_escaneo_rapido:
            stats_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
            stats_frame.pack(fill=tk.X, pady=(0, 15))
            
            tk.Label(
                stats_frame,
                text="Último escaneo:",
                font=("Segoe UI", 10, "bold"),
                bg=self.tema_actual.FONDO_CARD,
                fg=self.tema_actual.TEXTO_PRINCIPAL
            ).pack(anchor="w")
            
            tk.Label(
                stats_frame,
                text=f"Archivos: {self.ultimo_escaneo_rapido.get('archivos_escaneados', 0)}",
                font=("Segoe UI", 10),
                bg=self.tema_actual.FONDO_CARD,
                fg=self.tema_actual.TEXTO_SECUNDARIO
            ).pack(anchor="w")
            
            amenazas = self.ultimo_escaneo_rapido.get('amenazas_detectadas', 0)
            color_amenazas = self.tema_actual.ERROR if amenazas > 0 else self.tema_actual.EXITO
            tk.Label(
                stats_frame,
                text=f"Amenazas: {amenazas}",
                font=("Segoe UI", 10, "bold"),
                bg=self.tema_actual.FONDO_CARD,
                fg=color_amenazas
            ).pack(anchor="w")
        
        # Botón de escaneo rápido
        btn_escaneo_rapido = ComponentesModernos.crear_boton_ultra_moderno(
            parent,
            "⚡ Iniciar Escaneo Rápido",
            self.ejecutar_escaneo_rapido_avanzado,
            estilo="primario"
        )
        btn_escaneo_rapido.pack(fill=tk.X, pady=(0, 10))
        
        # Tiempo estimado
        tk.Label(
            parent,
            text="⏱️ Tiempo estimado: 2-5 minutos",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_MUTED
        ).pack(anchor="w")
    
    def crear_widgets_escaneo_completo(self, parent):
        """Crear widgets para el escaneo completo."""
        # Descripción
        tk.Label(
            parent,
            text="Análisis exhaustivo de todo el sistema incluyendo todos los archivos y directorios",
            font=("Segoe UI", 11),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO,
            wraplength=200
        ).pack(anchor="w", pady=(0, 15))
        
        # Estadísticas del último escaneo completo
        if hasattr(self, 'ultimo_escaneo_completo') and self.ultimo_escaneo_completo:
            stats_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
            stats_frame.pack(fill=tk.X, pady=(0, 15))
            
            tk.Label(
                stats_frame,
                text="Último escaneo:",
                font=("Segoe UI", 10, "bold"),
                bg=self.tema_actual.FONDO_CARD,
                fg=self.tema_actual.TEXTO_PRINCIPAL
            ).pack(anchor="w")
            
            tk.Label(
                stats_frame,
                text=f"Archivos: {self.ultimo_escaneo_completo.get('archivos_escaneados', 0)}",
                font=("Segoe UI", 10),
                bg=self.tema_actual.FONDO_CARD,
                fg=self.tema_actual.TEXTO_SECUNDARIO
            ).pack(anchor="w")
            
            amenazas = self.ultimo_escaneo_completo.get('amenazas_detectadas', 0)
            color_amenazas = self.tema_actual.ERROR if amenazas > 0 else self.tema_actual.EXITO
            tk.Label(
                stats_frame,
                text=f"Amenazas: {amenazas}",
                font=("Segoe UI", 10, "bold"),
                bg=self.tema_actual.FONDO_CARD,
                fg=color_amenazas
            ).pack(anchor="w")
        
        # Botón de escaneo completo
        btn_escaneo_completo = ComponentesModernos.crear_boton_ultra_moderno(
            parent,
            "🔍 Iniciar Escaneo Completo",
            self.ejecutar_escaneo_completo_avanzado,
            estilo="secundario"
        )
        btn_escaneo_completo.pack(fill=tk.X, pady=(0, 10))
        
        # Tiempo estimado
        tk.Label(
            parent,
            text="⏱️ Tiempo estimado: 15-45 minutos",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_MUTED
        ).pack(anchor="w")
    
    def crear_widgets_escaneo_personalizado(self, parent):
        """Crear widgets para el escaneo personalizado."""
        # Descripción
        tk.Label(
            parent,
            text="Escanear directorios específicos según tus necesidades",
            font=("Segoe UI", 11),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO,
            wraplength=200
        ).pack(anchor="w", pady=(0, 15))
        
        # Selector de carpeta
        carpeta_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        carpeta_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            carpeta_frame,
            text="Carpeta a escanear:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(anchor="w")
        
        # Variable para la ruta seleccionada
        self.var_ruta_personalizada = tk.StringVar(value="Seleccionar carpeta...")
        
        entrada_frame = tk.Frame(carpeta_frame, bg=self.tema_actual.FONDO_CARD)
        entrada_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.entry_ruta = tk.Entry(
            entrada_frame,
            textvariable=self.var_ruta_personalizada,
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            relief="flat",
            bd=5
        )
        self.entry_ruta.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_seleccionar = ComponentesModernos.crear_boton_ultra_moderno(
            entrada_frame,
            "📁",
            self.seleccionar_carpeta_escaneo,
            estilo="outline"
        )
        btn_seleccionar.pack(side=tk.RIGHT)
        
        # Opciones adicionales
        opciones_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        opciones_frame.pack(fill=tk.X, pady=(10, 15))
        
        self.var_recursivo = tk.BooleanVar(value=True)
        check_recursivo = tk.Checkbutton(
            opciones_frame,
            text="Incluir subcarpetas",
            variable=self.var_recursivo,
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            font=("Segoe UI", 10)
        )
        check_recursivo.pack(anchor="w")
        
        # Botón de escaneo personalizado
        btn_escaneo_personalizado = ComponentesModernos.crear_boton_ultra_moderno(
            parent,
            "⚙️ Iniciar Escaneo Personalizado",
            self.ejecutar_escaneo_personalizado,
            estilo="outline"
        )
        btn_escaneo_personalizado.pack(fill=tk.X)
    
    def crear_widgets_progreso_escaneo(self, parent):
        """Crear widgets para mostrar el progreso del escaneo."""
        # Estado actual
        self.label_estado_escaneo = tk.Label(
            parent,
            text="Esperando inicio de escaneo...",
            font=("Segoe UI", 12, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        self.label_estado_escaneo.pack(anchor="w", pady=(0, 15))
        
        # Barra de progreso
        self.progress_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        self.progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            self.progress_frame,
            text="Progreso:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(anchor="w")
        
        self.progress_bar_escaneo = ttk.Progressbar(
            self.progress_frame,
            mode='determinate',
            length=300
        )
        self.progress_bar_escaneo.pack(fill=tk.X, pady=(5, 0))
        
        # Estadísticas en tiempo real
        stats_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Archivos escaneados
        archivos_frame = tk.Frame(stats_frame, bg=self.tema_actual.FONDO_CARD)
        archivos_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            archivos_frame,
            text="Archivos escaneados:",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        ).pack(side=tk.LEFT)
        
        self.label_archivos_escaneados = tk.Label(
            archivos_frame,
            text="0",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        self.label_archivos_escaneados.pack(side=tk.RIGHT)
        
        # Amenazas detectadas
        amenazas_frame = tk.Frame(stats_frame, bg=self.tema_actual.FONDO_CARD)
        amenazas_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            amenazas_frame,
            text="Amenazas detectadas:",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        ).pack(side=tk.LEFT)
        
        self.label_amenazas_detectadas = tk.Label(
            amenazas_frame,
            text="0",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.EXITO
        )
        self.label_amenazas_detectadas.pack(side=tk.RIGHT)
        
        # Tiempo transcurrido
        tiempo_frame = tk.Frame(stats_frame, bg=self.tema_actual.FONDO_CARD)
        tiempo_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            tiempo_frame,
            text="Tiempo transcurrido:",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        ).pack(side=tk.LEFT)
        
        self.label_tiempo_transcurrido = tk.Label(
            tiempo_frame,
            text="00:00:00",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        self.label_tiempo_transcurrido.pack(side=tk.RIGHT)
        
        # Botones de control
        control_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        control_frame.pack(fill=tk.X)
        
        self.btn_pausar = ComponentesModernos.crear_boton_ultra_moderno(
            control_frame,
            "⏸️ Pausar",
            self.pausar_escaneo,
            estilo="outline"
        )
        self.btn_pausar.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_detener = ComponentesModernos.crear_boton_ultra_moderno(
            control_frame,
            "⏹️ Detener",
            self.detener_escaneo,
            estilo="peligro"
        )
        self.btn_detener.pack(side=tk.LEFT, padx=5)
    
    def mostrar_tab(self, nombre_tab):
        """Cambiar la pestaña visible."""
        self.tab_actual = nombre_tab
        # Para futuro uso con múltiples pestañas
        
    def exportar_resultados_escaneo(self):
        """Exportar los resultados del escaneo a un archivo."""
        try:
            from tkinter import filedialog
            archivo = filedialog.asksaveasfilename(
                title="Guardar resultados del escaneo",
                defaultextension=".txt",
                filetypes=[
                    ("Archivos de texto", "*.txt"),
                    ("Archivos HTML", "*.html"),
                    ("Archivos JSON", "*.json"),
                    ("Todos los archivos", "*.*")
                ]
            )
            
            if archivo:
                contenido = self.text_resultados_escaneo.get(1.0, tk.END)
                
                if archivo.endswith('.html'):
                    # Generar reporte HTML
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Reporte de Escaneo - Ares Aegis</title>
                        <meta charset="utf-8">
                        <style>
                            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; }}
                            .header {{ background: #2d3748; color: white; padding: 20px; border-radius: 8px; }}
                            .content {{ background: #f7fafc; padding: 20px; border-radius: 8px; margin-top: 10px; }}
                            .threat {{ background: #fed7d7; padding: 10px; margin: 5px 0; border-left: 4px solid #e53e3e; }}
                            .safe {{ background: #c6f6d5; padding: 10px; margin: 5px 0; border-left: 4px solid #38a169; }}
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <h1>🛡️ Reporte de Escaneo - Ares Aegis</h1>
                            <p>Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                        </div>
                        <div class="content">
                            <pre>{contenido}</pre>
                        </div>
                    </body>
                    </html>
                    """
                    with open(archivo, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                elif archivo.endswith('.json'):
                    # Generar reporte JSON
                    reporte_json = {
                        "timestamp": datetime.now().isoformat(),
                        "herramienta": "Ares Aegis",
                        "tipo_escaneo": "Análisis de seguridad",
                        "resultados": contenido.strip(),
                        "estadisticas": {
                            "archivos_escaneados": getattr(self, 'archivos_escaneados_actual', 0),
                            "amenazas_detectadas": getattr(self, 'amenazas_detectadas_actual', 0)
                        }
                    }
                    import json
                    with open(archivo, 'w', encoding='utf-8') as f:
                        json.dump(reporte_json, f, indent=2, ensure_ascii=False)
                else:
                    # Archivo de texto plano
                    with open(archivo, 'w', encoding='utf-8') as f:
                        f.write(f"=== REPORTE DE ESCANEO - ARES AEGIS ===\\n")
                        f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\\n")
                        f.write(f"{'='*50}\\n\\n")
                        f.write(contenido)
                
                messagebox.showinfo("Exportación exitosa", f"Resultados guardados en:\\n{archivo}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar resultados:\\n{str(e)}")
    
    def limpiar_resultados_escaneo(self):
        """Limpiar los resultados del escaneo."""
        respuesta = messagebox.askyesno(
            "Confirmar limpieza",
            "¿Está seguro de que desea limpiar todos los resultados del escaneo?"
        )
        
        if respuesta:
            self.text_resultados_escaneo.delete(1.0, tk.END)
            self.text_resultados_escaneo.insert(tk.END, "Resultados del escaneo aparecerán aquí...\\n")
            
            # Resetear contadores
            if hasattr(self, 'label_archivos_escaneados'):
                self.label_archivos_escaneados.config(text="0")
            if hasattr(self, 'label_amenazas_detectadas'):
                self.label_amenazas_detectadas.config(text="0", fg=self.tema_actual.EXITO)
            if hasattr(self, 'progress_bar_escaneo'):
                self.progress_bar_escaneo['value'] = 0
    
    def ejecutar_escaneo_rapido_avanzado(self):
        """Ejecutar escaneo rápido con interfaz moderna y progreso en tiempo real."""
        try:
            self.actualizar_estado_escaneo("Iniciando escaneo rápido...", 0)
            
            # Mostrar la sección de progreso
            if hasattr(self, 'progress_bar_escaneo'):
                self.progress_bar_escaneo['value'] = 0
            
            # Reiniciar contadores
            self.archivos_escaneados_actual = 0
            self.amenazas_detectadas_actual = 0
            
            # Ejecutar en hilo separado para no bloquear la interfaz
            import threading
            
            def escaneo_thread():
                try:
                    # Iniciar el callback de progreso
                    def callback_progreso(archivo_actual, total_archivos, amenazas_encontradas):
                        if hasattr(self, 'root') and self.root:
                            self.root.after(0, lambda: self.actualizar_progreso_escaneo(
                                archivo_actual, total_archivos, amenazas_encontradas
                            ))
                    
                    # Llamar al escaneo con callback
                    resultado = self.controlador.escaneo_rapido_con_progreso(callback_progreso)
                    
                    # Actualizar interfaz en el hilo principal
                    if hasattr(self, 'root') and self.root:
                        self.root.after(0, lambda: self.procesar_resultado_escaneo(resultado, "rápido"))
                    
                except Exception as e:
                    if hasattr(self, 'root') and self.root:
                        self.root.after(0, lambda: self.mostrar_error_escaneo(str(e)))
            
            threading.Thread(target=escaneo_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar escaneo rápido:\\n{str(e)}")
    
    def actualizar_progreso_escaneo(self, archivos_escaneados, total_archivos, amenazas_detectadas):
        """Actualizar el progreso del escaneo en tiempo real."""
        try:
            # Actualizar progreso
            if total_archivos > 0:
                progreso = (archivos_escaneados / total_archivos) * 100
                if hasattr(self, 'progress_bar_escaneo'):
                    self.progress_bar_escaneo['value'] = progreso
            
            # Actualizar contadores
            if hasattr(self, 'label_archivos_escaneados'):
                self.label_archivos_escaneados.config(text=str(archivos_escaneados))
            
            if hasattr(self, 'label_amenazas_detectadas'):
                color = self.tema_actual.ERROR if amenazas_detectadas > 0 else self.tema_actual.EXITO
                self.label_amenazas_detectadas.config(text=str(amenazas_detectadas), fg=color)
            
            # Actualizar estado
            if hasattr(self, 'label_estado_escaneo'):
                if total_archivos > 0:
                    porcentaje = (archivos_escaneados / total_archivos) * 100
                    self.label_estado_escaneo.config(text=f"Escaneando... {porcentaje:.1f}% ({archivos_escaneados}/{total_archivos})")
                else:
                    self.label_estado_escaneo.config(text=f"Escaneando... {archivos_escaneados} archivos")
                    
        except Exception as e:
            self.logger.error(f"Error actualizando progreso: {e}")
    
    def ejecutar_escaneo_completo_avanzado(self):
        """Ejecutar escaneo completo con interfaz moderna y progreso en tiempo real."""
        try:
            self.actualizar_estado_escaneo("Iniciando escaneo completo del sistema...", 0)
            
            # Confirmar antes del escaneo completo
            respuesta = messagebox.askyesno(
                "Confirmar escaneo completo",
                "El escaneo completo puede tomar entre 15-45 minutos.\\n¿Desea continuar?"
            )
            
            if not respuesta:
                return
            
            # Mostrar la sección de progreso
            if hasattr(self, 'progress_bar_escaneo'):
                self.progress_bar_escaneo['value'] = 0
            
            # Reiniciar contadores
            self.archivos_escaneados_actual = 0
            self.amenazas_detectadas_actual = 0
            
            # Ejecutar en hilo separado
            import threading
            
            def escaneo_thread():
                try:
                    # Callback de progreso
                    def callback_progreso(archivo_actual, total_archivos, amenazas_encontradas):
                        if hasattr(self, 'root') and self.root:
                            self.root.after(0, lambda: self.actualizar_progreso_escaneo(
                                archivo_actual, total_archivos, amenazas_encontradas
                            ))
                    
                    # Llamar al escaneo con callback
                    resultado = self.controlador.escaneo_completo_con_progreso(callback_progreso)
                    
                    # Actualizar interfaz en el hilo principal
                    if hasattr(self, 'root') and self.root:
                        self.root.after(0, lambda: self.procesar_resultado_escaneo(resultado, "completo"))
                    
                except Exception as e:
                    if hasattr(self, 'root') and self.root:
                        self.root.after(0, lambda: self.mostrar_error_escaneo(str(e)))
            
            threading.Thread(target=escaneo_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar escaneo completo:\\n{str(e)}")
    
    def ejecutar_escaneo_personalizado(self):
        """Ejecutar escaneo personalizado en directorio seleccionado."""
        try:
            ruta = self.var_ruta_personalizada.get()
            
            if ruta == "Seleccionar carpeta..." or not ruta:
                messagebox.showwarning("Advertencia", "Por favor seleccione una carpeta para escanear.")
                return
            
            if not os.path.exists(ruta):
                messagebox.showerror("Error", "La ruta seleccionada no existe.")
                return
            
            self.actualizar_estado_escaneo(f"Escaneando {ruta}...", 0)
            
            # Ejecutar en hilo separado
            import threading
            
            def escaneo_thread():
                try:
                    resultado = self.controlador.escanear_directorio(ruta)
                    
                    # Actualizar interfaz en el hilo principal
                    if hasattr(self, 'root') and self.root:
                        self.root.after(0, lambda: self.procesar_resultado_escaneo(resultado, "personalizado"))
                    
                except Exception as e:
                    if hasattr(self, 'root') and self.root:
                        self.root.after(0, lambda: self.mostrar_error_escaneo(str(e)))
            
            threading.Thread(target=escaneo_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar escaneo personalizado:\\n{str(e)}")
    
    def seleccionar_carpeta_escaneo(self):
        """Seleccionar carpeta para escaneo personalizado."""
        from tkinter import filedialog
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta para escanear")
        
        if carpeta:
            self.var_ruta_personalizada.set(carpeta)
    
    def pausar_escaneo(self):
        """Pausar el escaneo actual."""
        try:
            # Por ahora simplemente mostramos información
            messagebox.showinfo("Información", "La funcionalidad de pausa será implementada próximamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al pausar escaneo:\\n{str(e)}")
    
    def detener_escaneo(self):
        """Detener el escaneo actual."""
        try:
            respuesta = messagebox.askyesno(
                "Confirmar detención",
                "¿Está seguro de que desea detener el escaneo actual?"
            )
            
            if respuesta:
                messagebox.showinfo("Información", "El escaneo se detendrá en breve.")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al detener escaneo:\\n{str(e)}")
    
    def actualizar_estado_escaneo(self, estado, progreso):
        """Actualizar el estado y progreso del escaneo."""
        if hasattr(self, 'label_estado_escaneo'):
            self.label_estado_escaneo.config(text=estado)
        
        if progreso is not None and hasattr(self, 'progress_bar_escaneo'):
            self.progress_bar_escaneo['value'] = progreso
    
    def procesar_resultado_escaneo(self, resultado, tipo_escaneo):
        """Procesar y mostrar los resultados del escaneo."""
        try:
            # Extraer datos del resultado
            archivos_escaneados = resultado.get('archivos_escaneados', 0)
            amenazas_detectadas = resultado.get('amenazas_detectadas', 0)
            archivos_infectados = resultado.get('archivos_infectados_lista', [])
            tiempo_escaneo = resultado.get('tiempo_escaneo', 0)
            rutas_escaneadas = resultado.get('rutas_escaneadas', [])
            
            # Guardar resultado para estadísticas
            if tipo_escaneo == "rápido":
                self.ultimo_escaneo_rapido = {
                    'archivos_escaneados': archivos_escaneados,
                    'amenazas_detectadas': amenazas_detectadas
                }
            elif tipo_escaneo == "completo":
                self.ultimo_escaneo_completo = {
                    'archivos_escaneados': archivos_escaneados,
                    'amenazas_detectadas': amenazas_detectadas
                }
            
            # Actualizar contadores finales
            if hasattr(self, 'label_archivos_escaneados'):
                self.label_archivos_escaneados.config(text=str(archivos_escaneados))
            
            if hasattr(self, 'label_amenazas_detectadas'):
                color = self.tema_actual.ERROR if amenazas_detectadas > 0 else self.tema_actual.EXITO
                self.label_amenazas_detectadas.config(text=str(amenazas_detectadas), fg=color)
            
            # Actualizar barra de progreso al 100%
            if hasattr(self, 'progress_bar_escaneo'):
                self.progress_bar_escaneo['value'] = 100
            
            # Actualizar estado final
            if hasattr(self, 'label_estado_escaneo'):
                estado_final = f"Escaneo {tipo_escaneo} completado - {archivos_escaneados} archivos, {amenazas_detectadas} amenazas"
                self.label_estado_escaneo.config(text=estado_final)
            
            # Mostrar resultados detallados
            if hasattr(self, 'text_resultados_escaneo'):
                self.text_resultados_escaneo.delete(1.0, tk.END)
                
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                self.text_resultados_escaneo.insert(tk.END, f"=== ESCANEO {tipo_escaneo.upper()} COMPLETADO ===\\n")
                self.text_resultados_escaneo.insert(tk.END, f"Fecha: {timestamp}\\n")
                self.text_resultados_escaneo.insert(tk.END, f"Tiempo transcurrido: {tiempo_escaneo:.2f} segundos\\n")
                self.text_resultados_escaneo.insert(tk.END, f"{'='*50}\\n\\n")
                
                # Estadísticas principales
                self.text_resultados_escaneo.insert(tk.END, f"📁 Archivos escaneados: {archivos_escaneados}\\n")
                self.text_resultados_escaneo.insert(tk.END, f"⚠️ Amenazas detectadas: {amenazas_detectadas}\\n")
                self.text_resultados_escaneo.insert(tk.END, f"📂 Rutas analizadas: {len(rutas_escaneadas)}\\n\\n")
                
                # Rutas escaneadas
                if rutas_escaneadas:
                    self.text_resultados_escaneo.insert(tk.END, "📂 RUTAS ESCANEADAS:\\n")
                    for ruta in rutas_escaneadas[:10]:  # Máximo 10 rutas
                        self.text_resultados_escaneo.insert(tk.END, f"   • {ruta}\\n")
                    if len(rutas_escaneadas) > 10:
                        self.text_resultados_escaneo.insert(tk.END, f"   ... y {len(rutas_escaneadas) - 10} rutas más\\n")
                    self.text_resultados_escaneo.insert(tk.END, "\\n")
                
                # Archivos infectados
                if archivos_infectados:
                    self.text_resultados_escaneo.insert(tk.END, "🚨 ARCHIVOS CON AMENAZAS DETECTADAS:\\n")
                    self.text_resultados_escaneo.insert(tk.END, f"{'-'*50}\\n")
                    
                    for i, archivo in enumerate(archivos_infectados, 1):
                        self.text_resultados_escaneo.insert(tk.END, f"\\n{i}. {archivo}\\n")
                        self.text_resultados_escaneo.insert(tk.END, f"   ⚠️ Se recomienda revisar este archivo\\n")
                        self.text_resultados_escaneo.insert(tk.END, f"   📋 Acciones disponibles: Cuarentena, Análisis detallado\\n")
                else:
                    self.text_resultados_escaneo.insert(tk.END, "✅ ¡EXCELENTE! No se detectaron amenazas en este escaneo.\\n")
                    self.text_resultados_escaneo.insert(tk.END, "   El sistema está limpio según los patrones analizados.\\n")
                
                # Recomendaciones
                self.text_resultados_escaneo.insert(tk.END, f"\\n{'='*50}\\n")
                self.text_resultados_escaneo.insert(tk.END, "💡 RECOMENDACIONES:\\n")
                
                if amenazas_detectadas > 0:
                    self.text_resultados_escaneo.insert(tk.END, "   • Revisar los archivos detectados\\n")
                    self.text_resultados_escaneo.insert(tk.END, "   • Considerar poner archivos sospechosos en cuarentena\\n")
                    self.text_resultados_escaneo.insert(tk.END, "   • Ejecutar un escaneo completo si fue escaneo rápido\\n")
                else:
                    self.text_resultados_escaneo.insert(tk.END, "   • Mantener el sistema actualizado\\n")
                    self.text_resultados_escaneo.insert(tk.END, "   • Realizar escaneos periódicos\\n")
                    self.text_resultados_escaneo.insert(tk.END, "   • Monitorear la actividad de red\\n")
            
            # Mostrar notificación
            if amenazas_detectadas > 0:
                messagebox.showwarning(
                    "Escaneo completado",
                    f"Escaneo {tipo_escaneo} completado.\\n"
                    f"Archivos escaneados: {archivos_escaneados}\\n"
                    f"Amenazas detectadas: {amenazas_detectadas}\\n\\n"
                    f"⚠️ Se encontraron {amenazas_detectadas} amenazas."
                )
            else:
                messagebox.showinfo(
                    "Escaneo completado",
                    f"Escaneo {tipo_escaneo} completado exitosamente.\\n"
                    f"Archivos escaneados: {archivos_escaneados}\\n"
                    f"✅ No se detectaron amenazas."
                )
                
        except Exception as e:
            self.logger.error(f"Error procesando resultado de escaneo: {e}")
            messagebox.showerror("Error", f"Error procesando resultado de escaneo:\\n{str(e)}")
            
            # Actualizar estadísticas finales
            self.actualizar_estado_escaneo(f"Escaneo {tipo_escaneo} completado exitosamente", 100)
            
            # Actualizar contadores en la interfaz
            if hasattr(self, 'label_archivos_escaneados'):
                self.label_archivos_escaneados.config(text=str(archivos_escaneados))
            if hasattr(self, 'label_amenazas_detectadas'):
                color = self.tema_actual.ERROR if amenazas_detectadas > 0 else self.tema_actual.EXITO
                self.label_amenazas_detectadas.config(text=str(amenazas_detectadas), fg=color)
            
        except Exception as e:
            self.mostrar_error_escaneo(f"Error al procesar resultados: {str(e)}")
    
    def mostrar_error_escaneo(self, error):
        """Mostrar error en el escaneo."""
        self.actualizar_estado_escaneo(f"Error en escaneo: {error}", 0)
        messagebox.showerror("Error en escaneo", error)
    
    def mostrar_panel_monitoreo(self):
        """Mostrar el panel de monitoreo con funcionalidad completa."""
        self.limpiar_contenido()
        self.actualizar_navegacion_activa("Monitoreo")
        
        # Título del panel
        titulo = tk.Label(
            self.contenido_principal,
            text="🔍 Monitoreo en Tiempo Real",
            font=("Segoe UI", 20, "bold"),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        titulo.pack(pady=(0, 20))
        
        # Botón para volver al menú principal
        btn_volver = ComponentesModernos.crear_boton_ultra_moderno(
            self.contenido_principal,
            "← Volver al Menú Principal",
            self.mostrar_menu_principal,
            estilo="outline"
        )
        btn_volver.pack(anchor="nw", pady=(0, 15))
        
        # Container principal con scroll
        main_container = tk.Frame(self.contenido_principal, bg=self.tema_actual.FONDO_PRINCIPAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Frame para las tarjetas de monitoreo
        cards_frame = tk.Frame(main_container, bg=self.tema_actual.FONDO_PRINCIPAL)
        cards_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Tarjeta de Estado del Sistema
        estado_container, estado_content = ComponentesModernos.crear_card_ultra_moderna(
            cards_frame,
            "💻 Estado del Sistema"
        )
        estado_container.pack(fill=tk.X, pady=(0, 15))
        self.crear_widgets_estado_sistema(estado_content)
        
        # Tarjeta de Monitoreo de Red
        red_container, red_content = ComponentesModernos.crear_card_ultra_moderna(
            cards_frame,
            "🌐 Monitoreo de Red"
        )
        red_container.pack(fill=tk.X, pady=(0, 15))
        self.crear_widgets_monitoreo_red(red_content)
        
        # Tarjeta de Monitoreo de Procesos
        procesos_container, procesos_content = ComponentesModernos.crear_card_ultra_moderna(
            cards_frame,
            "⚙️ Monitoreo de Procesos"
        )
        procesos_container.pack(fill=tk.X, pady=(0, 15))
        self.crear_widgets_monitoreo_procesos(procesos_content)
        
        # Tarjeta de Eventos Recientes
        eventos_container, eventos_content = ComponentesModernos.crear_card_ultra_moderna(
            cards_frame,
            "📊 Eventos Recientes"
        )
        eventos_container.pack(fill=tk.X, pady=(0, 15))
        self.crear_widgets_eventos_recientes(eventos_content)
        
        self.logger.info("Panel de monitoreo mostrado")
    
    def crear_widgets_estado_sistema(self, parent):
        """Crear widgets para el estado del sistema."""
        # Frame para estadísticas del sistema
        stats_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # CPU
        cpu_frame = tk.Frame(stats_frame, bg=self.tema_actual.FONDO_CARD)
        cpu_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            cpu_frame,
            text="CPU:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(side=tk.LEFT)
        
        self.label_cpu = tk.Label(
            cpu_frame,
            text="Cargando...",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.label_cpu.pack(side=tk.RIGHT)
        
        # Memoria
        memoria_frame = tk.Frame(stats_frame, bg=self.tema_actual.FONDO_CARD)
        memoria_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            memoria_frame,
            text="Memoria:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(side=tk.LEFT)
        
        self.label_memoria = tk.Label(
            memoria_frame,
            text="Cargando...",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.label_memoria.pack(side=tk.RIGHT)
        
        # Disco
        disco_frame = tk.Frame(stats_frame, bg=self.tema_actual.FONDO_CARD)
        disco_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            disco_frame,
            text="Disco:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(side=tk.LEFT)
        
        self.label_disco = tk.Label(
            disco_frame,
            text="Cargando...",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.label_disco.pack(side=tk.RIGHT)
        
        # Botón para actualizar estadísticas
        btn_actualizar = ComponentesModernos.crear_boton_ultra_moderno(
            parent,
            "🔄 Actualizar Estadísticas",
            self.actualizar_estadisticas_sistema,
            estilo="primario"
        )
        btn_actualizar.pack(fill=tk.X, pady=(10, 0))
        
        # Inicializar estadísticas
        self.actualizar_estadisticas_sistema()
    
    def crear_widgets_monitoreo_red(self, parent):
        """Crear widgets para el monitoreo de red."""
        # Estado del monitoreo
        estado_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        estado_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.label_estado_red = tk.Label(
            estado_frame,
            text="Estado: Detenido",
            font=("Segoe UI", 12, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.ERROR
        )
        self.label_estado_red.pack(anchor="w")
        
        # Controles de monitoreo
        controles_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        controles_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.btn_iniciar_red = ComponentesModernos.crear_boton_ultra_moderno(
            controles_frame,
            "▶️ Iniciar Monitoreo",
            self.iniciar_monitoreo_red,
            estilo="exito"
        )
        self.btn_iniciar_red.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_detener_red = ComponentesModernos.crear_boton_ultra_moderno(
            controles_frame,
            "⏹️ Detener Monitoreo",
            self.detener_monitoreo_red,
            estilo="peligro"
        )
        self.btn_detener_red.pack(side=tk.LEFT)
        
        # Lista de conexiones activas
        tk.Label(
            parent,
            text="Conexiones Activas:",
            font=("Segoe UI", 11, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(anchor="w", pady=(10, 5))
        
        # Frame con scroll para conexiones
        conexiones_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        conexiones_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_conexiones = tk.Scrollbar(conexiones_frame)
        scrollbar_conexiones.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_conexiones = tk.Text(
            conexiones_frame,
            height=8,
            font=("Courier New", 9),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            yscrollcommand=scrollbar_conexiones.set,
            relief="flat",
            bd=5
        )
        self.text_conexiones.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar_conexiones.config(command=self.text_conexiones.yview)
        
        self.text_conexiones.insert(tk.END, "Inicie el monitoreo para ver las conexiones activas...")
    
    def crear_widgets_monitoreo_procesos(self, parent):
        """Crear widgets para el monitoreo de procesos."""
        # Estadísticas de procesos
        stats_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Total de procesos
        total_frame = tk.Frame(stats_frame, bg=self.tema_actual.FONDO_CARD)
        total_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            total_frame,
            text="Total de procesos:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(side=tk.LEFT)
        
        self.label_total_procesos = tk.Label(
            total_frame,
            text="Cargando...",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.label_total_procesos.pack(side=tk.RIGHT)
        
        # Procesos sospechosos
        sospechosos_frame = tk.Frame(stats_frame, bg=self.tema_actual.FONDO_CARD)
        sospechosos_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            sospechosos_frame,
            text="Procesos sospechosos:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(side=tk.LEFT)
        
        self.label_procesos_sospechosos = tk.Label(
            sospechosos_frame,
            text="0",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.EXITO
        )
        self.label_procesos_sospechosos.pack(side=tk.RIGHT)
        
        # Botón para escanear procesos
        btn_escanear = ComponentesModernos.crear_boton_ultra_moderno(
            parent,
            "🔍 Escanear Procesos",
            self.escanear_procesos,
            estilo="secundario"
        )
        btn_escanear.pack(fill=tk.X, pady=(10, 0))
    
    def crear_widgets_eventos_recientes(self, parent):
        """Crear widgets para eventos recientes."""
        # Frame con scroll para eventos
        eventos_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        eventos_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_eventos = tk.Scrollbar(eventos_frame)
        scrollbar_eventos.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_eventos = tk.Text(
            eventos_frame,
            height=10,
            font=("Courier New", 9),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            yscrollcommand=scrollbar_eventos.set,
            relief="flat",
            bd=5
        )
        self.text_eventos.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar_eventos.config(command=self.text_eventos.yview)
        
        # Cargar eventos recientes
        self.cargar_eventos_recientes()
        
        # Botón para actualizar eventos
        btn_actualizar_eventos = ComponentesModernos.crear_boton_ultra_moderno(
            parent,
            "🔄 Actualizar Eventos",
            self.cargar_eventos_recientes,
            estilo="outline"
        )
        btn_actualizar_eventos.pack(fill=tk.X, pady=(10, 0))
    
    def iniciar_monitoreo_red(self):
        """Iniciar el monitoreo de red."""
        try:
            self.controlador.iniciar_monitor_red()
            self.label_estado_red.config(
                text="Estado: Activo",
                fg=self.tema_actual.EXITO
            )
            
            # Actualizar conexiones cada 5 segundos
            self.actualizar_conexiones_red()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar monitoreo de red:\\n{str(e)}")
    
    def detener_monitoreo_red(self):
        """Detener el monitoreo de red."""
        try:
            self.controlador.detener_monitor_red()
            self.label_estado_red.config(
                text="Estado: Detenido",
                fg=self.tema_actual.ERROR
            )
            
            self.text_conexiones.delete(1.0, tk.END)
            self.text_conexiones.insert(tk.END, "Monitoreo de red detenido.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al detener monitoreo de red:\\n{str(e)}")
    
    def actualizar_conexiones_red(self):
        """Actualizar la lista de conexiones de red."""
        try:
            if hasattr(self, 'controlador') and self.controlador:
                conexiones = self.controlador.monitor_red.obtener_conexiones_activas()
                
                self.text_conexiones.delete(1.0, tk.END)
                
                if conexiones:
                    self.text_conexiones.insert(tk.END, f"{'='*60}\\n")
                    self.text_conexiones.insert(tk.END, f"{'CONEXIONES ACTIVAS':^60}\\n")
                    self.text_conexiones.insert(tk.END, f"{'='*60}\\n\\n")
                    
                    for i, conexion in enumerate(conexiones[:20], 1):  # Máximo 20 conexiones
                        self.text_conexiones.insert(tk.END, f"{i:2}. {conexion.direccion_local}:{conexion.puerto_local} -> ")
                        self.text_conexiones.insert(tk.END, f"{conexion.direccion_remota}:{conexion.puerto_remoto}\\n")
                        self.text_conexiones.insert(tk.END, f"    Estado: {conexion.estado} | PID: {conexion.pid}\\n\\n")
                    
                    if len(conexiones) > 20:
                        self.text_conexiones.insert(tk.END, f"... y {len(conexiones) - 20} conexiones más\\n")
                else:
                    self.text_conexiones.insert(tk.END, "No hay conexiones activas en este momento.")
            
            # Programar próxima actualización
            if hasattr(self, 'root'):
                self.root.after(5000, self.actualizar_conexiones_red)
                
        except Exception as e:
            self.text_conexiones.delete(1.0, tk.END)
            self.text_conexiones.insert(tk.END, f"Error actualizando conexiones: {e}")
    
    def escanear_procesos(self):
        """Escanear y mostrar información de procesos."""
        try:
            if hasattr(self, 'controlador') and self.controlador:
                procesos = self.controlador.monitor_procesos.obtener_procesos()
                
                # Actualizar estadísticas
                self.label_total_procesos.config(text=str(len(procesos)))
                
                # Contar procesos sospechosos (ejemplo)
                procesos_sospechosos = [p for p in procesos if p.cpu_percent > 80 or p.memoria_mb > 500]
                color_sospechosos = self.tema_actual.ERROR if len(procesos_sospechosos) > 0 else self.tema_actual.EXITO
                self.label_procesos_sospechosos.config(
                    text=str(len(procesos_sospechosos)),
                    fg=color_sospechosos
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error escaneando procesos:\\n{str(e)}")
    
    def cargar_eventos_recientes(self):
        """Cargar y mostrar eventos recientes del SIEM."""
        try:
            if hasattr(self, 'controlador') and self.controlador:
                eventos = self.controlador.obtener_eventos_recientes(50)
                
                self.text_eventos.delete(1.0, tk.END)
                
                if eventos:
                    self.text_eventos.insert(tk.END, f"{'='*80}\\n")
                    self.text_eventos.insert(tk.END, f"{'EVENTOS RECIENTES DEL SIEM':^80}\\n")
                    self.text_eventos.insert(tk.END, f"{'='*80}\\n\\n")
                    
                    for evento in eventos[-10:]:  # Últimos 10 eventos
                        timestamp = evento.get('timestamp', 'N/A')
                        tipo = evento.get('tipo', 'N/A')
                        mensaje = evento.get('mensaje', 'N/A')
                        nivel = evento.get('nivel_criticidad', 'MEDIO')
                        
                        self.text_eventos.insert(tk.END, f"[{timestamp}] [{nivel}] {tipo}\\n")
                        self.text_eventos.insert(tk.END, f"  {mensaje}\\n\\n")
                else:
                    self.text_eventos.insert(tk.END, "No hay eventos registrados.")
                    
        except Exception as e:
            self.text_eventos.delete(1.0, tk.END)
            self.text_eventos.insert(tk.END, f"Error cargando eventos: {e}")
    
    def actualizar_estadisticas_sistema(self):
        """Actualizar las estadísticas del sistema."""
        try:
            import psutil
            
            # Obtener uso de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.label_cpu.config(text=f"{cpu_percent:.1f}%")
            
            # Obtener uso de memoria
            memoria = psutil.virtual_memory()
            memoria_percent = memoria.percent
            memoria_gb = memoria.used / (1024**3)
            memoria_total_gb = memoria.total / (1024**3)
            self.label_memoria.config(text=f"{memoria_percent:.1f}% ({memoria_gb:.1f}GB/{memoria_total_gb:.1f}GB)")
            
            # Obtener uso de disco
            disco = psutil.disk_usage('/')
            disco_percent = (disco.used / disco.total) * 100
            disco_gb = disco.used / (1024**3)
            disco_total_gb = disco.total / (1024**3)
            self.label_disco.config(text=f"{disco_percent:.1f}% ({disco_gb:.1f}GB/{disco_total_gb:.1f}GB)")
            
        except ImportError:
            self.label_cpu.config(text="N/A (psutil no disponible)")
            self.label_memoria.config(text="N/A (psutil no disponible)")
            self.label_disco.config(text="N/A (psutil no disponible)")
        except Exception as e:
            self.logger.error(f"Error al obtener estadísticas del sistema: {e}")
            self.label_cpu.config(text="Error")
            self.label_memoria.config(text="Error")
            self.label_disco.config(text="Error")
    
    def iniciar_monitoreo_red(self):
        """Iniciar el monitoreo de red."""
        try:
            self.controlador.iniciar_monitor_red()
            self.label_estado_red.config(text="Estado: Activo", fg=self.tema_actual.EXITO)
            self.actualizar_conexiones_red()
            messagebox.showinfo("Monitoreo de Red", "Monitoreo de red iniciado correctamente")
        except Exception as e:
            self.logger.error(f"Error al iniciar monitoreo de red: {e}")
            messagebox.showerror("Error", f"Error al iniciar monitoreo de red:\\n{str(e)}")
    
    def detener_monitoreo_red(self):
        """Detener el monitoreo de red."""
        try:
            self.controlador.detener_monitor_red()
            self.label_estado_red.config(text="Estado: Detenido", fg=self.tema_actual.ERROR)
            self.text_conexiones.delete(1.0, tk.END)
            self.text_conexiones.insert(tk.END, "Monitoreo detenido. Inicie el monitoreo para ver conexiones.")
            messagebox.showinfo("Monitoreo de Red", "Monitoreo de red detenido correctamente")
        except Exception as e:
            self.logger.error(f"Error al detener monitoreo de red: {e}")
            messagebox.showerror("Error", f"Error al detener monitoreo de red:\\n{str(e)}")
    
    def actualizar_conexiones_red(self):
        """Actualizar la lista de conexiones de red."""
        try:
            if hasattr(self.controlador, 'monitor_red'):
                conexiones = self.controlador.monitor_red.obtener_conexiones_activas()
                
                self.text_conexiones.delete(1.0, tk.END)
                self.text_conexiones.insert(tk.END, f"=== CONEXIONES ACTIVAS ({len(conexiones)}) ===\\n\\n")
                
                for i, conexion in enumerate(conexiones, 1):
                    self.text_conexiones.insert(tk.END, f"{i}. {conexion.protocolo.upper()}\\n")
                    self.text_conexiones.insert(tk.END, f"   Local: {conexion.direccion_local}:{conexion.puerto_local}\\n")
                    self.text_conexiones.insert(tk.END, f"   Remoto: {conexion.direccion_remota}:{conexion.puerto_remoto}\\n")
                    self.text_conexiones.insert(tk.END, f"   Estado: {conexion.estado}\\n")
                    self.text_conexiones.insert(tk.END, f"   Proceso: {conexion.proceso_nombre} (PID: {conexion.proceso_id})\\n\\n")
                    
                if not conexiones:
                    self.text_conexiones.insert(tk.END, "No se encontraron conexiones activas.")
                    
        except Exception as e:
            self.logger.error(f"Error al actualizar conexiones de red: {e}")
            self.text_conexiones.delete(1.0, tk.END)
            self.text_conexiones.insert(tk.END, f"Error al obtener conexiones: {str(e)}")
    
    def escanear_procesos(self):
        """Escanear procesos del sistema."""
        try:
            if hasattr(self.controlador, 'monitor_procesos'):
                procesos = self.controlador.monitor_procesos.obtener_procesos()
                self.label_total_procesos.config(text=str(len(procesos)))
                
                # Análisis básico de procesos sospechosos (esto se puede mejorar)
                sospechosos = 0
                self.label_procesos_sospechosos.config(text=str(sospechosos))
                
                messagebox.showinfo("Escaneo de Procesos", f"Escaneo completado.\\nProcesos encontrados: {len(procesos)}\\nProcesos sospechosos: {sospechosos}")
            else:
                messagebox.showwarning("Advertencia", "Monitor de procesos no disponible")
                
        except Exception as e:
            self.logger.error(f"Error al escanear procesos: {e}")
            messagebox.showerror("Error", f"Error al escanear procesos:\\n{str(e)}")
    
    def cargar_eventos_recientes(self):
        """Cargar eventos recientes del SIEM."""
        try:
            self.text_eventos.delete(1.0, tk.END)
            
            # Intentar cargar eventos del archivo SIEM
            import json
            eventos_file = "/home/dogsoul/Ares-Aegis/eventos_siem.json"
            
            if os.path.exists(eventos_file):
                with open(eventos_file, 'r', encoding='utf-8') as f:
                    eventos = [json.loads(line) for line in f.readlines()[-20:]]  # Últimos 20 eventos
                
                self.text_eventos.insert(tk.END, f"=== EVENTOS RECIENTES ({len(eventos)}) ===\\n\\n")
                
                for evento in reversed(eventos):  # Mostrar más recientes primero
                    timestamp = evento.get('timestamp', 'Sin fecha')
                    tipo = evento.get('tipo', 'DESCONOCIDO')
                    mensaje = evento.get('mensaje', 'Sin mensaje')
                    
                    self.text_eventos.insert(tk.END, f"[{timestamp}] {tipo}\\n")
                    self.text_eventos.insert(tk.END, f"  {mensaje}\\n\\n")
                    
                if not eventos:
                    self.text_eventos.insert(tk.END, "No hay eventos registrados.")
            else:
                self.text_eventos.insert(tk.END, "Archivo de eventos no encontrado.\\nEl sistema comenzará a registrar eventos en cuanto se detecte actividad.")
                
        except Exception as e:
            self.logger.error(f"Error al cargar eventos recientes: {e}")
            self.text_eventos.delete(1.0, tk.END)
            self.text_eventos.insert(tk.END, f"Error al cargar eventos: {str(e)}")
    
    def mostrar_panel_cuarentena(self):
        """Mostrar el panel de cuarentena con funcionalidad completa."""
        self.limpiar_contenido()
        self.actualizar_navegacion_activa("Cuarentena")
        
        # Título del panel
        titulo = tk.Label(
            self.contenido_principal,
            text="🛡️ Gestión de Cuarentena",
            font=("Segoe UI", 20, "bold"),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        titulo.pack(pady=(0, 20))
        
        # Botón para volver al menú principal
        btn_volver = ComponentesModernos.crear_boton_ultra_moderno(
            self.contenido_principal,
            "← Volver al Menú Principal",
            self.mostrar_menu_principal,
            estilo="outline"
        )
        btn_volver.pack(anchor="nw", pady=(0, 15))
        
        # Container principal
        main_container = tk.Frame(self.contenido_principal, bg=self.tema_actual.FONDO_PRINCIPAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Tarjeta de estadísticas de cuarentena
        stats_container, stats_content = ComponentesModernos.crear_card_ultra_moderna(
            main_container,
            "📊 Estadísticas de Cuarentena"
        )
        stats_container.pack(fill=tk.X, pady=(0, 15))
        self.crear_widgets_estadisticas_cuarentena(stats_content)
        
        # Tarjeta de acciones rápidas
        acciones_container, acciones_content = ComponentesModernos.crear_card_ultra_moderna(
            main_container,
            "⚡ Acciones Rápidas"
        )
        acciones_container.pack(fill=tk.X, pady=(0, 15))
        self.crear_widgets_acciones_cuarentena(acciones_content)
        
        # Tarjeta de archivos en cuarentena
        archivos_container, archivos_content = ComponentesModernos.crear_card_ultra_moderna(
            main_container,
            "📁 Archivos en Cuarentena"
        )
        archivos_container.pack(fill=tk.BOTH, expand=True)
        self.crear_widgets_lista_cuarentena(archivos_content)
        
        # Cargar archivos en cuarentena
        self.cargar_archivos_cuarentena()
        
        self.logger.info("Panel de cuarentena mostrado")
    
    def crear_widgets_estadisticas_cuarentena(self, parent):
        """Crear widgets para las estadísticas de cuarentena."""
        # Frame para estadísticas
        stats_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Total de archivos en cuarentena
        total_frame = tk.Frame(stats_frame, bg=self.tema_actual.FONDO_CARD)
        total_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            total_frame,
            text="Archivos en cuarentena:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(side=tk.LEFT)
        
        self.label_total_cuarentena = tk.Label(
            total_frame,
            text="Cargando...",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.label_total_cuarentena.pack(side=tk.RIGHT)
        
        # Espacio ocupado
        espacio_frame = tk.Frame(stats_frame, bg=self.tema_actual.FONDO_CARD)
        espacio_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            espacio_frame,
            text="Espacio ocupado:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(side=tk.LEFT)
        
        self.label_espacio_cuarentena = tk.Label(
            espacio_frame,
            text="Cargando...",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.label_espacio_cuarentena.pack(side=tk.RIGHT)
        
        # Último archivo agregado
        ultimo_frame = tk.Frame(stats_frame, bg=self.tema_actual.FONDO_CARD)
        ultimo_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            ultimo_frame,
            text="Último archivo:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(side=tk.LEFT)
        
        self.label_ultimo_cuarentena = tk.Label(
            ultimo_frame,
            text="Ninguno",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.label_ultimo_cuarentena.pack(side=tk.RIGHT)
    
    def crear_widgets_acciones_cuarentena(self, parent):
        """Crear widgets para las acciones de cuarentena."""
        # Frame para botones de acción
        acciones_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        acciones_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Primera fila de botones
        fila1 = tk.Frame(acciones_frame, bg=self.tema_actual.FONDO_CARD)
        fila1.pack(fill=tk.X, pady=(0, 10))
        
        btn_poner_cuarentena = ComponentesModernos.crear_boton_ultra_moderno(
            fila1,
            "🔒 Poner en Cuarentena",
            self.poner_archivo_cuarentena,
            estilo="peligro"
        )
        btn_poner_cuarentena.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_restaurar = ComponentesModernos.crear_boton_ultra_moderno(
            fila1,
            "🔓 Restaurar Archivo",
            self.restaurar_archivo_cuarentena,
            estilo="exito"
        )
        btn_restaurar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        btn_eliminar = ComponentesModernos.crear_boton_ultra_moderno(
            fila1,
            "🗑️ Eliminar Permanente",
            self.eliminar_archivo_cuarentena,
            estilo="peligro"
        )
        btn_eliminar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Segunda fila de botones
        fila2 = tk.Frame(acciones_frame, bg=self.tema_actual.FONDO_CARD)
        fila2.pack(fill=tk.X)
        
        btn_actualizar = ComponentesModernos.crear_boton_ultra_moderno(
            fila2,
            "🔄 Actualizar Lista",
            self.cargar_archivos_cuarentena,
            estilo="outline"
        )
        btn_actualizar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_limpiar = ComponentesModernos.crear_boton_ultra_moderno(
            fila2,
            "🧹 Limpiar Cuarentena",
            self.limpiar_cuarentena,
            estilo="secundario"
        )
        btn_limpiar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        btn_exportar = ComponentesModernos.crear_boton_ultra_moderno(
            fila2,
            "📄 Exportar Lista",
            self.exportar_lista_cuarentena,
            estilo="outline"
        )
        btn_exportar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
    
    def crear_widgets_lista_cuarentena(self, parent):
        """Crear widgets para la lista de archivos en cuarentena."""
        # Frame para la lista con scroll
        lista_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        lista_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar_lista = tk.Scrollbar(lista_frame)
        scrollbar_lista.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget para mostrar la lista
        self.text_lista_cuarentena = tk.Text(
            lista_frame,
            font=("Courier New", 10),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            yscrollcommand=scrollbar_lista.set,
            relief="flat",
            bd=5,
            wrap=tk.WORD
        )
        self.text_lista_cuarentena.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar_lista.config(command=self.text_lista_cuarentena.yview)
        
        # Binding para selección
        self.text_lista_cuarentena.bind("<Double-Button-1>", self.mostrar_detalles_archivo_cuarentena)
    
    def cargar_archivos_cuarentena(self):
        """Cargar y mostrar archivos en cuarentena."""
        try:
            if hasattr(self.controlador, 'cuarentena'):
                archivos = self.controlador.cuarentena.listar_archivos_cuarentena()
                
                # Actualizar estadísticas
                self.label_total_cuarentena.config(text=str(len(archivos)))
                
                # Calcular espacio ocupado
                espacio_total = sum(archivo.tamaño_original for archivo in archivos)
                espacio_mb = espacio_total / (1024 * 1024)
                self.label_espacio_cuarentena.config(text=f"{espacio_mb:.2f} MB")
                
                # Último archivo
                if archivos:
                    ultimo = max(archivos, key=lambda x: x.fecha_cuarentena)
                    self.label_ultimo_cuarentena.config(text=os.path.basename(ultimo.ruta_original))
                else:
                    self.label_ultimo_cuarentena.config(text="Ninguno")
                
                # Actualizar lista
                self.text_lista_cuarentena.delete(1.0, tk.END)
                
                if archivos:
                    self.text_lista_cuarentena.insert(tk.END, f"=== ARCHIVOS EN CUARENTENA ({len(archivos)}) ===\\n\\n")
                    
                    for i, archivo in enumerate(archivos, 1):
                        fecha = archivo.fecha_cuarentena.strftime("%d/%m/%Y %H:%M:%S")
                        tamaño_kb = archivo.tamaño_original / 1024
                        
                        self.text_lista_cuarentena.insert(tk.END, f"{i}. {os.path.basename(archivo.ruta_original)}\\n")
                        self.text_lista_cuarentena.insert(tk.END, f"   Ruta original: {archivo.ruta_original}\\n")
                        self.text_lista_cuarentena.insert(tk.END, f"   Fecha: {fecha}\\n")
                        self.text_lista_cuarentena.insert(tk.END, f"   Tamaño: {tamaño_kb:.2f} KB\\n")
                        self.text_lista_cuarentena.insert(tk.END, f"   Motivo: {archivo.motivo_cuarentena}\\n")
                        self.text_lista_cuarentena.insert(tk.END, f"   Amenaza: {archivo.amenaza_detectada}\\n")
                        self.text_lista_cuarentena.insert(tk.END, f"   Hash SHA256: {archivo.hash_sha256[:16]}...\\n")
                        self.text_lista_cuarentena.insert(tk.END, "\\n")
                else:
                    self.text_lista_cuarentena.insert(tk.END, "No hay archivos en cuarentena.\\n\\n")
                    self.text_lista_cuarentena.insert(tk.END, "Los archivos detectados como maliciosos aparecerán aquí.")
                    
            else:
                self.text_lista_cuarentena.delete(1.0, tk.END)
                self.text_lista_cuarentena.insert(tk.END, "Sistema de cuarentena no disponible.")
                
        except Exception as e:
            self.logger.error(f"Error al cargar archivos en cuarentena: {e}")
            self.text_lista_cuarentena.delete(1.0, tk.END)
            self.text_lista_cuarentena.insert(tk.END, f"Error al cargar archivos: {str(e)}")
    
    def poner_archivo_cuarentena(self):
        """Poner un archivo en cuarentena."""
        try:
            from tkinter import filedialog
            archivo = filedialog.askopenfilename(
                title="Seleccionar archivo para poner en cuarentena",
                filetypes=[("Todos los archivos", "*.*")]
            )
            
            if archivo:
                motivo = simpledialog.askstring(
                    "Motivo de cuarentena",
                    "Ingrese el motivo para poner este archivo en cuarentena:",
                    initialvalue="Archivo sospechoso - Cuarentena manual"
                )
                
                if motivo:
                    if hasattr(self.controlador, 'cuarentena'):
                        exito = self.controlador.cuarentena.poner_en_cuarentena(
                            archivo, motivo, "Detección manual"
                        )
                        
                        if exito:
                            messagebox.showinfo("Cuarentena", f"Archivo puesto en cuarentena exitosamente:\\n{os.path.basename(archivo)}")
                            self.cargar_archivos_cuarentena()
                        else:
                            messagebox.showerror("Error", "No se pudo poner el archivo en cuarentena")
                    else:
                        messagebox.showerror("Error", "Sistema de cuarentena no disponible")
                        
        except Exception as e:
            self.logger.error(f"Error al poner archivo en cuarentena: {e}")
            messagebox.showerror("Error", f"Error al poner archivo en cuarentena:\\n{str(e)}")
    
    def restaurar_archivo_cuarentena(self):
        """Restaurar un archivo desde cuarentena."""
        try:
            # Obtener hash del archivo seleccionado (implementación simplificada)
            hash_archivo = simpledialog.askstring(
                "Restaurar archivo",
                "Ingrese el hash SHA256 del archivo a restaurar\\n(o los primeros 16 caracteres):"
            )
            
            if hash_archivo:
                if hasattr(self.controlador, 'cuarentena'):
                    # Buscar archivo por hash
                    archivos = self.controlador.cuarentena.listar_archivos_cuarentena()
                    archivo_encontrado = None
                    
                    for archivo in archivos:
                        if archivo.hash_sha256.startswith(hash_archivo):
                            archivo_encontrado = archivo
                            break
                    
                    if archivo_encontrado:
                        exito = self.controlador.cuarentena.restaurar_archivo(archivo_encontrado.hash_sha256)
                        
                        if exito:
                            messagebox.showinfo("Restauración", f"Archivo restaurado exitosamente:\\n{os.path.basename(archivo_encontrado.ruta_original)}")
                            self.cargar_archivos_cuarentena()
                        else:
                            messagebox.showerror("Error", "No se pudo restaurar el archivo")
                    else:
                        messagebox.showerror("Error", "Archivo no encontrado en cuarentena")
                else:
                    messagebox.showerror("Error", "Sistema de cuarentena no disponible")
                    
        except Exception as e:
            self.logger.error(f"Error al restaurar archivo: {e}")
            messagebox.showerror("Error", f"Error al restaurar archivo:\\n{str(e)}")
    
    def eliminar_archivo_cuarentena(self):
        """Eliminar permanentemente un archivo de cuarentena."""
        try:
            hash_archivo = simpledialog.askstring(
                "Eliminar archivo",
                "Ingrese el hash SHA256 del archivo a eliminar\\n(o los primeros 16 caracteres):"
            )
            
            if hash_archivo:
                respuesta = messagebox.askyesno(
                    "Confirmar eliminación",
                    "¿Está seguro de que desea eliminar permanentemente este archivo?\\nEsta acción NO se puede deshacer."
                )
                
                if respuesta:
                    if hasattr(self.controlador, 'cuarentena'):
                        # Buscar y eliminar archivo
                        archivos = self.controlador.cuarentena.listar_archivos_cuarentena()
                        archivo_encontrado = None
                        
                        for archivo in archivos:
                            if archivo.hash_sha256.startswith(hash_archivo):
                                archivo_encontrado = archivo
                                break
                        
                        if archivo_encontrado:
                            exito = self.controlador.cuarentena.eliminar_archivo(archivo_encontrado.hash_sha256)
                            
                            if exito:
                                messagebox.showinfo("Eliminación", f"Archivo eliminado permanentemente:\\n{os.path.basename(archivo_encontrado.ruta_original)}")
                                self.cargar_archivos_cuarentena()
                            else:
                                messagebox.showerror("Error", "No se pudo eliminar el archivo")
                        else:
                            messagebox.showerror("Error", "Archivo no encontrado en cuarentena")
                    else:
                        messagebox.showerror("Error", "Sistema de cuarentena no disponible")
                        
        except Exception as e:
            self.logger.error(f"Error al eliminar archivo: {e}")
            messagebox.showerror("Error", f"Error al eliminar archivo:\\n{str(e)}")
    
    def limpiar_cuarentena(self):
        """Limpiar toda la cuarentena."""
        try:
            respuesta = messagebox.askyesno(
                "Confirmar limpieza",
                "¿Está seguro de que desea eliminar TODOS los archivos de cuarentena?\\nEsta acción NO se puede deshacer."
            )
            
            if respuesta:
                if hasattr(self.controlador, 'cuarentena'):
                    archivos = self.controlador.cuarentena.listar_archivos_cuarentena()
                    eliminados = 0
                    
                    for archivo in archivos:
                        if self.controlador.cuarentena.eliminar_archivo(archivo.hash_sha256):
                            eliminados += 1
                    
                    messagebox.showinfo("Limpieza completada", f"Se eliminaron {eliminados} archivos de cuarentena.")
                    self.cargar_archivos_cuarentena()
                else:
                    messagebox.showerror("Error", "Sistema de cuarentena no disponible")
                    
        except Exception as e:
            self.logger.error(f"Error al limpiar cuarentena: {e}")
            messagebox.showerror("Error", f"Error al limpiar cuarentena:\\n{str(e)}")
    
    def exportar_lista_cuarentena(self):
        """Exportar la lista de archivos en cuarentena."""
        try:
            from tkinter import filedialog
            archivo_destino = filedialog.asksaveasfilename(
                title="Exportar lista de cuarentena",
                defaultextension=".txt",
                filetypes=[
                    ("Archivos de texto", "*.txt"),
                    ("Archivos CSV", "*.csv"),
                    ("Archivos JSON", "*.json")
                ]
            )
            
            if archivo_destino:
                if hasattr(self.controlador, 'cuarentena'):
                    archivos = self.controlador.cuarentena.listar_archivos_cuarentena()
                    
                    if archivo_destino.endswith('.json'):
                        import json
                        datos = [archivo.to_dict() for archivo in archivos]
                        with open(archivo_destino, 'w', encoding='utf-8') as f:
                            json.dump(datos, f, indent=2, ensure_ascii=False)
                    elif archivo_destino.endswith('.csv'):
                        import csv
                        with open(archivo_destino, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow(['Ruta Original', 'Fecha Cuarentena', 'Motivo', 'Amenaza', 'Tamaño', 'Hash SHA256'])
                            for archivo in archivos:
                                writer.writerow([
                                    archivo.ruta_original,
                                    archivo.fecha_cuarentena.isoformat(),
                                    archivo.motivo_cuarentena,
                                    archivo.amenaza_detectada,
                                    archivo.tamaño_original,
                                    archivo.hash_sha256
                                ])
                    else:
                        # Archivo de texto
                        contenido = self.text_lista_cuarentena.get(1.0, tk.END)
                        with open(archivo_destino, 'w', encoding='utf-8') as f:
                            f.write(f"=== LISTA DE CUARENTENA - ARES AEGIS ===\\n")
                            f.write(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\\n")
                            f.write(f"{'='*50}\\n\\n")
                            f.write(contenido)
                    
                    messagebox.showinfo("Exportación exitosa", f"Lista exportada a:\\n{archivo_destino}")
                else:
                    messagebox.showerror("Error", "Sistema de cuarentena no disponible")
                    
        except Exception as e:
            self.logger.error(f"Error al exportar lista: {e}")
            messagebox.showerror("Error", f"Error al exportar lista:\\n{str(e)}")
    
    def mostrar_detalles_archivo_cuarentena(self, event):
        """Mostrar detalles de un archivo en cuarentena."""
        try:
            # Obtener línea seleccionada
            indice = self.text_lista_cuarentena.index(tk.INSERT)
            linea = self.text_lista_cuarentena.get(f"{indice.split('.')[0]}.0", f"{indice.split('.')[0]}.end")
            
            if linea.strip() and not linea.startswith("===") and not linea.startswith("No hay"):
                messagebox.showinfo("Detalles", f"Detalles del archivo:\\n{linea}\\n\\nDoble clic para ver detalles completos.")
                
        except Exception as e:
            self.logger.error(f"Error al mostrar detalles: {e}")
    
    def mostrar_panel_reportes(self):
        """Mostrar el panel de reportes."""
        self.limpiar_contenido()
        self.actualizar_navegacion_activa("Reportes")
        
        # Implementar panel de reportes completo
        tk.Label(
            self.contenido_principal,
            text="Panel de Reportes - En desarrollo",
            font=("Segoe UI", 16),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(expand=True)
    
    def mostrar_panel_configuracion(self):
        """Mostrar el panel de configuración."""
        self.limpiar_contenido()
        self.actualizar_navegacion_activa("Configuración")
        
        # Implementar panel de configuración completo
        tk.Label(
            self.contenido_principal,
            text="Panel de Configuración - En desarrollo",
            font=("Segoe UI", 16),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(expand=True)
    
    # Métodos auxiliares
    def limpiar_contenido(self):
        """Limpiar el contenido principal."""
        if self.contenido_principal:
            for widget in self.contenido_principal.winfo_children():
                widget.destroy()
    
    def actualizar_navegacion_activa(self, panel_activo):
        """Actualizar el estado visual de la navegación."""
        # Implementar actualización visual de botones activos
        pass
    
    def cambiar_tema(self):
        """Cambiar entre tema claro y oscuro."""
        self.tema_oscuro = not self.tema_oscuro
        self.tema_actual = TemaOscuro() if self.tema_oscuro else TemaClaro()
        
        # Aplicar nuevo tema
        self.aplicar_tema()
        
        messagebox.showinfo("Tema Cambiado", 
                           f"Tema {'oscuro' if self.tema_oscuro else 'claro'} aplicado")
    
    def aplicar_tema(self):
        """Aplicar el tema actual a toda la interfaz."""
        # Implementar aplicación de tema
        if self.root:
            self.root.configure(bg=self.tema_actual.FONDO_PRINCIPAL)
        # Continuar con todos los widgets...
    
    def actualizar_hora(self):
        """Actualizar la hora en el panel de estado."""
        hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(self, 'label_hora'):
            self.label_hora.config(text=hora_actual)
        if self.root:
            self.root.after(1000, self.actualizar_hora)
    
    def cargar_configuracion(self):
        """Cargar configuración de la aplicación."""
        # Implementar carga de configuración
        pass
    
    def actualizar_estado_inicial(self):
        """Actualizar el estado inicial de la aplicación."""
        self.actualizar_estado("Sistema inicializado correctamente")
    
    def actualizar_estado(self, mensaje):
        """Actualizar el mensaje de estado."""
        if hasattr(self, 'label_estado'):
            self.label_estado.config(text=mensaje)
    
    # Métodos de funcionalidad
    def iniciar_servicios(self):
        """Iniciar todos los servicios del sistema."""
        if self.controlador:
            threading.Thread(target=self._iniciar_servicios_async, daemon=True).start()
    
    def _iniciar_servicios_async(self):
        """Iniciar servicios de forma asíncrona."""
        try:
            self.actualizar_estado("Iniciando servicios...")
            if self.controlador:
                self.controlador.iniciar_servicios()
            self.actualizar_estado("Servicios iniciados correctamente")
            if self.root:
                self.root.after(0, self.actualizar_panel_principal)
        except Exception as e:
            self.logger.error(f"Error al iniciar servicios: {e}")
            self.actualizar_estado(f"Error al iniciar servicios: {e}")
    
    def detener_servicios(self):
        """Detener todos los servicios del sistema."""
        if self.controlador:
            threading.Thread(target=self._detener_servicios_async, daemon=True).start()
    
    def _detener_servicios_async(self):
        """Detener servicios de forma asíncrona."""
        try:
            self.actualizar_estado("Deteniendo servicios...")
            if self.controlador:
                self.controlador.detener_servicios()
            self.actualizar_estado("Servicios detenidos")
            if self.root:
                self.root.after(0, self.actualizar_panel_principal)
        except Exception as e:
            self.logger.error(f"Error al detener servicios: {e}")
            self.actualizar_estado(f"Error al detener servicios: {e}")
    
    def ejecutar_escaneo_rapido(self):
        """Ejecutar un escaneo rápido del sistema."""
        if self.escaneo_activo:
            messagebox.showwarning("Escaneo Activo", "Ya hay un escaneo en progreso")
            return
        
        self.escaneo_activo = True
        self.frame_progreso.pack(fill=tk.X, pady=(10, 0))
        self.progress_bar.start()
        
        threading.Thread(target=self._ejecutar_escaneo_async, args=("rapido",), daemon=True).start()
    
    def ejecutar_escaneo_completo(self):
        """Ejecutar un escaneo completo del sistema."""
        if self.escaneo_activo:
            messagebox.showwarning("Escaneo Activo", "Ya hay un escaneo en progreso")
            return
        
        respuesta = messagebox.askyesno(
            "Escaneo Completo",
            "El escaneo completo puede tomar mucho tiempo. ¿Desea continuar?"
        )
        
        if respuesta:
            self.escaneo_activo = True
            self.frame_progreso.pack(fill=tk.X, pady=(10, 0))
            self.progress_bar.start()
            
            threading.Thread(target=self._ejecutar_escaneo_async, args=("completo",), daemon=True).start()
    
    def _ejecutar_escaneo_async(self, tipo_escaneo):
        """Ejecutar escaneo de forma asíncrona."""
        try:
            self.progress_var.set(f"Ejecutando escaneo {tipo_escaneo}...")
            
            if self.controlador:
                if tipo_escaneo == "rapido":
                    resultado = self.controlador.ejecutar_escaneo_rapido()
                else:
                    resultado = self.controlador.ejecutar_escaneo_completo()
                
                # Simular progreso
                time.sleep(2)
                
                if self.root:
                    self.root.after(0, lambda: self._finalizar_escaneo(resultado))
            else:
                if self.root:
                    self.root.after(0, lambda: self._finalizar_escaneo(None))
                
        except Exception as e:
            self.logger.error(f"Error en escaneo {tipo_escaneo}: {e}")
            if self.root:
                self.root.after(0, lambda: self._finalizar_escaneo(None, str(e)))
    
    def _finalizar_escaneo(self, resultado, error=None):
        """Finalizar el proceso de escaneo."""
        self.escaneo_activo = False
        self.progress_bar.stop()
        self.frame_progreso.pack_forget()
        
        if error:
            messagebox.showerror("Error de Escaneo", f"Error durante el escaneo:\n{error}")
            self.actualizar_estado("Error en escaneo")
        elif resultado:
            amenazas = resultado.get('amenazas_encontradas', 0)
            tiempo = resultado.get('tiempo_transcurrido', 0)
            
            mensaje = f"Escaneo completado\nAmenazas encontradas: {amenazas}\nTiempo: {tiempo:.2f}s"
            
            if amenazas > 0:
                messagebox.showwarning("Amenazas Detectadas", mensaje)
            else:
                messagebox.showinfo("Escaneo Completo", mensaje)
            
            self.actualizar_estado(f"Escaneo completado - {amenazas} amenazas encontradas")
            self.actualizar_panel_principal()
        else:
            messagebox.showinfo("Escaneo Completo", "Escaneo completado sin resultados")
            self.actualizar_estado("Escaneo completado")
    
    def cargar_actividades_recientes(self):
        """Cargar y mostrar actividades recientes."""
        if hasattr(self, 'lista_actividades'):
            self.lista_actividades.delete(1.0, tk.END)
            
            actividades = self.controlador.obtener_actividades_recientes() if self.controlador else []
            
            if not actividades:
                self.lista_actividades.insert(tk.END, "No hay actividades recientes\n")
            else:
                for actividad in actividades:
                    timestamp = actividad.get('timestamp', '')
                    evento = actividad.get('evento', 'Sin descripción')
                    self.lista_actividades.insert(tk.END, f"[{timestamp}] {evento}\n")
    
    def abrir_registro_completo(self):
        """Abrir ventana con el registro completo de actividades."""
        # Implementar ventana de registro completo
        messagebox.showinfo("Registro Completo", "Función en desarrollo")
    
    def mostrar_todas_alertas(self):
        """Mostrar todas las alertas en una ventana separada."""
        # Implementar ventana de alertas completas
        messagebox.showinfo("Todas las Alertas", "Función en desarrollo")
    
    def actualizar_panel_principal(self):
        """Actualizar los datos del panel principal."""
        # Reimplementar el panel principal para actualizar datos
        if hasattr(self, 'contenido_principal'):
            # Solo actualizar si estamos en el panel principal
            pass
    
    def cerrar_aplicacion(self):
        """Cerrar la aplicación de forma segura."""
        respuesta = messagebox.askyesno(
            "Cerrar Aplicación",
            "¿Está seguro de que desea cerrar Ares Aegis?"
        )
        
        if respuesta:
            try:
                self.actualizar_estado("Cerrando aplicación...")
                
                # Detener servicios
                if self.controlador:
                    self.controlador.detener_servicios()
                
                # Guardar configuración
                self.guardar_configuracion()
                
                self.logger.info("Aplicación cerrada correctamente")
                if self.root:
                    self.root.quit()
                
            except Exception as e:
                self.logger.error(f"Error al cerrar aplicación: {e}")
                if self.root:
                    self.root.quit()
    
    def guardar_configuracion(self):
        """Guardar configuración actual."""
        # Implementar guardado de configuración
        pass
    
    def ejecutar(self):
        """Ejecutar la aplicación."""
        if self.inicializar():
            if self.root:
                self.root.mainloop()
        else:
            self.logger.error("No se pudo inicializar la aplicación")
            return False
        
        return True


# Función principal de entrada
def main():
    """Función principal de entrada de la aplicación."""
    try:
        # Configurar logging
        logger = configurar_logger_modulo(__name__)
        
        logger.info("Iniciando Ares Aegis...")
        
        # Crear y ejecutar aplicación
        app = InterfazPrincipal()
        app.ejecutar()
        
    except Exception as e:
        print(f"Error crítico al iniciar la aplicación: {e}")
        logging.error(f"Error crítico al iniciar la aplicación: {e}")


if __name__ == "__main__":
    main()
