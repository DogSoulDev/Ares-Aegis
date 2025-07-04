#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Respuesta Automatizada
"""

import os
import json
import subprocess
import threading
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from ..utilidades.ayuda_logging import configurar_logger_modulo
from ..utilidades.ayuda_rutas import crear_ruta_segura


class ReglasDefensaAutomatizada:
    """Catálogo de reglas de defensa predefinidas del Égida."""
    
    @staticmethod
    def obtener_reglas_predefinidas() -> Dict[str, Dict[str, Any]]:
        """
        Retorna el catálogo completo de reglas de defensa automatizada.
        
        Returns:
            Dict con todas las reglas organizadas por categorías
        """
        return {
            "defensa_ssh": {
                "titulo": "🔐 Guardianes de las Puertas SSH",
                "descripcion": "Protección contra asaltos de fuerza bruta en las puertas SSH",
                "reglas": {
                    "bloqueo_fuerza_bruta_ssh": {
                        "nombre": "Bloqueo de Asaltos SSH",
                        "descripcion": "Banea IPs que realizan múltiples intentos fallidos de conexión SSH",
                        "evento_disparador": "failed_ssh_login",
                        "condicion": {
                            "tipo": "contador",
                            "umbral": 5,
                            "ventana_tiempo": 300  # 5 minutos
                        },
                        "accion": "bloquear_ip_iptables",
                        "parametros_configurables": {
                            "umbral_asaltos": {
                                "nombre": "Umbral de Asaltos",
                                "descripcion": "Número de intentos fallidos antes del destierro",
                                "tipo": "entero",
                                "valor_defecto": 5,
                                "min": 3,
                                "max": 20
                            },
                            "duracion_destierro": {
                                "nombre": "Duración del Destierro (minutos)",
                                "descripcion": "Tiempo que la IP permanece desterrada",
                                "tipo": "entero",
                                "valor_defecto": 60,
                                "min": 10,
                                "max": 1440
                            }
                        },
                        "nivel_riesgo": "MEDIO",
                        "mensaje_activacion": "El rayo de Zeus ha caído sobre la IP invasora - desterrada del reino SSH"
                    }
                }
            },
            
            "proteccion_procesos": {
                "titulo": "⚔️ Centinelas de los Procesos",
                "descripcion": "Vigilancia y eliminación de procesos sospechosos",
                "reglas": {
                    "terminar_procesos_temporales": {
                        "nombre": "Eliminación de Sombras en /tmp",
                        "descripcion": "Termina procesos ejecutándose desde directorios temporales",
                        "evento_disparador": "proceso_en_temporal",
                        "condicion": {
                            "tipo": "patron",
                            "patron_ruta": ["/tmp/", "/var/tmp/", "/dev/shm/"]
                        },
                        "accion": "terminar_proceso_y_cuarentena",
                        "parametros_configurables": {
                            "confirmacion_requerida": {
                                "nombre": "Requiere Confirmación",
                                "descripcion": "Pedir confirmación antes de eliminar el proceso",
                                "tipo": "booleano",
                                "valor_defecto": True
                            }
                        },
                        "nivel_riesgo": "ALTO",
                        "mensaje_activacion": "Una sombra impía ha sido detectada en tierras temporales - el destino la aguarda"
                    },
                    
                    "bloquear_procesos_sospechosos": {
                        "nombre": "Destierro de Procesos Malignos",
                        "descripcion": "Termina procesos con nombres sospechosos conocidos",
                        "evento_disparador": "proceso_sospechoso",
                        "condicion": {
                            "tipo": "lista_negra",
                            "nombres_proceso": ["nc", "netcat", "ncat", "socat", "wget", "curl", "python", "perl", "bash", "sh"]
                        },
                        "accion": "terminar_proceso",
                        "parametros_configurables": {
                            "lista_procesos_permitidos": {
                                "nombre": "Procesos Bendecidos (Excepciones)",
                                "descripcion": "Lista de procesos que no serán tocados por la ira divina",
                                "tipo": "lista",
                                "valor_defecto": []
                            }
                        },
                        "nivel_riesgo": "ALTO",
                        "mensaje_activacion": "El proceso maligno ha sido juzgado y su destino sellado por Ares"
                    }
                }
            },
            
            "guardianes_archivos": {
                "titulo": "📜 Guardianes de los Pergaminos",
                "descripcion": "Protección de archivos críticos del sistema",
                "reglas": {
                    "restaurar_archivos_criticos": {
                        "nombre": "Restauración de Pergaminos Sagrados",
                        "descripcion": "Restaura archivos críticos desde copias de seguridad cuando son modificados",
                        "evento_disparador": "archivo_critico_modificado",
                        "condicion": {
                            "tipo": "lista_archivos",
                            "archivos_protegidos": [
                                "/etc/passwd",
                                "/etc/shadow",
                                "/etc/hosts",
                                "/etc/sudoers"
                            ]
                        },
                        "accion": "restaurar_desde_backup",
                        "parametros_configurables": {
                            "crear_backup_automatico": {
                                "nombre": "Crear Copias Automáticas",
                                "descripcion": "Crear copias de seguridad antes de restaurar",
                                "tipo": "booleano",
                                "valor_defecto": True
                            }
                        },
                        "nivel_riesgo": "CRITICO",
                        "mensaje_activacion": "Un pergamino sagrado ha sido profanado - los dioses restauran su pureza original"
                    }
                }
            },
            
            "centinelas_red": {
                "titulo": "🌐 Centinelas de las Conexiones",
                "descripcion": "Monitoreo y bloqueo de conexiones maliciosas",
                "reglas": {
                    "bloquear_ips_maliciosas": {
                        "nombre": "Destierro de IPs Corruptas",
                        "descripcion": "Bloquea conexiones desde IPs conocidas como maliciosas",
                        "evento_disparador": "conexion_ip_maliciosa",
                        "condicion": {
                            "tipo": "lista_negra_ip",
                            "archivo_ips": "recursos/ips_maliciosas_local.txt"
                        },
                        "accion": "bloquear_ip_iptables",
                        "parametros_configurables": {
                            "actualizar_lista_automaticamente": {
                                "nombre": "Actualización Automática",
                                "descripcion": "Actualizar lista de IPs maliciosas automáticamente",
                                "tipo": "booleano",
                                "valor_defecto": False
                            }
                        },
                        "nivel_riesgo": "ALTO",
                        "mensaje_activacion": "Una IP corrupta ha intentado profanar el reino - desterrada por la Égida"
                    },
                    
                    "detectar_conexiones_c2": {
                        "nombre": "Cazador de Conexiones C2",
                        "descripción": "Detecta y bloquea conexiones a servidores de comando y control",
                        "evento_disparador": "conexion_c2_detectada",
                        "condicion": {
                            "tipo": "patron_red",
                            "puertos_sospechosos": [1337, 31337, 4444, 5555, 6666, 8080],
                            "dominios_sospechosos": [".tk", ".ml", ".ga", ".cf"]
                        },
                        "accion": "bloquear_y_alertar",
                        "parametros_configurables": {
                            "alertar_administrador": {
                                "nombre": "Alertar al Oráculo Mayor",
                                "descripción": "Enviar alerta inmediata cuando se detecte conexión C2",
                                "tipo": "booleano",
                                "valor_defecto": True
                            }
                        },
                        "nivel_riesgo": "CRITICO",
                        "mensaje_activacion": "¡Una conexión al reino de las sombras C2 ha sido interceptada! Los dioses han cortado el hilo maligno"
                    }
                }
            }
        }


class EjecutorAcciones:
    """Ejecutor de acciones defensivas del Égida."""
    
    def __init__(self):
        """Inicializa el ejecutor de acciones divinas."""
        self.logger = configurar_logger_modulo("ejecutor_acciones")
        self.directorio_backups = "/var/ares_aegis_backups/"
        
        # Crear directorio de backups si no existe
        try:
            crear_ruta_segura(self.directorio_backups)
        except Exception as e:
            self.logger.warning(f"No se pudo crear directorio de backups: {e}")
            self.directorio_backups = str(Path.home() / ".ares_aegis_backups")
            crear_ruta_segura(self.directorio_backups)
        
        self.logger.info("El ejecutor de acciones divinas ha despertado en el yunque celestial")
    
    def bloquear_ip_iptables(self, ip: str, duracion_minutos: int = 60) -> Dict[str, Any]:
        """
        Bloquea una IP usando iptables - El martillo de Zeus contra los invasores.
        
        Args:
            ip: Dirección IP a bloquear
            duracion_minutos: Duración del bloqueo en minutos
            
        Returns:
            Dict con resultado de la acción
        """
        try:
            # Comando para agregar regla de bloqueo
            comando_bloqueo = [
                'iptables', '-A', 'INPUT', 
                '-s', ip, 
                '-j', 'DROP'
            ]
            
            resultado = subprocess.run(
                comando_bloqueo,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if resultado.returncode == 0:
                # Programar desbloqueo automático
                if duracion_minutos > 0:
                    threading.Timer(
                        duracion_minutos * 60,
                        self._desbloquear_ip_automatico,
                        args=[ip]
                    ).start()
                
                mensaje = f"El rayo de Zeus ha caído sobre la IP {ip} - desterrada por {duracion_minutos} minutos"
                self.logger.info(mensaje)
                
                return {
                    'exitoso': True,
                    'accion': 'bloquear_ip',
                    'ip': ip,
                    'duracion_minutos': duracion_minutos,
                    'mensaje': mensaje
                }
            else:
                error_msg = f"Los dioses no pudieron forjar el bloqueo para {ip}: {resultado.stderr}"
                self.logger.error(error_msg)
                return {
                    'exitoso': False,
                    'accion': 'bloquear_ip',
                    'ip': ip,
                    'mensaje': error_msg
                }
        
        except Exception as e:
            error_msg = f"Una tormenta impidió el bloqueo de {ip}: {e}"
            self.logger.error(error_msg)
            return {
                'exitoso': False,
                'accion': 'bloquear_ip',
                'ip': ip,
                'mensaje': error_msg
            }
    
    def _desbloquear_ip_automatico(self, ip: str):
        """Desbloquea automáticamente una IP después del tiempo especificado."""
        try:
            comando_desbloqueo = [
                'iptables', '-D', 'INPUT',
                '-s', ip,
                '-j', 'DROP'
            ]
            
            resultado = subprocess.run(comando_desbloqueo, capture_output=True, text=True)
            
            if resultado.returncode == 0:
                mensaje = f"La IP {ip} ha cumplido su destierro - se le permite retornar al reino"
                self.logger.info(mensaje)
            else:
                self.logger.warning(f"No se pudo desbloquear automáticamente la IP {ip}")
        
        except Exception as e:
            self.logger.error(f"Error en desbloqueo automático de {ip}: {e}")
    
    def terminar_proceso(self, pid: int, nombre_proceso: str = "") -> Dict[str, Any]:
        """
        Termina un proceso - El juicio final de Ares sobre procesos malignos.
        
        Args:
            pid: ID del proceso a terminar
            nombre_proceso: Nombre del proceso para logging
            
        Returns:
            Dict con resultado de la acción
        """
        try:
            # Primero intentar terminación suave
            os.kill(pid, 15)  # SIGTERM
            time.sleep(2)
            
            # Verificar si el proceso aún existe
            try:
                os.kill(pid, 0)  # Verificar existencia
                # Si llega aquí, el proceso aún existe, usar fuerza
                os.kill(pid, 9)  # SIGKILL
                mensaje = f"El proceso {nombre_proceso} (PID: {pid}) ha sido juzgado y eliminado por la fuerza divina"
            except OSError:
                # El proceso ya no existe
                mensaje = f"El proceso {nombre_proceso} (PID: {pid}) ha aceptado su destino y se ha retirado"
            
            self.logger.info(mensaje)
            return {
                'exitoso': True,
                'accion': 'terminar_proceso',
                'pid': pid,
                'nombre_proceso': nombre_proceso,
                'mensaje': mensaje
            }
        
        except ProcessLookupError:
            mensaje = f"El proceso {nombre_proceso} (PID: {pid}) ya había partido hacia el reino de las sombras"
            self.logger.info(mensaje)
            return {
                'exitoso': True,
                'accion': 'terminar_proceso',
                'pid': pid,
                'mensaje': mensaje
            }
        
        except PermissionError:
            mensaje = f"Los dioses no otorgan poder suficiente para juzgar al proceso {nombre_proceso} (PID: {pid})"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'accion': 'terminar_proceso',
                'pid': pid,
                'mensaje': mensaje
            }
        
        except Exception as e:
            mensaje = f"Una tormenta inesperada impidió el juicio del proceso {nombre_proceso} (PID: {pid}): {e}"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'accion': 'terminar_proceso',
                'pid': pid,
                'mensaje': mensaje
            }
    
    def terminar_proceso_y_cuarentena(self, pid: int, ruta_ejecutable: str, nombre_proceso: str = "") -> Dict[str, Any]:
        """
        Termina un proceso y mueve su ejecutable a cuarentena.
        
        Args:
            pid: ID del proceso
            ruta_ejecutable: Ruta del archivo ejecutable
            nombre_proceso: Nombre del proceso
            
        Returns:
            Dict con resultado de la acción
        """
        resultado_terminar = self.terminar_proceso(pid, nombre_proceso)
        
        if resultado_terminar['exitoso'] and os.path.exists(ruta_ejecutable):
            # Mover a cuarentena
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"proceso_maligno_{nombre_proceso}_{timestamp}"
                destino_cuarentena = os.path.join("/var/ares_aegis_cuarentena/", nombre_archivo)
                
                crear_ruta_segura(destino_cuarentena)
                shutil.move(ruta_ejecutable, destino_cuarentena)
                
                mensaje = (f"El proceso {nombre_proceso} ha sido juzgado y su esencia corrupta "
                          f"exiliada a la cripta de Érebo: {destino_cuarentena}")
                
                self.logger.info(mensaje)
                resultado_terminar['cuarentena'] = {
                    'exitoso': True,
                    'destino': destino_cuarentena,
                    'mensaje': mensaje
                }
            
            except Exception as e:
                mensaje_error = f"El proceso fue juzgado pero su esencia corrupta no pudo ser exiliada: {e}"
                self.logger.error(mensaje_error)
                resultado_terminar['cuarentena'] = {
                    'exitoso': False,
                    'mensaje': mensaje_error
                }
        
        return resultado_terminar
    
    def restaurar_desde_backup(self, ruta_archivo: str) -> Dict[str, Any]:
        """
        Restaura un archivo desde la copia de seguridad más reciente.
        
        Args:
            ruta_archivo: Ruta del archivo a restaurar
            
        Returns:
            Dict con resultado de la acción
        """
        try:
            # Crear backup del archivo actual antes de restaurar
            if os.path.exists(ruta_archivo):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_actual = os.path.join(
                    self.directorio_backups,
                    f"backup_{os.path.basename(ruta_archivo)}_{timestamp}"
                )
                shutil.copy2(ruta_archivo, backup_actual)
                mensaje_backup = f"Una copia del pergamino corrupto ha sido guardada en {backup_actual}"
                self.logger.info(mensaje_backup)
            
            # Buscar backup más reciente
            patron_backup = f"backup_{os.path.basename(ruta_archivo)}_*"
            backups_encontrados = list(Path(self.directorio_backups).glob(patron_backup))
            
            if not backups_encontrados:
                mensaje = f"No se encontraron pergaminos ancestrales para restaurar {ruta_archivo}"
                self.logger.error(mensaje)
                return {
                    'exitoso': False,
                    'accion': 'restaurar_backup',
                    'archivo': ruta_archivo,
                    'mensaje': mensaje
                }
            
            # Tomar el backup más reciente
            backup_mas_reciente = max(backups_encontrados, key=os.path.getmtime)
            
            # Restaurar archivo
            shutil.copy2(str(backup_mas_reciente), ruta_archivo)
            
            mensaje = f"El pergamino sagrado {ruta_archivo} ha sido restaurado desde los archivos ancestrales"
            self.logger.info(mensaje)
            
            return {
                'exitoso': True,
                'accion': 'restaurar_backup',
                'archivo': ruta_archivo,
                'backup_usado': str(backup_mas_reciente),
                'mensaje': mensaje
            }
        
        except Exception as e:
            mensaje = f"Los dioses no pudieron restaurar el pergamino {ruta_archivo}: {e}"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'accion': 'restaurar_backup',
                'archivo': ruta_archivo,
                'mensaje': mensaje
            }
    
    def crear_backup_automatico(self, ruta_archivo: str) -> Dict[str, Any]:
        """
        Crea una copia de seguridad automática de un archivo.
        
        Args:
            ruta_archivo: Ruta del archivo a respaldar
            
        Returns:
            Dict con resultado de la operación
        """
        if not os.path.exists(ruta_archivo):
            return {
                'exitoso': False,
                'mensaje': f"El pergamino {ruta_archivo} no existe en este reino"
            }
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_backup = f"backup_{os.path.basename(ruta_archivo)}_{timestamp}"
            destino_backup = os.path.join(self.directorio_backups, nombre_backup)
            
            crear_ruta_segura(destino_backup)
            shutil.copy2(ruta_archivo, destino_backup)
            
            mensaje = f"Una copia del pergamino {ruta_archivo} ha sido guardada en la cripta del tiempo"
            self.logger.info(mensaje)
            
            return {
                'exitoso': True,
                'accion': 'crear_backup',
                'archivo_original': ruta_archivo,
                'archivo_backup': destino_backup,
                'mensaje': mensaje
            }
        
        except Exception as e:
            mensaje = f"No se pudo crear copia del pergamino {ruta_archivo}: {e}"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'accion': 'crear_backup',
                'archivo_original': ruta_archivo,
                'mensaje': mensaje
            }


class MonitorEventos:
    """Monitor de eventos para detección de amenazas en tiempo real."""
    
    def __init__(self, callback_evento: Callable):
        """
        Inicializa el monitor de eventos.
        
        Args:
            callback_evento: Función a llamar cuando se detecta un evento
        """
        self.logger = configurar_logger_modulo("monitor_eventos")
        self.callback_evento = callback_evento
        self.activo = False
        self.hilo_monitor = None
        
        self.logger.info("El monitor de eventos ha abierto sus ojos celestiales")
    
    def iniciar_monitoreo(self):
        """Inicia el monitoreo de eventos en tiempo real."""
        if self.activo:
            self.logger.warning("El monitor ya vigila los vientos del reino")
            return
        
        self.activo = True
        self.hilo_monitor = threading.Thread(target=self._loop_monitoreo, daemon=True)
        self.hilo_monitor.start()
        
        self.logger.info("El monitor de eventos ha comenzado su vigilia eterna")
    
    def detener_monitoreo(self):
        """Detiene el monitoreo de eventos."""
        self.activo = False
        if self.hilo_monitor:
            self.hilo_monitor.join(timeout=5)
        
        self.logger.info("El monitor de eventos ha cerrado sus ojos para el descanso")
    
    def _loop_monitoreo(self):
        """Loop principal de monitoreo de eventos."""
        while self.activo:
            try:
                # Monitorear logs de SSH
                self._monitorear_ssh()
                
                # Monitorear procesos sospechosos
                self._monitorear_procesos()
                
                # Monitorear cambios en archivos críticos
                self._monitorear_archivos_criticos()
                
                # Monitorear conexiones de red
                self._monitorear_conexiones_red()
                
                time.sleep(5)  # Pausa entre ciclos de monitoreo
            
            except Exception as e:
                self.logger.error(f"Error en loop de monitoreo: {e}")
                time.sleep(10)
    
    def _monitorear_ssh(self):
        """Monitorea intentos de login SSH fallidos."""
        try:
            # Leer últimas líneas del log de auth
            resultado = subprocess.run(
                ['tail', '-n', '50', '/var/log/auth.log'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.split('\n')
                
                for linea in lineas:
                    if 'Failed password' in linea or 'Invalid user' in linea:
                        # Extraer IP
                        import re
                        match_ip = re.search(r'from (\d+\.\d+\.\d+\.\d+)', linea)
                        
                        if match_ip:
                            ip = match_ip.group(1)
                            self.callback_evento('failed_ssh_login', {
                                'ip': ip,
                                'timestamp': datetime.now(),
                                'log_line': linea
                            })
        
        except Exception as e:
            self.logger.debug(f"Error monitoreando SSH: {e}")
    
    def _monitorear_procesos(self):
        """Monitorea procesos sospechosos."""
        try:
            resultado = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.split('\n')[1:]  # Omitir header
                
                for linea in lineas:
                    if linea.strip():
                        partes = linea.split(None, 10)
                        if len(partes) >= 11:
                            pid = partes[1]
                            comando = partes[10]
                            
                            # Verificar si está en directorio temporal
                            if any(temp_dir in comando for temp_dir in ['/tmp/', '/var/tmp/', '/dev/shm/']):
                                self.callback_evento('proceso_en_temporal', {
                                    'pid': int(pid),
                                    'comando': comando,
                                    'timestamp': datetime.now()
                                })
                            
                            # Verificar nombres sospechosos
                            nombres_sospechosos = ['nc', 'netcat', 'ncat', 'socat']
                            nombre_proceso = os.path.basename(comando.split()[0])
                            
                            if nombre_proceso in nombres_sospechosos:
                                self.callback_evento('proceso_sospechoso', {
                                    'pid': int(pid),
                                    'nombre': nombre_proceso,
                                    'comando': comando,
                                    'timestamp': datetime.now()
                                })
        
        except Exception as e:
            self.logger.debug(f"Error monitoreando procesos: {e}")
    
    def _monitorear_archivos_criticos(self):
        """Monitorea cambios en archivos críticos."""
        archivos_criticos = ['/etc/passwd', '/etc/shadow', '/etc/hosts', '/etc/sudoers']
        
        for archivo in archivos_criticos:
            if os.path.exists(archivo):
                try:
                    stat_info = os.stat(archivo)
                    tiempo_modificacion = stat_info.st_mtime
                    
                    # Aquí se podría implementar comparación con tiempos anteriores
                    # Por simplicidad, solo monitoreamos modificaciones muy recientes
                    tiempo_actual = time.time()
                    if tiempo_actual - tiempo_modificacion < 60:  # Modificado en el último minuto
                        self.callback_evento('archivo_critico_modificado', {
                            'archivo': archivo,
                            'timestamp': datetime.now(),
                            'tiempo_modificacion': tiempo_modificacion
                        })
                
                except Exception as e:
                    self.logger.debug(f"Error monitoreando archivo {archivo}: {e}")
    
    def _monitorear_conexiones_red(self):
        """Monitorea conexiones de red sospechosas."""
        try:
            resultado = subprocess.run(
                ['netstat', '-tuln'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.split('\n')
                
                for linea in lineas:
                    if 'ESTABLISHED' in linea:
                        # Aquí se podrían agregar más verificaciones de conexiones sospechosas
                        # Por ejemplo, comparar con lista de IPs maliciosas
                        pass
        
        except Exception as e:
            self.logger.debug(f"Error monitoreando conexiones: {e}")


class RespuestaAutomatizada:
    """Controlador principal del sistema de respuesta automatizada del Égida."""
    
    def __init__(self):
        """Inicializa el sistema de respuesta automatizada."""
        self.logger = configurar_logger_modulo("respuesta_automatizada")
        self.ejecutor_acciones = EjecutorAcciones()
        self.monitor_eventos = MonitorEventos(self._manejar_evento)
        
        # Estado del sistema
        self.activo = False
        self.reglas_activas = {}
        self.historial_acciones = []
        self.contadores_eventos = {}
        
        # Cargar reglas predefinidas
        self.reglas_disponibles = ReglasDefensaAutomatizada.obtener_reglas_predefinidas()
        
        # Archivo de configuración
        self.archivo_config = "recursos/reglas_respuesta.json"
        self._cargar_configuracion()
        
        self.logger.info("El sistema de respuesta automatizada del Égida ha despertado")
    
    def _cargar_configuracion(self):
        """Carga la configuración desde archivo."""
        try:
            if os.path.exists(self.archivo_config):
                with open(self.archivo_config, 'r', encoding='utf-8') as archivo:
                    config = json.load(archivo)
                    self.reglas_activas = config.get('reglas_activas', {})
                    self.logger.info(f"Configuración cargada: {len(self.reglas_activas)} reglas activas")
        except Exception as e:
            self.logger.warning(f"Error cargando configuración: {e}")
            self.reglas_activas = {}
    
    def _guardar_configuracion(self):
        """Guarda la configuración actual."""
        try:
            crear_ruta_segura(self.archivo_config)
            
            config = {
                'reglas_activas': self.reglas_activas,
                'ultima_actualizacion': datetime.now().isoformat()
            }
            
            with open(self.archivo_config, 'w', encoding='utf-8') as archivo:
                json.dump(config, archivo, ensure_ascii=False, indent=2)
                
            self.logger.info("Configuración guardada en los pergaminos sagrados")
        
        except Exception as e:
            self.logger.error(f"Error guardando configuración: {e}")
    
    def activar_defensa_automatizada(self, configuracion_reglas: Dict[str, Any]) -> Dict[str, Any]:
        """
        Activa el sistema de defensa automatizada con la configuración especificada.
        
        Args:
            configuracion_reglas: Configuración de reglas seleccionadas
            
        Returns:
            Dict con resultado de la activación
        """
        try:
            self.reglas_activas = configuracion_reglas
            self._guardar_configuracion()
            
            # Crear backups automáticos de archivos críticos
            archivos_criticos = ['/etc/passwd', '/etc/shadow', '/etc/hosts', '/etc/sudoers']
            backups_creados = []
            
            for archivo in archivos_criticos:
                if os.path.exists(archivo):
                    resultado_backup = self.ejecutor_acciones.crear_backup_automatico(archivo)
                    if resultado_backup['exitoso']:
                        backups_creados.append(archivo)
            
            # Iniciar monitoreo
            self.monitor_eventos.iniciar_monitoreo()
            self.activo = True
            
            mensaje = (f"¡El Égida Defensivo ha sido forjado! "
                      f"{len(self.reglas_activas)} reglas activas vigilarán el reino. "
                      f"Copias sagradas creadas para {len(backups_creados)} pergaminos críticos.")
            
            self.logger.info(mensaje)
            
            return {
                'exitoso': True,
                'reglas_activas': len(self.reglas_activas),
                'backups_creados': len(backups_creados),
                'mensaje': mensaje
            }
        
        except Exception as e:
            mensaje = f"Una tormenta impidió forjar el Égida Defensivo: {e}"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'mensaje': mensaje
            }
    
    def desactivar_defensa_automatizada(self) -> Dict[str, Any]:
        """
        Desactiva el sistema de defensa automatizada.
        
        Returns:
            Dict con resultado de la desactivación
        """
        try:
            self.monitor_eventos.detener_monitoreo()
            self.activo = False
            
            mensaje = "El Égida Defensivo ha retornado a su descanso eterno"
            self.logger.info(mensaje)
            
            return {
                'exitoso': True,
                'mensaje': mensaje,
                'acciones_realizadas': len(self.historial_acciones)
            }
        
        except Exception as e:
            mensaje = f"Error desactivando el Égida: {e}"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'mensaje': mensaje
            }
    
    def _manejar_evento(self, tipo_evento: str, datos_evento: Dict[str, Any]):
        """
        Maneja eventos detectados y ejecuta acciones correspondientes.
        
        Args:
            tipo_evento: Tipo del evento detectado
            datos_evento: Datos del evento
        """
        if not self.activo:
            return
        
        self.logger.info(f"Evento detectado: {tipo_evento}")
        
        # Buscar reglas que respondan a este tipo de evento
        for categoria, config_categoria in self.reglas_activas.items():
            for nombre_regla, config_regla in config_categoria.get('reglas', {}).items():
                regla_plantilla = self._obtener_regla_plantilla(categoria, nombre_regla)
                
                if regla_plantilla and regla_plantilla.get('evento_disparador') == tipo_evento:
                    if self._evaluar_condicion(regla_plantilla, datos_evento, config_regla):
                        self._ejecutar_accion(regla_plantilla, datos_evento, config_regla)
    
    def _obtener_regla_plantilla(self, categoria: str, nombre_regla: str) -> Optional[Dict[str, Any]]:
        """Obtiene la plantilla de una regla desde las reglas predefinidas."""
        categoria_reglas = self.reglas_disponibles.get(categoria, {}).get('reglas', {})
        return categoria_reglas.get(nombre_regla)
    
    def _evaluar_condicion(self, regla: Dict[str, Any], datos_evento: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """
        Evalúa si la condición de una regla se cumple.
        
        Args:
            regla: Definición de la regla
            datos_evento: Datos del evento
            config: Configuración específica de la regla
            
        Returns:
            True si la condición se cumple
        """
        condicion = regla.get('condicion', {})
        tipo_condicion = condicion.get('tipo')
        
        if tipo_condicion == 'contador':
            # Verificar umbral de eventos
            ip = datos_evento.get('ip', 'unknown')
            clave_contador = f"{regla.get('evento_disparador')}_{ip}"
            
            if clave_contador not in self.contadores_eventos:
                self.contadores_eventos[clave_contador] = {
                    'count': 0,
                    'primera_vez': time.time()
                }
            
            contador = self.contadores_eventos[clave_contador]
            tiempo_actual = time.time()
            ventana_tiempo = condicion.get('ventana_tiempo', 300)
            
            # Resetear contador si ha pasado la ventana de tiempo
            if tiempo_actual - contador['primera_vez'] > ventana_tiempo:
                contador['count'] = 0
                contador['primera_vez'] = tiempo_actual
            
            contador['count'] += 1
            umbral = config.get('umbral_asaltos', condicion.get('umbral', 5))
            
            return contador['count'] >= umbral
        
        elif tipo_condicion == 'patron':
            # Verificar si el evento coincide con patrones
            comando = datos_evento.get('comando', '')
            patrones = condicion.get('patron_ruta', [])
            
            return any(patron in comando for patron in patrones)
        
        elif tipo_condicion == 'lista_negra':
            # Verificar si el proceso está en la lista negra
            nombre_proceso = datos_evento.get('nombre', '')
            nombres_proceso = condicion.get('nombres_proceso', [])
            
            return nombre_proceso in nombres_proceso
        
        elif tipo_condicion == 'lista_archivos':
            # Verificar si el archivo está en la lista protegida
            archivo = datos_evento.get('archivo', '')
            archivos_protegidos = condicion.get('archivos_protegidos', [])
            
            return archivo in archivos_protegidos
        
        return False
    
    def _ejecutar_accion(self, regla: Dict[str, Any], datos_evento: Dict[str, Any], config: Dict[str, Any]):
        """
        Ejecuta la acción definida en una regla.
        
        Args:
            regla: Definición de la regla
            datos_evento: Datos del evento
            config: Configuración específica
        """
        accion = regla.get('accion')
        
        try:
            resultado = None
            
            if accion == 'bloquear_ip_iptables':
                ip = datos_evento.get('ip')
                duracion = config.get('duracion_destierro', 60)
                resultado = self.ejecutor_acciones.bloquear_ip_iptables(ip, duracion)
            
            elif accion == 'terminar_proceso':
                pid = datos_evento.get('pid')
                nombre = datos_evento.get('nombre', 'proceso_desconocido')
                resultado = self.ejecutor_acciones.terminar_proceso(pid, nombre)
            
            elif accion == 'terminar_proceso_y_cuarentena':
                pid = datos_evento.get('pid')
                comando = datos_evento.get('comando', '')
                ruta_ejecutable = comando.split()[0] if comando else ''
                nombre = datos_evento.get('nombre', 'proceso_temporal')
                resultado = self.ejecutor_acciones.terminar_proceso_y_cuarentena(pid, ruta_ejecutable, nombre)
            
            elif accion == 'restaurar_desde_backup':
                archivo = datos_evento.get('archivo')
                resultado = self.ejecutor_acciones.restaurar_desde_backup(archivo)
            
            # Registrar acción en historial
            if resultado:
                entrada_historial = {
                    'timestamp': datetime.now().isoformat(),
                    'regla': regla.get('nombre', 'Regla desconocida'),
                    'evento': datos_evento,
                    'resultado': resultado,
                    'mensaje': regla.get('mensaje_activacion', 'Acción ejecutada')
                }
                
                self.historial_acciones.append(entrada_historial)
                
                # Mantener solo las últimas 100 acciones en memoria
                if len(self.historial_acciones) > 100:
                    self.historial_acciones = self.historial_acciones[-100:]
                
                self.logger.info(f"Acción ejecutada: {regla.get('mensaje_activacion', 'Acción completada')}")
        
        except Exception as e:
            self.logger.error(f"Error ejecutando acción {accion}: {e}")
    
    def obtener_historial_acciones(self, limite: int = 50) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de acciones ejecutadas.
        
        Args:
            limite: Número máximo de acciones a retornar
            
        Returns:
            Lista de acciones ejecutadas
        """
        return self.historial_acciones[-limite:]
    
    def obtener_estado_sistema(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del sistema de respuesta automatizada.
        
        Returns:
            Dict con el estado del sistema
        """
        return {
            'activo': self.activo,
            'reglas_activas': len(self.reglas_activas),
            'acciones_ejecutadas': len(self.historial_acciones),
            'eventos_monitoreados': len(self.contadores_eventos),
            'ultima_accion': self.historial_acciones[-1]['timestamp'] if self.historial_acciones else None
        }
    
    def generar_reporte_markdown(self) -> str:
        """
        Genera un reporte del sistema en formato Markdown.
        
        Returns:
            Reporte en formato Markdown
        """
        estado = self.obtener_estado_sistema()
        
        md = "# ⚔️ Reporte del Égida Defensivo\n\n"
        md += f"**Estado:** {'🛡️ ACTIVO' if estado['activo'] else '😴 INACTIVO'}\n"
        md += f"**Reglas Activas:** {estado['reglas_activas']}\n"
        md += f"**Acciones Ejecutadas:** {estado['acciones_ejecutadas']}\n"
        md += f"**Última Acción:** {estado['ultima_accion'] or 'Ninguna'}\n\n"
        
        # Historial reciente
        historial = self.obtener_historial_acciones(10)
        if historial:
            md += "## 📜 Acciones Recientes del Égida\n\n"
            for accion in reversed(historial):
                md += f"- **{accion['timestamp']}**: {accion['mensaje']}\n"
            md += "\n"
        
        # Reglas activas
        if self.reglas_activas:
            md += "## ⚖️ Reglas de Defensa Activas\n\n"
            for categoria, config in self.reglas_activas.items():
                md += f"### {config.get('titulo', categoria)}\n\n"
                for nombre_regla in config.get('reglas', {}):
                    regla_plantilla = self._obtener_regla_plantilla(categoria, nombre_regla)
                    if regla_plantilla:
                        md += f"- **{regla_plantilla['nombre']}**: {regla_plantilla['descripcion']}\n"
                md += "\n"
        
        md += "---\n\n"
        md += "*Reporte generado por el Sistema de Respuesta Automatizada del Égida*\n"
        
        return md
