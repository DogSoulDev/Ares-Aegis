from typing import List, Optional
from datetime import datetime, timedelta
from threading import Lock
from ..modelos.alerta import Alerta, SeveridadAlerta, TipoAlerta

class ControladorAlertas:
    """Controlador centralizado para gestión de alertas en Ares Aegis (MVC)."""
    def __init__(self, max_historial: int = 200):
        self._alertas: List[Alerta] = []
        self._lock = Lock()
        self.max_historial = max_historial

    def agregar_alerta(self, alerta: Alerta):
        with self._lock:
            self._alertas.append(alerta)
            if len(self._alertas) > self.max_historial:
                self._alertas = self._alertas[-self.max_historial:]

    def crear_alerta(self, mensaje: str, tipo: TipoAlerta, severidad: SeveridadAlerta, fuente: str = "", datos: Optional[dict] = None):
        alerta = Alerta(mensaje, tipo, severidad, fuente, datetime.now(), datos)
        self.agregar_alerta(alerta)
        return alerta

    def obtener_alertas(self, limite: int = 20, severidad: Optional[SeveridadAlerta] = None, tipo: Optional[TipoAlerta] = None) -> List[Alerta]:
        with self._lock:
            alertas = self._alertas[::-1]  # Más recientes primero
            if severidad:
                alertas = [a for a in alertas if a.severidad == severidad]
            if tipo:
                alertas = [a for a in alertas if a.tipo == tipo]
            return alertas[:limite]

    def obtener_alertas_criticas(self, limite: int = 10) -> List[Alerta]:
        return self.obtener_alertas(limite, SeveridadAlerta.CRITICO)

    def obtener_alertas_recientes(self, minutos: int = 5) -> List[Alerta]:
        corte = datetime.now() - timedelta(minutes=minutos)
        with self._lock:
            return [a for a in self._alertas if a.timestamp >= corte]

    def limpiar_alertas(self):
        with self._lock:
            self._alertas.clear()

    def total_alertas(self) -> int:
        with self._lock:
            return len(self._alertas)

    def total_por_severidad(self, severidad: SeveridadAlerta) -> int:
        with self._lock:
            return sum(1 for a in self._alertas if a.severidad == severidad)

    def total_por_tipo(self, tipo: TipoAlerta) -> int:
        with self._lock:
            return sum(1 for a in self._alertas if a.tipo == tipo)

    def exportar_alertas(self) -> List[dict]:
        with self._lock:
            return [a.to_dict() for a in self._alertas]

    def importar_alertas(self, alertas_dict: List[dict]):
        with self._lock:
            self._alertas = [Alerta.from_dict(d) for d in alertas_dict][-self.max_historial:]
