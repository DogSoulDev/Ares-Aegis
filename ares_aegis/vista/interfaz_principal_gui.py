#!/usr/bin/env python3
"""
Interfaz Principal GUI - Ares Aegis
Interfaz gráfica principal inspirada en Windows Defender con estética japonesa

Autor: DogSoulDev
Versión: 2.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# Importar controladores y modelos
from ..controladores.controlador_principal import ControladorPrincipal
from ..modelos.siem import TipoEvento


class TemaJapones:
    """Paleta de colores japonesa para la interfaz."""
    
    # Colores principales inspirados en la estética japonesa
    SAKURA_ROSA = "#FFB7C5"          # Rosa suave de los cerezos
    BAMBOO_VERDE = "#4A6741"         # Verde bambú
    CIELO_AZUL = "#87CEEB"           # Azul cielo japonés
    TINTA_NEGRA = "#2C2C2C"          # Negro tinta sumi
    PAPEL_BLANCO = "#F8F8FF"         # Blanco papel de arroz
    ORO_DORADO = "#FFD700"           # Dorado tradicional
    ROJO_CARMESI = "#DC143C"         # Rojo carmesí
    PLATA_GRIS = "#C0C0C0"           # Plata mate
    
    # Colores de estado
    EXITO = "#4CAF50"                # Verde éxito
    ADVERTENCIA = "#FF9800"          # Naranja advertencia  
    ERROR = "#F44336"                # Rojo error
    INFO = "#2196F3"                 # Azul información
    
    # Gradientes y sombras
    SOMBRA_SUAVE = "#E0E0E0"
    BORDE_SUTIL = "#D0D0D0"


class IconosUnicode:
    """Iconos Unicode para la interfaz."""
    
    ESCUDO = "🛡️"
    ESCANEAR = "🔍"
    CUARENTENA = "🔒"
    RED = "🌐"
    FIM = "📁"
    CONFIGURACION = "⚙️"
    HISTORIAL = "📋"
    ALERTA = "⚠️"
    CORRECTO = "✅"
    ERROR = "❌"
    PAUSA = "⏸️"
    PLAY = "▶️"
    STOP = "⏹️"
    ACTUALIZAR = "🔄"
    LIMPIAR = "🧹"
    EXPORTAR = "📤"
    INFORMACION = "ℹ️"
    VIRUS = "🦠"
    SEGURO = "🔐"


class WidgetPersonalizado:
    """Widgets personalizados con el tema japonés."""
    
    @staticmethod
    def crear_boton_principal(parent, texto, comando, ancho=15):
        """Crea un botón principal con estilo japonés."""
        boton = tk.Button(
            parent,
            text=texto,
            command=comando,
            bg=TemaJapones.BAMBOO_VERDE,
            fg=TemaJapones.PAPEL_BLANCO,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=5,
            width=ancho,
            cursor="hand2"
        )
        
        # Efectos hover
        def on_enter(e):
            boton.config(bg=TemaJapones.CIELO_AZUL)
        
        def on_leave(e):
            boton.config(bg=TemaJapones.BAMBOO_VERDE)
        
        boton.bind("<Enter>", on_enter)
        boton.bind("<Leave>", on_leave)
        
        return boton
    
    @staticmethod
    def crear_boton_secundario(parent, texto, comando, ancho=12):
        """Crea un botón secundario con estilo japonés."""
        boton = tk.Button(
            parent,
            text=texto,
            command=comando,
            bg=TemaJapones.PLATA_GRIS,
            fg=TemaJapones.TINTA_NEGRA,
            font=("Segoe UI", 9),
            relief="flat",
            borderwidth=1,
            padx=8,
            pady=3,
            width=ancho,
            cursor="hand2"
        )
        
        def on_enter(e):
            boton.config(bg=TemaJapones.SOMBRA_SUAVE)
        
        def on_leave(e):
            boton.config(bg=TemaJapones.PLATA_GRIS)
        
        boton.bind("<Enter>", on_enter)
        boton.bind("<Leave>", on_leave)
        
        return boton
    
    @staticmethod
    def crear_frame_panel(parent, titulo=""):
        """Crea un frame panel con borde sutil."""
        frame = tk.Frame(
            parent,
            bg=TemaJapones.PAPEL_BLANCO,
            relief="solid",
            borderwidth=1,
            highlightbackground=TemaJapones.BORDE_SUTIL
        )
        
        if titulo:
            label_titulo = tk.Label(
                frame,
                text=titulo,
                bg=TemaJapones.PAPEL_BLANCO,
                fg=TemaJapones.TINTA_NEGRA,
                font=("Segoe UI", 11, "bold")
            )
            label_titulo.pack(pady=(10, 5))
        
        return frame
    
    @staticmethod
    def crear_etiqueta_estado(parent, texto_inicial="", color=TemaJapones.INFO):
        """Crea una etiqueta de estado con color."""
        label = tk.Label(
            parent,
            text=texto_inicial,
            bg=TemaJapones.PAPEL_BLANCO,
            fg=color,
            font=("Segoe UI", 9),
            anchor="w"
        )
        return label


class InterfazPrincipalGUI:
    """Interfaz gráfica principal de Ares Aegis."""
    
    def __init__(self, ventana_raiz: Optional[tk.Tk] = None):
        """
        Inicializa la interfaz principal.
        
        Args:
            ventana_raiz: Ventana raíz de Tkinter (opcional)
        """
        if ventana_raiz is None:
            self.ventana = tk.Tk()
        else:
            self.ventana = ventana_raiz
            
        self.controlador: Optional[ControladorPrincipal] = None
        
        # Estado de la aplicación
        self.escaneo_activo = False
        self.monitoreo_activo = False
        
        # Variables de UI
        self.var_ruta_escaneo = tk.StringVar(value=str(Path.home()))
        self.var_progreso = tk.IntVar()
        self.var_estado_general = tk.StringVar(value="🛡️ Ares Aegis - Listo para proteger")
        
        # Widgets principales
        self.barra_progreso: Optional[ttk.Progressbar] = None
        self.texto_log: Optional[scrolledtext.ScrolledText] = None
        self.etiqueta_estado: Optional[tk.Label] = None
        self.etiquetas_estadisticas: Dict[str, tk.Label] = {}
        
        self._configurar_ventana()
        self._crear_interfaz()
        self._inicializar_controlador()
        self._actualizar_interfaz_periodicamente()
    
    def _configurar_ventana(self):
        """Configura la ventana principal."""
        self.ventana.title("🛡️ Ares Aegis - Antivirus Avanzado")
        self.ventana.geometry("1200x800")
        self.ventana.minsize(1000, 700)
        self.ventana.configure(bg=TemaJapones.PAPEL_BLANCO)
        
        # Centrar ventana
        self.ventana.update_idletasks()
        x = (self.ventana.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (800 // 2)
        self.ventana.geometry(f"1200x800+{x}+{y}")
        
        # Configurar cierre
        self.ventana.protocol("WM_DELETE_WINDOW", self._on_cerrar)
        
        # Icono si está disponible
        try:
            icon_path = Path(__file__).parent.parent.parent / "recursos" / "aresIcon.png"
            if icon_path.exists():
                self.ventana.iconphoto(False, tk.PhotoImage(file=str(icon_path)))
        except Exception:
            pass
    
    def _crear_interfaz(self):
        """Crea todos los elementos de la interfaz."""
        # Frame principal
        main_frame = tk.Frame(self.ventana, bg=TemaJapones.PAPEL_BLANCO)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear secciones
        self._crear_cabecera(main_frame)
        self._crear_panel_control(main_frame)
        self._crear_panel_estadisticas(main_frame)
        self._crear_panel_log(main_frame)
        self._crear_barra_estado(main_frame)
    
    def _crear_cabecera(self, parent):
        """Crea la cabecera de la aplicación."""
        frame_cabecera = tk.Frame(parent, bg=TemaJapones.BAMBOO_VERDE, height=80)
        frame_cabecera.pack(fill=tk.X, pady=(0, 10))
        frame_cabecera.pack_propagate(False)
        
        # Título principal
        titulo = tk.Label(
            frame_cabecera,
            text="🛡️ ARES AEGIS",
            bg=TemaJapones.BAMBOO_VERDE,
            fg=TemaJapones.PAPEL_BLANCO,
            font=("Segoe UI", 20, "bold")
        )
        titulo.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Subtítulo
        subtitulo = tk.Label(
            frame_cabecera,
            text="Antivirus Avanzado para Kali Linux",
            bg=TemaJapones.BAMBOO_VERDE,
            fg=TemaJapones.SAKURA_ROSA,
            font=("Segoe UI", 12)
        )
        subtitulo.pack(side=tk.LEFT, padx=(0, 20), pady=20)
        
        # Estado general (lado derecho)
        self.etiqueta_estado = tk.Label(
            frame_cabecera,
            textvariable=self.var_estado_general,
            bg=TemaJapones.BAMBOO_VERDE,
            fg=TemaJapones.PAPEL_BLANCO,
            font=("Segoe UI", 11, "bold")
        )
        self.etiqueta_estado.pack(side=tk.RIGHT, padx=20, pady=20)
    
    def _crear_panel_control(self, parent):
        """Crea el panel de control principal."""
        frame_control = WidgetPersonalizado.crear_frame_panel(parent, "🎛️ Panel de Control")
        frame_control.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para botones principales
        frame_botones = tk.Frame(frame_control, bg=TemaJapones.PAPEL_BLANCO)
        frame_botones.pack(fill=tk.X, padx=20, pady=10)
        
        # Primera fila de botones
        fila1 = tk.Frame(frame_botones, bg=TemaJapones.PAPEL_BLANCO)
        fila1.pack(fill=tk.X, pady=5)
        
        WidgetPersonalizado.crear_boton_principal(
            fila1, f"{IconosUnicode.ESCANEAR} Escaneo Rápido", self._escaneo_rapido
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        WidgetPersonalizado.crear_boton_principal(
            fila1, f"{IconosUnicode.ESCANEAR} Escaneo Completo", self._escaneo_completo
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        WidgetPersonalizado.crear_boton_principal(
            fila1, f"{IconosUnicode.CUARENTENA} Cuarentena", self._abrir_cuarentena
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        WidgetPersonalizado.crear_boton_principal(
            fila1, f"{IconosUnicode.RED} Monitor Red", self._toggle_monitor_red
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Segunda fila de botones
        fila2 = tk.Frame(frame_botones, bg=TemaJapones.PAPEL_BLANCO)
        fila2.pack(fill=tk.X, pady=5)
        
        WidgetPersonalizado.crear_boton_secundario(
            fila2, f"{IconosUnicode.FIM} Verificar FIM", self._verificar_fim
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        WidgetPersonalizado.crear_boton_secundario(
            fila2, f"{IconosUnicode.ACTUALIZAR} Actualizar", self._actualizar_firmas
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        WidgetPersonalizado.crear_boton_secundario(
            fila2, f"{IconosUnicode.EXPORTAR} Exportar", self._exportar_reporte
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        WidgetPersonalizado.crear_boton_secundario(
            fila2, f"{IconosUnicode.CONFIGURACION} Configurar", self._abrir_configuracion
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Selector de ruta personalizada
        frame_ruta = tk.Frame(frame_control, bg=TemaJapones.PAPEL_BLANCO)
        frame_ruta.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            frame_ruta,
            text="📂 Ruta de escaneo personalizada:",
            bg=TemaJapones.PAPEL_BLANCO,
            fg=TemaJapones.TINTA_NEGRA,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT)
        
        entry_ruta = tk.Entry(
            frame_ruta,
            textvariable=self.var_ruta_escaneo,
            font=("Segoe UI", 10),
            width=50
        )
        entry_ruta.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        WidgetPersonalizado.crear_boton_secundario(
            frame_ruta, "📁 Explorar", self._seleccionar_directorio, 10
        ).pack(side=tk.RIGHT)
        
        WidgetPersonalizado.crear_boton_secundario(
            frame_ruta, f"{IconosUnicode.ESCANEAR} Escanear", self._escanear_ruta_personalizada, 10
        ).pack(side=tk.RIGHT, padx=(0, 5))
        
        # Barra de progreso
        frame_progreso = tk.Frame(frame_control, bg=TemaJapones.PAPEL_BLANCO)
        frame_progreso.pack(fill=tk.X, padx=20, pady=10)
        
        self.barra_progreso = ttk.Progressbar(
            frame_progreso,
            variable=self.var_progreso,
            maximum=100,
            style="Themed.Horizontal.TProgressbar"
        )
        self.barra_progreso.pack(fill=tk.X)
    
    def _crear_panel_estadisticas(self, parent):
        """Crea el panel de estadísticas."""
        frame_stats = WidgetPersonalizado.crear_frame_panel(parent, "📊 Estadísticas del Sistema")
        frame_stats.pack(fill=tk.X, pady=(0, 10))
        
        # Grid de estadísticas
        grid_stats = tk.Frame(frame_stats, bg=TemaJapones.PAPEL_BLANCO)
        grid_stats.pack(fill=tk.X, padx=20, pady=10)
        
        # Configurar grid
        for i in range(4):
            grid_stats.columnconfigure(i, weight=1)
        
        # Estadísticas principales
        stats_config = [
            ("🔍 Archivos Escaneados", "archivos_escaneados", 0, 0),
            ("🦠 Amenazas Detectadas", "amenazas_detectadas", 0, 1),
            ("🔒 Archivos en Cuarentena", "archivos_cuarentena", 0, 2),
            ("🌐 Conexiones Monitoreadas", "conexiones_red", 0, 3),
            ("📁 Archivos Monitoreados (FIM)", "archivos_fim", 1, 0),
            ("⚠️ Alertas Activas", "alertas_activas", 1, 1),
            ("⏱️ Uptime del Sistema", "uptime", 1, 2),
            ("💾 Uso de Memoria", "memoria", 1, 3)
        ]
        
        for texto, clave, fila, columna in stats_config:
            frame_stat = tk.Frame(grid_stats, bg=TemaJapones.SOMBRA_SUAVE, relief="solid", borderwidth=1)
            frame_stat.grid(row=fila, column=columna, padx=5, pady=5, sticky="ew")
            
            label_titulo = tk.Label(
                frame_stat,
                text=texto,
                bg=TemaJapones.SOMBRA_SUAVE,
                fg=TemaJapones.TINTA_NEGRA,
                font=("Segoe UI", 9, "bold")
            )
            label_titulo.pack(pady=(5, 0))
            
            label_valor = tk.Label(
                frame_stat,
                text="0",
                bg=TemaJapones.SOMBRA_SUAVE,
                fg=TemaJapones.BAMBOO_VERDE,
                font=("Segoe UI", 12, "bold")
            )
            label_valor.pack(pady=(0, 5))
            
            self.etiquetas_estadisticas[clave] = label_valor
    
    def _crear_panel_log(self, parent):
        """Crea el panel de logs."""
        frame_log = WidgetPersonalizado.crear_frame_panel(parent, "📋 Registro de Eventos")
        frame_log.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Frame para controles del log
        frame_controles_log = tk.Frame(frame_log, bg=TemaJapones.PAPEL_BLANCO)
        frame_controles_log.pack(fill=tk.X, padx=20, pady=5)
        
        WidgetPersonalizado.crear_boton_secundario(
            frame_controles_log, f"{IconosUnicode.LIMPIAR} Limpiar", self._limpiar_log, 10
        ).pack(side=tk.LEFT)
        
        WidgetPersonalizado.crear_boton_secundario(
            frame_controles_log, f"{IconosUnicode.ACTUALIZAR} Actualizar", self._actualizar_log, 10
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Área de texto para logs
        self.texto_log = scrolledtext.ScrolledText(
            frame_log,
            height=12,
            font=("Consolas", 9),
            bg=TemaJapones.TINTA_NEGRA,
            fg=TemaJapones.PAPEL_BLANCO,
            insertbackground=TemaJapones.PAPEL_BLANCO,
            selectbackground=TemaJapones.BAMBOO_VERDE
        )
        self.texto_log.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 10))
        
        # Agregar mensaje inicial
        self._agregar_log("✅ Ares Aegis iniciado correctamente", TemaJapones.EXITO)
        self._agregar_log("🛡️ Sistema de protección activado", TemaJapones.INFO)
    
    def _crear_barra_estado(self, parent):
        """Crea la barra de estado."""
        frame_estado = tk.Frame(parent, bg=TemaJapones.PLATA_GRIS, height=30)
        frame_estado.pack(fill=tk.X)
        frame_estado.pack_propagate(False)
        
        # Estado del sistema
        self.label_estado_sistema = tk.Label(
            frame_estado,
            text=f"{IconosUnicode.CORRECTO} Sistema Protegido",
            bg=TemaJapones.PLATA_GRIS,
            fg=TemaJapones.TINTA_NEGRA,
            font=("Segoe UI", 9)
        )
        self.label_estado_sistema.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Hora actual
        self.label_hora = tk.Label(
            frame_estado,
            text="",
            bg=TemaJapones.PLATA_GRIS,
            fg=TemaJapones.TINTA_NEGRA,
            font=("Segoe UI", 9)
        )
        self.label_hora.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self._actualizar_hora()
    
    def _inicializar_controlador(self):
        """Inicializa el controlador principal."""
        try:
            self.controlador = ControladorPrincipal()
            self._agregar_log("✅ Controlador principal inicializado", TemaJapones.EXITO)
        except Exception as e:
            self._agregar_log(f"❌ Error inicializando controlador: {e}", TemaJapones.ERROR)
            messagebox.showerror("Error", f"No se pudo inicializar el sistema:\n{e}")
    
    def _agregar_log(self, mensaje: str, color: str = TemaJapones.PAPEL_BLANCO):
        """Agrega un mensaje al log con timestamp."""
        if self.texto_log:
            timestamp = datetime.now().strftime("%H:%M:%S")
            linea = f"[{timestamp}] {mensaje}\n"
            
            self.texto_log.config(state=tk.NORMAL)
            self.texto_log.insert(tk.END, linea)
            self.texto_log.config(state=tk.DISABLED)
            self.texto_log.see(tk.END)
    
    def _actualizar_hora(self):
        """Actualiza la hora en la barra de estado."""
        if self.label_hora:
            hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.label_hora.config(text=hora_actual)
            self.ventana.after(1000, self._actualizar_hora)
    
    def _actualizar_interfaz_periodicamente(self):
        """Actualiza la interfaz cada cierto tiempo."""
        self._actualizar_estadisticas()
        self.ventana.after(5000, self._actualizar_interfaz_periodicamente)  # Cada 5 segundos
    
    def _actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas."""
        if not self.controlador:
            return
        
        try:
            stats = self.controlador.obtener_estadisticas_generales()
            
            # Actualizar etiquetas de estadísticas
            actualizaciones = {
                'archivos_escaneados': stats.get('archivos_escaneados', 0),
                'amenazas_detectadas': stats.get('amenazas_detectadas', 0),
                'archivos_cuarentena': stats.get('archivos_cuarentena', 0),
                'conexiones_red': stats.get('conexiones_activas', 0),
                'archivos_fim': stats.get('archivos_fim', 0),
                'alertas_activas': stats.get('alertas_activas', 0),
                'uptime': self._formatear_uptime(stats.get('uptime_segundos', 0)),
                'memoria': f"{stats.get('uso_memoria_mb', 0):.1f} MB"
            }
            
            for clave, valor in actualizaciones.items():
                if clave in self.etiquetas_estadisticas:
                    self.etiquetas_estadisticas[clave].config(text=str(valor))
            
            # Actualizar estado general
            if stats.get('amenazas_detectadas', 0) > 0:
                self.var_estado_general.set(f"⚠️ {stats['amenazas_detectadas']} amenazas detectadas")
                if self.label_estado_sistema:
                    self.label_estado_sistema.config(
                        text=f"{IconosUnicode.ALERTA} Amenazas Detectadas",
                        fg=TemaJapones.ERROR
                    )
            elif self.escaneo_activo:
                self.var_estado_general.set("🔍 Escaneo en progreso...")
                if self.label_estado_sistema:
                    self.label_estado_sistema.config(
                        text=f"{IconosUnicode.ESCANEAR} Escaneando",
                        fg=TemaJapones.ADVERTENCIA
                    )
            else:
                self.var_estado_general.set("🛡️ Sistema Protegido")
                if self.label_estado_sistema:
                    self.label_estado_sistema.config(
                        text=f"{IconosUnicode.CORRECTO} Sistema Protegido",
                        fg=TemaJapones.EXITO
                    )
        
        except Exception as e:
            self._agregar_log(f"❌ Error actualizando estadísticas: {e}", TemaJapones.ERROR)
    
    def _formatear_uptime(self, segundos: int) -> str:
        """Formatea el uptime en un formato legible."""
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        return f"{horas:02d}:{minutos:02d}"
    
    # Métodos de los botones de acción
    def _escaneo_rapido(self):
        """Ejecuta un escaneo rápido."""
        if self.escaneo_activo:
            self._agregar_log("⚠️ Ya hay un escaneo en progreso", TemaJapones.ADVERTENCIA)
            return
        
        self._agregar_log("🔍 Iniciando escaneo rápido...", TemaJapones.INFO)
        self._ejecutar_escaneo_async("rapido")
    
    def _escaneo_completo(self):
        """Ejecuta un escaneo completo."""
        if self.escaneo_activo:
            self._agregar_log("⚠️ Ya hay un escaneo en progreso", TemaJapones.ADVERTENCIA)
            return
        
        resultado = messagebox.askyesno(
            "Escaneo Completo",
            "El escaneo completo puede tardar mucho tiempo.\n¿Desea continuar?"
        )
        
        if resultado:
            self._agregar_log("🔍 Iniciando escaneo completo...", TemaJapones.INFO)
            self._ejecutar_escaneo_async("completo")
    
    def _escanear_ruta_personalizada(self):
        """Escanea una ruta personalizada."""
        if self.escaneo_activo:
            self._agregar_log("⚠️ Ya hay un escaneo en progreso", TemaJapones.ADVERTENCIA)
            return
        
        ruta = self.var_ruta_escaneo.get()
        if not ruta or not Path(ruta).exists():
            messagebox.showerror("Error", "La ruta especificada no existe")
            return
        
        self._agregar_log(f"🔍 Escaneando ruta: {ruta}", TemaJapones.INFO)
        self._ejecutar_escaneo_async("personalizado", ruta)
    
    def _ejecutar_escaneo_async(self, tipo_escaneo: str, ruta: str = ""):
        """Ejecuta un escaneo en un hilo separado."""
        def ejecutar():
            self.escaneo_activo = True
            self.var_progreso.set(0)
            
            try:
                if tipo_escaneo == "rapido":
                    resultado = self.controlador.escaneo_rapido()
                elif tipo_escaneo == "completo":
                    resultado = self.controlador.escaneo_completo()
                elif tipo_escaneo == "personalizado":
                    resultado = self.controlador.escanear_directorio(ruta)
                
                # Simular progreso
                for i in range(0, 101, 5):
                    self.var_progreso.set(i)
                    time.sleep(0.1)
                
                # Mostrar resultados
                self.ventana.after(0, lambda: self._mostrar_resultados_escaneo(resultado))
                
            except Exception as e:
                self.ventana.after(0, lambda: self._agregar_log(f"❌ Error en escaneo: {e}", TemaJapones.ERROR))
            
            finally:
                self.escaneo_activo = False
                self.var_progreso.set(0)
        
        threading.Thread(target=ejecutar, daemon=True).start()
    
    def _mostrar_resultados_escaneo(self, resultado: Dict[str, Any]):
        """Muestra los resultados del escaneo."""
        archivos = resultado.get('archivos_escaneados', 0)
        amenazas = resultado.get('amenazas_detectadas', 0)
        tiempo = resultado.get('tiempo_escaneo', 0)
        
        if amenazas > 0:
            self._agregar_log(f"⚠️ Escaneo completado: {amenazas} amenazas detectadas en {archivos} archivos", TemaJapones.ERROR)
            messagebox.showwarning(
                "Amenazas Detectadas",
                f"Se detectaron {amenazas} amenazas en {archivos} archivos escaneados.\n"
                f"Tiempo de escaneo: {tiempo:.2f} segundos\n\n"
                "Revise la cuarentena para más detalles."
            )
        else:
            self._agregar_log(f"✅ Escaneo completado: {archivos} archivos escaneados, sin amenazas", TemaJapones.EXITO)
            messagebox.showinfo(
                "Escaneo Completado",
                f"Escaneo completado exitosamente.\n"
                f"Archivos escaneados: {archivos}\n"
                f"Amenazas detectadas: 0\n"
                f"Tiempo de escaneo: {tiempo:.2f} segundos"
            )
    
    def _seleccionar_directorio(self):
        """Selecciona un directorio para escaneo personalizado."""
        directorio = filedialog.askdirectory(
            title="Seleccionar directorio para escanear",
            initialdir=self.var_ruta_escaneo.get()
        )
        
        if directorio:
            self.var_ruta_escaneo.set(directorio)
    
    def _abrir_cuarentena(self):
        """Abre la ventana de gestión de cuarentena."""
        self._agregar_log("🔒 Abriendo gestión de cuarentena...", TemaJapones.INFO)
        # TODO: Implementar ventana de cuarentena
        messagebox.showinfo("Cuarentena", "Funcionalidad de cuarentena en desarrollo")
    
    def _toggle_monitor_red(self):
        """Activa/desactiva el monitor de red."""
        if not self.controlador:
            return
        
        if self.monitoreo_activo:
            self.controlador.detener_monitor_red()
            self.monitoreo_activo = False
            self._agregar_log("🌐 Monitor de red detenido", TemaJapones.INFO)
        else:
            self.controlador.iniciar_monitor_red()
            self.monitoreo_activo = True
            self._agregar_log("🌐 Monitor de red iniciado", TemaJapones.EXITO)
    
    def _verificar_fim(self):
        """Verifica la integridad de archivos."""
        self._agregar_log("📁 Iniciando verificación de integridad...", TemaJapones.INFO)
        
        def verificar():
            try:
                resultado = self.controlador.verificar_integridad_archivos()
                cambios = resultado.get('cambios_detectados', 0)
                
                if cambios > 0:
                    self.ventana.after(0, lambda: self._agregar_log(
                        f"⚠️ FIM: {cambios} cambios detectados", TemaJapones.ADVERTENCIA
                    ))
                else:
                    self.ventana.after(0, lambda: self._agregar_log(
                        "✅ FIM: Sin cambios detectados", TemaJapones.EXITO
                    ))
            except Exception as e:
                self.ventana.after(0, lambda: self._agregar_log(
                    f"❌ Error en FIM: {e}", TemaJapones.ERROR
                ))
        
        threading.Thread(target=verificar, daemon=True).start()
    
    def _actualizar_firmas(self):
        """Actualiza las firmas de malware."""
        self._agregar_log("🔄 Actualizando firmas de malware...", TemaJapones.INFO)
        # TODO: Implementar actualización de firmas
        messagebox.showinfo("Actualización", "Funcionalidad de actualización en desarrollo")
    
    def _exportar_reporte(self):
        """Exporta un reporte del sistema."""
        archivo = filedialog.asksaveasfilename(
            title="Guardar reporte",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Texto", "*.txt"), ("Todos", "*.*")]
        )
        
        if archivo:
            try:
                reporte = self.controlador.generar_reporte_completo()
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(reporte)
                
                self._agregar_log(f"📤 Reporte exportado: {archivo}", TemaJapones.EXITO)
                messagebox.showinfo("Exportar", f"Reporte guardado exitosamente en:\n{archivo}")
            
            except Exception as e:
                self._agregar_log(f"❌ Error exportando reporte: {e}", TemaJapones.ERROR)
                messagebox.showerror("Error", f"No se pudo guardar el reporte:\n{e}")
    
    def _abrir_configuracion(self):
        """Abre la ventana de configuración."""
        self._agregar_log("⚙️ Abriendo configuración...", TemaJapones.INFO)
        # TODO: Implementar ventana de configuración
        messagebox.showinfo("Configuración", "Funcionalidad de configuración en desarrollo")
    
    def _limpiar_log(self):
        """Limpia el área de logs."""
        if self.texto_log:
            self.texto_log.config(state=tk.NORMAL)
            self.texto_log.delete(1.0, tk.END)
            self.texto_log.config(state=tk.DISABLED)
            self._agregar_log("✅ Log limpiado", TemaJapones.INFO)
    
    def _actualizar_log(self):
        """Actualiza el log con eventos recientes."""
        if not self.controlador:
            return
        
        try:
            eventos_recientes = self.controlador.obtener_eventos_recientes(10)
            
            for evento in eventos_recientes[-5:]:  # Últimos 5 eventos
                timestamp = evento.get('timestamp', '')
                mensaje = evento.get('mensaje', '')
                tipo = evento.get('tipo_evento', '')
                
                if timestamp and mensaje:
                    color = TemaJapones.PAPEL_BLANCO
                    if 'AMENAZA' in tipo or 'ERROR' in tipo:
                        color = TemaJapones.ERROR
                    elif 'ADVERTENCIA' in tipo:
                        color = TemaJapones.ADVERTENCIA
                    elif 'EXITO' in tipo or 'CORRECTO' in tipo:
                        color = TemaJapones.EXITO
                    
                    self._agregar_log(f"📋 {mensaje}", color)
        
        except Exception as e:
            self._agregar_log(f"❌ Error actualizando log: {e}", TemaJapones.ERROR)
    
    def _on_cerrar(self):
        """Maneja el cierre de la aplicación."""
        resultado = messagebox.askyesno(
            "Cerrar Ares Aegis",
            "¿Está seguro que desea cerrar Ares Aegis?\n\n"
            "Se detendrán todos los monitoreos activos."
        )
        
        if resultado:
            try:
                if self.controlador:
                    self.controlador.finalizar()
                    self._agregar_log("🔒 Sistema finalizado correctamente", TemaJapones.INFO)
            except Exception as e:
                print(f"Error al finalizar: {e}")
            
            self.ventana.destroy()
    
    def mostrar_notificacion(self, titulo: str, mensaje: str, tipo: str = "info"):
        """
        Muestra una notificación al usuario.
        
        Args:
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            tipo: Tipo de notificación (info, warning, error)
        """
        color = TemaJapones.INFO
        if tipo == "warning":
            color = TemaJapones.ADVERTENCIA
        elif tipo == "error":
            color = TemaJapones.ERROR
        elif tipo == "success":
            color = TemaJapones.EXITO
        
        self._agregar_log(f"🔔 {titulo}: {mensaje}", color)
        
        # También mostrar messagebox si es crítico
        if tipo == "error":
            messagebox.showerror(titulo, mensaje)
        elif tipo == "warning":
            messagebox.showwarning(titulo, mensaje)
    
    def ejecutar(self):
        """Ejecuta la interfaz gráfica."""
        try:
            self.ventana.mainloop()
        except KeyboardInterrupt:
            self._cerrar_aplicacion()
        except Exception as e:
            messagebox.showerror("Error", f"Error ejecutando la interfaz: {e}")
            self._cerrar_aplicacion()
    
    def _cerrar_aplicacion(self):
        """Cierra la aplicación limpiamente."""
        try:
            if self.controlador:
                self.controlador.finalizar()
            self.ventana.quit()
            self.ventana.destroy()
        except Exception as e:
            print(f"Error cerrando aplicación: {e}")
