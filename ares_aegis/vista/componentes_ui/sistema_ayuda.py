#!/usr/bin/env python3
"""
Sistema de Ayuda Contextual para Ares Aegis
===========================================

Proporciona ayuda contextual e instrucciones para cada dashboard y funcionalidad.
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
from typing import Dict, Any
from ...utils.utils_ayuda_logging import configurar_logger_modulo


class SistemaAyuda:
    """Sistema de ayuda contextual con iconos de información"""
    
    def __init__(self, colores):
        self.colores = colores
        self.logger = configurar_logger_modulo("sistema_ayuda")
        self.ayuda_config = self._cargar_configuracion_ayuda()
        
    def _cargar_configuracion_ayuda(self) -> Dict[str, Any]:
        """Carga la configuración de ayuda desde archivo JSON"""
        config_path = "configuracion/sistema_ayuda.json"
        
        # Configuración por defecto
        config_default = {
            "dashboard": {
                "titulo": "[SYSTEM] Dashboard Principal - Centro de Control",
                "descripcion": "Panel principal donde puedes ver el estado general de tu sistema",
                "funciones": [
                    "[STATS] Ver métricas del sistema en tiempo real",
                    " Acceder al terminal integrado",
                    " Monitorear CPU, memoria y disco",
                    " Navegar rápidamente a otras funciones"
                ],
                "tips": [
                    " Las métricas se actualizan automáticamente cada 5 segundos",
                    " Usa el terminal integrado para comandos rápidos",
                    " Los colores indican el estado: Verde=Bueno, Naranja=Cuidado, Rojo=Crítico"
                ]
            },
            "escaner": {
                "titulo": " Escáner de Vulnerabilidades",
                "descripcion": "Herramienta para detectar vulnerabilidades y amenazas en tu sistema",
                "funciones": [
                    " Análisis completo del sistema",
                    " Análisis de directorios específicos",
                    " Detección de malware y archivos sospechosos",
                    " Generación de informes detallados"
                ],
                "tips": [
                    " Ejecuta análisis regulares para mantener tu sistema seguro",
                    " El análisis completo puede tardar varios minutos",
                    " Revisa siempre los hallazgos antes de realizar acciones"
                ]
            },
            "auditoria_pam": {
                "titulo": "[LOCK] Auditoría de Autenticación PAM",
                "descripcion": "Análisis de la configuración de autenticación y seguridad del sistema",
                "funciones": [
                    " Auditoría de configuración PAM",
                    "[SHIELD] Auditoría completa de seguridad",
                    "[ERROR] Cancelar auditoría en progreso",
                    "[STATS] Ver resultados clasificados por prioridad"
                ],
                "tips": [
                    " PAM controla cómo los usuarios se autentican en el sistema",
                    " Los hallazgos críticos requieren atención inmediata",
                    " Puedes cancelar una auditoría si es necesario"
                ]
            },
            "monitor_sistema": {
                "titulo": " Monitor del Sistema",
                "descripcion": "Supervisión en tiempo real de procesos, red y actividad del sistema",
                "funciones": [
                    " Monitorización de procesos activos",
                    " Análisis de tráfico de red",
                    "[STATS] Estadísticas de recursos del sistema",
                    " Alertas de actividad sospechosa"
                ],
                "tips": [
                    " El monitor funciona en tiempo real",
                    " Los procesos con alto uso de CPU pueden indicar problemas",
                    " El tráfico de red inusual puede ser señal de compromiso"
                ]
            },
            "cuarentena": {
                "titulo": " Gestión de Cuarentena",
                "descripcion": "Administra archivos aislados por seguridad",
                "funciones": [
                    " Restaurar archivos seguros",
                    "[SHIELD] Ignorar archivos confiables",
                    " Eliminar archivos peligrosos permanentemente",
                    " Ver detalles de archivos en cuarentena"
                ],
                "tips": [
                    " Sólo restaura archivos si estás seguro de que son seguros",
                    " Usar 'Ignorar' añade el archivo a la lista blanca",
                    " La eliminación permanente NO se puede deshacer"
                ]
            },
            "reportes": {
                "titulo": "[STATS] Sistema de Informes",
                "descripcion": "Genera y visualiza informes de seguridad detallados",
                "funciones": [
                    " Generar informes de auditoría",
                    " Exportar informes en HTML/PDF",
                    " Visualizar historial de informes",
                    "[REFRESH] Programar informes automáticos"
                ],
                "tips": [
                    " Los informes incluyen recomendaciones específicas",
                    " Guarda informes importantes para referencia futura",
                    " Los informes automáticos ayudan al seguimiento continuo"
                ]
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Crear archivo de configuración
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_default, f, indent=2, ensure_ascii=False)
                return config_default
        except Exception:
            return config_default
    
    def crear_boton_ayuda(self, parent, dashboard_id: str) -> tk.Button:
        """Crea un botón de ayuda para un dashboard específico"""
        btn_ayuda = tk.Button(
            parent,
            text=" AYUDA",
            command=lambda: self.mostrar_ayuda(dashboard_id),
            bg=self.colores.cyan_brillante,
            fg=self.colores.negro_carbono,
            font=('Consolas', 11, 'bold'),
            relief='raised',
            bd=2,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        
        # Efecto hover más notable
        def on_enter(e):
            btn_ayuda.config(bg=self.colores.verde_esmeralda, relief='raised', bd=3)
        
        def on_leave(e):
            btn_ayuda.config(bg=self.colores.cyan_brillante, relief='raised', bd=2)
        
        btn_ayuda.bind("<Enter>", on_enter)
        btn_ayuda.bind("<Leave>", on_leave)
        
        return btn_ayuda
    
    def mostrar_ayuda(self, dashboard_id: str):
        """Muestra la ventana de ayuda para un dashboard específico"""
        if dashboard_id not in self.ayuda_config:
            messagebox.showinfo("Ayuda", "Información de ayuda no disponible para esta sección.")
            return
        
        config = self.ayuda_config[dashboard_id]
        
        # Crear ventana de ayuda
        ventana_ayuda = tk.Toplevel()
        ventana_ayuda.title(f"Ayuda - {config['titulo']}")
        ventana_ayuda.geometry("600x500")
        ventana_ayuda.resizable(True, True)
        ventana_ayuda.configure(bg=self.colores.fondo_secundario)
        
        # Centrar ventana
        ventana_ayuda.transient()
        ventana_ayuda.grab_set()
        
        # Frame principal con scroll
        main_frame = tk.Frame(ventana_ayuda, bg=self.colores.fondo_secundario)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        titulo_label = tk.Label(
            main_frame,
            text=config['titulo'],
            font=('Consolas', 16, 'bold'),
            fg=self.colores.texto_primario,
            bg=self.colores.fondo_secundario,
            wraplength=550
        )
        titulo_label.pack(pady=(0, 15))
        
        # Descripción
        desc_label = tk.Label(
            main_frame,
            text=config['descripcion'],
            font=('Consolas', 11),
            fg=self.colores.gris_platino,
            bg=self.colores.fondo_secundario,
            wraplength=550,
            justify='left'
        )
        desc_label.pack(pady=(0, 20))
        
        # Funciones
        if 'funciones' in config:
            func_frame = tk.LabelFrame(
                main_frame,
                text=" Funciones Principales",
                font=('Consolas', 12, 'bold'),
                fg=self.colores.verde_terminal,
                bg=self.colores.fondo_secundario,
                relief='flat',
                borderwidth=2
            )
            func_frame.pack(fill='x', pady=(0, 15))
            
            for funcion in config['funciones']:
                func_label = tk.Label(
                    func_frame,
                    text=funcion,
                    font=('Consolas', 10),
                    fg=self.colores.texto_primario,
                    bg=self.colores.fondo_secundario,
                    anchor='w',
                    wraplength=500
                )
                func_label.pack(anchor='w', padx=10, pady=2)
        
        # Tips
        if 'tips' in config:
            tips_frame = tk.LabelFrame(
                main_frame,
                text=" Consejos Útiles",
                font=('Consolas', 12, 'bold'),
                fg=self.colores.naranja_fuego,
                bg=self.colores.fondo_secundario,
                relief='flat',
                borderwidth=2
            )
            tips_frame.pack(fill='x', pady=(0, 20))
            
            for tip in config['tips']:
                tip_label = tk.Label(
                    tips_frame,
                    text=tip,
                    font=('Consolas', 10),
                    fg=self.colores.gris_platino,
                    bg=self.colores.fondo_secundario,
                    anchor='w',
                    wraplength=500
                )
                tip_label.pack(anchor='w', padx=10, pady=2)
        
        # Botón cerrar
        btn_cerrar = tk.Button(
            main_frame,
            text="[OK] Entendido",
            command=ventana_ayuda.destroy,
            bg=self.colores.verde_terminal,
            fg=self.colores.fondo_secundario,
            font=('Consolas', 11, 'bold'),
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        btn_cerrar.pack(pady=10)
        
        # Centrar la ventana en la pantalla
        ventana_ayuda.update_idletasks()
        x = (ventana_ayuda.winfo_screenwidth() // 2) - (ventana_ayuda.winfo_width() // 2)
        y = (ventana_ayuda.winfo_screenheight() // 2) - (ventana_ayuda.winfo_height() // 2)
        ventana_ayuda.geometry(f"+{x}+{y}")
    
    def agregar_ayuda_contextual(self, parent, dashboard_id: str, posicion='bottom-right'):
        """Agrega un botón de ayuda contextual a un widget padre"""
        try:
            # Intentar obtener el color de fondo del padre
            try:
                bg_color = parent.cget('bg')
            except:
                bg_color = self.colores.fondo_secundario
            
            # Frame para el botón de ayuda
            ayuda_frame = tk.Frame(parent, bg=bg_color)
            
            if posicion == 'top-right':
                ayuda_frame.place(relx=0.95, rely=0.05, anchor='ne')
            elif posicion == 'top-left':
                ayuda_frame.place(relx=0.05, rely=0.05, anchor='nw')
            elif posicion == 'bottom-right':
                ayuda_frame.place(relx=0.95, rely=0.95, anchor='se')
            elif posicion == 'bottom-left':
                ayuda_frame.place(relx=0.05, rely=0.95, anchor='sw')
            elif posicion == 'bottom-center':
                ayuda_frame.place(relx=0.5, rely=0.95, anchor='s')
            elif posicion == 'center-left':
                ayuda_frame.place(relx=0.02, rely=0.5, anchor='w')
            elif posicion == 'center-right':
                ayuda_frame.place(relx=0.98, rely=0.5, anchor='e')
            
            # Crear botón de ayuda
            btn_ayuda = self.crear_boton_ayuda(ayuda_frame, dashboard_id)
            btn_ayuda.pack()
            
            return btn_ayuda
        except Exception as e:
            self.logger.error(f"Error creando botón de ayuda para {dashboard_id}: {e}")
            return None
    
    def agregar_ayuda_con_pack(self, parent, dashboard_id: str, pady=(10, 0)):
        """Agrega un botón de ayuda usando pack en lugar de place para uso secuencial"""
        try:
            # Intentar obtener el color de fondo del padre
            try:
                bg_color = parent.cget('bg')
            except:
                bg_color = self.colores.fondo_secundario
            
            # Frame para el botón de ayuda
            ayuda_frame = tk.Frame(parent, bg=bg_color)
            ayuda_frame.pack(pady=pady)
            
            # Crear botón de ayuda
            btn_ayuda = self.crear_boton_ayuda(ayuda_frame, dashboard_id)
            btn_ayuda.pack()
            
            self.logger.info(f"Botón de ayuda con pack creado exitosamente para {dashboard_id}")
            return btn_ayuda
            
        except Exception as e:
            self.logger.error(f"Error agregando ayuda con pack para {dashboard_id}: {e}")
            return None
