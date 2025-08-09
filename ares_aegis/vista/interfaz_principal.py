#!/usr/bin/env python3
"""
Interfaz Principal de Ares Aegis - Estilo Kali Linux
Sistema de Ciberseguridad Modular con Arquitectura MVC

Creado por DogSoulDev
Versión: 4.0.0 - Edición Refactorizada con Nombres en Español
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os
import webbrowser
import time

from ares_aegis.controlador.controlador_principal import ControladorPrincipal
from ares_aegis.utils.utils_ayuda_logging import configurar_logger

# Componentes UI Modularizados
from ares_aegis.vista.componentes_ui.emoticonos_mitologicos import EmoticonosMitologicos
from ares_aegis.vista.componentes_ui.colores_kali import ColoresKaliLinux
from ares_aegis.vista.componentes_ui.metricas_tiempo_real import MetricasTiempoReal
from ares_aegis.vista.componentes_ui.gestor_cheatsheets import GestorCheatsheets
from ares_aegis.vista.componentes_ui.ventana_cheatsheets import VentanaCheatsheets
from ares_aegis.vista.componentes_ui.sistema_ayuda import SistemaAyuda

# Vistas Especializadas
from ares_aegis.vista.vista_dashboard import VistaDashboard
from ares_aegis.vista.vista_escaneador import VistaEscaneador
from ares_aegis.vista.vista_auditoria_pam import VistaAuditoriaPAM
from ares_aegis.vista.vista_monitor import VistaMonitor
from ares_aegis.vista.vista_monitor_procesos import VistaMonitorProcesos
from ares_aegis.vista.vista_monitor_red import VistaMonitorRed
from ares_aegis.vista.vista_siem import VistaSIEM
from ares_aegis.vista.vista_cuarentena import VistaCuarentena
from ares_aegis.vista.vista_reportes import VistaReportes
from ares_aegis.vista.vista_cheatsheets import VistaCheatsheets
from ares_aegis.vista.vista_constructor_wordlists import VistaConstructorWordlists


class InterfazPrincipalAresAegis:
    """
    Interfaz Principal de Ares Aegis con Arquitectura Modular
    Nombres en español y estilo Kali Linux profesional
    """
    
    def __init__(self):
        """Inicializar la interfaz mitológica con diseño modular"""
        self.logger = logging.getLogger(__name__)
        self.root = None
        self.controlador = None
        
        # Componentes UI
        self.colores = ColoresKaliLinux()
        self.emoticonos = EmoticonosMitologicos()
        
        # Sistema de ayuda
        self.sistema_ayuda = SistemaAyuda(self.colores)
        
        # Sistema de métricas
        self.metricas_tiempo_real = None
        
        # Gestor de cheatsheets
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cheatsheets_path = os.path.join(base_dir, "recursos", "cheatsheets")
        self.gestor_cheatsheets = GestorCheatsheets(cheatsheets_path)
        
        # Variables de estado
        self.estado_fortaleza = None
        self.vista_actual = None
        
        # Contenedores principales
        self.contenedor_principal = None
        self.area_contenido = None
        self.panel_lateral = None
        
        # Vistas especializadas
        self.vistas = {}
        
        self.logger.info(" Interfaz Principal de Ares Aegis inicializada con arquitectura modular")
    
    def inicializar(self, controlador=None) -> bool:
        """Inicializar la aplicación completa"""
        try:
            # Asignar controlador
            if controlador:
                self.controlador = controlador
            else:
                self.controlador = ControladorPrincipal()
                
            # Establecer referencia bidireccional
            try:
                setattr(self.controlador, 'interfaz', self)
            except (AttributeError, TypeError):
                pass  # El controlador no soporta interfaz
            
            if not self.controlador.inicializar_componentes():
                self.logger.warning(" Algunos componentes del controlador no se inicializaron correctamente")
            
            # Crear ventana principal
            self._crear_ventana_principal()
            
            # Configurar tema Kali Linux
            self._configurar_tema_kali()
            
            # Crear interfaz modular
            self._crear_interfaz_modular()
            
            # Inicializar vistas especializadas
            self._inicializar_vistas()
            
            # Iniciar sistema de métricas
            self._iniciar_metricas_tiempo_real()
            
            # Mostrar dashboard por defecto
            self._mostrar_vista('dashboard')
            
            self.logger.info("[OK] Interfaz Principal inicializada correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error inicializando interfaz: {e}")
            messagebox.showerror("Error Fatal", f"Error inicializando aplicación:\n{str(e)}")
            return False
    
    def _crear_ventana_principal(self):
        """Crear ventana principal estilo terminal profesional de ciberseguridad"""
        self.root = tk.Tk()
        self.root.title("SISTEMA DE CIBERSEGURIDAD • KALI EDITION")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 900)
        self.root.configure(bg=self.colores.fondo_primario)
        
        # Configurar grid para layout profesional
        self.root.grid_rowconfigure(0, weight=0)  # Barra superior
        self.root.grid_rowconfigure(1, weight=1)  # Área principal (sin toolbar)
        self.root.grid_rowconfigure(2, weight=0)  # Barra de estado
        self.root.grid_columnconfigure(0, weight=1)
        
        # Configurar icono si está disponible
        self._configurar_icono()
        
        # Configurar protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._cerrar_aplicacion)
        
        # Variables de estado
        self.estado_fortaleza = tk.StringVar()
        self.estado_fortaleza.set("SISTEMA OPERATIVO • CONEXIÓN SEGURA ESTABLECIDA")
    
    def _configurar_icono(self):
        """Configurar icono de la ventana"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            icon_paths = [
                os.path.join(base_dir, "recursos", "AresAegis.png"),
                os.path.join(base_dir, "recursos", "aresIcon.png")
            ]
            
            for path in icon_paths:
                if os.path.exists(path) and self.root:
                    self.root.iconphoto(False, tk.PhotoImage(file=path))
                    self.logger.info(f"[ICON] Icono cargado desde: {path}")
                    return
            
        except Exception as e:
            self.logger.debug(f"No se pudo cargar icono: {e}")
    
    def _configurar_tema_kali(self):
        """Configurar tema estilo herramientas profesionales de ciberseguridad"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # === CONFIGURAR ESTILOS PROFESIONALES ===
        
        # Frames con bordes sutiles
        style.configure('TFrame', 
                       background=self.colores.fondo_primario,
                       borderwidth=1,
                       relief='flat')
        
        style.configure('Card.TFrame',
                       background=self.colores.fondo_secundario,
                       borderwidth=1,
                       relief='solid')
        
        # Labels con tipografía terminal
        style.configure('TLabel', 
                       background=self.colores.fondo_primario, 
                       foreground=self.colores.texto_primario, 
                       font=('Consolas', 10))
        
        style.configure('Title.TLabel',
                       background=self.colores.fondo_primario,
                       foreground=self.colores.verde_terminal,
                       font=('Consolas', 14, 'bold'))
        
        style.configure('Header.TLabel',
                       background=self.colores.fondo_secundario,
                       foreground=self.colores.blanco_hueso,
                       font=('Consolas', 12, 'bold'))
        
        style.configure('Status.TLabel',
                       background=self.colores.fondo_primario,
                       foreground=self.colores.cyan_brillante,
                       font=('Consolas', 9))
        
        # Botones estilo terminal hacker
        style.configure('TButton', 
                       background=self.colores.gris_pizarra, 
                       foreground=self.colores.texto_primario, 
                       font=('Consolas', 10, 'bold'),
                       borderwidth=1,
                       focuscolor='none',
                       relief='flat')
        
        style.configure('Action.TButton',
                       background=self.colores.verde_bosque,
                       foreground=self.colores.blanco_hueso,
                       font=('Consolas', 11, 'bold'))
        
        style.configure('Danger.TButton',
                       background=self.colores.rojo_critico,
                       foreground=self.colores.blanco_hueso,
                       font=('Consolas', 10, 'bold'))
        
        style.map('TButton',
                 background=[('active', self.colores.boton_hover),
                           ('pressed', self.colores.verde_oliva)])
        
        style.map('Action.TButton',
                 background=[('active', self.colores.verde_terminal),
                           ('pressed', self.colores.verde_esmeralda)])
        
        # Notebook estilo pestañas profesionales
        style.configure('TNotebook', 
                       background=self.colores.fondo_primario,
                       borderwidth=0)
        
        style.configure('TNotebook.Tab', 
                       background=self.colores.fondo_terciario, 
                       foreground=self.colores.texto_secundario, 
                       padding=[20, 10],
                       font=('Consolas', 10, 'bold'),
                       borderwidth=1)
        
        style.map('TNotebook.Tab',
                 background=[('selected', self.colores.verde_terminal),
                           ('active', self.colores.gris_hierro)],
                 foreground=[('selected', self.colores.negro_profundo),
                           ('active', self.colores.blanco_hueso)])
        
        # Entry y Text estilo terminal
        style.configure('TEntry',
                       fieldbackground=self.colores.negro_carbono,
                       foreground=self.colores.texto_primario,
                       borderwidth=1,
                       insertcolor=self.colores.verde_terminal)
        
        # Progressbar estilo hacker
        style.configure('TProgressbar',
                       background=self.colores.verde_terminal,
                       troughcolor=self.colores.fondo_terciario,
                       borderwidth=0,
                       lightcolor=self.colores.verde_fosforescente,
                       darkcolor=self.colores.verde_bosque)
    
    def _crear_interfaz_modular(self):
        """Crear interfaz profesional estilo herramientas de ciberseguridad"""
        # === BARRA SUPERIOR PROFESIONAL ===
        self._crear_barra_superior()
        
        # === ÁREA PRINCIPAL CON LAYOUT PROFESIONAL ===
        self._crear_area_principal_profesional()
        
        # === BARRA DE ESTADO INFERIOR ===
        self._crear_barra_estado()
    
    def _crear_barra_superior(self):
        """Crear barra superior estilo terminal profesional"""
        self.barra_superior = tk.Frame(self.root, 
                                     bg=self.colores.negro_carbono, 
                                     height=60, 
                                     relief='flat', 
                                     bd=1)
        self.barra_superior.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.barra_superior.grid_propagate(False)
        
        # Configurar grid simplificado
        self.barra_superior.grid_columnconfigure(0, weight=1)  # Espacio central
        self.barra_superior.grid_columnconfigure(1, weight=0)  # Información del sistema

        # === TÍTULO DEL SISTEMA ===
        titulo_frame = tk.Frame(self.barra_superior, bg=self.colores.negro_carbono)
        titulo_frame.grid(row=0, column=0, sticky="nsw", padx=20, pady=15)
        
        tk.Label(titulo_frame,
                text=" ARES AEGIS • SISTEMA DE CIBERSEGURIDAD",
                font=('Consolas', 14, 'bold'),
                fg=self.colores.naranja_fuego,
                bg=self.colores.negro_carbono).pack(anchor='w')

        # === INFORMACIÓN DEL SISTEMA ===
        sistema_frame = tk.Frame(self.barra_superior, bg=self.colores.negro_carbono)
        sistema_frame.grid(row=0, column=1, sticky="nse", padx=20, pady=10)
        
        # Usuario y sistema
        tk.Label(sistema_frame,
                text=f"USER: {os.getenv('USERNAME', 'operator').upper()}",
                font=('Consolas', 9, 'bold'),
                fg=self.colores.amarillo_medio,
                bg=self.colores.negro_carbono).pack(anchor='e')
        
        tk.Label(sistema_frame,
                text=f"HOST: {os.getenv('COMPUTERNAME', 'localhost').upper()}",
                font=('Consolas', 9),
                fg=self.colores.gris_platino,
                bg=self.colores.negro_carbono).pack(anchor='e')
    
    def _crear_area_principal_profesional(self):
        """Crear área principal con layout profesional estilo Burp Suite"""
        self.contenedor_principal = tk.Frame(self.root, bg=self.colores.fondo_primario)
        self.contenedor_principal.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # Configurar grid responsive profesional
        self.contenedor_principal.grid_rowconfigure(0, weight=1)
        self.contenedor_principal.grid_columnconfigure(0, weight=0)  # Panel navegación lateral
        self.contenedor_principal.grid_columnconfigure(1, weight=1)  # Área contenido principal
        
        # === PANEL DE NAVEGACIÓN LATERAL ===
        self._crear_panel_navegacion_profesional()
        
        # === ÁREA DE CONTENIDO PRINCIPAL ===
        self.area_contenido = tk.Frame(self.contenedor_principal,
                                     bg=self.colores.fondo_secundario,
                                     relief='flat',
                                     bd=0)
        self.area_contenido.grid(row=0, column=1, sticky="nsew", padx=(1, 0), pady=0)
    
    def _crear_barra_estado(self):
        """Crear barra de estado inferior estilo terminal"""
        self.barra_estado = tk.Frame(self.root, 
                                   bg=self.colores.negro_carbono, 
                                   height=30, 
                                   relief='flat')
        self.barra_estado.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        self.barra_estado.grid_propagate(False)
        
        # === INFORMACIÓN DE ESTADO ===
        tk.Label(self.barra_estado,
                text="Listo • Todos los sistemas operacionales • Último escaneo: Nunca",
                font=('Consolas', 8),
                fg=self.colores.gris_platino,
                bg=self.colores.negro_carbono).pack(side='left', padx=20, pady=5)
        
        # === ESTADÍSTICAS RÁPIDAS ===
        estadisticas_frame = tk.Frame(self.barra_estado, bg=self.colores.negro_carbono)
        estadisticas_frame.pack(side='right', padx=20, pady=5)
        
        stats = [
            ("AMENAZAS:", "0", self.colores.verde_terminal),
            ("ESCANEADOS:", "0", self.colores.cyan_brillante),
            ("CUARENTENA:", "0", self.colores.amarillo_medio)
        ]
        
        for label, valor, color in stats:
            tk.Label(estadisticas_frame,
                    text=f"{label} {valor}",
                    font=('Consolas', 8, 'bold'),
                    fg=color,
                    bg=self.colores.negro_carbono).pack(side='left', padx=10)
    
    def _crear_panel_navegacion_profesional(self):
        """Crear panel de navegación lateral estilo herramientas profesionales"""
        self.panel_lateral = tk.Frame(self.contenedor_principal,
                                    bg=self.colores.gris_pizarra,
                                    width=280,
                                    relief='flat',
                                    bd=0)
        self.panel_lateral.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.panel_lateral.grid_propagate(False)
        
        # === HEADER DEL PANEL ===
        panel_header = tk.Frame(self.panel_lateral, 
                              bg=self.colores.negro_carbono, 
                              height=50)
        panel_header.pack(fill='x', padx=0, pady=0)
        panel_header.pack_propagate(False)
        
        tk.Label(panel_header,
                text="MÓDULOS",
                font=('Consolas', 12, 'bold'),
                fg=self.colores.verde_terminal,
                bg=self.colores.negro_carbono).pack(expand=True, pady=15)
        
        # === NAVEGACIÓN PRINCIPAL CON ESTILO PROFESIONAL ===
        self._crear_navegacion_modular_profesional()
        
        # === PANEL DE MÉTRICAS EN TIEMPO REAL ===
        self._crear_panel_metricas_lateral()
        
        # === PANEL DE ACCESOS RÁPIDOS ===
        self._crear_panel_accesos_rapidos()
    
    def _crear_navegacion_modular_profesional(self):
        """Crear navegación modular con estilo profesional"""
        nav_container = tk.Frame(self.panel_lateral, bg=self.colores.gris_pizarra)
        nav_container.pack(fill='x', padx=0, pady=10)
        
        # Módulos principales con iconografía profesional
        modulos = [
            ('dashboard', ' INICIO', 'Centralita principal', self._mostrar_dashboard),
            ('escaneador', ' ESCÁNER', 'Escáner de vulnerabilidades', self._mostrar_escaneador),
            ('auditoria_pam', '[LOCK] AUDITORÍA PAM', 'Auditoría de autenticación', self._mostrar_auditoria_pam),
            ('monitor_procesos', ' MONITOR PROCESOS', 'Monitor de procesos del sistema', self._mostrar_monitor_procesos),
            ('monitor_red', ' MONITOR RED', 'Monitor de actividad de red', self._mostrar_monitor_red),
            ('siem', '[SHIELD] SIEM', 'Sistema de eventos de seguridad', self._mostrar_siem),
            ('cuarentena', ' CUARENTENA', 'Gestión de cuarentena', self._mostrar_cuarentena)
        ]
        
        self.botones_navegacion = {}
        
        for modulo_id, titulo, descripcion, comando in modulos:
            # Container para cada módulo
            modulo_frame = tk.Frame(nav_container, bg=self.colores.gris_pizarra)
            modulo_frame.pack(fill='x', padx=10, pady=2)
            
            # Botón principal del módulo
            btn = tk.Button(modulo_frame,
                           text=titulo,
                           command=comando,
                           bg=self.colores.gris_hierro,
                           fg=self.colores.texto_primario,
                           font=('Consolas', 10, 'bold'),
                           relief='flat',
                           anchor='w',
                           padx=15, pady=12,
                           cursor='hand2')
            btn.pack(fill='x')
            
            # Descripción del módulo
            desc_label = tk.Label(modulo_frame,
                                 text=descripcion,
                                 font=('Consolas', 8),
                                 fg=self.colores.gris_platino,
                                 bg=self.colores.gris_pizarra,
                                 anchor='w')
            desc_label.pack(fill='x', padx=20, pady=(0, 5))
            
            # Efectos hover profesionales
            self._agregar_efecto_hover_modulo(btn, modulo_id)
            
            # Guardar referencia
            self.botones_navegacion[modulo_id] = btn
    
    def _crear_panel_metricas_lateral(self):
        """Crear panel de métricas en tiempo real en el lateral"""
        metricas_frame = tk.LabelFrame(self.panel_lateral,
                                     text="ESTADO DEL SISTEMA",
                                     bg=self.colores.gris_pizarra,
                                     fg=self.colores.cyan_brillante,
                                     font=('Consolas', 9, 'bold'),
                                     relief='flat',
                                     bd=1)
        metricas_frame.pack(fill='x', padx=10, pady=10)
        
        # Métricas básicas
        metricas_info = [
            ("CPU", "25%", self.colores.verde_terminal),
            ("RAM", "45%", self.colores.amarillo_medio),
            ("DISK", "60%", self.colores.cyan_brillante),
            ("AMENAZAS", "0", self.colores.verde_terminal)
        ]
        
        for nombre, valor, color in metricas_info:
            metrica_row = tk.Frame(metricas_frame, bg=self.colores.gris_pizarra)
            metrica_row.pack(fill='x', padx=10, pady=5)
            
            tk.Label(metrica_row,
                    text=f"{nombre}:",
                    font=('Consolas', 9),
                    fg=self.colores.gris_platino,
                    bg=self.colores.gris_pizarra).pack(side='left')
            
            tk.Label(metrica_row,
                    text=valor,
                    font=('Consolas', 9, 'bold'),
                    fg=color,
                    bg=self.colores.gris_pizarra).pack(side='right')
    
    def _crear_panel_accesos_rapidos(self):
        """Crear panel de accesos rápidos"""
        accesos_frame = tk.LabelFrame(self.panel_lateral,
                                    text="ACCESO RÁPIDO",
                                    bg=self.colores.gris_pizarra,
                                    fg=self.colores.purpura_neon,
                                    font=('Consolas', 9, 'bold'),
                                    relief='flat',
                                    bd=1)
        accesos_frame.pack(fill='x', padx=10, pady=10)
        
        # Botones de acceso rápido
        accesos = [
            (" REPORTES", self._mostrar_reportes),
            ("[TOOL] CONSTRUCTOR WORDLISTS", self._mostrar_constructor_wordlists),
            (" GUÍAS", self._mostrar_cheatsheets),
            ("‍ DESARROLLADOR", self._abrir_github)
        ]
        
        for texto, comando in accesos:
            btn = tk.Button(accesos_frame,
                           text=texto,
                           command=comando,
                           bg=self.colores.negro_carbono,
                           fg=self.colores.texto_secundario,
                           font=('Consolas', 9),
                           relief='flat',
                           padx=10, pady=8,
                           cursor='hand2',
                           anchor='w')
            btn.pack(fill='x', padx=5, pady=2)
            
            # Efecto hover
            self._agregar_efecto_hover_acceso(btn)
    
    # === MÉTODOS DE EFECTOS VISUALES ===
    
    def _agregar_efecto_hover_toolbar(self, widget, color_activo):
        """Agregar efecto hover para toolbar"""
        color_original = widget.cget('bg')
        
        def on_enter(event):
            widget.configure(bg=color_activo, fg=self.colores.negro_profundo)
        
        def on_leave(event):
            widget.configure(bg=color_original, fg=color_activo)
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def _agregar_efecto_hover_modulo(self, widget, modulo_id):
        """Agregar efecto hover para módulos"""
        color_original = widget.cget('bg')
        color_activo = self.colores.verde_bosque if modulo_id == self.vista_actual else self.colores.gris_titanio
        
        def on_enter(event):
            if modulo_id != self.vista_actual:
                widget.configure(bg=color_activo, fg=self.colores.blanco_hueso)
        
        def on_leave(event):
            if modulo_id != self.vista_actual:
                widget.configure(bg=color_original, fg=self.colores.texto_primario)
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def _agregar_efecto_hover_acceso(self, widget):
        """Agregar efecto hover para accesos rápidos"""
        color_original = widget.cget('bg')
        
        def on_enter(event):
            widget.configure(bg=self.colores.gris_hierro, fg=self.colores.cyan_brillante)
        
        def on_leave(event):
            widget.configure(bg=color_original, fg=self.colores.texto_secundario)
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    

    
    def _extraer_datos_json(self, contenido, tipo):
        """Extraer datos de archivo JSON"""
        datos = []
        
        if isinstance(contenido, list):
            # Lista directa de elementos
            for item in contenido:
                dato = self._normalizar_dato(item, tipo)
                if dato:
                    datos.append(dato)
        elif isinstance(contenido, dict):
            # Buscar arrays dentro del diccionario
            for key, value in contenido.items():
                if isinstance(value, list):
                    for item in value:
                        dato = self._normalizar_dato(item, tipo)
                        if dato:
                            datos.append(dato)
        
        return datos
    
    def _procesar_fila_csv(self, row, tipo):
        """Procesar fila de CSV"""
        return self._normalizar_dato(row, tipo)
    
    def _procesar_archivo_texto(self, lineas, tipo):
        """Procesar archivo de texto línea por línea"""
        datos = []
        
        for linea in lineas:
            linea = linea.strip()
            if linea and not linea.startswith('#'):  # Ignorar comentarios
                if tipo == 'cve':
                    # Buscar patrones CVE
                    import re
                    cve_match = re.search(r'CVE-\d{4}-\d{4,}', linea)
                    if cve_match:
                        datos.append({
                            'id': cve_match.group(),
                            'descripcion': linea,
                            'severidad': 'Unknown'
                        })
                elif tipo == 'malware':
                    # Tratar cada línea como hash o nombre de malware
                    datos.append({
                        'nombre': linea,
                        'hash': linea if len(linea) in [32, 40, 64] else '',
                        'tipo': 'Custom'
                    })
                elif tipo == 'vulnerabilidades':
                    # Tratar como descripción de vulnerabilidad
                    datos.append({
                        'nombre': linea,
                        'descripcion': linea,
                        'severidad': 'Medium'
                    })
        
        return datos
    
    def _normalizar_dato(self, item, tipo):
        """Normalizar datos según el tipo de base de datos"""
        if not item:
            return None
            
        if isinstance(item, str):
            item = {'raw': item}
        
        if tipo == 'cve':
            return {
                'id': item.get('id', item.get('cve_id', item.get('CVE', item.get('raw', '')))),
                'descripcion': item.get('description', item.get('desc', item.get('summary', item.get('raw', '')))),
                'severidad': item.get('severity', item.get('score', item.get('cvss', 'Unknown'))),
                'fecha': item.get('published', item.get('date', '')),
                'referencias': item.get('references', [])
            }
        elif tipo == 'malware':
            return {
                'nombre': item.get('name', item.get('malware_name', item.get('raw', ''))),
                'hash': item.get('hash', item.get('md5', item.get('sha256', ''))),
                'tipo': item.get('type', item.get('family', 'Unknown')),
                'descripcion': item.get('description', item.get('details', ''))
            }
        elif tipo == 'vulnerabilidades':
            return {
                'nombre': item.get('name', item.get('vuln_name', item.get('raw', ''))),
                'descripcion': item.get('description', item.get('details', item.get('raw', ''))),
                'severidad': item.get('severity', item.get('risk', 'Medium')),
                'solucion': item.get('solution', item.get('fix', ''))
            }
        
        return None
    
    def _cambiar_vista(self, nombre_vista):
        """Cambiar a una vista específica"""
        try:
            if nombre_vista in self.vistas:
                # Limpiar área de contenido
                if self.area_contenido:
                    for widget in self.area_contenido.winfo_children():
                        widget.destroy()
                
                # Crear la nueva vista
                vista = self.vistas[nombre_vista]
                if hasattr(vista, 'crear_vista'):
                    vista.crear_vista()
                    self.logger.info(f"Vista {nombre_vista} creada exitosamente")
                else:
                    self.logger.warning(f"Vista {nombre_vista} no tiene método crear_vista")
            else:
                self.logger.error(f"Vista {nombre_vista} no encontrada")
        except Exception as e:
            self.logger.error(f"Error cambiando a vista {nombre_vista}: {e}")
            messagebox.showerror("Error", f"Error cargando vista {nombre_vista}: {e}")
    
    def _inicializar_vistas(self):
        """Inicializar vistas especializadas"""
        self.vistas = {
            'dashboard': VistaDashboard(self.area_contenido, self.controlador, self.colores),
            'escaneador': VistaEscaneador(self.area_contenido, self.controlador, self.colores),
            'auditoria_pam': VistaAuditoriaPAM(self.area_contenido, self.controlador, self.colores),
            'monitor': VistaMonitor(self.area_contenido, self.controlador, self.colores),
            'monitor_procesos': VistaMonitorProcesos(self.area_contenido, self.controlador, self.colores),
            'monitor_red': VistaMonitorRed(self.area_contenido, self.controlador, self.colores),
            'siem': VistaSIEM(self.area_contenido, self.controlador, self.colores),
            'cuarentena': VistaCuarentena(self.area_contenido, self.controlador, self.colores),
            'constructor_wordlists': VistaConstructorWordlists(self.area_contenido, self.controlador, self.colores),
            'reportes': VistaReportes(self.area_contenido, self.controlador, self.colores),
            'cheatsheets': VistaCheatsheets(self.area_contenido, self.controlador, self.colores)
        }
        
        # Registrar el dashboard con el controlador para estadísticas en tiempo real
        if self.controlador and 'dashboard' in self.vistas:
            self.controlador.registrar_dashboard(self.vistas['dashboard'])
            self.logger.info("Dashboard registrado con el controlador para estadísticas en tiempo real")
    
    def _iniciar_metricas_tiempo_real(self):
        """Iniciar sistema de métricas en tiempo real"""
        def callback_metricas(metricas):
            # Actualizar vista dashboard si está activa
            if (self.vista_actual == 'dashboard' and 'dashboard' in self.vistas and 
                self.root and hasattr(self.root, 'after')):
                self.root.after(0, lambda: self.vistas['dashboard'].actualizar_metricas(metricas))
        
        self.metricas_tiempo_real = MetricasTiempoReal(self.controlador, callback_metricas)
        self.metricas_tiempo_real.iniciar()
    
    def _mostrar_vista(self, vista_id):
        """Mostrar vista específica con resaltado del módulo activo"""
        if vista_id in self.vistas:
            # Actualizar vista actual
            vista_anterior = self.vista_actual
            self.vista_actual = vista_id
            
            # Resetear colores de todos los botones
            if hasattr(self, 'botones_navegacion'):
                for modulo, boton in self.botones_navegacion.items():
                    if modulo == vista_id:
                        # Resaltar módulo activo
                        boton.configure(
                            bg=self.colores.verde_terminal,
                            fg=self.colores.negro_profundo
                        )
                    else:
                        # Restaurar color normal
                        boton.configure(
                            bg=self.colores.gris_hierro,
                            fg=self.colores.texto_primario
                        )
            
            # Limpiar área de contenido
            if self.area_contenido:
                for widget in self.area_contenido.winfo_children():
                    widget.destroy()
            
            # Mostrar la vista
            if vista_id == 'auditoria_pam':
                # Vista de auditoría PAM requiere manejo especial
                self.vistas[vista_id].crear_vista(self.area_contenido)
            else:
                # Otras vistas usan el método estándar
                self.vistas[vista_id].crear_vista()
            
            self.logger.info(f"[VIEW] Vista {vista_id} mostrada")
            
            # Actualizar estado en barra inferior
            self._actualizar_estado_barra(vista_id)
    
    def _actualizar_estado_barra(self, vista_id):
        """Actualizar estado en la barra inferior"""
        nombres_vistas = {
            'dashboard': 'Inicio',
            'escaneador': 'Escáner',
            'auditoria_pam': 'Auditoría PAM',
            'monitor': 'Monitor del Sistema',
            'monitor_procesos': 'Monitor de Procesos',
            'monitor_red': 'Monitor de Red',
            'siem': 'Sistema SIEM', 
            'cuarentena': 'Gestor de Cuarentena',
            'reportes': 'Reportes y Análisis',
            'cheatsheets': 'Gestor de CheatSheets'
        }
        
        nombre_vista = nombres_vistas.get(vista_id, vista_id.upper())
        nuevo_estado = f"Módulo activo: {nombre_vista} • Sistema operativo"
        
        # Buscar y actualizar el label de estado en la barra
        for widget in self.barra_estado.winfo_children():
            if isinstance(widget, tk.Label) and "Listo" in widget.cget('text'):
                widget.configure(text=nuevo_estado)
                break
    
    # Métodos de navegación con nombres en español
    def _mostrar_dashboard(self):
        """Mostrar tablero de guerra principal"""
        self._mostrar_vista('dashboard')
    
    def _mostrar_escaneador(self):
        """Mostrar escáner de amenazas"""
        self._mostrar_vista('escaneador')
    
    def _mostrar_auditoria_pam(self):
        """Mostrar auditoría de autenticación PAM"""
        self._mostrar_vista('auditoria_pam')
    
    def _mostrar_monitor(self):
        """Mostrar vigilancia del sistema"""
        self._mostrar_vista('monitor')

    def _mostrar_monitor_procesos(self):
        """Mostrar monitor especializado de procesos"""
        self._mostrar_vista('monitor_procesos')

    def _mostrar_monitor_red(self):
        """Mostrar monitor especializado de red"""
        self._mostrar_vista('monitor_red')
    
    def _mostrar_siem(self):
        """Mostrar sistema SIEM"""
        self._mostrar_vista('siem')
    
    def _mostrar_cuarentena(self):
        """Mostrar prisión de archivos"""
        self._mostrar_vista('cuarentena')
    
    def _mostrar_constructor_wordlists(self):
        """Mostrar constructor de wordlists"""
        self._mostrar_vista('constructor_wordlists')
    
    def _mostrar_reportes(self):
        """Mostrar crónicas de batalla"""
        self._mostrar_vista('reportes')
    
    def _abrir_github(self):
        """Abrir página de GitHub"""
        try:
            webbrowser.open("https://github.com/DogSoulDev")
            self.logger.info(" Abriendo GitHub de DogSoulDev")
        except Exception as e:
            self.logger.error(f"Error abriendo GitHub: {e}")
            messagebox.showinfo("GitHub", "Visita: https://github.com/DogSoulDev")
    
    def _mostrar_cheatsheets(self):
        """Mostrar vista de gestión de cheatsheets"""
        self._mostrar_vista('cheatsheets')
    
    def _actualizar_sistema(self):
        """Actualizar el estado del sistema y recargar componentes"""
        try:
            self.logger.info("[REFRESH] Actualizando sistema...")
            
            # Actualizar métricas
            if self.metricas_tiempo_real:
                try:
                    # Intentar actualizar métricas usando getattr de forma segura
                    actualizar_metricas = getattr(self.metricas_tiempo_real, 'actualizar_metricas', None)
                    if actualizar_metricas and callable(actualizar_metricas):
                        actualizar_metricas()
                except Exception as e:
                    self.logger.warning(f"No se pudieron actualizar métricas: {e}")
            
            # Actualizar estado de la fortaleza
            if self.estado_fortaleza and hasattr(self.estado_fortaleza, 'set'):
                self.estado_fortaleza.set("SISTEMA ACTUALIZADO • CONEXIÓN SEGURA VERIFICADA")
            
            # Actualizar vista actual si existe
            if hasattr(self, 'vista_actual') and self.vista_actual:
                self._mostrar_vista(self.vista_actual)
            
            messagebox.showinfo("Sistema Actualizado", 
                              "[OK] Sistema actualizado correctamente\n"
                              "[STATS] Métricas refrescadas\n"
                              "[LOCK] Estado de seguridad verificado")
            
            self.logger.info("[OK] Sistema actualizado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error actualizando sistema: {e}")
            messagebox.showerror("Error de Actualización", 
                               f"[ERROR] Error actualizando sistema:\n{str(e)}")
    
    def _cerrar_aplicacion(self):
        """Cerrar aplicación correctamente limpiando todos los recursos"""
        try:
            self.logger.info("[SHIELD] Iniciando proceso de cierre seguro de la aplicación...")
            
            # Detener métricas de tiempo real
            if hasattr(self, 'metricas_tiempo_real') and self.metricas_tiempo_real:
                try:
                    self.metricas_tiempo_real.detener()
                    self.logger.info("[OK] Métricas de tiempo real detenidas")
                except Exception as e:
                    self.logger.error(f"Error deteniendo métricas: {e}")
            
            # Finalizar todas las vistas activas
            self._finalizar_vistas_activas()
            
            # Finalizar controlador principal
            if hasattr(self, 'controlador') and self.controlador:
                try:
                    # Verificar si finalizar es async o sync
                    if hasattr(self.controlador, 'finalizar') and callable(self.controlador.finalizar):
                        import asyncio
                        if asyncio.iscoroutinefunction(self.controlador.finalizar):
                            # Es async - crear nueva event loop si es necesario
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    # Crear nueva tarea para el método async
                                    asyncio.create_task(self.controlador.finalizar())
                                else:
                                    loop.run_until_complete(self.controlador.finalizar())
                            except RuntimeError:
                                # No hay loop activo, crear uno nuevo
                                asyncio.run(self.controlador.finalizar())
                        else:
                            # Es sync
                            self.controlador.finalizar()
                    self.logger.info("[OK] Controlador principal finalizado")
                except Exception as e:
                    self.logger.error(f"Error finalizando controlador: {e}")
            
            # Detener hilos restantes
            self._detener_hilos_interfaz()
            
            self.logger.info("[SYSTEM] Sistema Ares Aegis finalizado correctamente")
            
            # Cerrar ventana principal
            if hasattr(self, 'root') and self.root:
                self.root.quit()  # Salir del mainloop
                self.root.destroy()  # Destruir la ventana
            
        except Exception as e:
            self.logger.error(f"Error cerrando aplicación: {e}")
            # Forzar cierre en caso de error
            if hasattr(self, 'root') and self.root:
                try:
                    self.root.quit()
                    self.root.destroy()
                except:
                    pass
    
    def _finalizar_vistas_activas(self):
        """Finalizar todas las vistas activas para liberar recursos"""
        try:
            # Finalizar nuevas vistas del sistema MVC
            if hasattr(self, 'vistas') and self.vistas:
                for vista_id, vista in self.vistas.items():
                    if vista and hasattr(vista, 'finalizar'):
                        try:
                            vista.finalizar()
                            self.logger.info(f"[OK] Vista {vista_id} finalizada")
                        except Exception as e:
                            self.logger.error(f"Error finalizando vista {vista_id}: {e}")
            
            # Lista de vistas conocidas que pueden tener recursos activos (compatibilidad)
            vistas_con_recursos = [
                'vista_monitor', 'vista_escaneador', 'vista_cuarentena',
                'vista_reportes', 'vista_siem', 'vista_auditoria_pam'
            ]
            
            for vista_nombre in vistas_con_recursos:
                if hasattr(self, vista_nombre):
                    vista = getattr(self, vista_nombre)
                    if vista and hasattr(vista, 'destruir_vista'):
                        try:
                            vista.destruir_vista()
                            self.logger.info(f"[OK] Vista {vista_nombre} finalizada")
                        except Exception as e:
                            self.logger.error(f"Error finalizando {vista_nombre}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error finalizando vistas: {e}")
    
    def _detener_hilos_interfaz(self):
        """Detener hilos específicos de la interfaz"""
        try:
            import threading
            import time
            
            # Obtener hilos activos
            hilos_activos = threading.enumerate()
            hilos_interfaz = []
            
            for hilo in hilos_activos:
                if (hilo != threading.current_thread() and 
                    hilo.is_alive() and 
                    ('vista' in hilo.name.lower() or 
                     'interfaz' in hilo.name.lower() or
                     'update' in hilo.name.lower())):
                    hilos_interfaz.append(hilo)
            
            if hilos_interfaz:
                self.logger.info(f"[REFRESH] Finalizando {len(hilos_interfaz)} hilos de interfaz...")
                
                for hilo in hilos_interfaz:
                    try:
                        hilo.join(timeout=1.0)  # Timeout corto para interfaz
                        if not hilo.is_alive():
                            self.logger.info(f"[OK] Hilo {hilo.name} finalizado")
                        else:
                            self.logger.warning(f" Hilo {hilo.name} no respondió")
                    except Exception as e:
                        self.logger.error(f"Error finalizando hilo {hilo.name}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error deteniendo hilos de interfaz: {e}")
    
    def ejecutar(self):
        """Ejecutar la aplicación"""
        try:
            self.logger.info("[SYSTEM] Iniciando Sistema de Ciberseguridad Ares Aegis")
            if self.root and hasattr(self.root, 'mainloop'):
                self.root.mainloop()
            else:
                self.logger.error("[ERROR] No se puede ejecutar: ventana principal no inicializada")
        except Exception as e:
            self.logger.error(f"Error ejecutando aplicación: {e}")


# Alias para compatibilidad con código existente
InterfazCybersecSimple = InterfazPrincipalAresAegis
