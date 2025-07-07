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
        Simula el bloqueo de una IP (sin iptables, portable y seguro).
        Args:
            ip: Dirección IP a bloquear
            duracion_minutos: Duración del bloqueo en minutos
        Returns:
            Dict con resultado de la acción
        """
        self.logger.warning("Bloqueo real de IP no implementado sin iptables. Acción simulada para portabilidad y clean code.")
        mensaje = f"(Simulado) El rayo de Zeus ha caído sobre la IP {ip} - desterrada por {duracion_minutos} minutos"
        return {
            'exitoso': True,
            'accion': 'bloquear_ip',
            'ip': ip,
            'duracion_minutos': duracion_minutos,
            'mensaje': mensaje
        }

    def _desbloquear_ip_automatico(self, ip: str):
        """Simula el desbloqueo automático de una IP (sin iptables)."""
        self.logger.warning(f"(Simulado) La IP {ip} ha cumplido su destierro - se le permite retornar al reino (sin iptables)")
    
    
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
                destino_cuarentena = os.path.join("/home/dogsoul/Ares-Aegis/cuarentena_avanzada/activos/", nombre_archivo)
                
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
    """
    Modelo del sistema de respuesta automatizada del Égida.
    
    NOTA: Esta clase mantiene la interfaz original para compatibilidad,
    pero delega la lógica de control al ControladorRespuestaAutomatizada.
    """
    
    def __init__(self):
        """Inicializa el sistema de respuesta automatizada."""
        self.logger = configurar_logger_modulo("respuesta_automatizada")
        
        # Importar controlador dinámicamente para evitar dependencias circulares
        try:
            from ..controladores.controlador_respuesta_automatizada import ControladorRespuestaAutomatizada
            self.controlador = ControladorRespuestaAutomatizada()
        except ImportError:
            # Fallback temporal si el controlador no está disponible
            self.logger.warning("Controlador de respuesta automatizada no disponible, usando implementación legacy")
            self.controlador = None
            self._inicializar_legacy()
        
        self.logger.info("El sistema de respuesta automatizada del Égida ha despertado")
    
    def _inicializar_legacy(self):
        """Inicialización legacy para compatibilidad."""
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
    
    def activar_defensa_automatizada(self, configuracion_reglas: Dict[str, Any]) -> Dict[str, Any]:
        """
        Activa el sistema de defensa automatizada con la configuración especificada.
        
        Args:
            configuracion_reglas: Configuración de reglas seleccionadas
            
        Returns:
            Dict con resultado de la activación
        """
        if self.controlador:
            return self.controlador.activar_sistema(configuracion_reglas)
        else:
            return self._activar_defensa_automatizada_legacy(configuracion_reglas)
    
    def desactivar_defensa_automatizada(self) -> Dict[str, Any]:
        """
        Desactiva el sistema de defensa automatizada.
        
        Returns:
            Dict con resultado de la desactivación
        """
        if self.controlador:
            return self.controlador.desactivar_sistema()
        else:
            return self._desactivar_defensa_automatizada_legacy()
    
    def obtener_estado_sistema(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del sistema de respuesta automatizada.
        
        Returns:
            Dict con el estado del sistema
        """
        if self.controlador:
            return self.controlador.obtener_estado()
        else:
            return self._obtener_estado_sistema_legacy()
    
    def generar_reporte_acciones(self, callback_progreso: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Genera un reporte de las acciones realizadas por el sistema.
        
        Args:
            callback_progreso: Función de callback para progreso
            
        Returns:
            Dict con el reporte
        """
        if self.controlador:
            historial = self.controlador.obtener_historial_acciones()
            estadisticas = self.controlador.obtener_estadisticas_eventos()
            
            return {
                'exitoso': True,
                'total_acciones': len(historial),
                'historial_reciente': historial[-10:],  # Últimas 10 acciones
                'estadisticas': estadisticas
            }
        else:
            return self._generar_reporte_acciones_legacy(callback_progreso)
    
    # Métodos legacy para compatibilidad
    
    def _cargar_configuracion(self):
        """Carga la configuración desde archivo (legacy)."""
        try:
            if os.path.exists(self.archivo_config):
                with open(self.archivo_config, 'r', encoding='utf-8') as archivo:
                    config = json.load(archivo)
                    self.reglas_activas = config.get('reglas_activas', {})
                    self.logger.info(f"Configuración cargada: {len(self.reglas_activas)} reglas activas")
        except Exception as e:
            self.logger.warning(f"Error cargando configuración: {e}")
            self.reglas_activas = {}
    
    def _activar_defensa_automatizada_legacy(self, configuracion_reglas: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación legacy de activación."""
        try:
            self.reglas_activas = configuracion_reglas
            self.monitor_eventos.iniciar_monitoreo()
            self.activo = True
            
            mensaje = f"Sistema activado con {len(configuracion_reglas)} reglas (modo legacy)"
            self.logger.info(mensaje)
            
            return {
                'exitoso': True,
                'reglas_activas': len(configuracion_reglas),
                'mensaje': mensaje
            }
        except Exception as e:
            mensaje = f"Error en activación legacy: {e}"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'mensaje': mensaje
            }
    
    def _desactivar_defensa_automatizada_legacy(self) -> Dict[str, Any]:
        """Implementación legacy de desactivación."""
        try:
            self.monitor_eventos.detener_monitoreo()
            self.activo = False
            
            mensaje = "Sistema desactivado (modo legacy)"
            self.logger.info(mensaje)
            
            return {
                'exitoso': True,
                'mensaje': mensaje,
                'acciones_realizadas': len(self.historial_acciones)
            }
        except Exception as e:
            mensaje = f"Error en desactivación legacy: {e}"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'mensaje': mensaje
            }
    
    def _obtener_estado_sistema_legacy(self) -> Dict[str, Any]:
        """Implementación legacy de obtener estado."""
        return {
            'activo': getattr(self, 'activo', False),
            'reglas_activas': len(getattr(self, 'reglas_activas', {})),
            'eventos_procesados': len(getattr(self, 'contadores_eventos', {})),
            'acciones_realizadas': len(getattr(self, 'historial_acciones', [])),
            'modo': 'legacy'
        }
    
    def _generar_reporte_acciones_legacy(self, callback_progreso: Optional[Callable] = None) -> Dict[str, Any]:
        """Implementación legacy de generación de reportes."""
        if callback_progreso:
            callback_progreso("Generando reporte en modo legacy...")
        
        return {
            'exitoso': True,
            'total_acciones': len(getattr(self, 'historial_acciones', [])),
            'modo': 'legacy'
        }
    
    def _manejar_evento(self, tipo_evento: str, datos_evento: Dict[str, Any]):
        """
        Delegación del manejo de eventos al controlador.
        Método mantenido para compatibilidad con MonitorEventos.
        
        Args:
            tipo_evento: Tipo del evento detectado
            datos_evento: Datos del evento
        """
        if self.controlador:
            self.controlador.manejar_evento(tipo_evento, datos_evento)
        else:
            # Legacy implementation
            self.logger.info(f"Evento detectado (legacy): {tipo_evento}")
            # TODO: Implementar lógica legacy si es necesaria


# ==============================================================================
# CLASES MODELO PURAS (sin lógica de controlador)
# ==============================================================================
