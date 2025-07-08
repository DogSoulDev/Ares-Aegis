from ..modelos.fim import FIM, NivelCriticidadFIM
from .controlador_alertas import ControladorAlertas
from ..modelos.alerta import SeveridadAlerta, TipoAlerta

class ControladorAlertasFIM:
    """Controlador para integración de alertas FIM con el sistema centralizado de alertas."""
    def __init__(self, fim: FIM, controlador_alertas: ControladorAlertas):
        self.fim = fim
        self.controlador_alertas = controlador_alertas

    def verificar_integridad(self):
        alertas_fim = self.fim.verificar_integridad_completa()
        for alerta_fim in alertas_fim:
            # Mapear criticidad FIM a SeveridadAlerta
            criticidad_map = {
                NivelCriticidadFIM.CRITICO: SeveridadAlerta.CRITICO,
                NivelCriticidadFIM.ALTO: SeveridadAlerta.ALTO,
                NivelCriticidadFIM.MEDIO: SeveridadAlerta.MEDIO,
                NivelCriticidadFIM.BAJO: SeveridadAlerta.BAJO,
                NivelCriticidadFIM.INFO: SeveridadAlerta.INFO
            }
            severidad = criticidad_map.get(alerta_fim.nivel_criticidad, SeveridadAlerta.INFO)
            mensaje = alerta_fim.descripcion
            datos = {
                "archivo": alerta_fim.archivo_afectado,
                "tipo_cambio": str(alerta_fim.tipo_cambio),
                "nivel_criticidad": alerta_fim.nivel_criticidad.value,
                "diferencias": alerta_fim.diferencias_detectadas,
                "evidencia": alerta_fim.evidencia
            }
            self.controlador_alertas.crear_alerta(
                mensaje=mensaje,
                tipo=TipoAlerta.INTEGRIDAD,
                severidad=severidad,
                fuente="FIM",
                datos=datos
            )
