#!/usr/bin/env python3
"""
Ares Aegis - Temas Modernos
Sistema de temas para la interfaz de usuario

Autor: DogSoulDev
Versión: 3.0.0
"""

from typing import Dict, Any, Optional, List


class TemaClaro:
    """Tema claro para la interfaz con colores modernos profesionales."""
    
    # Colores principales - Paleta profesional inspirada en aplicaciones de ciberseguridad modernas
    FONDO_PRINCIPAL = "#fafbfc"       # Gris ultra claro, profesional
    FONDO_SECUNDARIO = "#f1f3f4"      # Gris claro para barras de navegación
    FONDO_CARD = "#ffffff"            # Blanco puro para tarjetas con sombra
    FONDO_SIDEBAR = "#2c3e50"         # Azul gris oscuro para sidebar profesional
    TEXTO_PRINCIPAL = "#2d3436"       # Gris muy oscuro para máxima legibilidad
    TEXTO_SECUNDARIO = "#636e72"      # Gris medio para texto secundario
    TEXTO_MUTED = "#a2a8b0"          # Gris claro para texto deshabilitado
    TEXTO_SIDEBAR = "#ecf0f1"         # Texto claro para sidebar oscuro
    PRIMARIO = "#0984e3"             # Azul profesional para elementos principales
    SECUNDARIO = "#74b9ff"           # Azul claro para elementos secundarios
    ACCENT = "#6c5ce7"               # Violeta para elementos de acento
    EXITO = "#00b894"                # Verde profesional para éxito
    SUCCESS = "#00b894"              # Alias para éxito
    WARNING = "#fdcb6e"              # Amarillo profesional para advertencias
    DANGER = "#e17055"               # Rojo profesional para errores/peligro
    ERROR = "#e17055"                # Alias para peligro
    INFO = "#74b9ff"                 # Azul claro para información
    BORDER = "#ddd"                  # Color de bordes sutil
    SHADOW = "#00000010"             # Sombra muy sutil
    HOVER = "#f8f9fa"                # Color de hover sutil
    
    # Colores específicos para ciberseguridad - Inspirados en dashboards profesionales
    AMENAZA_CRITICA = "#d63031"      # Rojo intenso profesional
    AMENAZA_ALTA = "#e17055"         # Rojo-naranja para amenazas altas
    AMENAZA_MEDIA = "#f39c12"        # Naranja profesional
    AMENAZA_BAJA = "#f1c40f"         # Amarillo para amenazas bajas
    PROTEGIDO = "#00b894"            # Verde profesional para estado seguro
    ESCANEANDO = "#0984e3"           # Azul para procesos activos
    MONITOREANDO = "#6c5ce7"         # Violeta para monitoreo
    DESCONOCIDO = "#95a5a6"          # Gris para estados indefinidos
    CUARENTENA = "#e67e22"           # Naranja para elementos en cuarentena
    LIMPIO = "#27ae60"               # Verde para elementos limpios
    
    # Colores para gráficos y métricas
    GRAFICO_1 = "#0984e3"            # Azul principal
    GRAFICO_2 = "#00b894"            # Verde
    GRAFICO_3 = "#e17055"            # Rojo-naranja
    GRAFICO_4 = "#6c5ce7"            # Violeta
    GRAFICO_5 = "#fdcb6e"            # Amarillo
    
    @staticmethod
    def obtener_colores() -> Dict[str, str]:
        """Retorna los colores del tema claro."""
        return {
            "bg_principal": TemaClaro.FONDO_PRINCIPAL,
            "bg_secundario": TemaClaro.FONDO_SECUNDARIO,
            "bg_card": TemaClaro.FONDO_CARD,
            "bg_sidebar": TemaClaro.FONDO_SIDEBAR,
            "text_principal": TemaClaro.TEXTO_PRINCIPAL,
            "text_secundario": TemaClaro.TEXTO_SECUNDARIO,
            "text_muted": TemaClaro.TEXTO_MUTED,
            "text_sidebar": TemaClaro.TEXTO_SIDEBAR,
            "primario": TemaClaro.PRIMARIO,
            "secundario": TemaClaro.SECUNDARIO,
            "accent": TemaClaro.ACCENT,
            "success": TemaClaro.SUCCESS,
            "warning": TemaClaro.WARNING,
            "danger": TemaClaro.DANGER,
            "info": TemaClaro.INFO,
            "border": TemaClaro.BORDER,
            "shadow": TemaClaro.SHADOW,
            "hover": TemaClaro.HOVER,
            "amenaza_critica": TemaClaro.AMENAZA_CRITICA,
            "amenaza_alta": TemaClaro.AMENAZA_ALTA,
            "amenaza_media": TemaClaro.AMENAZA_MEDIA,
            "amenaza_baja": TemaClaro.AMENAZA_BAJA,
            "protegido": TemaClaro.PROTEGIDO,
            "escaneando": TemaClaro.ESCANEANDO,
            "monitoreando": TemaClaro.MONITOREANDO,
            "desconocido": TemaClaro.DESCONOCIDO,
            "cuarentena": TemaClaro.CUARENTENA,
            "limpio": TemaClaro.LIMPIO
        }
    
    @staticmethod
    def obtener_fuentes() -> Dict[str, Any]:
        """Retorna la configuración de fuentes modernas."""
        return {
            "titulo": ("Segoe UI", 18, "bold"),
            "subtitulo": ("Segoe UI", 14, "bold"),
            "subtitulo_card": ("Segoe UI", 12, "bold"),
            "normal": ("Segoe UI", 10),
            "pequeña": ("Segoe UI", 9),
            "codigo": ("Consolas", 10),
            "monospace": ("Liberation Mono", 9),
            "icono": ("Segoe UI Symbol", 14),
            "icono_grande": ("Segoe UI Symbol", 20),
            "metrica": ("Segoe UI", 24, "bold"),
            "badge": ("Segoe UI", 8, "bold")
        }


class TemaOscuro:
    """Tema oscuro para la interfaz con colores modernos profesionales."""
    
    # Colores principales - Paleta oscura moderna y profesional
    FONDO_PRINCIPAL = "#1e1e2e"       # Gris muy oscuro moderno
    FONDO_SECUNDARIO = "#313244"      # Gris oscuro para navegación
    FONDO_CARD = "#313244"            # Gris oscuro para tarjetas
    FONDO_SIDEBAR = "#181825"         # Negro azulado para sidebar
    TEXTO_PRINCIPAL = "#cdd6f4"       # Blanco azulado para texto principal
    TEXTO_SECUNDARIO = "#bac2de"      # Gris azulado para texto secundario
    TEXTO_MUTED = "#6c7086"          # Gris medio para texto deshabilitado
    TEXTO_SIDEBAR = "#f38ba8"         # Rosa sutil para sidebar
    PRIMARIO = "#89b4fa"             # Azul claro profesional
    SECUNDARIO = "#74c7ec"           # Cian para elementos secundarios
    ACCENT = "#cba6f7"               # Violeta para elementos de acento
    EXITO = "#a6e3a1"                # Verde claro para éxito
    SUCCESS = "#a6e3a1"              # Alias para éxito
    WARNING = "#f9e2af"              # Amarillo claro para advertencias
    DANGER = "#f38ba8"               # Rosa para errores/peligro
    ERROR = "#f38ba8"                # Alias para peligro
    INFO = "#74c7ec"                 # Cian para información
    BORDER = "#45475a"               # Color de bordes oscuro
    SHADOW = "#00000040"             # Sombra más intensa
    HOVER = "#45475a"                # Color de hover oscuro
    
    # Colores específicos para ciberseguridad - Tema oscuro profesional
    AMENAZA_CRITICA = "#f38ba8"      # Rosa intenso para amenazas críticas
    AMENAZA_ALTA = "#fab387"         # Naranja claro para amenazas altas
    AMENAZA_MEDIA = "#f9e2af"        # Amarillo claro para amenazas medias
    AMENAZA_BAJA = "#a6e3a1"         # Verde claro para amenazas bajas
    PROTEGIDO = "#a6e3a1"            # Verde claro para estado seguro
    ESCANEANDO = "#89b4fa"           # Azul claro para procesos
    MONITOREANDO = "#cba6f7"         # Violeta para monitoreo
    DESCONOCIDO = "#6c7086"          # Gris para estados indefinidos
    CUARENTENA = "#fab387"           # Naranja claro para cuarentena
    LIMPIO = "#a6e3a1"               # Verde claro para elementos limpios
    
    # Colores para gráficos y métricas
    GRAFICO_1 = "#89b4fa"            # Azul claro
    GRAFICO_2 = "#a6e3a1"            # Verde claro
    GRAFICO_3 = "#f38ba8"            # Rosa
    GRAFICO_4 = "#cba6f7"            # Violeta
    GRAFICO_5 = "#f9e2af"            # Amarillo claro
    
    @staticmethod
    def obtener_colores() -> Dict[str, str]:
        """Retorna los colores del tema oscuro."""
        return {
            "bg_principal": TemaOscuro.FONDO_PRINCIPAL,
            "bg_secundario": TemaOscuro.FONDO_SECUNDARIO,
            "bg_card": TemaOscuro.FONDO_CARD,
            "bg_sidebar": TemaOscuro.FONDO_SIDEBAR,
            "text_principal": TemaOscuro.TEXTO_PRINCIPAL,
            "text_secundario": TemaOscuro.TEXTO_SECUNDARIO,
            "text_muted": TemaOscuro.TEXTO_MUTED,
            "text_sidebar": TemaOscuro.TEXTO_SIDEBAR,
            "primario": TemaOscuro.PRIMARIO,
            "secundario": TemaOscuro.SECUNDARIO,
            "accent": TemaOscuro.ACCENT,
            "success": TemaOscuro.SUCCESS,
            "warning": TemaOscuro.WARNING,
            "danger": TemaOscuro.DANGER,
            "info": TemaOscuro.INFO,
            "border": TemaOscuro.BORDER,
            "shadow": TemaOscuro.SHADOW,
            "hover": TemaOscuro.HOVER,
            "amenaza_critica": TemaOscuro.AMENAZA_CRITICA,
            "amenaza_alta": TemaOscuro.AMENAZA_ALTA,
            "amenaza_media": TemaOscuro.AMENAZA_MEDIA,
            "amenaza_baja": TemaOscuro.AMENAZA_BAJA,
            "protegido": TemaOscuro.PROTEGIDO,
            "escaneando": TemaOscuro.ESCANEANDO,
            "monitoreando": TemaOscuro.MONITOREANDO,
            "desconocido": TemaOscuro.DESCONOCIDO,
            "cuarentena": TemaOscuro.CUARENTENA,
            "limpio": TemaOscuro.LIMPIO
        }
    
    @staticmethod
    def obtener_fuentes() -> Dict[str, Any]:
        """Retorna la configuración de fuentes modernas."""
        return {
            "titulo": ("Segoe UI", 18, "bold"),
            "subtitulo": ("Segoe UI", 14, "bold"),
            "subtitulo_card": ("Segoe UI", 12, "bold"),
            "normal": ("Segoe UI", 10),
            "pequeña": ("Segoe UI", 9),
            "codigo": ("Consolas", 10),
            "monospace": ("Liberation Mono", 9),
            "icono": ("Segoe UI Symbol", 14),
            "icono_grande": ("Segoe UI Symbol", 20),
            "metrica": ("Segoe UI", 24, "bold"),
            "badge": ("Segoe UI", 8, "bold")
        }


class ComponentesModernos:
    """Componentes modernos ultra-profesionales para la interfaz usando solo Python/Tkinter."""
    
    @staticmethod
    def crear_boton_ultra_moderno(parent, texto: str, comando=None, estilo: str = "primario", icono: Optional[str] = None):
        """Crea un botón moderno ultra estilizado con efectos visuales."""
        import tkinter as tk
        from typing import Callable, Optional
        
        # Colores según el estilo - Paleta profesional
        estilos = {
            "primario": {"bg": "#0984e3", "fg": "#ffffff", "hover": "#0770c4", "active": "#055a9b"},
            "secundario": {"bg": "#74b9ff", "fg": "#ffffff", "hover": "#5ba7ff", "active": "#4295ff"},
            "exito": {"bg": "#00b894", "fg": "#ffffff", "hover": "#00a085", "active": "#008876"},
            "peligro": {"bg": "#e17055", "fg": "#ffffff", "hover": "#dc6249", "active": "#d7543d"},
            "advertencia": {"bg": "#fdcb6e", "fg": "#2d3436", "hover": "#fcc74b", "active": "#fbc328"},
            "outline": {"bg": "#ffffff", "fg": "#0984e3", "hover": "#f8f9fa", "active": "#e9ecef"},
            "ghost": {"bg": "#fafbfc", "fg": "#636e72", "hover": "#f1f3f4", "active": "#e9ecef"}
        }
        
        color_config = estilos.get(estilo, estilos["primario"])
        
        try:
            bg_color = parent.cget('bg') if hasattr(parent, 'cget') else "#ffffff"
        except:
            bg_color = "#ffffff"
        
        # Frame contenedor con padding
        frame = tk.Frame(parent, bg=bg_color)
        
        # Crear botón con estilo moderno
        boton = tk.Button(
            frame,
            text=f"{icono} {texto}" if icono else texto,
            command=comando if comando is not None else lambda: None,
            bg=color_config["bg"],
            fg=color_config["fg"],
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 10, "normal"),
            padx=20,
            pady=10
        )
        
        # Efectos de hover y click
        def on_enter(e):
            boton.config(bg=color_config["hover"])
            
        def on_leave(e):
            boton.config(bg=color_config["bg"])
            
        def on_click(e):
            boton.config(bg=color_config["active"])
            boton.after(100, lambda: boton.config(bg=color_config["hover"]))
        
        boton.bind("<Enter>", on_enter)
        boton.bind("<Leave>", on_leave)
        boton.bind("<Button-1>", on_click)
        
        boton.pack(fill=tk.BOTH, expand=True)
        return frame
    
    @staticmethod
    def crear_card_ultra_moderna(parent, titulo: str = "", descripcion: str = "", padding: int = 20, 
                                icono: Optional[str] = None, color_acento: str = "#0984e3"):
        """Crea una tarjeta moderna ultra estilizada con sombra y efectos."""
        import tkinter as tk
        
        # Container principal con efecto de elevación
        container = tk.Frame(
            parent,
            bg="#ffffff",
            relief="flat",
            borderwidth=0,
            highlightbackground="#e0e6ed",
            highlightthickness=1
        )
        
        # Simular sombra con frames adicionales
        shadow_frame = tk.Frame(parent, bg="#f1f3f4", height=2)
        shadow_frame.place(in_=container, relx=0.01, rely=0.01, relwidth=0.99, relheight=0.99)
        
        # Header de la tarjeta si hay título
        if titulo:
            header_frame = tk.Frame(container, bg="#fafbfc", height=60)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            # Frame para icono y título
            title_frame = tk.Frame(header_frame, bg="#fafbfc")
            title_frame.pack(fill=tk.BOTH, expand=True, padx=padding, pady=15)
            
            # Icono si se proporciona
            if icono:
                icon_label = tk.Label(
                    title_frame,
                    text=icono,
                    font=("Segoe UI", 16),
                    bg="#fafbfc",
                    fg=color_acento
                )
                icon_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Título
            titulo_label = tk.Label(
                title_frame,
                text=titulo,
                font=("Segoe UI", 14, "bold"),
                bg="#fafbfc",
                fg="#2d3436"
            )
            titulo_label.pack(side=tk.LEFT)
            
            # Descripción si se proporciona
            if descripcion:
                desc_label = tk.Label(
                    header_frame,
                    text=descripcion,
                    font=("Segoe UI", 9),
                    bg="#fafbfc",
                    fg="#636e72"
                )
                desc_label.pack(padx=padding, pady=(0, 10), anchor=tk.W)
        
        # Contenido de la tarjeta
        content_frame = tk.Frame(container, bg="#ffffff")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
        
        # Efectos de hover
        def on_enter(e):
            container.config(highlightbackground="#74b9ff")
            
        def on_leave(e):
            container.config(highlightbackground="#e0e6ed")
        
        container.bind("<Enter>", on_enter)
        container.bind("<Leave>", on_leave)
        
        # Propiedades para acceso
        setattr(container, 'content_frame', content_frame)
        setattr(content_frame, 'FONDO_CARD', "#ffffff")
        
        return container, content_frame
    
    @staticmethod
    def crear_badge_estado(parent, texto: str, estado: str = "info"):
        """Crea un badge/etiqueta de estado moderno."""
        import tkinter as tk
        
        # Colores según el estado
        colores_estado = {
            "exito": {"bg": "#d1f2eb", "fg": "#00b894", "border": "#00b894"},
            "peligro": {"bg": "#fdedec", "fg": "#e17055", "border": "#e17055"},
            "advertencia": {"bg": "#fef9e7", "fg": "#f39c12", "border": "#f39c12"},
            "info": {"bg": "#e3f2fd", "fg": "#0984e3", "border": "#0984e3"},
            "neutral": {"bg": "#f8f9fa", "fg": "#636e72", "border": "#dee2e6"}
        }
        
        colores = colores_estado.get(estado, colores_estado["info"])
        
        # Frame del badge
        badge_frame = tk.Frame(
            parent,
            bg=colores["bg"],
            relief="solid",
            borderwidth=1,
            highlightbackground=colores["border"],
            highlightthickness=1
        )
        
        # Label del texto
        label = tk.Label(
            badge_frame,
            text=texto,
            bg=colores["bg"],
            fg=colores["fg"],
            font=("Segoe UI", 8, "bold"),
            padx=8,
            pady=2
        )
        label.pack()
        
        return badge_frame
    
    @staticmethod
    def crear_input_moderno(parent, placeholder: str = "", tipo: str = "texto"):
        """Crea un input moderno con placeholder y efectos."""
        import tkinter as tk
        
        # Frame contenedor
        input_frame = tk.Frame(parent, bg="#ffffff")
        
        # Variable para el texto
        var = tk.StringVar()
        
        # Entry principal
        entry = tk.Entry(
            input_frame,
            textvariable=var,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#2d3436",
            relief="flat",
            borderwidth=0,
            insertbackground="#0984e3"
        )
        
        # Frame para el borde personalizado
        border_frame = tk.Frame(
            input_frame,
            bg="#dee2e6",
            height=2
        )
        
        entry.pack(fill=tk.X, padx=12, pady=(12, 4))
        border_frame.pack(fill=tk.X)
        
        # Placeholder
        if placeholder:
            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg="#2d3436")
                border_frame.config(bg="#0984e3")
                
            def on_focus_out(e):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg="#a2a8b0")
                border_frame.config(bg="#dee2e6")
            
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
            
            # Configurar placeholder inicial
            entry.insert(0, placeholder)
            entry.config(fg="#a2a8b0")
        
        # Configurar tipo específico
        if tipo == "password":
            entry.config(show="*")
        
        setattr(input_frame, 'entry', entry)
        setattr(input_frame, 'get_value', lambda: var.get() if var.get() != placeholder else "")
        
        return input_frame
    
    @staticmethod
    def crear_metrica_profesional(parent, valor: str, etiqueta: str, icono: str = "📊", 
                                 color: str = "#0984e3", tendencia: Optional[str] = None):
        """Crea una métrica profesional con iconos y tendencias."""
        import tkinter as tk
        
        # Frame principal
        metric_frame = tk.Frame(parent, bg="#ffffff")
        
        # Frame superior con icono y valor
        top_frame = tk.Frame(metric_frame, bg="#ffffff")
        top_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Icono
        icon_label = tk.Label(
            top_frame,
            text=icono,
            font=("Segoe UI", 20),
            bg="#ffffff",
            fg=color
        )
        icon_label.pack(side=tk.LEFT, padx=(10, 15))
        
        # Valor
        valor_label = tk.Label(
            top_frame,
            text=valor,
            font=("Segoe UI", 24, "bold"),
            bg="#ffffff",
            fg="#2d3436"
        )
        valor_label.pack(side=tk.LEFT)
        
        # Tendencia si se proporciona
        if tendencia:
            trend_color = "#00b894" if tendencia.startswith("↑") else "#e17055" if tendencia.startswith("↓") else "#636e72"
            trend_label = tk.Label(
                top_frame,
                text=tendencia,
                font=("Segoe UI", 12),
                bg="#ffffff",
                fg=trend_color
            )
            trend_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Etiqueta
        etiqueta_label = tk.Label(
            metric_frame,
            text=etiqueta,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#636e72"
        )
        etiqueta_label.pack(pady=(0, 10))
        
        return metric_frame
    
    @staticmethod
    def crear_progress_moderno(parent, valor: int = 0, maximo: int = 100, color: str = "#0984e3"):
        """Crea una barra de progreso moderna."""
        import tkinter as tk
        
        # Frame contenedor
        progress_frame = tk.Frame(parent, bg="#ffffff")
        
        # Fondo de la barra
        bg_frame = tk.Frame(
            progress_frame,
            bg="#f1f3f4",
            height=8
        )
        bg_frame.pack(fill=tk.X, padx=10, pady=5)
        bg_frame.pack_propagate(False)
        
        # Barra de progreso
        progress_bar = tk.Frame(
            bg_frame,
            bg=color,
            height=8
        )
        
        # Calcular ancho basado en el valor
        def actualizar_progreso(nuevo_valor):
            porcentaje = min(nuevo_valor / maximo, 1.0)
            progress_bar.place(relwidth=porcentaje, relheight=1.0)
        
        # Configurar progreso inicial
        actualizar_progreso(valor)
        
        # Label con porcentaje
        porcentaje_label = tk.Label(
            progress_frame,
            text=f"{int((valor/maximo)*100)}%",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#636e72"
        )
        porcentaje_label.pack(pady=(2, 5))
        
        # Método para actualizar
        setattr(progress_frame, 'actualizar', lambda v: (
            actualizar_progreso(v),
            porcentaje_label.config(text=f"{int((v/maximo)*100)}%")
        ))
        
        return progress_frame
    
    @staticmethod
    def crear_sidebar_profesional(parent, ancho: int = 250):
        """Crea una sidebar profesional moderna para navegación."""
        import tkinter as tk
        
        # Frame principal de la sidebar
        sidebar_frame = tk.Frame(
            parent,
            bg="#2c3e50",
            width=ancho
        )
        sidebar_frame.pack_propagate(False)
        
        # Header de la sidebar
        header_frame = tk.Frame(sidebar_frame, bg="#34495e", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Logo/Título
        logo_label = tk.Label(
            header_frame,
            text="🛡️ Ares Aegis",
            font=("Segoe UI", 16, "bold"),
            bg="#34495e",
            fg="#ecf0f1"
        )
        logo_label.pack(expand=True)
        
        # Frame para navegación
        nav_frame = tk.Frame(sidebar_frame, bg="#2c3e50")
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=20)
        
        setattr(sidebar_frame, 'nav_frame', nav_frame)
        return sidebar_frame
    
    @staticmethod
    def crear_item_navegacion(parent, texto: str, icono: str, comando=None, activo: bool = False):
        """Crea un item de navegación para la sidebar."""
        import tkinter as tk
        
        # Colores según estado
        if activo:
            bg_color = "#3498db"
            fg_color = "#ffffff"
        else:
            bg_color = "#2c3e50"
            fg_color = "#bdc3c7"
        
        # Frame del item
        item_frame = tk.Frame(parent, bg=bg_color, cursor="hand2")
        item_frame.pack(fill=tk.X, pady=2)
        
        # Label con icono y texto
        item_label = tk.Label(
            item_frame,
            text=f"{icono}  {texto}",
            font=("Segoe UI", 11),
            bg=bg_color,
            fg=fg_color,
            anchor="w",
            padx=15,
            pady=12
        )
        item_label.pack(fill=tk.X)
        
        # Efectos hover
        def on_enter(e):
            if not activo:
                item_frame.config(bg="#34495e")
                item_label.config(bg="#34495e", fg="#ecf0f1")
                
        def on_leave(e):
            if not activo:
                item_frame.config(bg="#2c3e50")
                item_label.config(bg="#2c3e50", fg="#bdc3c7")
        
        def on_click(e):
            if comando:
                comando()
        
        item_frame.bind("<Enter>", on_enter)
        item_frame.bind("<Leave>", on_leave)
        item_frame.bind("<Button-1>", on_click)
        item_label.bind("<Enter>", on_enter)
        item_label.bind("<Leave>", on_leave)
        item_label.bind("<Button-1>", on_click)
        
        return item_frame
    
    @staticmethod
    def crear_alerta_profesional(parent, mensaje: str, tipo: str = "info", accion: Optional[str] = None):
        """Crea una alerta profesional moderna."""
        import tkinter as tk
        
        # Configuración por tipo
        tipos_config = {
            "exito": {
                "bg": "#d4edda", "fg": "#155724", "border": "#c3e6cb",
                "icono": "✅", "titulo": "Éxito"
            },
            "error": {
                "bg": "#f8d7da", "fg": "#721c24", "border": "#f5c6cb",
                "icono": "❌", "titulo": "Error"
            },
            "advertencia": {
                "bg": "#fff3cd", "fg": "#856404", "border": "#ffeaa7",
                "icono": "⚠️", "titulo": "Advertencia"
            },
            "info": {
                "bg": "#d1ecf1", "fg": "#0c5460", "border": "#bee5eb",
                "icono": "ℹ️", "titulo": "Información"
            },
            "critico": {
                "bg": "#f5c6cb", "fg": "#721c24", "border": "#f1b0b7",
                "icono": "🚨", "titulo": "Crítico"
            }
        }
        
        config = tipos_config.get(tipo, tipos_config["info"])
        
        # Frame principal
        alert_frame = tk.Frame(
            parent,
            bg=config["bg"],
            relief="solid",
            borderwidth=1,
            highlightbackground=config["border"],
            highlightthickness=1
        )
        
        # Frame contenido
        content_frame = tk.Frame(alert_frame, bg=config["bg"])
        content_frame.pack(fill=tk.X, padx=15, pady=12)
        
        # Frame superior con icono y título
        top_frame = tk.Frame(content_frame, bg=config["bg"])
        top_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Icono y título
        title_label = tk.Label(
            top_frame,
            text=f"{config['icono']} {config['titulo']}",
            font=("Segoe UI", 10, "bold"),
            bg=config["bg"],
            fg=config["fg"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Botón cerrar
        close_btn = tk.Label(
            top_frame,
            text="✕",
            font=("Segoe UI", 10, "bold"),
            bg=config["bg"],
            fg=config["fg"],
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda e: alert_frame.destroy())
        
        # Mensaje
        msg_label = tk.Label(
            content_frame,
            text=mensaje,
            font=("Segoe UI", 9),
            bg=config["bg"],
            fg=config["fg"],
            wraplength=400,
            justify=tk.LEFT
        )
        msg_label.pack(anchor="w")
        
        # Botón de acción si se proporciona
        if accion:
            action_btn = ComponentesModernos.crear_boton_ultra_moderno(
                content_frame, accion, estilo="primario"
            )
            action_btn.pack(anchor="w", pady=(10, 0))
        
        return alert_frame
    
    @staticmethod
    def crear_tabla_moderna(parent, columnas: List[str], datos: Optional[List[List[str]]] = None):
        """Crea una tabla moderna con estilo profesional."""
        import tkinter as tk
        
        # Frame contenedor
        table_frame = tk.Frame(parent, bg="#ffffff")
        
        # Frame para headers
        header_frame = tk.Frame(table_frame, bg="#f8f9fa", height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Headers
        for i, columna in enumerate(columnas):
            header_label = tk.Label(
                header_frame,
                text=columna,
                font=("Segoe UI", 10, "bold"),
                bg="#f8f9fa",
                fg="#495057",
                relief="flat",
                borderwidth=1,
                highlightbackground="#dee2e6"
            )
            header_label.grid(row=0, column=i, sticky="ew", padx=1)
            header_frame.grid_columnconfigure(i, weight=1)
        
        # Frame para datos con scroll
        data_frame = tk.Frame(table_frame, bg="#ffffff")
        data_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar para scroll
        canvas = tk.Canvas(data_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = tk.Scrollbar(data_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Datos si se proporcionan
        if datos:
            for i, fila in enumerate(datos):
                for j, valor in enumerate(fila):
                    bg_color = "#ffffff" if i % 2 == 0 else "#f8f9fa"
                    cell_label = tk.Label(
                        scrollable_frame,
                        text=valor,
                        font=("Segoe UI", 9),
                        bg=bg_color,
                        fg="#495057",
                        relief="flat",
                        borderwidth=1,
                        highlightbackground="#dee2e6",
                        padx=10,
                        pady=8
                    )
                    cell_label.grid(row=i, column=j, sticky="ew", padx=1, pady=1)
                    scrollable_frame.grid_columnconfigure(j, weight=1)
        
        # Métodos para manipular datos
        def agregar_fila(nueva_fila):
            i = len(scrollable_frame.winfo_children()) // len(columnas)
            for j, valor in enumerate(nueva_fila):
                bg_color = "#ffffff" if i % 2 == 0 else "#f8f9fa"
                cell_label = tk.Label(
                    scrollable_frame,
                    text=valor,
                    font=("Segoe UI", 9),
                    bg=bg_color,
                    fg="#495057",
                    relief="flat",
                    borderwidth=1,
                    highlightbackground="#dee2e6",
                    padx=10,
                    pady=8
                )
                cell_label.grid(row=i, column=j, sticky="ew", padx=1, pady=1)
        
        setattr(table_frame, 'agregar_fila', agregar_fila)
        return table_frame
    
    @staticmethod
    def estilo_boton(tema: str = "claro") -> Dict[str, Any]:
        """Retorna el estilo para botones."""
        if tema == "oscuro":
            return {
                "bg": "#4dabf7",
                "fg": "#ffffff",
                "activebackground": "#339af0",
                "activeforeground": "#ffffff",
                "relief": "flat",
                "borderwidth": 0,
                "cursor": "hand2"
            }
        else:
            return {
                "bg": "#007bff",
                "fg": "#ffffff",
                "activebackground": "#0056b3",
                "activeforeground": "#ffffff",
                "relief": "flat",
                "borderwidth": 0,
                "cursor": "hand2"
            }
    
    @staticmethod
    def estilo_entrada(tema: str = "claro") -> Dict[str, Any]:
        """Retorna el estilo para campos de entrada."""
        if tema == "oscuro":
            return {
                "bg": "#3c3c3c",
                "fg": "#ffffff",
                "insertbackground": "#ffffff",
                "selectbackground": "#4dabf7",
                "selectforeground": "#ffffff",
                "relief": "flat",
                "borderwidth": 1,
                "highlightthickness": 1,
                "highlightcolor": "#4dabf7"
            }
        else:
            return {
                "bg": "#ffffff",
                "fg": "#212529",
                "insertbackground": "#212529",
                "selectbackground": "#007bff",
                "selectforeground": "#ffffff",
                "relief": "flat",
                "borderwidth": 1,
                "highlightthickness": 1,
                "highlightcolor": "#007bff"
            }
    
    @staticmethod
    def estilo_texto(tema: str = "claro") -> Dict[str, Any]:
        """Retorna el estilo para áreas de texto."""
        if tema == "oscuro":
            return {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "insertbackground": "#ffffff",
                "selectbackground": "#4dabf7",
                "selectforeground": "#ffffff",
                "relief": "flat",
                "borderwidth": 1,
                "wrap": "word"
            }
        else:
            return {
                "bg": "#ffffff",
                "fg": "#212529",
                "insertbackground": "#212529",
                "selectbackground": "#007bff",
                "selectforeground": "#ffffff",
                "relief": "flat",
                "borderwidth": 1,
                "wrap": "word"
            }
    
    @staticmethod
    def estilo_marco(tema: str = "claro") -> Dict[str, Any]:
        """Retorna el estilo para marcos."""
        if tema == "oscuro":
            return {
                "bg": "#3c3c3c",
                "relief": "flat",
                "borderwidth": 1,
                "highlightbackground": "#555555"
            }
        else:
            return {
                "bg": "#f8f9fa",
                "relief": "flat", 
                "borderwidth": 1,
                "highlightbackground": "#dee2e6"
            }
    
    @staticmethod
    def aplicar_tema_ventana(ventana, tema: str = "claro") -> None:
        """Aplica un tema a una ventana completa."""
        colores = TemaClaro.obtener_colores() if tema == "claro" else TemaOscuro.obtener_colores()
        
        try:
            ventana.configure(bg=colores["bg_principal"])
        except Exception:
            pass  # Algunos widgets no soportan todos los atributos
    
    @staticmethod
    def configurar_widget(widget, tipo: str, tema: str = "claro") -> None:
        """Configura un widget con el estilo apropiado."""
        try:
            if tipo == "boton":
                widget.configure(**ComponentesModernos.estilo_boton(tema))
            elif tipo == "entrada":
                widget.configure(**ComponentesModernos.estilo_entrada(tema))
            elif tipo == "texto":
                widget.configure(**ComponentesModernos.estilo_texto(tema))
            elif tipo == "marco":
                widget.configure(**ComponentesModernos.estilo_marco(tema))
        except Exception:
            pass  # Algunos widgets pueden no soportar ciertos atributos


def obtener_tema_sistema() -> str:
    """Intenta detectar el tema del sistema."""
    try:
        import platform
        if platform.system() == "Windows":
            # En Windows, por defecto usamos tema claro
            return "claro"
        elif platform.system() == "Darwin":  # macOS
            # En macOS, por defecto usamos tema claro
            return "claro"
        else:  # Linux y otros
            # En Linux, por defecto usamos tema claro
            return "claro"
    except Exception:
        return "claro"


def crear_esquema_colores_personalizado(base: str = "claro") -> Dict[str, str]:
    """Crea un esquema de colores personalizado basado en un tema base."""
    if base == "oscuro":
        return TemaOscuro.obtener_colores()
    else:
        return TemaClaro.obtener_colores()


# Configuración por defecto
TEMA_POR_DEFECTO = obtener_tema_sistema()
COLORES_POR_DEFECTO = crear_esquema_colores_personalizado(TEMA_POR_DEFECTO)
FUENTES_POR_DEFECTO = TemaClaro.obtener_fuentes() if TEMA_POR_DEFECTO == "claro" else TemaOscuro.obtener_fuentes()

__all__ = [
    'TemaClaro',
    'TemaOscuro', 
    'ComponentesModernos',
    'obtener_tema_sistema',
    'crear_esquema_colores_personalizado',
    'TEMA_POR_DEFECTO',
    'COLORES_POR_DEFECTO',
    'FUENTES_POR_DEFECTO'
]
