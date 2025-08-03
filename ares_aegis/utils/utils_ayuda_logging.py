import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

def configurar_logger(nombre_logger: str = "ares_aegis", nivel: int = logging.INFO, archivo_log: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(nombre_logger)
    if logger.handlers: return logger
    
    logger.setLevel(nivel)
    formato = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(nivel)
    handler_consola.setFormatter(formato)
    logger.addHandler(handler_consola)
    
    if archivo_log:
        try:
            Path(archivo_log).parent.mkdir(parents=True, exist_ok=True)
            handler_archivo = logging.FileHandler(archivo_log)
            handler_archivo.setLevel(nivel)
            handler_archivo.setFormatter(formato)
            logger.addHandler(handler_archivo)
        except Exception as e:
            logger.warning(f"No se pudo crear archivo de log {archivo_log}: {e}")
    return logger

configurar_logger_principal = configurar_logger


def configurar_logger_modulo(nombre_modulo: str, logger_padre: Optional[logging.Logger] = None) -> logging.Logger:
    nombre_completo = f"{logger_padre.name}.{nombre_modulo}" if logger_padre else f"ares_aegis.{nombre_modulo}"
    logger = logging.getLogger(nombre_completo)
    if logger_padre and not logger.handlers: logger.setLevel(logger_padre.level)
    return logger

def log_evento_seguridad(logger: logging.Logger, evento: str, detalles: str = ""):
    mensaje = f"[SEGURIDAD] {evento}"
    if detalles: mensaje += f" - {detalles}"
    logger.warning(mensaje)

def log_amenaza_detectada(logger: logging.Logger, archivo: str, amenaza: str):
    logger.error(f"[AMENAZA] Detectada en {archivo}: {amenaza}")

def log_inicio_escaneo(logger: logging.Logger, tipo_escaneo: str, objetivo: str):
    logger.info(f"[ESCANEO] Iniciando {tipo_escaneo} en {objetivo}")

def log_fin_escaneo(logger: logging.Logger, tipo_escaneo: str, resultado: str, amenazas_encontradas: int = 0):
    mensaje = f"[ESCANEO] Finalizado {tipo_escaneo} - {resultado}"
    if amenazas_encontradas > 0: mensaje += f" - {amenazas_encontradas} amenaza(s) detectada(s)"
    logger.warning(mensaje) if amenazas_encontradas > 0 else logger.info(mensaje)

def log_error_sistema(logger: logging.Logger, modulo: str, error: str):
    logger.error(f"[ERROR] {modulo}: {error}")

def log_operacion_cuarentena(logger: logging.Logger, operacion: str, archivo: str):
    logger.info(f"[CUARENTENA] {operacion.capitalize()}: {archivo}")

def obtener_ruta_log_por_defecto() -> str:
    try:
        ruta_sistema = "/var/log/ares_aegis/ares_aegis.log"
        Path(ruta_sistema).parent.mkdir(parents=True, exist_ok=True)
        if os.access(Path(ruta_sistema).parent, os.W_OK): return ruta_sistema
    except: pass
    return str(Path.cwd() / "ares_aegis.log")

def configurar_logging_completo(nivel: int = logging.INFO) -> logging.Logger:
    archivo_log = obtener_ruta_log_por_defecto()
    logger = configurar_logger_principal("ares_aegis", nivel, archivo_log)
    logger.info("=" * 60)
    logger.info("Sistema de logging de Ares Aegis iniciado")
    logger.info(f"Archivo de log: {archivo_log}")
    logger.info("=" * 60)
    return logger
