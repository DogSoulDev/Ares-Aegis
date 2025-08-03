#!/usr/bin/env python3
"""
Ares Aegis - Controlador Base
Clase base para todos los controladores del sistema

Creado por DogSoulDev
Versión: 4.0.0 - Arquitectura MVC Optimizada
"""

import abc
import asyncio
import threading
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from contextlib import asynccontextmanager

from ..utils.utils_ayuda_logging import configurar_logger_modulo


class ControladorBaseException(Exception):
    """Excepción base para todos los controladores"""
    pass


class ControladorNoInicializadoException(ControladorBaseException):
    """Excepción cuando se intenta usar un controlador no inicializado"""
    pass


class ControladorBase(abc.ABC):
    """
    Clase base abstracta para todos los controladores del sistema.
    
    Proporciona funcionalidad común como:
    - Gestión de estado
    - Logging consistente
    - Manejo de errores
    - Operaciones asíncronas
    - Métricas básicas
    """
    
    def __init__(self, nombre_controlador: str):
        """
        Inicializar controlador base.
        
        Args:
            nombre_controlador: Nombre único del controlador
        """
        self.nombre = nombre_controlador
        self.logger = configurar_logger_modulo(f"controlador_{nombre_controlador}")
        
        # Estado del controlador
        self._inicializado = False
        self._activo = False
        self._error_critico = False
        
        # Threading y sincronización
        self._lock = threading.RLock()
        self._ejecutores_activos = set()
        
        # Métricas básicas
        self._metricas = {
            'operaciones_exitosas': 0,
            'operaciones_fallidas': 0,
            'tiempo_ultima_operacion': None,
            'tiempo_inicializacion': None,
            'errores_consecutivos': 0
        }
        
        # Configuración de retry
        self._max_reintentos = 3
        self._tiempo_espera_reintento = 1.0
        
        self.logger.info(f"Controlador {self.nombre} creado")
    
    @property
    def inicializado(self) -> bool:
        """Verificar si el controlador está inicializado"""
        return self._inicializado
    
    @property
    def activo(self) -> bool:
        """Verificar si el controlador está activo"""
        return self._activo and self._inicializado
    
    @property
    def tiene_error_critico(self) -> bool:
        """Verificar si hay un error crítico"""
        return self._error_critico
    
    @property
    def metricas(self) -> Dict[str, Any]:
        """Obtener métricas del controlador"""
        with self._lock:
            return self._metricas.copy()
    
    def verificar_inicializado(self):
        """Verificar que el controlador esté inicializado"""
        if not self._inicializado:
            raise ControladorNoInicializadoException(
                f"Controlador {self.nombre} no está inicializado"
            )
    
    @abc.abstractmethod
    async def _inicializar_impl(self) -> bool:
        """
        Implementación específica de inicialización.
        
        Returns:
            True si la inicialización fue exitosa
        """
        pass
    
    @abc.abstractmethod
    async def _finalizar_impl(self) -> bool:
        """
        Implementación específica de finalización.
        
        Returns:
            True si la finalización fue exitosa
        """
        pass
    
    async def inicializar(self) -> bool:
        """
        Inicializar el controlador de forma segura.
        
        Returns:
            True si la inicialización fue exitosa
        """
        if self._inicializado:
            self.logger.warning(f"Controlador {self.nombre} ya está inicializado")
            return True
        
        try:
            self.logger.info(f"Inicializando controlador {self.nombre}...")
            
            inicio = datetime.now()
            resultado = await self._inicializar_impl()
            fin = datetime.now()
            
            if resultado:
                with self._lock:
                    self._inicializado = True
                    self._activo = True
                    self._error_critico = False
                    self._metricas['tiempo_inicializacion'] = fin
                    self._metricas['errores_consecutivos'] = 0
                
                tiempo_transcurrido = (fin - inicio).total_seconds()
                self.logger.info(
                    f"Controlador {self.nombre} inicializado exitosamente "
                    f"en {tiempo_transcurrido:.2f}s"
                )
            else:
                self.logger.error(f"Falló la inicialización del controlador {self.nombre}")
                
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error crítico inicializando {self.nombre}: {e}", exc_info=True)
            self._error_critico = True
            return False
    
    async def finalizar(self) -> bool:
        """
        Finalizar el controlador de forma segura.
        
        Returns:
            True si la finalización fue exitosa
        """
        if not self._inicializado:
            return True
        
        try:
            self.logger.info(f"Finalizando controlador {self.nombre}...")
            
            # Esperar a que terminen las operaciones activas
            while self._ejecutores_activos:
                await asyncio.sleep(0.1)
            
            resultado = await self._finalizar_impl()
            
            with self._lock:
                self._inicializado = False
                self._activo = False
            
            self.logger.info(f"Controlador {self.nombre} finalizado")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error finalizando {self.nombre}: {e}", exc_info=True)
            return False
    
    @asynccontextmanager
    async def operacion_segura(self, nombre_operacion: str):
        """
        Context manager para operaciones seguras con manejo de errores.
        
        Args:
            nombre_operacion: Nombre descriptivo de la operación
        """
        self.verificar_inicializado()
        
        operacion_id = f"{nombre_operacion}_{datetime.now().timestamp()}"
        
        try:
            self._ejecutores_activos.add(operacion_id)
            inicio = datetime.now()
            
            self.logger.debug(f"Iniciando operación: {nombre_operacion}")
            
            yield
            
            fin = datetime.now()
            tiempo_transcurrido = (fin - inicio).total_seconds()
            
            with self._lock:
                self._metricas['operaciones_exitosas'] += 1
                self._metricas['tiempo_ultima_operacion'] = fin
                self._metricas['errores_consecutivos'] = 0
            
            self.logger.debug(
                f"Operación {nombre_operacion} completada en {tiempo_transcurrido:.2f}s"
            )
            
        except Exception as e:
            with self._lock:
                self._metricas['operaciones_fallidas'] += 1
                self._metricas['errores_consecutivos'] += 1
            
            self.logger.error(f"Error en operación {nombre_operacion}: {e}", exc_info=True)
            
            # Marcar error crítico si hay muchos errores consecutivos
            if self._metricas['errores_consecutivos'] >= 5:
                self._error_critico = True
                self.logger.critical(
                    f"Controlador {self.nombre} marcado con error crítico "
                    f"después de {self._metricas['errores_consecutivos']} errores consecutivos"
                )
            
            raise
            
        finally:
            self._ejecutores_activos.discard(operacion_id)
    
    async def ejecutar_con_reintentos(
        self, 
        operacion: Callable,
        *args,
        max_reintentos: Optional[int] = None,
        tiempo_espera: Optional[float] = None,
        **kwargs
    ) -> Any:
        """
        Ejecutar operación con reintentos automáticos.
        
        Args:
            operacion: Función a ejecutar
            max_reintentos: Número máximo de reintentos
            tiempo_espera: Tiempo de espera entre reintentos
            *args, **kwargs: Argumentos para la operación
            
        Returns:
            Resultado de la operación
        """
        max_reintentos = max_reintentos or self._max_reintentos
        tiempo_espera = tiempo_espera or self._tiempo_espera_reintento
        
        ultimo_error = None
        
        for intento in range(max_reintentos + 1):
            try:
                if asyncio.iscoroutinefunction(operacion):
                    return await operacion(*args, **kwargs)
                else:
                    return operacion(*args, **kwargs)
                    
            except Exception as e:
                ultimo_error = e
                
                if intento < max_reintentos:
                    self.logger.warning(
                        f"Intento {intento + 1}/{max_reintentos + 1} falló: {e}. "
                        f"Reintentando en {tiempo_espera}s..."
                    )
                    await asyncio.sleep(tiempo_espera)
                    tiempo_espera *= 2  # Backoff exponencial
                else:
                    self.logger.error(f"Todos los reintentos fallaron. Último error: {e}")
        
        raise ultimo_error
    
    def obtener_estado(self) -> Dict[str, Any]:
        """
        Obtener estado completo del controlador.
        
        Returns:
            Diccionario con el estado del controlador
        """
        return {
            'nombre': self.nombre,
            'inicializado': self._inicializado,
            'activo': self._activo,
            'error_critico': self._error_critico,
            'ejecutores_activos': len(self._ejecutores_activos),
            'metricas': self.metricas
        }
    
    def resetear_metricas(self):
        """Resetear las métricas del controlador"""
        with self._lock:
            self._metricas.update({
                'operaciones_exitosas': 0,
                'operaciones_fallidas': 0,
                'tiempo_ultima_operacion': None,
                'errores_consecutivos': 0
            })
        
        self.logger.info(f"Métricas del controlador {self.nombre} reseteadas")
