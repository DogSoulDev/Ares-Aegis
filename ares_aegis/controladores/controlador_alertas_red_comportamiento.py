from ..modelos.analizador_comportamiento_red import MonitorTrafico
from .controlador_alertas import ControladorAlertas
from ..modelos.alerta import SeveridadAlerta, TipoAlerta

class ControladorAlertasRedComportamiento:
    """Controlador para integración de alertas de comportamiento de red con el sistema centralizado de alertas."""
    def __init__(self, monitor_trafico: MonitorTrafico, controlador_alertas: ControladorAlertas):
        self.monitor_trafico = monitor_trafico
        self.controlador_alertas = controlador_alertas

    def verificar_alertas_red(self):
        # Suponemos que el monitor ya tiene alertas activas generadas
        for alerta in getattr(self.monitor_trafico, 'alertas_activas', []):
            severidad = SeveridadAlerta.ALTO  # Puedes mapear según lógica propia si hay nivel
            mensaje = alerta.get('descripcion', 'Alerta de red detectada')
            datos = {
                "puerto": alerta.get('puerto'),
                "estado": alerta.get('estado'),
                "protocolo": alerta.get('protocolo'),
                "detalles": alerta
            }
            self.controlador_alertas.crear_alerta(
                mensaje=mensaje,
                tipo=TipoAlerta.RED,
                severidad=severidad,
                fuente="RED-COMPORTAMIENTO",
                datos=datos
            )
