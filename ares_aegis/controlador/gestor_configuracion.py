#!/usr/bin/env python3
"""
Ares Aegis - Gestor de Configuración Centralizado
Sistema centralizado para gestionar configuraciones de todos los controladores

Creado por DogSoulDev
Versión: 4.0.0 - Arquitectura MVC Optimizada
"""

import json
import os
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging

from ..utils.ayuda_logging import configurar_logger_modulo
from ..utils.ayuda_rutas import crear_ruta_segura


@dataclass
class ConfiguracionSIEM:
    """Configuración para el controlador SIEM"""
    ventana_tiempo: int = 300
    umbral_eventos_similares: int = 5
    tipos_eventos_criticos: List[str] = None
    max_eventos_memoria: int = 10000
    archivo_eventos: str = "eventos_siem.json"
    integrar_journald: bool = True
    monitorear_auth_log: bool = True
    
    def __post_init__(self):
        if self.tipos_eventos_criticos is None:
            self.tipos_eventos_criticos = [
                "AMENAZA_DETECTADA",
                "MALWARE_DETECTADO",
                "ACCESO_NO_AUTORIZADO"
            ]


@dataclass
class ConfiguracionEscaneador:
    """Configuración para el controlador de escaneador"""
    extensiones_peligrosas: List[str] = None
    tamaño_maximo_archivo_mb: int = 100
    timeout_escaneo_segundos: int = 30
    usar_cache: bool = True
    threads_escaneo: int = 4
    usar_yara: bool = True
    usar_clamav: bool = True
    usar_checksec: bool = True
    analisis_profundo: bool = True
    
    def __post_init__(self):
        if self.extensiones_peligrosas is None:
            self.extensiones_peligrosas = [
                ".exe", ".bat", ".cmd", ".scr", ".pif", ".com", 
                ".js", ".vbs", ".ps1", ".jar", ".dll"
            ]


@dataclass
class ConfiguracionFIM:
    """Configuración para el controlador FIM"""
    rutas_monitoreadas: List[str] = None
    rutas_criticas_sistema: List[str] = None
    rutas_excluidas: List[str] = None
    intervalo_verificacion_minutos: int = 5
    detectar_cambios_contenido: bool = True
    detectar_cambios_permisos: bool = True
    detectar_cambios_propietario: bool = True
    max_archivos_monitoreados: int = 50000
    usar_inotify: bool = True
    verificacion_integridad: bool = True
    
    def __post_init__(self):
        if self.rutas_monitoreadas is None:
            # Rutas para Kali Linux
            self.rutas_monitoreadas = [
                "/etc",
                "/usr/bin",
                "/usr/sbin",
                "/boot",
                "/home",
                "/opt"
            ]
        
        if self.rutas_criticas_sistema is None:
            self.rutas_criticas_sistema = [
                "/etc/passwd",
                "/etc/shadow",
                "/etc/sudoers",
                "/etc/ssh/sshd_config",
                "/etc/hosts",
                "/etc/crontab",
                "/etc/pam.d"
            ]
        
        if self.rutas_excluidas is None:
            self.rutas_excluidas = [
                "*.log", "*.tmp", "*.temp", "__pycache__", "*.pyc"
            ]


@dataclass
class ConfiguracionMonitorRed:
    """Configuración para el controlador de monitor de red"""
    umbral_conexiones_sospechosas: int = 50
    ventana_analisis_minutos: int = 5
    puertos_criticos: List[int] = None
    puertos_pentesting: List[int] = None
    ips_whitelist: List[str] = None
    detectar_port_scanning: bool = True
    detectar_ddos: bool = True
    detectar_arp_spoofing: bool = True
    timeout_conexion_segundos: int = 5
    usar_netstat: bool = True
    usar_ss: bool = True
    usar_lsof: bool = True
    capturar_paquetes: bool = True
    analizar_trafico: bool = True
    
    def __post_init__(self):
        if self.puertos_criticos is None:
            self.puertos_criticos = [22, 23, 80, 443, 21, 25, 53, 110, 143, 993, 995]
        
        if self.puertos_pentesting is None:
            self.puertos_pentesting = [4444, 4445, 8080, 8443, 9999, 31337, 12345, 54321]
        
        if self.ips_whitelist is None:
            self.ips_whitelist = ["127.0.0.1", "::1", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]


@dataclass
class ConfiguracionCuarentena:
    """Configuración para el controlador de cuarentena"""
    directorio_cuarentena: str = "cuarentena"
    directorio_backup: str = "cuarentena/backups"
    analisis_automatico: bool = True
    notificar_cuarentena: bool = True
    backup_antes_cuarentena: bool = True
    periodo_retencion_dias: int = 30
    max_tamaño_cuarentena_gb: int = 10
    encriptacion_cuarentena: bool = True
    verificacion_hash: bool = True
    
    def __post_init__(self):
        # Crear directorios si no existen
        Path(self.directorio_cuarentena).mkdir(parents=True, exist_ok=True)
        Path(self.directorio_backup).mkdir(parents=True, exist_ok=True)


@dataclass
class ConfiguracionReportes:
    """Configuración para el controlador de reportes"""
    directorio_reportes: str = "reportes"
    formato_por_defecto: str = "markdown"
    incluir_graficos: bool = False
    incluir_metricas: bool = True
    periodo_por_defecto_dias: int = 7
    max_reportes_guardados: int = 100
    auto_limpieza_dias: int = 90
    enviar_email: bool = False
    generar_pdf: bool = True
    incluir_recomendaciones: bool = True
    
    def __post_init__(self):
        # Crear directorio si no existe
        Path(self.directorio_reportes).mkdir(parents=True, exist_ok=True)


@dataclass
class ConfiguracionGlobal:
    """Configuración global del sistema"""
    siem: ConfiguracionSIEM = None
    escaneador: ConfiguracionEscaneador = None
    fim: ConfiguracionFIM = None
    monitor_red: ConfiguracionMonitorRed = None
    cuarentena: ConfiguracionCuarentena = None
    reportes: ConfiguracionReportes = None
    
    # Configuración general
    nivel_log: str = "INFO"
    max_threads_globales: int = 10
    timeout_operaciones_segundos: int = 60
    modo_debug: bool = False
    
    def __post_init__(self):
        if self.siem is None:
            self.siem = ConfiguracionSIEM()
        if self.escaneador is None:
            self.escaneador = ConfiguracionEscaneador()
        if self.fim is None:
            self.fim = ConfiguracionFIM()
        if self.monitor_red is None:
            self.monitor_red = ConfiguracionMonitorRed()
        if self.cuarentena is None:
            self.cuarentena = ConfiguracionCuarentena()
        if self.reportes is None:
            self.reportes = ConfiguracionReportes()


class GestorConfiguracion:
    """
    Gestor centralizado de configuración para todos los controladores.
    
    Características:
    - Configuración centralizada en archivo JSON
    - Hot-reload de configuración
    - Validación de configuración
    - Configuración por defecto
    - Thread-safe
    """
    
    _instancia = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    cls._instancia = super().__new__(cls)
        return cls._instancia
    
    def __init__(self):
        if hasattr(self, '_inicializado'):
            return
            
        self.logger = configurar_logger_modulo("gestor_configuracion")
        self._configuracion: ConfiguracionGlobal = ConfiguracionGlobal()
        self._archivo_config = Path("configuracion/ares_aegis_config.json")
        self._lock_config = threading.RLock()
        self._callbacks_cambio = []
        self._inicializado = True
        
        # Crear directorio de configuración
        self._archivo_config.parent.mkdir(parents=True, exist_ok=True)
        
        # Cargar configuración
        self.cargar_configuracion()
        
        self.logger.info("Gestor de configuración inicializado")
    
    def cargar_configuracion(self) -> bool:
        """
        Cargar configuración desde archivo.
        
        Returns:
            True si la carga fue exitosa
        """
        try:
            if self._archivo_config.exists():
                with open(self._archivo_config, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Reconstruir configuración desde JSON
                with self._lock_config:
                    self._configuracion = self._dict_a_configuracion(data)
                
                self.logger.info(f"Configuración cargada desde {self._archivo_config}")
                self._notificar_cambio()
                return True
            else:
                # Crear configuración por defecto
                self.guardar_configuracion()
                self.logger.info("Configuración por defecto creada")
                return True
                
        except Exception as e:
            self.logger.error(f"Error cargando configuración: {e}")
            # Usar configuración por defecto en caso de error
            self._configuracion = ConfiguracionGlobal()
            return False
    
    def guardar_configuracion(self) -> bool:
        """
        Guardar configuración actual al archivo.
        
        Returns:
            True si el guardado fue exitoso
        """
        try:
            with self._lock_config:
                data = self._configuracion_a_dict(self._configuracion)
            
            # Guardar con formato legible
            with open(self._archivo_config, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuración guardada en {self._archivo_config}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando configuración: {e}")
            return False
    
    def obtener_configuracion(self) -> ConfiguracionGlobal:
        """
        Obtener configuración actual.
        
        Returns:
            Configuración global actual
        """
        with self._lock_config:
            # Retornar copia para evitar modificaciones externas
            return self._dict_a_configuracion(
                self._configuracion_a_dict(self._configuracion)
            )
    
    def actualizar_configuracion(self, nueva_config: ConfiguracionGlobal) -> bool:
        """
        Actualizar configuración completa.
        
        Args:
            nueva_config: Nueva configuración
            
        Returns:
            True si la actualización fue exitosa
        """
        try:
            with self._lock_config:
                self._configuracion = nueva_config
            
            success = self.guardar_configuracion()
            if success:
                self._notificar_cambio()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error actualizando configuración: {e}")
            return False
    
    def obtener_config_controlador(self, nombre_controlador: str) -> Any:
        """
        Obtener configuración específica de un controlador.
        
        Args:
            nombre_controlador: Nombre del controlador
            
        Returns:
            Configuración del controlador o None si no existe
        """
        with self._lock_config:
            return getattr(self._configuracion, nombre_controlador, None)
    
    def suscribir_cambios(self, callback: callable):
        """
        Suscribirse a notificaciones de cambio de configuración.
        
        Args:
            callback: Función a llamar cuando cambie la configuración
        """
        self._callbacks_cambio.append(callback)
    
    def _notificar_cambio(self):
        """Notificar a todos los suscriptores sobre cambios de configuración"""
        for callback in self._callbacks_cambio:
            try:
                callback(self._configuracion)
            except Exception as e:
                self.logger.error(f"Error en callback de configuración: {e}")
    
    def _configuracion_a_dict(self, config: ConfiguracionGlobal) -> Dict[str, Any]:
        """Convertir configuración a diccionario"""
        return asdict(config)
    
    def _dict_a_configuracion(self, data: Dict[str, Any]) -> ConfiguracionGlobal:
        """Convertir diccionario a configuración"""
        return ConfiguracionGlobal(
            siem=ConfiguracionSIEM(**data.get('siem', {})),
            escaneador=ConfiguracionEscaneador(**data.get('escaneador', {})),
            fim=ConfiguracionFIM(**data.get('fim', {})),
            monitor_red=ConfiguracionMonitorRed(**data.get('monitor_red', {})),
            cuarentena=ConfiguracionCuarentena(**data.get('cuarentena', {})),
            reportes=ConfiguracionReportes(**data.get('reportes', {})),
            nivel_log=data.get('nivel_log', 'INFO'),
            max_threads_globales=data.get('max_threads_globales', 10),
            timeout_operaciones_segundos=data.get('timeout_operaciones_segundos', 60),
            modo_debug=data.get('modo_debug', False)
        )
    
    def validar_configuracion(self) -> List[str]:
        """
        Validar configuración actual.
        
        Returns:
            Lista de errores de validación (vacía si no hay errores)
        """
        errores = []
        
        try:
            config = self.obtener_configuracion()
            
            # Validar valores numéricos
            if config.siem.ventana_tiempo <= 0:
                errores.append("SIEM: ventana_tiempo debe ser mayor a 0")
            
            if config.escaneador.tamaño_maximo_archivo_mb <= 0:
                errores.append("Escaneador: tamaño_maximo_archivo_mb debe ser mayor a 0")
            
            if config.fim.intervalo_verificacion_minutos <= 0:
                errores.append("FIM: intervalo_verificacion_minutos debe ser mayor a 0")
            
            # Validar directorios
            for ruta in config.fim.rutas_monitoreadas:
                if not Path(ruta).exists():
                    errores.append(f"FIM: ruta monitoreada no existe: {ruta}")
            
            # Validar nivel de log
            niveles_validos = ['DEBUG', 'INFO', 'ADVERTENCIA', 'ERROR', 'CRITICAL']
            if config.nivel_log not in niveles_validos:
                errores.append(f"Nivel de log inválido: {config.nivel_log}")
            
        except Exception as e:
            errores.append(f"Error validando configuración: {e}")
        
        return errores


# Instancia singleton global
gestor_configuracion = GestorConfiguracion()
