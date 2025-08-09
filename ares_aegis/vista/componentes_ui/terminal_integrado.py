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
import platform
from .emoticonos_mitologicos import EmoticonosMitologicos


class TerminalIntegrado:
    # ... (código existente)
    def _detectar_shell_usuario(self):
        """Detectar el shell predeterminado del usuario de forma multiplataforma."""
        sistema = platform.system()
        if sistema == "Windows":
            return os.environ.get('COMSPEC', 'cmd.exe')
        elif sistema == "Linux":
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
                self.logger.warning(f"Error detectando shell en Linux: {e}")
                return '/bin/bash'
        else:
            # Fallback para otros sistemas (macOS, etc.)
            return '/bin/sh'
    
    # ... (código existente)

    def _iniciar_proceso_shell(self):
        """Iniciar proceso real del shell de forma multiplataforma."""
        try:
            env = os.environ.copy()
            creationflags = 0
            preexec_fn = None
            
            sistema = platform.system()
            if sistema == "Windows":
                # No se necesita preexec_fn en Windows
                # CREATE_NEW_PROCESS_GROUP es para permitir enviar Ctrl+C
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            elif sistema == "Linux":
                env['TERM'] = 'xterm-256color'
                env['COLORTERM'] = 'truecolor'
                env['PS1'] = '(\\u\\h)-[\\w]\\n\\$ '
                env['DEBIAN_FRONTEND'] = 'noninteractive'
                # preexec_fn para crear un nuevo grupo de procesos en Linux
                preexec_fn = os.setsid
            
            proceso = subprocess.Popen(
                [self.shell_usuario],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=0,
                env=env,
                preexec_fn=preexec_fn,
                creationflags=creationflags
            )
            
            return proceso
            
        except Exception as e:
            self.logger.error(f"Error iniciando shell {self.shell_usuario}: {e}")
            return None

    # ... (código existente)

    def _enviar_ctrl_c(self, terminal_id):
        """Enviar Ctrl+C al proceso de forma multiplataforma."""
        if terminal_id not in self.terminales_activos:
            return 'break'
            
        terminal_info = self.terminales_activos[terminal_id]
        proceso = terminal_info['proceso']
        
        try:
            if proceso and proceso.poll() is None:
                sistema = platform.system()
                if sistema == "Windows":
                    # Enviar Ctrl+C en Windows
                    proceso.send_signal(signal.CTRL_C_EVENT)
                elif sistema == "Linux":
                    # Enviar SIGINT al grupo de procesos en Linux
                    os.killpg(os.getpgid(proceso.pid), signal.SIGINT)
                
                # Mostrar ^C en el terminal
                text_widget = terminal_info['text_widget']
                text_widget.insert(tk.END, '^C\n')
                text_widget.see(tk.END)
                
        except Exception as e:
            self.logger.warning(f"Error enviando Ctrl+C al terminal {terminal_id}: {e}")
        
        return 'break'

    # ... (código existente)

    def _cerrar_terminal_actual(self):
        """Cerrar el terminal actualmente seleccionado de forma multiplataforma."""
        if not self.terminal_actual or self.terminal_actual not in self.terminales_activos:
            return
            
        terminal_id = self.terminal_actual
        terminal_info = self.terminales_activos[terminal_id]
        
        try:
            terminal_info['activo'] = False
            
            proceso = terminal_info['proceso']
            if proceso and proceso.poll() is None:
                try:
                    sistema = platform.system()
                    if sistema == "Linux":
                        # Terminar grupo de procesos en Linux
                        os.killpg(os.getpgid(proceso.pid), signal.SIGTERM)
                        time.sleep(0.1)
                        if proceso.poll() is None:
                            os.killpg(os.getpgid(proceso.pid), signal.SIGKILL)
                    else: # Windows y otros
                        proceso.terminate()
                        time.sleep(0.1)
                        if proceso.poll() is None:
                            proceso.kill()
                except Exception as e:
                    self.logger.error(f"Error terminando proceso del shell: {e}")
                    proceso.kill() # Fallback
            
            # ... (resto del código de cierre)
        except Exception as e:
            self.logger.error(f"Error cerrando terminal {terminal_id}: {e}")