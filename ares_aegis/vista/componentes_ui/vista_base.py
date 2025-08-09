#!/usr/bin/env python3
"""
Clase Base Vista - Patrón base para todas las vistas de Ares Aegis
Implementa patrón Template Method para eliminar duplicación de código
"""

import tkinter as tk
from tkinter import messagebox
import logging
from abc import ABC, abstractmethod


class VistaBase(ABC):
    """
    Clase base para todas las vistas de Ares Aegis
    Implementa patrón Template Method y elimina duplicación de código
    """
    
    def __init__(self, contenedor_padre, controlador, colores):
        """Inicialización común para todas las vistas"""
        self.contenedor_padre = contenedor_padre
        self.controlador = controlador
        self.colores = colores
        self.logger = logging.getLogger(self.__class__.__name__)
        self.frame_principal = None
        
        # Configuración común de UI
        self._configurar_ui_comun()
        
    def _configurar_ui_comun(self):
        """Configuración común de UI para todas las vistas"""
        # Variables de estado comunes
        self.estado_var = tk.StringVar(value=self._get_estado_inicial())
        
    @abstractmethod
    def _get_estado_inicial(self):
        """Estado inicial específico de cada vista - debe implementarse"""
        pass
        
    @abstractmethod
    def _get_titulo_ventana(self):
        """Título específico de cada vista - debe implementarse"""
        pass
        
    @abstractmethod
    def _get_descripcion_funcionalidades(self):
        """Descripción de funcionalidades específicas - debe implementarse"""
        pass
        
    @abstractmethod
    def crear_vista(self):
        """Crear la vista específica - debe implementarse por cada subclase"""
        pass
        
    def mostrar_informacion(self):
        """
        Método template para mostrar información de ayuda
        Implementa patrón Template Method - estructura común, detalles específicos
        """
        titulo = self._get_titulo_ventana()
        funcionalidades = self._get_descripcion_funcionalidades()
        
        info_text = f"""[SHIELD] {titulo}

{funcionalidades}

 CONTROLES COMUNES:
• Botón de ayuda (?) para información detallada
• Área de logs para seguimiento de actividad
• Controles de estado en tiempo real

[TOOL] FUNCIONES AVANZADAS:
• Integración completa con sistema SIEM
• Logs centralizados y estructurados
• Interfaz optimizada para Kali Linux
        """
        
        messagebox.showinfo(titulo, info_text)
        self.logger.info(f"Mostrada información de ayuda para {titulo}")
        
    def limpiar_vista(self):
        """Limpiar elementos de la vista - método template común"""
        if self.frame_principal:
            for widget in self.frame_principal.winfo_children():
                widget.destroy()
        self.logger.info(f"Vista {self.__class__.__name__} limpiada")
        
    def actualizar_estado(self, nuevo_estado):
        """Actualizar estado de la vista - método común"""
        self.estado_var.set(nuevo_estado)
        self.logger.info(f"Estado actualizado: {nuevo_estado}")
        
    def _crear_frame_principal(self):
        """Crear frame principal común para todas las vistas"""
        if self.frame_principal:
            self.frame_principal.destroy()
            
        self.frame_principal = tk.Frame(
            self.contenedor_padre,
            bg=self.colores.FONDO,
            relief='flat',
            bd=0
        )
        self.frame_principal.pack(fill='both', expand=True, padx=5, pady=5)
        
        return self.frame_principal
        
    def _crear_titulo_seccion(self, texto, icono="[SHIELD]"):
        """Crear título de sección estandarizado"""
        frame_titulo = tk.Frame(self.frame_principal, bg=self.colores.FONDO)
        frame_titulo.pack(fill='x', pady=(0, 10))
        
        label_titulo = tk.Label(
            frame_titulo,
            text=f"{icono} {texto}",
            font=('Hack', 14, 'bold'),
            fg=self.colores.VERDE_CLARO,
            bg=self.colores.FONDO
        )
        label_titulo.pack(side='left')
        
        return frame_titulo
        
    def _crear_boton_estandar(self, padre, texto, comando, icono="", estado='normal'):
        """Crear botón con estilo estandarizado"""
        # Validar estado del botón
        estados_validos = ['normal', 'active', 'disabled']
        estado_final = estado if estado in estados_validos else 'normal'
            
        boton = tk.Button(
            padre,
            text=f"{icono} {texto}",
            command=comando,
            font=('Hack', 10, 'bold'),
            fg=self.colores.TEXTO_CLARO,
            bg=self.colores.VERDE_OSCURO,
            activeforeground=self.colores.TEXTO_CLARO,
            activebackground=self.colores.VERDE_CLARO,
            relief='flat',
            bd=1,
            padx=20,
            pady=8
        )
        
        # Configurar estado después de la creación
        if estado_final == 'disabled':
            boton.config(state='disabled')
        elif estado_final == 'active':
            boton.config(state='active')
        else:
            boton.config(state='normal')
            
        return boton
        
    def _crear_area_texto_logs(self, padre, altura=10):
        """Crear área de texto para logs estandarizada"""
        frame_logs = tk.Frame(padre, bg=self.colores.FONDO)
        
        # Título del área de logs
        label_logs = tk.Label(
            frame_logs,
            text=" Registro de Actividad",
            font=('Hack', 10, 'bold'),
            fg=self.colores.VERDE_CLARO,
            bg=self.colores.FONDO
        )
        label_logs.pack(anchor='w')
        
        # Área de texto con scrollbar
        frame_texto = tk.Frame(frame_logs, bg=self.colores.FONDO)
        frame_texto.pack(fill='both', expand=True, pady=(5, 0))
        
        texto_logs = tk.Text(
            frame_texto,
            height=altura,
            font=('Hack', 9),
            fg=self.colores.TEXTO_CLARO,
            bg=self.colores.GRIS_OSCURO,
            insertbackground=self.colores.VERDE_CLARO,
            selectbackground=self.colores.VERDE_OSCURO,
            wrap=tk.WORD,
            state='disabled'
        )
        
        scrollbar = tk.Scrollbar(frame_texto, command=texto_logs.yview)
        texto_logs.configure(yscrollcommand=scrollbar.set)
        
        texto_logs.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        return frame_logs, texto_logs
        
    def _escribir_log(self, texto_widget, mensaje):
        """Escribir mensaje en área de logs"""
        if texto_widget:
            texto_widget.config(state='normal')
            texto_widget.insert(tk.END, f"{mensaje}\n")
            texto_widget.see(tk.END)
            texto_widget.config(state='disabled')
            
    def _mostrar_error(self, titulo, mensaje):
        """Mostrar error estandarizado"""
        messagebox.showerror(titulo, mensaje)
        self.logger.error(f"Error mostrado: {titulo} - {mensaje}")
        
    def _mostrar_exito(self, titulo, mensaje):
        """Mostrar mensaje de éxito estandarizado"""
        messagebox.showinfo(titulo, mensaje)
        self.logger.info(f"Éxito mostrado: {titulo} - {mensaje}")
        
    def _validar_inicializacion(self):
        """Validar que la vista esté correctamente inicializada"""
        if not self.controlador:
            raise ValueError(f"Controlador no inicializado en {self.__class__.__name__}")
        if not self.colores:
            raise ValueError(f"Colores no inicializados en {self.__class__.__name__}")
        if not self.contenedor_padre:
            raise ValueError(f"Contenedor padre no inicializado en {self.__class__.__name__}")
            
        self.logger.info(f"Vista {self.__class__.__name__} correctamente inicializada")
        return True
