#!/usr/bin/env python3
"""
Controlador de Respuesta Automatizada para Ares Aegis v3.0.0
Gestiona la orquestación y coordinación del sistema de respuesta automatizada.
"""

import json
import os
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass

from ..utilidades.ayuda_logging import configurar_logger_modulo
from ..utilidades.ayuda_rutas import crear_ruta_segura
from ..modelos.siem import SIEM
from ..modelos.respondedor_incidentes import RespondedorIncidentes, TipoIncidente


@dataclass
class EstadoRespuestaAutomatizada:
    """Estado del sistema de respuesta automatizada."""
    activo: bool = False
    reglas_activas: Optional[Dict[str, Any]] = None
    contadores_eventos: Optional[Dict[str, Any]] = None
    historial_acciones: Optional[List[Dict[str, Any]]] = None
    timestamp_activacion: Optional[str] = None
    
    def __post_init__(self):
        if self.reglas_activas is None:
            self.reglas_activas = {}
        if self.contadores_eventos is None:
            self.contadores_eventos = {}
        if self.historial_acciones is None:
            self.historial_acciones = []


class ControladorRespuestaAutomatizada:
    """
    Controlador para la gestión del sistema de respuesta automatizada.
    
    Responsabilidades:
    - Coordinar activación/desactivación del sistema
    - Gestionar estado y configuración
    - Orquestar respuestas a eventos
    - Mantener historial de acciones
    """
    
    def __init__(self, siem: Optional[SIEM] = None, respondedor: Optional[RespondedorIncidentes] = None):
        """Inicializa el controlador de respuesta automatizada."""
        self.logger = configurar_logger_modulo("controlador_respuesta_automatizada")
        
        # Dependencias
        self.siem = siem or SIEM()
        self.respondedor = respondedor or RespondedorIncidentes()
        
        # Estado del controlador
        self.estado = EstadoRespuestaAutomatizada()
        self._lock_estado = threading.Lock()
        
        # Configuración
        self.archivo_config = "recursos/reglas_respuesta.json"
        self.reglas_disponibles = {}
        
        # Monitor de eventos
        self._monitor_eventos: Optional[threading.Thread] = None
        self._detener_monitor = threading.Event()
        
        # Callbacks registrados
        self._callbacks_eventos: Dict[str, List[Callable]] = {}
        
        self.logger.info("ControladorRespuestaAutomatizada inicializado")
        
        # Registrar en SIEM
        from ..modelos.siem import TipoEvento
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Controlador de respuesta automatizada inicializado",
            {"controlador": "respuesta_automatizada"},
            "MEDIO"
        )
    
    def activar_sistema(self, configuracion_reglas: Dict[str, Any], 
                       callback_progreso: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Activa el sistema de respuesta automatizada.
        
        Args:
            configuracion_reglas: Configuración de reglas a activar
            callback_progreso: Función de callback para progreso
            
        Returns:
            Dict con resultado de la activación
        """
        try:
            with self._lock_estado:
                if self.estado.activo:
                    return {
                        'exitoso': False,
                        'mensaje': 'El sistema ya está activo'
                    }
                
                if callback_progreso:
                    callback_progreso("Validando configuración de reglas...")
                
                # Validar configuración
                if not self._validar_configuracion(configuracion_reglas):
                    return {
                        'exitoso': False,
                        'mensaje': 'Configuración de reglas inválida'
                    }
                
                if callback_progreso:
                    callback_progreso("Aplicando configuración...")
                
                # Aplicar configuración
                self.estado.reglas_activas = configuracion_reglas.copy()
                self.estado.timestamp_activacion = datetime.now().isoformat()
                
                if callback_progreso:
                    callback_progreso("Guardando configuración...")
                
                # Guardar configuración
                self._guardar_configuracion()
                
                if callback_progreso:
                    callback_progreso("Iniciando monitor de eventos...")
                
                # Iniciar monitor de eventos
                self._iniciar_monitor_eventos()
                
                if callback_progreso:
                    callback_progreso("Registrando callbacks de incidentes...")
                
                # Registrar callbacks en el respondedor de incidentes
                self._registrar_callbacks_incidentes()
                
                self.estado.activo = True
                
                if callback_progreso:
                    callback_progreso("Sistema activado exitosamente")
            
            mensaje = f"Sistema de respuesta automatizada activado con {len(configuracion_reglas)} reglas"
            self.logger.info(mensaje)
            
            # Registrar en SIEM
            from ..modelos.siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_INICIADO,
                "Sistema de respuesta automatizada activado",
                {
                    "reglas_activas": len(configuracion_reglas),
                    "timestamp": self.estado.timestamp_activacion
                },
                "ALTO"
            )
            
            return {
                'exitoso': True,
                'mensaje': mensaje,
                'reglas_activas': len(configuracion_reglas),
                'timestamp_activacion': self.estado.timestamp_activacion
            }
            
        except Exception as e:
            mensaje = f"Error activando sistema de respuesta automatizada: {e}"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'mensaje': mensaje
            }
    
    def desactivar_sistema(self, callback_progreso: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Desactiva el sistema de respuesta automatizada.
        
        Args:
            callback_progreso: Función de callback para progreso
            
        Returns:
            Dict con resultado de la desactivación
        """
        try:
            with self._lock_estado:
                if not self.estado.activo:
                    return {
                        'exitoso': False,
                        'mensaje': 'El sistema ya está inactivo'
                    }
                
                if callback_progreso:
                    callback_progreso("Deteniendo monitor de eventos...")
                
                # Detener monitor de eventos
                self._detener_monitor_eventos()
                
                if callback_progreso:
                    callback_progreso("Desregistrando callbacks...")
                
                # Limpiar callbacks
                self._desregistrar_callbacks_incidentes()
                
                if callback_progreso:
                    callback_progreso("Guardando estado final...")
                
                # Guardar estado final
                self._guardar_configuracion()
                
                acciones_realizadas = len(self.estado.historial_acciones or [])
                self.estado.activo = False
                
                if callback_progreso:
                    callback_progreso("Sistema desactivado exitosamente")
            
            mensaje = f"Sistema desactivado. Se realizaron {acciones_realizadas} acciones"
            self.logger.info(mensaje)
            
            # Registrar en SIEM
            from ..modelos.siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_DETENIDO,
                "Sistema de respuesta automatizada desactivado",
                {
                    "acciones_realizadas": acciones_realizadas,
                    "duracion_activo": self._calcular_duracion_activo()
                },
                "MEDIO"
            )
            
            return {
                'exitoso': True,
                'mensaje': mensaje,
                'acciones_realizadas': acciones_realizadas
            }
            
        except Exception as e:
            mensaje = f"Error desactivando sistema: {e}"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'mensaje': mensaje
            }
    
    def manejar_evento(self, tipo_evento: str, datos_evento: Dict[str, Any]) -> bool:
        """
        Maneja un evento del sistema y ejecuta respuestas correspondientes.
        
        Args:
            tipo_evento: Tipo del evento
            datos_evento: Datos del evento
            
        Returns:
            True si se procesó el evento
        """
        if not self.estado.activo:
            return False
        
        try:
            self.logger.info(f"Procesando evento: {tipo_evento}")
            
            # Ejecutar callbacks registrados
            callbacks = self._callbacks_eventos.get(tipo_evento, [])
            for callback in callbacks:
                try:
                    callback(datos_evento)
                except Exception as e:
                    self.logger.error(f"Error ejecutando callback para {tipo_evento}: {e}")
            
            # Buscar reglas que respondan a este evento
            reglas_aplicables = self._buscar_reglas_aplicables(tipo_evento, datos_evento)
            
            for regla in reglas_aplicables:
                if self._evaluar_condicion_regla(regla, datos_evento):
                    self._ejecutar_accion_regla(regla, datos_evento)
            
            # Registrar en historial
            self._registrar_accion_historial(tipo_evento, datos_evento, len(reglas_aplicables))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error manejando evento {tipo_evento}: {e}")
            return False
    
    def registrar_callback_evento(self, tipo_evento: str, callback: Callable):
        """
        Registra un callback para un tipo de evento específico.
        
        Args:
            tipo_evento: Tipo de evento
            callback: Función callback
        """
        if tipo_evento not in self._callbacks_eventos:
            self._callbacks_eventos[tipo_evento] = []
        
        self._callbacks_eventos[tipo_evento].append(callback)
        self.logger.info(f"Callback registrado para evento: {tipo_evento}")
    
    def obtener_estado(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del sistema.
        
        Returns:
            Dict con el estado del sistema
        """
        with self._lock_estado:
            return {
                'activo': self.estado.activo,
                'reglas_activas': len(self.estado.reglas_activas or {}),
                'eventos_procesados': len(self.estado.contadores_eventos or {}),
                'acciones_realizadas': len(self.estado.historial_acciones or []),
                'timestamp_activacion': self.estado.timestamp_activacion,
                'duracion_activo': self._calcular_duracion_activo() if self.estado.activo else None
            }
    
    def obtener_historial_acciones(self, limite: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de acciones realizadas.
        
        Args:
            limite: Número máximo de acciones a retornar
            
        Returns:
            Lista de acciones
        """
        with self._lock_estado:
            historial = self.estado.historial_acciones or []
            return historial[-limite:]
    
    def obtener_estadisticas_eventos(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de eventos procesados.
        
        Returns:
            Dict con estadísticas
        """
        with self._lock_estado:
            contadores = self.estado.contadores_eventos or {}
            return {
                'contadores_eventos': contadores.copy(),
                'tipos_eventos_unicos': len(set(
                    evento.split('_')[0] for evento in contadores.keys()
                )),
                'total_eventos': sum(
                    contador.get('count', 0) for contador in contadores.values()
                )
            }
    
    # Métodos privados de implementación
    
    def _validar_configuracion(self, configuracion: Dict[str, Any]) -> bool:
        """Valida la configuración de reglas."""
        try:
            # Validaciones básicas
            if not isinstance(configuracion, dict):
                return False
            
            # TODO: Implementar validaciones específicas según reglas disponibles
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando configuración: {e}")
            return False
    
    def _guardar_configuracion(self):
        """Guarda la configuración actual."""
        try:
            crear_ruta_segura(self.archivo_config)
            
            config = {
                'reglas_activas': self.estado.reglas_activas,
                'timestamp_activacion': self.estado.timestamp_activacion,
                'ultima_actualizacion': datetime.now().isoformat()
            }
            
            with open(self.archivo_config, 'w', encoding='utf-8') as archivo:
                json.dump(config, archivo, ensure_ascii=False, indent=2)
                
            self.logger.info("Configuración guardada exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error guardando configuración: {e}")
    
    def _cargar_configuracion(self):
        """Carga la configuración desde archivo."""
        try:
            if os.path.exists(self.archivo_config):
                with open(self.archivo_config, 'r', encoding='utf-8') as archivo:
                    config = json.load(archivo)
                    self.estado.reglas_activas = config.get('reglas_activas', {})
                    self.estado.timestamp_activacion = config.get('timestamp_activacion')
                    self.logger.info("Configuración cargada exitosamente")
        except Exception as e:
            self.logger.warning(f"Error cargando configuración: {e}")
    
    def _iniciar_monitor_eventos(self):
        """Inicia el monitor de eventos."""
        self._detener_monitor.clear()
        self._monitor_eventos = threading.Thread(
            target=self._loop_monitor_eventos,
            daemon=True,
            name="MonitorEventosRespuesta"
        )
        self._monitor_eventos.start()
        self.logger.info("Monitor de eventos iniciado")
    
    def _detener_monitor_eventos(self):
        """Detiene el monitor de eventos."""
        if self._monitor_eventos and self._monitor_eventos.is_alive():
            self._detener_monitor.set()
            self._monitor_eventos.join(timeout=10)
            self.logger.info("Monitor de eventos detenido")
    
    def _loop_monitor_eventos(self):
        """Loop principal del monitor de eventos."""
        while not self._detener_monitor.wait(1.0):
            try:
                # TODO: Implementar lógica de monitoreo específica
                pass
            except Exception as e:
                self.logger.error(f"Error en loop monitor eventos: {e}")
    
    def _registrar_callbacks_incidentes(self):
        """Registra callbacks en el respondedor de incidentes."""
        try:
            # Registrar callback para cada tipo de incidente
            for tipo_incidente in TipoIncidente:
                self.respondedor.registrar_callback_personalizado(
                    tipo_incidente,
                    lambda incidente, tipo=tipo_incidente: self._callback_incidente(incidente, tipo)
                )
            self.logger.info("Callbacks de incidentes registrados")
        except Exception as e:
            self.logger.error(f"Error registrando callbacks: {e}")
    
    def _desregistrar_callbacks_incidentes(self):
        """Desregistra callbacks del respondedor de incidentes."""
        try:
            # TODO: Implementar desregistro de callbacks si está disponible
            self.logger.info("Callbacks de incidentes desregistrados")
        except Exception as e:
            self.logger.error(f"Error desregistrando callbacks: {e}")
    
    def _callback_incidente(self, incidente, tipo_incidente: TipoIncidente):
        """Callback ejecutado cuando se procesa un incidente."""
        try:
            datos_evento = {
                'incidente_id': incidente.id,
                'tipo': tipo_incidente.value,
                'severidad': incidente.severidad,
                'timestamp': incidente.timestamp.isoformat()
            }
            
            self.manejar_evento(f"incidente_{tipo_incidente.value.lower()}", datos_evento)
            
        except Exception as e:
            self.logger.error(f"Error en callback de incidente: {e}")
    
    def _buscar_reglas_aplicables(self, tipo_evento: str, datos_evento: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Busca reglas aplicables para un evento."""
        reglas_aplicables = []
        
        try:
            reglas_activas = self.estado.reglas_activas or {}
            for categoria, config_categoria in reglas_activas.items():
                for nombre_regla, config_regla in config_categoria.get('reglas', {}).items():
                    # TODO: Implementar lógica específica de búsqueda de reglas
                    # basada en las reglas disponibles del sistema
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error buscando reglas aplicables: {e}")
        
        return reglas_aplicables
    
    def _evaluar_condicion_regla(self, regla: Dict[str, Any], datos_evento: Dict[str, Any]) -> bool:
        """Evalúa si una regla se aplica a un evento."""
        try:
            # TODO: Implementar evaluación de condiciones específicas
            return True
        except Exception as e:
            self.logger.error(f"Error evaluando condición de regla: {e}")
            return False
    
    def _ejecutar_accion_regla(self, regla: Dict[str, Any], datos_evento: Dict[str, Any]):
        """Ejecuta la acción de una regla."""
        try:
            # TODO: Implementar ejecución de acciones específicas
            self.logger.info(f"Ejecutando acción de regla: {regla.get('nombre', 'unknown')}")
        except Exception as e:
            self.logger.error(f"Error ejecutando acción de regla: {e}")
    
    def _registrar_accion_historial(self, tipo_evento: str, datos_evento: Dict[str, Any], reglas_ejecutadas: int):
        """Registra una acción en el historial."""
        try:
            with self._lock_estado:
                if self.estado.historial_acciones is None:
                    self.estado.historial_acciones = []
                
                accion = {
                    'timestamp': datetime.now().isoformat(),
                    'tipo_evento': tipo_evento,
                    'reglas_ejecutadas': reglas_ejecutadas,
                    'datos_evento': datos_evento
                }
                
                self.estado.historial_acciones.append(accion)
                
                # Limitar tamaño del historial
                if len(self.estado.historial_acciones) > 10000:
                    self.estado.historial_acciones = self.estado.historial_acciones[-5000:]
                    
        except Exception as e:
            self.logger.error(f"Error registrando acción en historial: {e}")
    
    def _calcular_duracion_activo(self) -> Optional[str]:
        """Calcula la duración que el sistema ha estado activo."""
        if not self.estado.timestamp_activacion:
            return None
        
        try:
            inicio = datetime.fromisoformat(self.estado.timestamp_activacion)
            duracion = datetime.now() - inicio
            return str(duracion)
        except Exception:
            return None
