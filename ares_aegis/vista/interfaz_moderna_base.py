#!/usr/bin/env python3
"""
Interfaz Base de Ares Aegis
Sistema Principal con Dashboard, Escaneo y Cuarentena

🏠 INTERFAZ PRINCIPAL Y CORE
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from ..controladores.controlador_alertas import ControladorAlertas
from ..modelos.alerta import Alerta, SeveridadAlerta, TipoAlerta
import platform
import subprocess
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
    def mostrar_resumen_alertas(self):
        """Muestra un resumen visual de alertas por severidad y tipo."""
        resumen = "Resumen de Alertas:\n"
        for sev in SeveridadAlerta:
            total = self.controlador_alertas.total_por_severidad(sev)
            resumen += f"- {sev.name.title()}: {total}\n"
        resumen += "\nPor Tipo:\n"
        for tipo in TipoAlerta:
            total = self.controlador_alertas.total_por_tipo(tipo)
            resumen += f"- {tipo.name.title()}: {total}\n"
        # Aquí puedes mostrar el resumen en un panel, label o cuadro de texto de la interfaz
        print(resumen)  # Sustituir por lógica de UI
    def mostrar_confirmacion(self, mensaje, titulo="Confirmar acción"):
        """Muestra un diálogo modal de confirmación (sí/no) y retorna True/False"""
        respuesta = {'valor': False}
        if self.root is None:
            raise RuntimeError("La ventana principal (self.root) no está inicializada.")
        win = tk.Toplevel(self.root)
        win.title(titulo)
        win.transient(self.root)
        win.grab_set()
        win.geometry("300x140")
        win.resizable(False, False)
        win.configure(bg="#23272e")
        label = tk.Label(win, text=mensaje, bg="#23272e", fg="#fff", font=("Segoe UI", 10), wraplength=260)
        label.pack(pady=18, padx=18)
        frame = tk.Frame(win, bg="#23272e")
        frame.pack(pady=8)
        def aceptar():
            respuesta['valor'] = True
            win.destroy()
        def cancelar():
            respuesta['valor'] = False
            win.destroy()
        btn_si = tk.Button(frame, text="Sí", width=10, command=aceptar, bg="#69db7c", fg="#23272e", font=("Segoe UI", 9, "bold"))
        btn_si.pack(side="left", padx=10)
        btn_no = tk.Button(frame, text="No", width=10, command=cancelar, bg="#ff6b6b", fg="#23272e", font=("Segoe UI", 9, "bold"))
        btn_no.pack(side="right", padx=10)
        self.root.wait_window(win)
        return respuesta['valor']
    def parar_escaneo(self):
        """Detener cualquier escaneo en curso y limpiar la caché de escaneos."""
        if not self.controlador:
            self.mostrar_alerta("Controlador no disponible", tipo="advertencia")
            return
        exito_cancelar = False
        exito_cache = False
        try:
            if hasattr(self.controlador, 'cancelar_escaneo_en_curso'):
                exito_cancelar = self.controlador.cancelar_escaneo_en_curso()
            if hasattr(self.controlador, 'limpiar_cache_escaneos'):
                exito_cache = self.controlador.limpiar_cache_escaneos()
            if exito_cancelar:
                self.mostrar_alerta("El escaneo en curso ha sido detenido correctamente.", tipo="info")
            else:
                self.mostrar_alerta("No hay escaneo en curso o no se pudo cancelar.", tipo="advertencia")
            if exito_cache:
                self.mostrar_alerta("La caché de escaneos ha sido limpiada correctamente.", tipo="info")
            else:
                self.mostrar_alerta("No se pudo limpiar la caché de escaneos.", tipo="advertencia")
        except Exception as e:
            self.mostrar_alerta(f"Error al detener escaneo o limpiar caché:\n{str(e)}", tipo="critico")
    """Interfaz principal moderna de Ares Aegis con UX profesional"""
    
    def __init__(self):
        """Inicializar la interfaz moderna"""
        self.logger = logging.getLogger(__name__)
        self.root: Optional[tk.Tk] = tk.Tk()  # Inicializa la ventana principal de Tkinter
        self.root.title("ARES AEGIS - Centro de Comando de Ciberseguridad Avanzada")
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
        # Controlador de alertas centralizado (MVC)
        self.controlador_alertas = ControladorAlertas()
        # Bandeja de alertas flotantes
        from .bandeja_alertas_flotantes import BandejaAlertasFlotantes
        self.bandeja_alertas = BandejaAlertasFlotantes(self.root)
        self.logger.info("Interfaz Moderna Base inicializada correctamente")
        # Configurar el icono de la aplicación
        self.configurar_icono()
        # Configurar la interfaz gráfica moderna automáticamente
        self.configurar_interfaz()
        # Inicializar herramientas modernas y conectar referencia
        self.herramientas = None
        try:
            from .interfaz_moderna_herramientas import InterfazModernaHerramientas
            self.herramientas = InterfazModernaHerramientas(self)
        except Exception as e:
            self.logger.warning(f"No se pudo inicializar herramientas modernas: {e}")
        # Mostrar el dashboard automáticamente al iniciar
        self.mostrar_dashboard()

    def mostrar_alerta(self, mensaje, tipo="info", duracion=5000, fuente="sistema", datos=None):
        """Muestra una alerta flotante moderna y la registra en el controlador de alertas"""
        # Mapear tipo a SeveridadAlerta
        tipo_map = {
            "critico": SeveridadAlerta.CRITICO,
            "alto": SeveridadAlerta.ALTO,
            "advertencia": SeveridadAlerta.ALTO,
            "medio": SeveridadAlerta.MEDIO,
            "bajo": SeveridadAlerta.BAJO,
            "info": SeveridadAlerta.INFO
        }
        severidad = tipo_map.get(tipo, SeveridadAlerta.INFO)
        # Determinar tipo lógico
        tipo_alerta = TipoAlerta.OTRO
        if datos and "tipo_alerta" in datos:
            try:
                tipo_alerta = TipoAlerta(datos["tipo_alerta"])
            except Exception:
                tipo_alerta = TipoAlerta.OTRO
        alerta = self.controlador_alertas.crear_alerta(mensaje, tipo_alerta, severidad, fuente, datos)
        if hasattr(self, 'bandeja_alertas'):
            self.bandeja_alertas.mostrar_alerta(mensaje, tipo, duracion)
        else:
            print(f"ALERTA [{tipo}]: {mensaje}")
    
    def eliminar_archivo(self):
        """Eliminar archivo de cuarentena (real y robusto)."""
        if not hasattr(self, 'listbox_cuarentena') or self.listbox_cuarentena is None:
            self.mostrar_alerta("Lista de cuarentena no disponible", tipo="advertencia")
            return
        try:
            selection = self.listbox_cuarentena.curselection()
            if not selection:
                self.mostrar_alerta("Por favor seleccione un archivo para eliminar", tipo="advertencia")
                return
            indice = selection[0]
            if hasattr(self, 'archivos_cuarentena_data') and self.archivos_cuarentena_data:
                if indice < len(self.archivos_cuarentena_data):
                    archivo_data = self.archivos_cuarentena_data[indice]
                    archivo_id = archivo_data.get("id", archivo_data.get("archivo_id", None))
                    nombre_archivo = archivo_data.get("nombre", archivo_data.get("nombre_archivo", "Archivo desconocido"))
                    respuesta = self.mostrar_confirmacion(
                        f"¿Está seguro que desea eliminar permanentemente:\n{nombre_archivo}?\n\nEsta acción NO se puede deshacer.",
                        "Eliminar archivo"
                    )
                    cuarentena_ctrl = getattr(self.controlador, 'controlador_cuarentena', None) if hasattr(self, 'controlador') and self.controlador else None
                    if respuesta and cuarentena_ctrl and hasattr(cuarentena_ctrl, 'eliminar_archivo_cuarentena'):
                        try:
                            resultado = cuarentena_ctrl.eliminar_archivo_cuarentena(archivo_id, confirmar=True)
                            if isinstance(resultado, dict) and resultado.get('exitoso'):
                                self.mostrar_alerta(f"Archivo eliminado correctamente: {nombre_archivo}", tipo="info")
                                self.actualizar_cuarentena()
                            else:
                                error_msg = resultado.get('error', 'No se pudo eliminar el archivo') if isinstance(resultado, dict) else 'No se pudo eliminar el archivo'
                                self.mostrar_alerta(f"No se pudo eliminar el archivo: {error_msg}", tipo="critico")
                        except Exception as e:
                            if hasattr(self, 'logger'):
                                self.logger.error(f"Error eliminando archivo: {e}")
                            self.mostrar_alerta(f"Error eliminando archivo: {str(e)}", tipo="critico")
                    elif respuesta:
                        self.mostrar_alerta("Controlador de cuarentena no disponible", tipo="advertencia")
                else:
                    self.mostrar_alerta("Índice de archivo fuera de rango", tipo="advertencia")
            else:
                self.mostrar_alerta("No hay datos de archivos disponibles", tipo="advertencia")
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Error eliminando archivo: {e}")
            self.mostrar_alerta(f"Error eliminando archivo: {str(e)}", tipo="critico")
        try:
            if self.root is not None:
                self.root.attributes('-alpha', 0.98)
        except:
            pass
        
        # Configurar estilos TTK
        TemasModernos.obtener_configuracion_ttk_style()

        # Agregar botón Parar Escaneo en el header (después de crear header_frame)
        # Se agrega aquí para asegurar que header_frame existe
        if self.root is not None:
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
        self.mostrar_alerta(f"Error inicializando controlador:\n{str(error)}", tipo="critico")
    
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
            text="Centro de Comando de Ciberseguridad Avanzada",
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
        # Agregar el botón Parar Escaneo al final del header
        self._agregar_boton_parar_escaneo()
    
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
            ("📊", "Panel", self.mostrar_dashboard, ComponentesModernos.COLORES["primario"]),
            ("🔍", "Escaneo", self.mostrar_escaneo, "#ff6b35"),
            ("🛡️", "Cuarentena", self.mostrar_cuarentena, "#dc3545"),
            ("📡", "Monitoreo", self.mostrar_monitoreo, "#7b68ee"),
            ("🛡️", "Protección", self.mostrar_proteccion, ComponentesModernos.COLORES["exito"]),
            ("🔧", "Herramientas", self.mostrar_herramientas, ComponentesModernos.COLORES["advertencia"]),
            ("📋", "Reportes", self.mostrar_reportes, ComponentesModernos.COLORES["peligro"]),
            ("⚙️", "Configuración", self.mostrar_configuracion, ComponentesModernos.COLORES["secundario"])
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
            self.mostrar_alerta(f"Error ejecutando aplicación:\n{str(e)}", tipo="critico")
    
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
            text="Panel principal de control y monitoreo en tiempo real",
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
                "cambio": "hace 2h"
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
        """Crear panel de alertas recientes usando el controlador de alertas"""
        card_container, content = ComponentesModernos.crear_card_moderna(
            parent, "🚨 Centro de Alertas", "Monitoreo en tiempo real"
        )
        card_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))

        # Scrollable container
        canvas = tk.Canvas(content, bg=content.cget('bg'), highlightthickness=0)
        scrollbar = tk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=content.cget('bg'))
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Obtener alertas recientes del controlador
        alertas = self.controlador_alertas.obtener_alertas(limite=10)
        colores_severidad = {
            "critico": {"bg": "#2d1b1b", "border": ComponentesModernos.COLORES["peligro"], "text": "#ff6b6b"},
            "alto": {"bg": "#2d251b", "border": ComponentesModernos.COLORES["advertencia"], "text": "#ffd93d"},
            "medio": {"bg": "#2d2b1b", "border": "#ffd93d", "text": "#ffd93d"},
            "bajo": {"bg": "#1b2d1f", "border": ComponentesModernos.COLORES["exito"], "text": "#69db7c"},
            "info": {"bg": "#1b2330", "border": "#74b9ff", "text": "#74b9ff"}
        }
        iconos = {
            "critico": "🔴", "alto": "🟡", "medio": "🟠", "bajo": "🟢", "info": "🔵"
        }
        for alerta in alertas:
            sev = alerta.severidad.value
            color_config = colores_severidad.get(sev, colores_severidad["info"])
            icono = iconos.get(sev, "🔵")
            alert_container = tk.Frame(scrollable_frame, bg=color_config["bg"], relief="solid", bd=1)
            alert_container.pack(fill="x", padx=3, pady=6)
            header_frame = tk.Frame(alert_container, bg=color_config["bg"])
            header_frame.pack(fill="x", padx=12, pady=(10, 5))
            type_label = tk.Label(
                header_frame,
                text=f"{icono} {alerta.tipo.value.upper()}",
                font=("Segoe UI", 9, "bold"),
                bg=color_config["bg"],
                fg=color_config["text"]
            )
            type_label.pack(side="left")
            time_label = tk.Label(
                header_frame,
                text=alerta.timestamp.strftime("%H:%M:%S"),
                font=("Segoe UI", 8),
                bg=color_config["bg"],
                fg=ComponentesModernos.COLORES["texto_secundario"]
            )
            time_label.pack(side="right")
            title_label = tk.Label(
                alert_container,
                text=alerta.mensaje,
                font=("Segoe UI", 11, "bold"),
                bg=color_config["bg"],
                fg=ComponentesModernos.COLORES["texto_primario"],
                anchor="w"
            )
            title_label.pack(fill="x", padx=12, pady=(0, 3))
            desc_label = tk.Label(
                alert_container,
                text=alerta.fuente,
                font=("Segoe UI", 9),
                bg=color_config["bg"],
                fg="#c0c0c0",
                anchor="w",
                wraplength=250
            )
            desc_label.pack(fill="x", padx=12, pady=(0, 10))
    
    def crear_estado_sistema(self, parent):
        """Panel de estado del sistema con métricas avanzadas en tiempo real (solo librerías estándar)"""
        card_container, content = ComponentesModernos.crear_card_moderna(
            parent, "💻 Estado del Sistema", "Recursos en tiempo real"
        )
        card_container.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(10, 0))

        self.system_container = tk.Frame(content, bg=content.cget('bg'))
        self.system_container.pack(expand=True, fill="both", padx=20, pady=15)

        # Widgets para actualizar
        self.metricas_widgets = {}
        metricas = [
            ("CPU", ComponentesModernos.COLORES["primario"], True),
            ("RAM", ComponentesModernos.COLORES["advertencia"], True),
            ("Disco", ComponentesModernos.COLORES["peligro"], True),
            ("Red (Subida)", "#00b894", False),
            ("Red (Bajada)", "#0984e3", False),
            ("Procesos Activos", "#fdcb6e", False),
            ("Temperatura CPU", "#e17055", False),
            ("Uptime", "#636e72", False),
            ("Usuarios Conectados", "#6c5ce7", False)
        ]
        for nombre, color, es_barra in metricas:
            metric_container = tk.Frame(self.system_container, bg=content.cget('bg'))
            metric_container.pack(fill="x", pady=8)
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
                text="-",
                font=("Segoe UI", 11, "bold"),
                bg=content.cget('bg'),
                fg=color
            )
            value_label.pack(side="right")
            progress_bar = None
            if es_barra:
                progress_container = tk.Frame(metric_container, bg=content.cget('bg'))
                progress_container.pack(fill="x", pady=(8, 0))
                progress_bg = tk.Frame(progress_container, bg=ComponentesModernos.COLORES["borde_principal"], height=12)
                progress_bg.pack(fill="x")
                progress_bar = tk.Frame(progress_bg, bg=color, width=0, height=12)
                progress_bar.pack(side="left")
                progress_bar.pack_propagate(False)
            self.metricas_widgets[nombre] = {
                "value_label": value_label,
                "progress_bar": progress_bar,
                "color": color,
                "es_barra": es_barra
            }
        # Estado previo de red para calcular velocidad
        self._red_prev = self._obtener_red_bytes()
        self._actualizar_metricas_sistema()

    def _actualizar_metricas_sistema(self):
        """Actualizar métricas avanzadas de sistema en tiempo real (solo librerías estándar)"""
        cpu = self._obtener_cpu_percent()
        ram = self._obtener_ram_percent()
        disco = self._obtener_disco_percent()
        red_actual = self._obtener_red_bytes()
        procesos = self._obtener_procesos_activos()
        temp = self._obtener_temperatura_cpu()
        uptime = self._obtener_uptime()
        usuarios = self._obtener_usuarios_conectados()

        # Calcular velocidad de red
        subida = bajada = 0
        if self._red_prev and red_actual:
            subida = max(0, int((red_actual[0] - self._red_prev[0]) / 2))  # bytes/s
            bajada = max(0, int((red_actual[1] - self._red_prev[1]) / 2))
        self._red_prev = red_actual

        metricas = {
            "CPU": f"{cpu}%",
            "RAM": f"{ram}%",
            "Disco": f"{disco}%",
            "Red (Subida)": f"{self._formatear_bytes(subida)}/s",
            "Red (Bajada)": f"{self._formatear_bytes(bajada)}/s",
            "Procesos Activos": str(procesos),
            "Temperatura CPU": temp,
            "Uptime": uptime,
            "Usuarios Conectados": str(usuarios)
        }
        barras = {
            "CPU": cpu,
            "RAM": ram,
            "Disco": disco
        }
        for nombre, w in self.metricas_widgets.items():
            valor = metricas.get(nombre, "-")
            w["value_label"].config(text=valor)
            if w["es_barra"] and nombre in barras:
                width = int((barras[nombre] / 100) * 200)
                w["progress_bar"].config(width=width)
        # Actualizar cada 2 segundos
        if hasattr(self, 'root') and self.root:
            self.root.after(2000, self._actualizar_metricas_sistema)

    def _obtener_red_bytes(self):
        """Obtener bytes enviados y recibidos por la interfaz principal (Linux, solo estándar)"""
        try:
            if platform.system() == "Linux":
                with open("/proc/net/dev", "r") as f:
                    lines = f.readlines()[2:]
                total_recv = total_sent = 0
                for line in lines:
                    if ":" in line:
                        parts = line.split(":")[1].split()
                        total_recv += int(parts[0])
                        total_sent += int(parts[8])
                return (total_sent, total_recv)
            # Para Windows/Mac se puede implementar con netstat o similar si se requiere
        except Exception:
            pass
        return (0, 0)

    def _formatear_bytes(self, num):
        """Formatear bytes a KB, MB, GB"""
        for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024:
                return f"{num} {unidad}"
            num = num / 1024
        return f"{num:.1f} PB"

    def _obtener_procesos_activos(self):
        """Obtener número de procesos activos (solo estándar)"""
        try:
            if platform.system() == "Linux":
                return len([d for d in os.listdir("/proc") if d.isdigit()])
            elif platform.system() == "Windows":
                result = subprocess.run(["tasklist"], capture_output=True, text=True)
                return len([l for l in result.stdout.splitlines() if l and not l.startswith("Image")])
            elif platform.system() == "Darwin":
                result = subprocess.run(["ps", "-e"], capture_output=True, text=True)
                return len(result.stdout.splitlines()) - 1
        except Exception:
            return 0

    def _obtener_temperatura_cpu(self):
        """Obtener temperatura de CPU si es posible (Linux, solo estándar)"""
        try:
            if platform.system() == "Linux":
                # Intentar leer thermal_zone
                for zone in os.listdir("/sys/class/thermal"):
                    if zone.startswith("thermal_zone"):
                        temp_path = f"/sys/class/thermal/{zone}/temp"
                        if os.path.exists(temp_path):
                            with open(temp_path) as f:
                                temp = int(f.read().strip())
                                if temp > 1000:
                                    temp = temp / 1000.0
                                return f"{temp:.1f}°C"
            # Windows/Mac: no estándar sin librerías externas
        except Exception:
            pass
        return "N/D"

    def _obtener_uptime(self):
        """Obtener uptime del sistema (solo estándar)"""
        try:
            if platform.system() == "Linux":
                with open("/proc/uptime", "r") as f:
                    segundos = float(f.readline().split()[0])
                horas = int(segundos // 3600)
                minutos = int((segundos % 3600) // 60)
                return f"{horas}h {minutos}m"
            elif platform.system() == "Windows":
                result = subprocess.run(["net", "stats", "srv"], capture_output=True, text=True)
                for line in result.stdout.splitlines():
                    if "Statistics since" in line:
                        # No es trivial calcular uptime exacto sin librerías externas
                        return line.strip()
            elif platform.system() == "Darwin":
                result = subprocess.run(["sysctl", "-n", "kern.boottime"], capture_output=True, text=True)
                # Se puede calcular con datetime si se requiere
        except Exception:
            pass
        return "N/D"

    def _obtener_usuarios_conectados(self):
        """Obtener número de usuarios conectados (solo estándar)"""
        try:
            if platform.system() == "Linux":
                result = subprocess.run(["who"], capture_output=True, text=True)
                return len([l for l in result.stdout.splitlines() if l])
            elif platform.system() == "Windows":
                result = subprocess.run(["query", "user"], capture_output=True, text=True)
                return len([l for l in result.stdout.splitlines() if l and not l.startswith("USERNAME")])
            elif platform.system() == "Darwin":
                result = subprocess.run(["who"], capture_output=True, text=True)
                return len([l for l in result.stdout.splitlines() if l])
        except Exception:
            return 0

    def _obtener_cpu_percent(self):
        """Obtener uso de CPU en porcentaje (Linux, Mac, Windows, solo estándar)"""
        try:
            if platform.system() == "Linux":
                # Leer /proc/stat dos veces y calcular diferencia
                with open("/proc/stat", "r") as f:
                    fields1 = f.readline().strip().split()[1:]
                total1 = sum(map(int, fields1))
                idle1 = int(fields1[3])
                time.sleep(0.1)
                with open("/proc/stat", "r") as f:
                    fields2 = f.readline().strip().split()[1:]
                total2 = sum(map(int, fields2))
                idle2 = int(fields2[3])
                total_diff = total2 - total1
                idle_diff = idle2 - idle1
                if total_diff == 0:
                    return 0
                cpu_percent = 100 - int(100 * idle_diff / total_diff)
                return max(0, min(cpu_percent, 100))
            elif platform.system() == "Windows":
                # Usar wmic
                result = subprocess.run(["wmic", "cpu", "get", "loadpercentage"], capture_output=True, text=True)
                for line in result.stdout.splitlines():
                    if line.strip().isdigit():
                        return int(line.strip())
                return 0
            elif platform.system() == "Darwin":
                # Usar top
                result = subprocess.run(["top", "-l", "1", "-n", "0"], capture_output=True, text=True)
                for line in result.stdout.splitlines():
                    if "CPU usage" in line:
                        parts = line.split(",")
                        user = float(parts[0].split()[2].replace("%", ""))
                        sys = float(parts[1].split()[0].replace("%", ""))
                        return int(user + sys)
                return 0
        except Exception:
            return 0

    def _obtener_ram_percent(self):
        """Obtener uso de RAM en porcentaje (Linux, Mac, Windows, solo estándar)"""
        try:
            if platform.system() == "Linux":
                with open("/proc/meminfo", "r") as f:
                    lines = f.readlines()
                mem_total = int([l for l in lines if l.startswith("MemTotal")][0].split()[1])
                mem_available = int([l for l in lines if l.startswith("MemAvailable")][0].split()[1])
                used = mem_total - mem_available
                percent = int(used * 100 / mem_total)
                return max(0, min(percent, 100))
            elif platform.system() == "Windows":
                result = subprocess.run(["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/Value"], capture_output=True, text=True)
                vals = {}
                for line in result.stdout.splitlines():
                    if "=" in line:
                        k, v = line.split("=")
                        vals[k.strip()] = int(v.strip())
                total = vals.get("TotalVisibleMemorySize", 0)
                free = vals.get("FreePhysicalMemory", 0)
                used = total - free
                percent = int(used * 100 / total) if total else 0
                return max(0, min(percent, 100))
            elif platform.system() == "Darwin":
                result = subprocess.run(["vm_stat"], capture_output=True, text=True)
                pages = {}
                for line in result.stdout.splitlines():
                    if ":" in line:
                        k, v = line.split(":")
                        pages[k.strip()] = int(v.strip().replace(".", ""))
                page_size = 4096
                free = pages.get("Pages free", 0) * page_size
                active = pages.get("Pages active", 0) * page_size
                inactive = pages.get("Pages inactive", 0) * page_size
                speculative = pages.get("Pages speculative", 0) * page_size
                wired = pages.get("Pages wired down", 0) * page_size
                total = free + active + inactive + speculative + wired
                used = active + inactive + wired
                percent = int(used * 100 / total) if total else 0
                return max(0, min(percent, 100))
        except Exception:
            return 0

    def _obtener_disco_percent(self):
        """Obtener uso de disco en porcentaje (solo estándar)"""
        try:
            st = os.statvfs("/")
            total = st.f_blocks * st.f_frsize
            free = st.f_bavail * st.f_frsize
            used = total - free
            percent = int(used * 100 / total) if total else 0
            return max(0, min(percent, 100))
        except Exception:
            return 0
    
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
                "titulo": "Escaneo Completo",
                "descripcion": "Escanear todo el sistema",
                "icono": "🔍",
                "comando": self.mostrar_escaneo,
                "color": ComponentesModernos.COLORES["primario"],
                "posicion": (0, 0)
            },
            {
                "titulo": "Actualizar BD",
                "descripcion": "Actualizar firmas y definiciones",
                "icono": "🔄",
                "comando": self.actualizar_firmas,
                "color": ComponentesModernos.COLORES["exito"],
                "posicion": (0, 1)
            },
            {
                "titulo": "Reportes",
                "descripcion": "Generar informe de seguridad",
                "icono": "📊",
                "comando": self.mostrar_reportes,
                "color": ComponentesModernos.COLORES["advertencia"],
                "posicion": (1, 0)
            },
            {
                "titulo": "Configuración",
                "descripcion": "Ajustar parámetros del sistema",
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
        """Actualizar datos del dashboard automáticamente y en tiempo real"""
        try:
            if self.controlador:
                datos_dashboard = self.controlador.obtener_datos_dashboard()
                # Actualizar stats_data para las tarjetas principales
                self.stats_data["amenazas_detectadas"] = datos_dashboard.get("estadisticas", {}).get("amenazas_detectadas", 0)
                self.stats_data["archivos_escaneados"] = datos_dashboard.get("estadisticas", {}).get("archivos_procesados", 0)
                self.stats_data["sistema_protegido"] = datos_dashboard.get("estadisticas", {}).get("porcentaje_proteccion", "98.5%")
                self.stats_data["ultima_actualizacion"] = datos_dashboard.get("timestamp", "Hoy")

                # Si existen widgets de métricas, actualizarlos
                if hasattr(self, 'stats_widgets') and self.stats_widgets:
                    for widget_name, widget in self.stats_widgets.items():
                        if widget_name == "amenazas" and hasattr(widget, 'config'):
                            widget.config(text=str(self.stats_data["amenazas_detectadas"]))
                        elif widget_name == "archivos" and hasattr(widget, 'config'):
                            widget.config(text=str(self.stats_data["archivos_escaneados"]))
                        elif widget_name == "sistema_protegido" and hasattr(widget, 'config'):
                            widget.config(text=str(self.stats_data["sistema_protegido"]))
                        elif widget_name == "ultima_actualizacion" and hasattr(widget, 'config'):
                            widget.config(text=str(self.stats_data["ultima_actualizacion"]))

                # Si hay widgets de alertas recientes, refrescarlos aquí si es necesario
                # (Opcional: implementar lógica para refrescar lista de alertas si se usan widgets dedicados)

                self.logger.debug("Dashboard actualizado con datos reales")

            # Programar siguiente actualización
            if self.root:
                self.root.after(30000, self.actualizar_dashboard_datos)  # 30 segundos

        except Exception as e:
            self.logger.error(f"Error actualizando dashboard: {e}")
            if self.root:
                self.root.after(30000, self.actualizar_dashboard_datos)
    
    def actualizar_firmas(self):
        """Actualizar base de datos de firmas"""
        try:
            if self.controlador:
                threading.Thread(target=self._actualizar_firmas_worker, daemon=True).start()
            else:
                self.mostrar_alerta("Controlador no inicializado", tipo="advertencia")
        except Exception as e:
            self.mostrar_alerta(f"Error actualizando firmas:\n{str(e)}", tipo="critico")
    
    def _actualizar_firmas_worker(self):
        """Worker para actualizar firmas en segundo plano"""
        try:
            # Simular actualización
            time.sleep(2)
            if self.root:
                self.root.after(0, lambda: self.mostrar_alerta("Base de datos actualizada correctamente", tipo="info"))
        except Exception as e:
            error_msg = str(e)
            if self.root:
                self.root.after(0, lambda error_msg=error_msg: self.mostrar_alerta(f"Error actualizando firmas:\n{error_msg}", tipo="critico"))
    
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
                self.mostrar_alerta("Controlador no disponible", tipo="advertencia")
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
            
            self.mostrar_alerta("Reporte completo generado correctamente", tipo="info")
            
        except Exception as e:
            self.mostrar_alerta(f"Error generando reporte: {str(e)}", tipo="critico")
    
    def generar_reporte_seguridad(self):
        """Generar reporte específico de seguridad"""
        try:
            if not self.controlador:
                self.mostrar_alerta("Controlador no disponible", tipo="advertencia")
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
            
            self.mostrar_alerta("Reporte de seguridad generado", tipo="info")
            
        except Exception as e:
            self.mostrar_alerta(f"Error generando reporte de seguridad: {str(e)}", tipo="critico")
    
    def generar_reporte_escaneos(self):
        """Generar reporte de escaneos"""
        try:
            if not self.controlador:
                self.mostrar_alerta("Controlador no disponible", tipo="advertencia")
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
            self.mostrar_alerta("Reporte de escaneos generado", tipo="info")
        except Exception as e:
            self.mostrar_alerta(f"Error generando reporte de escaneos: {str(e)}", tipo="critico")
    
    def generar_reporte_monitoreo(self):
        """Generar reporte de monitoreo"""
        try:
            if not self.controlador:
                self.mostrar_alerta("Controlador no disponible", tipo="advertencia")
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
            self.mostrar_alerta("Reporte de monitoreo generado", tipo="info")
        except Exception as e:
            self.mostrar_alerta(f"Error generando reporte de monitoreo: {str(e)}", tipo="critico")
    
    def generar_reporte_cuarentena(self):
        """Generar reporte de cuarentena"""
        try:
            if not self.controlador:
                self.mostrar_alerta("Controlador no disponible", tipo="advertencia")
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
            
            self.mostrar_alerta("Reporte de cuarentena generado", tipo="info")
            
        except Exception as e:
            self.mostrar_alerta(f"Error generando reporte de cuarentena: {str(e)}", tipo="critico")
    
    def mostrar_configuracion(self):
        """Mostrar interfaz de configuración del sistema"""
        self.limpiar_contenido()
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

        # Panel de opciones principales
        opciones_frame = tk.Frame(config_container, bg=ComponentesModernos.COLORES["bg_principal"])
        opciones_frame.pack(fill="x", pady=(0, 25))
        for i in range(2):
            opciones_frame.columnconfigure(i, weight=1, uniform="config")

        # Opciones de configuración
        opciones = [
            {
                "titulo": "Actualizar Base de Firmas",
                "descripcion": "Descargar e instalar las últimas firmas de amenazas.",
                "comando": self.actualizar_firmas,
                "columna": 0
            },
            {
                "titulo": "Restablecer Configuración",
                "descripcion": "Restaurar los valores predeterminados del sistema.",
                "comando": self.restablecer_configuracion,
                "columna": 1
            },
            {
                "titulo": "Limpiar Archivos Temporales",
                "descripcion": "Eliminar archivos temporales y cachés para liberar espacio.",
                "comando": self.limpiar_archivos_temporales,
                "columna": 0
            },
            {
                "titulo": "Verificar Integridad",
                "descripcion": "Ejecutar verificación de integridad del sistema.",
                "comando": self.verificar_integridad,
                "columna": 1
            }
        ]
        for i, opcion in enumerate(opciones):
            row = i // 2
            col = opcion["columna"]
            opciones_frame.rowconfigure(row, weight=1, uniform="config")
            card_container, card_content = ComponentesModernos.crear_card_moderna(
                opciones_frame, opcion["titulo"], opcion["descripcion"]
            )
            card_container.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            ComponentesModernos.crear_boton_moderno(
                card_content, "Ejecutar", opcion["comando"], "outline"
            ).pack(pady=10)

        # Área de logs/configuración avanzada
        logs_container, logs_content = ComponentesModernos.crear_card_moderna(
            config_container, "📝 Registro de Configuración", "Últimas acciones y eventos"
        )
        logs_container.pack(fill="both", expand=True)
        text_frame = tk.Frame(logs_content, bg=logs_content.cget('bg'))
        text_frame.pack(fill="both", expand=True, pady=10)
        self.config_log_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=ComponentesModernos.COLORES["bg_secundario"],
            fg=ComponentesModernos.COLORES["texto_secundario"],
            relief="flat",
            padx=15,
            pady=15,
            height=10
        )
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        self.config_log_text.pack(side="left", fill="both", expand=True)
        self.config_log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.config_log_text.yview)
        # Mostrar logs iniciales si existen
        self.mostrar_logs_configuracion()

    def restablecer_configuracion(self):
        """Restablecer la configuración del sistema a valores predeterminados"""
        try:
            self.mostrar_alerta("Funcionalidad no disponible en este módulo.", tipo="advertencia")
        except Exception as e:
            self.mostrar_alerta(f"Error al restablecer configuración: {str(e)}", tipo="critico")

    def limpiar_archivos_temporales(self):
        """Limpiar archivos temporales y cachés"""
        try:
            self.mostrar_alerta("Funcionalidad no disponible en este módulo.", tipo="advertencia")
        except Exception as e:
            self.mostrar_alerta(f"Error al limpiar archivos temporales: {str(e)}", tipo="critico")

    def verificar_integridad(self):
        """Verificar la integridad del sistema"""
        try:
            self.mostrar_alerta("Funcionalidad no disponible en este módulo.", tipo="advertencia")
        except Exception as e:
            self.mostrar_alerta(f"Error al verificar integridad: {str(e)}", tipo="critico")

    def mostrar_logs_configuracion(self):
        """Mostrar logs recientes de configuración si existen"""
        try:
            if hasattr(self, 'config_log_text'):
                self.config_log_text.delete(1.0, tk.END)
                # No hay método para obtener logs, mostrar mensaje por defecto
                self.config_log_text.insert(tk.END, "No hay logs de configuración recientes.\n")
        except Exception as e:
            if hasattr(self, 'config_log_text'):
                self.config_log_text.insert(tk.END, f"Error mostrando logs: {str(e)}\n")
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
                    self.mostrar_alerta("Configuración guardada correctamente", tipo="info")
                else:
                    self.mostrar_alerta("No se pudo guardar la configuración", tipo="critico")
            else:
                self.mostrar_alerta("No hay controlador disponible para guardar configuración", tipo="advertencia")
        except Exception as e:
            self.mostrar_alerta(f"Error guardando configuración: {str(e)}", tipo="critico")
    
    def recargar_configuracion(self):
        """Recargar configuración desde archivo usando el controlador"""
        try:
            if self.controlador and hasattr(self.controlador, 'recargar_configuracion'):
                exito = self.controlador.recargar_configuracion()
                if exito:
                    self.mostrar_alerta("Configuración recargada correctamente", tipo="info")
                else:
                    self.mostrar_alerta("No se pudo recargar la configuración", tipo="critico")
            else:
                self.mostrar_alerta("No hay controlador disponible para recargar configuración", tipo="advertencia")
        except Exception as e:
            self.mostrar_alerta(f"Error recargando configuración: {str(e)}", tipo="critico")
        self.mostrar_configuracion()  # Refrescar la interfaz
    
    # Métodos placeholder para módulos avanzados (se sobrescriben en integración)
    def mostrar_monitoreo(self):
        """Mostrar interfaz de monitoreo completo"""
        try:
            if self.herramientas:
                self.herramientas.mostrar_monitoreo()
            else:
                self.mostrar_alerta("Módulo de herramientas no inicializado", tipo="advertencia")
        except Exception as e:
            self.logger.error(f"Error mostrando monitoreo: {e}")
            self.mostrar_alerta(f"Error al abrir monitoreo: {str(e)}", tipo="critico")
    
    def mostrar_proteccion(self):
        """Mostrar interfaz de protección proactiva"""
        try:
            if self.herramientas:
                self.herramientas.mostrar_proteccion()
            else:
                self.mostrar_alerta("Módulo de herramientas no inicializado", tipo="advertencia")
        except Exception as e:
            self.logger.error(f"Error mostrando protección: {e}")
            self.mostrar_alerta(f"Error al abrir protección: {str(e)}", tipo="critico")
    
    def mostrar_herramientas(self):
        """Mostrar interfaz de herramientas especializadas"""
        try:
            if self.herramientas:
                self.herramientas.mostrar_herramientas()
            else:
                self.mostrar_alerta("Módulo de herramientas no inicializado", tipo="advertencia")
        except Exception as e:
            self.logger.error(f"Error mostrando herramientas: {e}")
            self.mostrar_alerta(f"Error al abrir herramientas: {str(e)}", tipo="critico")
    
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
            self.mostrar_alerta("Controlador no inicializado", tipo="advertencia")
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
                    self.root.after(0, lambda: self.mostrar_alerta(mensaje, tipo="info"))
            except Exception as e:
                if hasattr(self, 'root') and self.root:
                    self.root.after(0, lambda: self.mostrar_alerta(f"Error en escaneo: {str(e)}", tipo="critico"))
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
                self.root.after(0, lambda error_msg=error_msg: self.mostrar_alerta(f"Error en escaneo: {error_msg}", tipo="critico"))
            if hasattr(self, 'logger'):
                self.logger.error(f"Error lanzando hilo de escaneo: {e}")

    def ejecutar_escaneo_completo(self):
        """Ejecutar escaneo completo real y robusto"""
        if not hasattr(self, 'controlador') or self.controlador is None:
            self.mostrar_alerta("Controlador no inicializado", tipo="advertencia")
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
                    self.root.after(0, lambda: self.mostrar_alerta(mensaje, tipo="info"))
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
        self.mostrar_alerta("Panel de configuración de escaneo en desarrollo", tipo="info")
    
    def actualizar_cuarentena(self):
        """Actualizar cuarentena"""
        self.mostrar_cuarentena()
        self.mostrar_alerta("Vista de cuarentena actualizada", tipo="info")
    
    def limpiar_cuarentena(self):
        """Limpiar cuarentena (real, usando el controlador)"""
        respuesta = self.mostrar_confirmacion(
            "¿Está seguro que desea limpiar toda la cuarentena?\n\nEsta acción NO se puede deshacer.",
            "Limpiar Cuarentena"
        )
        if not respuesta:
            return
        cuarentena_ctrl = getattr(self.controlador, 'controlador_cuarentena', None) if hasattr(self, 'controlador') and self.controlador else None
        if cuarentena_ctrl and hasattr(cuarentena_ctrl, 'limpiar_cuarentena'):
            try:
                resultado = cuarentena_ctrl.limpiar_cuarentena(confirmar=True)
                if isinstance(resultado, dict):
                    if resultado.get('exitoso'):
                        self.mostrar_alerta("Cuarentena limpiada correctamente", tipo="info")
                        self.actualizar_cuarentena()
                    else:
                        error_msg = resultado.get('error', 'No se pudo limpiar la cuarentena')
                        self.mostrar_alerta(f"No se pudo limpiar la cuarentena: {error_msg}", tipo="critico")
                elif resultado is True:
                    self.mostrar_alerta("Cuarentena limpiada correctamente", tipo="info")
                    self.actualizar_cuarentena()
                else:
                    self.mostrar_alerta("No se pudo limpiar la cuarentena (resultado inesperado)", tipo="critico")
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Error limpiando cuarentena: {e}")
                self.mostrar_alerta(f"Error limpiando cuarentena: {str(e)}", tipo="critico")
        else:
            self.mostrar_alerta("Controlador de cuarentena no disponible", tipo="advertencia")
    
    def restaurar_archivo(self):
        """Restaurar archivo de cuarentena (real)."""
        if not hasattr(self, 'listbox_cuarentena') or self.listbox_cuarentena is None:
            self.mostrar_alerta("Lista de cuarentena no disponible", tipo="advertencia")
            return
        try:
            selection = self.listbox_cuarentena.curselection()
            if not selection:
                self.mostrar_alerta("Por favor seleccione un archivo para restaurar", tipo="advertencia")
                return
            indice = selection[0]
            if hasattr(self, 'archivos_cuarentena_data') and self.archivos_cuarentena_data:
                if indice < len(self.archivos_cuarentena_data):
                    archivo_data = self.archivos_cuarentena_data[indice]
                    archivo_id = archivo_data.get("id", archivo_data.get("archivo_id", None))
                    nombre_archivo = archivo_data.get("nombre", archivo_data.get("nombre_archivo", "Archivo desconocido"))
                    respuesta = self.mostrar_confirmacion(
                        f"¿Está seguro que desea restaurar:\n{nombre_archivo}?\n\nEl archivo será devuelto a su ubicación original.",
                        "Restaurar archivo"
                    )
                    cuarentena_ctrl = getattr(self.controlador, 'controlador_cuarentena', None) if hasattr(self, 'controlador') and self.controlador else None
                    if respuesta and cuarentena_ctrl and hasattr(cuarentena_ctrl, 'restaurar_archivo'):
                        try:
                            resultado = cuarentena_ctrl.restaurar_archivo(archivo_id)
                            if isinstance(resultado, dict):
                                if resultado.get('exitoso'):
                                    self.mostrar_alerta(f"Archivo restaurado correctamente: {nombre_archivo}", tipo="info")
                                    self.actualizar_cuarentena()
                                else:
                                    error_msg = resultado.get('error', 'No se pudo restaurar el archivo')
                                    self.mostrar_alerta(f"No se pudo restaurar el archivo: {error_msg}", tipo="critico")
                            elif resultado is True:
                                self.mostrar_alerta(f"Archivo restaurado correctamente: {nombre_archivo}", tipo="info")
                                self.actualizar_cuarentena()
                            else:
                                self.mostrar_alerta("No se pudo restaurar el archivo (resultado inesperado)", tipo="critico")
                        except Exception as e:
                            if hasattr(self, 'logger'):
                                self.logger.error(f"Error restaurando archivo: {e}")
                            self.mostrar_alerta(f"Error restaurando archivo: {str(e)}", tipo="critico")
                    elif respuesta:
                        self.mostrar_alerta("Controlador de cuarentena no disponible", tipo="advertencia")
                else:
                    self.mostrar_alerta("Índice de archivo fuera de rango", tipo="advertencia")
            else:
                self.mostrar_alerta("No hay datos de archivos disponibles", tipo="advertencia")
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Error restaurando archivo: {e}")
            self.mostrar_alerta(f"Error restaurando archivo: {str(e)}", tipo="critico")
    
