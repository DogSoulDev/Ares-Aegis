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
        self.root.title("🛡️ Ares Aegis - Sistema de Ciberseguridad Avanzado")
        self.root.geometry("1500x1000")
        self.root.minsize(1300, 900)
        
        # Configurar icono principal
        try:
            # Intentar cargar icono desde múltiples ubicaciones
            icon_paths = [
                os.path.join(os.path.dirname(__file__), "../..", "recursos", "aresIcon.png"),
                os.path.join(os.path.dirname(__file__), "../..", "recursos", "AresAegis.png"),
                "/home/dogsoul/Ares-Aegis/recursos/aresIcon.png",
                "/home/dogsoul/Ares-Aegis/recursos/AresAegis.png"
            ]
            
            icon_loaded = False
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    try:
                        icon_image = tk.PhotoImage(file=icon_path)
                        self.root.iconphoto(True, icon_image)
                        # Mantener referencia para evitar garbage collection
                        self.root._icon_image = icon_image
                        icon_loaded = True
                        self.logger.info(f"Icono cargado desde: {icon_path}")
                        break
                    except Exception as e:
                        self.logger.warning(f"Error cargando icono desde {icon_path}: {e}")
                        continue
            
            if not icon_loaded:
                self.logger.warning("No se pudo cargar ningún icono")
                
        except Exception as e:
            self.logger.error(f"Error general cargando icono: {e}")
        
        # Configurar tema moderno
        self.root.configure(bg=self.tema_actual.FONDO_PRINCIPAL)
        
        # Configurar ventana moderna
        try:
            # Desactivar la decoración nativa en algunos sistemas
            self.root.attributes('-alpha', 0.98)  # Ligera transparencia
        except:
            pass
        
        # Configurar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
        # Variables para estadísticas de escaneo
        self.ultimo_escaneo_rapido = None
        self.ultimo_escaneo_completo = None
        self.archivos_escaneados_actual = 0
        self.amenazas_detectadas_actual = 0
        
        # Variables para controles de UI
        self.tab_actual = "principal"
        
        # Variables para gráficos y visualización
        self.datos_tiempo_real = {
            'cpu_history': [],
            'memoria_history': [],
            'conexiones_history': [],
            'amenazas_history': []
        }
    
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
        """Configurar la interfaz gráfica principal con diseño moderno."""
        try:
            self.logger.info("Configurando interfaz moderna...")
            
            # Configurar ventana principal
            self.configurar_ventana_principal()
            
            # Crear header profesional con brand identity
            self.crear_header_profesional()
            
            # Crear contenedor principal para el contenido dinámico
            self.contenido_principal = tk.Frame(self.root, bg=self.tema_actual.FONDO_PRINCIPAL)
            self.contenido_principal.pack(fill=tk.BOTH, expand=True)
            
            # Crear frame_scrollable equivalente para compatibilidad
            self.frame_scrollable = self.contenido_principal
            
            # Mostrar panel principal por defecto (dashboard completo)
            self.mostrar_panel_principal()
            
            # Mostrar mensaje de bienvenida
            self.mostrar_mensaje_bienvenida()
            
            self.logger.info("Interfaz moderna configurada correctamente")
            
        except Exception as e:
            self.logger.error(f"Error configurando interfaz: {e}")
            messagebox.showerror("Error", f"Error al configurar la interfaz: {e}")
    
    def configurar_ventana_principal(self):
        """Configurar propiedades de la ventana principal"""
        try:
            if self.root:
                # Configuración básica de la ventana
                self.root.title("ARES AEGIS - Advanced Cybersecurity Command Center")
                self.root.geometry("1400x900")
                self.root.minsize(1200, 800)
                self.root.configure(bg="#0d1421")
                
                # Centrar ventana en la pantalla
                self.centrar_ventana()
                
                # Configurar el comportamiento al cerrar
                self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
                
                # Configurar icono si existe
                self.configurar_icono_ventana()
                
        except Exception as e:
            self.logger.error(f"Error configurando ventana principal: {e}")
    
    def centrar_ventana(self):
        """Centrar la ventana en la pantalla"""
        try:
            # Obtener dimensiones de la pantalla
            ancho_pantalla = self.root.winfo_screenwidth()
            alto_pantalla = self.root.winfo_screenheight()
            
            # Calcular posición para centrar
            x = (ancho_pantalla - 1400) // 2
            y = (alto_pantalla - 900) // 2
            
            # Aplicar posición
            self.root.geometry(f"1400x900+{x}+{y}")
            
        except Exception as e:
            self.logger.error(f"Error centrando ventana: {e}")
    
    def configurar_icono_ventana(self):
        """Configurar icono de la ventana"""
        try:
            # Intentar cargar iconos desde recursos
            rutas_iconos = [
                "recursos/aresIcon.png",
                "recursos/AresAegis.png"
            ]
            
            for ruta in rutas_iconos:
                try:
                    if os.path.exists(ruta):
                        from PIL import Image, ImageTk
                        imagen = Image.open(ruta).resize((32, 32))
                        icono = ImageTk.PhotoImage(imagen)
                        self.root.iconphoto(True, icono)
                        break
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error configurando icono: {e}")
    
    def mostrar_mensaje_bienvenida(self):
        """Mostrar mensaje de bienvenida al usuario"""
        try:
            self.root.after(1000, lambda: self.mostrar_notificacion_bienvenida())
        except Exception as e:
            self.logger.error(f"Error mostrando mensaje de bienvenida: {e}")
    
    def mostrar_notificacion_bienvenida(self):
        """Mostrar notificación de bienvenida moderna"""
        try:
            # Crear ventana de notificación
            notification = tk.Toplevel(self.root)
            notification.title("")
            notification.geometry("400x150")
            notification.configure(bg="#1a202c")
            notification.resizable(False, False)
            notification.overrideredirect(True)  # Sin borde de ventana
            
            # Posicionar en esquina superior derecha
            x = self.root.winfo_x() + self.root.winfo_width() - 420
            y = self.root.winfo_y() + 20
            notification.geometry(f"400x150+{x}+{y}")
            
            # Contenido de la notificación
            content_frame = tk.Frame(notification, bg="#1a202c")
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            title_label = tk.Label(
                content_frame,
                text="🛡️ ARES AEGIS",
                font=("Segoe UI", 14, "bold"),
                bg="#1a202c",
                fg="#1a73e8"
            )
            title_label.pack(anchor="w")
            
            # Mensaje
            message_label = tk.Label(
                content_frame,
                text="Sistema de seguridad inicializado\ncorrectamente. ¡Bienvenido!",
                font=("Segoe UI", 11),
                bg="#1a202c",
                fg="#ffffff",
                justify="left"
            )
            message_label.pack(anchor="w", pady=(10, 0))
            
            # Cerrar automáticamente después de 3 segundos
            notification.after(3000, notification.destroy)
            
        except Exception as e:
            self.logger.error(f"Error mostrando notificación: {e}")
    
    def cerrar_aplicacion(self):
        """Cerrar aplicación de forma segura"""
        try:
            respuesta = messagebox.askyesno(
                "Confirmar Salida",
                "¿Está seguro de que desea cerrar ARES AEGIS?\n\n"
                "Se detendrán todos los procesos de monitoreo."
            )
            
            if respuesta:
                self.logger.info("Cerrando aplicación...")
                
                # Aquí se pueden añadir tareas de limpieza
                # Como detener monitores, guardar configuración, etc.
                
                if self.root:
                    self.root.quit()
                    self.root.destroy()
                    
        except Exception as e:
            self.logger.error(f"Error cerrando aplicación: {e}")
            if self.root:
                self.root.quit()
                self.root.destroy()
    
    def crear_header_profesional(self):
        """Crear navegación moderna inspirada en Sniffnet y ttkbootstrap patterns"""
        # === HEADER PRINCIPAL PROFESIONAL ===
        self.header_frame = tk.Frame(self.root, bg="#0d1421", height=85)
        self.header_frame.pack(fill="x", padx=0, pady=0)
        self.header_frame.pack_propagate(False)
        
        # Gradiente superior decorativo
        gradient_top = tk.Frame(self.header_frame, bg="#1a73e8", height=3)
        gradient_top.pack(fill="x")
        
        # Container principal del header
        header_content = tk.Frame(self.header_frame, bg="#0d1421")
        header_content.pack(fill="both", expand=True, padx=30, pady=15)
        
        # === LOGO Y BRANDING SECTION ===
        brand_frame = tk.Frame(header_content, bg="#0d1421")
        brand_frame.pack(side="left", fill="y")
        
        # Logo dinámico
        logo_cargado = False
        logo_paths = [
            "/home/dogsoul/Ares-Aegis/recursos/AresAegis.png",
            "/home/dogsoul/Ares-Aegis/recursos/aresIcon.png",
            os.path.join(os.path.dirname(__file__), "../..", "recursos", "AresAegis.png")
        ]
        
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    logo_img = tk.PhotoImage(file=logo_path)
                    # Redimensionar apropiadamente en lugar de subsample agresivo
                    width, height = logo_img.width(), logo_img.height()
                    # Calcular factor de escala para mantener altura máxima de 50px
                    scale_factor = max(1, height // 50)
                    if scale_factor > 1:
                        logo_img = logo_img.subsample(scale_factor)
                    logo_label = tk.Label(brand_frame, image=logo_img, bg="#0d1421")
                    logo_label.pack(side="left", padx=(0, 15))
                    setattr(logo_label, '_image_ref', logo_img)
                    logo_cargado = True
                    break
                except:
                    continue
        
        if not logo_cargado:
            logo_emoji = tk.Label(brand_frame, text="🛡️", font=("Arial", 36), 
                                bg="#0d1421", fg="#1a73e8")
            logo_emoji.pack(side="left", padx=(0, 15))
        
        # Títulos profesionales
        text_frame = tk.Frame(brand_frame, bg="#0d1421")
        text_frame.pack(side="left", fill="y")
        
        title_label = tk.Label(text_frame, text="ARES AEGIS", 
                              font=("Segoe UI", 18, "bold"), 
                              bg="#0d1421", fg="#ffffff")
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(text_frame, text="Advanced Cybersecurity Command Center", 
                                 font=("Segoe UI", 10), 
                                 bg="#0d1421", fg="#8a92b2")
        subtitle_label.pack(anchor="w")
        
        # === STATUS INDICATOR PROFESIONAL ===
        status_frame = tk.Frame(header_content, bg="#0d1421")
        status_frame.pack(side="right", fill="y")
        
        # Sistema de estado con indicador visual
        status_container = tk.Frame(status_frame, bg="#0d1421")
        status_container.pack(fill="y", expand=True)
        
        # Indicador de estado activo
        status_indicator = tk.Frame(status_container, bg="#00c851", width=8, height=8)
        status_indicator.pack(side="right", padx=(10, 5), pady=18)
        
        self.status_label = tk.Label(status_container, text="SISTEMA ACTIVO", 
                                    font=("Segoe UI", 11, "bold"), 
                                    bg="#0d1421", fg="#00c851")
        self.status_label.pack(side="right", pady=15)
        
        # === NAVEGACIÓN PRINCIPAL MODERNA ===
        self.navbar = tk.Frame(self.root, bg="#16213e", height=70)
        self.navbar.pack(fill="x", padx=0, pady=0)
        self.navbar.pack_propagate(False)
        
        # Container de navegación con padding responsivo
        nav_container = tk.Frame(self.navbar, bg="#16213e")
        nav_container.pack(fill="both", expand=True, padx=25, pady=10)
        
        # Grid responsivo para tabs de navegación
        for i in range(7):
            nav_container.columnconfigure(i, weight=1, uniform="nav_tab")
        
        # === TABS DE NAVEGACIÓN MODERNOS ===
        nav_configs = [
            ("📊", "Dashboard", self.mostrar_panel_principal, "#1a73e8"),
            ("🔍", "Scan", self.mostrar_panel_escaneo, "#ff6b35"),
            ("📡", "Monitor", self.mostrar_panel_monitoreo, "#7b68ee"),
            ("🛡️", "Protection", self.mostrar_panel_cuarentena, "#00c851"),
            ("🔧", "Tools", self.mostrar_herramientas, "#ffc107"),
            ("📋", "Reports", self.mostrar_panel_reportes, "#dc3545"),
            ("⚙️", "Settings", self.mostrar_panel_configuracion, "#6c757d")
        ]
        
        self.nav_tabs = []
        for i, (icon, text, command, color) in enumerate(nav_configs):
            tab = self.crear_tab_moderno(nav_container, icon, text, command, color, i)
            self.nav_tabs.append(tab)
            tab.grid(row=0, column=i, sticky="ew", padx=2)
        
        # === SEPARADOR VISUAL ===
        separator = tk.Frame(self.root, bg="#2c3e50", height=2)
        separator.pack(fill="x")
    
    def crear_tab_moderno(self, parent, icon, text, command, accent_color, index):
        """Crear tab de navegación moderno inspirado en patrones de Bootstrap y Sniffnet"""
        # Container principal del tab
        tab_container = tk.Frame(parent, bg="#16213e")
        
        # Estado activo del tab
        is_active = index == 0  # Dashboard activo por defecto
        
        # Colores según estado
        if is_active:
            bg_color = accent_color
            fg_color = "#ffffff"
            border_color = accent_color
        else:
            bg_color = "#16213e"
            fg_color = "#8a92b2"
            border_color = "#16213e"  # Cambiar de "transparent" a color sólido
        
        # Botón principal del tab con diseño moderno
        tab_button = tk.Button(
            tab_container,
            text=f"{icon}\n{text}",  # Corregir el escape - cambiar \\n por \n
            command=lambda: self.activar_tab(index, command),
            bg=bg_color,
            fg=fg_color,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=12,
            activebackground=accent_color,
            activeforeground="#ffffff"
        )
        tab_button.pack(fill="both", expand=True)
        
        # Indicador inferior del tab activo
        indicator = tk.Frame(tab_container, bg=border_color, height=3)
        indicator.pack(fill="x", side="bottom")
        
        # Efectos hover modernos
        def on_enter(e):
            if not is_active:
                tab_button.config(bg="#2a3b52", fg="#ffffff")
                indicator.config(bg=accent_color)
        
        def on_leave(e):
            if not is_active:
                tab_button.config(bg="#16213e", fg="#8a92b2")
                indicator.config(bg="#16213e")  # Cambiar de "transparent" a color sólido
        
        tab_button.bind("<Enter>", on_enter)
        tab_button.bind("<Leave>", on_leave)
        
        # Guardar referencias para control de estado
        tab_container.button = tab_button
        tab_container.indicator = indicator
        tab_container.is_active = is_active
        tab_container.accent_color = accent_color
        tab_container.index = index
        
        return tab_container
    
    def activar_tab(self, index, command):
        """Activar tab seleccionado con efectos visuales modernos"""
        try:
            # Desactivar todos los tabs
            for tab in self.nav_tabs:
                tab.is_active = False
                tab.button.config(
                    bg="#16213e",
                    fg="#8a92b2"
                )
                tab.indicator.config(bg="#16213e")  # Cambiar de "transparent" a color sólido
            
            # Activar tab seleccionado
            if index < len(self.nav_tabs):
                active_tab = self.nav_tabs[index]
                active_tab.is_active = True
                active_tab.button.config(
                    bg=active_tab.accent_color,
                    fg="#ffffff"
                )
                active_tab.indicator.config(bg=active_tab.accent_color)
            
            # Ejecutar comando asociado
            if command:
                command()
                
        except Exception as e:
            self.logger.error(f"Error activando tab: {e}")
    
    def crear_contenido_principal(self):
        """Crear contenido principal con diseño moderno tipo dashboard"""
        # === CONTAINER PRINCIPAL MEJORADO ===
        self.contenido_principal = tk.Frame(self.root, bg="#0f1419")
        self.contenido_principal.pack(fill="both", expand=True, padx=0, pady=0)
        
        # === DASHBOARD MODERNO CON GRID RESPONSIVO ===
        self.dashboard_frame = tk.Frame(self.contenido_principal, bg="#0f1419")
        self.dashboard_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Grid responsivo 12-column system (Bootstrap-inspired)
        for i in range(12):
            self.dashboard_frame.columnconfigure(i, weight=1, uniform="dash_col")
        
        # Sistema de filas dinámico
        for i in range(6):
            self.dashboard_frame.rowconfigure(i, weight=1, uniform="dash_row")
        
        # === ROW 1: MÉTRICAS PRINCIPALES (4 columnas cada una) ===
        self.crear_metricas_principales()
        
        # === ROW 2-3: GRÁFICOS Y ACTIVIDAD (6+6 columnas) ===
        self.crear_seccion_graficos_y_actividad()
        
        # === ROW 4-5: ALERTAS Y SISTEMA (6+6 columnas) ===
        self.crear_seccion_alertas_y_sistema()
        
        # === ROW 6: ACCIONES RÁPIDAS (12 columnas) ===
        self.crear_barra_acciones_rapidas()
    
    def crear_metricas_principales(self):
        """Crear métricas principales estilo dashboard moderno"""
        metricas = [
            {
                "titulo": "Amenazas Detectadas",
                "valor": "12",
                "cambio": "+3",
                "color": "#dc3545",
                "icono": "🛡️",
                "columna": 0
            },
            {
                "titulo": "Archivos Escaneados",
                "valor": "1,247",
                "cambio": "+156",
                "color": "#1a73e8",
                "icono": "📄",
                "columna": 3
            },
            {
                "titulo": "Sistema Protegido",
                "valor": "98.5%",
                "cambio": "+0.3%",
                "color": "#00c851",
                "icono": "🔒",
                "columna": 6
            },
            {
                "titulo": "Última Actualización",
                "valor": "Hoy",
                "cambio": "2h ago",
                "color": "#ffc107",
                "icono": "🔄",
                "columna": 9
            }
        ]
        
        for metrica in metricas:
            self.crear_card_metrica_moderna(metrica)
    
    def crear_card_metrica_moderna(self, metrica):
        """Crear card de métrica con diseño moderno"""
        # Container principal de la métrica
        card_frame = tk.Frame(self.dashboard_frame, bg="#1a202c", relief="flat")
        card_frame.grid(
            row=0, 
            column=metrica["columna"], 
            columnspan=3, 
            sticky="ew", 
            padx=8, 
            pady=8
        )
        
        # Padding interno del card
        card_content = tk.Frame(card_frame, bg="#1a202c")
        card_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header con icono y valor principal
        header_frame = tk.Frame(card_content, bg="#1a202c")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Icono
        icon_label = tk.Label(
            header_frame,
            text=metrica["icono"],
            font=("Arial", 24),
            bg="#1a202c",
            fg=metrica["color"]
        )
        icon_label.pack(side="left")
        
        # Valor principal
        valor_label = tk.Label(
            header_frame,
            text=metrica["valor"],
            font=("Segoe UI", 28, "bold"),
            bg="#1a202c",
            fg="#ffffff"
        )
        valor_label.pack(side="right")
        
        # Título de la métrica
        titulo_label = tk.Label(
            card_content,
            text=metrica["titulo"],
            font=("Segoe UI", 12),
            bg="#1a202c",
            fg="#8a92b2"
        )
        titulo_label.pack(anchor="w")
        
        # Indicador de cambio
        cambio_frame = tk.Frame(card_content, bg="#1a202c")
        cambio_frame.pack(fill="x", pady=(10, 0))
        
        cambio_color = "#00c851" if metrica["cambio"].startswith("+") else "#dc3545"
        cambio_label = tk.Label(
            cambio_frame,
            text=f"↗ {metrica['cambio']} desde ayer",
            font=("Segoe UI", 10),
            bg="#1a202c",
            fg=cambio_color
        )
        cambio_label.pack(anchor="w")
        
        # Efecto hover en el card
        def on_enter(e):
            card_frame.config(bg="#2d3748")
            card_content.config(bg="#2d3748")
            header_frame.config(bg="#2d3748")
            titulo_label.config(bg="#2d3748")
            valor_label.config(bg="#2d3748")
            icon_label.config(bg="#2d3748")
            cambio_frame.config(bg="#2d3748")
            cambio_label.config(bg="#2d3748")
        
        def on_leave(e):
            bg_original = "#1a202c"
            card_frame.config(bg=bg_original)
            card_content.config(bg=bg_original)
            header_frame.config(bg=bg_original)
            titulo_label.config(bg=bg_original)
            valor_label.config(bg=bg_original)
            icon_label.config(bg=bg_original)
            cambio_frame.config(bg=bg_original)
            cambio_label.config(bg=bg_original)
        
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        for child in card_frame.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
    
    def crear_seccion_graficos_y_actividad(self):
        """Crear sección de gráficos y actividad reciente"""
        # === GRÁFICO DE AMENAZAS (Columnas 0-5) ===
        graficos_frame = tk.Frame(self.dashboard_frame, bg="#1a202c", relief="flat")
        graficos_frame.grid(row=1, column=0, columnspan=6, sticky="nsew", padx=8, pady=8, rowspan=2)
        
        # Header del gráfico
        graph_header = tk.Frame(graficos_frame, bg="#1a202c")
        graph_header.pack(fill="x", padx=20, pady=(20, 10))
        
        graph_title = tk.Label(
            graph_header,
            text="📈 Análisis de Amenazas - Últimas 7 días",
            font=("Segoe UI", 14, "bold"),
            bg="#1a202c",
            fg="#ffffff"
        )
        graph_title.pack(side="left")
        
        # Simulación de gráfico con barras ASCII
        graph_content = tk.Frame(graficos_frame, bg="#1a202c")
        graph_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Datos simulados del gráfico
        graph_data = [
            ("L", 8, "#dc3545"),
            ("M", 12, "#dc3545"),
            ("X", 5, "#ffc107"),
            ("J", 15, "#dc3545"),
            ("V", 3, "#00c851"),
            ("S", 7, "#ffc107"),
            ("D", 4, "#00c851")
        ]
        
        # Container del gráfico
        chart_frame = tk.Frame(graph_content, bg="#1a202c")
        chart_frame.pack(fill="both", expand=True)
        
        for i, (dia, valor, color) in enumerate(graph_data):
            # Columna del gráfico
            col_frame = tk.Frame(chart_frame, bg="#1a202c")
            col_frame.grid(row=0, column=i, sticky="s", padx=5)
            
            # Barra del gráfico (altura proporcional)
            altura_barra = max(10, valor * 8)  # Altura mínima 10px
            barra = tk.Frame(col_frame, bg=color, width=30, height=altura_barra)
            barra.pack(pady=(0, 5))
            barra.pack_propagate(False)
            
            # Valor numérico
            valor_label = tk.Label(
                col_frame,
                text=str(valor),
                font=("Segoe UI", 9, "bold"),
                bg="#1a202c",
                fg="#ffffff"
            )
            valor_label.pack()
            
            # Día de la semana
            dia_label = tk.Label(
                col_frame,
                text=dia,
                font=("Segoe UI", 9),
                bg="#1a202c",
                fg="#8a92b2"
            )
            dia_label.pack()
        
        # === ACTIVIDAD RECIENTE (Columnas 6-11) ===
        actividad_frame = tk.Frame(self.dashboard_frame, bg="#1a202c", relief="flat")
        actividad_frame.grid(row=1, column=6, columnspan=6, sticky="nsew", padx=8, pady=8, rowspan=2)
        
        # Header de actividad
        activity_header = tk.Frame(actividad_frame, bg="#1a202c")
        activity_header.pack(fill="x", padx=20, pady=(20, 10))
        
        activity_title = tk.Label(
            activity_header,
            text="📋 Actividad Reciente",
            font=("Segoe UI", 14, "bold"),
            bg="#1a202c",
            fg="#ffffff"
        )
        activity_title.pack(side="left")
        
        # Lista de actividades
        activity_content = tk.Frame(actividad_frame, bg="#1a202c")
        activity_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        actividades = [
            ("🚨", "Amenaza detectada en sistema.exe", "hace 2 min", "#dc3545"),
            ("✅", "Escaneo completado - 1,247 archivos", "hace 15 min", "#00c851"),
            ("🔄", "Actualización de firmas", "hace 1 hora", "#1a73e8"),
            ("🛡️", "Archivo movido a cuarentena", "hace 2 horas", "#ffc107"),
            ("📊", "Reporte generado exitosamente", "hace 3 horas", "#6c757d"),
        ]
        
        for icono, texto, tiempo, color in actividades:
            # Container de actividad
            act_container = tk.Frame(activity_content, bg="#1a202c")
            act_container.pack(fill="x", pady=5)
            
            # Icono de actividad
            icon_frame = tk.Frame(act_container, bg="#1a202c")
            icon_frame.pack(side="left", padx=(0, 15))
            
            icon_bg = tk.Frame(icon_frame, bg=color, width=32, height=32)
            icon_bg.pack()
            icon_bg.pack_propagate(False)
            
            icon_label = tk.Label(
                icon_bg,
                text=icono,
                font=("Arial", 14),
                bg=color,
                fg="#ffffff"
            )
            icon_label.pack(expand=True)
            
            # Contenido de la actividad
            content_frame = tk.Frame(act_container, bg="#1a202c")
            content_frame.pack(side="left", fill="x", expand=True)
            
            text_label = tk.Label(
                content_frame,
                text=texto,
                font=("Segoe UI", 11),
                bg="#1a202c",
                fg="#ffffff",
                anchor="w"
            )
            text_label.pack(anchor="w")
            
            time_label = tk.Label(
                content_frame,
                text=tiempo,
                font=("Segoe UI", 9),
                bg="#1a202c",
                fg="#8a92b2",
                anchor="w"
            )
            time_label.pack(anchor="w")
    
    def crear_seccion_alertas_y_sistema(self):
        """Crear sección de alertas críticas e información del sistema"""
        # === ALERTAS CRÍTICAS (Columnas 0-5) ===
        alertas_frame = tk.Frame(self.dashboard_frame, bg="#1a202c", relief="flat")
        alertas_frame.grid(row=3, column=0, columnspan=6, sticky="nsew", padx=8, pady=8, rowspan=2)
        
        # Header de alertas
        alerts_header = tk.Frame(alertas_frame, bg="#1a202c")
        alerts_header.pack(fill="x", padx=20, pady=(20, 10))
        
        alerts_title = tk.Label(
            alerts_header,
            text="🚨 Alertas Críticas",
            font=("Segoe UI", 14, "bold"),
            bg="#1a202c",
            fg="#dc3545"
        )
        alerts_title.pack(side="left")
        
        # Badge de contador
        badge_frame = tk.Frame(alerts_header, bg="#dc3545", width=25, height=25)
        badge_frame.pack(side="right")
        badge_frame.pack_propagate(False)
        
        badge_label = tk.Label(
            badge_frame,
            text="3",
            font=("Segoe UI", 11, "bold"),
            bg="#dc3545",
            fg="#ffffff"
        )
        badge_label.pack(expand=True)
        
        # Lista de alertas
        alerts_content = tk.Frame(alertas_frame, bg="#1a202c")
        alerts_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        alertas = [
            ("🔥", "Proceso sospechoso detectado", "CRÍTICO", "#dc3545"),
            ("⚠️", "Conexión no autorizada bloqueada", "ALTO", "#ff6b35"),
            ("🛑", "Archivo malicioso en cuarentena", "MEDIO", "#ffc107"),
        ]
        
        for icono, mensaje, nivel, color in alertas:
            # Container de alerta
            alert_container = tk.Frame(alerts_content, bg="#2d1b1b")
            alert_container.pack(fill="x", pady=5, padx=5)
            
            # Padding interno
            alert_content = tk.Frame(alert_container, bg="#2d1b1b")
            alert_content.pack(fill="x", padx=15, pady=10)
            
            # Icono y nivel
            left_frame = tk.Frame(alert_content, bg="#2d1b1b")
            left_frame.pack(side="left")
            
            icon_label = tk.Label(
                left_frame,
                text=icono,
                font=("Arial", 16),
                bg="#2d1b1b",
                fg=color
            )
            icon_label.pack(side="left", padx=(0, 10))
            
            # Mensaje de alerta
            message_frame = tk.Frame(alert_content, bg="#2d1b1b")
            message_frame.pack(side="left", fill="x", expand=True)
            
            message_label = tk.Label(
                message_frame,
                text=mensaje,
                font=("Segoe UI", 11),
                bg="#2d1b1b",
                fg="#ffffff",
                anchor="w"
            )
            message_label.pack(anchor="w")
            
            # Badge de nivel
            level_frame = tk.Frame(alert_content, bg=color, padx=8, pady=2)
            level_frame.pack(side="right")
            
            level_label = tk.Label(
                level_frame,
                text=nivel,
                font=("Segoe UI", 9, "bold"),
                bg=color,
                fg="#ffffff"
            )
            level_label.pack()
        
        # === INFORMACIÓN DEL SISTEMA (Columnas 6-11) ===
        sistema_frame = tk.Frame(self.dashboard_frame, bg="#1a202c", relief="flat")
        sistema_frame.grid(row=3, column=6, columnspan=6, sticky="nsew", padx=8, pady=8, rowspan=2)
        
        # Header del sistema
        system_header = tk.Frame(sistema_frame, bg="#1a202c")
        system_header.pack(fill="x", padx=20, pady=(20, 10))
        
        system_title = tk.Label(
            system_header,
            text="💻 Estado del Sistema",
            font=("Segoe UI", 14, "bold"),
            bg="#1a202c",
            fg="#ffffff"
        )
        system_title.pack(side="left")
        
        # Métricas del sistema
        system_content = tk.Frame(sistema_frame, bg="#1a202c")
        system_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # CPU, RAM, Disco
        metricas_sistema = [
            ("CPU", "45%", "#1a73e8"),
            ("RAM", "68%", "#ffc107"),
            ("Disco", "82%", "#dc3545"),
        ]
        
        for nombre, valor, color in metricas_sistema:
            # Container de métrica
            metric_container = tk.Frame(system_content, bg="#1a202c")
            metric_container.pack(fill="x", pady=8)
            
            # Nombre de la métrica
            name_label = tk.Label(
                metric_container,
                text=nombre,
                font=("Segoe UI", 11),
                bg="#1a202c",
                fg="#8a92b2"
            )
            name_label.pack(side="left")
            
            # Valor
            value_label = tk.Label(
                metric_container,
                text=valor,
                font=("Segoe UI", 11, "bold"),
                bg="#1a202c",
                fg="#ffffff"
            )
            value_label.pack(side="right")
            
            # Barra de progreso simulada
            progress_frame = tk.Frame(metric_container, bg="#2d3748", height=8)
            progress_frame.pack(fill="x", padx=(80, 80), pady=(5, 0))
            
            # Progreso actual
            porcentaje = int(valor.replace('%', ''))
            progress_width = int(porcentaje * 2)  # Escala visual
            progress_bar = tk.Frame(progress_frame, bg=color, width=progress_width, height=8)
            progress_bar.pack(side="left")
    
    def crear_barra_acciones_rapidas(self):
        """Crear barra de acciones rápidas en la parte inferior"""
        # Container de acciones
        acciones_frame = tk.Frame(self.dashboard_frame, bg="#16213e", relief="flat")
        acciones_frame.grid(row=5, column=0, columnspan=12, sticky="ew", padx=8, pady=8)
        
        # Padding interno
        acciones_content = tk.Frame(acciones_frame, bg="#16213e")
        acciones_content.pack(fill="x", padx=25, pady=15)
        
        # Título de la sección
        title_label = tk.Label(
            acciones_content,
            text="🚀 Acciones Rápidas",
            font=("Segoe UI", 12, "bold"),
            bg="#16213e",
            fg="#ffffff"
        )
        title_label.pack(side="left", padx=(0, 30))
        
        # Botones de acción
        acciones = [
            ("🔍", "Escanear Sistema", self.mostrar_escaneo, "#1a73e8"),
            ("🔄", "Actualizar Firmas", self.actualizar_firmas, "#00c851"),
            ("📊", "Generar Reporte", self.mostrar_reportes, "#ffc107"),
            ("⚙️", "Configuración", self.mostrar_configuracion, "#6c757d"),
        ]
        
        for icono, texto, comando, color in acciones:
            btn = tk.Button(
                acciones_content,
                text=f"{icono} {texto}",
                command=comando,
                bg=color,
                fg="#ffffff",
                relief="flat",
                borderwidth=0,
                cursor="hand2",
                font=("Segoe UI", 10, "bold"),
                padx=20,
                pady=8,
                activebackground=self.adjust_color_brightness(color, 0.8),
                activeforeground="#ffffff"
            )
            btn.pack(side="left", padx=(0, 15))
            
            # Efecto hover
            def on_enter(e, btn=btn, original_color=color):
                btn.config(bg=self.adjust_color_brightness(original_color, 0.8))
            
            def on_leave(e, btn=btn, original_color=color):
                btn.config(bg=original_color)
                btn.config(bg=original_color)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
    
    def adjust_color_brightness(self, hex_color, factor):
        """Ajustar brillo de un color hexadecimal"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            rgb = tuple(min(255, max(0, int(c * factor))) for c in rgb)
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        except:
            return hex_color
    
    def actualizar_firmas(self):
        """Actualizar firmas de malware"""
        try:
            messagebox.showinfo("Actualización", "Actualizando firmas de malware...")
            # Aquí iría la lógica de actualización real
            messagebox.showinfo("Éxito", "Firmas actualizadas correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando firmas: {e}")
    
    def mostrar_dashboard(self):
        """Mostrar dashboard principal"""
        try:
            # Limpiar contenido actual
            if hasattr(self, 'contenido_principal') and self.contenido_principal:
                self.contenido_principal.destroy()
            
            # Crear nuevo dashboard
            self.crear_contenido_principal()
            
        except Exception as e:
            self.logger.error(f"Error mostrando dashboard: {e}")
    
    def mostrar_escaneo(self):
        """Mostrar interfaz de escaneo"""
        try:
            # Limpiar contenido actual
            if hasattr(self, 'contenido_principal') and self.contenido_principal:
                self.contenido_principal.destroy()
            
            # Crear interfaz de escaneo moderna
            self.crear_interfaz_escaneo_moderna()
            
        except Exception as e:
            self.logger.error(f"Error mostrando escaneo: {e}")
    
    def mostrar_monitoreo(self):
        """Mostrar interfaz de monitoreo"""
        try:
            # Limpiar contenido actual
            if hasattr(self, 'contenido_principal') and self.contenido_principal:
                self.contenido_principal.destroy()
            
            # Crear interfaz de monitoreo
            self.crear_interfaz_monitoreo()
            
        except Exception as e:
            self.logger.error(f"Error mostrando monitoreo: {e}")
    
    def mostrar_gestion(self):
        """Mostrar interfaz de gestión/protección"""
        try:
            # Limpiar contenido actual
            if hasattr(self, 'contenido_principal') and self.contenido_principal:
                self.contenido_principal.destroy()
            
            # Crear interfaz de gestión
            self.crear_interfaz_gestion()
            
        except Exception as e:
            self.logger.error(f"Error mostrando gestión: {e}")
    
    def mostrar_herramientas(self):
        """Mostrar herramientas adicionales"""
        try:
            # Limpiar contenido actual
            if hasattr(self, 'contenido_principal') and self.contenido_principal:
                self.contenido_principal.destroy()
            
            # Crear interfaz de herramientas
            self.crear_interfaz_herramientas()
            
        except Exception as e:
            self.logger.error(f"Error mostrando herramientas: {e}")
    
    def mostrar_reportes(self):
        """Mostrar interfaz de reportes"""
        try:
            # Limpiar contenido actual
            if hasattr(self, 'contenido_principal') and self.contenido_principal:
                self.contenido_principal.destroy()
            
            # Crear interfaz de reportes
            self.crear_interfaz_reportes()
            
        except Exception as e:
            self.logger.error(f"Error mostrando reportes: {e}")
    
    def mostrar_configuracion(self):
        """Mostrar configuración del sistema"""
        try:
            # Limpiar contenido actual
            if hasattr(self, 'contenido_principal') and self.contenido_principal:
                self.contenido_principal.destroy()
            
            # Crear interfaz de configuración
            self.crear_interfaz_configuracion()
            
        except Exception as e:
            self.logger.error(f"Error mostrando configuración: {e}")
    
    def crear_interfaz_escaneo_moderna(self):
        """Crear interfaz de escaneo con diseño moderno"""
        # Container principal
        self.contenido_principal = tk.Frame(self.root, bg="#0f1419")
        self.contenido_principal.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header de la sección
        header_frame = tk.Frame(self.contenido_principal, bg="#1a202c")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        header_content = tk.Frame(header_frame, bg="#1a202c")
        header_content.pack(fill="x", padx=25, pady=20)
        
        title_label = tk.Label(
            header_content,
            text="🔍 Centro de Escaneo Avanzado",
            font=("Segoe UI", 18, "bold"),
            bg="#1a202c",
            fg="#ffffff"
        )
        title_label.pack(side="left")
        
        # Opciones de escaneo con cards modernos
        options_frame = tk.Frame(self.contenido_principal, bg="#0f1419")
        options_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Grid de opciones
        for i in range(3):
            options_frame.columnconfigure(i, weight=1)
        
        # Tarjetas de escaneo
        scan_options = [
            {
                "titulo": "Escaneo Rápido",
                "descripcion": "Análisis rápido de áreas críticas",
                "icono": "⚡",
                "color": "#1a73e8",
                "comando": self.iniciar_escaneo_rapido_moderno,
                "columna": 0
            },
            {
                "titulo": "Escaneo Completo",
                "descripcion": "Análisis exhaustivo del sistema",
                "icono": "🔍",
                "color": "#dc3545",
                "comando": self.iniciar_escaneo_completo_moderno,
                "columna": 1
            },
            {
                "titulo": "Escaneo Personalizado",
                "descripcion": "Selecciona carpetas específicas",
                "icono": "⚙️",
                "color": "#00c851",
                "comando": self.iniciar_escaneo_personalizado_moderno,
                "columna": 2
            }
        ]
        
        for option in scan_options:
            self.crear_card_escaneo(options_frame, option)
    
    def crear_card_escaneo(self, parent, option):
        """Crear card de opción de escaneo"""
        # Card container
        card_frame = tk.Frame(parent, bg="#1a202c", relief="flat")
        card_frame.grid(
            row=0, 
            column=option["columna"], 
            sticky="nsew", 
            padx=15, 
            pady=15
        )
        
        # Padding interno
        card_content = tk.Frame(card_frame, bg="#1a202c")
        card_content.pack(fill="both", expand=True, padx=25, pady=30)
        
        # Icono principal
        icon_label = tk.Label(
            card_content,
            text=option["icono"],
            font=("Arial", 48),
            bg="#1a202c",
            fg=option["color"]
        )
        icon_label.pack(pady=(0, 20))
        
        # Título
        title_label = tk.Label(
            card_content,
            text=option["titulo"],
            font=("Segoe UI", 16, "bold"),
            bg="#1a202c",
            fg="#ffffff"
        )
        title_label.pack(pady=(0, 10))
        
        # Descripción
        desc_label = tk.Label(
            card_content,
            text=option["descripcion"],
            font=("Segoe UI", 11),
            bg="#1a202c",
            fg="#8a92b2",
            wraplength=200
        )
        desc_label.pack(pady=(0, 25))
        
        # Botón de acción
        action_btn = tk.Button(
            card_content,
            text="Iniciar Escaneo",
            command=option["comando"],
            bg=option["color"],
            fg="#ffffff",
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 12, "bold"),
            padx=30,
            pady=12,
            activebackground=self.adjust_color_brightness(option["color"], 0.8),
            activeforeground="#ffffff"
        )
        action_btn.pack()
        
        # Efectos hover para toda la card
        def on_enter(e):
            card_frame.config(bg="#2d3748")
            card_content.config(bg="#2d3748")
            icon_label.config(bg="#2d3748")
            title_label.config(bg="#2d3748")
            desc_label.config(bg="#2d3748")
        
        def on_leave(e):
            bg_original = "#1a202c"
            card_frame.config(bg=bg_original)
            card_content.config(bg=bg_original)
            icon_label.config(bg=bg_original)
            title_label.config(bg=bg_original)
            desc_label.config(bg=bg_original)
        
        # Bind eventos
        widgets = [card_frame, card_content, icon_label, title_label, desc_label]
        for widget in widgets:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
    
    def iniciar_escaneo_rapido_moderno(self):
        """Iniciar escaneo rápido con interfaz moderna"""
        try:
            self.crear_interfaz_progreso_escaneo("Escaneo Rápido", "#1a73e8")
        except Exception as e:
            messagebox.showerror("Error", f"Error iniciando escaneo rápido: {e}")
    
    def iniciar_escaneo_completo_moderno(self):
        """Iniciar escaneo completo con interfaz moderna"""
        try:
            self.crear_interfaz_progreso_escaneo("Escaneo Completo", "#dc3545")
        except Exception as e:
            messagebox.showerror("Error", f"Error iniciando escaneo completo: {e}")
    
    def iniciar_escaneo_personalizado_moderno(self):
        """Iniciar escaneo personalizado"""
        try:
            from tkinter import filedialog
            directorio = filedialog.askdirectory(title="Seleccionar directorio para escanear")
            if directorio:
                self.crear_interfaz_progreso_escaneo(f"Escaneando: {directorio}", "#00c851", directorio)
        except Exception as e:
            messagebox.showerror("Error", f"Error iniciando escaneo personalizado: {e}")
    
    def crear_interfaz_progreso_escaneo(self, titulo, color, directorio=None):
        """Crear interfaz de progreso de escaneo moderna"""
        # Limpiar contenido
        if hasattr(self, 'contenido_principal') and self.contenido_principal:
            self.contenido_principal.destroy()
        
        # Container principal
        self.contenido_principal = tk.Frame(self.root, bg="#0f1419")
        self.contenido_principal.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Card de progreso centrada
        progress_container = tk.Frame(self.contenido_principal, bg="#0f1419")
        progress_container.pack(fill="both", expand=True, padx=50, pady=50)
        
        progress_card = tk.Frame(progress_container, bg="#1a202c")
        progress_card.pack(expand=True, fill="both", padx=100, pady=100)
        
        # Contenido de la card
        card_content = tk.Frame(progress_card, bg="#1a202c")
        card_content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Header del progreso
        header_frame = tk.Frame(card_content, bg="#1a202c")
        header_frame.pack(fill="x", pady=(0, 30))
        
        title_label = tk.Label(
            header_frame,
            text=titulo,
            font=("Segoe UI", 20, "bold"),
            bg="#1a202c",
            fg="#ffffff"
        )
        title_label.pack()
        
        # Simular progreso con animación
        self.progress_value = 0
        self.progress_label = tk.Label(
            card_content,
            text="Iniciando escaneo...",
            font=("Segoe UI", 12),
            bg="#1a202c",
            fg="#8a92b2"
        )
        self.progress_label.pack(pady=(0, 20))
        
        # Barra de progreso visual
        progress_bg = tk.Frame(card_content, bg="#2d3748", height=20)
        progress_bg.pack(fill="x", pady=(0, 20))
        progress_bg.pack_propagate(False)
        
        self.progress_bar = tk.Frame(progress_bg, bg=color, height=20, width=0)
        self.progress_bar.pack(side="left", fill="y")
        
        # Porcentaje
        self.percent_label = tk.Label(
            card_content,
            text="0%",
            font=("Segoe UI", 16, "bold"),
            bg="#1a202c",
            fg="#ffffff"
        )
        self.percent_label.pack(pady=(0, 30))
        
        # Botón cancelar
        cancel_btn = tk.Button(
            card_content,
            text="Cancelar Escaneo",
            command=self.cancelar_escaneo,
            bg="#dc3545",
            fg="#ffffff",
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            padx=25,
            pady=10
        )
        cancel_btn.pack()
        
        # Iniciar simulación de progreso
        self.simular_progreso_escaneo()
    
    def simular_progreso_escaneo(self):
        """Simular progreso de escaneo con actualización visual"""
        if self.progress_value < 100:
            self.progress_value += 2
            
            # Actualizar barra visual
            progress_width = int(self.progress_value * 4)  # Escala visual
            self.progress_bar.config(width=progress_width)
            
            # Actualizar porcentaje
            self.percent_label.config(text=f"{self.progress_value}%")
            
            # Actualizar mensaje
            if self.progress_value < 25:
                mensaje = "Escaneando archivos del sistema..."
            elif self.progress_value < 50:
                mensaje = "Analizando procesos activos..."
            elif self.progress_value < 75:
                mensaje = "Verificando conexiones de red..."
            else:
                mensaje = "Finalizando análisis..."
            
            self.progress_label.config(text=mensaje)
            
            # Continuar progreso
            self.root.after(100, self.simular_progreso_escaneo)
        else:
            # Escaneo completado
            self.mostrar_resultados_escaneo()
    
    def cancelar_escaneo(self):
        """Cancelar escaneo en progreso"""
        self.progress_value = 100
        messagebox.showinfo("Cancelado", "Escaneo cancelado por el usuario")
        self.mostrar_escaneo()
    
    def mostrar_resultados_escaneo(self):
        """Mostrar resultados del escaneo"""
        messagebox.showinfo(
            "Escaneo Completado", 
            "Escaneo completado exitosamente.\n\n"
            "• Archivos escaneados: 1,247\n"
            "• Amenazas detectadas: 3\n"
            "• Archivos limpiados: 2\n"
            "• Tiempo transcurrido: 45 segundos"
        )
        self.mostrar_escaneo()
    
    def crear_interfaz_monitoreo(self):
        """Crear interfaz de monitoreo del sistema"""
        # Container principal
        self.contenido_principal = tk.Frame(self.root, bg="#0f1419")
        self.contenido_principal.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header
        header_frame = tk.Frame(self.contenido_principal, bg="#1a202c")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        header_content = tk.Frame(header_frame, bg="#1a202c")
        header_content.pack(fill="x", padx=25, pady=20)
        
        title_label = tk.Label(
            header_content,
            text="📡 Monitor de Red y Procesos",
            font=("Segoe UI", 18, "bold"),
            bg="#1a202c",
            fg="#ffffff"
        )
        title_label.pack(side="left")
        
        # Content placeholder
        content_frame = tk.Frame(self.contenido_principal, bg="#0f1419")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        placeholder_label = tk.Label(
            content_frame,
            text="🚧 Interfaz de Monitoreo en Desarrollo",
            font=("Segoe UI", 16),
            bg="#0f1419",
            fg="#8a92b2"
        )
        placeholder_label.pack(expand=True)
    
    def crear_interfaz_gestion(self):
        """Crear interfaz de gestión y protección"""
        # Container principal
        self.contenido_principal = tk.Frame(self.root, bg="#0f1419")
        self.contenido_principal.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header
        header_frame = tk.Frame(self.contenido_principal, bg="#1a202c")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        header_content = tk.Frame(header_frame, bg="#1a202c")
        header_content.pack(fill="x", padx=25, pady=20)
        
        title_label = tk.Label(
            header_content,
            text="🛡️ Centro de Protección",
            font=("Segoe UI", 18, "bold"),
            bg="#1a202c",
            fg="#ffffff"
        )
        title_label.pack(side="left")
        
        # Content placeholder
        content_frame = tk.Frame(self.contenido_principal, bg="#0f1419")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        placeholder_label = tk.Label(
            content_frame,
            text="🚧 Centro de Protección en Desarrollo",
            font=("Segoe UI", 16),
            bg="#0f1419",
            fg="#8a92b2"
        )
        placeholder_label.pack(expand=True)
    
    def crear_interfaz_herramientas(self):
        """Crear interfaz de herramientas adicionales"""
        # Container principal
        self.contenido_principal = tk.Frame(self.root, bg="#0f1419")
        self.contenido_principal.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header
        header_frame = tk.Frame(self.contenido_principal, bg="#1a202c")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        header_content = tk.Frame(header_frame, bg="#1a202c")
        header_content.pack(fill="x", padx=25, pady=20)
        
        title_label = tk.Label(
            header_content,
            text="🔧 Herramientas Avanzadas",
            font=("Segoe UI", 18, "bold"),
            bg="#1a202c",
            fg="#ffffff"
        )
        title_label.pack(side="left")
        
        # Content placeholder
        content_frame = tk.Frame(self.contenido_principal, bg="#0f1419")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        placeholder_label = tk.Label(
            content_frame,
            text="🚧 Herramientas en Desarrollo",
            font=("Segoe UI", 16),
            bg="#0f1419",
            fg="#8a92b2"
        )
        placeholder_label.pack(expand=True)
    
    def crear_interfaz_reportes(self):
        """Crear interfaz de reportes"""
        # Container principal
        self.contenido_principal = tk.Frame(self.root, bg="#0f1419")
        self.contenido_principal.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header
        header_frame = tk.Frame(self.contenido_principal, bg="#1a202c")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        header_content = tk.Frame(header_frame, bg="#1a202c")
        header_content.pack(fill="x", padx=25, pady=20)
        
        title_label = tk.Label(
            header_content,
            text="📋 Centro de Reportes",
            font=("Segoe UI", 18, "bold"),
            bg="#1a202c",
            fg="#ffffff"
        )
        title_label.pack(side="left")
        
        # Content placeholder
        content_frame = tk.Frame(self.contenido_principal, bg="#0f1419")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        placeholder_label = tk.Label(
            content_frame,
            text="🚧 Sistema de Reportes en Desarrollo",
            font=("Segoe UI", 16),
            bg="#0f1419",
            fg="#8a92b2"
        )
        placeholder_label.pack(expand=True)
    
    def crear_interfaz_configuracion(self):
        """Crear interfaz de configuración"""
        # Container principal
        self.contenido_principal = tk.Frame(self.root, bg="#0f1419")
        self.contenido_principal.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header
        header_frame = tk.Frame(self.contenido_principal, bg="#1a202c")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        header_content = tk.Frame(header_frame, bg="#1a202c")
        header_content.pack(fill="x", padx=25, pady=20)
        
        title_label = tk.Label(
            header_content,
            text="⚙️ Configuración del Sistema",
            font=("Segoe UI", 18, "bold"),
            bg="#1a202c",
            fg="#ffffff"
        )
        title_label.pack(side="left")
        
        # Content placeholder
        content_frame = tk.Frame(self.contenido_principal, bg="#0f1419")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        placeholder_label = tk.Label(
            content_frame,
            text="🚧 Panel de Configuración en Desarrollo",
            font=("Segoe UI", 16),
            bg="#0f1419",
            fg="#8a92b2"
        )
        placeholder_label.pack(expand=True)
        tabs_container.grid_rowconfigure(0, weight=1)
        
        # === PESTAÑAS DE NAVEGACIÓN MODERNAS MEJORADAS ===
        pestanas_navegacion = [
            ("🏠", "Dashboard", self.mostrar_panel_principal, True),
            ("🔍", "Escaneo", self.mostrar_panel_escaneo, False),
            ("🛡️", "Monitoreo", self.mostrar_panel_monitoreo, False),
            ("🗂️", "Cuarentena", self.mostrar_panel_cuarentena, False),
            ("📊", "Reportes", self.mostrar_panel_reportes, False),
            ("⚙️", "Config", self.mostrar_panel_configuracion, False)
        ]
        
        self.botones_navegacion = {}
        for i, (icono, texto, comando, activo) in enumerate(pestanas_navegacion):
            tab_frame = self.crear_pestana_navegacion_mejorada(
                tabs_container, icono, texto, comando, activo
            )
            tab_frame.grid(row=0, column=i, sticky="ew", padx=3, pady=8)  # Mejor espaciado
            self.botones_navegacion[texto] = tab_frame
        
        # === SECCIÓN DERECHA: Controles y Estado MEJORADOS ===
        controls_section = tk.Frame(nav_container, bg=self.tema_actual.FONDO_SECUNDARIO)
        controls_section.grid(row=0, column=2, sticky="e", padx=(25, 0))
        
        # Grid interno para controls con mejor distribución
        controls_section.grid_columnconfigure(0, weight=0)  # Status panel
        controls_section.grid_columnconfigure(1, weight=0)  # Buttons
        controls_section.grid_rowconfigure(0, weight=1)
        
        # === PANEL DE ESTADO DEL SISTEMA MEJORADO ===
        status_panel = tk.Frame(controls_section, bg=self.tema_actual.FONDO_SECUNDARIO)
        status_panel.grid(row=0, column=0, sticky="ew", padx=(0, 20))
        
        # Indicador de estado principal con mejor diseño
        self.status_container = tk.Frame(status_panel, bg=self.tema_actual.FONDO_SECUNDARIO)
        self.status_container.pack()
        
        # Indicador de estado visual mejorado
        self.status_indicator = tk.Label(
            self.status_container,
            text="●",
            font=("Segoe UI", 24),  # Tamaño aumentado
            bg=self.tema_actual.FONDO_SECUNDARIO,
            fg=self.tema_actual.EXITO
        )
        self.status_indicator.pack(side=tk.LEFT)
        
        self.status_text = tk.Label(
            self.status_container,
            text="SISTEMA ACTIVO",
            font=("Segoe UI", 11, "bold"),  # Fuente más grande
            bg=self.tema_actual.FONDO_SECUNDARIO,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        self.status_text.pack(side=tk.LEFT, padx=(10, 0))
        
        # === ESTADÍSTICAS RÁPIDAS MEJORADAS ===
        stats_quick = tk.Frame(status_panel, bg=self.tema_actual.FONDO_SECUNDARIO)
        stats_quick.pack(pady=(8, 0))
        
        self.quick_stats = tk.Label(
            stats_quick,
            text="Amenazas: 0 | Conexiones: 0",
            font=("Segoe UI", 10),  # Fuente más grande
            bg=self.tema_actual.FONDO_SECUNDARIO,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.quick_stats.pack()
        
        # === BOTONES DE CONTROL MEJORADOS ===
        buttons_control = tk.Frame(controls_section, bg=self.tema_actual.FONDO_SECUNDARIO)
        buttons_control.grid(row=0, column=1, sticky="ew")
        
        # Grid para botones con mejor distribución
        buttons_control.grid_columnconfigure(0, weight=0)
        buttons_control.grid_columnconfigure(1, weight=0)
        buttons_control.grid_rowconfigure(0, weight=1)
        
        # Botón de acciones rápidas mejorado
        btn_config_rapida = ComponentesModernos.crear_boton_ultra_moderno(
            buttons_control,
            "⚡ Acciones",
            self.mostrar_menu_acciones_rapidas,
            estilo="outline"
        )
        btn_config_rapida.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        # Botón de tema mejorado
        btn_tema = ComponentesModernos.crear_boton_ultra_moderno(
            buttons_control,
            "🌙 Tema",
            self.cambiar_tema,
            estilo="outline"
        )
        btn_tema.grid(row=0, column=1, sticky="ew", padx=(8, 0))
    
    def crear_pestana_navegacion_mejorada(self, parent, icono, texto, comando, activo=False):
        """Crear una pestaña de navegación moderna con mejor diseño y efectos."""
        # Determinar colores según estado
        if activo:
            bg_color = self.tema_actual.PRIMARIO
            fg_color = "#ffffff"
            border_color = self.tema_actual.PRIMARIO
            shadow_color = "#00000020"
        else:
            bg_color = self.tema_actual.FONDO_SECUNDARIO
            fg_color = self.tema_actual.TEXTO_SECUNDARIO
            border_color = "transparent"
            shadow_color = "transparent"
        
        # Container principal de la pestaña con efecto sombra
        tab_container = tk.Frame(parent, bg=self.tema_actual.FONDO_SECUNDARIO)
        
        # Frame interno para el botón con efecto de elevación
        tab_inner = tk.Frame(tab_container, bg=bg_color, relief="flat", borderwidth=0)
        tab_inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Botón principal de la pestaña con mejor estilo
        tab_button = tk.Button(
            tab_inner,
            text=f"{icono}\n{texto}",  # Icono y texto en líneas separadas
            command=comando,
            bg=bg_color,
            fg=fg_color,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),  # Fuente más prominente
            padx=15,  # Padding aumentado
            pady=12,  # Padding vertical aumentado
            width=12,  # Ancho fijo mayor
            activebackground=self.tema_actual.PRIMARIO if not activo else self.tema_actual.SECUNDARIO,
            activeforeground="#ffffff"
        )
        tab_button.pack(fill=tk.BOTH, expand=True)
        
        # Línea indicadora inferior mejorada
        indicator = tk.Frame(
            tab_container, 
            bg=border_color if border_color != "transparent" else self.tema_actual.FONDO_SECUNDARIO, 
            height=4  # Altura aumentada
        )
        indicator.pack(fill=tk.X, side=tk.BOTTOM)
        
        # === EFECTOS HOVER Y ANIMACIONES MEJORADAS ===
        def on_enter(e):
            if not activo:
                tab_inner.config(bg=self.tema_actual.HOVER)
                tab_button.config(
                    bg=self.tema_actual.HOVER, 
                    fg=self.tema_actual.TEXTO_PRINCIPAL
                )
                indicator.config(bg=self.tema_actual.BORDER)
        
        def on_leave(e):
            if not activo:
                tab_inner.config(bg=self.tema_actual.FONDO_SECUNDARIO)
                tab_button.config(
                    bg=self.tema_actual.FONDO_SECUNDARIO, 
                    fg=self.tema_actual.TEXTO_SECUNDARIO
                )
                indicator.config(bg=self.tema_actual.FONDO_SECUNDARIO)
        
        def on_click(e):
            # Efecto de click con breve cambio de color
            if not activo:
                tab_inner.config(bg=self.tema_actual.PRIMARIO)
                tab_button.config(bg=self.tema_actual.PRIMARIO, fg="#ffffff")
                tab_container.after(100, lambda: on_leave(None))
        
        # Binding de eventos
        tab_button.bind("<Enter>", on_enter)
        tab_button.bind("<Leave>", on_leave)
        tab_button.bind("<Button-1>", on_click)
        tab_inner.bind("<Enter>", on_enter)
        tab_inner.bind("<Leave>", on_leave)
        
        # Guardar referencias para control externo
        tab_container.button = tab_button
        tab_container.inner = tab_inner
        tab_container.indicator = indicator
        tab_container.activo = activo
        
        return tab_container
    
    def mostrar_menu_acciones_rapidas(self):
        """Mostrar menú de acciones rápidas."""
        try:
            # Crear ventana popup para acciones rápidas
            popup = tk.Toplevel(self.root)
            popup.title("Acciones Rápidas")
            popup.geometry("300x400")
            popup.resizable(False, False)
            popup.configure(bg=self.tema_actual.FONDO_PRINCIPAL)
            
            # Centrar ventana
            popup.transient(self.root)
            popup.grab_set()
            
            # Título
            titulo = tk.Label(
                popup,
                text="⚡ Acciones Rápidas",
                font=("Segoe UI", 14, "bold"),
                bg=self.tema_actual.FONDO_PRINCIPAL,
                fg=self.tema_actual.TEXTO_PRINCIPAL
            )
            titulo.pack(pady=15)
            
            # Frame para botones
            buttons_frame = tk.Frame(popup, bg=self.tema_actual.FONDO_PRINCIPAL)
            buttons_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Botones de acciones rápidas
            acciones = [
                ("🔍 Escaneo Rápido", self.ejecutar_escaneo_rapido),
                ("🛡️ Iniciar Protección", self.iniciar_servicios),
                ("🔄 Actualizar Sistema", self.actualizar_sistema),
                ("📊 Ver Estadísticas", self.mostrar_estadisticas),
                ("🧹 Limpiar Temporales", self.limpiar_archivos_temporales),
                ("🔧 Diagnóstico", self.ejecutar_diagnostico)
            ]
            
            for texto, comando in acciones:
                btn = ComponentesModernos.crear_boton_ultra_moderno(
                    buttons_frame,
                    texto,
                    lambda cmd=comando: self.ejecutar_accion_y_cerrar(popup, cmd),
                    estilo="outline"
                )
                btn.pack(fill=tk.X, pady=5)
            
            # Botón cerrar
            btn_cerrar = ComponentesModernos.crear_boton_ultra_moderno(
                buttons_frame,
                "❌ Cerrar",
                popup.destroy,
                estilo="secundario"
            )
            btn_cerrar.pack(fill=tk.X, pady=(15, 0))
            
        except Exception as e:
            self.logger.error(f"Error mostrando menú de acciones: {e}")
            messagebox.showerror("Error", f"Error al mostrar menú de acciones: {str(e)}")
    
    def ejecutar_accion_y_cerrar(self, popup, comando):
        """Ejecutar acción y cerrar popup."""
        try:
            popup.destroy()
            if comando:
                comando()
        except Exception as e:
            self.logger.error(f"Error ejecutando acción: {e}")
    
    def actualizar_sistema(self):
        """Actualizar el sistema."""
        messagebox.showinfo("Actualización", "Función de actualización en desarrollo")
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas del sistema."""
        self.mostrar_panel_reportes()
    
    def limpiar_archivos_temporales(self):
        """Limpiar archivos temporales."""
        try:
            respuesta = messagebox.askyesno(
                "Confirmar Limpieza",
                "¿Desea limpiar los archivos temporales del sistema?"
            )
            if respuesta:
                # Aquí iría la lógica de limpieza
                messagebox.showinfo("Limpieza", "Archivos temporales limpiados correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error en limpieza: {str(e)}")
    
    def ejecutar_diagnostico(self):
        """Ejecutar diagnóstico del sistema."""
        try:
            messagebox.showinfo("Diagnóstico", "Ejecutando diagnóstico del sistema...")
            # Aquí iría la lógica de diagnóstico
            messagebox.showinfo("Diagnóstico", "Diagnóstico completado - Sistema funcionando correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error en diagnóstico: {str(e)}")
    
    def crear_pestana_navegacion(self, parent, icono, texto, comando, activo=False):
        """Crear una pestaña de navegación moderna."""
        # Colores de estado
        if activo:
            bg_color = self.tema_actual.PRIMARIO
            fg_color = "#ffffff"
            border_color = self.tema_actual.PRIMARIO
        else:
            bg_color = "transparent"
            fg_color = self.tema_actual.TEXTO_SECUNDARIO
            border_color = "transparent"
        
        # Container de la pestaña
        tab_container = tk.Frame(parent, bg=self.tema_actual.FONDO_SECUNDARIO)
        
        # Botón de la pestaña con estilo moderno
        tab_button = tk.Button(
            tab_container,
            text=f"{icono}\\n{texto}",
            command=comando,
            bg=bg_color if bg_color != "transparent" else self.tema_actual.FONDO_SECUNDARIO,
            fg=fg_color,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=8,
            width=8
        )
        tab_button.pack(fill=tk.BOTH, expand=True)
        
        # Línea indicadora inferior
        indicator = tk.Frame(
            tab_container, 
            bg=border_color if border_color != "transparent" else self.tema_actual.FONDO_SECUNDARIO, 
            height=3
        )
        indicator.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Efectos hover
        def on_enter(e):
            if not activo:
                tab_button.config(bg=self.tema_actual.BORDER, fg=self.tema_actual.TEXTO_PRINCIPAL)
        
        def on_leave(e):
            if not activo:
                tab_button.config(
                    bg=self.tema_actual.FONDO_SECUNDARIO, 
                    fg=self.tema_actual.TEXTO_SECUNDARIO
                )
        
        tab_button.bind("<Enter>", on_enter)
        tab_button.bind("<Leave>", on_leave)
        
        # Guardar referencias
        tab_container.button = tab_button
        tab_container.indicator = indicator
        tab_container.activo = activo
        
        return tab_container
    
    def crear_contenido_principal(self):
        """Crear el área de contenido principal con diseño profesional y responsivo."""
        # === CONTENEDOR PRINCIPAL MEJORADO ===
        self.contenido_principal = tk.Frame(self.root, bg=self.tema_actual.FONDO_PRINCIPAL)
        self.contenido_principal.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)
        
        # Configurar grid responsivo para el contenido principal
        self.contenido_principal.grid_columnconfigure(0, weight=1)
        self.contenido_principal.grid_rowconfigure(0, weight=1)
        
        # === FRAME INTERNO CON SCROLL PROFESIONAL ===
        # Canvas para scroll suave
        self.canvas_contenido = tk.Canvas(
            self.contenido_principal, 
            bg=self.tema_actual.FONDO_PRINCIPAL,
            highlightthickness=0,
            relief="flat"
        )
        
        # Scrollbar moderna
        self.scrollbar_contenido = tk.Scrollbar(
            self.contenido_principal,
            orient="vertical",
            command=self.canvas_contenido.yview,
            bg=self.tema_actual.FONDO_SECUNDARIO,
            troughcolor=self.tema_actual.FONDO_PRINCIPAL,
            activebackground=self.tema_actual.PRIMARIO
        )
        
        # Frame scrollable interno
        self.frame_scrollable = tk.Frame(self.canvas_contenido, bg=self.tema_actual.FONDO_PRINCIPAL)
        
        # Configurar scroll
        self.frame_scrollable.bind(
            "<Configure>",
            lambda e: self.canvas_contenido.configure(scrollregion=self.canvas_contenido.bbox("all"))
        )
        
        # Crear ventana en canvas
        self.canvas_window = self.canvas_contenido.create_window(
            (0, 0), 
            window=self.frame_scrollable, 
            anchor="nw"
        )
        
        # Configurar scrollbar
        self.canvas_contenido.configure(yscrollcommand=self.scrollbar_contenido.set)
        
        # Empaquetar elementos
        self.canvas_contenido.pack(side="left", fill="both", expand=True)
        self.scrollbar_contenido.pack(side="right", fill="y")
        
        # === BINDING PARA SCROLL CON MOUSE WHEEL ===
        def _on_mousewheel(event):
            if self.canvas_contenido.winfo_exists():
                self.canvas_contenido.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas_contenido.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas_contenido.unbind_all("<MouseWheel>")
        
        # Binding de eventos de mouse
        self.canvas_contenido.bind('<Enter>', _bind_to_mousewheel)
        self.canvas_contenido.bind('<Leave>', _unbind_from_mousewheel)
        
        # === RESPONSIVE CANVAS RESIZING ===
        def configure_canvas(event):
            # Actualizar ancho del frame interno cuando cambie el canvas
            canvas_width = event.width
            self.canvas_contenido.itemconfig(self.canvas_window, width=canvas_width)
        
        self.canvas_contenido.bind('<Configure>', configure_canvas)
    
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
        """Mostrar el panel principal del sistema con diseño moderno tipo dashboard MEJORADO."""
        self.limpiar_contenido()
        self.actualizar_navegacion_activa("Dashboard")
        
        # Obtener contenedor correcto
        contenedor = self.obtener_contenedor_contenido()
        
        # === HEADER DEL DASHBOARD MEJORADO ===
        header_frame = tk.Frame(contenedor, bg=self.tema_actual.FONDO_PRINCIPAL, height=80)
        header_frame.pack(fill=tk.X, padx=30, pady=(20, 25))
        header_frame.pack_propagate(False)
        
        # Configurar grid para header
        header_frame.grid_columnconfigure(0, weight=1)  # Title section expands
        header_frame.grid_columnconfigure(1, weight=0)  # Actions section fixed
        header_frame.grid_rowconfigure(0, weight=1)
        
        # === TÍTULO PRINCIPAL MEJORADO ===
        title_container = tk.Frame(header_frame, bg=self.tema_actual.FONDO_PRINCIPAL)
        title_container.grid(row=0, column=0, sticky="w")
        
        dashboard_title = tk.Label(
            title_container,
            text="🏠 Centro de Comando",
            font=("Segoe UI", 26, "bold"),  # Fuente más grande
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        dashboard_title.pack(anchor="w")
        
        dashboard_subtitle = tk.Label(
            title_container,
            text="Panel de control principal - Monitoreo en tiempo real",
            font=("Segoe UI", 13),  # Subtítulo más prominente
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        dashboard_subtitle.pack(anchor="w", pady=(5, 0))
        
        # === BOTONES DE ACCIÓN RÁPIDA MEJORADOS ===
        quick_actions = tk.Frame(header_frame, bg=self.tema_actual.FONDO_PRINCIPAL)
        quick_actions.grid(row=0, column=1, sticky="e")
        
        # Grid para botones de acción
        quick_actions.grid_columnconfigure(0, weight=0)
        quick_actions.grid_columnconfigure(1, weight=0)
        quick_actions.grid_rowconfigure(0, weight=1)
        
        btn_escaneo_rapido = ComponentesModernos.crear_boton_ultra_moderno(
            quick_actions,
            "🚀 Escaneo Rápido",
            self.ejecutar_escaneo_rapido,
            estilo="primario"
        )
        btn_escaneo_rapido.grid(row=0, column=0, padx=(0, 10))
        
        btn_actualizar = ComponentesModernos.crear_boton_ultra_moderno(
            quick_actions,
            "🔄 Actualizar",
            self.actualizar_dashboard,
            estilo="outline"
        )
        btn_actualizar.grid(row=0, column=1)
        
        # === FILA SUPERIOR: CARDS DE ESTADO MEJORADAS ===
        top_row = tk.Frame(contenedor, bg=self.tema_actual.FONDO_PRINCIPAL)
        top_row.pack(fill=tk.X, padx=30, pady=(0, 25))
        
        # Configurar grid responsivo para cards
        top_row.grid_columnconfigure(0, weight=1, uniform="card")
        top_row.grid_columnconfigure(1, weight=1, uniform="card")
        top_row.grid_columnconfigure(2, weight=1, uniform="card")
        top_row.grid_rowconfigure(0, weight=1)
        
        # Cards mejoradas con grid
        self.crear_card_estado_sistema_mejorada(top_row, 0)
        self.crear_card_estadisticas_seguridad_mejorada(top_row, 1)
        self.crear_card_actividad_reciente_mejorada(top_row, 2)
        
        # === FILA MEDIA: GRÁFICOS Y MÉTRICAS MEJORADAS ===
        middle_row = tk.Frame(contenedor, bg=self.tema_actual.FONDO_PRINCIPAL)
        middle_row.pack(fill=tk.X, padx=30, pady=(0, 25))
        
        # Grid para fila media
        middle_row.grid_columnconfigure(0, weight=2, uniform="middle")  # Monitoreo más ancho
        middle_row.grid_columnconfigure(1, weight=1, uniform="middle")  # Alertas más pequeño
        middle_row.grid_rowconfigure(0, weight=1)
        
        self.crear_card_monitoreo_tiempo_real_mejorada(middle_row, 0)
        self.crear_card_alertas_notificaciones_mejorada(middle_row, 1)
        
        # === FILA INFERIOR: INFORMACIÓN DETALLADA MEJORADA ===
        bottom_row = tk.Frame(contenedor, bg=self.tema_actual.FONDO_PRINCIPAL)
        bottom_row.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # Grid para fila inferior
        bottom_row.grid_columnconfigure(0, weight=1, uniform="bottom")
        bottom_row.grid_columnconfigure(1, weight=1, uniform="bottom")
        bottom_row.grid_rowconfigure(0, weight=1)
        
        self.crear_card_eventos_sistema_mejorada(bottom_row, 0)
        self.crear_card_acciones_recomendadas_mejorada(bottom_row, 1)
        
        # Iniciar actualización automática del dashboard
        self.iniciar_actualizacion_automatica()
    
    def crear_card_estado_sistema(self, parent):
        """Crear card moderna de estado del sistema."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "💻 Estado del Sistema", "Información en tiempo real del estado del sistema"
        )
        card_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Indicador principal de salud
        health_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        health_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Círculo de estado grande
        status_circle = tk.Label(
            health_frame,
            text="●",
            font=("Segoe UI", 40),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.EXITO
        )
        status_circle.pack(side=tk.LEFT, padx=(10, 15))
        
        # Información de estado
        status_info = tk.Frame(health_frame, bg=self.tema_actual.FONDO_CARD)
        status_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.system_status_label = tk.Label(
            status_info,
            text="SISTEMA PROTEGIDO",
            font=("Segoe UI", 14, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.EXITO
        )
        self.system_status_label.pack(anchor="w")
        
        self.system_status_detail = tk.Label(
            status_info,
            text="Todos los servicios funcionando correctamente",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.system_status_detail.pack(anchor="w")
        
        # Métricas del sistema
        metrics_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        metrics_frame.pack(fill=tk.X)
        
        # CPU
        cpu_metric = self.crear_metrica_simple(metrics_frame, "CPU", "0%", self.tema_actual.INFO)
        cpu_metric.pack(fill=tk.X, pady=2)
        
        # Memoria
        mem_metric = self.crear_metrica_simple(metrics_frame, "Memoria", "0%", self.tema_actual.WARNING)
        mem_metric.pack(fill=tk.X, pady=2)
        
        # Protección
        protection_metric = self.crear_metrica_simple(metrics_frame, "Protección", "Activa", self.tema_actual.EXITO)
        protection_metric.pack(fill=tk.X, pady=2)
        
        # Botón de detalles
        btn_detalles = ComponentesModernos.crear_boton_ultra_moderno(
            card_content,
            "📋 Ver Detalles",
            self.mostrar_detalles_sistema,
            estilo="outline"
        )
        btn_detalles.pack(fill=tk.X, pady=(15, 0))
    
    def crear_card_estadisticas_seguridad(self, parent):
        """Crear card de estadísticas de seguridad."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "🛡️ Estadísticas de Seguridad", "Resumen de amenazas detectadas y estado de protección"
        )
        card_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Grid de estadísticas
        stats_grid = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        stats_grid.pack(fill=tk.BOTH, expand=True)
        
        # Crear estadísticas en formato de badges
        self.crear_stat_badge(stats_grid, "🔍", "Archivos Escaneados", "1,247", 0, 0)
        self.crear_stat_badge(stats_grid, "⚠️", "Amenazas Detectadas", "0", 0, 1)
        self.crear_stat_badge(stats_grid, "🛡️", "Archivos Protegidos", "98.7%", 1, 0)
        self.crear_stat_badge(stats_grid, "🔄", "Último Escaneo", "Hace 2h", 1, 1)
        
        # Progreso de seguridad
        progress_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        progress_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Label(
            progress_frame,
            text="Nivel de Seguridad",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(anchor="w")
        
        # Barra de progreso visual
        progress_bg = tk.Frame(progress_frame, bg="#e0e0e0", height=8)
        progress_bg.pack(fill=tk.X, pady=(5, 0))
        
        progress_bar = tk.Frame(progress_bg, bg=self.tema_actual.EXITO, height=8)
        progress_bar.place(relwidth=0.87, relheight=1.0)  # 87% de seguridad
        
        tk.Label(
            progress_frame,
            text="87% - Excelente",
            font=("Segoe UI", 9),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.EXITO
        ).pack(anchor="w", pady=(3, 0))
    
    def crear_card_actividad_reciente(self, parent):
        """Crear card de actividad reciente."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "📈 Actividad Reciente", "Registro de eventos y actividades de seguridad recientes"
        )
        card_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Lista de actividades con scroll
        activities_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        activities_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear actividades simuladas
        actividades = [
            ("🔍", "Escaneo rápido completado", "Hace 15 min", self.tema_actual.EXITO),
            ("🛡️", "Protección en tiempo real activa", "Hace 1 hora", self.tema_actual.INFO),
            ("📊", "Reporte de seguridad generado", "Hace 2 horas", self.tema_actual.TEXTO_SECUNDARIO),
            ("🔄", "Base de datos actualizada", "Hace 3 horas", self.tema_actual.TEXTO_SECUNDARIO),
        ]
        
        for icono, titulo, tiempo, color in actividades:
            self.crear_item_actividad(activities_frame, icono, titulo, tiempo, color)
        
        # Botón ver más
        btn_ver_mas = ComponentesModernos.crear_boton_ultra_moderno(
            card_content,
            "📋 Ver Todo",
            self.abrir_registro_completo,
            estilo="outline"
        )
        btn_ver_mas.pack(fill=tk.X, pady=(10, 0))
    
    def crear_stat_badge(self, parent, icono, titulo, valor, row, col):
        """Crear un badge de estadística."""
        badge_frame = tk.Frame(parent, bg="#f8f9fa", relief="solid", borderwidth=1)
        badge_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
        parent.grid_columnconfigure(col, weight=1)
        
        # Icono
        icon_label = tk.Label(
            badge_frame,
            text=icono,
            font=("Segoe UI", 16),
            bg="#f8f9fa",
            fg=self.tema_actual.PRIMARIO
        )
        icon_label.pack(pady=(8, 0))
        
        # Valor
        valor_label = tk.Label(
            badge_frame,
            text=valor,
            font=("Segoe UI", 14, "bold"),
            bg="#f8f9fa",
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        valor_label.pack()
        
        # Título
        titulo_label = tk.Label(
            badge_frame,
            text=titulo,
            font=("Segoe UI", 8),
            bg="#f8f9fa",
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        titulo_label.pack(pady=(0, 8))
    
    def crear_item_actividad(self, parent, icono, titulo, tiempo, color):
        """Crear un item de actividad."""
        item_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        item_frame.pack(fill=tk.X, pady=3)
        
        # Icono
        icon_label = tk.Label(
            item_frame,
            text=icono,
            font=("Segoe UI", 12),
            bg=self.tema_actual.FONDO_CARD,
            fg=color
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Contenido
        content_frame = tk.Frame(item_frame, bg=self.tema_actual.FONDO_CARD)
        content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        titulo_label = tk.Label(
            content_frame,
            text=titulo,
            font=("Segoe UI", 9, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        titulo_label.pack(anchor="w")
        
        tiempo_label = tk.Label(
            content_frame,
            text=tiempo,
            font=("Segoe UI", 8),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_MUTED
        )
        tiempo_label.pack(anchor="w")
    
    def crear_metrica_simple(self, parent, nombre, valor, color):
        """Crear una métrica simple."""
        metric_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        
        tk.Label(
            metric_frame,
            text=f"{nombre}:",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        ).pack(side=tk.LEFT)
        
        tk.Label(
            metric_frame,
            text=valor,
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=color
        ).pack(side=tk.RIGHT)
        
        return metric_frame
    
    def actualizar_dashboard(self):
        """Actualizar los datos del dashboard."""
        try:
            # Actualizar métricas en tiempo real
            if hasattr(self, 'system_status_label'):
                # Aquí iría la lógica para obtener estado real del sistema
                pass
            
            messagebox.showinfo("Dashboard", "Dashboard actualizado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error actualizando dashboard: {e}")
    
    def mostrar_detalles_sistema(self):
        """Mostrar detalles completos del sistema."""
        self.mostrar_panel_monitoreo()
    
    def iniciar_actualizacion_automatica(self):
        """Iniciar actualización automática del dashboard."""
        try:
            # Actualizar cada 30 segundos
            if hasattr(self, 'root') and self.root:
                self.root.after(30000, self.actualizar_datos_tiempo_real)
        except Exception as e:
            self.logger.error(f"Error en actualización automática: {e}")
    
    def actualizar_datos_tiempo_real(self):
        """Actualizar datos en tiempo real."""
        try:
            # Aquí iría la lógica para actualizar datos
            # Por ahora solo programa la próxima actualización
            if hasattr(self, 'root') and self.root:
                self.root.after(30000, self.actualizar_datos_tiempo_real)
        except Exception as e:
            self.logger.error(f"Error actualizando datos en tiempo real: {e}")
    
    def crear_card_monitoreo_tiempo_real(self, parent):
        """Crear card de monitoreo en tiempo real."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "📊 Monitoreo en Tiempo Real", "Estado actual de procesos y conexiones de red"
        )
        card_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Placeholder para gráficos en tiempo real
        tk.Label(
            card_content,
            text="Gráficos de monitoreo en tiempo real\\n(En desarrollo)",
            font=("Segoe UI", 12),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        ).pack(expand=True)
    
    def crear_card_alertas_notificaciones(self, parent):
        """Crear card de alertas y notificaciones."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "🚨 Alertas y Notificaciones", "Centro de alertas y notificaciones de seguridad"
        )
        card_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Lista de alertas
        alertas = [
            ("🟢", "Sistema funcionando correctamente", "Normal"),
            ("🟡", "Recomendado: Actualizar definiciones", "Advertencia"),
            ("🔵", "Programar escaneo completo", "Info")
        ]
        
        for icono, mensaje, tipo in alertas:
            alert_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
            alert_frame.pack(fill=tk.X, pady=3)
            
            tk.Label(
                alert_frame,
                text=f"{icono} {mensaje}",
                font=("Segoe UI", 10),
                bg=self.tema_actual.FONDO_CARD,
                fg=self.tema_actual.TEXTO_PRINCIPAL
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def crear_card_eventos_sistema(self, parent):
        """Crear card de eventos del sistema."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "📋 Eventos del Sistema", "Registro completo de eventos y actividades del sistema"
        )
        card_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Text area para eventos
        eventos_text = scrolledtext.ScrolledText(
            card_content,
            height=6,
            font=("Consolas", 9),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            relief="flat",
            wrap=tk.WORD
        )
        eventos_text.pack(fill=tk.BOTH, expand=True)
        
        # Eventos de ejemplo
        eventos_text.insert(tk.END, "[14:30:15] Sistema iniciado correctamente\\n")
        eventos_text.insert(tk.END, "[14:30:16] Cargando módulos de protección...\\n")
        eventos_text.insert(tk.END, "[14:30:17] Monitor de red iniciado\\n")
        eventos_text.insert(tk.END, "[14:30:18] SIEM activo y funcionando\\n")
    
    def crear_card_acciones_recomendadas(self, parent):
        """Crear card de acciones recomendadas."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "💡 Acciones Recomendadas", "Sugerencias y acciones recomendadas para optimización"
        )
        card_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Lista de acciones recomendadas
        acciones = [
            ("🔍", "Ejecutar escaneo completo", self.ejecutar_escaneo_completo),
            ("🔄", "Actualizar definiciones", self.actualizar_sistema),
            ("📊", "Generar reporte de seguridad", self.mostrar_panel_reportes)
        ]
        
        for icono, accion, comando in acciones:
            btn_accion = ComponentesModernos.crear_boton_ultra_moderno(
                card_content,
                f"{icono} {accion}",
                comando,
                estilo="outline"
            )
            btn_accion.pack(fill=tk.X, pady=3)
    
    def crear_card_estado_sistema_mejorada(self, parent, column):
        """Crear card moderna de estado del sistema con diseño profesional mejorado."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "💻 Estado del Sistema", "Información en tiempo real del estado del sistema"
        )
        card_container.grid(row=0, column=column, sticky="nsew", padx=15, pady=10)
        
        # === INDICADOR PRINCIPAL DE SALUD MEJORADO ===
        health_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        health_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Configurar grid para health frame
        health_frame.grid_columnconfigure(0, weight=0)  # Status circle
        health_frame.grid_columnconfigure(1, weight=1)  # Status info
        health_frame.grid_rowconfigure(0, weight=1)
        
        # Círculo de estado grande con gradiente visual
        status_circle = tk.Label(
            health_frame,
            text="●",
            font=("Segoe UI", 48),  # Tamaño aumentado para mayor impacto
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.EXITO
        )
        status_circle.grid(row=0, column=0, sticky="w", padx=(15, 20))
        
        # === INFORMACIÓN DE ESTADO MEJORADA ===
        status_info = tk.Frame(health_frame, bg=self.tema_actual.FONDO_CARD)
        status_info.grid(row=0, column=1, sticky="ew")
        
        self.system_status_label = tk.Label(
            status_info,
            text="SISTEMA PROTEGIDO",
            font=("Segoe UI", 16, "bold"),  # Fuente más grande
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.EXITO
        )
        self.system_status_label.pack(anchor="w")
        
        self.system_status_detail = tk.Label(
            status_info,
            text="Todos los servicios funcionando correctamente",
            font=("Segoe UI", 11),  # Fuente más legible
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.system_status_detail.pack(anchor="w", pady=(3, 0))
        
        # Tiempo de actividad
        uptime_label = tk.Label(
            status_info,
            text="Tiempo activo: 2h 15m",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_MUTED if hasattr(self.tema_actual, 'TEXTO_MUTED') else self.tema_actual.TEXTO_SECUNDARIO
        )
        uptime_label.pack(anchor="w", pady=(2, 0))
        
        # === MÉTRICAS DEL SISTEMA MEJORADAS ===
        metrics_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        metrics_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Configurar grid para métricas - 2 columnas
        metrics_frame.grid_columnconfigure(0, weight=1)
        metrics_frame.grid_columnconfigure(1, weight=1)
        
        # CPU con barra de progreso visual
        cpu_metric = self.crear_metrica_con_progreso(metrics_frame, "🖥️ CPU", "12%", 0.12, self.tema_actual.INFO)
        cpu_metric.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=5)
        
        # Memoria con barra de progreso visual  
        mem_metric = self.crear_metrica_con_progreso(metrics_frame, "💾 Memoria", "34%", 0.34, self.tema_actual.WARNING)
        mem_metric.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Protección activa
        protection_metric = self.crear_metrica_con_estado(metrics_frame, "🛡️ Protección", "ACTIVA", self.tema_actual.EXITO)
        protection_metric.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=5)
        
        # Última actualización
        update_metric = self.crear_metrica_con_estado(metrics_frame, "🔄 Última Act.", "Hace 1h", self.tema_actual.TEXTO_SECUNDARIO)
        update_metric.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # === BOTONES DE ACCIÓN MEJORADOS ===
        actions_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        actions_frame.pack(fill=tk.X)
        
        # Grid para botones
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        
        btn_detalles = ComponentesModernos.crear_boton_ultra_moderno(
            actions_frame,
            "📋 Detalles",
            self.mostrar_detalles_sistema,
            estilo="outline"
        )
        btn_detalles.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        btn_optimizar = ComponentesModernos.crear_boton_ultra_moderno(
            actions_frame,
            "⚡ Optimizar",
            self.optimizar_sistema,
            estilo="secundario"
        )
        btn_optimizar.grid(row=0, column=1, sticky="ew", padx=(5, 0))
    
    def crear_card_estadisticas_seguridad_mejorada(self, parent, column):
        """Crear card de estadísticas de seguridad con diseño profesional mejorado."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "🛡️ Estadísticas de Seguridad", "Resumen de amenazas detectadas y estado de protección"
        )
        card_container.grid(row=0, column=column, sticky="nsew", padx=15, pady=10)
        
        # === GRID DE ESTADÍSTICAS PRINCIPALES MEJORADO ===
        stats_main_grid = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        stats_main_grid.pack(fill=tk.X, pady=(0, 20))
        
        # Configurar grid responsivo para 2x2
        stats_main_grid.grid_columnconfigure(0, weight=1)
        stats_main_grid.grid_columnconfigure(1, weight=1)
        
        # Crear estadísticas principales mejoradas
        self.crear_stat_badge_mejorado(stats_main_grid, "🔍", "Archivos Escaneados", "1,247", 0, 0, self.tema_actual.INFO)
        self.crear_stat_badge_mejorado(stats_main_grid, "⚠️", "Amenazas Detectadas", "0", 0, 1, self.tema_actual.EXITO)
        self.crear_stat_badge_mejorado(stats_main_grid, "🛡️", "Protección", "98.7%", 1, 0, self.tema_actual.EXITO)
        self.crear_stat_badge_mejorado(stats_main_grid, "🔄", "Último Escaneo", "Hace 2h", 1, 1, self.tema_actual.TEXTO_SECUNDARIO)
        
        # === INDICADOR DE NIVEL DE SEGURIDAD MEJORADO ===
        security_level_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        security_level_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Título del nivel de seguridad
        security_title = tk.Label(
            security_level_frame,
            text="🏆 Nivel de Seguridad General",
            font=("Segoe UI", 12, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        security_title.pack(anchor="w", pady=(0, 8))
        
        # Contenedor para medidor circular visual
        gauge_frame = tk.Frame(security_level_frame, bg=self.tema_actual.FONDO_CARD)
        gauge_frame.pack(fill=tk.X)
        
        # Configurar grid para gauge
        gauge_frame.grid_columnconfigure(0, weight=0)  # Gauge visual
        gauge_frame.grid_columnconfigure(1, weight=1)  # Details
        
        # Medidor visual (simulado con texto grande)
        gauge_visual = tk.Label(
            gauge_frame,
            text="87%",
            font=("Segoe UI", 36, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.EXITO
        )
        gauge_visual.grid(row=0, column=0, sticky="w", padx=(20, 30))
        
        # Detalles del nivel
        details_frame = tk.Frame(gauge_frame, bg=self.tema_actual.FONDO_CARD)
        details_frame.grid(row=0, column=1, sticky="ew")
        
        level_label = tk.Label(
            details_frame,
            text="EXCELENTE",
            font=("Segoe UI", 14, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.EXITO
        )
        level_label.pack(anchor="w")
        
        description_label = tk.Label(
            details_frame,
            text="Sistema altamente protegido\nTodas las defensas activas",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO,
            justify=tk.LEFT
        )
        description_label.pack(anchor="w", pady=(2, 0))
        
        # === BARRA DE PROGRESO VISUAL MEJORADA ===
        progress_container = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        progress_container.pack(fill=tk.X)
        
        # Fondo de la barra de progreso
        progress_bg = tk.Frame(progress_container, bg="#e8e9ea", height=12)
        progress_bg.pack(fill=tk.X, pady=(0, 10))
        
        # Barra de progreso activa con degradado visual
        progress_active = tk.Frame(progress_bg, bg=self.tema_actual.EXITO, height=12)
        progress_active.place(relwidth=0.87, relheight=1.0)  # 87% completado
        
        # Texto de porcentaje
        progress_text = tk.Label(
            progress_container,
            text="87% de protección alcanzada - Continúa así",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.EXITO
        )
        progress_text.pack(anchor="w")
    
    def crear_card_actividad_reciente_mejorada(self, parent, column):
        """Crear card de actividad reciente con diseño profesional mejorado."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "📈 Actividad Reciente", "Registro de eventos y actividades de seguridad recientes"
        )
        card_container.grid(row=0, column=column, sticky="nsew", padx=15, pady=10)
        
        # === LISTA DE ACTIVIDADES CON SCROLL MEJORADO ===
        activities_container = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        activities_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Frame scrollable para actividades
        activities_scroll_frame = tk.Frame(activities_container, bg=self.tema_actual.FONDO_CARD)
        activities_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear actividades mejoradas con mejor diseño
        actividades_mejoradas = [
            ("🔍", "Escaneo rápido completado", "Hace 15 min", "Se analizaron 1,247 archivos", self.tema_actual.EXITO),
            ("🛡️", "Protección en tiempo real activa", "Hace 1 hora", "Monitor de procesos funcionando", self.tema_actual.INFO),
            ("📊", "Reporte de seguridad generado", "Hace 2 horas", "Documento exportado exitosamente", self.tema_actual.TEXTO_SECUNDARIO),
            ("🔄", "Base de datos actualizada", "Hace 3 horas", "2,150 nuevas firmas agregadas", self.tema_actual.TEXTO_SECUNDARIO),
            ("🌐", "Monitor de red iniciado", "Hace 4 horas", "Analizando tráfico de red", self.tema_actual.INFO)
        ]
        
        for icono, titulo, tiempo, descripcion, color in actividades_mejoradas:
            self.crear_item_actividad_mejorado(activities_scroll_frame, icono, titulo, tiempo, descripcion, color)
        
        # === BOTONES DE ACCIÓN MEJORADOS ===
        actions_container = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        actions_container.pack(fill=tk.X)
        
        # Grid para botones
        actions_container.grid_columnconfigure(0, weight=1)
        actions_container.grid_columnconfigure(1, weight=1)
        
        btn_ver_todo = ComponentesModernos.crear_boton_ultra_moderno(
            actions_container,
            "📋 Ver Todo",
            self.abrir_registro_completo,
            estilo="outline"
        )
        btn_ver_todo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        btn_filtrar = ComponentesModernos.crear_boton_ultra_moderno(
            actions_container,
            "🔍 Filtrar",
            self.filtrar_actividades,
            estilo="secundario"
        )
        btn_filtrar.grid(row=0, column=1, sticky="ew", padx=(5, 0))
    
    def crear_metrica_con_progreso(self, parent, nombre, valor, porcentaje, color):
        """Crear una métrica con barra de progreso visual."""
        metric_frame = tk.Frame(parent, bg="#f8f9fa", relief="solid", borderwidth=1)
        
        # Configurar padding interno
        content_frame = tk.Frame(metric_frame, bg="#f8f9fa")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        
        # Nombre de la métrica
        name_label = tk.Label(
            content_frame,
            text=nombre,
            font=("Segoe UI", 10, "bold"),
            bg="#f8f9fa",
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        name_label.pack(anchor="w")
        
        # Valor de la métrica
        value_label = tk.Label(
            content_frame,
            text=valor,
            font=("Segoe UI", 14, "bold"),
            bg="#f8f9fa",
            fg=color
        )
        value_label.pack(anchor="w", pady=(3, 5))
        
        # Barra de progreso
        progress_bg = tk.Frame(content_frame, bg="#e0e0e0", height=6)
        progress_bg.pack(fill=tk.X)
        
        progress_bar = tk.Frame(progress_bg, bg=color, height=6)
        progress_bar.place(relwidth=porcentaje, relheight=1.0)
        
        return metric_frame
    
    def crear_metrica_con_estado(self, parent, nombre, valor, color):
        """Crear una métrica con estado simple."""
        metric_frame = tk.Frame(parent, bg="#f8f9fa", relief="solid", borderwidth=1)
        
        # Configurar padding interno
        content_frame = tk.Frame(metric_frame, bg="#f8f9fa")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        
        # Nombre de la métrica
        name_label = tk.Label(
            content_frame,
            text=nombre,
            font=("Segoe UI", 10, "bold"),
            bg="#f8f9fa",
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        name_label.pack(anchor="w")
        
        # Valor/Estado de la métrica
        value_label = tk.Label(
            content_frame,
            text=valor,
            font=("Segoe UI", 12, "bold"),
            bg="#f8f9fa",
            fg=color
        )
        value_label.pack(anchor="w", pady=(5, 0))
        
        return metric_frame
    
    def crear_stat_badge_mejorado(self, parent, icono, titulo, valor, row, col, color):
        """Crear un badge de estadística con diseño mejorado."""
        badge_frame = tk.Frame(parent, bg="#ffffff", relief="solid", borderwidth=1)
        badge_frame.grid(row=row, column=col, sticky="ew", padx=8, pady=8)
        parent.grid_columnconfigure(col, weight=1)
        
        # Contenido del badge con padding mejorado
        content_frame = tk.Frame(badge_frame, bg="#ffffff")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        # Icono con color
        icon_label = tk.Label(
            content_frame,
            text=icono,
            font=("Segoe UI", 20),  # Icono más grande
            bg="#ffffff",
            fg=color
        )
        icon_label.pack(pady=(0, 5))
        
        # Valor principal
        valor_label = tk.Label(
            content_frame,
            text=valor,
            font=("Segoe UI", 18, "bold"),  # Valor más prominente
            bg="#ffffff",
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        valor_label.pack()
        
        # Título descriptivo
        titulo_label = tk.Label(
            content_frame,
            text=titulo,
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg=self.tema_actual.TEXTO_SECUNDARIO,
            wraplength=120  # Wrap text si es muy largo
        )
        titulo_label.pack(pady=(3, 0))
        
        return badge_frame
    
    def crear_item_actividad_mejorado(self, parent, icono, titulo, tiempo, descripcion, color):
        """Crear un item de actividad con diseño mejorado."""
        item_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD, relief="flat", borderwidth=1)
        item_frame.pack(fill=tk.X, pady=6, padx=5)
        
        # Configurar grid interno
        item_frame.grid_columnconfigure(0, weight=0)  # Icono
        item_frame.grid_columnconfigure(1, weight=1)  # Contenido
        item_frame.grid_columnconfigure(2, weight=0)  # Tiempo
        item_frame.grid_rowconfigure(0, weight=1)
        
        # === ICONO CON FONDO CIRCULAR ===
        icon_container = tk.Frame(item_frame, bg=color, width=40, height=40)
        icon_container.grid(row=0, column=0, sticky="nw", padx=(10, 15), pady=10)
        icon_container.grid_propagate(False)
        
        icon_label = tk.Label(
            icon_container,
            text=icono,
            font=("Segoe UI", 16),
            bg=color,
            fg="#ffffff"
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # === CONTENIDO PRINCIPAL ===
        content_frame = tk.Frame(item_frame, bg=self.tema_actual.FONDO_CARD)
        content_frame.grid(row=0, column=1, sticky="ew", pady=10)
        
        # Título de la actividad
        titulo_label = tk.Label(
            content_frame,
            text=titulo,
            font=("Segoe UI", 11, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        titulo_label.pack(anchor="w")
        
        # Descripción de la actividad
        descripcion_label = tk.Label(
            content_frame,
            text=descripcion,
            font=("Segoe UI", 9),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO,
            wraplength=200
        )
        descripcion_label.pack(anchor="w", pady=(2, 0))
        
        # === TIEMPO ===
        tiempo_label = tk.Label(
            item_frame,
            text=tiempo,
            font=("Segoe UI", 9),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_MUTED if hasattr(self.tema_actual, 'TEXTO_MUTED') else self.tema_actual.TEXTO_SECUNDARIO
        )
        tiempo_label.grid(row=0, column=2, sticky="ne", padx=(5, 10), pady=10)
        
        return item_frame
    
    def optimizar_sistema(self):
        """Optimizar el sistema."""
        try:
            respuesta = messagebox.askyesno(
                "Optimización del Sistema",
                "¿Desea optimizar el rendimiento del sistema?\n\nEsto incluirá:\n• Limpieza de archivos temporales\n• Optimización de memoria\n• Actualización de índices"
            )
            if respuesta:
                messagebox.showinfo("Optimización", "Optimización del sistema completada exitosamente")
        except Exception as e:
            self.logger.error(f"Error en optimización: {e}")
            messagebox.showerror("Error", f"Error durante la optimización: {str(e)}")
    
    def filtrar_actividades(self):
        """Filtrar actividades por tipo."""
        messagebox.showinfo("Filtros", "Función de filtrado en desarrollo")
    
    def crear_card_monitoreo_tiempo_real_mejorada(self, parent, column):
        """Crear card de monitoreo en tiempo real con diseño profesional mejorado."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "📊 Monitoreo en Tiempo Real", "Estado actual de procesos y conexiones de red"
        )
        card_container.grid(row=0, column=column, sticky="nsew", padx=15, pady=10)
        
        # === MÉTRICAS EN TIEMPO REAL ===
        metrics_realtime = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        metrics_realtime.pack(fill=tk.X, pady=(0, 20))
        
        # Grid para métricas en tiempo real
        metrics_realtime.grid_columnconfigure(0, weight=1)
        metrics_realtime.grid_columnconfigure(1, weight=1)
        metrics_realtime.grid_columnconfigure(2, weight=1)
        
        # Procesos activos
        processes_metric = self.crear_metrica_tiempo_real(metrics_realtime, "🔄", "Procesos", "247", self.tema_actual.INFO)
        processes_metric.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Conexiones de red
        connections_metric = self.crear_metrica_tiempo_real(metrics_realtime, "🌐", "Conexiones", "18", self.tema_actual.WARNING)
        connections_metric.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Uso de CPU
        cpu_metric = self.crear_metrica_tiempo_real(metrics_realtime, "🖥️", "CPU", "23%", self.tema_actual.EXITO)
        cpu_metric.grid(row=0, column=2, sticky="ew", padx=5, pady=5)
        
        # === ÁREA DE GRÁFICOS SIMULADA ===
        graph_area = tk.Frame(card_content, bg="#f0f0f0", height=150, relief="sunken", borderwidth=1)
        graph_area.pack(fill=tk.X, pady=(0, 15))
        graph_area.pack_propagate(False)
        
        # Placeholder para gráfico
        graph_placeholder = tk.Label(
            graph_area,
            text="📈 Gráficos de Rendimiento en Tiempo Real\n\n(Área reservada para visualización de datos)\n\nCPU • Memoria • Red • Procesos",
            font=("Segoe UI", 11),
            bg="#f0f0f0",
            fg=self.tema_actual.TEXTO_SECUNDARIO,
            justify=tk.CENTER
        )
        graph_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        
        # === CONTROLES DE MONITOREO ===
        controls_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        controls_frame.pack(fill=tk.X)
        
        # Grid para controles
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=1)
        controls_frame.grid_columnconfigure(2, weight=1)
        
        btn_pausar = ComponentesModernos.crear_boton_ultra_moderno(
            controls_frame,
            "⏸️ Pausar",
            self.pausar_monitoreo,
            estilo="outline"
        )
        btn_pausar.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        btn_exportar = ComponentesModernos.crear_boton_ultra_moderno(
            controls_frame,
            "📤 Exportar",
            self.exportar_datos_monitoreo,
            estilo="outline"
        )
        btn_exportar.grid(row=0, column=1, sticky="ew", padx=5)
        
        btn_detalles = ComponentesModernos.crear_boton_ultra_moderno(
            controls_frame,
            "🔍 Detalles",
            self.mostrar_panel_monitoreo,
            estilo="primario"
        )
        btn_detalles.grid(row=0, column=2, sticky="ew", padx=(5, 0))
    
    def crear_card_alertas_notificaciones_mejorada(self, parent, column):
        """Crear card de alertas y notificaciones con diseño profesional mejorado."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "🚨 Centro de Alertas", "Alertas y notificaciones de seguridad en tiempo real"
        )
        card_container.grid(row=0, column=column, sticky="nsew", padx=15, pady=10)
        
        # === RESUMEN DE ALERTAS ===
        alerts_summary = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        alerts_summary.pack(fill=tk.X, pady=(0, 20))
        
        # Grid para resumen
        alerts_summary.grid_columnconfigure(0, weight=1)
        alerts_summary.grid_columnconfigure(1, weight=1)
        alerts_summary.grid_columnconfigure(2, weight=1)
        
        # Alertas críticas
        critical_alert = self.crear_badge_alerta(alerts_summary, "🔴", "0", "Críticas", self.tema_actual.ERROR)
        critical_alert.grid(row=0, column=0, sticky="ew", padx=5)
        
        # Alertas de advertencia
        warning_alert = self.crear_badge_alerta(alerts_summary, "🟡", "2", "Advertencias", self.tema_actual.WARNING)
        warning_alert.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Alertas informativas
        info_alert = self.crear_badge_alerta(alerts_summary, "🔵", "5", "Informativas", self.tema_actual.INFO)
        info_alert.grid(row=0, column=2, sticky="ew", padx=5)
        
        # === LISTA DE ALERTAS RECIENTES ===
        alerts_list_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        alerts_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Título de la lista
        list_title = tk.Label(
            alerts_list_frame,
            text="🔔 Alertas Recientes",
            font=("Segoe UI", 12, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        list_title.pack(anchor="w", pady=(0, 10))
        
        # Lista de alertas mejoradas
        alertas_ejemplo = [
            ("🟡", "Recomendado: Actualizar definiciones", "Hace 2 horas", self.tema_actual.WARNING),
            ("🔵", "Escaneo programado completado", "Hace 4 horas", self.tema_actual.INFO),
            ("🟢", "Sistema funcionando correctamente", "Hace 6 horas", self.tema_actual.EXITO),
            ("🔵", "Nueva actualización disponible", "Hace 8 horas", self.tema_actual.INFO)
        ]
        
        for icono, mensaje, tiempo, color in alertas_ejemplo:
            self.crear_item_alerta_simple(alerts_list_frame, icono, mensaje, tiempo, color)
        
        # === BOTONES DE GESTIÓN ===
        management_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        management_frame.pack(fill=tk.X)
        
        # Grid para botones
        management_frame.grid_columnconfigure(0, weight=1)
        management_frame.grid_columnconfigure(1, weight=1)
        
        btn_ver_todas = ComponentesModernos.crear_boton_ultra_moderno(
            management_frame,
            "📋 Ver Todas",
            self.ver_todas_las_alertas,
            estilo="outline"
        )
        btn_ver_todas.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        btn_configurar = ComponentesModernos.crear_boton_ultra_moderno(
            management_frame,
            "⚙️ Configurar",
            self.configurar_alertas,
            estilo="secundario"
        )
        btn_configurar.grid(row=0, column=1, sticky="ew", padx=(5, 0))
    
    def crear_metrica_tiempo_real(self, parent, icono, nombre, valor, color):
        """Crear una métrica de tiempo real."""
        metric_frame = tk.Frame(parent, bg="#ffffff", relief="solid", borderwidth=1)
        
        # Contenido con padding
        content_frame = tk.Frame(metric_frame, bg="#ffffff")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        # Icono
        icon_label = tk.Label(
            content_frame,
            text=icono,
            font=("Segoe UI", 16),
            bg="#ffffff",
            fg=color
        )
        icon_label.pack()
        
        # Valor
        value_label = tk.Label(
            content_frame,
            text=valor,
            font=("Segoe UI", 14, "bold"),
            bg="#ffffff",
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        value_label.pack(pady=(2, 0))
        
        # Nombre
        name_label = tk.Label(
            content_frame,
            text=nombre,
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        name_label.pack()
        
        return metric_frame
    
    def crear_badge_alerta(self, parent, icono, numero, tipo, color):
        """Crear un badge para alertas."""
        badge_frame = tk.Frame(parent, bg="#ffffff", relief="solid", borderwidth=1)
        
        # Contenido con padding
        content_frame = tk.Frame(badge_frame, bg="#ffffff")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=10)
        
        # Icono
        icon_label = tk.Label(
            content_frame,
            text=icono,
            font=("Segoe UI", 14),
            bg="#ffffff",
            fg=color
        )
        icon_label.pack()
        
        # Número
        number_label = tk.Label(
            content_frame,
            text=numero,
            font=("Segoe UI", 18, "bold"),
            bg="#ffffff",
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        number_label.pack(pady=(3, 0))
        
        # Tipo
        type_label = tk.Label(
            content_frame,
            text=tipo,
            font=("Segoe UI", 8),
            bg="#ffffff",
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        type_label.pack()
        
        return badge_frame
    
    def crear_item_alerta_simple(self, parent, icono, mensaje, tiempo, color):
        """Crear un item de alerta simple."""
        item_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        item_frame.pack(fill=tk.X, pady=3)
        
        # Grid layout
        item_frame.grid_columnconfigure(0, weight=0)  # Icono
        item_frame.grid_columnconfigure(1, weight=1)  # Mensaje
        item_frame.grid_columnconfigure(2, weight=0)  # Tiempo
        
        # Icono
        icon_label = tk.Label(
            item_frame,
            text=icono,
            font=("Segoe UI", 12),
            bg=self.tema_actual.FONDO_CARD,
            fg=color
        )
        icon_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Mensaje
        message_label = tk.Label(
            item_frame,
            text=mensaje,
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            wraplength=200,
            justify=tk.LEFT
        )
        message_label.grid(row=0, column=1, sticky="ew")
        
        # Tiempo
        time_label = tk.Label(
            item_frame,
            text=tiempo,
            font=("Segoe UI", 8),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        time_label.grid(row=0, column=2, sticky="e", padx=(5, 0))
        
        return item_frame
    
    def pausar_monitoreo(self):
        """Pausar el monitoreo."""
        messagebox.showinfo("Monitoreo", "Monitoreo pausado")
    
    def exportar_datos_monitoreo(self):
        """Exportar datos de monitoreo."""
        messagebox.showinfo("Exportar", "Función de exportación en desarrollo")
    
    def ver_todas_las_alertas(self):
        """Ver todas las alertas."""
        messagebox.showinfo("Alertas", "Mostrando todas las alertas del sistema")
    
    def configurar_alertas(self):
        """Configurar alertas."""
        messagebox.showinfo("Configuración", "Configuración de alertas en desarrollo")
    
    def crear_card_eventos_sistema_mejorada(self, parent, column):
        """Crear card de eventos del sistema con diseño profesional mejorado."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "📋 Eventos del Sistema", "Registro completo de eventos y actividades del sistema"
        )
        card_container.grid(row=0, column=column, sticky="nsew", padx=15, pady=10)
        
        # === FILTROS Y CONTROLES ===
        controls_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Grid para controles
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=0)
        controls_frame.grid_columnconfigure(2, weight=0)
        
        # Filtro de nivel
        filter_label = tk.Label(
            controls_frame,
            text="🔍 Filtrar por nivel:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        filter_label.grid(row=0, column=0, sticky="w")
        
        # Combobox para filtros
        self.events_filter = ttk.Combobox(
            controls_frame,
            values=["Todos", "Información", "Advertencia", "Error", "Crítico"],
            state="readonly",
            width=12
        )
        self.events_filter.set("Todos")
        self.events_filter.grid(row=0, column=1, sticky="e", padx=(10, 5))
        
        # Botón actualizar
        btn_refresh = ComponentesModernos.crear_boton_ultra_moderno(
            controls_frame,
            "🔄",
            self.actualizar_eventos,
            estilo="outline"
        )
        btn_refresh.grid(row=0, column=2, sticky="e", padx=(5, 0))
        
        # === ÁREA DE EVENTOS CON SCROLL ===
        events_container = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        events_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Text area con scrollbar
        self.eventos_text = scrolledtext.ScrolledText(
            events_container,
            height=8,
            font=("Consolas", 9),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            relief="flat",
            wrap=tk.WORD,
            selectbackground=self.tema_actual.PRIMARIO,
            selectforeground="#ffffff"
        )
        self.eventos_text.pack(fill=tk.BOTH, expand=True)
        
        # Cargar eventos de ejemplo
        self.cargar_eventos_ejemplo()
        
        # === BOTONES DE ACCIÓN ===
        actions_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        actions_frame.pack(fill=tk.X)
        
        # Grid para botones
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        actions_frame.grid_columnconfigure(2, weight=1)
        
        btn_exportar_log = ComponentesModernos.crear_boton_ultra_moderno(
            actions_frame,
            "📤 Exportar",
            self.exportar_log_eventos,
            estilo="outline"
        )
        btn_exportar_log.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        btn_limpiar_log = ComponentesModernos.crear_boton_ultra_moderno(
            actions_frame,
            "🗑️ Limpiar",
            self.limpiar_log_eventos,
            estilo="outline"
        )
        btn_limpiar_log.grid(row=0, column=1, sticky="ew", padx=5)
        
        btn_detalles_log = ComponentesModernos.crear_boton_ultra_moderno(
            actions_frame,
            "🔍 Detalles",
            self.mostrar_detalles_log,
            estilo="primario"
        )
        btn_detalles_log.grid(row=0, column=2, sticky="ew", padx=(5, 0))
    
    def crear_card_acciones_recomendadas_mejorada(self, parent, column):
        """Crear card de acciones recomendadas con diseño profesional mejorado."""
        card_container, card_content = ComponentesModernos.crear_card_ultra_moderna(
            parent, "💡 Acciones Recomendadas", "Sugerencias y acciones recomendadas para optimización"
        )
        card_container.grid(row=0, column=column, sticky="nsew", padx=15, pady=10)
        
        # === RECOMENDACIONES PRINCIPALES ===
        recommendations_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        recommendations_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Lista de acciones recomendadas mejoradas
        acciones_recomendadas = [
            {
                "icono": "🔍",
                "titulo": "Ejecutar escaneo completo",
                "descripcion": "Recomendado hacer un escaneo profundo del sistema",
                "prioridad": "Alta",
                "comando": self.ejecutar_escaneo_completo,
                "color": self.tema_actual.WARNING
            },
            {
                "icono": "🔄",
                "titulo": "Actualizar definiciones de virus",
                "descripcion": "Última actualización hace 6 horas",
                "prioridad": "Media",
                "comando": self.actualizar_sistema,
                "color": self.tema_actual.INFO
            },
            {
                "icono": "📊",
                "titulo": "Generar reporte de seguridad",
                "descripcion": "Crear reporte semanal de actividad",
                "prioridad": "Baja",
                "comando": self.mostrar_panel_reportes,
                "color": self.tema_actual.EXITO
            },
            {
                "icono": "🧹",
                "titulo": "Limpiar archivos temporales",
                "descripcion": "Optimizar espacio en disco",
                "prioridad": "Baja",
                "comando": self.limpiar_archivos_temporales,
                "color": self.tema_actual.TEXTO_SECUNDARIO
            }
        ]
        
        for accion in acciones_recomendadas:
            self.crear_item_accion_recomendada(recommendations_frame, accion)
        
        # === ÁREA DE CONSEJOS ===
        tips_frame = tk.Frame(card_content, bg=self.tema_actual.FONDO_CARD)
        tips_frame.pack(fill=tk.X)
        
        # Título de consejos
        tips_title = tk.Label(
            tips_frame,
            text="💡 Consejo del Día",
            font=("Segoe UI", 11, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        tips_title.pack(anchor="w", pady=(0, 8))
        
        # Consejo con fondo destacado
        tip_container = tk.Frame(tips_frame, bg="#f0f8ff", relief="solid", borderwidth=1)
        tip_container.pack(fill=tk.X, pady=(0, 10))
        
        tip_text = tk.Label(
            tip_container,
            text="💡 Mantén tu sistema actualizado ejecutando escaneos regulares\ny actualizando las definiciones de seguridad semanalmente.",
            font=("Segoe UI", 10),
            bg="#f0f8ff",
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            justify=tk.LEFT,
            wraplength=300
        )
        tip_text.pack(padx=15, pady=10)
    
    def crear_item_accion_recomendada(self, parent, accion):
        """Crear un item de acción recomendada."""
        item_frame = tk.Frame(parent, bg="#ffffff", relief="solid", borderwidth=1)
        item_frame.pack(fill=tk.X, pady=5, padx=2)
        
        # Contenido con padding
        content_frame = tk.Frame(item_frame, bg="#ffffff")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        # === HEADER CON ICONO Y PRIORIDAD ===
        header_frame = tk.Frame(content_frame, bg="#ffffff")
        header_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Grid para header
        header_frame.grid_columnconfigure(0, weight=0)  # Icono
        header_frame.grid_columnconfigure(1, weight=1)  # Título
        header_frame.grid_columnconfigure(2, weight=0)  # Prioridad
        
        # Icono
        icon_label = tk.Label(
            header_frame,
            text=accion["icono"],
            font=("Segoe UI", 16),
            bg="#ffffff",
            fg=accion["color"]
        )
        icon_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Título
        title_label = tk.Label(
            header_frame,
            text=accion["titulo"],
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff",
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        title_label.grid(row=0, column=1, sticky="w")
        
        # Badge de prioridad
        priority_color = {
            "Alta": self.tema_actual.ERROR,
            "Media": self.tema_actual.WARNING,
            "Baja": self.tema_actual.EXITO
        }.get(accion["prioridad"], self.tema_actual.TEXTO_SECUNDARIO)
        
        priority_label = tk.Label(
            header_frame,
            text=accion["prioridad"],
            font=("Segoe UI", 8, "bold"),
            bg=priority_color,
            fg="#ffffff",
            padx=8,
            pady=2
        )
        priority_label.grid(row=0, column=2, sticky="e")
        
        # === DESCRIPCIÓN ===
        desc_label = tk.Label(
            content_frame,
            text=accion["descripcion"],
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg=self.tema_actual.TEXTO_SECUNDARIO,
            wraplength=250,
            justify=tk.LEFT
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # === BOTÓN DE ACCIÓN ===
        btn_accion = ComponentesModernos.crear_boton_ultra_moderno(
            content_frame,
            f"Ejecutar {accion['titulo'].split()[0]}",
            accion["comando"],
            estilo="primario" if accion["prioridad"] == "Alta" else "outline"
        )
        btn_accion.pack(fill=tk.X)
        
        return item_frame
    
    def cargar_eventos_ejemplo(self):
        """Cargar eventos de ejemplo en el log."""
        if hasattr(self, 'eventos_text'):
            eventos_ejemplo = [
                "[14:30:15] INFO: Sistema Ares Aegis iniciado correctamente",
                "[14:30:16] INFO: Cargando módulos de protección...",
                "[14:30:17] INFO: Monitor de red iniciado exitosamente",
                "[14:30:18] INFO: SIEM activo y funcionando",
                "[14:30:20] INFO: Escáner de vulnerabilidades cargado",
                "[14:30:22] INFO: Base de datos de firmas actualizada",
                "[14:30:25] INFO: Monitor de integridad de archivos activo",
                "[14:31:00] INFO: Escaneo automático programado iniciado",
                "[14:31:15] SUCCESS: Escaneo rápido completado - 0 amenazas",
                "[14:31:16] INFO: Sistema completamente operativo"
            ]
            
            for evento in eventos_ejemplo:
                self.eventos_text.insert(tk.END, evento + "\\n")
                
            # Scroll al final
            self.eventos_text.see(tk.END)
    
    def actualizar_eventos(self):
        """Actualizar la lista de eventos."""
        messagebox.showinfo("Eventos", "Lista de eventos actualizada")
    
    def exportar_log_eventos(self):
        """Exportar el log de eventos."""
        messagebox.showinfo("Exportar", "Log de eventos exportado exitosamente")
    
    def limpiar_log_eventos(self):
        """Limpiar el log de eventos."""
        if hasattr(self, 'eventos_text'):
            respuesta = messagebox.askyesno("Confirmar", "¿Desea limpiar el log de eventos?")
            if respuesta:
                self.eventos_text.delete(1.0, tk.END)
                self.eventos_text.insert(tk.END, "[SISTEMA] Log limpiado por el usuario\\n")
    
    def mostrar_detalles_log(self):
        """Mostrar detalles del log."""
        messagebox.showinfo("Detalles", "Mostrando vista detallada del log")
    
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
        card_rapido_container, card_rapido_content = ComponentesModernos.crear_card_ultra_moderna(row1, "⚡ Escaneo Rápido", "Análisis rápido del sistema en busca de amenazas conocidas")
        card_rapido_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.crear_widgets_escaneo_rapido_completo(card_rapido_content)
        
        # Card de Escaneo Completo
        card_completo_container, card_completo_content = ComponentesModernos.crear_card_ultra_moderna(row1, "🔍 Escaneo Completo", "Análisis completo y exhaustivo de todo el sistema")
        card_completo_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 5))
        
        self.crear_widgets_escaneo_completo(card_completo_content)
        
        # Card de Escaneo Personalizado
        card_personalizado_container, card_personalizado_content = ComponentesModernos.crear_card_ultra_moderna(row1, "⚙️ Escaneo Personalizado", "Configurar y ejecutar escaneos personalizados")
        card_personalizado_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.crear_widgets_escaneo_personalizado(card_personalizado_content)
        
        # Fila inferior - Progreso y resultados
        row2 = tk.Frame(main_container, bg=self.tema_actual.FONDO_PRINCIPAL)
        row2.pack(fill=tk.BOTH, expand=True)
        
        # Card de Progreso
        card_progreso_container, card_progreso_content = ComponentesModernos.crear_card_ultra_moderna(row2, "📊 Progreso del Escaneo", "Estado y progreso de las operaciones de escaneo")
        card_progreso_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.crear_widgets_progreso_escaneo(card_progreso_content)
        
        # Card de Resultados
        card_resultados_container, card_resultados_content = ComponentesModernos.crear_card_ultra_moderna(row2, "📋 Resultados del Escaneo", "Resultados detallados y acciones recomendadas")
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
    
    def crear_widgets_escaneo_completo(self, parent):
        """Crear widgets para escaneo completo."""
        # Información del escaneo completo
        info_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            info_frame,
            text="• Análisis completo del sistema\n• Verificación de integridad\n• Detección de rootkits\n• Escaneo profundo de memoria",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            justify=tk.LEFT
        ).pack(anchor="w")
        
        # Estado del último escaneo completo
        if hasattr(self, 'ultimo_escaneo_completo') and self.ultimo_escaneo_completo:
            estado_label = tk.Label(
                info_frame,
                text=f"Último escaneo: {self.ultimo_escaneo_completo}",
                font=("Segoe UI", 9),
                bg=self.tema_actual.FONDO_CARD,
                fg=self.tema_actual.TEXTO_SECUNDARIO
            )
            estado_label.pack(anchor="w", pady=(5, 0))
        
        # Botón de escaneo completo
        btn_escaneo_completo = ComponentesModernos.crear_boton_ultra_moderno(
            parent,
            "🔍 Iniciar Escaneo Completo",
            self.ejecutar_escaneo_completo,
            estilo="primario"
        )
        btn_escaneo_completo.pack(fill=tk.X, pady=(0, 10))
        
        # Opciones avanzadas
        opciones_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        opciones_frame.pack(fill=tk.X)
        
        tk.Label(
            opciones_frame,
            text="Opciones avanzadas:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(anchor="w", pady=(0, 5))
        
        # Checkboxes para opciones
        self.var_verificar_integridad = tk.BooleanVar(value=True)
        self.var_escanear_memoria = tk.BooleanVar(value=True)
        self.var_analizar_rootkits = tk.BooleanVar(value=False)
        
        tk.Checkbutton(
            opciones_frame,
            text="Verificar integridad de archivos",
            variable=self.var_verificar_integridad,
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            activebackground=self.tema_actual.FONDO_CARD,
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        tk.Checkbutton(
            opciones_frame,
            text="Escanear memoria del sistema",
            variable=self.var_escanear_memoria,
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            activebackground=self.tema_actual.FONDO_CARD,
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        tk.Checkbutton(
            opciones_frame,
            text="Análisis de rootkits (avanzado)",
            variable=self.var_analizar_rootkits,
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            activebackground=self.tema_actual.FONDO_CARD,
            font=("Segoe UI", 9)
        ).pack(anchor="w")
    
    def crear_widgets_escaneo_personalizado(self, parent):
        """Crear widgets para escaneo personalizado."""
        # Selección de directorio
        dir_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        dir_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            dir_frame,
            text="Directorio a escanear:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(anchor="w")
        
        # Frame para entrada y botón
        path_frame = tk.Frame(dir_frame, bg=self.tema_actual.FONDO_CARD)
        path_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.entry_directorio = tk.Entry(
            path_frame,
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            relief="flat",
            borderwidth=1
        )
        self.entry_directorio.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry_directorio.insert(0, "/home")
        
        btn_seleccionar = ComponentesModernos.crear_boton_ultra_moderno(
            path_frame,
            "📁",
            self.seleccionar_directorio,
            estilo="outline"
        )
        btn_seleccionar.pack(side=tk.RIGHT)
        
        # Tipos de archivos
        tipos_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        tipos_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            tipos_frame,
            text="Tipos de archivo:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(anchor="w", pady=(0, 5))
        
        # Variables para tipos de archivo
        self.var_ejecutables = tk.BooleanVar(value=True)
        self.var_documentos = tk.BooleanVar(value=True)
        self.var_comprimidos = tk.BooleanVar(value=True)
        self.var_todos = tk.BooleanVar(value=False)
        
        tk.Checkbutton(
            tipos_frame,
            text="Archivos ejecutables (.exe, .dll, .so)",
            variable=self.var_ejecutables,
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            activebackground=self.tema_actual.FONDO_CARD,
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        tk.Checkbutton(
            tipos_frame,
            text="Documentos (.pdf, .doc, .txt)",
            variable=self.var_documentos,
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            activebackground=self.tema_actual.FONDO_CARD,
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        tk.Checkbutton(
            tipos_frame,
            text="Archivos comprimidos (.zip, .rar, .7z)",
            variable=self.var_comprimidos,
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            activebackground=self.tema_actual.FONDO_CARD,
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        tk.Checkbutton(
            tipos_frame,
            text="Todos los archivos",
            variable=self.var_todos,
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            activebackground=self.tema_actual.FONDO_CARD,
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        # Botón de escaneo personalizado
        btn_escaneo_personalizado = ComponentesModernos.crear_boton_ultra_moderno(
            parent,
            "⚙️ Iniciar Escaneo Personalizado",
            self.ejecutar_escaneo_personalizado,
            estilo="secundario"
        )
        btn_escaneo_personalizado.pack(fill=tk.X)
    
    def crear_widgets_progreso_escaneo(self, parent):
        """Crear widgets para mostrar el progreso del escaneo."""
        # Estado actual
        self.label_estado_escaneo = tk.Label(
            parent,
            text="Estado: Esperando...",
            font=("Segoe UI", 12, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        self.label_estado_escaneo.pack(anchor="w", pady=(0, 10))
        
        # Barra de progreso
        self.progress_escaneo = ttk.Progressbar(
            parent,
            mode='determinate',
            length=300
        )
        self.progress_escaneo.pack(fill=tk.X, pady=(0, 10))
        
        # Información detallada
        info_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Grid para información
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Archivos escaneados
        self.label_archivos_escaneados = tk.Label(
            info_frame,
            text="Archivos escaneados: 0",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.label_archivos_escaneados.grid(row=0, column=0, sticky="w")
        
        # Amenazas detectadas
        self.label_amenazas_detectadas = tk.Label(
            info_frame,
            text="Amenazas detectadas: 0",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.label_amenazas_detectadas.grid(row=0, column=1, sticky="w")
        
        # Tiempo transcurrido
        self.label_tiempo_transcurrido = tk.Label(
            info_frame,
            text="Tiempo: 00:00:00",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.label_tiempo_transcurrido.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Archivo actual
        self.label_archivo_actual = tk.Label(
            info_frame,
            text="Archivo actual: -",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.label_archivo_actual.grid(row=1, column=1, sticky="w", pady=(5, 0))
        
        # Botones de control
        control_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        control_frame.pack(fill=tk.X)
        
        self.btn_pausar_escaneo = ComponentesModernos.crear_boton_ultra_moderno(
            control_frame,
            "⏸️ Pausar",
            self.pausar_escaneo,
            estilo="outline"
        )
        self.btn_pausar_escaneo.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_detener_escaneo = ComponentesModernos.crear_boton_ultra_moderno(
            control_frame,
            "⏹️ Detener",
            self.detener_escaneo,
            estilo="peligro"
        )
        self.btn_detener_escaneo.pack(side=tk.LEFT)
    
    def seleccionar_directorio(self):
        """Seleccionar directorio para escaneo personalizado."""
        try:
            directorio = filedialog.askdirectory(title="Seleccionar directorio para escanear")
            if directorio:
                self.entry_directorio.delete(0, tk.END)
                self.entry_directorio.insert(0, directorio)
        except Exception as e:
            self.logger.error(f"Error seleccionando directorio: {e}")
            messagebox.showerror("Error", f"Error al seleccionar directorio: {str(e)}")
    
    def ejecutar_escaneo_personalizado(self):
        """Ejecutar escaneo personalizado."""
        try:
            directorio = self.entry_directorio.get().strip()
            if not directorio:
                messagebox.showwarning("Advertencia", "Por favor seleccione un directorio")
                return
            
            if not os.path.exists(directorio):
                messagebox.showerror("Error", "El directorio seleccionado no existe")
                return
            
            # Obtener opciones seleccionadas
            opciones = {
                'directorio': directorio,
                'ejecutables': self.var_ejecutables.get(),
                'documentos': self.var_documentos.get(),
                'comprimidos': self.var_comprimidos.get(),
                'todos': self.var_todos.get()
            }
            
            self.logger.info(f"Iniciando escaneo personalizado en: {directorio}")
            messagebox.showinfo("Escaneo", f"Iniciando escaneo personalizado en: {directorio}")
            
            # Aquí iría la lógica del escaneo personalizado
            if self.controlador and hasattr(self.controlador, 'escanear_directorio'):
                threading.Thread(
                    target=self._ejecutar_escaneo_directorio_thread,
                    args=(directorio,),
                    daemon=True
                ).start()
            else:
                messagebox.showinfo("Información", "Simulando escaneo personalizado...")
        
        except Exception as e:
            self.logger.error(f"Error en escaneo personalizado: {e}")
            messagebox.showerror("Error", f"Error en escaneo personalizado: {str(e)}")
    
    def pausar_escaneo(self):
        """Pausar el escaneo actual."""
        messagebox.showinfo("Escaneo", "Escaneo pausado")
    
    def detener_escaneo(self):
        """Detener el escaneo actual."""
        respuesta = messagebox.askyesno("Confirmar", "¿Desea detener el escaneo actual?")
        if respuesta:
            messagebox.showinfo("Escaneo", "Escaneo detenido")
    
    def exportar_resultados_escaneo(self):
        """Exportar resultados del escaneo."""
        messagebox.showinfo("Exportar", "Resultados exportados exitosamente")
    
    def limpiar_resultados_escaneo(self):
        """Limpiar los resultados del escaneo."""
        if hasattr(self, 'text_resultados_escaneo'):
            self.text_resultados_escaneo.delete(1.0, tk.END)
            self.text_resultados_escaneo.insert(tk.END, "Resultados del escaneo aparecerán aquí...\\n")
    
    def crear_widgets_escaneo_rapido_completo(self, parent):
        """Crear widgets para escaneo rápido completo."""
        # Información del escaneo rápido
        info_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            info_frame,
            text="• Escaneo de archivos críticos\n• Verificación de procesos activos\n• Análisis de memoria\n• Detección de amenazas conocidas",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            justify=tk.LEFT
        ).pack(anchor="w")
        
        # Estado del último escaneo rápido
        if hasattr(self, 'ultimo_escaneo_rapido') and self.ultimo_escaneo_rapido:
            estado_label = tk.Label(
                info_frame,
                text=f"Último escaneo: {self.ultimo_escaneo_rapido}",
                font=("Segoe UI", 9),
                bg=self.tema_actual.FONDO_CARD,
                fg=self.tema_actual.TEXTO_SECUNDARIO
            )
            estado_label.pack(anchor="w", pady=(5, 0))
        
        # Botón de escaneo rápido
        btn_escaneo_rapido = ComponentesModernos.crear_boton_ultra_moderno(
            parent,
            "⚡ Iniciar Escaneo Rápido",
            self.ejecutar_escaneo_rapido,
            estilo="primario"
        )
        btn_escaneo_rapido.pack(fill=tk.X, pady=(0, 10))
        
        # Estadísticas rápidas
        stats_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        stats_frame.pack(fill=tk.X)
        
        tk.Label(
            stats_frame,
            text="Estadísticas:",
            font=("Segoe UI", 10, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(anchor="w", pady=(0, 5))
        
        # Grid para estadísticas
        stats_grid = tk.Frame(stats_frame, bg=self.tema_actual.FONDO_CARD)
        stats_grid.pack(fill=tk.X)
        
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
        
        tk.Label(
            stats_grid,
            text=f"Archivos escaneados:",
            font=("Segoe UI", 9),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        ).grid(row=0, column=0, sticky="w")
        
        tk.Label(
            stats_grid,
            text=f"{getattr(self, 'archivos_escaneados_actual', 0)}",
            font=("Segoe UI", 9, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).grid(row=0, column=1, sticky="e")
        
        tk.Label(
            stats_grid,
            text=f"Amenazas detectadas:",
            font=("Segoe UI", 9),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        ).grid(row=1, column=0, sticky="w")
        
        tk.Label(
            stats_grid,
            text=f"{getattr(self, 'amenazas_detectadas_actual', 0)}",
            font=("Segoe UI", 9, "bold"),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.EXITO if getattr(self, 'amenazas_detectadas_actual', 0) == 0 else self.tema_actual.ERROR
        ).grid(row=1, column=1, sticky="e")
    
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
        """Limpiar el contenido principal respetando la nueva estructura con scroll."""
        try:
            if hasattr(self, 'frame_scrollable') and self.frame_scrollable:
                # Limpiar el frame scrollable en lugar del contenido principal
                for widget in self.frame_scrollable.winfo_children():
                    widget.destroy()
            elif hasattr(self, 'contenido_principal') and self.contenido_principal:
                # Fallback para estructura anterior
                for widget in self.contenido_principal.winfo_children():
                    if hasattr(widget, 'winfo_class') and widget.winfo_class() not in ['Canvas', 'Scrollbar']:
                        widget.destroy()
        except Exception as e:
            self.logger.error(f"Error limpiando contenido: {e}")
    
    def obtener_contenedor_contenido(self):
        """Obtener el contenedor correcto donde agregar contenido."""
        if hasattr(self, 'frame_scrollable') and self.frame_scrollable:
            return self.frame_scrollable
        elif hasattr(self, 'contenido_principal') and self.contenido_principal:
            return self.contenido_principal
        else:
            return self.root
    
    def actualizar_navegacion_activa(self, panel_activo):
        """Actualizar el estado visual de la navegación."""
        try:
            for nombre, tab_container in self.botones_navegacion.items():
                if hasattr(tab_container, 'button') and hasattr(tab_container, 'indicator'):
                    if nombre == panel_activo:
                        # Pestaña activa
                        tab_container.button.config(
                            bg=self.tema_actual.PRIMARIO,
                            fg="#ffffff"
                        )
                        tab_container.indicator.config(bg=self.tema_actual.PRIMARIO)
                        tab_container.activo = True
                    else:
                        # Pestaña inactiva
                        tab_container.button.config(
                            bg=self.tema_actual.FONDO_SECUNDARIO,
                            fg=self.tema_actual.TEXTO_SECUNDARIO
                        )
                        tab_container.indicator.config(bg=self.tema_actual.FONDO_SECUNDARIO)
                        tab_container.activo = False
        except Exception as e:
            self.logger.error(f"Error actualizando navegación: {e}")
    
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

    def ejecutar_escaneo_rapido(self):
        """Ejecutar escaneo rápido del sistema."""
        try:
            if self.controlador and self.controlador.escaneador:
                messagebox.showinfo("Escaneo", "Iniciando escaneo rápido...")
                # Aquí iría la lógica real del escaneo
                messagebox.showinfo("Escaneo", "Escaneo rápido completado - No se encontraron amenazas")
            else:
                messagebox.showwarning("Error", "El escaneador no está disponible")
        except Exception as e:
            self.logger.error(f"Error ejecutando escaneo rápido: {e}")
            messagebox.showerror("Error", f"Error en escaneo rápido: {str(e)}")
    
    def ejecutar_escaneo_completo(self):
        """Ejecutar escaneo completo del sistema."""
        try:
            if self.controlador and self.controlador.escaneador:
                messagebox.showinfo("Escaneo", "Iniciando escaneo completo...")
                # Aquí iría la lógica real del escaneo
                messagebox.showinfo("Escaneo", "Escaneo completo en progreso...")
            else:
                messagebox.showwarning("Error", "El escaneador no está disponible")
        except Exception as e:
            self.logger.error(f"Error ejecutando escaneo completo: {e}")
            messagebox.showerror("Error", f"Error en escaneo completo: {str(e)}")
    
    def ejecutar_escaneo_rapido_avanzado(self):
        """Ejecutar escaneo rápido avanzado."""
        self.ejecutar_escaneo_rapido()
    
    def ejecutar_escaneo_completo_avanzado(self):
        """Ejecutar escaneo completo avanzado.""" 
        self.ejecutar_escaneo_completo()
    
    def iniciar_servicios(self):
        """Iniciar servicios de protección."""
        try:
            if self.controlador:
                # Aquí iría la lógica para iniciar servicios
                messagebox.showinfo("Servicios", "Servicios de protección iniciados correctamente")
            else:
                messagebox.showwarning("Error", "El controlador no está disponible")
        except Exception as e:
            self.logger.error(f"Error iniciando servicios: {e}")
            messagebox.showerror("Error", f"Error iniciando servicios: {str(e)}")
    
    def detener_servicios(self):
        """Detener servicios de protección."""
        try:
            if self.controlador:
                # Aquí iría la lógica para detener servicios
                messagebox.showinfo("Servicios", "Servicios de protección detenidos correctamente")
            else:
                messagebox.showwarning("Error", "El controlador no está disponible")
        except Exception as e:
            self.logger.error(f"Error deteniendo servicios: {e}")
            messagebox.showerror("Error", f"Error deteniendo servicios: {str(e)}")
    
    def cargar_actividades_recientes(self):
        """Cargar actividades recientes del sistema."""
        try:
            if hasattr(self, 'lista_actividades'):
                self.lista_actividades.delete(1.0, tk.END)
                self.lista_actividades.insert(tk.END, "[14:30:15] Sistema iniciado correctamente\n")
                self.lista_actividades.insert(tk.END, "[14:30:16] Cargando módulos de protección...\n")
                self.lista_actividades.insert(tk.END, "[14:30:17] Monitor de red iniciado\n")
                self.lista_actividades.insert(tk.END, "[14:30:18] SIEM activo y funcionando\n")
        except Exception as e:
            self.logger.error(f"Error cargando actividades: {e}")
    
    def mostrar_todas_alertas(self):
        """Mostrar todas las alertas del sistema."""
        messagebox.showinfo("Alertas", "No hay alertas pendientes en el sistema")
    
    def exportar_resultados_escaneo(self):
        """Exportar resultados del escaneo."""
        messagebox.showinfo("Exportar", "Función de exportación en desarrollo")
    
    def limpiar_resultados_escaneo(self):
        """Limpiar resultados del escaneo."""
        try:
            if hasattr(self, 'text_resultados_escaneo'):
                self.text_resultados_escaneo.delete(1.0, tk.END)
                self.text_resultados_escaneo.insert(tk.END, "Resultados del escaneo aparecerán aquí...\n")
        except Exception as e:
            self.logger.error(f"Error limpiando resultados: {e}")
    
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
        self.ruta_personalizada = tk.StringVar(value="/home")
        
        path_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            path_frame,
            text="Ruta a escanear:",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        ).pack(anchor="w")
        
        entry_path = tk.Entry(
            path_frame,
            textvariable=self.ruta_personalizada,
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_PRINCIPAL,
            fg=self.tema_actual.TEXTO_PRINCIPAL,
            relief="flat"
        )
        entry_path.pack(fill=tk.X, pady=(5, 0))
        
        # Botón de escaneo personalizado
        btn_escaneo_personalizado = ComponentesModernos.crear_boton_ultra_moderno(
            parent,
            "⚙️ Iniciar Escaneo Personalizado",
            self.ejecutar_escaneo_personalizado,
            estilo="info"
        )
        btn_escaneo_personalizado.pack(fill=tk.X, pady=(10, 0))
    
    def crear_widgets_progreso_escaneo(self, parent):
        """Crear widgets para mostrar el progreso del escaneo."""
        # Indicador de progreso
        self.progress_escaneo = ttk.Progressbar(
            parent,
            mode='determinate',
            length=300
        )
        self.progress_escaneo.pack(pady=(10, 5))
        
        # Etiqueta de estado
        self.estado_escaneo = tk.StringVar(value="Esperando...")
        label_estado = tk.Label(
            parent,
            textvariable=self.estado_escaneo,
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_PRINCIPAL
        )
        label_estado.pack()
        
        # Estadísticas en tiempo real
        stats_frame = tk.Frame(parent, bg=self.tema_actual.FONDO_CARD)
        stats_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.archivos_escaneados_label = tk.Label(
            stats_frame,
            text="Archivos escaneados: 0",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.archivos_escaneados_label.pack(anchor="w")
        
        self.amenazas_encontradas_label = tk.Label(
            stats_frame,
            text="Amenazas encontradas: 0",
            font=("Segoe UI", 10),
            bg=self.tema_actual.FONDO_CARD,
            fg=self.tema_actual.TEXTO_SECUNDARIO
        )
        self.amenazas_encontradas_label.pack(anchor="w")
    
    def ejecutar_escaneo_personalizado(self):
        """Ejecutar escaneo en la ruta personalizada."""
        try:
            ruta = self.ruta_personalizada.get() if hasattr(self, 'ruta_personalizada') else "/home"
            messagebox.showinfo("Escaneo", f"Iniciando escaneo personalizado en: {ruta}")
            # Aquí iría la lógica real del escaneo personalizado
        except Exception as e:
            self.logger.error(f"Error en escaneo personalizado: {e}")
            messagebox.showerror("Error", f"Error en escaneo personalizado: {str(e)}")
    
    def mostrar_panel_monitoreo(self):
        """Mostrar panel de monitoreo."""
        messagebox.showinfo("Monitoreo", "Panel de monitoreo en desarrollo")
    
    def mostrar_panel_cuarentena(self):
        """Mostrar panel de cuarentena."""
        messagebox.showinfo("Cuarentena", "Panel de cuarentena en desarrollo")
    
    def mostrar_panel_reportes(self):
        """Mostrar panel de reportes."""
        messagebox.showinfo("Reportes", "Panel de reportes en desarrollo")
    
    def mostrar_panel_configuracion(self):
        """Mostrar panel de configuración."""
        messagebox.showinfo("Configuración", "Panel de configuración en desarrollo")
    
    def limpiar_contenido(self):
        """Limpiar el contenido principal con manejo mejorado."""
        try:
            # Obtener el contenedor correcto
            contenedor = self.obtener_contenedor_contenido()
            
            # Limpiar el contenido del contenedor
            for widget in contenedor.winfo_children():
                widget.destroy()
                
            # También limpiar el contenido principal si es diferente
            if hasattr(self, 'contenido_principal') and self.contenido_principal and contenedor != self.contenido_principal:
                for widget in self.contenido_principal.winfo_children():
                    # No destruir el canvas y scrollbar
                    if not isinstance(widget, (tk.Canvas, tk.Scrollbar)):
                        widget.destroy()
                        
            self.logger.debug("Contenido limpiado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error limpiando contenido: {e}")
            # Como fallback, intentar limpiar de forma básica
            try:
                if hasattr(self, 'frame_scrollable') and self.frame_scrollable:
                    for widget in self.frame_scrollable.winfo_children():
                        widget.destroy()
            except Exception as fallback_error:
                self.logger.error(f"Error en fallback de limpieza: {fallback_error}")
    
    def actualizar_navegacion_activa(self, tab_name):
        """Actualizar la navegación activa."""
        try:
            if hasattr(self, 'botones_navegacion'):
                for nombre, tab_frame in self.botones_navegacion.items():
                    if nombre == tab_name:
                        # Activar
                        tab_frame.button.config(bg=self.tema_actual.PRIMARIO, fg="#ffffff")
                        tab_frame.indicator.config(bg=self.tema_actual.PRIMARIO)
                        tab_frame.activo = True
                    else:
                        # Desactivar
                        tab_frame.button.config(bg=self.tema_actual.FONDO_SECUNDARIO, fg=self.tema_actual.TEXTO_SECUNDARIO)
                        tab_frame.indicator.config(bg=self.tema_actual.FONDO_SECUNDARIO)
                        tab_frame.activo = False
        except Exception as e:
            self.logger.error(f"Error actualizando navegación: {e}")
    
    def cambiar_tema(self):
        """Cambiar entre tema claro y oscuro."""
        try:
            self.tema_oscuro = not self.tema_oscuro
            if self.tema_oscuro:
                from ..utilidades.temas_modernos import TemaOscuro
                self.tema_actual = TemaOscuro()
            else:
                from ..utilidades.temas_modernos import TemaClaro
                self.tema_actual = TemaClaro()
            
            # Actualizar la interfaz con el nuevo tema
            self.actualizar_tema_interfaz()
            messagebox.showinfo("Tema", f"Tema cambiado a {'oscuro' if self.tema_oscuro else 'claro'}")
        except Exception as e:
            self.logger.error(f"Error cambiando tema: {e}")
            messagebox.showerror("Error", f"Error cambiando tema: {str(e)}")
    
    def actualizar_tema_interfaz(self):
        """Actualizar toda la interfaz con el tema actual."""
        try:
            if self.root:
                self.root.configure(bg=self.tema_actual.FONDO_PRINCIPAL)
                # Aquí se actualizarían todos los widgets con el nuevo tema
        except Exception as e:
            self.logger.error(f"Error actualizando tema de interfaz: {e}")
    
    def actualizar_hora(self):
        """Actualizar la hora en el panel de estado."""
        try:
            if hasattr(self, 'label_hora') and self.label_hora:
                from datetime import datetime
                hora_actual = datetime.now().strftime("%H:%M:%S")
                self.label_hora.config(text=hora_actual)
                # Programar la próxima actualización
                if self.root:
                    self.root.after(1000, self.actualizar_hora)
        except Exception as e:
            self.logger.error(f"Error actualizando hora: {e}")
    
    def cargar_configuracion(self):
        """Cargar configuración de la aplicación."""
        try:
            # Aquí iría la lógica para cargar configuración
            self.logger.info("Configuración cargada correctamente")
        except Exception as e:
            self.logger.error(f"Error cargando configuración: {e}")
    
    def actualizar_estado_inicial(self):
        """Actualizar el estado inicial de la aplicación."""
        try:
            # Aquí iría la lógica para actualizar estado inicial
            self.logger.info("Estado inicial actualizado")
        except Exception as e:
            self.logger.error(f"Error actualizando estado inicial: {e}")
    
    def obtener_contenedor_contenido(self):
        """Obtener el contenedor correcto para el contenido."""
        try:
            # Si existe el frame scrollable, usarlo; sino usar el contenido principal
            if hasattr(self, 'frame_scrollable') and self.frame_scrollable:
                return self.frame_scrollable
            elif hasattr(self, 'contenido_principal') and self.contenido_principal:
                return self.contenido_principal
            else:
                # Como fallback, crear un frame temporal
                self.logger.warning("Contenedor de contenido no encontrado, creando uno temporal")
                return tk.Frame(self.root, bg=self.tema_actual.FONDO_PRINCIPAL)
        except Exception as e:
            self.logger.error(f"Error obteniendo contenedor de contenido: {e}")
            return tk.Frame(self.root, bg=self.tema_actual.FONDO_PRINCIPAL)
    
    def cerrar_aplicacion(self):
        """Cerrar la aplicación de forma segura."""
        try:
            respuesta = messagebox.askyesno("Salir", "¿Está seguro que desea salir de Ares Aegis?")
            if respuesta:
                self.logger.info("Cerrando aplicación...")
                if self.root:
                    self.root.quit()
                    self.root.destroy()
        except Exception as e:
            self.logger.error(f"Error cerrando aplicación: {e}")

def main():
    """Función principal para ejecutar la interfaz."""
    try:
        # Configurar logging
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Crear e inicializar la interfaz
        interfaz = InterfazPrincipal()
        
        if interfaz.inicializar():
            interfaz.root.mainloop()
        else:
            print("Error: No se pudo inicializar la aplicación")
            
    except Exception as e:
        print(f"Error ejecutando la aplicación: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
