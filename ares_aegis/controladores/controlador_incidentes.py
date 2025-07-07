#!/usr/bin/env python3
"""
Controlador de Incidentes para Ares Aegis v3.0.0
Gestiona la coordinación y orquestación del sistema de respuesta a incidentes.
"""

import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field

from ..utilidades.ayuda_logging import configurar_logger_modulo
from ..modelos.siem import SIEM
from ..modelos.respondedor_incidentes import RespondedorIncidentes, TipoIncidente, Incidente


@dataclass
class EstadoControladorIncidentes:
    """Estado del controlador de incidentes."""
    procesando: bool = False
    callbacks_registrados: Dict[TipoIncidente, List[Callable]] = field(default_factory=dict)
    estadisticas: Dict[str, Any] = field(default_factory=dict)
    timestamp_inicio: Optional[str] = None


class ControladorIncidentes:
    """
    Controlador para la gestión y coordinación del sistema de respuesta a incidentes.
    
    Responsabilidades:
    - Coordinar el procesamiento de incidentes
    - Gestionar callbacks y notificaciones
    - Mantener estadísticas de procesamiento
    - Controlar hilos de procesamiento
    """
    
    def __init__(self, siem: Optional[SIEM] = None, respondedor: Optional[RespondedorIncidentes] = None):
        """Inicializa el controlador de incidentes."""
        self.logger = configurar_logger_modulo("controlador_incidentes")
        
        # Dependencias
        self.siem = siem or SIEM()
        self.respondedor = respondedor or RespondedorIncidentes()
        
        # Estado del controlador
        self.estado = EstadoControladorIncidentes()
        self._lock_estado = threading.Lock()
        
        # Control de hilos
        self._hilo_procesamiento: Optional[threading.Thread] = None
        self._detener_procesamiento = threading.Event()
        
        # Callbacks del controlador
        self._callbacks_controlador: Dict[str, List[Callable]] = {}
        
        self.logger.info("ControladorIncidentes inicializado")
        
        # Registrar en SIEM
        from ..modelos.siem import TipoEvento
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Controlador de incidentes inicializado",
            {"controlador": "incidentes"},
            "MEDIO"
        )
    
    def iniciar_procesamiento(self, callback_progreso: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Inicia el procesamiento coordinado de incidentes.
        
        Args:
            callback_progreso: Función de callback para progreso
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            with self._lock_estado:
                if self.estado.procesando:
                    return {
                        'exitoso': False,
                        'mensaje': 'El procesamiento ya está activo'
                    }
                
                if callback_progreso:
                    callback_progreso("Iniciando procesamiento de incidentes...")
                
                # Registrar callbacks en el respondedor
                self._registrar_callbacks_respondedor()
                
                # Iniciar hilo de procesamiento coordinado
                self._iniciar_hilo_procesamiento()
                
                # Actualizar estado
                self.estado.procesando = True
                self.estado.timestamp_inicio = datetime.now().isoformat()
                self.estado.estadisticas = {
                    'incidentes_procesados': 0,
                    'callbacks_ejecutados': 0,
                    'errores': 0,
                    'inicio': self.estado.timestamp_inicio
                }
                
                if callback_progreso:
                    callback_progreso("Procesamiento iniciado exitosamente")
            
            mensaje = "Sistema de procesamiento de incidentes iniciado"
            self.logger.info(mensaje)
            
            # Registrar en SIEM
            from ..modelos.siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_INICIADO,
                "Procesamiento de incidentes iniciado",
                {"timestamp_inicio": self.estado.timestamp_inicio},
                "ALTO"
            )
            
            return {
                'exitoso': True,
                'mensaje': mensaje,
                'timestamp_inicio': self.estado.timestamp_inicio
            }
            
        except Exception as e:
            mensaje = f"Error iniciando procesamiento de incidentes: {e}"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'mensaje': mensaje
            }
    
    def detener_procesamiento(self, callback_progreso: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Detiene el procesamiento coordinado de incidentes.
        
        Args:
            callback_progreso: Función de callback para progreso
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            with self._lock_estado:
                if not self.estado.procesando:
                    return {
                        'exitoso': False,
                        'mensaje': 'El procesamiento ya está inactivo'
                    }
                
                if callback_progreso:
                    callback_progreso("Deteniendo procesamiento de incidentes...")
                
                # Detener hilo de procesamiento
                self._detener_hilo_procesamiento()
                
                # Desregistrar callbacks
                self._desregistrar_callbacks_respondedor()
                
                estadisticas_finales = self.estado.estadisticas.copy()
                self.estado.procesando = False
                
                if callback_progreso:
                    callback_progreso("Procesamiento detenido exitosamente")
            
            mensaje = f"Procesamiento detenido. Estadísticas: {estadisticas_finales}"
            self.logger.info(mensaje)
            
            # Registrar en SIEM
            from ..modelos.siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_DETENIDO,
                "Procesamiento de incidentes detenido",
                estadisticas_finales,
                "MEDIO"
            )
            
            return {
                'exitoso': True,
                'mensaje': mensaje,
                'estadisticas': estadisticas_finales
            }
            
        except Exception as e:
            mensaje = f"Error deteniendo procesamiento: {e}"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'mensaje': mensaje
            }
    
    def registrar_callback_incidente(self, tipo_incidente: TipoIncidente, callback: Callable):
        """
        Registra un callback para un tipo de incidente específico.
        
        Args:
            tipo_incidente: Tipo de incidente
            callback: Función callback
        """
        with self._lock_estado:
            if tipo_incidente not in self.estado.callbacks_registrados:
                self.estado.callbacks_registrados[tipo_incidente] = []
            
            self.estado.callbacks_registrados[tipo_incidente].append(callback)
            
            # También registrar en el respondedor si está procesando
            if self.estado.procesando:
                self.respondedor.registrar_callback_personalizado(tipo_incidente, callback)
        
        self.logger.info(f"Callback registrado para incidente: {tipo_incidente.value}")
    
    def registrar_callback_evento(self, evento: str, callback: Callable):
        """
        Registra un callback para eventos del controlador.
        
        Args:
            evento: Nombre del evento
            callback: Función callback
        """
        if evento not in self._callbacks_controlador:
            self._callbacks_controlador[evento] = []
        
        self._callbacks_controlador[evento].append(callback)
        self.logger.info(f"Callback registrado para evento: {evento}")
    
    def procesar_incidente_coordinado(self, incidente: Incidente) -> Dict[str, Any]:
        """
        Procesa un incidente con coordinación adicional del controlador.
        
        Args:
            incidente: Incidente a procesar
            
        Returns:
            Dict con resultado del procesamiento
        """
        try:
            # Ejecutar callbacks del controlador
            self._ejecutar_callbacks_evento('incidente_recibido', incidente)
            
            # Delegar al respondedor
            self.respondedor._procesar_incidente_individual(incidente)
            
            resultado = {
                'exitoso': True,
                'mensaje': 'Incidente procesado exitosamente',
                'incidente_id': incidente.id
            }
            
            # Actualizar estadísticas
            with self._lock_estado:
                if 'incidentes_procesados' in self.estado.estadisticas:
                    self.estado.estadisticas['incidentes_procesados'] += 1
            
            # Ejecutar callbacks de finalización
            self._ejecutar_callbacks_evento('incidente_procesado', {
                'incidente': incidente,
                'resultado': resultado
            })
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error procesando incidente coordinado: {e}")
            with self._lock_estado:
                if 'errores' in self.estado.estadisticas:
                    self.estado.estadisticas['errores'] += 1
            
            return {
                'exitoso': False,
                'mensaje': f'Error en procesamiento coordinado: {e}'
            }
    
    def obtener_estado(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del controlador.
        
        Returns:
            Dict con el estado del controlador
        """
        with self._lock_estado:
            return {
                'procesando': self.estado.procesando,
                'callbacks_registrados': {
                    tipo.value: len(callbacks) 
                    for tipo, callbacks in self.estado.callbacks_registrados.items()
                },
                'estadisticas': self.estado.estadisticas.copy(),
                'timestamp_inicio': self.estado.timestamp_inicio,
                'duracion_activo': self._calcular_duracion_activo() if self.estado.procesando else None
            }
    
    def obtener_estadisticas_detalladas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas detalladas del procesamiento.
        
        Returns:
            Dict con estadísticas detalladas
        """
        with self._lock_estado:
            estado_respondedor = self.respondedor.obtener_estadisticas()
            
            return {
                'controlador': self.estado.estadisticas.copy(),
                'respondedor': estado_respondedor,
                'callbacks_totales': sum(
                    len(callbacks) for callbacks in self.estado.callbacks_registrados.values()
                ),
                'tipos_incidentes_monitoreados': len(self.estado.callbacks_registrados)
            }
    
    # Métodos privados de implementación
    
    def _registrar_callbacks_respondedor(self):
        """Registra todos los callbacks en el respondedor."""
        try:
            for tipo_incidente, callbacks in self.estado.callbacks_registrados.items():
                for callback in callbacks:
                    self.respondedor.registrar_callback_personalizado(tipo_incidente, callback)
            
            self.logger.info("Callbacks registrados en respondedor")
        except Exception as e:
            self.logger.error(f"Error registrando callbacks: {e}")
    
    def _desregistrar_callbacks_respondedor(self):
        """Desregistra callbacks del respondedor."""
        try:
            # TODO: Implementar desregistro si el respondedor lo soporta
            self.logger.info("Callbacks desregistrados del respondedor")
        except Exception as e:
            self.logger.error(f"Error desregistrando callbacks: {e}")
    
    def _iniciar_hilo_procesamiento(self):
        """Inicia el hilo de procesamiento coordinado."""
        self._detener_procesamiento.clear()
        self._hilo_procesamiento = threading.Thread(
            target=self._loop_procesamiento_coordinado,
            daemon=True,
            name="ProcesadorIncidentes"
        )
        self._hilo_procesamiento.start()
        self.logger.info("Hilo de procesamiento coordinado iniciado")
    
    def _detener_hilo_procesamiento(self):
        """Detiene el hilo de procesamiento coordinado."""
        if self._hilo_procesamiento and self._hilo_procesamiento.is_alive():
            self._detener_procesamiento.set()
            self._hilo_procesamiento.join(timeout=15)
            self.logger.info("Hilo de procesamiento coordinado detenido")
    
    def _loop_procesamiento_coordinado(self):
        """Loop principal del procesamiento coordinado."""
        self.logger.info("Iniciando loop de procesamiento coordinado")
        
        while not self._detener_procesamiento.wait(1.0):
            try:
                # Monitorear estado del respondedor
                self._monitorear_estado_respondedor()
                
                # Ejecutar mantenimiento de estadísticas
                self._actualizar_estadisticas()
                
                # Ejecutar callbacks periódicos
                self._ejecutar_callbacks_evento('tick_procesamiento', {
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"Error en loop de procesamiento coordinado: {e}")
                time.sleep(5)  # Pausa en caso de error
        
        self.logger.info("Loop de procesamiento coordinado finalizado")
    
    def _monitorear_estado_respondedor(self):
        """Monitorea el estado del respondedor."""
        try:
            estado_respondedor = self.respondedor.obtener_estadisticas()
            
            # Verificar si hay alertas o problemas
            if estado_respondedor.get('cola_incidentes', 0) > 100:
                self._ejecutar_callbacks_evento('cola_saturada', {
                    'tamaño_cola': estado_respondedor['cola_incidentes']
                })
            
        except Exception as e:
            self.logger.debug(f"Error monitoreando respondedor: {e}")
    
    def _actualizar_estadisticas(self):
        """Actualiza las estadísticas del controlador."""
        try:
            with self._lock_estado:
                if 'callbacks_ejecutados' in self.estado.estadisticas:
                    # Contar callbacks ejecutados en el respondedor
                    # TODO: Obtener estas métricas del respondedor
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Error actualizando estadísticas: {e}")
    
    def _ejecutar_callbacks_evento(self, evento: str, datos: Any):
        """Ejecuta callbacks para un evento específico."""
        callbacks = self._callbacks_controlador.get(evento, [])
        
        for callback in callbacks:
            try:
                callback(datos)
                with self._lock_estado:
                    if 'callbacks_ejecutados' in self.estado.estadisticas:
                        self.estado.estadisticas['callbacks_ejecutados'] += 1
            except Exception as e:
                self.logger.error(f"Error ejecutando callback para {evento}: {e}")
                with self._lock_estado:
                    if 'errores' in self.estado.estadisticas:
                        self.estado.estadisticas['errores'] += 1
    
    def _calcular_duracion_activo(self) -> Optional[str]:
        """Calcula la duración que el controlador ha estado activo."""
        if not self.estado.timestamp_inicio:
            return None
        
        try:
            inicio = datetime.fromisoformat(self.estado.timestamp_inicio)
            duracion = datetime.now() - inicio
            return str(duracion)
        except Exception:
            return None
