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

# Añadir path para importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importar modelos
from modelos.siem import SIEM, TipoEvento
from modelos.escaneador import Escaneador
from modelos.fim import FIM
from modelos.cuarentena import GestorCuarentena
from modelos.integracion_externa import IntegracionExterna

# Importar los nuevos módulos de monitoreo
try:
    from modelos.monitor_red import MonitorRed
    MODULOS_MONITOREO_DISPONIBLES = True
except ImportError:
    MonitorRed = None
    MODULOS_MONITOREO_DISPONIBLES = False


# Paleta de colores suaves y cálidos inspirada en el estilo japonés
COLORES = {
    "fondo_principal": "#F5F5DC",        # Beige suave, como papel de arroz
    "fondo_secundario": "#EFEBE9",       # Crema claro
    "fondo_tarjeta": "#FFF8E1",          # Amarillo muy pálido
    "borde_sutil": "#D7CCC8",            # Marrón muy claro, casi gris
    "texto_oscuro": "#3E2723",           # Marrón muy oscuro, casi negro suave
    "texto_claro": "#795548",            # Marrón medio
    "texto_secundario": "#8D6E63",       # Marrón claro
    "boton_normal": "#BCAAA4",           # Gris cálido con toque marrón
    "boton_activo": "#A1887F",           # Gris marrón más oscuro
    "boton_info": "#81C784",             # Verde suave (matcha claro)
    "boton_info_activo": "#66BB6A",      # Verde matcha más intenso
    "boton_peligro": "#FFAB91",          # Naranja suave (atardecer)
    "boton_peligro_activo": "#FF8A65",   # Naranja más intenso
    "boton_exito": "#A5D6A7",            # Verde menta suave
    "boton_exito_activo": "#81C784",     # Verde menta activo
    "resaltado_entrada": "#FFF3E0",      # Crema para campos de entrada
    "sombra": "#E0E0E0"                  # Gris muy claro para sombras
}


class InterfazPrincipalGUI:
    """Interfaz gráfica principal de Ares Aegis."""

    def __init__(self, ventana_maestra: tk.Tk, controlador=None):
        """
        Inicializa la interfaz principal.

        Args:
            ventana_maestra: Ventana principal de tkinter
            controlador: Controlador principal (opcional)
        """
        self.ventana_maestra = ventana_maestra
        self.controlador = controlador
        self.logger = logging.getLogger(__name__)

        # Modo de privilegios ('root' o 'limitado')
        self.modo_privilegios = 'limitado'  # Por defecto modo limitado

        # Configurar ventana principal
        self._configurar_ventana_principal()

        # Inicializar backend (inyección de dependencias)
        self._inicializar_backend()

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

        # Intentar cargar la imagen principal de marca
        self._cargar_imagen_principal()

        # Configurar comportamiento de cierre
        self.ventana_maestra.protocol("WM_DELETE_WINDOW", self._al_cerrar_aplicacion)

    def _cargar_icono_aplicacion(self):
        """Intenta cargar el icono de la aplicación."""
        # Usar un icono simple interno si no hay archivos externos
        try:
            # Intentar primero con archivos externos
            rutas_icono = [
                Path(__file__).parent.parent.parent / "recursos" / "aresIcon.ppm",
                Path(__file__).parent.parent.parent / "recursos" / "aresIcon.gif"
            ]

            for ruta_icono in rutas_icono:
                if ruta_icono.exists():
                    self.icono_app = tk.PhotoImage(file=str(ruta_icono))
                    self.ventana_maestra.iconphoto(True, self.icono_app)
                    self.logger.info(f"Icono cargado: {ruta_icono}")
                    return

            # Si no hay archivos externos, crear un icono simple
            self.logger.info("Usando icono por defecto del sistema")

        except tk.TclError as e:
            self.logger.info(f"Usando configuración de icono por defecto: {e}")
        except Exception as e:
            self.logger.info(f"Configuración de icono omitida: {e}")

    def _cargar_imagen_principal(self):
        """Intenta cargar la imagen principal de marca Ares Aegis."""
        rutas_imagen = [
            Path(__file__).parent.parent.parent / "recursos" / "AresAegis.ppm",
            Path(__file__).parent.parent.parent / "recursos" / "AresAegis.gif",
            Path(__file__).parent.parent.parent / "recursos" / "AresAegis.png"
        ]

        self.imagen_principal = None
        for ruta_imagen in rutas_imagen:
            try:
                if ruta_imagen.exists():
                    self.imagen_principal = tk.PhotoImage(file=str(ruta_imagen))
                    self.logger.info(f"Imagen principal cargada: {ruta_imagen}")
                    return
            except tk.TclError as e:
                self.logger.warning(f"No se pudo cargar imagen {ruta_imagen}: {e}")

        self.logger.info("Imagen principal no disponible - continuando sin imagen de marca")

    def _inicializar_backend(self):
        """Inicializa los módulos del backend con inyección de dependencias."""
        try:
            # Inicializar SIEM como dependencia central
            self.siem = SIEM()

            # Inicializar módulos pasando el SIEM y configuraciones correctas
            self.escaneador = Escaneador(self.siem)
            self.fim = FIM(self.siem)
            self.gestor_cuarentena = GestorCuarentena(None, self.siem)  # directorio por defecto
            self.integracion_externa = IntegracionExterna(self.siem)

            # Inicializar módulos de monitoreo si están disponibles
            if MODULOS_MONITOREO_DISPONIBLES and MonitorRed is not None:
                self.monitor_red = MonitorRed(self.siem)
            else:
                self.monitor_red = None

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

        # Configurar grid con mejor distribución para la imagen
        frame_principal.columnconfigure(0, weight=1)
        frame_principal.rowconfigure(0, weight=0)  # Título fijo
        frame_principal.rowconfigure(1, weight=0)  # Subtítulo fijo
        frame_principal.rowconfigure(2, weight=0)  # Estado privilegios fijo
        frame_principal.rowconfigure(3, weight=0)  # Imagen fija
        frame_principal.rowconfigure(4, weight=1)  # Espaciador flexible
        frame_principal.rowconfigure(5, weight=0)  # Botones fijos
        frame_principal.rowconfigure(6, weight=0)  # Botón salir fijo

        # Título principal
        ttk.Label(frame_principal, text="Ares Aegis",
                 style='Titulo.TLabel').grid(row=0, column=0, pady=(0, 5), sticky="n")

        ttk.Label(frame_principal, text="Antivirus Avanzado para Kali Linux",
                 style='Subtitulo.TLabel').grid(row=1, column=0, pady=(0, 5), sticky="n")

        # Indicador de estado de privilegios
        estado_privilegios = "🔐 Modo Administrador" if self.modo_privilegios == 'root' else "⚠️ Modo Limitado"
        color_privilegios = COLORES["boton_exito"] if self.modo_privilegios == 'root' else COLORES["boton_peligro"]

        label_privilegios = ttk.Label(frame_principal, text=estado_privilegios,
                                    style='Privilegios.TLabel')
        label_privilegios.grid(row=2, column=0, pady=(0, 15), sticky="n")

        # Cargar y mostrar imagen de marca con ajuste de tamaño
        self._mostrar_imagen_marca(frame_principal, row=3)

        # Frame para botones de categorías
        frame_botones = ttk.Frame(frame_principal, style='Card.TFrame', padding="25")
        frame_botones.grid(row=5, column=0, pady=20, sticky="ew", padx=50)
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
                  style='Danger.TButton').grid(row=5, column=0, pady=30)

    def _mostrar_imagen_marca(self, parent_frame: ttk.Frame, row: int):
        """Intenta mostrar la imagen principal de marca AresAegis.png con ajuste de tamaño."""
        # Primero intentar usar la imagen ya cargada en la inicialización
        if hasattr(self, 'imagen_principal') and self.imagen_principal:
            try:
                # Crear frame contenedor para la imagen con un tamaño controlado
                frame_imagen = ttk.Frame(parent_frame)
                frame_imagen.grid(row=row, column=0, pady=15, sticky="n")

                # Ajustar el tamaño de la imagen si es necesario
                imagen_ajustada = self._ajustar_tamaño_imagen(self.imagen_principal, max_width=300, max_height=200)

                label_imagen = ttk.Label(frame_imagen, image=imagen_ajustada)
                label_imagen.pack()

                # Mantener referencia para evitar garbage collection
                self.imagen_marca_mostrada = imagen_ajustada

                self.logger.info("Imagen principal mostrada con ajuste de tamaño")
                return
            except Exception as e:
                self.logger.warning(f"Error ajustando imagen principal: {e}")

        # Si no está en cache, intentar cargar directamente
        rutas_imagen = [
            Path(__file__).parent.parent.parent / "recursos" / "AresAegis.ppm",
            Path(__file__).parent.parent.parent / "recursos" / "AresAegis.gif",
            Path(__file__).parent.parent.parent / "recursos" / "AresAegis.png",
            # Mantener compatibilidad con nombres antiguos
            Path(__file__).parent.parent.parent / "recursos" / "Ares.ppm",
            Path(__file__).parent.parent.parent / "recursos" / "Ares.gif",
            Path(__file__).parent.parent.parent / "recursos" / "Ares.jpeg"
        ]

        for ruta_imagen in rutas_imagen:
            try:
                if ruta_imagen.exists():
                    imagen_temp = tk.PhotoImage(file=str(ruta_imagen))

                    # Crear frame contenedor
                    frame_imagen = ttk.Frame(parent_frame)
                    frame_imagen.grid(row=row, column=0, pady=15, sticky="n")

                    # Ajustar tamaño
                    imagen_ajustada = self._ajustar_tamaño_imagen(imagen_temp, max_width=300, max_height=200)

                    label_imagen = ttk.Label(frame_imagen, image=imagen_ajustada)
                    label_imagen.pack()

                    # Mantener referencia
                    self.imagen_marca_mostrada = imagen_ajustada

                    self.logger.info(f"Imagen de marca cargada y ajustada: {ruta_imagen}")
                    return
            except tk.TclError as e:
                self.logger.warning(f"No se pudo cargar imagen {ruta_imagen}: {e}")

        # Placeholder mejorado si no se puede cargar ninguna imagen
        frame_placeholder = ttk.Frame(parent_frame, style='Card.TFrame', padding="20")
        frame_placeholder.grid(row=row, column=0, pady=15, sticky="n", padx=40)

        ttk.Label(frame_placeholder, text="🛡️ ARES AEGIS 🛡️",
                 style='Titulo.TLabel').pack(pady=(0, 5))
        ttk.Label(frame_placeholder, text="Protección Avanzada para Kali Linux",
                 style='Subtitulo.TLabel').pack()
        ttk.Label(frame_placeholder, text="[Imagen no disponible - usando placeholder]",
                 font=('Helvetica', 8, 'italic'),
                 foreground=COLORES["texto_secundario"],
                 background=COLORES["fondo_tarjeta"]).pack(pady=(5, 0))

        self.logger.info("Usando placeholder textual mejorado para imagen de marca")

    def _ajustar_tamaño_imagen(self, imagen: tk.PhotoImage, max_width: int = 300, max_height: int = 200) -> tk.PhotoImage:
        """
        Ajusta el tamaño de una imagen PhotoImage manteniendo la proporción.

        Args:
            imagen: La imagen PhotoImage original
            max_width: Ancho máximo deseado
            max_height: Alto máximo deseado

        Returns:
            PhotoImage redimensionada
        """
        try:
            # Obtener dimensiones actuales
            width_actual = imagen.width()
            height_actual = imagen.height()

            # Si la imagen ya es más pequeña que los límites, devolverla tal como está
            if width_actual <= max_width and height_actual <= max_height:
                return imagen

            # Calcular factor de escala manteniendo proporción
            scale_w = max_width / width_actual
            scale_h = max_height / height_actual
            scale = min(scale_w, scale_h)

            # Calcular factor de subsample (debe ser entero >= 1)
            factor_sub = max(1, int(1 / scale))

            # Aplicar subsample para reducir el tamaño
            try:
                imagen_redimensionada = imagen.subsample(factor_sub)
                self.logger.debug(f"Imagen redimensionada de {width_actual}x{height_actual} a {imagen_redimensionada.width()}x{imagen_redimensionada.height()} (factor: {factor_sub})")
                return imagen_redimensionada
            except Exception as sub_error:
                self.logger.warning(f"Error aplicando subsample: {sub_error}")
                return imagen

        except Exception as e:
            self.logger.warning(f"Error redimensionando imagen: {e}, usando imagen original")
            return imagen

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
            resultados_lista = self.escaneador.escanear_directorio(ruta)

            # Convertir lista de resultados a reporte
            resultados = self.escaneador.generar_reporte_directorio(resultados_lista)
            markdown_resultado = self.escaneador.generar_reporte_markdown_directorio(resultados)
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
        self._actualizar_area_resultados("⚠️ Función de monitoreo de procesos en desarrollo")
        self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, 'Función de monitoreo de procesos solicitada')

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

            if self.monitor_red is None:
                self._actualizar_area_resultados("❌ Monitor de red no disponible")
                return

            # Obtener conexiones activas
            conexiones = self.monitor_red.obtener_conexiones_activas()
            conexiones_sospechosas = self.monitor_red.detectar_conexiones_sospechosas()
            puertos_sospechosos = self.monitor_red.detectar_puertos_en_escucha_sospechosos()
            estadisticas = self.monitor_red.obtener_estadisticas_red()

            resumen = f"""=== MONITOREO DE RED ===
Total de conexiones: {estadisticas['total_conexiones']}
Conexiones TCP: {estadisticas['conexiones_tcp']}
Conexiones UDP: {estadisticas['conexiones_udp']}
Conexiones establecidas: {estadisticas['conexiones_establecidas']}
Puertos en escucha: {estadisticas['puertos_en_escucha']}
Conexiones sospechosas: {len(conexiones_sospechosas)}
Puertos sospechosos: {len(puertos_sospechosos)}

"""

            self._actualizar_area_resultados(resumen)

            # Mostrar conexiones sospechosas
            if conexiones_sospechosas:
                self._actualizar_area_resultados("🚨 CONEXIONES SOSPECHOSAS:")
                for conexion in conexiones_sospechosas:
                    local = f"{conexion.direccion_local}:{conexion.puerto_local}"
                    remoto = f"{conexion.direccion_remota}:{conexion.puerto_remoto}" if conexion.direccion_remota else 'N/A'
                    info = f"- {conexion.protocolo} {local} -> {remoto} (Proceso: {conexion.proceso})"
                    self._actualizar_area_resultados(info)
                self._actualizar_area_resultados("")

            # Mostrar puertos sospechosos
            if puertos_sospechosos:
                self._actualizar_area_resultados("🚨 PUERTOS SOSPECHOSOS:")
                for puerto in puertos_sospechosos:
                    info = f"- Puerto {puerto.puerto_local}/{puerto.protocolo} (Proceso: {puerto.proceso})"
                    self._actualizar_area_resultados(info)
                self._actualizar_area_resultados("")

            # Generar reporte
            try:
                if self.monitor_red is not None:
                    reporte = self.monitor_red.generar_reporte_markdown(conexiones_sospechosas)
                    self._actualizar_area_resultados("📄 Reporte generado en el área de resultados")
                else:
                    self._actualizar_area_resultados("📄 Monitor de red no disponible para generar reporte")
            except Exception as e:
                self._actualizar_area_resultados(f"Error al generar reporte: {e}")

            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, 'Monitoreo de red completado')

        except Exception as e:
            self._mostrar_error("Error de Monitoreo", f"Error en monitoreo de red: {e}")

    def _detener_monitoreo_red(self):
        """Detiene el monitoreo de red (placeholder)."""
        self._actualizar_area_resultados("Monitoreo de red detenido.")
        self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, 'Monitoreo de red detenido')

    def _analizar_logs_sistema(self):
        """Analiza los logs del sistema."""
        self._actualizar_area_resultados("⚠️ Función de análisis de logs en desarrollo")
        self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, 'Función de análisis de logs solicitada')
