
from enum import Enum
from datetime import datetime
from typing import Optional, Dict

class SeveridadAlerta(Enum):
    CRITICO = "critico"
    ALTO = "alto"
    MEDIO = "medio"
    BAJO = "bajo"
    INFO = "info"

class TipoAlerta(Enum):
    AMENAZA = "amenaza"
    INTEGRIDAD = "integridad"
    PROCESO = "proceso"
    RED = "red"
    SISTEMA = "sistema"
    RECURSO = "recurso"
    CORRELACION = "correlacion"
    OTRO = "otro"


class Alerta:
    """Modelo centralizado de alerta para SIEM/antivirus"""
    def __init__(self, mensaje: str, tipo: TipoAlerta, severidad: SeveridadAlerta, fuente: str = "", timestamp: Optional[datetime] = None, datos: Optional[Dict] = None):
        self.mensaje = mensaje
        self.tipo = tipo
        self.severidad = severidad
        self.fuente = fuente or "sistema"
        self.timestamp = timestamp or datetime.now()
        self.datos = datos or {}

    def to_dict(self):
        return {
            "mensaje": self.mensaje,
            "tipo": self.tipo.value,
            "severidad": self.severidad.value,
            "fuente": self.fuente,
            "timestamp": self.timestamp.isoformat(),
            "datos": self.datos
        }

    @staticmethod
    def from_dict(data):
        return Alerta(
            mensaje=data.get("mensaje", ""),
            tipo=TipoAlerta(data.get("tipo", "otro")),
            severidad=SeveridadAlerta(data.get("severidad", "info")),
            fuente=data.get("fuente", "sistema"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            datos=data.get("datos", {})
        )

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] ({self.severidad.value.upper()}) {self.tipo.value.upper()}: {self.mensaje}"
