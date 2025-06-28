"""
Configuración y utilidades de logging para el proyecto.
Permite registrar eventos, advertencias y errores de forma profesional.

Uso:
    from antivirus_kali.utilidades import logger
    logger.info("Mensaje informativo")
    logger.error("Mensaje de error")
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Formatter personalizado con colores para terminal"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Verde
        'WARNING': '\033[33m',   # Amarillo
        'ERROR': '\033[31m',     # Rojo
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Formatear mensaje con color
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        return super().format(record)


class SiemLogger:
    """
    Logger especializado para el sistema Ares Aegis con soporte para múltiples niveles
    y rotación de archivos.
    """
    
    def __init__(self, name: str = "AresAegis", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Evitar duplicar handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura los manejadores de logging"""
        
        # Formato para logs
        formato_detallado = (
            "%(asctime)s | %(name)s | %(levelname)s | "
            "%(filename)s:%(lineno)d | %(funcName)s() | %(message)s"
        )
        
        formato_simple = "%(asctime)s | %(levelname)s | %(message)s"
        
        # Handler para archivo con rotación
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        archivo_handler = RotatingFileHandler(
            log_dir / "ares_aegis.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        archivo_handler.setLevel(logging.DEBUG)
        archivo_handler.setFormatter(logging.Formatter(formato_detallado))
        
        # Handler para errores críticos
        error_handler = RotatingFileHandler(
            log_dir / "ares_aegis_errors.log",
            maxBytes=5*1024*1024,   # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(formato_detallado))
        
        # Handler para consola con colores
        consola_handler = logging.StreamHandler(sys.stdout)
        consola_handler.setLevel(logging.INFO)
        consola_handler.setFormatter(ColoredFormatter(formato_simple))
        
        # Agregar handlers
        self.logger.addHandler(archivo_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(consola_handler)
    
    def debug(self, mensaje: str, **kwargs):
        """Log de debug"""
        self.logger.debug(mensaje, **kwargs)
    
    def info(self, mensaje: str, **kwargs):
        """Log informativo"""
        self.logger.info(mensaje, **kwargs)
    
    def warning(self, mensaje: str, **kwargs):
        """Log de advertencia"""
        self.logger.warning(mensaje, **kwargs)
    
    def error(self, mensaje: str, excepcion: Optional[Exception] = None, **kwargs):
        """Log de error"""
        if excepcion:
            self.logger.error(f"{mensaje} | Excepción: {str(excepcion)}", **kwargs)
        else:
            self.logger.error(mensaje, **kwargs)
    
    def critical(self, mensaje: str, excepcion: Optional[Exception] = None, **kwargs):
        """Log crítico"""
        if excepcion:
            self.logger.critical(f"{mensaje} | Excepción: {str(excepcion)}", **kwargs)
        else:
            self.logger.critical(mensaje, **kwargs)
    
    def log_siem_event(self, evento: str, nivel: str = "INFO", 
                       categoria: str = "SIEM", **detalles):
        """
        Log especializado para eventos del SIEM
        
        Args:
            evento: Descripción del evento
            nivel: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            categoria: Categoría del evento (SIEM, ESCANEO, RED, etc.)
            detalles: Detalles adicionales del evento
        """
        timestamp = datetime.now().isoformat()
        mensaje = f"[{categoria}] {evento}"
        
        if detalles:
            detalles_str = " | ".join([f"{k}={v}" for k, v in detalles.items()])
            mensaje += f" | {detalles_str}"
        
        nivel_func = getattr(self.logger, nivel.lower(), self.logger.info)
        nivel_func(mensaje)
    
    def log_security_event(self, evento: str, severidad: str = "MEDIA", 
                          origen: str = "SISTEMA", **contexto):
        """
        Log especializado para eventos de seguridad
        
        Args:
            evento: Descripción del evento de seguridad
            severidad: BAJA, MEDIA, ALTA, CRITICA
            origen: Origen del evento (SISTEMA, RED, ARCHIVO, etc.)
            contexto: Contexto adicional del evento
        """
        nivel_map = {
            "BAJA": "info",
            "MEDIA": "warning", 
            "ALTA": "error",
            "CRITICA": "critical"
        }
        
        timestamp = datetime.now().isoformat()
        mensaje = f"[SEGURIDAD-{severidad}] [{origen}] {evento}"
        
        if contexto:
            contexto_str = " | ".join([f"{k}={v}" for k, v in contexto.items()])
            mensaje += f" | {contexto_str}"
        
        nivel_func = getattr(self.logger, nivel_map.get(severidad, "info"))
        nivel_func(mensaje)


# Instancia global del logger
_logger_instance = None

def get_logger(name: str = "AresAegis", log_level: str = "INFO") -> SiemLogger:
    """
    Obtiene la instancia del logger (singleton)
    
    Args:
        name: Nombre del logger
        log_level: Nivel de logging
        
    Returns:
        Instancia del SiemLogger
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SiemLogger(name, log_level)
    return _logger_instance


# Crear instancia por defecto para uso directo
logger = get_logger()

# Exports para facilitar importación
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical
log_siem_event = logger.log_siem_event
log_security_event = logger.log_security_event
