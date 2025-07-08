from ..modelos.monitor_red import MonitorRed
from .controlador_alertas import ControladorAlertas
from ..modelos.alerta import SeveridadAlerta, TipoAlerta

class ControladorAlertasRed:
    """Controlador para integración de alertas de red con el sistema centralizado de alertas."""
    def __init__(self, monitor_red: MonitorRed, controlador_alertas: ControladorAlertas):
        self.monitor_red = monitor_red
        self.controlador_alertas = controlador_alertas

    def verificar_eventos_red(self):
        # Ejemplo: Si se implementan eventos sospechosos, aquí se procesarían
        # Por ahora, solo se simula una alerta de ejemplo si hay muchas conexiones
        conexiones = self.monitor_red.obtener_conexiones()
        if len(conexiones) > 100:  # Umbral de ejemplo
            mensaje = f"Conexiones de red inusuales detectadas: {len(conexiones)} activas."
            datos = {"total_conexiones": len(conexiones)}
            self.controlador_alertas.crear_alerta(
                mensaje=mensaje,
                tipo=TipoAlerta.RED,
                severidad=SeveridadAlerta.ALTO,
                fuente="Red",
                datos=datos
            )
