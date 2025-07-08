from ..modelos.siem import SIEM, EventoSIEM
from .controlador_alertas import ControladorAlertas
from ..modelos.alerta import SeveridadAlerta, TipoAlerta

class ControladorAlertasSIEM:
    """Controlador para integración de eventos SIEM con el sistema centralizado de alertas."""
    def __init__(self, siem: SIEM, controlador_alertas: ControladorAlertas):
        self.siem = siem
        self.controlador_alertas = controlador_alertas

    def verificar_eventos_siem(self, severidades_interes=None):
        eventos = self.siem.obtener_eventos(limite=100)
        for evento in eventos:
            # Mapear prioridad SIEM a SeveridadAlerta
            prioridad = getattr(evento, 'prioridad', 'INFO')
            prioridad_map = {
                'CRITICO': SeveridadAlerta.CRITICO,
                'ALTO': SeveridadAlerta.ALTO,
                'MEDIO': SeveridadAlerta.MEDIO,
                'BAJO': SeveridadAlerta.BAJO,
                'INFO': SeveridadAlerta.INFO
            }
            severidad = prioridad_map.get(str(prioridad).upper(), SeveridadAlerta.INFO)
            if severidades_interes and severidad not in severidades_interes:
                continue
            mensaje = getattr(evento, 'mensaje', 'Evento SIEM detectado')
            datos = evento.to_dict() if hasattr(evento, 'to_dict') else {}
            self.controlador_alertas.crear_alerta(
                mensaje=mensaje,
                tipo=TipoAlerta.CORRELACION,
                severidad=severidad,
                fuente="SIEM",
                datos=datos
            )
