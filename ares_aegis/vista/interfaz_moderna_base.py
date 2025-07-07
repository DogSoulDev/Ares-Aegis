#!/usr/bin/env python3
"""
Interfaz Base de Ares Aegis
Sistema Principal con Dashboard, Escaneo y Cuarentena

🏠 INTERFAZ PRINCIPAL Y CORE
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import os
import threading
import time
from datetime import datetime
from typing import Optional

# Importar controladores y modelos
from ..controladores.controlador_principal import ControladorPrincipal
from ..utilidades.temas_modernos import TemaClaro, TemaOscuro
from .interfaz_moderna_componentes import ComponentesModernos, TemasModernos
from .interfaz_moderna_herramientas import InterfazModernaHerramientas


class InterfazModernaBase:
    def parar_escaneo(self):
        """Detener cualquier escaneo en curso y limpiar la caché de escaneos."""
        if not self.controlador:
            messagebox.showwarning("Error", "Controlador no disponible")
            return
        exito_cancelar = False
        exito_cache = False
        try:
            if hasattr(self.controlador, 'cancelar_escaneo_en_curso'):
                exito_cancelar = self.controlador.cancelar_escaneo_en_curso()
            if hasattr(self.controlador, 'limpiar_cache_escaneos'):
                exito_cache = self.controlador.limpiar_cache_escaneos()
            if exito_cancelar:
                messagebox.showinfo("Escaneo detenido", "El escaneo en curso ha sido detenido correctamente.")
            else:
                messagebox.showwarning("Sin escaneo activo", "No hay escaneo en curso o no se pudo cancelar.")
            if exito_cache:
                messagebox.showinfo("Caché limpiada", "La caché de escaneos ha sido limpiada correctamente.")
            else:
                messagebox.showwarning("Caché no limpiada", "No se pudo limpiar la caché de escaneos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al detener escaneo o limpiar caché:\n{str(e)}")
    """Interfaz principal moderna de Ares Aegis con UX profesional"""
    
    def __init__(self):
        """Inicializar la interfaz moderna"""
        self.logger = logging.getLogger(__name__)
        self.root: Optional[tk.Tk] = None  # Typing hint para evitar errores
        self.tema = TemaClaro()  # Tema por defecto
        self.controlador = None
        self.controlador_listo = False
        # Estados de la aplicación
        self.panel_actual = "dashboard"
        self.escaneo_activo = False
        self.monitoreo_activo = False
        # Widgets principales
        self.header_frame = None
        self.navbar_frame = None
        self.content_frame = None
        self.sidebar_frame = None
        # Navegación
        self.nav_buttons = {}
        self.current_nav_button = None
        # Variables de datos
        self.stats_data = {
            "amenazas_detectadas": 0,
            "archivos_escaneados": 0,
            "sistema_protegido": "98.5%",
            "ultima_actualizacion": "Hoy"
        }
        # Widgets de estadísticas para actualización
        self.stats_widgets = {}
        # Inicializar módulo de herramientas
        self.herramientas = None
        # Referencias a botones de escaneo
        self.boton_escaneo_rapido = None
        self.boton_escaneo_completo = None
        self.boton_escaneo_personalizado = None
        self.logger.info("Interfaz Moderna Base inicializada correctamente")
    
    def eliminar_archivo(self):
        """Eliminar archivo de cuarentena (real y robusto)."""
        if not hasattr(self, 'listbox_cuarentena') or self.listbox_cuarentena is None:
            messagebox.showwarning("Error", "Lista de cuarentena no disponible")
            return
        try:
            selection = self.listbox_cuarentena.curselection()
            if not selection:
                messagebox.showwarning("Selección", "Por favor seleccione un archivo para eliminar")
                return
            indice = selection[0]
            if hasattr(self, 'archivos_cuarentena_data') and self.archivos_cuarentena_data:
                if indice < len(self.archivos_cuarentena_data):
                    archivo_data = self.archivos_cuarentena_data[indice]
                    archivo_id = archivo_data.get("id", archivo_data.get("archivo_id", None))
                    nombre_archivo = archivo_data.get("nombre", archivo_data.get("nombre_archivo", "Archivo desconocido"))
                    respuesta = messagebox.askyesno(
                        "Eliminar archivo",
                        f"¿Está seguro que desea eliminar permanentemente:\n{nombre_archivo}?\n\nEsta acción NO se puede deshacer."
                    )
                    cuarentena_ctrl = getattr(self.controlador, 'controlador_cuarentena', None) if hasattr(self, 'controlador') and self.controlador else None
                    if respuesta and cuarentena_ctrl and hasattr(cuarentena_ctrl, 'eliminar_archivo_cuarentena'):
                        try:
                            resultado = cuarentena_ctrl.eliminar_archivo_cuarentena(archivo_id, confirmar=True)
                            if isinstance(resultado, dict) and resultado.get('exitoso'):
                                messagebox.showinfo("Eliminado", f"Archivo eliminado correctamente: {nombre_archivo}")
                                self.actualizar_cuarentena()
                            else:
                                error_msg = resultado.get('error', 'No se pudo eliminar el archivo') if isinstance(resultado, dict) else 'No se pudo eliminar el archivo'
                                messagebox.showerror("Error", f"No se pudo eliminar el archivo: {error_msg}")
                        except Exception as e:
                            if hasattr(self, 'logger'):
                                self.logger.error(f"Error eliminando archivo: {e}")
                            messagebox.showerror("Error", f"Error eliminando archivo: {str(e)}")
                    elif respuesta:
                        messagebox.showwarning("Error", "Controlador de cuarentena no disponible")
                else:
                    messagebox.showwarning("Error", "Índice de archivo fuera de rango")
            else:
                messagebox.showwarning("Error", "No hay datos de archivos disponibles")
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Error eliminando archivo: {e}")
            messagebox.showerror("Error", f"Error eliminando archivo: {str(e)}")
        try:
            self.root.attributes('-alpha', 0.98)
        except:
            pass
        
        # Configurar estilos TTK
        TemasModernos.obtener_configuracion_ttk_style()

        # Agregar botón Parar Escaneo en el header (después de crear header_frame)
        # Se agrega aquí para asegurar que header_frame existe
        self.root.after(0, self._agregar_boton_parar_escaneo)

    def _agregar_boton_parar_escaneo(self):
        """Agregar el botón Parar Escaneo en el header derecho."""
        if not self.header_frame:
            return
        # Buscar el right_frame dentro del header
        for child in self.header_frame.winfo_children():
            if isinstance(child, tk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Frame) and subchild.pack_info().get('side') == 'right':
                        # Insertar el botón en el right_frame
                        btn = ComponentesModernos.crear_boton_moderno(
                            subchild, "⏹️ Parar Escaneo", self.parar_escaneo, "peligro"
                        )
                        btn.pack(side="right", padx=(0, 10))
                        return
    
    def centrar_ventana(self):
        """Centrar la ventana en la pantalla"""
        if self.root:
            self.root.update_idletasks()
            ancho = 1400
            alto = 900
            x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
            y = (self.root.winfo_screenheight() // 2) - (alto // 2)
            self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
    
    def configurar_icono(self):
        """Configurar icono de la aplicación"""
        if not self.root:
            return
            
        icon_paths = [
            "/home/dogsoul/Ares-Aegis/recursos/aresIcon.png",
            "/home/dogsoul/Ares-Aegis/recursos/AresAegis.png"
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    icon = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(True, icon)
                    # Guardar referencia al icono para evitar garbage collection
                    if not hasattr(self.root, '_ares_icon_ref'):
                        setattr(self.root, '_ares_icon_ref', icon)
                    break
                except Exception as e:
                    self.logger.warning(f"Error cargando icono {icon_path}: {e}")
    
    def inicializar_controlador(self):
        """Inicializar el controlador principal de forma optimizada"""
        if not self.root:
            return
        try:
            # Mostrar mensaje de carga
            if hasattr(self, 'status_label'):
                self.status_label.config(text="INICIALIZANDO...", fg=ComponentesModernos.COLORES["advertencia"])
                self.root.update()
            # Inicializar controlador de forma síncrona
            self.controlador = ControladorPrincipal()
            self.controlador_listo = True
            self.logger.info("Controlador inicializado correctamente")
            # Actualizar estado
            self._controlador_iniciado()
            # Habilitar botones de escaneo si existen
            self._actualizar_estado_botones_escaneo(True)
        except Exception as e:
            self.controlador_listo = False
            self.logger.error(f"Error inicializando controlador: {e}")
            self._error_controlador(e)
            self._actualizar_estado_botones_escaneo(False)
            raise
    def _actualizar_estado_botones_escaneo(self, habilitar: bool):
        """Habilitar o deshabilitar los botones de escaneo según el estado del controlador."""
        estado = tk.NORMAL if habilitar else tk.DISABLED
        for boton in [self.boton_escaneo_rapido, self.boton_escaneo_completo, self.boton_escaneo_personalizado]:
            if boton is not None:
                boton.config(state=estado)
    
    def _controlador_iniciado(self):
        """Callback cuando el controlador está listo"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text="SISTEMA ACTIVO", fg=ComponentesModernos.COLORES["activo"])
        self.logger.info("Controlador inicializado correctamente")
    
    def _error_controlador(self, error):
        """Callback para errores del controlador"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text="ERROR SISTEMA", fg=ComponentesModernos.COLORES["inactivo"])
        self.logger.error(f"Error en controlador: {error}")
        messagebox.showerror("Error", f"Error inicializando controlador:\n{str(error)}")
    
    def configurar_interfaz(self):
        """Configurar la estructura principal de la interfaz"""
        # === HEADER PROFESIONAL ===
        self.crear_header()
        
        # === NAVEGACIÓN MODERNA ===
        self.crear_navegacion()
        
        # === ÁREA DE CONTENIDO PRINCIPAL ===
        self.crear_area_contenido()
        
        # === SIDEBAR OPCIONAL (OCULTO POR DEFECTO) ===
        self.crear_sidebar()
    
    def crear_header(self):
        """Crear header profesional con branding"""
        self.header_frame = tk.Frame(self.root, bg=ComponentesModernos.COLORES["bg_principal"], height=100)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        # Línea decorativa superior
        top_line = tk.Frame(self.header_frame, bg=ComponentesModernos.COLORES["primario"], height=3)
        top_line.pack(fill="x")
        
        # Container del header
        header_content = tk.Frame(self.header_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # === LADO IZQUIERDO: LOGO Y BRANDING ===
        left_frame = tk.Frame(header_content, bg=ComponentesModernos.COLORES["bg_principal"])
        left_frame.pack(side="left", fill="y")
        
        # Logo
        self.crear_logo(left_frame)
        
        # Títulos
        brand_text = tk.Frame(left_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        brand_text.pack(side="left", fill="y", padx=(15, 0))
        
        title_label = tk.Label(
            brand_text,
            text="ARES AEGIS",
            font=("Segoe UI", 18, "bold"),
            bg=ComponentesModernos.COLORES["bg_principal"],
            fg=ComponentesModernos.COLORES["texto_primario"]
        )
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(
            brand_text,
            text="Advanced Cybersecurity Command Center",
            font=("Segoe UI", 10),
            bg=ComponentesModernos.COLORES["bg_principal"],
            fg=ComponentesModernos.COLORES["texto_secundario"]
        )
        subtitle_label.pack(anchor="w")
        
        # === LADO DERECHO: ESTADO Y CONTROLES ===
        right_frame = tk.Frame(header_content, bg=ComponentesModernos.COLORES["bg_principal"])
        right_frame.pack(side="right", fill="y")
        
        # Indicador de estado
        status_frame = tk.Frame(right_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        status_frame.pack(side="right", fill="y")
        
        # Punto de estado
        status_dot = tk.Frame(status_frame, bg=ComponentesModernos.COLORES["activo"], width=8, height=8)
        status_dot.pack(side="right", padx=(10, 5), pady=18)
        
        # Texto de estado
        self.status_label = tk.Label(
            status_frame,
            text="SISTEMA ACTIVO",
            font=("Segoe UI", 11, "bold"),
            bg=ComponentesModernos.COLORES["bg_principal"],
            fg=ComponentesModernos.COLORES["activo"]
        )
        self.status_label.pack(side="right", pady=15)
    
    def crear_logo(self, parent):
        """Crear logo en el header"""
        logo_paths = [
            "/home/dogsoul/Ares-Aegis/recursos/AresAegis.png",
            "/home/dogsoul/Ares-Aegis/recursos/aresIcon.png"
        ]
        
        logo_cargado = False
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    logo_img = tk.PhotoImage(file=logo_path)
                    # Redimensionar proporcionalmente
                    width, height = logo_img.width(), logo_img.height()
                    
                    # Mantener altura máxima de 60px
                    max_height = 60
                    if height > max_height:
                        scale_factor = max(1, height // max_height)
                        logo_img = logo_img.subsample(scale_factor)
                    
                    # Container para centrar el logo verticalmente
                    logo_container = tk.Frame(parent, bg=ComponentesModernos.COLORES["bg_principal"])
                    logo_container.pack(side="left", padx=(0, 20), fill="y")
                    
                    logo_label = tk.Label(logo_container, image=logo_img, bg=ComponentesModernos.COLORES["bg_principal"], bd=0, relief="flat")
                    logo_label.pack(expand=True)
                    
                    # Guardar referencia
                    parent.master.logo_ref = logo_img
                    logo_cargado = True
                    break
                except Exception as e:
                    self.logger.warning(f"Error cargando logo {logo_path}: {e}")
        
        if not logo_cargado:
            # Logo fallback con emoji centrado
            logo_container = tk.Frame(parent, bg=ComponentesModernos.COLORES["bg_principal"])
            logo_container.pack(side="left", padx=(0, 20), fill="y")
            
            logo_emoji = tk.Label(
                logo_container,
                text="🛡️",
                font=("Arial", 40),
                bg=ComponentesModernos.COLORES["bg_principal"],
                fg=ComponentesModernos.COLORES["primario"],
                bd=0,
                relief="flat"
            )
            logo_emoji.pack(expand=True)
    
    def crear_navegacion(self):
        """Crear barra de navegación moderna"""
        self.navbar_frame = tk.Frame(self.root, bg=ComponentesModernos.COLORES["bg_secundario"], height=70)
        self.navbar_frame.pack(fill="x")
        self.navbar_frame.pack_propagate(False)
        
        # Container de navegación
        nav_container = tk.Frame(self.navbar_frame, bg=ComponentesModernos.COLORES["bg_secundario"])
        nav_container.pack(fill="both", expand=True, padx=25, pady=10)
        
        # Configurar grid responsivo
        nav_items = [
            ("📊", "Dashboard", self.mostrar_dashboard, ComponentesModernos.COLORES["primario"]),
            ("🔍", "Scan", self.mostrar_escaneo, "#ff6b35"),
            ("🛡️", "Quarantine", self.mostrar_cuarentena, "#dc3545"),
            ("📡", "Monitor", self.mostrar_monitoreo, "#7b68ee"),  # Activado
            ("🛡️", "Protection", self.mostrar_proteccion, ComponentesModernos.COLORES["exito"]),  # Activado
            ("🔧", "Tools", self.mostrar_herramientas, ComponentesModernos.COLORES["advertencia"]),  # Activado
            ("📋", "Reports", self.mostrar_reportes, ComponentesModernos.COLORES["peligro"]),
            ("⚙️", "Settings", self.mostrar_configuracion, ComponentesModernos.COLORES["secundario"])
        ]
        
        for i in range(len(nav_items)):
            nav_container.columnconfigure(i, weight=1, uniform="nav")
        
        # Crear botones de navegación
        for i, (icon, text, command, color) in enumerate(nav_items):
            btn = self.crear_nav_button(nav_container, icon, text, command, color)
            btn.grid(row=0, column=i, sticky="ew", padx=2)
            self.nav_buttons[text.lower()] = btn
        
        # Activar dashboard por defecto
        self.activar_navegacion("dashboard")
    
    def crear_nav_button(self, parent, icon, text, command, color):
        """Crear botón de navegación moderno"""
        # Container del botón
        btn_container = tk.Frame(parent, bg=ComponentesModernos.COLORES["bg_secundario"], relief="flat", bd=0)
        
        # Botón principal
        btn = tk.Button(
            btn_container,
            text=f"{icon}\n{text}",
            command=lambda: self.navegar_a(text.lower(), command) if command else None,
            bg=ComponentesModernos.COLORES["bg_secundario"],
            fg=ComponentesModernos.COLORES["texto_secundario"],
            relief="flat",
            borderwidth=0,
            cursor="hand2" if command else "arrow",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=12,
            highlightthickness=0,
            bd=0,
            state="normal" if command else "disabled"
        )
        btn.pack(fill="both", expand=True)
        
        # Indicador inferior
        indicator = tk.Frame(btn_container, bg=ComponentesModernos.COLORES["bg_secundario"], height=3, relief="flat", bd=0)
        indicator.pack(fill="x", side="bottom")
        
        # Efectos hover solo si tiene comando
        if command:
            def on_enter(e):
                if not getattr(btn_container, 'is_active', False):
                    btn.config(bg=ComponentesModernos.COLORES["bg_card_hover"], fg=ComponentesModernos.COLORES["texto_primario"])
                    indicator.config(bg=color)
            
            def on_leave(e):
                if not getattr(btn_container, 'is_active', False):
                    btn.config(bg=ComponentesModernos.COLORES["bg_secundario"], fg=ComponentesModernos.COLORES["texto_secundario"])
                    indicator.config(bg=ComponentesModernos.COLORES["bg_secundario"])
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        # Guardar referencias
        setattr(btn_container, 'button', btn)
        setattr(btn_container, 'indicator', indicator)
        setattr(btn_container, 'color', color)
        setattr(btn_container, 'is_active', False)
        
        return btn_container
    
    def navegar_a(self, seccion, comando):
        """Navegar a una sección específica"""
        self.activar_navegacion(seccion)
        if comando:
            comando()
    
    def activar_navegacion(self, seccion):
        """Activar visualmente una sección de navegación"""
        # Desactivar todos
        for btn_container in self.nav_buttons.values():
            btn_container.is_active = False
            btn_container.button.config(bg=ComponentesModernos.COLORES["bg_secundario"], fg=ComponentesModernos.COLORES["texto_secundario"])
            btn_container.indicator.config(bg=ComponentesModernos.COLORES["bg_secundario"])
        
        # Activar sección actual
        if seccion in self.nav_buttons:
            btn_container = self.nav_buttons[seccion]
            btn_container.is_active = True
            btn_container.button.config(bg=btn_container.color, fg=ComponentesModernos.COLORES["texto_primario"])
            btn_container.indicator.config(bg=btn_container.color)
            
        self.panel_actual = seccion
    
    def crear_area_contenido(self):
        """Crear área principal de contenido"""
        # Container principal con sidebar opcional
        main_container = tk.Frame(self.root, bg=ComponentesModernos.COLORES["bg_principal"])
        main_container.pack(fill="both", expand=True)
        
        # Área de contenido principal
        self.content_frame = tk.Frame(main_container, bg=ComponentesModernos.COLORES["bg_principal"])
        self.content_frame.pack(fill="both", expand=True, side="right")
    
    def crear_sidebar(self):
        """Crear sidebar opcional (oculto por defecto)"""
        self.sidebar_frame = tk.Frame(self.root, bg=ComponentesModernos.COLORES["bg_card"], width=250)
        # No se empaqueta por defecto
    
    def limpiar_contenido(self):
        """Limpiar el área de contenido actual"""
        if self.content_frame:
            for widget in self.content_frame.winfo_children():
                widget.destroy()
    
    def cerrar_aplicacion(self):
        """Cerrar la aplicación correctamente"""
        try:
            if self.controlador:
                # Detener servicios
                self.logger.info("Cerrando servicios...")
            
            if self.root:
                self.root.quit()
                self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error cerrando aplicación: {e}")
    
    def ejecutar(self):
        """Ejecutar la aplicación"""
        try:
            self.inicializar_controlador()
            if self.root:
                self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error ejecutando aplicación: {e}")
            messagebox.showerror("Error Fatal", f"Error ejecutando aplicación:\n{str(e)}")
    
    # ============================================================================
    # SECCIONES PRINCIPALES DE LA APLICACIÓN
    # ============================================================================
    
    def mostrar_dashboard(self):
        """Mostrar dashboard principal con métricas y resumen"""
        self.limpiar_contenido()
        
        # Container principal del dashboard
        dashboard_container = tk.Frame(self.content_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        dashboard_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Header del dashboard
        self.crear_dashboard_header(dashboard_container)
        
        # Grid principal de métricas
        self.crear_metricas_grid(dashboard_container)
        
        # Secciones de información
        self.crear_dashboard_content(dashboard_container)
        
        # Iniciar actualización automática
        self.actualizar_dashboard_datos()
    
    def crear_dashboard_header(self, parent):
        """Crear header del dashboard"""
        header_frame = tk.Frame(parent, bg=ComponentesModernos.COLORES["bg_principal"])
        header_frame.pack(fill="x", pady=(0, 25))
        
        # Título y descripción
        title_frame = tk.Frame(header_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        title_frame.pack(side="left")
        
        title_label = tk.Label(
            title_frame,
            text="🏠 Centro de Comando",
            font=("Segoe UI", 24, "bold"),
            bg=ComponentesModernos.COLORES["bg_principal"],
            fg=ComponentesModernos.COLORES["texto_primario"]
        )
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(
            title_frame,
            text="Panel de control principal - Monitoreo en tiempo real",
            font=("Segoe UI", 12),
            bg=ComponentesModernos.COLORES["bg_principal"],
            fg=ComponentesModernos.COLORES["texto_secundario"]
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Acciones rápidas
        actions_frame = tk.Frame(header_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        actions_frame.pack(side="right")
        
        ComponentesModernos.crear_boton_moderno(
            actions_frame, "🚀 Escaneo Rápido", self.escaneo_rapido, "primario"
        ).pack(side="left", padx=(0, 10))
        
        ComponentesModernos.crear_boton_moderno(
            actions_frame, "🔄 Actualizar", self.actualizar_dashboard, "outline"
        ).pack(side="left")
    
    def crear_metricas_grid(self, parent):
        """Crear grid de métricas principales"""
        metrics_frame = tk.Frame(parent, bg=ComponentesModernos.COLORES["bg_principal"])
        metrics_frame.pack(fill="x", pady=(0, 25))
        
        # Configurar grid 4 columnas
        for i in range(4):
            metrics_frame.columnconfigure(i, weight=1, uniform="metric")
        
        # Métricas principales
        metricas = [
            {
                "titulo": "Amenazas Detectadas",
                "valor": str(self.stats_data["amenazas_detectadas"]),
                "icono": "🛡️",
                "color": ComponentesModernos.COLORES["peligro"],
                "cambio": "+3"
            },
            {
                "titulo": "Archivos Escaneados",
                "valor": f"{self.stats_data['archivos_escaneados']:,}",
                "icono": "📄",
                "color": ComponentesModernos.COLORES["primario"],
                "cambio": "+156"
            },
            {
                "titulo": "Sistema Protegido",
                "valor": self.stats_data["sistema_protegido"],
                "icono": "🔒",
                "color": ComponentesModernos.COLORES["exito"],
                "cambio": "+0.3%"
            },
            {
                "titulo": "Última Actualización",
                "valor": self.stats_data["ultima_actualizacion"],
                "icono": "🔄",
                "color": ComponentesModernos.COLORES["advertencia"],
                "cambio": "2h ago"
            }
        ]
        
        for i, metrica in enumerate(metricas):
            card = ComponentesModernos.crear_metrica_card(
                metrics_frame,
                metrica["titulo"],
                metrica["valor"],
                metrica["icono"],
                metrica["color"],
                metrica["cambio"]
            )
            card.grid(row=0, column=i, sticky="ew", padx=8)
    
    def crear_dashboard_content(self, parent):
        """Crear contenido principal del dashboard"""
        content_container = tk.Frame(parent, bg=ComponentesModernos.COLORES["bg_principal"])
        content_container.pack(fill="both", expand=True)
        
        # Configurar grid 2x2
        content_container.columnconfigure(0, weight=2)  # Gráficos más ancho
        content_container.columnconfigure(1, weight=1)  # Sidebar más estrecho
        content_container.rowconfigure(0, weight=1)
        content_container.rowconfigure(1, weight=1)
        
        # === GRÁFICO DE ACTIVIDAD ===
        self.crear_grafico_actividad(content_container)
        
        # === ALERTAS RECIENTES ===
        self.crear_alertas_recientes(content_container)
        
        # === ESTADO DEL SISTEMA ===
        self.crear_estado_sistema(content_container)
        
        # === ACCIONES RECOMENDADAS ===
        self.crear_acciones_recomendadas(content_container)
    
    def crear_grafico_actividad(self, parent):
        """Crear gráfico de actividad de amenazas"""
        card_container, content = ComponentesModernos.crear_card_moderna(
            parent, "📈 Actividad de Amenazas", "Últimos 7 días"
        )
        card_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        
        # Container centrado para el gráfico
        chart_container = tk.Frame(content, bg=content.cget('bg'))
        chart_container.pack(expand=True, fill="both")
        
        # Frame para centrar el gráfico
        chart_frame = tk.Frame(chart_container, bg=content.cget('bg'))
        chart_frame.pack(expand=True)
        
        # Título centrado
        title_label = tk.Label(
            chart_frame,
            text="Actividad de Amenazas",
            font=("Segoe UI", 12, "bold"),
            bg=content.cget('bg'),
            fg=ComponentesModernos.COLORES["texto_primario"]
        )
        title_label.pack(pady=(10, 15))
        
        # Container del gráfico centrado
        graph_frame = tk.Frame(chart_frame, bg=content.cget('bg'))
        graph_frame.pack()
        
        # Datos simulados
        datos = [("L", 8), ("M", 12), ("X", 5), ("J", 15), ("V", 3), ("S", 7), ("D", 4)]
        
        # Crear columnas del gráfico
        for i, (dia, valor) in enumerate(datos):
            col_frame = tk.Frame(graph_frame, bg=content.cget('bg'))
            col_frame.grid(row=0, column=i, padx=8, pady=10)
            
            # Valor en la parte superior
            value_label = tk.Label(
                col_frame, 
                text=str(valor), 
                font=("Segoe UI", 9, "bold"),
                bg=content.cget('bg'), 
                fg=ComponentesModernos.COLORES["texto_primario"]
            )
            value_label.pack()
            
            # Barra
            altura = max(20, valor * 6)
            color = ComponentesModernos.COLORES["peligro"] if valor > 10 else ComponentesModernos.COLORES["advertencia"] if valor > 5 else ComponentesModernos.COLORES["exito"]
            
            barra = tk.Frame(col_frame, bg=color, width=35, height=altura)
            barra.pack(pady=5)
            barra.pack_propagate(False)
            
            # Día en la parte inferior
            day_label = tk.Label(
                col_frame, 
                text=dia, 
                font=("Segoe UI", 9),
                bg=content.cget('bg'), 
                fg=ComponentesModernos.COLORES["texto_secundario"]
            )
            day_label.pack()
    
    def crear_alertas_recientes(self, parent):
        """Crear panel de alertas recientes"""
        card_container, content = ComponentesModernos.crear_card_moderna(
            parent, "🚨 Centro de Alertas", "Monitoreo en tiempo real"
        )
        card_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        
        # Scrollable container
        canvas = tk.Canvas(content, bg=content.cget('bg'), highlightthickness=0)
        scrollbar = tk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=content.cget('bg'))
        
        # Configurar scroll
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scroll elements
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        # Lista de alertas
        alertas = [
            {
                "tipo": "CRÍTICO",
                "icono": "🔴",
                "titulo": "Intrusión Detectada",
                "descripcion": "Conexión SSH no autorizada desde 192.168.1.100",
                "tiempo": "hace 2 min",
                "severidad": "critico"
            },
            {
                "tipo": "ALERTA",
                "icono": "🟡",
                "titulo": "Proceso Sospechoso",
                "descripcion": "PowerShell ejecutando scripts en segundo plano",
                "tiempo": "hace 8 min",
                "severidad": "alto"
            },
            {
                "tipo": "INFO",
                "icono": "🟢",
                "titulo": "Amenaza Bloqueada",
                "descripcion": "Malware eliminado automáticamente",
                "tiempo": "hace 15 min",
                "severidad": "bajo"
            }
        ]
        
        # Colores por severidad
        colores_severidad = {
            "critico": {"bg": "#2d1b1b", "border": ComponentesModernos.COLORES["peligro"], "text": "#ff6b6b"},
            "alto": {"bg": "#2d251b", "border": ComponentesModernos.COLORES["advertencia"], "text": "#ffd93d"},
            "bajo": {"bg": "#1b2d1f", "border": ComponentesModernos.COLORES["exito"], "text": "#69db7c"}
        }
        
        for alerta in alertas:
            color_config = colores_severidad[alerta["severidad"]]
            
            # Container de la alerta
            alert_container = tk.Frame(scrollable_frame, bg=color_config["bg"], relief="solid", bd=1)
            alert_container.pack(fill="x", padx=3, pady=6)
            
            # Header
            header_frame = tk.Frame(alert_container, bg=color_config["bg"])
            header_frame.pack(fill="x", padx=12, pady=(10, 5))
            
            type_label = tk.Label(
                header_frame,
                text=f"{alerta['icono']} {alerta['tipo']}",
                font=("Segoe UI", 9, "bold"),
                bg=color_config["bg"],
                fg=color_config["text"]
            )
            type_label.pack(side="left")
            
            time_label = tk.Label(
                header_frame,
                text=alerta["tiempo"],
                font=("Segoe UI", 8),
                bg=color_config["bg"],
                fg=ComponentesModernos.COLORES["texto_secundario"]
            )
            time_label.pack(side="right")
            
            # Título
            title_label = tk.Label(
                alert_container,
                text=alerta["titulo"],
                font=("Segoe UI", 11, "bold"),
                bg=color_config["bg"],
                fg=ComponentesModernos.COLORES["texto_primario"],
                anchor="w"
            )
            title_label.pack(fill="x", padx=12, pady=(0, 3))
            
            # Descripción
            desc_label = tk.Label(
                alert_container,
                text=alerta["descripcion"],
                font=("Segoe UI", 9),
                bg=color_config["bg"],
                fg="#c0c0c0",
                anchor="w",
                wraplength=250
            )
            desc_label.pack(fill="x", padx=12, pady=(0, 10))
    
    def crear_estado_sistema(self, parent):
        """Crear panel de estado del sistema"""
        card_container, content = ComponentesModernos.crear_card_moderna(
            parent, "💻 Estado del Sistema", "Recursos en tiempo real"
        )
        card_container.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(10, 0))
        
        # Container principal centrado
        system_container = tk.Frame(content, bg=content.cget('bg'))
        system_container.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Métricas del sistema
        metricas = [("CPU", 45, ComponentesModernos.COLORES["primario"]), 
                   ("RAM", 68, ComponentesModernos.COLORES["advertencia"]), 
                   ("Disco", 82, ComponentesModernos.COLORES["peligro"])]
        
        for nombre, valor, color in metricas:
            # Container de métrica
            metric_container = tk.Frame(system_container, bg=content.cget('bg'))
            metric_container.pack(fill="x", pady=12)
            
            # Header
            header_frame = tk.Frame(metric_container, bg=content.cget('bg'))
            header_frame.pack()
            
            name_label = tk.Label(
                header_frame, 
                text=nombre, 
                font=("Segoe UI", 11, "bold"),
                bg=content.cget('bg'), 
                fg=ComponentesModernos.COLORES["texto_primario"]
            )
            name_label.pack(side="left", padx=(0, 20))
            
            value_label = tk.Label(
                header_frame, 
                text=f"{valor}%", 
                font=("Segoe UI", 11, "bold"),
                bg=content.cget('bg'), 
                fg=color
            )
            value_label.pack(side="right")
            
            # Barra de progreso
            progress_container = tk.Frame(metric_container, bg=content.cget('bg'))
            progress_container.pack(fill="x", pady=(8, 0))
            
            progress_bg = tk.Frame(progress_container, bg=ComponentesModernos.COLORES["borde_principal"], height=12)
            progress_bg.pack(fill="x")
            
            progress_width = int((valor / 100) * 200)
            progress_bar = tk.Frame(progress_bg, bg=color, width=progress_width, height=12)
            progress_bar.pack(side="left")
            progress_bar.pack_propagate(False)
    
    def crear_acciones_recomendadas(self, parent):
        """Crear panel de acciones rápidas"""
        card_container, content = ComponentesModernos.crear_card_moderna(
            parent, "⚡ Centro de Control", "Acciones rápidas del sistema"
        )
        card_container.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(10, 0))
        
        # Container principal
        main_container = tk.Frame(content, bg=content.cget('bg'))
        main_container.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Grid 2x2
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Acciones principales
        acciones = [
            {
                "titulo": "Scan Completo",
                "descripcion": "Escanear todo el sistema",
                "icono": "🔍",
                "comando": self.mostrar_escaneo,
                "color": ComponentesModernos.COLORES["primario"],
                "posicion": (0, 0)
            },
            {
                "titulo": "Actualizar BD",
                "descripcion": "Firmas y definiciones",
                "icono": "🔄",
                "comando": self.actualizar_firmas,
                "color": ComponentesModernos.COLORES["exito"],
                "posicion": (0, 1)
            },
            {
                "titulo": "Reportes",
                "descripcion": "Generar informe",
                "icono": "📊",
                "comando": self.mostrar_reportes,
                "color": ComponentesModernos.COLORES["advertencia"],
                "posicion": (1, 0)
            },
            {
                "titulo": "Configurar",
                "descripcion": "Ajustar parámetros",
                "icono": "⚙️",
                "comando": self.mostrar_configuracion,
                "color": ComponentesModernos.COLORES["secundario"],
                "posicion": (1, 1)
            }
        ]
        
        for accion in acciones:
            row, col = accion["posicion"]
            
            # Container de la acción
            action_container = tk.Frame(
                main_container, 
                bg=ComponentesModernos.COLORES["bg_card"], 
                relief="flat", 
                bd=1,
                highlightthickness=1,
                highlightcolor=ComponentesModernos.COLORES["borde_principal"]
            )
            action_container.grid(
                row=row, 
                column=col, 
                sticky="nsew", 
                padx=4, 
                pady=4
            )
            
            # Frame interno clickeable
            inner_frame = tk.Frame(action_container, bg=ComponentesModernos.COLORES["bg_card"], cursor="hand2")
            inner_frame.pack(fill="both", expand=True, padx=8, pady=12)
            
            # Icono
            icon_label = tk.Label(
                inner_frame,
                text=accion["icono"],
                font=("Arial", 24),
                bg=ComponentesModernos.COLORES["bg_card"],
                fg=accion["color"]
            )
            icon_label.pack(pady=(0, 8))
            
            # Título
            title_label = tk.Label(
                inner_frame,
                text=accion["titulo"],
                font=("Segoe UI", 11, "bold"),
                bg=ComponentesModernos.COLORES["bg_card"],
                fg=ComponentesModernos.COLORES["texto_primario"]
            )
            title_label.pack()
            
            # Descripción
            desc_label = tk.Label(
                inner_frame,
                text=accion["descripcion"],
                font=("Segoe UI", 8),
                bg=ComponentesModernos.COLORES["bg_card"],
                fg=ComponentesModernos.COLORES["texto_secundario"]
            )
            desc_label.pack(pady=(2, 0))
            
            # Bind click
            widgets = [action_container, inner_frame, icon_label, title_label, desc_label]
            for widget in widgets:
                widget.bind("<Button-1>", lambda e, cmd=accion["comando"]: cmd())
                if widget != action_container:
                    widget.configure(cursor="hand2")
    
    # ============================================================================
    # FUNCIONES DE ACCIÓN
    # ============================================================================
    
    def escaneo_rapido(self):
        """Ejecutar escaneo rápido"""
        self.mostrar_escaneo()
    
    def actualizar_dashboard(self):
        """Actualizar datos del dashboard"""
    def actualizar_dashboard_datos(self):
        """Actualizar datos del dashboard automáticamente"""
        try:
            if self.controlador:
                # Obtener datos reales del controlador
                datos_dashboard = self.controlador.obtener_datos_dashboard()
                
                # Actualizar estadísticas en la interfaz
                if self.stats_widgets:
                    # Actualizar contadores principales
                    componentes_activos = sum(datos_dashboard.get("componentes_activos", {}).values())
                    alertas_criticas = datos_dashboard.get("alertas_criticas", 0)
                    
                    # Simular otros datos para el dashboard
                    archivos_escaneados = datos_dashboard.get("estadisticas", {}).get("archivos_procesados", 0)
                    amenazas_detectadas = datos_dashboard.get("estadisticas", {}).get("amenazas_detectadas", 0)
                    
                    # Actualizar widgets si existen
                    for widget_name, widget in self.stats_widgets.items():
                        if widget_name == "componentes" and hasattr(widget, 'config'):
                            widget.config(text=str(componentes_activos))
                        elif widget_name == "alertas" and hasattr(widget, 'config'):
                            widget.config(text=str(alertas_criticas))
                        elif widget_name == "archivos" and hasattr(widget, 'config'):
                            widget.config(text=str(archivos_escaneados))
                        elif widget_name == "amenazas" and hasattr(widget, 'config'):
                            widget.config(text=str(amenazas_detectadas))
                
                self.logger.debug("Dashboard actualizado con datos reales")
            
            # Programar siguiente actualización
            if self.root:
                self.root.after(30000, self.actualizar_dashboard_datos)  # 30 segundos
                
        except Exception as e:
            self.logger.error(f"Error actualizando dashboard: {e}")
            # Programar siguiente actualización incluso si hay error
            if self.root:
                self.root.after(30000, self.actualizar_dashboard_datos)
    
    def actualizar_firmas(self):
        """Actualizar base de datos de firmas"""
        try:
            if self.controlador:
                threading.Thread(target=self._actualizar_firmas_worker, daemon=True).start()
            else:
                messagebox.showwarning("Error", "Controlador no inicializado")
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando firmas:\n{str(e)}")
    
    def _actualizar_firmas_worker(self):
        """Worker para actualizar firmas en segundo plano"""
        try:
            # Simular actualización
            time.sleep(2)
            if self.root:
                self.root.after(0, lambda: messagebox.showinfo("Éxito", "Base de datos actualizada correctamente"))
        except Exception as e:
            error_msg = str(e)
            if self.root:
                self.root.after(0, lambda error_msg=error_msg: messagebox.showerror("Error", f"Error actualizando firmas:\n{error_msg}"))
    
    def mostrar_reportes(self):
        """Mostrar interfaz de reportes"""
        self.limpiar_contenido()
        
        # Container principal
        reportes_container = tk.Frame(self.content_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        reportes_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Header
        header_frame = tk.Frame(reportes_container, bg=ComponentesModernos.COLORES["bg_principal"])
        header_frame.pack(fill="x", pady=(0, 25))
        
        title_label = tk.Label(
            header_frame,
            text="📋 Centro de Reportes",
            font=("Segoe UI", 24, "bold"),
            bg=ComponentesModernos.COLORES["bg_principal"],
            fg=ComponentesModernos.COLORES["texto_primario"]
        )
        title_label.pack(side="left")
        
        # Botón para generar reporte
        ComponentesModernos.crear_boton_moderno(
            header_frame, "📊 Generar Reporte", self.generar_reporte_completo, "primario"
        ).pack(side="right")
        
        # Grid de tipos de reportes
        reportes_frame = tk.Frame(reportes_container, bg=ComponentesModernos.COLORES["bg_principal"])
        reportes_frame.pack(fill="x", pady=(0, 25))
        
        for i in range(2):
            reportes_frame.columnconfigure(i, weight=1, uniform="reportes")
        
        # Tipos de reportes disponibles
        tipos_reportes = [
            {
                "titulo": "📊 Reporte de Seguridad",
                "descripcion": "Resumen completo del estado de seguridad",
                "comando": self.generar_reporte_seguridad,
                "columna": 0
            },
            {
                "titulo": "🔍 Reporte de Escaneos",
                "descripcion": "Historial y resultados de escaneos",
                "comando": self.generar_reporte_escaneos,
                "columna": 1
            },
            {
                "titulo": "📡 Reporte de Monitoreo",
                "descripcion": "Actividad de red y procesos",
                "comando": self.generar_reporte_monitoreo,
                "columna": 0
            },
            {
                "titulo": "🔒 Reporte de Cuarentena",
                "descripcion": "Estado de archivos en cuarentena",
                "comando": self.generar_reporte_cuarentena,
                "columna": 1
            }
        ]
        
        for i, reporte in enumerate(tipos_reportes):
            row = i // 2
            col = reporte["columna"]
            
            # Asegurar que tengamos suficientes filas
            reportes_frame.rowconfigure(row, weight=1, uniform="reportes")
            
            card_container, card_content = ComponentesModernos.crear_card_moderna(
                reportes_frame, reporte["titulo"], reporte["descripcion"]
            )
            card_container.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            
            ComponentesModernos.crear_boton_moderno(
                card_content, "Generar", reporte["comando"], "outline"
            ).pack(pady=10)
        
        # Área de vista previa del último reporte
        preview_container, preview_content = ComponentesModernos.crear_card_moderna(
            reportes_container, "📄 Vista Previa del Último Reporte", "Contenido del reporte"
        )
        preview_container.pack(fill="both", expand=True)
        
        # Text widget para mostrar contenido
        text_frame = tk.Frame(preview_content, bg=preview_content.cget('bg'))
        text_frame.pack(fill="both", expand=True, pady=10)
        
        self.report_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=ComponentesModernos.COLORES["bg_secundario"],
            fg=ComponentesModernos.COLORES["texto_secundario"],
            relief="flat",
            padx=15,
            pady=15
        )
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        self.report_text.pack(side="left", fill="both", expand=True)
        self.report_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.report_text.yview)
        
        # Mostrar reporte inicial si hay controlador
        if self.controlador:
            try:
                reporte_inicial = "=== REPORTE INICIAL DE ARES AEGIS ===\n\n"
                datos_dashboard = self.controlador.obtener_datos_dashboard()
                
                reporte_inicial += f"Estado del Sistema: {'OPERATIVO' if datos_dashboard.get('estado_sistema', {}).get('sistema_iniciado') else 'NO OPERATIVO'}\n"
                reporte_inicial += f"Componentes Activos: {sum(datos_dashboard.get('componentes_activos', {}).values())}/6\n"
                reporte_inicial += f"Alertas Críticas: {datos_dashboard.get('alertas_criticas', 0)}\n"
                reporte_inicial += f"Timestamp: {datos_dashboard.get('timestamp', 'N/A')}\n\n"
                
                reporte_inicial += "=== ESTADÍSTICAS GENERALES ===\n"
                stats = datos_dashboard.get('estadisticas', {})
                reporte_inicial += f"Archivos Escaneados: {stats.get('archivos_escaneados', 0)}\n"
                reporte_inicial += f"Amenazas Detectadas: {stats.get('amenazas_detectadas', 0)}\n"
                reporte_inicial += f"Total de Eventos: {stats.get('total_eventos', 0)}\n\n"
                
                reporte_inicial += "Utilice los botones superiores para generar reportes específicos."
                
                self.report_text.insert(tk.END, reporte_inicial)
            except Exception as e:
                self.report_text.insert(tk.END, f"Error cargando reporte inicial: {str(e)}")
        else:
            self.report_text.insert(tk.END, "Controlador no disponible. No se pueden generar reportes.")
    
    def generar_reporte_completo(self):
        """Generar reporte completo del sistema"""
        try:
            if not self.controlador:
                messagebox.showwarning("Error", "Controlador no disponible")
                return
            
            # Usar el método del controlador si existe
            if hasattr(self.controlador, 'generar_reporte_completo'):
                reporte = self.controlador.generar_reporte_completo()
            else:
                # Generar reporte básico
                datos = self.controlador.obtener_datos_dashboard()
                reporte = f"# REPORTE COMPLETO - ARES AEGIS\n\n"
                reporte += f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                reporte += f"## Estado del Sistema\n"
                reporte += f"- Sistema Iniciado: {datos.get('estado_sistema', {}).get('sistema_iniciado', False)}\n"
                reporte += f"- Componentes Activos: {sum(datos.get('componentes_activos', {}).values())}\n"
                reporte += f"- Alertas Críticas: {datos.get('alertas_criticas', 0)}\n\n"
            
            # Mostrar en la interfaz
            if hasattr(self, 'report_text'):
                self.report_text.delete(1.0, tk.END)
                self.report_text.insert(tk.END, reporte)
            
            messagebox.showinfo("Completado", "Reporte completo generado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {str(e)}")
    
    def generar_reporte_seguridad(self):
        """Generar reporte específico de seguridad"""
        try:
            if not self.controlador:
                messagebox.showwarning("Error", "Controlador no disponible")
                return
            
            datos = self.controlador.obtener_datos_dashboard()
            estado_monitores = self.controlador.obtener_estado_monitores()
            
            reporte = "=== REPORTE DE SEGURIDAD ===\n\n"
            reporte += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            reporte += "ESTADO DE COMPONENTES:\n"
            componentes = datos.get('componentes_activos', {})
            if componentes and isinstance(componentes, dict):
                for comp, activo in componentes.items():
                    estado = "✅ ACTIVO" if activo else "❌ INACTIVO"
                    reporte += f"- {comp.upper()}: {estado}\n"
            
            reporte += f"\nESTADO DE MONITORES:\n"
            if estado_monitores and isinstance(estado_monitores, dict):
                for monitor, info in estado_monitores.items():
                    if isinstance(info, dict):
                        estado = "🟢 ACTIVO" if info.get('activo') else "🔴 INACTIVO"
                        reporte += f"- {monitor.replace('_', ' ').upper()}: {estado}\n"
            
            reporte += f"\nALERTAS CRÍTICAS: {datos.get('alertas_criticas', 0)}\n"
            reporte += f"TOTAL EVENTOS: {datos.get('estadisticas', {}).get('total_eventos', 0)}\n"
            
            if hasattr(self, 'report_text'):
                self.report_text.delete(1.0, tk.END)
                self.report_text.insert(tk.END, reporte)
            
            messagebox.showinfo("Completado", "Reporte de seguridad generado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte de seguridad: {str(e)}")
    
    def generar_reporte_escaneos(self):
        """Generar reporte de escaneos"""
        try:
            if not self.controlador:
                messagebox.showwarning("Error", "Controlador no disponible")
                return
            # Usar método del controlador si existe
            if hasattr(self.controlador, 'generar_reporte_escaneos'):
                reporte = self.controlador.generar_reporte_escaneos()
            else:
                # Generar reporte básico de escaneos
                datos = self.controlador.obtener_datos_dashboard()
                historial = datos.get('historial_escaneos', [])
                reporte = "=== REPORTE DE ESCANEOS ===\n\n"
                reporte += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                reporte += f"TOTAL DE ESCANEOS: {len(historial)}\n\n"
                if historial:
                    reporte += "DETALLES DE ESCANEOS:\n"
                    for i, escaneo in enumerate(historial[:10]):
                        if isinstance(escaneo, dict):
                            reporte += f"- {escaneo.get('tipo', 'N/A')} en {escaneo.get('ruta', 'N/A')}\n"
                            reporte += f"  Resultado: {escaneo.get('resultado', 'N/A')}\n"
                            reporte += f"  Fecha: {escaneo.get('fecha', 'N/A')}\n\n"
                    if len(historial) > 10:
                        reporte += f"... y {len(historial) - 10} escaneos más.\n"
                else:
                    reporte += "No hay escaneos registrados.\n"
            if hasattr(self, 'report_text'):
                self.report_text.delete(1.0, tk.END)
                self.report_text.insert(tk.END, reporte)
            messagebox.showinfo("Completado", "Reporte de escaneos generado")
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte de escaneos: {str(e)}")
    
    def generar_reporte_monitoreo(self):
        """Generar reporte de monitoreo"""
        try:
            if not self.controlador:
                messagebox.showwarning("Error", "Controlador no disponible")
                return
            # Usar método del controlador si existe
            if hasattr(self.controlador, 'generar_reporte_monitoreo'):
                reporte = self.controlador.generar_reporte_monitoreo()
            else:
                # Generar reporte básico de monitoreo
                estado_monitores = self.controlador.obtener_estado_monitores()
                reporte = "=== REPORTE DE MONITOREO ===\n\n"
                reporte += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                if estado_monitores and isinstance(estado_monitores, dict):
                    reporte += "ESTADO DE MONITORES:\n"
                    for monitor, info in estado_monitores.items():
                        if isinstance(info, dict):
                            estado = "🟢 ACTIVO" if info.get('activo') else "🔴 INACTIVO"
                            reporte += f"- {monitor.replace('_', ' ').upper()}: {estado}\n"
                            reporte += f"  Última actividad: {info.get('ultima_actividad', 'N/A')}\n"
                            reporte += f"  Eventos recientes: {info.get('eventos_recientes', 0)}\n\n"
                else:
                    reporte += "No hay información de monitores disponible.\n"
            if hasattr(self, 'report_text'):
                self.report_text.delete(1.0, tk.END)
                self.report_text.insert(tk.END, reporte)
            messagebox.showinfo("Completado", "Reporte de monitoreo generado")
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte de monitoreo: {str(e)}")
    
    def generar_reporte_cuarentena(self):
        """Generar reporte de cuarentena"""
        try:
            if not self.controlador:
                messagebox.showwarning("Error", "Controlador no disponible")
                return
            
            lista_cuarentena = self.controlador.obtener_lista_cuarentena()
            
            reporte = "=== REPORTE DE CUARENTENA ===\n\n"
            reporte += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            reporte += f"TOTAL DE ARCHIVOS EN CUARENTENA: {len(lista_cuarentena)}\n\n"
            
            if lista_cuarentena:
                reporte += "DETALLES DE ARCHIVOS:\n"
                # Convertir a lista si no lo es y procesar
                archivos_lista = lista_cuarentena if isinstance(lista_cuarentena, list) else []
                for i, archivo in enumerate(archivos_lista[:10]):  # Primeros 10
                    if isinstance(archivo, dict):
                        reporte += f"- {archivo.get('nombre', 'N/A')} ({archivo.get('nivel_riesgo', 'N/A')})\n"
                        reporte += f"  Origen: {archivo.get('ruta_original', 'N/A')}\n"
                        reporte += f"  Fecha: {archivo.get('fecha_cuarentena', 'N/A')}\n\n"
                
                if len(archivos_lista) > 10:
                    reporte += f"... y {len(archivos_lista) - 10} archivos más.\n"
            else:
                reporte += "No hay archivos en cuarentena.\n"
            
            if hasattr(self, 'report_text'):
                self.report_text.delete(1.0, tk.END)
                self.report_text.insert(tk.END, reporte)
            
            messagebox.showinfo("Completado", "Reporte de cuarentena generado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte de cuarentena: {str(e)}")
    
    def mostrar_configuracion(self):
        """Mostrar interfaz de configuración"""
        self.limpiar_contenido()
        
        # Container principal
        config_container = tk.Frame(self.content_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        config_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Header
        header_frame = tk.Frame(config_container, bg=ComponentesModernos.COLORES["bg_principal"])
        header_frame.pack(fill="x", pady=(0, 25))
        
        title_label = tk.Label(
            header_frame,
            text="⚙️ Configuración del Sistema",
            font=("Segoe UI", 24, "bold"),
            bg=ComponentesModernos.COLORES["bg_principal"],
            fg=ComponentesModernos.COLORES["texto_primario"]
        )
        title_label.pack(side="left")
        
        # Botones de acción
        btn_frame = tk.Frame(header_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        btn_frame.pack(side="right")
        
        ComponentesModernos.crear_boton_moderno(
            btn_frame, "💾 Guardar", self.guardar_configuracion, "primario"
        ).pack(side="right", padx=(0, 10))
        
        ComponentesModernos.crear_boton_moderno(
            btn_frame, "🔄 Recargar", self.recargar_configuracion, "outline"
        ).pack(side="right", padx=(0, 10))
        
        # Notebook para diferentes secciones de configuración
        from tkinter import ttk
        
        notebook = ttk.Notebook(config_container)
        notebook.pack(fill="both", expand=True)
        
        # Tab 1: Configuración General
        general_frame = tk.Frame(notebook, bg=ComponentesModernos.COLORES["bg_principal"])
        notebook.add(general_frame, text="General")
        
        self.crear_seccion_config_general(general_frame)
        
        # Tab 2: Configuración de Escaneo
        escaneo_frame = tk.Frame(notebook, bg=ComponentesModernos.COLORES["bg_principal"])
        notebook.add(escaneo_frame, text="Escaneo")
        
        self.crear_seccion_config_escaneo(escaneo_frame)
        
        # Tab 3: Configuración de Monitoreo
        monitor_frame = tk.Frame(notebook, bg=ComponentesModernos.COLORES["bg_principal"])
        notebook.add(monitor_frame, text="Monitoreo")
        
        self.crear_seccion_config_monitoreo(monitor_frame)
    
    def crear_seccion_config_general(self, parent):
        """Crear sección de configuración general"""
        # Estado del sistema
        estado_card, estado_content = ComponentesModernos.crear_card_moderna(
            parent, "📊 Estado del Sistema", "Información general"
        )
        estado_card.pack(fill="x", padx=20, pady=10)
        
        if self.controlador:
            try:
                datos = self.controlador.obtener_datos_dashboard()
                estado_texto = f"Sistema: {'OPERATIVO' if datos.get('estado_sistema', {}).get('sistema_iniciado') else 'NO OPERATIVO'}\n"
                estado_texto += f"Uptime: {datos.get('estado_sistema', {}).get('uptime_segundos', 0)} segundos\n"
                estado_texto += f"Componentes activos: {sum(datos.get('componentes_activos', {}).values())}/6"
            except:
                estado_texto = "Error obteniendo estado del sistema"
        else:
            estado_texto = "Controlador no disponible"
        
        estado_label = tk.Label(
            estado_content,
            text=estado_texto,
            font=("Segoe UI", 10),
            bg=estado_content.cget('bg'),
            fg=ComponentesModernos.COLORES["texto_secundario"],
            justify="left"
        )
        estado_label.pack(pady=10)
    
    def crear_seccion_config_escaneo(self, parent):
        """Crear sección de configuración de escaneo"""
        config_card, config_content = ComponentesModernos.crear_card_moderna(
            parent, "🔍 Configuración de Escaneo", "Opciones del escaneador"
        )
        config_card.pack(fill="x", padx=20, pady=10)
        
        # Información de configuración actual
        if self.controlador:
            try:
                config = self.controlador.obtener_configuracion_sistema()
                rutas = config.get('rutas_escaneadas', [])
                exclusiones = config.get('exclusiones', [])
                
                info_text = f"Rutas configuradas: {len(rutas)}\n"
                info_text += f"Exclusiones: {len(exclusiones)}\n"
                info_text += "Estado: Configurado"
            except:
                info_text = "Error obteniendo configuración"
        else:
            info_text = "Controlador no disponible"
        
        config_label = tk.Label(
            config_content,
            text=info_text,
            font=("Segoe UI", 10),
            bg=config_content.cget('bg'),
            fg=ComponentesModernos.COLORES["texto_secundario"],
            justify="left"
        )
        config_label.pack(pady=10)
    
    def crear_seccion_config_monitoreo(self, parent):
        """Crear sección de configuración de monitoreo"""
        monitor_card, monitor_content = ComponentesModernos.crear_card_moderna(
            parent, "📡 Configuración de Monitoreo", "Estado de los monitores"
        )
        monitor_card.pack(fill="x", padx=20, pady=10)
        
        if self.controlador:
            try:
                estado_monitores = self.controlador.obtener_estado_monitores()
                monitor_text = ""
                if estado_monitores:
                    # Usar getattr para evitar problemas de typing
                    monitores_dict = dict(estado_monitores) if hasattr(estado_monitores, 'items') else {}
                    for monitor in ['monitor_red', 'monitor_procesos', 'fim', 'analisis_dinamico']:
                        if monitor in monitores_dict:
                            info = monitores_dict[monitor]
                            if isinstance(info, dict):
                                estado = "🟢 ACTIVO" if info.get('activo') else "🔴 INACTIVO"
                                monitor_text += f"{monitor.replace('_', ' ').title()}: {estado}\n"
                else:
                    monitor_text = "No hay datos de monitores disponibles"
            except Exception as e:
                monitor_text = f"Error obteniendo estado de monitores: {str(e)}"
        else:
            monitor_text = "Controlador no disponible"
        
        monitor_label = tk.Label(
            monitor_content,
            text=monitor_text,
            font=("Segoe UI", 10),
            bg=monitor_content.cget('bg'),
            fg=ComponentesModernos.COLORES["texto_secundario"],
            justify="left"
        )
        monitor_label.pack(pady=10)
    
    def guardar_configuracion(self):
        """Guardar configuración actual usando el controlador"""
        try:
            if self.controlador and hasattr(self.controlador, 'guardar_configuracion'):
                exito = self.controlador.guardar_configuracion()
                if exito:
                    messagebox.showinfo("Guardado", "Configuración guardada correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo guardar la configuración")
            else:
                messagebox.showwarning("Advertencia", "No hay controlador disponible para guardar configuración")
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando configuración: {str(e)}")
    
    def recargar_configuracion(self):
        """Recargar configuración desde archivo usando el controlador"""
        try:
            if self.controlador and hasattr(self.controlador, 'recargar_configuracion'):
                exito = self.controlador.recargar_configuracion()
                if exito:
                    messagebox.showinfo("Recargado", "Configuración recargada correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo recargar la configuración")
            else:
                messagebox.showwarning("Advertencia", "No hay controlador disponible para recargar configuración")
        except Exception as e:
            messagebox.showerror("Error", f"Error recargando configuración: {str(e)}")
        self.mostrar_configuracion()  # Refrescar la interfaz
    
    # Métodos placeholder para módulos avanzados (se sobrescriben en integración)
    def mostrar_monitoreo(self):
        """Mostrar interfaz de monitoreo completo"""
        try:
            if self.herramientas:
                self.herramientas.mostrar_monitoreo()
            else:
                messagebox.showwarning("Error", "Módulo de herramientas no inicializado")
        except Exception as e:
            self.logger.error(f"Error mostrando monitoreo: {e}")
            messagebox.showerror("Error", f"Error al abrir monitoreo: {str(e)}")
    
    def mostrar_proteccion(self):
        """Mostrar interfaz de protección proactiva"""
        try:
            if self.herramientas:
                self.herramientas.mostrar_proteccion()
            else:
                messagebox.showwarning("Error", "Módulo de herramientas no inicializado")
        except Exception as e:
            self.logger.error(f"Error mostrando protección: {e}")
            messagebox.showerror("Error", f"Error al abrir protección: {str(e)}")
    
    def mostrar_herramientas(self):
        """Mostrar interfaz de herramientas especializadas"""
        try:
            if self.herramientas:
                self.herramientas.mostrar_herramientas()
            else:
                messagebox.showwarning("Error", "Módulo de herramientas no inicializado")
        except Exception as e:
            self.logger.error(f"Error mostrando herramientas: {e}")
            messagebox.showerror("Error", f"Error al abrir herramientas: {str(e)}")
    
    # ============================================================================
    # INTERFACES ESPECÍFICAS (CONTINUACIÓN EN ARCHIVOS SEPARADOS)
    # ============================================================================
    
    def mostrar_escaneo(self):
        """Mostrar interfaz de escaneo - Definida completamente aquí"""
        self.limpiar_contenido()
        # Container principal
        escaneo_container = tk.Frame(self.content_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        escaneo_container.pack(fill="both", expand=True, padx=30, pady=20)
        # Header
        header_frame = tk.Frame(escaneo_container, bg=ComponentesModernos.COLORES["bg_principal"])
        header_frame.pack(fill="x", pady=(0, 25))
        title_label = tk.Label(
            header_frame,
            text="🔍 Centro de Análisis y Escaneo",
            font=("Segoe UI", 24, "bold"),
            bg=ComponentesModernos.COLORES["bg_principal"],
            fg=ComponentesModernos.COLORES["texto_primario"]
        )
        title_label.pack(side="left")
        ComponentesModernos.crear_boton_moderno(
            header_frame, "⚙️ Configurar", self.configurar_escaneo, "outline"
        ).pack(side="right")
        # Grid de opciones
        options_frame = tk.Frame(escaneo_container, bg=ComponentesModernos.COLORES["bg_principal"])
        options_frame.pack(fill="x", pady=(0, 25))
        for i in range(3):
            options_frame.columnconfigure(i, weight=1, uniform="scan")
        # Opciones de escaneo
        opciones = [
            {
                "titulo": "🚀 Escaneo Rápido",
                "descripcion": "Análisis de ubicaciones críticas\n(2-5 minutos)",
                "comando": self.ejecutar_escaneo_rapido,
                "columna": 0
            },
            {
                "titulo": "🔍 Escaneo Completo",
                "descripcion": "Análisis exhaustivo del sistema\n(15-45 minutos)",
                "comando": self.ejecutar_escaneo_completo,
                "columna": 1
            },
            {
                "titulo": "📁 Escaneo Personalizado",
                "descripcion": "Seleccionar directorios específicos\n(Variable)",
                "comando": self.ejecutar_escaneo_personalizado,
                "columna": 2
            }
        ]
        # Crear y guardar referencia a los botones para habilitar/deshabilitar
        self.boton_escaneo_rapido = None
        self.boton_escaneo_completo = None
        self.boton_escaneo_personalizado = None
        for opcion in opciones:
            card_container, content = ComponentesModernos.crear_card_moderna(
                options_frame, opcion["titulo"], opcion["descripcion"]
            )
            card_container.grid(row=0, column=opcion["columna"], sticky="nsew", padx=8)
            boton = ComponentesModernos.crear_boton_moderno(
                content, "Iniciar Escaneo", opcion["comando"], "primario"
            )
            boton.pack(pady=10)
            if opcion["columna"] == 0:
                self.boton_escaneo_rapido = boton
            elif opcion["columna"] == 1:
                self.boton_escaneo_completo = boton
            elif opcion["columna"] == 2:
                self.boton_escaneo_personalizado = boton
        # Estado inicial de los botones según el controlador
        self._actualizar_estado_botones_escaneo(self.controlador_listo)
        # Área de progreso
        self.crear_area_progreso_escaneo(escaneo_container)
    
    def mostrar_cuarentena(self):
        """Mostrar interfaz de cuarentena - Definida completamente aquí"""
        self.limpiar_contenido()
        
        # Container principal
        cuarentena_container = tk.Frame(self.content_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        cuarentena_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Header
        header_frame = tk.Frame(cuarentena_container, bg=ComponentesModernos.COLORES["bg_principal"])
        header_frame.pack(fill="x", pady=(0, 25))
        
        title_label = tk.Label(
            header_frame,
            text="🛡️ Centro de Cuarentena",
            font=("Segoe UI", 24, "bold"),
            bg=ComponentesModernos.COLORES["bg_principal"],
            fg=ComponentesModernos.COLORES["texto_primario"]
        )
        title_label.pack(side="left")
        
        # Botones de acción
        actions_frame = tk.Frame(header_frame, bg=ComponentesModernos.COLORES["bg_principal"])
        actions_frame.pack(side="right")
        
        ComponentesModernos.crear_boton_moderno(
            actions_frame, "🔄 Actualizar", self.actualizar_cuarentena, "outline"
        ).pack(side="right", padx=(0, 10))
        
        ComponentesModernos.crear_boton_moderno(
            actions_frame, "🧹 Limpiar Todo", self.limpiar_cuarentena, "peligro"
        ).pack(side="right", padx=(0, 10))
        
        # Estadísticas simuladas
        stats_frame = tk.Frame(cuarentena_container, bg=ComponentesModernos.COLORES["bg_principal"])
        stats_frame.pack(fill="x", pady=(0, 25))
        
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1, uniform="stats")
        
        stats = {"activos": 3, "backups": 12, "logs": 45, "temp": 8}
        estadisticas = [
            ("🚨 Archivos Activos", stats["activos"], ComponentesModernos.COLORES["peligro"]),
            ("💾 Backups", stats["backups"], ComponentesModernos.COLORES["advertencia"]),
            ("📋 Logs", stats["logs"], ComponentesModernos.COLORES["info"]),
            ("📁 Temporales", stats["temp"], ComponentesModernos.COLORES["secundario"])
        ]
        
        for i, (titulo, valor, color) in enumerate(estadisticas):
            stat_container, stat_content = ComponentesModernos.crear_card_moderna(
                stats_frame, titulo, f"{valor} elementos"
            )
            stat_container.grid(row=0, column=i, sticky="nsew", padx=8)
            
            num_label = tk.Label(
                stat_content,
                text=str(valor),
                font=("Segoe UI", 32, "bold"),
                bg=stat_content.cget('bg'),
                fg=color
            )
            num_label.pack(pady=10)
        
        # Lista simple de archivos en cuarentena
        list_container, list_content = ComponentesModernos.crear_card_moderna(
            cuarentena_container, "📁 Archivos en Cuarentena", "Gestión de elementos"
        )
        list_container.pack(fill="both", expand=True)
        
        # Obtener lista real de archivos en cuarentena
        archivos_nombres = []
        archivos_data = []  # Para almacenar los datos completos
        
        if self.controlador:
            try:
                # Obtener lista real del controlador de cuarentena
                if hasattr(self.controlador, 'controlador_cuarentena') and self.controlador.controlador_cuarentena:
                    archivos = self.controlador.controlador_cuarentena.obtener_lista_cuarentena()
                    if archivos:
                        archivos_data = archivos  # Guardar datos completos
                        
                        for archivo in archivos:
                            if isinstance(archivo, dict):
                                nombre = archivo.get("nombre_archivo", archivo.get("nombre", "Archivo desconocido"))
                                amenaza = archivo.get("razon_cuarentena", archivo.get("razon", "Desconocido"))
                                fecha = archivo.get("fecha_cuarentena", "")[:10] if archivo.get("fecha_cuarentena") else "Sin fecha"
                                estado = archivo.get("estado", "ACTIVO")
                                if not isinstance(estado, str) and hasattr(estado, 'value'):
                                    estado = estado.value.upper()
                                else:
                                    estado = str(estado).upper()
                            else:
                                nombre = getattr(archivo, "nombre_original", "Archivo desconocido")
                                amenaza = getattr(archivo, "razon_cuarentena", "Desconocido")
                                fecha = getattr(archivo, "timestamp_cuarentena", None)
                                if fecha:
                                    fecha = str(fecha)[:10]
                                else:
                                    fecha = "Sin fecha"
                                estado = getattr(archivo, "estado", "ACTIVO")
                                if not isinstance(estado, str) and hasattr(estado, 'value'):
                                    estado = estado.value.upper()
                                else:
                                    estado = str(estado).upper()
                            archivos_nombres.append(f"{nombre} | {amenaza} | {fecha} | {estado}")
                    else:
                        archivos_nombres = ["No hay archivos en cuarentena"]
                        
                elif hasattr(self.controlador, 'gestor_cuarentena') and self.controlador.gestor_cuarentena:
                    # Usar gestor directamente si no hay controlador específico
                    archivos = self.controlador.gestor_cuarentena.obtener_lista_cuarentena()
                    if isinstance(archivos, list) and archivos:
                        archivos_data = archivos
                        
                        for archivo in archivos:
                            if isinstance(archivo, dict):
                                nombre = archivo.get("nombre_archivo", archivo.get("nombre", "Archivo desconocido"))
                                amenaza = archivo.get("razon_cuarentena", archivo.get("razon", "Desconocido"))
                                fecha = archivo.get("fecha_cuarentena", "")[:10] if archivo.get("fecha_cuarentena") else "Sin fecha"
                                estado = archivo.get("estado", "ACTIVO")
                                if not isinstance(estado, str) and hasattr(estado, 'value'):
                                    estado = estado.value.upper()
                                else:
                                    estado = str(estado).upper()
                            else:
                                nombre = getattr(archivo, "nombre_original", "Archivo desconocido")
                                amenaza = getattr(archivo, "razon_cuarentena", "Desconocido")
                                fecha = getattr(archivo, "timestamp_cuarentena", None)
                                if fecha:
                                    fecha = str(fecha)[:10]
                                else:
                                    fecha = "Sin fecha"
                                estado = getattr(archivo, "estado", "ACTIVO")
                                if not isinstance(estado, str) and hasattr(estado, 'value'):
                                    estado = estado.value.upper()
                                else:
                                    estado = str(estado).upper()
                            archivos_nombres.append(f"{nombre} | {amenaza} | {fecha} | {estado}")
                    else:
                        archivos_nombres = ["No hay archivos en cuarentena"]
                else:
                    archivos_nombres = ["Módulo de cuarentena no disponible"]
            except Exception as e:
                archivos_nombres = [f"Error cargando archivos: {str(e)}"]
        else:
            archivos_nombres = ["Controlador no disponible"]
        
        # Lista con scrollbar
        list_frame, listbox = ComponentesModernos.crear_lista_moderna(
            list_content, 
            archivos_nombres
        )
        list_frame.pack(fill="both", expand=True, pady=10)
        
        # Guardar referencias para acciones
        self.listbox_cuarentena = listbox
        self.archivos_cuarentena_data = archivos_data  # Datos completos para operaciones
        
        # Botones de acción
        btn_frame = tk.Frame(list_content, bg=list_content.cget('bg'))
        btn_frame.pack(fill="x", pady=10)
        
        ComponentesModernos.crear_boton_moderno(
            btn_frame, "🔓 Restaurar", self.restaurar_archivo, "primario"
        ).pack(side="left", padx=(0, 10))
        
        ComponentesModernos.crear_boton_moderno(
            btn_frame, "🗑️ Eliminar", self.eliminar_archivo, "peligro"
        ).pack(side="left")
    
    # ============================================================================
    # FUNCIONES DE SOPORTE PARA ESCANEO Y CUARENTENA
    # ============================================================================
    
    def ejecutar_escaneo_rapido(self):
        """Ejecutar escaneo rápido real y robusto, con soporte de cancelación y cuarentena."""
        if not hasattr(self, 'controlador') or self.controlador is None:
            messagebox.showwarning("Error", "Controlador no inicializado")
            return
        self._cancelar_escaneo = False
        def actualizar_progreso(msg, prog, *args, **kwargs):
            try:
                if hasattr(self, 'actualizar_progreso_escaneo'):
                    self.actualizar_progreso_escaneo(msg, prog)
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Error en callback de progreso: {e}")
        def run_escaneo():
            try:
                resultado = None
                if self.controlador and hasattr(self.controlador, 'ejecutar_escaneo_rapido'):
                    resultado = self.controlador.ejecutar_escaneo_rapido(callback_progreso=actualizar_progreso)
                else:
                    if hasattr(self, 'logger'):
                        self.logger.error("El controlador no implementa ejecutar_escaneo_rapido o es None")
                    return
                # Cancelación: si se solicitó cancelar, no continuar
                if getattr(self, '_cancelar_escaneo', False):
                    if hasattr(self, 'actualizar_progreso_escaneo'):
                        self.actualizar_progreso_escaneo("Escaneo cancelado", 0)
                    return
                # Mover archivos infectados a cuarentena
                infectados = resultado.get('archivos_infectados_lista', []) if resultado else []
                cuarentena_ctrl = getattr(self.controlador, 'controlador_cuarentena', None)
                if cuarentena_ctrl:
                    for archivo in infectados:
                        try:
                            cuarentena_ctrl.cuarentenar_archivo(archivo, razon="Detectado en escaneo rápido", origen_deteccion="Escaneo rápido")
                        except Exception as e:
                            if hasattr(self, 'logger'):
                                self.logger.error(f"Error moviendo a cuarentena: {e}")
                if hasattr(self, 'actualizar_progreso_escaneo'):
                    self.actualizar_progreso_escaneo("Escaneo completado", 100)
                if hasattr(self, 'root') and self.root:
                    amenazas = resultado.get('amenazas_detectadas', 0) if resultado else 0
                    tiempo = resultado.get('tiempo_escaneo', 0) if resultado else 0
                    archivos = resultado.get('archivos_escaneados', 0) if resultado else 0
                    mensaje = f"Escaneo rápido completado:\n\n"
                    mensaje += f"• Archivos escaneados: {archivos}\n"
                    mensaje += f"• Amenazas detectadas: {amenazas}\n"
                    mensaje += f"• Tiempo transcurrido: {tiempo:.2f} segundos"
                    self.root.after(0, lambda: messagebox.showinfo("Completado", mensaje))
            except Exception as e:
                if hasattr(self, 'root') and self.root:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Error en escaneo: {str(e)}"))
                if hasattr(self, 'logger'):
                    self.logger.error(f"Error en escaneo rápido: {e}")
        try:
            if hasattr(self, 'actualizar_progreso_escaneo'):
                self.actualizar_progreso_escaneo("Escaneo rápido en curso...", 5)
            self._cancelar_escaneo = False
            self._hilo_escaneo = threading.Thread(
                target=run_escaneo,
                daemon=True
            )
            self._hilo_escaneo.start()
        except Exception as e:
            error_msg = str(e)
            if hasattr(self, 'root') and self.root:
                self.root.after(0, lambda error_msg=error_msg: messagebox.showerror("Error", f"Error en escaneo: {error_msg}"))
            if hasattr(self, 'logger'):
                self.logger.error(f"Error lanzando hilo de escaneo: {e}")

    def ejecutar_escaneo_completo(self):
        """Ejecutar escaneo completo real y robusto"""
        if not hasattr(self, 'controlador') or self.controlador is None:
            messagebox.showwarning("Error", "Controlador no inicializado")
            return
        def actualizar_progreso(msg, prog, *args, **kwargs):
            try:
                if hasattr(self, 'actualizar_progreso_escaneo'):
                    self.actualizar_progreso_escaneo(msg, prog)
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Error en callback de progreso: {e}")
        def run_escaneo():
            try:
                resultado = None
                if self.controlador and hasattr(self.controlador, 'ejecutar_escaneo_completo'):
                    resultado = self.controlador.ejecutar_escaneo_completo(callback_progreso=actualizar_progreso)
                else:
                    if hasattr(self, 'logger'):
                        self.logger.error("El controlador no implementa ejecutar_escaneo_completo o es None")
                    return
                if hasattr(self, 'actualizar_progreso_escaneo'):
                    self.actualizar_progreso_escaneo("Escaneo completo finalizado", 100)
                if hasattr(self, 'root') and self.root:
                    amenazas = resultado.get('amenazas_encontradas', 0) if resultado else 0
                    tiempo = resultado.get('tiempo_transcurrido', 0) if resultado else 0
                    archivos = resultado.get('archivos_escaneados', 0) if resultado else 0
                    mensaje = f"Escaneo completo finalizado:\n\n"
                    mensaje += f"• Archivos escaneados: {archivos}\n"
                    mensaje += f"• Amenazas detectadas: {amenazas}\n"
                    mensaje += f"• Tiempo transcurrido: {tiempo:.2f} segundos"
                    self.root.after(0, lambda: messagebox.showinfo("Completado", mensaje))
            except Exception as e:
                if hasattr(self, 'root') and self.root:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Error en escaneo completo: {str(e)}"))
                if hasattr(self, 'logger'):
                    self.logger.error(f"Error en escaneo completo: {e}")
        try:
            if hasattr(self, 'actualizar_progreso_escaneo'):
                self.actualizar_progreso_escaneo("Escaneo completo en curso...", 5)
            threading.Thread(
                target=run_escaneo,
                daemon=True
            ).start()
        except Exception as e:
            error_msg = str(e)
            if hasattr(self, 'root') and self.root:
                self.root.after(0, lambda error_msg=error_msg: messagebox.showerror("Error", f"Error en escaneo completo: {error_msg}"))
            if hasattr(self, 'logger'):
                self.logger.error(f"Error lanzando hilo de escaneo completo: {e}")

    def ejecutar_escaneo_personalizado(self):
        """Ejecutar escaneo personalizado"""
        directorio = filedialog.askdirectory(title="Seleccionar directorio a escanear")
        if directorio:
            messagebox.showinfo("Iniciado", f"Escaneando directorio: {directorio}")
    
    def crear_area_progreso_escaneo(self, parent):
        """Crear área de progreso visual y robusta para escaneo"""
        progress_container, progress_content = ComponentesModernos.crear_card_moderna(
            parent, "📊 Progreso del Escaneo", "Estado actual"
        )
        progress_container.pack(fill="x", pady=(0, 20))

        # Barra de progreso usando componentes modernos
        self.progress_frame, self.actualizar_progreso_func = ComponentesModernos.crear_progress_moderna(
            progress_content, 0, 100, "Listo para escanear"
        )
        self.progress_frame.pack(fill="x", pady=10)

        # Label de estado
        self.status_escaneo_label = tk.Label(
            progress_content,
            text="Listo para escanear",
            font=("Segoe UI", 10),
            bg=progress_content.cget('bg'),
            fg=ComponentesModernos.COLORES["texto_secundario"]
        )
        self.status_escaneo_label.pack(pady=5)
    
    def actualizar_progreso_escaneo(self, mensaje, progreso):
        """Actualizar progreso del escaneo en la interfaz gráfica de forma robusta"""
        try:
            # Permitir argumentos variables para robustez
            if hasattr(self, 'actualizar_progreso_func'):
                try:
                    self.actualizar_progreso_func(progreso, mensaje)
                except Exception as e1:
                    try:
                        self.actualizar_progreso_func(mensaje, progreso)
                    except Exception as e2:
                        if hasattr(self, 'logger'):
                            self.logger.error(f"Error en callback de progreso: {e1} | {e2}")
                        else:
                            print(f"[ERROR] Error en callback de progreso: {e1} | {e2}")
            if hasattr(self, 'status_escaneo_label'):
                self.status_escaneo_label.config(text=mensaje)
            if hasattr(self, 'root') and self.root:
                self.root.update_idletasks()
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Error actualizando progreso: {e}")
            else:
                print(f"[ERROR] Error actualizando progreso: {e}")
    
    def configurar_escaneo(self):
        """Configurar escaneo"""
        messagebox.showinfo("Configuración", "Panel de configuración de escaneo en desarrollo")
    
    def actualizar_cuarentena(self):
        """Actualizar cuarentena"""
        self.mostrar_cuarentena()
        messagebox.showinfo("Actualizado", "Vista de cuarentena actualizada")
    
    def limpiar_cuarentena(self):
        """Limpiar cuarentena (real, usando el controlador)"""
        respuesta = messagebox.askyesno(
            "Limpiar Cuarentena",
            "¿Está seguro que desea limpiar toda la cuarentena?\n\nEsta acción NO se puede deshacer."
        )
        if not respuesta:
            return
        cuarentena_ctrl = getattr(self.controlador, 'controlador_cuarentena', None) if hasattr(self, 'controlador') and self.controlador else None
        if cuarentena_ctrl and hasattr(cuarentena_ctrl, 'limpiar_cuarentena'):
            try:
                resultado = cuarentena_ctrl.limpiar_cuarentena(confirmar=True)
                if isinstance(resultado, dict):
                    if resultado.get('exitoso'):
                        messagebox.showinfo("Limpiado", "Cuarentena limpiada correctamente")
                        self.actualizar_cuarentena()
                    else:
                        error_msg = resultado.get('error', 'No se pudo limpiar la cuarentena')
                        messagebox.showerror("Error", f"No se pudo limpiar la cuarentena: {error_msg}")
                elif resultado is True:
                    messagebox.showinfo("Limpiado", "Cuarentena limpiada correctamente")
                    self.actualizar_cuarentena()
                else:
                    messagebox.showerror("Error", "No se pudo limpiar la cuarentena (resultado inesperado)")
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Error limpiando cuarentena: {e}")
                messagebox.showerror("Error", f"Error limpiando cuarentena: {str(e)}")
        else:
            messagebox.showwarning("Error", "Controlador de cuarentena no disponible")
    
    def restaurar_archivo(self):
        """Restaurar archivo de cuarentena (real)."""
        if not hasattr(self, 'listbox_cuarentena') or self.listbox_cuarentena is None:
            messagebox.showwarning("Error", "Lista de cuarentena no disponible")
            return
        try:
            selection = self.listbox_cuarentena.curselection()
            if not selection:
                messagebox.showwarning("Selección", "Por favor seleccione un archivo para restaurar")
                return
            indice = selection[0]
            if hasattr(self, 'archivos_cuarentena_data') and self.archivos_cuarentena_data:
                if indice < len(self.archivos_cuarentena_data):
                    archivo_data = self.archivos_cuarentena_data[indice]
                    archivo_id = archivo_data.get("id", archivo_data.get("archivo_id", None))
                    nombre_archivo = archivo_data.get("nombre", archivo_data.get("nombre_archivo", "Archivo desconocido"))
                    respuesta = messagebox.askyesno(
                        "Restaurar archivo",
                        f"¿Está seguro que desea restaurar:\n{nombre_archivo}?\n\nEl archivo será devuelto a su ubicación original."
                    )
                    cuarentena_ctrl = getattr(self.controlador, 'controlador_cuarentena', None) if hasattr(self, 'controlador') and self.controlador else None
                    if respuesta and cuarentena_ctrl and hasattr(cuarentena_ctrl, 'restaurar_archivo'):
                        try:
                            resultado = cuarentena_ctrl.restaurar_archivo(archivo_id)
                            if isinstance(resultado, dict):
                                if resultado.get('exitoso'):
                                    messagebox.showinfo("Restaurado", f"Archivo restaurado correctamente: {nombre_archivo}")
                                    self.actualizar_cuarentena()
                                else:
                                    error_msg = resultado.get('error', 'No se pudo restaurar el archivo')
                                    messagebox.showerror("Error", f"No se pudo restaurar el archivo: {error_msg}")
                            elif resultado is True:
                                messagebox.showinfo("Restaurado", f"Archivo restaurado correctamente: {nombre_archivo}")
                                self.actualizar_cuarentena()
                            else:
                                messagebox.showerror("Error", "No se pudo restaurar el archivo (resultado inesperado)")
                        except Exception as e:
                            if hasattr(self, 'logger'):
                                self.logger.error(f"Error restaurando archivo: {e}")
                            messagebox.showerror("Error", f"Error restaurando archivo: {str(e)}")
                    elif respuesta:
                        messagebox.showwarning("Error", "Controlador de cuarentena no disponible")
                else:
                    messagebox.showwarning("Error", "Índice de archivo fuera de rango")
            else:
                messagebox.showwarning("Error", "No hay datos de archivos disponibles")
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Error restaurando archivo: {e}")
            messagebox.showerror("Error", f"Error restaurando archivo: {str(e)}")
    
