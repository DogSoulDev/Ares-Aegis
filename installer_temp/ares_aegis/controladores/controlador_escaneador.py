#!/usr/bin/env python3
"""
Ares Aegis - Controlador de Escaneador Optimizado
Controlador especializado para gestionar todas las operaciones de escaneo

Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.
La copia, distribución o modificación no autorizada está estrictamente prohibida.

Versión: 4.0.0 - Arquitectura Optimizada
"""

import asyncio
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..modelos.escaneador import EscaneadorMalware
from ..modelos.siem import SIEM, TipoEvento
from ..utils.ayuda_logging import configurar_logger_modulo
from .controlador_base import ControladorBase
from .gestor_configuracion import gestor_configuracion


class ControladorEscaneador(ControladorBase):
    """Controlador especializado para operaciones de escaneo con arquitectura optimizada."""
    
    def __init__(self, escaneador: EscaneadorMalware, siem: SIEM):
        """
        Inicializar el controlador de escaneador.
        
        Args:
            escaneador: Instancia del escaneador de malware
            siem: Instancia del SIEM para registro de eventos
        """
        super().__init__("escaneador")
        
        self.escaneador = escaneador
        self.siem = siem
        self.configuracion = gestor_configuracion.obtener_config_controlador("escaneador")
        
        # Estado del controlador
        self.escaneo_activo = False
        self.ultimo_escaneo = None
        self.escaneos_programados = []
        self.pool_threads = None
        
        # Cache de resultados para optimización
        self._cache_escaneos = {}
        self._cache_timeout = 3600  # 1 hora
        
        self.logger.info("Controlador de Escaneador inicializado con nueva arquitectura")
    
    async def _inicializar_impl(self) -> bool:
        """Implementación de inicialización del controlador de escaneador"""
        try:
            # Inicializar pool de threads para operaciones intensivas
            max_threads = self.configuracion.threads_escaneo if self.configuracion else 4
            self.pool_threads = ThreadPoolExecutor(
                max_workers=max_threads,
                thread_name_prefix="AresEscaneador"
            )
            
            self.logger.info(f"Pool de threads inicializado con {max_threads} workers")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando controlador de escaneador: {e}")
            return False
    
    async def _finalizar_impl(self) -> bool:
        """Implementación de finalización del controlador de escaneador"""
        try:
            if self.pool_threads:
                self.pool_threads.shutdown(wait=True)
                self.logger.info("Pool de threads finalizado")
            return True
        except Exception as e:
            self.logger.error(f"Error finalizando controlador de escaneador: {e}")
            return False
    
    def iniciar_escaneo(self, ruta: str, tipo_escaneo: str = "rapido", callback_progreso: Optional[Callable] = None) -> bool:
        """
        Método unificado para iniciar escaneos desde la interfaz.
        
        Args:
            ruta: Directorio a escanear
            tipo_escaneo: Tipo de escaneo ('rapido', 'completo', 'directorio')
            callback_progreso: Función callback para reportar progreso
            
        Returns:
            bool: True si el escaneo se inició correctamente
        """
        try:
            if self.escaneo_activo:
                self.logger.warning("Ya hay un escaneo en progreso")
                return False
            
            self.logger.info(f"Iniciando escaneo {tipo_escaneo} en: {ruta}")
            
            if tipo_escaneo == "rapido":
                # Ejecutar escaneo rápido en un thread
                def ejecutar_rapido():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        resultado = loop.run_until_complete(self.ejecutar_escaneo_rapido(callback_progreso))
                        self.ultimo_escaneo = resultado
                    except Exception as e:
                        self.logger.error(f"Error en escaneo rápido: {e}")
                    finally:
                        loop.close()
                
                thread = threading.Thread(target=ejecutar_rapido, daemon=True)
                thread.start()
                
            elif tipo_escaneo == "completo":
                # Ejecutar escaneo completo en un thread
                def ejecutar_completo():
                    try:
                        resultado = self.ejecutar_escaneo_completo(callback_progreso)
                        self.ultimo_escaneo = resultado
                    except Exception as e:
                        self.logger.error(f"Error en escaneo completo: {e}")
                
                thread = threading.Thread(target=ejecutar_completo, daemon=True)
                thread.start()
                
            else:  # directorio por defecto
                # Ejecutar escaneo de directorio en un thread
                def ejecutar_directorio():
                    try:
                        resultado = self.ejecutar_escaneo_directorio(ruta, callback_progreso)
                        self.ultimo_escaneo = resultado
                    except Exception as e:
                        self.logger.error(f"Error en escaneo de directorio: {e}")
                
                thread = threading.Thread(target=ejecutar_directorio, daemon=True)
                thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error iniciando escaneo: {e}")
            return False
    
    async def ejecutar_escaneo_rapido(self, callback_progreso: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Ejecutar un escaneo rápido del sistema.
        
        Args:
            callback_progreso: Función callback para reportar progreso
            
        Returns:
            Dict[str, Any]: Resultados del escaneo
        """
        with self.lock:
            if self.escaneo_activo:
                raise RuntimeError("Ya hay un escaneo en progreso")
            
            self.escaneo_activo = True
        
        try:
            self.logger.info("Iniciando escaneo rápido")
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ESCANEO_INICIADO,
                    "Escaneo rápido iniciado desde controlador",
                    {'tipo': 'rapido'},
                    "MEDIO"
                )
            
            # Rutas para escaneo rápido
            rutas_rapidas = [
                str(Path.home() / "Downloads"),
                str(Path.home() / "Desktop"), 
                "/tmp",
                str(Path.home() / "Documents")
            ]
            
            # Filtrar rutas que existen
            rutas_existentes = [ruta for ruta in rutas_rapidas if Path(ruta).exists()]
            
            inicio_tiempo = time.time()
            archivos_escaneados = 0
            amenazas_detectadas = 0
            archivos_infectados = []
            
            # Procesar cada ruta
            for ruta in rutas_existentes:
                try:
                    if callback_progreso:
                        callback_progreso(f"Escaneando: {ruta}", archivos_escaneados, amenazas_detectadas)
                    
                    path_obj = Path(ruta)
                    if path_obj.is_file():
                        resultado = self.escaneador.escanear_archivo(str(path_obj))
                        archivos_escaneados += 1
                        if resultado and resultado.tiene_amenazas():
                            amenazas_detectadas += 1
                            archivos_infectados.append(str(path_obj))
                    
                    elif path_obj.is_dir():
                        # Escanear archivos específicos para escaneo rápido
                        extensiones = ['.exe', '.bat', '.cmd', '.scr', '.com', '.pif', '.vbs', '.js', '.jar']
                        for ext in extensiones:
                            for archivo in path_obj.rglob(f'*{ext}'):
                                if archivo.is_file():
                                    try:
                                        resultado = self.escaneador.escanear_archivo(str(archivo))
                                        archivos_escaneados += 1
                                        if resultado and resultado.tiene_amenazas():
                                            amenazas_detectadas += 1
                                            archivos_infectados.append(str(archivo))
                                        
                                        if callback_progreso and archivos_escaneados % 10 == 0:
                                            callback_progreso(f"Archivo: {archivo.name}", archivos_escaneados, amenazas_detectadas)
                                    
                                    except Exception as e:
                                        self.logger.warning(f"Error escaneando {archivo}: {e}")
                
                except Exception as e:
                    self.logger.warning(f"Error accediendo a {ruta}: {e}")
            
            tiempo_total = time.time() - inicio_tiempo
            
            # Crear resultado
            resultado = {
                'tipo_escaneo': 'rapido',
                'archivos_escaneados': archivos_escaneados,
                'amenazas_detectadas': amenazas_detectadas,
                'archivos_infectados': len(archivos_infectados),
                'tiempo_escaneo': tiempo_total,
                'rutas_escaneadas': rutas_existentes,
                'archivos_infectados_lista': archivos_infectados,
                'timestamp': datetime.now().isoformat()
            }
            
            # Guardar como último escaneo
            self.ultimo_escaneo = resultado
            
            # Registrar finalización
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ESCANEO_FINALIZADO,
                    f"Escaneo rápido completado: {amenazas_detectadas} amenazas en {archivos_escaneados} archivos",
                    resultado,
                    "ALTO" if amenazas_detectadas > 0 else "BAJO"
                )
            
            if callback_progreso:
                callback_progreso("Escaneo completado", archivos_escaneados, amenazas_detectadas)
            
            self.logger.info(f"Escaneo rápido completado: {archivos_escaneados} archivos, {amenazas_detectadas} amenazas en {tiempo_total:.2f}s")
            return resultado
        
        finally:
            with self.lock:
                self.escaneo_activo = False
    
    def ejecutar_escaneo_completo(self, callback_progreso: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Ejecutar un escaneo completo del sistema.
        
        Args:
            callback_progreso: Función callback para reportar progreso
            
        Returns:
            Dict[str, Any]: Resultados del escaneo
        """
        with self.lock:
            if self.escaneo_activo:
                raise RuntimeError("Ya hay un escaneo en progreso")
            
            self.escaneo_activo = True
        
        try:
            self.logger.info("Iniciando escaneo completo")
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ESCANEO_INICIADO,
                    "Escaneo completo iniciado desde controlador",
                    {'tipo': 'completo'},
                    "MEDIO"
                )
            
            # Rutas para escaneo completo
            rutas_completas = [
                str(Path.home()),
                "/opt",
                "/usr/local",
                "/var/www",
                "/etc"
            ]
            
            # Filtrar rutas que existen
            rutas_existentes = [ruta for ruta in rutas_completas if Path(ruta).exists()]
            
            inicio_tiempo = time.time()
            archivos_escaneados = 0
            amenazas_detectadas = 0
            archivos_infectados = []
            
            # Procesar cada ruta
            for ruta in rutas_existentes:
                try:
                    if callback_progreso:
                        callback_progreso(f"Escaneando: {ruta}", archivos_escaneados, amenazas_detectadas)
                    
                    path_obj = Path(ruta)
                    if path_obj.is_file():
                        resultado = self.escaneador.escanear_archivo(str(path_obj))
                        archivos_escaneados += 1
                        if resultado and resultado.tiene_amenazas():
                            amenazas_detectadas += 1
                            archivos_infectados.append(str(path_obj))
                    
                    elif path_obj.is_dir():
                        for archivo in path_obj.rglob('*'):
                            if archivo.is_file() and archivo.stat().st_size < 100 * 1024 * 1024:  # < 100MB
                                try:
                                    resultado = self.escaneador.escanear_archivo(str(archivo))
                                    archivos_escaneados += 1
                                    if resultado and resultado.tiene_amenazas():
                                        amenazas_detectadas += 1
                                        archivos_infectados.append(str(archivo))
                                    
                                    if callback_progreso and archivos_escaneados % 50 == 0:
                                        callback_progreso(f"Archivo: {archivo.name}", archivos_escaneados, amenazas_detectadas)
                                
                                except Exception as e:
                                    self.logger.warning(f"Error escaneando {archivo}: {e}")
                
                except Exception as e:
                    self.logger.warning(f"Error accediendo a {ruta}: {e}")
            
            tiempo_total = time.time() - inicio_tiempo
            
            # Crear resultado
            resultado = {
                'tipo_escaneo': 'completo',
                'archivos_escaneados': archivos_escaneados,
                'amenazas_detectadas': amenazas_detectadas,
                'archivos_infectados': len(archivos_infectados),
                'tiempo_escaneo': tiempo_total,
                'rutas_escaneadas': rutas_existentes,
                'archivos_infectados_lista': archivos_infectados,
                'timestamp': datetime.now().isoformat()
            }
            
            # Guardar como último escaneo
            self.ultimo_escaneo = resultado
            
            # Registrar finalización
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ESCANEO_FINALIZADO,
                    f"Escaneo completo completado: {amenazas_detectadas} amenazas en {archivos_escaneados} archivos",
                    resultado,
                    "ALTO" if amenazas_detectadas > 0 else "BAJO"
                )
            
            if callback_progreso:
                callback_progreso("Escaneo completado", archivos_escaneados, amenazas_detectadas)
            
            self.logger.info(f"Escaneo completo completado: {archivos_escaneados} archivos, {amenazas_detectadas} amenazas en {tiempo_total:.2f}s")
            return resultado
        
        finally:
            with self.lock:
                self.escaneo_activo = False
    
    def ejecutar_escaneo_directorio(self, ruta: str, callback_progreso: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Ejecutar escaneo de un directorio específico.
        
        Args:
            ruta: Ruta del directorio a escanear
            callback_progreso: Función callback para reportar progreso
            
        Returns:
            Dict[str, Any]: Resultados del escaneo
        """
        if not Path(ruta).exists():
            raise ValueError(f"La ruta no existe: {ruta}")
        
        with self.lock:
            if self.escaneo_activo:
                raise RuntimeError("Ya hay un escaneo en progreso")
            
            self.escaneo_activo = True
        
        try:
            self.logger.info(f"Iniciando escaneo de directorio: {ruta}")
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ESCANEO_INICIADO,
                    f"Escaneo de directorio iniciado: {ruta}",
                    {'tipo': 'directorio', 'ruta': ruta},
                    "MEDIO"
                )
            
            inicio_tiempo = time.time()
            archivos_escaneados = 0
            amenazas_detectadas = 0
            archivos_infectados = []
            
            path_obj = Path(ruta)
            
            if callback_progreso:
                callback_progreso(f"Escaneando: {ruta}", 0, 0)
            
            if path_obj.is_file():
                resultado = self.escaneador.escanear_archivo(str(path_obj))
                archivos_escaneados = 1
                if resultado and resultado.tiene_amenazas():
                    amenazas_detectadas = 1
                    archivos_infectados.append(str(path_obj))
            
            elif path_obj.is_dir():
                for archivo in path_obj.rglob('*'):
                    if archivo.is_file() and archivo.stat().st_size < 50 * 1024 * 1024:  # < 50MB
                        try:
                            resultado = self.escaneador.escanear_archivo(str(archivo))
                            archivos_escaneados += 1
                            if resultado and resultado.tiene_amenazas():
                                amenazas_detectadas += 1
                                archivos_infectados.append(str(archivo))
                            
                            if callback_progreso and archivos_escaneados % 25 == 0:
                                callback_progreso(f"Archivo: {archivo.name}", archivos_escaneados, amenazas_detectadas)
                        
                        except Exception as e:
                            self.logger.warning(f"Error escaneando {archivo}: {e}")
            
            tiempo_total = time.time() - inicio_tiempo
            
            # Crear resultado
            resultado = {
                'tipo_escaneo': 'directorio',
                'ruta_escaneada': ruta,
                'archivos_escaneados': archivos_escaneados,
                'amenazas_detectadas': amenazas_detectadas,
                'archivos_infectados': len(archivos_infectados),
                'tiempo_escaneo': tiempo_total,
                'archivos_infectados_lista': archivos_infectados,
                'timestamp': datetime.now().isoformat()
            }
            
            # Registrar finalización
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ESCANEO_FINALIZADO,
                    f"Escaneo de directorio finalizado: {ruta}",
                    resultado,
                    "MEDIO"
                )
            
            if callback_progreso:
                callback_progreso("Escaneo completado", archivos_escaneados, amenazas_detectadas)
            
            self.logger.info(f"Escaneo de directorio completado en {tiempo_total:.2f}s")
            return resultado
        
        finally:
            with self.lock:
                self.escaneo_activo = False
    
    def obtener_estadisticas_escaneos(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de escaneos realizados.
        
        Returns:
            Dict[str, Any]: Estadísticas de escaneos
        """
        try:
            stats_escaneador = self.escaneador.obtener_estadisticas()
            
            return {
                'total_archivos_escaneados': stats_escaneador.get('total_archivos_escaneados', 0),
                'total_amenazas_detectadas': stats_escaneador.get('total_amenazas_detectadas', 0),
                'ultimo_escaneo': self.ultimo_escaneo,
                'escaneo_activo': self.escaneo_activo,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'total_archivos_escaneados': 0,
                'total_amenazas_detectadas': 0,
                'ultimo_escaneo': self.ultimo_escaneo,
                'escaneo_activo': self.escaneo_activo,
                'timestamp': datetime.now().isoformat()
            }
    
    def obtener_ultimo_escaneo(self) -> Optional[Dict[str, Any]]:
        """
        Obtener información del último escaneo realizado.
        
        Returns:
            Optional[Dict[str, Any]]: Datos del último escaneo o None
        """
        return self.ultimo_escaneo
    
    def esta_escaneando(self) -> bool:
        """
        Verificar si hay un escaneo en progreso.
        
        Returns:
            bool: True si hay un escaneo activo
        """
        return self.escaneo_activo
    
    def cancelar_escaneo(self) -> bool:
        """
        Cancelar el escaneo actual si es posible.
        
        Returns:
            bool: True si se canceló exitosamente
        """
        if self.escaneo_activo:
            self.logger.info("Solicitando cancelación del escaneo activo")
            # Aquí se implementaría la lógica de cancelación
            # Por ahora solo registramos la solicitud
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ESCANEO_INTERRUMPIDO,
                    "Escaneo cancelado por solicitud del usuario",
                    {},
                    "MEDIO"
                )
            return True
        
        return False
    
    def programar_escaneo(self, tipo_escaneo: str, horario: datetime, parametros: Optional[Dict[str, Any]] = None) -> str:
        """
        Programar un escaneo para ejecutarse en el futuro.
        
        Args:
            tipo_escaneo: Tipo de escaneo ('rapido', 'completo', 'directorio')
            horario: Horario programado para el escaneo
            parametros: Parámetros adicionales para el escaneo
            
        Returns:
            str: ID del escaneo programado
        """
        escaneo_id = f"scan_{int(time.time())}_{len(self.escaneos_programados)}"
        
        escaneo_programado = {
            'id': escaneo_id,
            'tipo': tipo_escaneo,
            'horario': horario,
            'parametros': parametros or {},
            'estado': 'programado',
            'creado': datetime.now()
        }
        
        self.escaneos_programados.append(escaneo_programado)
        
        self.logger.info(f"Escaneo programado: {escaneo_id} para {horario}")
        
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.CONFIGURACION_MODIFICADA,
                f"Escaneo programado: {tipo_escaneo} para {horario.isoformat()}",
                escaneo_programado,
                "BAJO"
            )
        
        return escaneo_id
    
    def obtener_escaneos_programados(self) -> List[Dict[str, Any]]:
        """
        Obtener lista de escaneos programados.
        
        Returns:
            List[Dict[str, Any]]: Lista de escaneos programados
        """
        return self.escaneos_programados.copy()
    
    def cancelar_escaneo_programado(self, escaneo_id: str) -> bool:
        """
        Cancelar un escaneo programado.
        
        Args:
            escaneo_id: ID del escaneo a cancelar
            
        Returns:
            bool: True si se canceló exitosamente
        """
        for i, escaneo in enumerate(self.escaneos_programados):
            if escaneo['id'] == escaneo_id:
                del self.escaneos_programados[i]
                self.logger.info(f"Escaneo programado cancelado: {escaneo_id}")
                return True
        
        return False


