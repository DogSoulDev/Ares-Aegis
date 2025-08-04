#!/usr/bin/env python3
"""
Terminal Integrado para Ares Aegis
Terminal REAL con shell del usuario integrado en la interfaz para Kali Linux
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import os
import logging
import time
import signal
from .emoticonos_mitologicos import EmoticonosMitologicos


class TerminalIntegrado:
    """Terminal real integrado con shell del usuario para Kali Linux"""
    
    def __init__(self, contenedor_padre, colores):
        self.contenedor_padre = contenedor_padre
        self.colores = colores
        self.logger = logging.getLogger(__name__)
        
        # Variables del terminal
        self.proceso_shell = None
        self.terminales_activos = {}
        self.terminal_actual = None
        self.contador_terminales = 0
        
        # Variables de interfaz
        self.notebook = None
        self.frame_principal = None
        
        # Detectar shell del usuario en Kali Linux
        self.shell_usuario = self._detectar_shell_usuario()
        
    def _detectar_shell_usuario(self):
        """Detectar el shell predeterminado del usuario en Kali Linux"""
        try:
            # En Kali Linux, usar directamente la variable SHELL
            shell_env = os.environ.get('SHELL', '/bin/bash')
            if os.path.exists(shell_env):
                return shell_env
            
            # Shells comunes en Kali Linux en orden de preferencia
            shells_kali = ['/bin/zsh', '/bin/bash', '/bin/sh']
            for shell in shells_kali:
                if os.path.exists(shell):
                    return shell
                    
            # Fallback a bash (siempre disponible en Kali)
            return '/bin/bash'
                
        except Exception as e:
            self.logger.warning(f"Error detectando shell: {e}")
            return '/bin/bash'
    
    def crear_terminal_widget(self):
        """Crear el widget principal del terminal"""
        # Frame principal del terminal
        self.frame_principal = tk.Frame(self.contenedor_padre, bg=self.colores.fondo_secundario)
        
        # Header con controles
        self._crear_header_terminal()
        
        # Notebook para múltiples terminales
        self._crear_notebook_terminales()
        
        # Crear primer terminal
        self._crear_nuevo_terminal()
        
        return self.frame_principal
    
    def _crear_header_terminal(self):
        """Crear header con controles del terminal"""
        header = tk.Frame(self.frame_principal, bg=self.colores.fondo_terciario, height=40)
        header.pack(fill='x', pady=(0, 5))
        header.pack_propagate(False)
        
        # Título
        tk.Label(header,
                text=f"💻 {EmoticonosMitologicos.HERMES} Terminal Integrado Kali - {self.shell_usuario}",
                font=('Consolas', 11, 'bold'),
                fg=self.colores.acento_primario,
                bg=self.colores.fondo_terciario).pack(side='left', padx=10, pady=8)
        
        # Botones de control
        controles_frame = tk.Frame(header, bg=self.colores.fondo_terciario)
        controles_frame.pack(side='right', padx=10, pady=5)
        
        # Botón nuevo terminal
        tk.Button(controles_frame,
                 text="➕ Nuevo",
                 command=self._crear_nuevo_terminal,
                 bg=self.colores.exito,
                 fg='white',
                 font=('Consolas', 9, 'bold'),
                 relief='flat',
                 padx=10, pady=2,
                 cursor='hand2').pack(side='left', padx=(0, 5))
        
        # Botón cerrar terminal actual
        tk.Button(controles_frame,
                 text="❌ Cerrar",
                 command=self._cerrar_terminal_actual,
                 bg=self.colores.error,
                 fg='white',
                 font=('Consolas', 9, 'bold'),
                 relief='flat',
                 padx=10, pady=2,
                 cursor='hand2').pack(side='left', padx=(0, 5))
        
        # Botón limpiar
        tk.Button(controles_frame,
                 text="🧹 Limpiar",
                 command=self._limpiar_terminal_actual,
                 bg=self.colores.acento_primario,
                 fg='white',
                 font=('Consolas', 9, 'bold'),
                 relief='flat',
                 padx=10, pady=2,
                 cursor='hand2').pack(side='left')
    
    def _crear_notebook_terminales(self):
        """Crear notebook para múltiples terminales"""
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill='both', expand=True)
        
        # Configurar estilo del notebook para tema oscuro
        self._configurar_estilo_notebook()
    
    def _configurar_estilo_notebook(self):
        """Configurar estilo del notebook para tema oscuro de Kali"""
        try:
            style = ttk.Style()
            style.theme_use('clam')
            
            # Configurar colores del notebook
            style.configure('TNotebook', 
                          background=self.colores.fondo_secundario,
                          borderwidth=0)
            style.configure('TNotebook.Tab', 
                          background=self.colores.fondo_primario,
                          foreground=self.colores.texto_primario,
                          padding=[10, 5],
                          font=('Consolas', 9))
            style.map('TNotebook.Tab',
                     background=[('selected', self.colores.acento_primario),
                               ('active', self.colores.fondo_terciario)])
        except Exception as e:
            self.logger.warning(f"No se pudo configurar estilo del notebook: {e}")
    
    def _crear_nuevo_terminal(self):
        """Crear una nueva instancia de terminal"""
        self.contador_terminales += 1
        terminal_id = f"terminal_{self.contador_terminales}"
        
        # Frame para este terminal
        terminal_frame = tk.Frame(self.notebook, bg=self.colores.fondo_primario)
        
        # Crear el widget de texto del terminal
        terminal_text = tk.Text(terminal_frame,
                              bg='#1a1a1a',  # Negro terminal
                              fg='#00ff00',  # Verde terminal clásico
                              font=('Consolas', 10),
                              wrap='word',
                              insertbackground='#00ff00',  # Cursor verde
                              selectbackground='#333333')
        
        # Scrollbar para el terminal
        scrollbar = tk.Scrollbar(terminal_frame, command=terminal_text.yview)
        terminal_text.configure(yscrollcommand=scrollbar.set)
        
        # Layout del terminal
        terminal_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Crear proceso del shell real
        proceso_shell = self._iniciar_proceso_shell()
        
        # Almacenar información del terminal
        self.terminales_activos[terminal_id] = {
            'frame': terminal_frame,
            'text_widget': terminal_text,
            'proceso': proceso_shell,
            'hilo_lectura': None,
            'buffer_comando': '',
            'activo': True
        }
        
        # Agregar tab al notebook
        tab_name = f"Terminal {self.contador_terminales}"
        if self.notebook:
            self.notebook.add(terminal_frame, text=tab_name)
            self.notebook.select(terminal_frame)
        self.terminal_actual = terminal_id
        
        # Configurar eventos del terminal
        self._configurar_eventos_terminal(terminal_id)
        
        # Iniciar hilo de lectura
        self._iniciar_hilo_lectura(terminal_id)
        
        # Mostrar prompt inicial
        self._mostrar_prompt_inicial(terminal_id)
        
        self.logger.info(f"Terminal {terminal_id} creado con shell: {self.shell_usuario}")
    
    def _iniciar_proceso_shell(self):
        """Iniciar proceso real del shell en Kali Linux"""
        try:
            # Configurar variables de entorno específicas para Kali Linux
            env = os.environ.copy()
            env['TERM'] = 'xterm-256color'
            env['COLORTERM'] = 'truecolor'
            env['PS1'] = '┌──(\\u㉿\\h)-[\\w]\\n└─\\$ '  # Prompt auténtico de Kali Linux 2024+
            env['DEBIAN_FRONTEND'] = 'noninteractive'  # Para comandos no interactivos
            
            # Crear proceso nativo para Kali Linux
            proceso = subprocess.Popen(
                [self.shell_usuario],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=0,
                env=env,
                preexec_fn=getattr(os, 'setsid')  # Usar getattr para funciones Linux
            )
            
            return proceso
            
        except Exception as e:
            self.logger.error(f"Error iniciando shell {self.shell_usuario}: {e}")
            return None
    
    def _configurar_eventos_terminal(self, terminal_id):
        """Configurar eventos de teclado y mouse para el terminal"""
        terminal_info = self.terminales_activos[terminal_id]
        text_widget = terminal_info['text_widget']
        
        # Bind para Enter (ejecutar comando)
        text_widget.bind('<Return>', lambda e: self._ejecutar_comando(terminal_id))
        
        # Bind para teclas especiales
        text_widget.bind('<Control-c>', lambda e: self._enviar_ctrl_c(terminal_id))
        text_widget.bind('<Control-d>', lambda e: self._enviar_ctrl_d(terminal_id))
        text_widget.bind('<Up>', lambda e: self._historial_anterior(terminal_id))
        text_widget.bind('<Down>', lambda e: self._historial_siguiente(terminal_id))
        
        # Bind para clic (posicionar cursor)
        text_widget.bind('<Button-1>', lambda e: self._posicionar_cursor(terminal_id, e))
        
        # Enfocar el terminal
        text_widget.focus_set()
    
    def _mostrar_prompt_inicial(self, terminal_id):
        """Mostrar prompt inicial del terminal"""
        terminal_info = self.terminales_activos[terminal_id]
        text_widget = terminal_info['text_widget']
        
        # Obtener información del sistema Kali Linux
        try:
            usuario = os.getenv('USER', 'kali')
            hostname = getattr(os, 'uname')().nodename  # Usar getattr para funciones Linux
        except:
            usuario = 'kali'
            hostname = 'kali-sistema'
        
        # Mensaje de bienvenida estilo Kali Linux
        bienvenida = f"""🛡️  {EmoticonosMitologicos.ARES} ARES AEGIS - TERMINAL KALI LINUX 
┌─[{usuario}@{hostname}]─[{os.getcwd()}]
└─$ Kali Linux Terminal Ready
Shell: {self.shell_usuario} | Terminal ID: {terminal_id[-1]}

"""
        
        text_widget.insert(tk.END, bienvenida)
        text_widget.see(tk.END)
    
    def _iniciar_hilo_lectura(self, terminal_id):
        """Iniciar hilo para leer output del shell"""
        def leer_output():
            terminal_info = self.terminales_activos.get(terminal_id)
            if not terminal_info or not terminal_info['activo']:
                return
                
            proceso = terminal_info['proceso']
            if not proceso:  # Si no hay proceso, salir
                return
                
            text_widget = terminal_info['text_widget']
            
            try:
                while terminal_info['activo'] and proceso.poll() is None:
                    try:
                        # Leer output del proceso
                        output = proceso.stdout.read(1)
                        if output:
                            # Actualizar interfaz en el hilo principal
                            self.contenedor_padre.after(0, 
                                lambda o=output: self._actualizar_output(terminal_id, o))
                        time.sleep(0.01)  # Pequeña pausa para no saturar CPU
                        
                    except Exception as e:
                        if terminal_info['activo']:
                            self.logger.warning(f"Error leyendo output del terminal {terminal_id}: {e}")
                        break
                        
            except Exception as e:
                self.logger.error(f"Error en hilo de lectura del terminal {terminal_id}: {e}")
        
        # Iniciar hilo
        if terminal_id in self.terminales_activos:
            hilo = threading.Thread(target=leer_output, daemon=True)
            hilo.start()
            self.terminales_activos[terminal_id]['hilo_lectura'] = hilo
    
    def _actualizar_output(self, terminal_id, output):
        """Actualizar output en la interfaz"""
        if terminal_id not in self.terminales_activos:
            return
            
        terminal_info = self.terminales_activos[terminal_id]
        text_widget = terminal_info['text_widget']
        
        try:
            text_widget.insert(tk.END, output)
            text_widget.see(tk.END)
        except tk.TclError:
            # Widget destruido
            pass
    
    def _ejecutar_comando(self, terminal_id):
        """Ejecutar comando en el terminal de Kali Linux"""
        if terminal_id not in self.terminales_activos:
            return 'break'
            
        terminal_info = self.terminales_activos[terminal_id]
        text_widget = terminal_info['text_widget']
        proceso = terminal_info['proceso']
        
        try:
            # Obtener línea actual (comando)
            linea_actual = text_widget.get('insert linestart', 'insert lineend')
            
            # Extraer comando (después del prompt)
            if '$ ' in linea_actual:
                comando = linea_actual.split('$ ', 1)[-1]
            else:
                comando = linea_actual.strip()
            
            # Enviar comando al shell
            if proceso and proceso.poll() is None:
                proceso.stdin.write(comando + '\n')
                proceso.stdin.flush()
            
            # Agregar nueva línea
            text_widget.insert(tk.END, '\n')
            text_widget.see(tk.END)
            
        except Exception as e:
            self.logger.error(f"Error ejecutando comando en terminal {terminal_id}: {e}")
        
        return 'break'  # Prevenir comportamiento por defecto
    
    def _enviar_ctrl_c(self, terminal_id):
        """Enviar Ctrl+C al proceso en Kali Linux"""
        if terminal_id not in self.terminales_activos:
            return 'break'
            
        terminal_info = self.terminales_activos[terminal_id]
        proceso = terminal_info['proceso']
        
        try:
            if proceso and proceso.poll() is None:
                # Enviar SIGINT al grupo de procesos en Kali Linux
                killpg = getattr(os, 'killpg')
                getpgid = getattr(os, 'getpgid')
                killpg(getpgid(proceso.pid), signal.SIGINT)
                
                # Mostrar ^C en el terminal
                text_widget = terminal_info['text_widget']
                text_widget.insert(tk.END, '^C\n')
                text_widget.see(tk.END)
                
        except Exception as e:
            self.logger.warning(f"Error enviando Ctrl+C al terminal {terminal_id}: {e}")
        
        return 'break'
    
    def _enviar_ctrl_d(self, terminal_id):
        """Enviar Ctrl+D al proceso (EOF) en Kali Linux"""
        if terminal_id not in self.terminales_activos:
            return 'break'
            
        terminal_info = self.terminales_activos[terminal_id]
        proceso = terminal_info['proceso']
        
        try:
            if proceso and proceso.poll() is None:
                proceso.stdin.write('\x04')  # ASCII para Ctrl+D
                proceso.stdin.flush()
                
        except Exception as e:
            self.logger.warning(f"Error enviando Ctrl+D al terminal {terminal_id}: {e}")
        
        return 'break'
    
    def _historial_anterior(self, terminal_id):
        """Navegar historial hacia atrás (flecha arriba) - Para implementar"""
        # TODO: Implementar historial de comandos
        return 'break'
    
    def _historial_siguiente(self, terminal_id):
        """Navegar historial hacia adelante (flecha abajo) - Para implementar"""
        # TODO: Implementar historial de comandos
        return 'break'
    
    def _posicionar_cursor(self, terminal_id, event):
        """Posicionar cursor al hacer clic - Para implementar"""
        # TODO: Implementar posicionamiento inteligente del cursor
        pass
    
    def _cerrar_terminal_actual(self):
        """Cerrar el terminal actualmente seleccionado"""
        if not self.terminal_actual or self.terminal_actual not in self.terminales_activos:
            return
            
        terminal_id = self.terminal_actual
        terminal_info = self.terminales_activos[terminal_id]
        
        try:
            # Marcar como inactivo
            terminal_info['activo'] = False
            
            # Terminar proceso del shell en Kali Linux
            proceso = terminal_info['proceso']
            if proceso and proceso.poll() is None:
                try:
                    # Terminar grupo de procesos en Kali Linux usando funciones nativas
                    killpg = getattr(os, 'killpg')
                    getpgid = getattr(os, 'getpgid')
                    sigterm = getattr(signal, 'SIGTERM')
                    sigkill = getattr(signal, 'SIGKILL')
                    
                    killpg(getpgid(proceso.pid), sigterm)
                    time.sleep(0.1)
                    if proceso.poll() is None:
                        killpg(getpgid(proceso.pid), sigkill)
                except Exception:
                    proceso.terminate()
            
            # Remover tab del notebook
            frame = terminal_info['frame']
            if self.notebook:
                self.notebook.forget(frame)
            
            # Limpiar referencia
            del self.terminales_activos[terminal_id]
            
            # Seleccionar otro terminal si existe
            if self.terminales_activos:
                self.terminal_actual = list(self.terminales_activos.keys())[0]
            else:
                self.terminal_actual = None
                
            self.logger.info(f"Terminal {terminal_id} cerrado")
            
        except Exception as e:
            self.logger.error(f"Error cerrando terminal {terminal_id}: {e}")
    
    def _limpiar_terminal_actual(self):
        """Limpiar contenido del terminal actual"""
        if not self.terminal_actual or self.terminal_actual not in self.terminales_activos:
            return
            
        terminal_info = self.terminales_activos[self.terminal_actual]
        text_widget = terminal_info['text_widget']
        
        try:
            text_widget.delete(1.0, tk.END)
            self._mostrar_prompt_inicial(self.terminal_actual)
        except Exception as e:
            self.logger.error(f"Error limpiando terminal {self.terminal_actual}: {e}")
    
    def cerrar_todos_terminales(self):
        """Cerrar todos los terminales activos"""
        for terminal_id in list(self.terminales_activos.keys()):
            self.terminal_actual = terminal_id
            self._cerrar_terminal_actual()
        
        self.logger.info("Todos los terminales de Kali Linux cerrados")
    
    def obtener_info_terminales(self):
        """Obtener información de los terminales activos de Kali Linux"""
        return {
            'total': len(self.terminales_activos),
            'activo': self.terminal_actual,
            'shell': self.shell_usuario,
            'terminales': list(self.terminales_activos.keys())
        }
