#!/usr/bin/env python3
"""
Interfaz Principal GUI - Ares Aegis
Interfaz gráfica principal del antivirus con estilo japonés

Autor: DogSoulDev
Versión: 2.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter.scrolledtext import ScrolledText
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Importar modelos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from modelos.siem import SIEM, TipoEvento
from modelos.escaneador import Escaneador
from modelos.fim import FIM
from modelos.gestor_cuarentena import GestorCuarentena
from modelos.integracion_externa import IntegracionExterna

# Importar los nuevos módulos de monitoreo
try:
    from modelos.monitor_procesos import MonitorProcesos
    from modelos.monitor_red import MonitorRed
    from modelos.analizador_logs import AnalizadorLogs
    MODULOS_MONITOREO_DISPONIBLES = True
except ImportError:
    MODULOS_MONITOREO_DISPONIBLES = False


# Paleta de colores suaves y cálidos inspirada en el estilo japonés
COLORES = {
    "fondo_principal": "#F5F5DC",      # Beige suave, como papel de arroz
    "fondo_secundario": "#EFEBE9",     # Crema claro
    "fondo_tarjeta": "#FFF8E1",        # Amarillo muy pálido
    "borde_sutil": "#D7CCC8",          # Marrón muy claro, casi gris
    "texto_oscuro": "#3E2723",         # Marrón muy oscuro, casi negro suave
    "texto_claro": "#795548",          # Marrón medio
    "texto_secundario": "#8D6E63",     # Marrón claro
    "boton_normal": "#BCAAA4",         # Gris cálido con toque marrón
    "boton_activo": "#A1887F",         # Gris marrón más oscuro
    "boton_info": "#81C784",           # Verde suave (matcha claro)
    "boton_info_activo": "#66BB6A",    # Verde matcha más intenso
    "boton_peligro": "#FFAB91",        # Naranja suave (atardecer)
    "boton_peligro_activo": "#FF8A65", # Naranja más intenso
    "boton_exito": "#A5D6A7",          # Verde menta suave
    "boton_exito_activo": "#81C784",   # Verde menta activo
    "resaltado_entrada": "#FFF3E0",    # Crema para campos de entrada
    "sombra": "#E0E0E0"                # Gris muy claro para sombras
}


class InterfazPrincipalGUI:
    """Interfaz gráfica principal de Ares Aegis."""
    
    def __init__(self, ventana_maestra: tk.Tk):
        """
        Inicializa la interfaz principal.
        
        Args:
            ventana_maestra: Ventana principal de tkinter
        """
        self.ventana_maestra = ventana_maestra
        self.logger = logging.getLogger(__name__)
        
        # Configurar ventana principal
        self._configurar_ventana_principal()
        
        # Inicializar backend (inyección de dependencias)
        self._inicializar_backend()
        
        # Verificar privilegios de root
        if not self._verificar_privilegios_root():
            self._mostrar_error_privilegios()
            return
        
        # Configurar estilos
        self._configurar_estilos()
        
        # Variables de interfaz
        self.area_resultados: Optional[ScrolledText] = None
        self.entrada_ruta_analisis: Optional[ttk.Entry] = None
        self.area_log_siem: Optional[ScrolledText] = None
        
        # Crear menú principal
        self.crear_menu_principal()
    
    def _configurar_ventana_principal(self):
        """Configura las propiedades de la ventana principal."""
        self.ventana_maestra.title("Ares Aegis: Antivirus Avanzado para Kali Linux")
        self.ventana_maestra.geometry("1200x800")
        self.ventana_maestra.minsize(800, 600)
        self.ventana_maestra.configure(bg=COLORES["fondo_principal"])
        
        # Intentar cargar el icono de la aplicación
        self._cargar_icono_aplicacion()
        
        # Configurar comportamiento de cierre
        self.ventana_maestra.protocol("WM_DELETE_WINDOW", self._al_cerrar_aplicacion)
    
    def _cargar_icono_aplicacion(self):
        """Intenta cargar el icono de la aplicación."""
        rutas_icono = [
            Path(__file__).parent.parent.parent / "recursos" / "aresIcon.ppm",
            Path(__file__).parent.parent.parent / "recursos" / "aresIcon.gif",
            Path(__file__).parent.parent.parent / "recursos" / "aresIcon.png"
        ]
        
        for ruta_icono in rutas_icono:
            try:
                if ruta_icono.exists():
                    self.icono_app = tk.PhotoImage(file=str(ruta_icono))
                    self.ventana_maestra.iconphoto(True, self.icono_app)
                    self.logger.info(f"Icono cargado: {ruta_icono}")
                    return
            except tk.TclError as e:
                self.logger.warning(f"No se pudo cargar icono {ruta_icono}: {e}")
        
        self.logger.warning("No se pudo cargar ningún icono de aplicación")
    
    def _inicializar_backend(self):
        """Inicializa los módulos del backend con inyección de dependencias."""
        try:
            # Inicializar SIEM como dependencia central
            self.siem = SIEM()
            
            # Inicializar módulos pasando el SIEM
            self.escaneador = Escaneador(self.siem)
            self.fim = FIM(self.siem)
            self.gestor_cuarentena = GestorCuarentena(self.siem)
            self.integracion_externa = IntegracionExterna(self.siem)
            
            # Inicializar módulos de monitoreo si están disponibles
            if MODULOS_MONITOREO_DISPONIBLES:
                self.monitor_procesos = MonitorProcesos(self.siem)
                self.monitor_red = MonitorRed(self.siem)
                self.analizador_logs = AnalizadorLogs(self.siem)
            
            self.logger.info("Backend inicializado correctamente")
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, "Interfaz GUI inicializada")
            
        except Exception as e:
            self.logger.error(f"Error inicializando backend: {e}")
            messagebox.showerror("Error de Inicialización", 
                               f"No se pudo inicializar el backend de Ares Aegis:\\n{e}")
            sys.exit(1)
    
    def _verificar_privilegios_root(self) -> bool:
        """Verifica si el script se está ejecutando con privilegios de root."""
        return os.geteuid() == 0
    
    def _mostrar_error_privilegios(self):
        """Muestra error de privilegios y cierra la aplicación."""
        mensaje = ("Ares Aegis requiere privilegios de ROOT para funcionar correctamente.\\n\\n"
                  "Por favor, ejecute la aplicación con:\\n"
                  "sudo python3 main.py")
        
        messagebox.showerror("Error de Privilegios", mensaje)
        print("ERROR: Se requieren privilegios de root para ejecutar Ares Aegis")
        self.ventana_maestra.destroy()
        sys.exit(1)
    
    def _configurar_estilos(self):
        """Configura los estilos personalizados para la interfaz."""
        self.estilo = ttk.Style()
        self.estilo.theme_use('alt')
        
        # Configurar estilos de Frame
        self.estilo.configure('TFrame', background=COLORES["fondo_principal"])
        self.estilo.configure('Card.TFrame', background=COLORES["fondo_tarjeta"], 
                            relief="flat", borderwidth=1)
        
        # Configurar estilos de Label
        self.estilo.configure('TLabel', 
                            font=('Helvetica', 11), 
                            foreground=COLORES["texto_oscuro"], 
                            background=COLORES["fondo_principal"])
        
        self.estilo.configure('Titulo.TLabel', 
                            font=('Helvetica', 24, 'bold'), 
                            foreground=COLORES["texto_oscuro"], 
                            background=COLORES["fondo_principal"])
        
        self.estilo.configure('Subtitulo.TLabel', 
                            font=('Helvetica', 16, 'bold'), 
                            foreground=COLORES["texto_claro"], 
                            background=COLORES["fondo_principal"])
        
        self.estilo.configure('CardTitle.TLabel', 
                            font=('Helvetica', 14, 'bold'), 
                            foreground=COLORES["texto_oscuro"], 
                            background=COLORES["fondo_tarjeta"])
        
        # Configurar estilos de Button
        self.estilo.configure('TButton', 
                            font=('Helvetica', 11, 'bold'), 
                            padding=(15, 10),
                            background=COLORES["boton_normal"], 
                            foreground=COLORES["texto_oscuro"],
                            relief="flat", 
                            borderwidth=0, 
                            focusthickness=0)
        
        self.estilo.map('TButton', 
                       background=[('active', COLORES["boton_activo"]), 
                                 ('!disabled', COLORES["boton_normal"])],
                       relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        
        # Botones especiales
        self.estilo.configure('Info.TButton', 
                            background=COLORES["boton_info"], 
                            foreground=COLORES["texto_oscuro"])
        self.estilo.map('Info.TButton', 
                       background=[('active', COLORES["boton_info_activo"])])
        
        self.estilo.configure('Danger.TButton', 
                            background=COLORES["boton_peligro"], 
                            foreground=COLORES["texto_oscuro"])
        self.estilo.map('Danger.TButton', 
                       background=[('active', COLORES["boton_peligro_activo"])])
        
        self.estilo.configure('Success.TButton', 
                            background=COLORES["boton_exito"], 
                            foreground=COLORES["texto_oscuro"])
        self.estilo.map('Success.TButton', 
                       background=[('active', COLORES["boton_exito_activo"])])
        
        self.estilo.configure('Secondary.TButton', 
                            background=COLORES["borde_sutil"], 
                            foreground=COLORES["texto_oscuro"])
        self.estilo.map('Secondary.TButton', 
                       background=[('active', COLORES["boton_activo"])])
        
        # Configurar estilos de Entry
        self.estilo.configure('TEntry', 
                            fieldbackground=COLORES["resaltado_entrada"], 
                            foreground=COLORES["texto_oscuro"],
                            font=('Helvetica', 10), 
                            borderwidth=1, 
                            relief="solid")
    
    def limpiar_interfaz(self):
        """Elimina todos los widgets actuales de la ventana."""
        for widget in self.ventana_maestra.winfo_children():
            widget.destroy()
    
    def crear_menu_principal(self):
        """Crea el menú principal con las categorías de operación."""
        self.limpiar_interfaz()
        self.ventana_maestra.title("Ares Aegis: Menú Principal")
        
        # Frame principal con padding
        frame_principal = ttk.Frame(self.ventana_maestra, padding="30")
        frame_principal.pack(expand=True, fill='both')
        
        # Configurar grid
        frame_principal.columnconfigure(0, weight=1)
        for i in range(8):
            frame_principal.rowconfigure(i, weight=1)
        
        # Título principal
        ttk.Label(frame_principal, text="Ares Aegis", 
                 style='Titulo.TLabel').grid(row=0, column=0, pady=(0, 5), sticky="n")
        
        ttk.Label(frame_principal, text="Antivirus Avanzado para Kali Linux", 
                 style='Subtitulo.TLabel').grid(row=1, column=0, pady=(0, 20), sticky="n")
        
        # Cargar y mostrar imagen de marca
        self._mostrar_imagen_marca(frame_principal, row=2)
        
        # Frame para botones de categorías
        frame_botones = ttk.Frame(frame_principal, style='Card.TFrame', padding="25")
        frame_botones.grid(row=4, column=0, pady=20, sticky="nsew", padx=50)
        frame_botones.columnconfigure(0, weight=1)
        
        # Botones de categorías principales
        ttk.Button(frame_botones, text="🔍 Detección y Análisis de Archivos", 
                  command=self.mostrar_menu_analisis_archivos,
                  style='Info.TButton').grid(row=0, column=0, pady=8, sticky="ew", padx=20)
        
        ttk.Button(frame_botones, text="📊 Monitoreo de Sistema y Procesos", 
                  command=self.mostrar_menu_monitoreo,
                  style='Info.TButton').grid(row=1, column=0, pady=8, sticky="ew", padx=20)
        
        ttk.Button(frame_botones, text="🗂️ Gestión de Registros y Cuarentena", 
                  command=self.mostrar_menu_logs_cuarentena,
                  style='Info.TButton').grid(row=2, column=0, pady=8, sticky="ew", padx=20)
        
        ttk.Button(frame_botones, text="🛠️ Herramientas del Sistema", 
                  command=self.mostrar_menu_herramientas,
                  style='Info.TButton').grid(row=3, column=0, pady=8, sticky="ew", padx=20)
        
        # Botón de salir
        ttk.Button(frame_principal, text="❌ Salir", 
                  command=self._al_cerrar_aplicacion,
                  style='Danger.TButton').grid(row=6, column=0, pady=30)
    
    def _mostrar_imagen_marca(self, parent_frame: ttk.Frame, row: int):
        """Intenta mostrar la imagen de marca Ares.jpeg."""
        rutas_imagen = [
            Path(__file__).parent.parent.parent / "recursos" / "Ares.ppm",
            Path(__file__).parent.parent.parent / "recursos" / "Ares.gif",
            Path(__file__).parent.parent.parent / "recursos" / "Ares.jpeg"
        ]
        
        for ruta_imagen in rutas_imagen:
            try:
                if ruta_imagen.exists():
                    self.imagen_marca = tk.PhotoImage(file=str(ruta_imagen))
                    ttk.Label(parent_frame, image=self.imagen_marca).grid(
                        row=row, column=0, pady=15, sticky="n")
                    self.logger.info(f"Imagen de marca cargada: {ruta_imagen}")
                    return
            except tk.TclError as e:
                self.logger.warning(f"No se pudo cargar imagen {ruta_imagen}: {e}")
        
        # Placeholder si no se puede cargar la imagen
        ttk.Label(parent_frame, text="[Logo de Ares Aegis]", 
                 style='Subtitulo.TLabel').grid(row=row, column=0, pady=15, sticky="n")
        self.logger.warning("Usando placeholder para imagen de marca")
    
    def mostrar_menu_analisis_archivos(self):
        """Muestra el menú de detección y análisis de archivos."""
        self.limpiar_interfaz()
        self.ventana_maestra.title("Ares Aegis: Detección y Análisis de Archivos")
        
        frame_principal = ttk.Frame(self.ventana_maestra, padding="20")
        frame_principal.pack(expand=True, fill='both')
        
        # Configurar grid
        frame_principal.columnconfigure(0, weight=1)
        frame_principal.rowconfigure(2, weight=1)  # Área de resultados expandible
        
        # Título
        ttk.Label(frame_principal, text="🔍 Detección y Análisis de Archivos", 
                 style='Titulo.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Frame de controles
        frame_controles = ttk.Frame(frame_principal, style='Card.TFrame', padding="20")
        frame_controles.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        frame_controles.columnconfigure(1, weight=1)
        
        # Entrada de ruta
        ttk.Label(frame_controles, text="Ruta del Archivo/Directorio:", 
                 style='CardTitle.TLabel').grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.entrada_ruta_analisis = ttk.Entry(frame_controles, width=80)
        self.entrada_ruta_analisis.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        # Botones de selección
        frame_seleccion = ttk.Frame(frame_controles)
        frame_seleccion.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(frame_seleccion, text="Seleccionar Archivo", 
                  command=self._seleccionar_archivo,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_seleccion, text="Seleccionar Directorio", 
                  command=self._seleccionar_directorio,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        
        # Botones de acción
        frame_acciones = ttk.Frame(frame_controles)
        frame_acciones.grid(row=2, column=0, columnspan=2, pady=15)
        
        ttk.Button(frame_acciones, text="🔍 Escanear Archivo (Interno)", 
                  command=self._escanear_archivo_interno).pack(pady=3, fill=tk.X)
        
        ttk.Button(frame_acciones, text="📁 Escanear Directorio (Interno)", 
                  command=self._escanear_directorio_interno).pack(pady=3, fill=tk.X)
        
        ttk.Button(frame_acciones, text="🦠 Escanear con ClamAV", 
                  command=self._escanear_con_clamav).pack(pady=3, fill=tk.X)
        
        # Área de resultados
        ttk.Label(frame_principal, text="Resultados del Análisis:", 
                 style='Subtitulo.TLabel').grid(row=3, column=0, sticky="w", padx=20, pady=(20, 5))
        
        self.area_resultados = ScrolledText(
            frame_principal, 
            wrap=tk.WORD, 
            width=120, 
            height=20,
            font=('Consolas', 10), 
            bg=COLORES["fondo_secundario"], 
            fg=COLORES["texto_oscuro"],
            relief="flat",
            borderwidth=1
        )
        self.area_resultados.grid(row=4, column=0, sticky="nsew", padx=20, pady=5)
        
        # Botones de acción inferiores
        frame_inferior = ttk.Frame(frame_principal)
        frame_inferior.grid(row=5, column=0, pady=15)
        
        ttk.Button(frame_inferior, text="📄 Exportar a Markdown", 
                  command=self._exportar_resultados_markdown,
                  style='Success.TButton').pack(side=tk.LEFT, padx=10)
        
        ttk.Button(frame_inferior, text="🔙 Volver al Menú Principal", 
                  command=self.crear_menu_principal,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=10)
    
    def mostrar_menu_monitoreo(self):
        """Muestra el menú de monitoreo de sistema."""
        self.limpiar_interfaz()
        self.ventana_maestra.title("Ares Aegis: Monitoreo de Sistema")
        
        frame_principal = ttk.Frame(self.ventana_maestra, padding="20")
        frame_principal.pack(expand=True, fill='both')
        
        frame_principal.columnconfigure(0, weight=1)
        frame_principal.rowconfigure(2, weight=1)
        
        # Título
        ttk.Label(frame_principal, text="📊 Monitoreo de Sistema y Procesos", 
                 style='Titulo.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Frame de controles FIM
        frame_fim = ttk.Frame(frame_principal, style='Card.TFrame', padding="20")
        frame_fim.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        frame_fim.columnconfigure(0, weight=1)
        
        ttk.Label(frame_fim, text="🛡️ Monitoreo de Integridad de Archivos (FIM)", 
                 style='CardTitle.TLabel').grid(row=0, column=0, pady=(0, 10))
        
        frame_botones_fim = ttk.Frame(frame_fim)
        frame_botones_fim.grid(row=1, column=0)
        
        ttk.Button(frame_botones_fim, text="Crear Línea Base", 
                  command=self._crear_baseline_fim).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botones_fim, text="Verificar Integridad", 
                  command=self._verificar_integridad_fim).pack(side=tk.LEFT, padx=5)
        
        # Frame de controles de procesos
        if MODULOS_MONITOREO_DISPONIBLES:
            frame_procesos = ttk.Frame(frame_principal, style='Card.TFrame', padding="20")
            frame_procesos.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
            frame_procesos.columnconfigure(0, weight=1)
            
            ttk.Label(frame_procesos, text="📂 Monitoreo de Procesos", 
                     style='CardTitle.TLabel').grid(row=0, column=0, pady=(0, 10))
            
            frame_botones_procesos = ttk.Frame(frame_procesos)
            frame_botones_procesos.grid(row=1, column=0)
            
            ttk.Button(frame_botones_procesos, text="Iniciar Monitoreo de Procesos", 
                      command=self._iniciar_monitoreo_procesos).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(frame_botones_procesos, text="Detener Monitoreo de Procesos", 
                      command=self._detener_monitoreo_procesos).pack(side=tk.LEFT, padx=5)
        
        # Frame de controles de red
        if MODULOS_MONITOREO_DISPONIBLES:
            frame_red = ttk.Frame(frame_principal, style='Card.TFrame', padding="20")
            frame_red.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
            frame_red.columnconfigure(0, weight=1)
            
            ttk.Label(frame_red, text="🌐 Monitoreo de Red", 
                     style='CardTitle.TLabel').grid(row=0, column=0, pady=(0, 10))
            
            frame_botones_red = ttk.Frame(frame_red)
            frame_botones_red.grid(row=1, column=0)
            
            ttk.Button(frame_botones_red, text="Iniciar Monitoreo de Red", 
                      command=self._iniciar_monitoreo_red).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(frame_botones_red, text="Detener Monitoreo de Red", 
                      command=self._detener_monitoreo_red).pack(side=tk.LEFT, padx=5)
        
        # Área de resultados para monitoreo
        ttk.Label(frame_principal, text="Resultados del Monitoreo:", 
                 style='Subtitulo.TLabel').grid(row=4, column=0, sticky="w", padx=20, pady=(20, 5))
        
        self.area_resultados = ScrolledText(
            frame_principal, 
            wrap=tk.WORD, 
            width=120, 
            height=20,
            font=('Consolas', 10), 
            bg=COLORES["fondo_secundario"], 
            fg=COLORES["texto_oscuro"],
            relief="flat",
            borderwidth=1
        )
        self.area_resultados.grid(row=5, column=0, sticky="nsew", padx=20, pady=5)
        
        # Botones inferiores
        frame_inferior = ttk.Frame(frame_principal)
        frame_inferior.grid(row=6, column=0, pady=15)
        
        ttk.Button(frame_inferior, text="📄 Exportar Log SIEM", 
                  command=self._exportar_log_siem,
                  style='Success.TButton').pack(side=tk.LEFT, padx=10)
        
        ttk.Button(frame_inferior, text="🔙 Volver al Menú Principal", 
                  command=self.crear_menu_principal,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=10)
    
    def mostrar_menu_logs_cuarentena(self):
        """Muestra el menú de gestión de logs y cuarentena."""
        self.limpiar_interfaz()
        self.ventana_maestra.title("Ares Aegis: Gestión de Registros y Cuarentena")
        
        frame_principal = ttk.Frame(self.ventana_maestra, padding="20")
        frame_principal.pack(expand=True, fill='both')
        
        frame_principal.columnconfigure(0, weight=1)
        frame_principal.rowconfigure(2, weight=1)
        
        # Título
        ttk.Label(frame_principal, text="🗂️ Gestión de Registros y Cuarentena", 
                 style='Titulo.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Frame de controles de cuarentena
        frame_cuarentena = ttk.Frame(frame_principal, style='Card.TFrame', padding="20")
        frame_cuarentena.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        frame_cuarentena.columnconfigure(0, weight=1)
        
        ttk.Label(frame_cuarentena, text="🚨 Gestión de Cuarentena", 
                 style='CardTitle.TLabel').grid(row=0, column=0, pady=(0, 10))
        
        frame_botones_cuarentena = ttk.Frame(frame_cuarentena)
        frame_botones_cuarentena.grid(row=1, column=0)
        
        ttk.Button(frame_botones_cuarentena, text="Listar Archivos en Cuarentena", 
                  command=self._listar_cuarentena).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botones_cuarentena, text="Limpiar Cuarentena Antigua", 
                  command=self._limpiar_cuarentena_antigua,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        
        # Área de resultados
        ttk.Label(frame_principal, text="Información de Cuarentena:", 
                 style='Subtitulo.TLabel').grid(row=3, column=0, sticky="w", padx=20, pady=(20, 5))
        
        self.area_resultados = ScrolledText(
            frame_principal, 
            wrap=tk.WORD, 
            width=120, 
            height=20,
            font=('Consolas', 10), 
            bg=COLORES["fondo_secundario"], 
            fg=COLORES["texto_oscuro"],
            relief="flat",
            borderwidth=1
        )
        self.area_resultados.grid(row=4, column=0, sticky="nsew", padx=20, pady=5)
        
        # Botones inferiores
        frame_inferior = ttk.Frame(frame_principal)
        frame_inferior.grid(row=5, column=0, pady=15)
        
        ttk.Button(frame_inferior, text="🔙 Volver al Menú Principal", 
                  command=self.crear_menu_principal,
                  style='Secondary.TButton').pack()
    
    def mostrar_menu_herramientas(self):
        """Muestra el menú de herramientas del sistema."""
        self.limpiar_interfaz()
        self.ventana_maestra.title("Ares Aegis: Herramientas del Sistema")
        
        frame_principal = ttk.Frame(self.ventana_maestra, padding="20")
        frame_principal.pack(expand=True, fill='both')
        
        frame_principal.columnconfigure(0, weight=1)
        frame_principal.rowconfigure(2, weight=1)
        
        # Título
        ttk.Label(frame_principal, text="🛠️ Herramientas del Sistema", 
                 style='Titulo.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Frame de herramientas externas
        frame_herramientas = ttk.Frame(frame_principal, style='Card.TFrame', padding="20")
        frame_herramientas.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        frame_herramientas.columnconfigure(0, weight=1)
        
        ttk.Label(frame_herramientas, text="🔧 Herramientas Externas", 
                 style='CardTitle.TLabel').grid(row=0, column=0, pady=(0, 10))
        
        frame_botones_herramientas = ttk.Frame(frame_herramientas)
        frame_botones_herramientas.grid(row=1, column=0)
        
        ttk.Button(frame_botones_herramientas, text="Verificar Herramientas Disponibles", 
                  command=self._verificar_herramientas).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botones_herramientas, text="Actualizar ClamAV", 
                  command=self._actualizar_clamav).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botones_herramientas, text="Analizar Logs del Sistema", 
                  command=self._analizar_logs_sistema).pack(side=tk.LEFT, padx=5)
        
        # Área de resultados
        ttk.Label(frame_principal, text="Estado de Herramientas:", 
                 style='Subtitulo.TLabel').grid(row=3, column=0, sticky="w", padx=20, pady=(20, 5))
        
        self.area_resultados = ScrolledText(
            frame_principal, 
            wrap=tk.WORD, 
            width=120, 
            height=20,
            font=('Consolas', 10), 
            bg=COLORES["fondo_secundario"], 
            fg=COLORES["texto_oscuro"],
            relief="flat",
            borderwidth=1
        )
        self.area_resultados.grid(row=4, column=0, sticky="nsew", padx=20, pady=5)
        
        # Botones inferiores
        frame_inferior = ttk.Frame(frame_principal)
        frame_inferior.grid(row=5, column=0, pady=15)
        
        ttk.Button(frame_inferior, text="🔙 Volver al Menú Principal", 
                  command=self.crear_menu_principal,
                  style='Secondary.TButton').pack()
    
    # === MÉTODOS DE ACCIÓN ===
    
    def _seleccionar_archivo(self):
        """Abre diálogo para seleccionar archivo."""
        ruta = filedialog.askopenfilename(title="Seleccionar archivo para análisis")
        if ruta and self.entrada_ruta_analisis:
            self.entrada_ruta_analisis.delete(0, tk.END)
            self.entrada_ruta_analisis.insert(0, ruta)
            self.siem.log_evento(TipoEvento.GUI_ACCION, f"Archivo seleccionado: {ruta}")
    
    def _seleccionar_directorio(self):
        """Abre diálogo para seleccionar directorio."""
        ruta = filedialog.askdirectory(title="Seleccionar directorio para análisis")
        if ruta and self.entrada_ruta_analisis:
            self.entrada_ruta_analisis.delete(0, tk.END)
            self.entrada_ruta_analisis.insert(0, ruta)
            self.siem.log_evento(TipoEvento.GUI_ACCION, f"Directorio seleccionado: {ruta}")
    
    def _escanear_archivo_interno(self):
        """Escanea un archivo con el motor interno."""
        if not self.entrada_ruta_analisis:
            return
        
        ruta = self.entrada_ruta_analisis.get().strip()
        if not ruta:
            messagebox.showerror("Error", "Por favor, ingrese una ruta de archivo.")
            return
        
        try:
            self._actualizar_area_resultados("🔍 Iniciando escaneo interno del archivo...\\n")
            resultado = self.escaneador.escanear_archivo(ruta)
            
            markdown_resultado = resultado.to_markdown()
            self._actualizar_area_resultados(markdown_resultado)
            
            if not resultado.limpio:
                messagebox.showwarning("Amenaza Detectada", 
                                     f"Se detectaron {len(resultado.amenazas)} amenaza(s) en el archivo.")
            
        except Exception as e:
            self._mostrar_error("Error de Escaneo", f"Error escaneando archivo: {e}")
    
    def _escanear_directorio_interno(self):
        """Escanea un directorio con el motor interno."""
        if not self.entrada_ruta_analisis:
            return
        
        ruta = self.entrada_ruta_analisis.get().strip()
        if not ruta:
            messagebox.showerror("Error", "Por favor, ingrese una ruta de directorio.")
            return
        
        try:
            self._actualizar_area_resultados("📁 Iniciando escaneo interno del directorio...\\n")
            resultados = self.escaneador.escanear_directorio(ruta)
            
            markdown_resultado = self.escaneador.generar_reporte_markdown(resultados)
            self._actualizar_area_resultados(markdown_resultado)
            
            if resultados['amenazas_encontradas'] > 0:
                messagebox.showwarning("Amenazas Detectadas", 
                                     f"Se detectaron {resultados['amenazas_encontradas']} amenaza(s) en el directorio.")
            
        except Exception as e:
            self._mostrar_error("Error de Escaneo", f"Error escaneando directorio: {e}")
    
    def _escanear_con_clamav(self):
        """Escanea con ClamAV."""
        if not self.entrada_ruta_analisis:
            return
        
        ruta = self.entrada_ruta_analisis.get().strip()
        if not ruta:
            messagebox.showerror("Error", "Por favor, ingrese una ruta.")
            return
        
        try:
            self._actualizar_area_resultados("🦠 Iniciando escaneo con ClamAV...\\n")
            
            if os.path.isfile(ruta):
                resultado = self.integracion_externa.clamav.escanear_archivo(ruta)
            elif os.path.isdir(ruta):
                resultado = self.integracion_externa.clamav.escanear_directorio(ruta)
            else:
                messagebox.showerror("Error", "La ruta especificada no existe.")
                return
            
            markdown_resultado = resultado.to_markdown()
            self._actualizar_area_resultados(markdown_resultado)
            
        except Exception as e:
            self._mostrar_error("Error de ClamAV", f"Error ejecutando ClamAV: {e}")
    
    def _crear_baseline_fim(self):
        """Crea una nueva línea base FIM."""
        directorio = filedialog.askdirectory(title="Seleccionar directorio para monitorear")
        if not directorio:
            return
        
        try:
            self._actualizar_area_resultados("🛡️ Creando línea base de integridad...\\n")
            estadisticas = self.fim.crear_baseline([directorio], incluir_criticos=True)
            
            resultado = f"✅ Línea base creada exitosamente\\n"
            resultado += f"📊 Archivos procesados: {estadisticas['archivos_procesados']}\\n"
            resultado += f"📁 Directorios monitoreados: {estadisticas['directorios_monitoreados']}\\n"
            resultado += f"⚠️ Errores: {estadisticas['errores']}\\n\\n"
            
            self._actualizar_area_resultados(resultado)
            
        except Exception as e:
            self._mostrar_error("Error FIM", f"Error creando línea base: {e}")
    
    def _verificar_integridad_fim(self):
        """Verifica la integridad de archivos."""
        try:
            self._actualizar_area_resultados("🔍 Verificando integridad de archivos...\\n")
            cambios = self.fim.verificar_integridad()
            
            if not cambios:
                self._actualizar_area_resultados("✅ No se detectaron cambios en la integridad.\\n\\n")
            else:
                reporte = self.fim.generar_reporte_markdown(cambios)
                self._actualizar_area_resultados(reporte)
                
                messagebox.showwarning("Cambios Detectados", 
                                     f"Se detectaron {len(cambios)} cambio(s) en los archivos monitoreados.")
            
        except Exception as e:
            self._mostrar_error("Error FIM", f"Error verificando integridad: {e}")
    
    def _listar_cuarentena(self):
        """Lista archivos en cuarentena."""
        try:
            self._actualizar_area_resultados("🗂️ Listando archivos en cuarentena...\\n")
            reporte = self.gestor_cuarentena.generar_reporte_markdown()
            self._actualizar_area_resultados(reporte)
            
        except Exception as e:
            self._mostrar_error("Error de Cuarentena", f"Error listando cuarentena: {e}")
    
    def _limpiar_cuarentena_antigua(self):
        """Limpia archivos antiguos de la cuarentena."""
        dias = simpledialog.askinteger("Limpiar Cuarentena", 
                                      "¿Archivos más antiguos de cuántos días eliminar?",
                                      initialvalue=30, minvalue=1, maxvalue=365)
        if not dias:
            return
        
        if not messagebox.askyesno("Confirmar", 
                                  f"¿Está seguro de eliminar archivos en cuarentena más antiguos de {dias} días?"):
            return
        
        try:
            eliminados = self.gestor_cuarentena.limpiar_cuarentena_antigua(dias)
            mensaje = f"✅ Se eliminaron {eliminados} archivo(s) de la cuarentena.\\n\\n"
            self._actualizar_area_resultados(mensaje)
            
        except Exception as e:
            self._mostrar_error("Error de Cuarentena", f"Error limpiando cuarentena: {e}")
    
    def _verificar_herramientas(self):
        """Verifica herramientas externas disponibles."""
        try:
            self._actualizar_area_resultados("🔧 Verificando herramientas disponibles...\\n")
            reporte = self.integracion_externa.generar_reporte_herramientas_disponibles()
            self._actualizar_area_resultados(reporte)
            
        except Exception as e:
            self._mostrar_error("Error de Herramientas", f"Error verificando herramientas: {e}")
    
    def _actualizar_clamav(self):
        """Actualiza la base de datos de ClamAV."""
        try:
            self._actualizar_area_resultados("🦠 Actualizando base de datos de ClamAV...\\n")
            resultado = self.integracion_externa.clamav.actualizar_base_datos()
            
            markdown_resultado = resultado.to_markdown()
            self._actualizar_area_resultados(markdown_resultado)
            
        except Exception as e:
            self._mostrar_error("Error de ClamAV", f"Error actualizando ClamAV: {e}")
    
    def _exportar_resultados_markdown(self):
        """Exporta los resultados actuales a un archivo Markdown."""
        if not self.area_resultados:
            return
        
        contenido = self.area_resultados.get(1.0, tk.END).strip()
        if not contenido:
            messagebox.showinfo("Exportar", "No hay contenido para exportar.")
            return
        
        self._exportar_a_markdown(contenido, "Reporte de Análisis de Ares Aegis")
    
    def _exportar_log_siem(self):
        """Exporta el log del SIEM a Markdown."""
        try:
            contenido = self.siem.obtener_eventos_markdown(limite=100)
            self._exportar_a_markdown(contenido, "Log de Eventos del SIEM")
        except Exception as e:
            self._mostrar_error("Error de Exportación", f"Error exportando log SIEM: {e}")
    
    def _exportar_a_markdown(self, contenido: str, titulo: str):
        """Exporta contenido a un archivo Markdown."""
        ruta_guardar = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Archivos Markdown", "*.md"), ("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Guardar informe Markdown"
        )
        
        if not ruta_guardar:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            informe_markdown = f"# {titulo}\\n\\n"
            informe_markdown += f"**Fecha de Generación:** {timestamp}\\n"
            informe_markdown += f"**Generado por:** Ares Aegis v2.0\\n\\n"
            informe_markdown += "---\\n\\n"
            informe_markdown += contenido;
            
            with open(ruta_guardar, "w", encoding="utf-8") as f:
                f.write(informe_markdown)
            
            messagebox.showinfo("Exportación Exitosa", f"Informe guardado en:\\n{ruta_guardar}")
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, f"Informe Markdown exportado: {ruta_guardar}")
            
        except Exception as e:
            self._mostrar_error("Error de Exportación", f"No se pudo guardar el informe: {e}")
    
    # === MÉTODOS AUXILIARES ===
    
    def _actualizar_area_resultados(self, texto: str):
        """Actualiza el área de resultados con nuevo texto."""
        if self.area_resultados:
            self.area_resultados.insert(tk.END, texto + "\\n")
            self.area_resultados.see(tk.END)
    
    def _mostrar_error(self, titulo: str, mensaje: str):
        """Muestra un mensaje de error y lo registra."""
        messagebox.showerror(titulo, mensaje)
        self.siem.log_evento(TipoEvento.ERROR, f"{titulo}: {mensaje}")
    
    def _al_cerrar_aplicacion(self):
        """Maneja el cierre de la aplicación."""
        if messagebox.askyesno("Salir", "¿Está seguro de que desea salir de Ares Aegis?"):
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, "Aplicación cerrada por el usuario")
            self.ventana_maestra.quit()
            self.ventana_maestra.destroy()
    
    def _iniciar_monitoreo_procesos(self):
        """Inicia el monitoreo de procesos del sistema."""
        if not MODULOS_MONITOREO_DISPONIBLES:
            self._mostrar_error("Módulos no disponibles", "Los módulos de monitoreo no están disponibles")
            return
        
        try:
            self._actualizar_area_resultados("🔍 Iniciando monitoreo de procesos...")
            resultado = self.monitor_procesos.escanear_sistema()
            
            stats = resultado['estadisticas']
            resumen = f"""=== MONITOREO DE PROCESOS ===
Total de procesos: {stats['total_procesos']}
Procesos sospechosos: {stats['procesos_sospechosos']}
Procesos nuevos: {stats['procesos_nuevos']}
Uso promedio CPU: {stats['uso_cpu_promedio']:.2f}%
Memoria total: {stats['memoria_total_mb']:.2f} MB
Tiempo de escaneo: {stats['tiempo_escaneo']:.2f} segundos

"""
            
            self._actualizar_area_resultados(resumen)
            
            # Mostrar procesos sospechosos
            if resultado['procesos_sospechosos']:
                self._actualizar_area_resultados("🚨 PROCESOS SOSPECHOSOS DETECTADOS:")
                for proceso in resultado['procesos_sospechosos']:
                    info = f"- {proceso['nombre']} (PID: {proceso['pid']}) - {', '.join(proceso['razones_sospecha'])}"
                    self._actualizar_area_resultados(info)
                self._actualizar_area_resultados("")
            
            # Exportar reporte
            try:
                archivo_reporte = self.monitor_procesos.exportar_reporte_markdown(resultado)
                self._actualizar_area_resultados(f"📄 Reporte exportado a: {archivo_reporte}")
            except Exception as e:
                self._actualizar_area_resultados(f"Error al exportar reporte: {e}")
            
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, 'Monitoreo de procesos completado')
            
        except Exception as e:
            self._mostrar_error("Error de Monitoreo", f"Error en monitoreo de procesos: {e}")
    
    def _detener_monitoreo_procesos(self):
        """Detiene el monitoreo de procesos (placeholder)."""
        self._actualizar_area_resultados("Monitoreo de procesos detenido.")
        self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, 'Monitoreo de procesos detenido')
    
    def _iniciar_monitoreo_red(self):
        """Inicia el monitoreo de red del sistema."""
        if not MODULOS_MONITOREO_DISPONIBLES:
            self._mostrar_error("Módulos no disponibles", "Los módulos de monitoreo no están disponibles")
            return
        
        try:
            self._actualizar_area_resultados("🌐 Iniciando monitoreo de red...")
            resultado = self.monitor_red.escanear_sistema_red()
            
            stats = resultado['estadisticas']
            resumen = f"""=== MONITOREO DE RED ===
Total de conexiones: {stats['total_conexiones']}
Conexiones sospechosas: {stats['conexiones_sospechosas']}
Puertos abiertos: {stats['total_puertos_abiertos']}
Puertos sospechosos: {stats['puertos_sospechosos']}
Dispositivos en red: {stats['dispositivos_en_red']}
Tiempo de escaneo: {stats['tiempo_escaneo']:.2f} segundos

"""
            
            self._actualizar_area_resultados(resumen)
            
            # Mostrar conexiones sospechosas
            if resultado['conexiones_sospechosas']:
                self._actualizar_area_resultados("🚨 CONEXIONES SOSPECHOSAS:")
                for conexion in resultado['conexiones_sospechosas']:
                    local = f"{conexion['direccion_local']}:{conexion['puerto_local']}"
                    remoto = f"{conexion['direccion_remota']}:{conexion['puerto_remoto']}" if conexion['direccion_remota'] else 'N/A'
                    info = f"- {conexion['protocolo']} {local} -> {remoto} ({', '.join(conexion['razones_sospecha'])})"
                    self._actualizar_area_resultados(info)
                self._actualizar_area_resultados("")
            
            # Mostrar puertos sospechosos
            if resultado['puertos_sospechosos']:
                self._actualizar_area_resultados("🚨 PUERTOS SOSPECHOSOS:")
                for puerto in resultado['puertos_sospechosos']:
                    info = f"- Puerto {puerto['puerto']}/{puerto['protocolo']} ({puerto['servicio']}) - {', '.join(puerto['razones_sospecha'])}"
                    self._actualizar_area_resultados(info)
                self._actualizar_area_resultados("")
            
            # Exportar reporte
            try:
                archivo_reporte = self.monitor_red.exportar_reporte_markdown(resultado)
                self._actualizar_area_resultados(f"📄 Reporte exportado a: {archivo_reporte}")
            except Exception as e:
                self._actualizar_area_resultados(f"Error al exportar reporte: {e}")
            
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, 'Monitoreo de red completado')
            
        except Exception as e:
            self._mostrar_error("Error de Monitoreo", f"Error en monitoreo de red: {e}")
    
    def _detener_monitoreo_red(self):
        """Detiene el monitoreo de red (placeholder)."""
        self._actualizar_area_resultados("Monitoreo de red detenido.")
        self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, 'Monitoreo de red detenido')
    
    def _analizar_logs_sistema(self):
        """Analiza los logs del sistema."""
        if not MODULOS_MONITOREO_DISPONIBLES:
            self._mostrar_error("Módulos no disponibles", "Los módulos de monitoreo no están disponibles")
            return
        
        try:
            # Preguntar período de análisis
            horas = simpledialog.askinteger(
                "Análisis de Logs",
                "¿Cuántas horas hacia atrás analizar?",
                initialvalue=24,
                minvalue=1,
                maxvalue=168  # Una semana máximo
            )
            
            if not horas:
                return
            
            self._actualizar_area_resultados(f"Analizando logs de las últimas {horas} horas...")
            
            # Realizar análisis
            resultado = self.analizador_logs.analizar_periodo(horas_atras=horas)
            
            # Mostrar resultados
            stats = resultado['estadisticas']
            resumen = f"""=== ANÁLISIS DE LOGS DEL SISTEMA ===
Período analizado: {horas} horas
Total de eventos: {stats['total_eventos']:,}
Eventos sospechosos: {stats['eventos_sospechosos']}
Ataques detectados: {stats['ataques_brute_force']}
Archivos procesados: {stats['archivos_procesados']}
Tiempo de procesamiento: {stats['tiempo_procesamiento']:.2f} segundos

"""
            
            self._actualizar_area_resultados(resumen)
            
            # Mostrar ataques detectados
            if resultado['ataques_detectados']:
                self._actualizar_area_resultados("🚨 ATAQUES DETECTADOS:")
                for ataque in resultado['ataques_detectados']:
                    info = f"- Fuerza bruta desde {ataque['ip_origen']}: {ataque['intentos_totales']} intentos en {ataque['duracion_segundos']:.0f} segundos"
                    self._actualizar_area_resultados(info)
                self._actualizar_area_resultados("")
            
            # Mostrar eventos sospechosos (primeros 10)
            if resultado['eventos_sospechosos']:
                self._actualizar_area_resultados("⚠️ EVENTOS SOSPECHOSOS (primeros 10):")
                for i, evento in enumerate(resultado['eventos_sospechosos'][:10]):
                    info = f"{i+1}. {evento['timestamp']}: {evento['mensaje'][:80]}..."
                    self._actualizar_area_resultados(info)
                
                if len(resultado['eventos_sospechosos']) > 10:
                    self._actualizar_area_resultados(f"... y {len(resultado['eventos_sospechosos']) - 10} eventos más.")
                self._actualizar_area_resultados("")
            
            # Exportar reporte
            try:
                archivo_reporte = self.analizador_logs.exportar_reporte_markdown(resultado)
                self._actualizar_area_resultados(f"📄 Reporte exportado a: {archivo_reporte}")
            except Exception as e:
                self._actualizar_area_resultados(f"Error al exportar reporte: {e}")
            
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, f'Análisis de logs completado ({horas} horas)')
            
        except Exception as e:
            self._mostrar_error("Error de Análisis", f"Error en análisis de logs: {e}")
