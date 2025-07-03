#!/usr/bin/env python3
"""
Respondedor de Incidentes - Ares Aegis
Módulo para respuesta automatizada y manual a incidentes de seguridad

Este módulo coordina las respuestas a incidentes detectados,
desde bloqueo automático hasta notificaciones y generación de reportes.

Autor: DogSoulDev
Versión: 2.0.0 - "Los Guardianes de Némesis"
"""

import os
import time
import subprocess
import threading
import smtplib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, NamedTuple
from enum import Enum
from email.message import EmailMessage
from ..utilidades.ayuda_logging import configurar_logger_modulo


class TipoIncidente(Enum):
    """Tipos de incidentes que pueden ser manejados."""
    MALWARE_DETECTADO = "malware_detectado"
    ACCESO_NO_AUTORIZADO = "acceso_no_autorizado"
    FUERZA_BRUTA = "fuerza_bruta"
    ESCANEO_PUERTOS = "escaneo_puertos"
    PROCESO_SOSPECHOSO = "proceso_sospechoso"
    ARCHIVO_SOSPECHOSO = "archivo_sospechoso"
    TRAFICO_ANOMALO = "trafico_anomalo"
    ESCALADA_PRIVILEGIOS = "escalada_privilegios"
    FALLA_SERVICIO_CRITICO = "falla_servicio_critico"
    AGOTAMIENTO_RECURSOS = "agotamiento_recursos"


class NivelRespuesta(Enum):
    """Niveles de respuesta para incidentes."""
    AUTOMATICA = "automatica"
    NOTIFICACION = "notificacion"
    MANUAL = "manual"
    CRITICA = "critica"


class AccionRespuesta(NamedTuple):
    """Acción de respuesta a un incidente."""
    tipo: str
    descripcion: str
    comando: Optional[str]
    requiere_confirmacion: bool
    nivel_privilegios: str
    timeout: int


class Incidente:
    """Representa un incidente de seguridad detectado."""
    
    def __init__(self, tipo: TipoIncidente, descripcion: str, gravedad: str,
                 metadatos: Dict[str, Any], fuente: str):
        """
        Inicializa un incidente.
        
        Args:
            tipo: Tipo del incidente
            descripcion: Descripción del incidente
            gravedad: Nivel de gravedad (BAJO, MEDIO, ALTO, CRITICO)
            metadatos: Información adicional del incidente
            fuente: Componente que detectó el incidente
        """
        self.id = self._generar_id()
        self.tipo = tipo
        self.descripcion = descripcion
        self.gravedad = gravedad
        self.metadatos = metadatos
        self.fuente = fuente
        self.timestamp_deteccion = datetime.now()
        self.timestamp_respuesta: Optional[datetime] = None
        self.estado = "DETECTADO"
        self.acciones_ejecutadas: List[str] = []
        self.respuesta_automatica_aplicada = False
        self.notificaciones_enviadas: List[str] = []
    
    def _generar_id(self) -> str:
        """Genera un ID único para el incidente."""
        timestamp = int(time.time())
        return f"INC-{timestamp}"
    
    def marcar_como_en_proceso(self):
        """Marca el incidente como en proceso de respuesta."""
        self.estado = "EN_PROCESO"
        self.timestamp_respuesta = datetime.now()
    
    def marcar_como_resuelto(self):
        """Marca el incidente como resuelto."""
        self.estado = "RESUELTO"
    
    def agregar_accion(self, accion: str):
        """Agrega una acción ejecutada al incidente."""
        self.acciones_ejecutadas.append(f"{datetime.now().strftime('%H:%M:%S')} - {accion}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el incidente a diccionario."""
        return {
            'id': self.id,
            'tipo': self.tipo.value,
            'descripcion': self.descripcion,
            'gravedad': self.gravedad,
            'metadatos': self.metadatos,
            'fuente': self.fuente,
            'timestamp_deteccion': self.timestamp_deteccion.isoformat(),
            'timestamp_respuesta': self.timestamp_respuesta.isoformat() if self.timestamp_respuesta else None,
            'estado': self.estado,
            'acciones_ejecutadas': self.acciones_ejecutadas,
            'respuesta_automatica_aplicada': self.respuesta_automatica_aplicada,
            'notificaciones_enviadas': self.notificaciones_enviadas
        }


class ConfiguracionRespuesta:
    """Configuración de respuestas automáticas para tipos de incidentes."""
    
    def __init__(self):
        """Inicializa la configuración de respuestas."""
        self.configuraciones = {
            TipoIncidente.MALWARE_DETECTADO: {
                'nivel_respuesta': NivelRespuesta.AUTOMATICA,
                'acciones': [
                    AccionRespuesta(
                        tipo="cuarentena_archivo",
                        descripcion="Mover archivo a cuarentena",
                        comando=None,  # Se maneja internamente
                        requiere_confirmacion=False,
                        nivel_privilegios="usuario",
                        timeout=30
                    ),
                    AccionRespuesta(
                        tipo="terminacion_proceso",
                        descripcion="Terminar procesos relacionados",
                        comando="pkill -f {proceso}",
                        requiere_confirmacion=False,
                        nivel_privilegios="root",
                        timeout=10
                    )
                ]
            },
            
            TipoIncidente.FUERZA_BRUTA: {
                'nivel_respuesta': NivelRespuesta.AUTOMATICA,
                'acciones': [
                    AccionRespuesta(
                        tipo="bloqueo_ip",
                        descripcion="Bloquear IP atacante",
                        comando="iptables -A INPUT -s {ip} -j DROP",
                        requiere_confirmacion=False,
                        nivel_privilegios="root",
                        timeout=5
                    ),
                    AccionRespuesta(
                        tipo="fail2ban_ban",
                        descripcion="Activar fail2ban para IP",
                        comando="fail2ban-client set sshd banip {ip}",
                        requiere_confirmacion=False,
                        nivel_privilegios="root",
                        timeout=10
                    )
                ]
            },
            
            TipoIncidente.ESCANEO_PUERTOS: {
                'nivel_respuesta': NivelRespuesta.NOTIFICACION,
                'acciones': [
                    AccionRespuesta(
                        tipo="bloqueo_temporal_ip",
                        descripcion="Bloquear IP temporalmente",
                        comando="iptables -A INPUT -s {ip} -j DROP",
                        requiere_confirmacion=True,
                        nivel_privilegios="root",
                        timeout=5
                    )
                ]
            },
            
            TipoIncidente.PROCESO_SOSPECHOSO: {
                'nivel_respuesta': NivelRespuesta.NOTIFICACION,
                'acciones': [
                    AccionRespuesta(
                        tipo="suspension_proceso",
                        descripcion="Suspender proceso sospechoso",
                        comando="kill -STOP {pid}",
                        requiere_confirmacion=True,
                        nivel_privilegios="root",
                        timeout=5
                    ),
                    AccionRespuesta(
                        tipo="analisis_profundo",
                        descripcion="Análisis profundo del proceso",
                        comando=None,
                        requiere_confirmacion=False,
                        nivel_privilegios="usuario",
                        timeout=60
                    )
                ]
            },
            
            TipoIncidente.ARCHIVO_SOSPECHOSO: {
                'nivel_respuesta': NivelRespuesta.AUTOMATICA,
                'acciones': [
                    AccionRespuesta(
                        tipo="cuarentena_preventiva",
                        descripcion="Cuarentena preventiva del archivo",
                        comando=None,
                        requiere_confirmacion=False,
                        nivel_privilegios="usuario",
                        timeout=30
                    )
                ]
            },
            
            TipoIncidente.ESCALADA_PRIVILEGIOS: {
                'nivel_respuesta': NivelRespuesta.CRITICA,
                'acciones': [
                    AccionRespuesta(
                        tipo="bloqueo_usuario",
                        descripcion="Bloquear cuenta de usuario",
                        comando="usermod -L {usuario}",
                        requiere_confirmacion=True,
                        nivel_privilegios="root",
                        timeout=5
                    ),
                    AccionRespuesta(
                        tipo="auditoria_sesion",
                        descripcion="Auditoría completa de la sesión",
                        comando=None,
                        requiere_confirmacion=False,
                        nivel_privilegios="root",
                        timeout=120
                    )
                ]
            },
            
            TipoIncidente.FALLA_SERVICIO_CRITICO: {
                'nivel_respuesta': NivelRespuesta.AUTOMATICA,
                'acciones': [
                    AccionRespuesta(
                        tipo="reinicio_servicio",
                        descripcion="Reiniciar servicio crítico",
                        comando="systemctl restart {servicio}",
                        requiere_confirmacion=False,
                        nivel_privilegios="root",
                        timeout=30
                    )
                ]
            }
        }
    
    def obtener_configuracion(self, tipo_incidente: TipoIncidente) -> Dict[str, Any]:
        """Obtiene la configuración para un tipo de incidente."""
        return self.configuraciones.get(tipo_incidente, {
            'nivel_respuesta': NivelRespuesta.MANUAL,
            'acciones': []
        })


class RespondedorIncidentes:
    """Respondedor principal de incidentes de seguridad."""
    
    def __init__(self, siem=None, cuarentena=None):
        """
        Inicializa el respondedor de incidentes.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
            cuarentena: Instancia del sistema de cuarentena
        """
        self.logger = configurar_logger_modulo("respondedor_incidentes")
        self.siem = siem
        self.cuarentena = cuarentena
        
        # Estado del respondedor
        self.activo = False
        self.modo_automatico = True
        self.incidentes: List[Incidente] = []
        self.incidentes_resueltos: List[Incidente] = []
        
        # Configuración
        self.config_respuesta = ConfiguracionRespuesta()
        self.config_notificaciones = {
            'email_enabled': False,
            'email_smtp_server': 'localhost',
            'email_smtp_port': 587,
            'email_usuario': '',
            'email_password': '',
            'email_destinatarios': [],
            'webhook_urls': [],
            'telegram_enabled': False,
            'telegram_bot_token': '',
            'telegram_chat_id': ''
        }
        
        # Callbacks personalizados
        self.callbacks_personalizados: Dict[TipoIncidente, List[Callable]] = {}
        
        # Límites de seguridad
        self.limite_acciones_por_minuto = 10
        self.acciones_recientes: List[datetime] = []
        
        # Hilo para procesamiento de incidentes
        self.hilo_procesamiento: Optional[threading.Thread] = None
        self.cola_incidentes: List[Incidente] = []
        self.lock_cola = threading.Lock()
        
        self.logger.info("Los Guardianes de Némesis han tomado posición en los bastiones")
    
    def activar(self):
        """Activa el respondedor de incidentes."""
        if self.activo:
            self.logger.warning("Los Guardianes ya vigilan el reino")
            return
        
        self.activo = True
        
        # Iniciar hilo de procesamiento
        self.hilo_procesamiento = threading.Thread(target=self._procesar_cola_incidentes, daemon=True)
        self.hilo_procesamiento.start()
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_INICIADO,
                "Los Guardianes de Némesis inician la vigilancia eternal",
                {"componente": "respondedor_incidentes"},
                "MEDIO"
            )
        
        self.logger.info("Los Guardianes de Némesis han activado la respuesta divina")
    
    def desactivar(self):
        """Desactiva el respondedor de incidentes."""
        if not self.activo:
            return
        
        self.activo = False
        
        # Esperar que termine el hilo de procesamiento
        if self.hilo_procesamiento:
            self.hilo_procesamiento.join(timeout=10)
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_DETENIDO,
                "Los Guardianes de Némesis han regresado al Olimpo",
                {
                    "incidentes_procesados": len(self.incidentes),
                    "incidentes_resueltos": len(self.incidentes_resueltos)
                },
                "MEDIO"
            )
        
        self.logger.info("Los Guardianes de Némesis han cerrado la guardia")
    
    def procesar_incidente(self, tipo: TipoIncidente, descripcion: str, gravedad: str,
                          metadatos: Dict[str, Any], fuente: str) -> str:
        """
        Procesa un nuevo incidente de seguridad.
        
        Args:
            tipo: Tipo del incidente
            descripcion: Descripción del incidente
            gravedad: Nivel de gravedad
            metadatos: Información adicional
            fuente: Componente que detectó el incidente
            
        Returns:
            ID del incidente creado
        """
        if not self.activo:
            self.logger.warning("Incidente recibido pero los Guardianes no están activos")
            return ""
        
        # Crear incidente
        incidente = Incidente(tipo, descripcion, gravedad, metadatos, fuente)
        
        # Agregar a la cola para procesamiento asíncrono
        with self.lock_cola:
            self.cola_incidentes.append(incidente)
        
        self.logger.info(f"Nuevo incidente detectado: {incidente.id} - {descripcion}")
        
        return incidente.id
    
    def _procesar_cola_incidentes(self):
        """Procesa la cola de incidentes de forma asíncrona."""
        self.logger.info("Iniciando procesamiento asíncrono de incidentes")
        
        while self.activo:
            try:
                # Obtener incidentes de la cola
                incidentes_a_procesar = []
                with self.lock_cola:
                    if self.cola_incidentes:
                        incidentes_a_procesar = self.cola_incidentes[:]
                        self.cola_incidentes.clear()
                
                # Procesar cada incidente
                for incidente in incidentes_a_procesar:
                    self._procesar_incidente_individual(incidente)
                
                time.sleep(1)  # Pausa breve para evitar uso excesivo de CPU
                
            except Exception as e:
                self.logger.error(f"Error en procesamiento de cola de incidentes: {e}")
                time.sleep(5)
    
    def _procesar_incidente_individual(self, incidente: Incidente):
        """Procesa un incidente individual."""
        try:
            incidente.marcar_como_en_proceso()
            self.incidentes.append(incidente)
            
            # Obtener configuración de respuesta
            config = self.config_respuesta.obtener_configuracion(incidente.tipo)
            nivel_respuesta = config.get('nivel_respuesta', NivelRespuesta.MANUAL)
            
            # Registrar en SIEM
            if self.siem:
                from .siem import TipoEvento
                self.siem.registrar_evento(
                    TipoEvento.AMENAZA_DETECTADA,
                    f"Los Guardianes responden a: {incidente.descripcion}",
                    {
                        "incidente_id": incidente.id,
                        "tipo_incidente": incidente.tipo.value,
                        "gravedad": incidente.gravedad,
                        "nivel_respuesta": nivel_respuesta.value
                    },
                    incidente.gravedad
                )
            
            # Ejecutar respuesta según el nivel
            if nivel_respuesta == NivelRespuesta.AUTOMATICA:
                self._ejecutar_respuesta_automatica(incidente, config)
            elif nivel_respuesta == NivelRespuesta.CRITICA:
                self._ejecutar_respuesta_critica(incidente, config)
            
            # Siempre enviar notificaciones si están configuradas
            if nivel_respuesta in [NivelRespuesta.NOTIFICACION, NivelRespuesta.CRITICA]:
                self._enviar_notificaciones(incidente)
            
            # Ejecutar callbacks personalizados
            self._ejecutar_callbacks_personalizados(incidente)
            
            incidente.marcar_como_resuelto()
            self.incidentes_resueltos.append(incidente)
            
            self.logger.info(f"Incidente {incidente.id} procesado y resuelto")
            
        except Exception as e:
            self.logger.error(f"Error procesando incidente {incidente.id}: {e}")
            incidente.agregar_accion(f"ERROR: {str(e)}")
    
    def _ejecutar_respuesta_automatica(self, incidente: Incidente, config: Dict[str, Any]):
        """Ejecuta respuesta automática para un incidente."""
        acciones = config.get('acciones', [])
        
        for accion in acciones:
            if not accion.requiere_confirmacion:
                self._ejecutar_accion(incidente, accion)
        
        incidente.respuesta_automatica_aplicada = True
        incidente.agregar_accion("Respuesta automática aplicada por los Guardianes")
    
    def _ejecutar_respuesta_critica(self, incidente: Incidente, config: Dict[str, Any]):
        """Ejecuta respuesta crítica inmediata."""
        acciones = config.get('acciones', [])
        
        # En modo crítico, ejecutar todas las acciones inmediatamente
        for accion in acciones:
            self._ejecutar_accion(incidente, accion)
        
        incidente.agregar_accion("Respuesta crítica ejecutada - protocolo de emergencia activado")
        
        # Notificación especial para incidentes críticos
        self._enviar_notificacion_critica(incidente)
    
    def _ejecutar_accion(self, incidente: Incidente, accion: AccionRespuesta) -> bool:
        """
        Ejecuta una acción específica de respuesta.
        
        Args:
            incidente: Incidente al que responder
            accion: Acción a ejecutar
            
        Returns:
            True si la acción se ejecutó correctamente
        """
        # Verificar límites de seguridad
        if not self._verificar_limites_seguridad():
            incidente.agregar_accion(f"BLOQUEADO: Límite de acciones excedido para {accion.tipo}")
            return False
        
        try:
            if accion.tipo == "cuarentena_archivo":
                return self._ejecutar_cuarentena_archivo(incidente, accion)
            
            elif accion.tipo == "terminacion_proceso":
                return self._ejecutar_terminacion_proceso(incidente, accion)
            
            elif accion.tipo == "bloqueo_ip":
                return self._ejecutar_bloqueo_ip(incidente, accion)
            
            elif accion.tipo == "bloqueo_temporal_ip":
                return self._ejecutar_bloqueo_temporal_ip(incidente, accion)
            
            elif accion.tipo == "suspension_proceso":
                return self._ejecutar_suspension_proceso(incidente, accion)
            
            elif accion.tipo == "reinicio_servicio":
                return self._ejecutar_reinicio_servicio(incidente, accion)
            
            elif accion.tipo == "bloqueo_usuario":
                return self._ejecutar_bloqueo_usuario(incidente, accion)
            
            elif accion.comando:
                return self._ejecutar_comando_sistema(incidente, accion)
            
            else:
                self.logger.warning(f"Tipo de acción no reconocido: {accion.tipo}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error ejecutando acción {accion.tipo}: {e}")
            incidente.agregar_accion(f"ERROR ejecutando {accion.tipo}: {str(e)}")
            return False
    
    def _verificar_limites_seguridad(self) -> bool:
        """Verifica que no se excedan los límites de seguridad para acciones."""
        ahora = datetime.now()
        ventana = timedelta(minutes=1)
        
        # Limpiar acciones antiguas
        self.acciones_recientes = [
            timestamp for timestamp in self.acciones_recientes
            if ahora - timestamp <= ventana
        ]
        
        # Verificar límite
        if len(self.acciones_recientes) >= self.limite_acciones_por_minuto:
            self.logger.warning("Límite de acciones por minuto excedido")
            return False
        
        # Agregar acción actual
        self.acciones_recientes.append(ahora)
        return True
    
    def _ejecutar_cuarentena_archivo(self, incidente: Incidente, accion: AccionRespuesta) -> bool:
        """Ejecuta cuarentena de archivo."""
        if not self.cuarentena:
            incidente.agregar_accion("FALLO: Sistema de cuarentena no disponible")
            return False
        
        archivo = incidente.metadatos.get('archivo')
        if not archivo:
            incidente.agregar_accion("FALLO: No se especificó archivo para cuarentena")
            return False
        
        try:
            resultado = self.cuarentena.cuarentenar_archivo(archivo, f"Incidente: {incidente.id}")
            if resultado:
                incidente.agregar_accion(f"Archivo {archivo} enviado a cuarentena")
                return True
            else:
                incidente.agregar_accion(f"FALLO: No se pudo cuarentenar {archivo}")
                return False
        except Exception as e:
            incidente.agregar_accion(f"ERROR en cuarentena: {str(e)}")
            return False
    
    def _ejecutar_terminacion_proceso(self, incidente: Incidente, accion: AccionRespuesta) -> bool:
        """Ejecuta terminación de proceso."""
        pid = incidente.metadatos.get('pid')
        if not pid:
            incidente.agregar_accion("FALLO: No se especificó PID para terminación")
            return False
        
        try:
            resultado = subprocess.run(
                ['kill', '-TERM', str(pid)],
                capture_output=True,
                text=True,
                timeout=accion.timeout
            )
            
            if resultado.returncode == 0:
                incidente.agregar_accion(f"Proceso {pid} terminado exitosamente")
                return True
            else:
                incidente.agregar_accion(f"FALLO terminando proceso {pid}: {resultado.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            incidente.agregar_accion(f"TIMEOUT terminando proceso {pid}")
            return False
        except Exception as e:
            incidente.agregar_accion(f"ERROR terminando proceso: {str(e)}")
            return False
    
    def _ejecutar_bloqueo_ip(self, incidente: Incidente, accion: AccionRespuesta) -> bool:
        """Ejecuta bloqueo de IP con iptables."""
        ip = incidente.metadatos.get('ip_atacante') or incidente.metadatos.get('ip_origen')
        if not ip:
            incidente.agregar_accion("FALLO: No se especificó IP para bloqueo")
            return False
        
        try:
            comando = f"iptables -A INPUT -s {ip} -j DROP"
            resultado = subprocess.run(
                comando.split(),
                capture_output=True,
                text=True,
                timeout=accion.timeout
            )
            
            if resultado.returncode == 0:
                incidente.agregar_accion(f"IP {ip} bloqueada con iptables")
                return True
            else:
                incidente.agregar_accion(f"FALLO bloqueando IP {ip}: {resultado.stderr}")
                return False
        
        except Exception as e:
            incidente.agregar_accion(f"ERROR bloqueando IP: {str(e)}")
            return False
    
    def _ejecutar_bloqueo_temporal_ip(self, incidente: Incidente, accion: AccionRespuesta) -> bool:
        """Ejecuta bloqueo temporal de IP (30 minutos)."""
        ip = incidente.metadatos.get('ip_atacante') or incidente.metadatos.get('ip_origen')
        if not ip:
            return False
        
        try:
            # Bloquear IP
            subprocess.run(
                f"iptables -A INPUT -s {ip} -j DROP".split(),
                capture_output=True,
                timeout=5
            )
            
            # Programar desbloqueo en 30 minutos
            def desbloquear_ip():
                time.sleep(1800)  # 30 minutos
                try:
                    subprocess.run(
                        f"iptables -D INPUT -s {ip} -j DROP".split(),
                        capture_output=True,
                        timeout=5
                    )
                    self.logger.info(f"IP {ip} desbloqueada automáticamente")
                except:
                    pass
            
            threading.Thread(target=desbloquear_ip, daemon=True).start()
            
            incidente.agregar_accion(f"IP {ip} bloqueada temporalmente (30 min)")
            return True
        
        except Exception as e:
            incidente.agregar_accion(f"ERROR en bloqueo temporal: {str(e)}")
            return False
    
    def _ejecutar_suspension_proceso(self, incidente: Incidente, accion: AccionRespuesta) -> bool:
        """Ejecuta suspensión de proceso."""
        pid = incidente.metadatos.get('pid')
        if not pid:
            return False
        
        try:
            resultado = subprocess.run(
                ['kill', '-STOP', str(pid)],
                capture_output=True,
                text=True,
                timeout=accion.timeout
            )
            
            if resultado.returncode == 0:
                incidente.agregar_accion(f"Proceso {pid} suspendido")
                return True
            else:
                incidente.agregar_accion(f"FALLO suspendiendo proceso {pid}")
                return False
        
        except Exception as e:
            incidente.agregar_accion(f"ERROR suspendiendo proceso: {str(e)}")
            return False
    
    def _ejecutar_reinicio_servicio(self, incidente: Incidente, accion: AccionRespuesta) -> bool:
        """Ejecuta reinicio de servicio."""
        servicio = incidente.metadatos.get('servicio')
        if not servicio:
            return False
        
        try:
            resultado = subprocess.run(
                ['systemctl', 'restart', servicio],
                capture_output=True,
                text=True,
                timeout=accion.timeout
            )
            
            if resultado.returncode == 0:
                incidente.agregar_accion(f"Servicio {servicio} reiniciado")
                return True
            else:
                incidente.agregar_accion(f"FALLO reiniciando servicio {servicio}")
                return False
        
        except Exception as e:
            incidente.agregar_accion(f"ERROR reiniciando servicio: {str(e)}")
            return False
    
    def _ejecutar_bloqueo_usuario(self, incidente: Incidente, accion: AccionRespuesta) -> bool:
        """Ejecuta bloqueo de cuenta de usuario."""
        usuario = incidente.metadatos.get('usuario')
        if not usuario:
            return False
        
        try:
            resultado = subprocess.run(
                ['usermod', '-L', usuario],
                capture_output=True,
                text=True,
                timeout=accion.timeout
            )
            
            if resultado.returncode == 0:
                incidente.agregar_accion(f"Usuario {usuario} bloqueado")
                return True
            else:
                incidente.agregar_accion(f"FALLO bloqueando usuario {usuario}")
                return False
        
        except Exception as e:
            incidente.agregar_accion(f"ERROR bloqueando usuario: {str(e)}")
            return False
    
    def _ejecutar_comando_sistema(self, incidente: Incidente, accion: AccionRespuesta) -> bool:
        """Ejecuta un comando de sistema genérico."""
        if not accion.comando:
            return False
        
        try:
            # Formatear comando con metadatos del incidente
            comando_formateado = accion.comando.format(**incidente.metadatos)
            
            resultado = subprocess.run(
                comando_formateado.split(),
                capture_output=True,
                text=True,
                timeout=accion.timeout
            )
            
            if resultado.returncode == 0:
                incidente.agregar_accion(f"Comando ejecutado: {comando_formateado}")
                return True
            else:
                incidente.agregar_accion(f"FALLO comando: {resultado.stderr}")
                return False
        
        except Exception as e:
            incidente.agregar_accion(f"ERROR ejecutando comando: {str(e)}")
            return False
    
    def _enviar_notificaciones(self, incidente: Incidente):
        """Envía notificaciones para un incidente."""
        if self.config_notificaciones.get('email_enabled', False):
            self._enviar_notificacion_email(incidente)
        
        # Agregar más métodos de notificación aquí
        # (webhook, Telegram, etc.)
    
    def _enviar_notificacion_critica(self, incidente: Incidente):
        """Envía notificación especial para incidentes críticos."""
        # Implementar notificaciones de alta prioridad
        self.logger.critical(f"INCIDENTE CRÍTICO: {incidente.descripcion}")
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.AMENAZA_DETECTADA,
                "ALERTA CRÍTICA - Los Guardianes declaran estado de emergencia",
                {
                    "incidente_id": incidente.id,
                    "tipo": incidente.tipo.value,
                    "gravedad": "CRITICO"
                },
                "CRITICO"
            )
    
    def _enviar_notificacion_email(self, incidente: Incidente):
        """Envía notificación por email."""
        try:
            if not self.config_notificaciones.get('email_destinatarios'):
                return
            
            servidor = self.config_notificaciones['email_smtp_server']
            puerto = self.config_notificaciones['email_smtp_port']
            usuario = self.config_notificaciones['email_usuario']
            password = self.config_notificaciones['email_password']
            
            mensaje = EmailMessage()
            mensaje['From'] = usuario
            mensaje['To'] = ', '.join(self.config_notificaciones['email_destinatarios'])
            mensaje['Subject'] = f"[Ares Aegis] Incidente de Seguridad: {incidente.tipo.value}"
            
            cuerpo = f"""
Los Guardianes de Némesis reportan un incidente de seguridad:

ID: {incidente.id}
Tipo: {incidente.tipo.value}
Gravedad: {incidente.gravedad}
Descripción: {incidente.descripcion}
Fuente: {incidente.fuente}
Timestamp: {incidente.timestamp_deteccion}

Acciones Ejecutadas:
{chr(10).join(incidente.acciones_ejecutadas)}

Metadatos:
{incidente.metadatos}
"""
            
            mensaje.set_content(cuerpo)
            
            with smtplib.SMTP(servidor, puerto) as server:
                server.starttls()
                server.login(usuario, password)
                server.send_message(mensaje)
            
            incidente.notificaciones_enviadas.append("email")
            self.logger.info(f"Notificación email enviada para incidente {incidente.id}")
        
        except Exception as e:
            self.logger.error(f"Error enviando notificación email: {e}")
    
    def _ejecutar_callbacks_personalizados(self, incidente: Incidente):
        """Ejecuta callbacks personalizados para el tipo de incidente."""
        callbacks = self.callbacks_personalizados.get(incidente.tipo, [])
        
        for callback in callbacks:
            try:
                callback(incidente)
                incidente.agregar_accion(f"Callback personalizado ejecutado: {callback.__name__}")
            except Exception as e:
                self.logger.error(f"Error ejecutando callback {callback.__name__}: {e}")
                incidente.agregar_accion(f"ERROR en callback {callback.__name__}: {str(e)}")
    
    def registrar_callback_personalizado(self, tipo_incidente: TipoIncidente, callback: Callable):
        """
        Registra un callback personalizado para un tipo de incidente.
        
        Args:
            tipo_incidente: Tipo de incidente
            callback: Función a ejecutar cuando ocurra el incidente
        """
        if tipo_incidente not in self.callbacks_personalizados:
            self.callbacks_personalizados[tipo_incidente] = []
        
        self.callbacks_personalizados[tipo_incidente].append(callback)
        self.logger.info(f"Callback personalizado registrado para {tipo_incidente.value}")
    
    def configurar_notificaciones(self, configuracion: Dict[str, Any]):
        """
        Configura el sistema de notificaciones.
        
        Args:
            configuracion: Diccionario con configuración de notificaciones
        """
        self.config_notificaciones.update(configuracion)
        self.logger.info("Configuración de notificaciones actualizada")
    
    def obtener_incidentes_recientes(self, horas: int = 24) -> List[Dict[str, Any]]:
        """
        Obtiene incidentes recientes.
        
        Args:
            horas: Número de horas hacia atrás
            
        Returns:
            Lista de incidentes en formato diccionario
        """
        timestamp_limite = datetime.now() - timedelta(hours=horas)
        
        incidentes_recientes = [
            incidente for incidente in self.incidentes
            if incidente.timestamp_deteccion > timestamp_limite
        ]
        
        return [incidente.to_dict() for incidente in incidentes_recientes]
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del respondedor."""
        total_incidentes = len(self.incidentes)
        incidentes_resueltos = len(self.incidentes_resueltos)
        
        # Contar por tipo
        conteo_tipos = {}
        for incidente in self.incidentes:
            tipo = incidente.tipo.value
            conteo_tipos[tipo] = conteo_tipos.get(tipo, 0) + 1
        
        # Contar por gravedad
        conteo_gravedad = {}
        for incidente in self.incidentes:
            gravedad = incidente.gravedad
            conteo_gravedad[gravedad] = conteo_gravedad.get(gravedad, 0) + 1
        
        return {
            'activo': self.activo,
            'modo_automatico': self.modo_automatico,
            'total_incidentes': total_incidentes,
            'incidentes_resueltos': incidentes_resueltos,
            'incidentes_pendientes': len(self.cola_incidentes),
            'conteo_por_tipo': conteo_tipos,
            'conteo_por_gravedad': conteo_gravedad,
            'callbacks_registrados': len(self.callbacks_personalizados),
            'ultimo_incidente': self.incidentes[-1].timestamp_deteccion.isoformat() if self.incidentes else None
        }
    
    def generar_reporte_incidentes(self) -> str:
        """Genera un reporte detallado de incidentes en formato Markdown."""
        stats = self.obtener_estadisticas()
        
        md = "# ⚔️ Informe de los Guardianes de Némesis\n\n"
        md += f"**Estado de los Guardianes:** {'🟢 Vigilando' if self.activo else '🔴 Inactivos'}\n"
        md += f"**Modo de Operación:** {'🤖 Automático' if self.modo_automatico else '👤 Manual'}\n"
        md += f"**Total de Incidentes:** {stats['total_incidentes']}\n"
        md += f"**Incidentes Resueltos:** {stats['incidentes_resueltos']}\n"
        md += f"**Incidentes Pendientes:** {stats['incidentes_pendientes']}\n\n"
        
        # Incidentes por tipo
        if stats['conteo_por_tipo']:
            md += "## 📊 Incidentes por Tipo\n\n"
            md += "| Tipo | Cantidad |\n"
            md += "|------|----------|\n"
            for tipo, cantidad in sorted(stats['conteo_por_tipo'].items()):
                md += f"| {tipo} | {cantidad} |\n"
            md += "\n"
        
        # Incidentes por gravedad
        if stats['conteo_por_gravedad']:
            md += "## 🚨 Incidentes por Gravedad\n\n"
            md += "| Gravedad | Cantidad |\n"
            md += "|----------|----------|\n"
            for gravedad, cantidad in sorted(stats['conteo_por_gravedad'].items()):
                emoji = {"BAJO": "🟢", "MEDIO": "🟡", "ALTO": "🟠", "CRITICO": "🔴"}.get(gravedad, "⚪")
                md += f"| {emoji} {gravedad} | {cantidad} |\n"
            md += "\n"
        
        # Incidentes recientes
        incidentes_recientes = sorted(
            self.incidentes[-10:],
            key=lambda i: i.timestamp_deteccion,
            reverse=True
        ) if self.incidentes else []
        
        if incidentes_recientes:
            md += "## 🕒 Incidentes Recientes\n\n"
            md += "| ID | Tipo | Gravedad | Descripción | Estado |\n"
            md += "|----|------|----------|-------------|--------|\n"
            
            for incidente in incidentes_recientes:
                descripcion_corta = incidente.descripcion[:50] + "..." if len(incidente.descripcion) > 50 else incidente.descripcion
                emoji_estado = {"DETECTADO": "🟡", "EN_PROCESO": "🟠", "RESUELTO": "🟢"}.get(incidente.estado, "⚪")
                md += f"| {incidente.id} | {incidente.tipo.value} | {incidente.gravedad} | {descripcion_corta} | {emoji_estado} {incidente.estado} |\n"
            md += "\n"
        
        md += "---\n"
        md += "*Informe generado por los Guardianes de Némesis de Ares Aegis*\n"
        
        return md
