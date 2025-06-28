"""
Configuración global de la aplicación Ares Aegis.
Constantes, rutas y parámetros centralizados para todo el sistema.
"""

import os
from pathlib import Path
from typing import Dict, Any

# === RUTAS DEL SISTEMA ===
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
RESOURCES_DIR = BASE_DIR / "recursos"
ICONS_DIR = RESOURCES_DIR / "iconos"
YARA_RULES_DIR = RESOURCES_DIR / "reglas_yara"
CONFIG_DIR = BASE_DIR / "configuraciones"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = PROJECT_ROOT
REPORTS_DIR = BASE_DIR / "reports"

# Crear directorios si no existen
for directory in [DATA_DIR, CONFIG_DIR, REPORTS_DIR]:
    directory.mkdir(exist_ok=True)

# === CONFIGURACIÓN DEL MINI-SIEM ===
SIEM_CONFIG = {
    "database": {
        "path": str(DATA_DIR / "siem_events.db"),
        "retention_days": int(os.getenv("SIEM_RETENTION_DAYS", "30")),
        "batch_size": 100,
        "connection_timeout": 30
    },
    "collection": {
        "poll_interval": 1,
        "max_events_per_batch": 1000,
        "sources": [
            "/var/log/auth.log",
            "/var/log/syslog", 
            "/var/log/dpkg.log",
            "/var/log/kern.log"
        ]
    },
    "notifications": {
        "desktop": os.getenv("ALERT_DESKTOP_ENABLED", "true").lower() == "true",
        "terminal": os.getenv("ALERT_TERMINAL_ENABLED", "true").lower() == "true",
        "log_file": True,
        "webhook_url": os.getenv("ALERT_WEBHOOK_URL", "")
    },
    "correlation": {
        "max_events_memory": 10000,
        "cleanup_interval": 3600  # segundos
    }
}

# === CONFIGURACIÓN DEL ANTIVIRUS ===
ANTIVIRUS_CONFIG = {
    "clamav": {
        "database_path": os.getenv("CLAMAV_DB_PATH", "/var/lib/clamav"),
        "socket_path": "/var/run/clamav/clamd.ctl",
        "timeout": 60
    },
    "yara": {
        "rules_path": str(YARA_RULES_DIR),
        "compiled_rules_cache": str(DATA_DIR / "yara_compiled.cache")
    },
    "scan": {
        "max_file_size": 100 * 1024 * 1024,  # 100MB
        "skip_extensions": [".log", ".tmp"],
        "quarantine_dir": str(DATA_DIR / "quarantine")
    }
}

# === CONFIGURACIÓN DE LA INTERFAZ ===
UI_CONFIG = {
    "theme": {
        "primary_color": "#3498db",
        "secondary_color": "#2c3e50",
        "accent_color": "#27ae60",
        "warning_color": "#f39c12",
        "error_color": "#e74c3c"
    },
    "window": {
        "min_width": 1200,
        "min_height": 800,
        "default_width": 1400,
        "default_height": 900
    },
    "performance": {
        "update_interval": 1000,  # ms
        "max_log_entries": 1000
    }
}

# === CONFIGURACIÓN DE LOGGING ===
LOGGING_CONFIG = {
    "level": os.getenv("ARES_LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": str(LOGS_DIR / "ares_aegis.log"),
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# === CONFIGURACIÓN DE SEGURIDAD ===
SECURITY_CONFIG = {
    "input_validation": {
        "max_path_length": 4096,
        "allowed_extensions": [".py", ".txt", ".log", ".conf", ".json"],
        "blocked_paths": ["/etc/passwd", "/etc/shadow", "/etc/sudoers"]
    },
    "file_operations": {
        "max_file_size": 50 * 1024 * 1024,  # 50MB
        "safe_temp_dir": str(DATA_DIR / "temp")
    }
}

# === CONSTANTES GLOBALES ===
APP_NAME = "Ares Aegis"
APP_VERSION = "1.0.0"
APP_AUTHOR = "DogSoulDev"
APP_DESCRIPTION = "Sistema de Seguridad Avanzado con Mini-SIEM"

# === UTILIDADES DE CONFIGURACIÓN ===
def get_config_value(config_dict: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Obtener valor de configuración usando notación de puntos.
    Ejemplo: get_config_value(SIEM_CONFIG, "database.path")
    """
    keys = key_path.split('.')
    value = config_dict
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value

def validate_paths() -> bool:
    """Validar que todas las rutas necesarias existan o puedan crearse."""
    try:
        for directory in [DATA_DIR, CONFIG_DIR, REPORTS_DIR]:
            directory.mkdir(exist_ok=True)
        return True
    except Exception:
        return False

def get_system_requirements() -> Dict[str, str]:
    """Obtener requisitos del sistema actual."""
    import platform
    import sys
    
    return {
        "os": platform.system(),
        "os_version": platform.release(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "architecture": platform.machine()
    }

# Validar configuración al importar el módulo
if not validate_paths():
    import warnings
    warnings.warn("No se pudieron crear algunos directorios de configuración")
