from ..modelos.monitor_procesos import AnalizadorComportamientoProcesos, AlertaProceso, NivelRiesgoProceso
from .controlador_alertas import ControladorAlertas
from ..modelos.alerta import SeveridadAlerta, TipoAlerta

class ControladorAlertasProcesos:
    """Controlador para integración de alertas de procesos con el sistema centralizado de alertas."""
    def __init__(self, analizador: AnalizadorComportamientoProcesos, controlador_alertas: ControladorAlertas):
        self.analizador = analizador
        self.controlador_alertas = controlador_alertas

    def verificar_alertas_procesos(self):
        # Suponemos que el analizador ya tiene alertas activas generadas
        for alerta_proc in getattr(self.analizador, 'alertas_activas', []):
            # Mapear nivel de riesgo proceso a SeveridadAlerta
            riesgo_map = {
                NivelRiesgoProceso.CRITICO: SeveridadAlerta.CRITICO,
                NivelRiesgoProceso.ALTO: SeveridadAlerta.ALTO,
                NivelRiesgoProceso.MEDIO: SeveridadAlerta.MEDIO,
                NivelRiesgoProceso.BAJO: SeveridadAlerta.BAJO,
                NivelRiesgoProceso.INFO: SeveridadAlerta.INFO
            }
            severidad = riesgo_map.get(getattr(alerta_proc, 'nivel_severidad', NivelRiesgoProceso.INFO), SeveridadAlerta.INFO)
            mensaje = getattr(alerta_proc, 'descripcion', 'Alerta de proceso detectada')
            datos = {
                "proceso": getattr(alerta_proc, 'nombre_proceso', None),
                "pid": getattr(alerta_proc, 'pid', None),
                "tipo_amenaza": getattr(alerta_proc, 'tipo_amenaza', None),
                "riesgo": getattr(alerta_proc, 'nivel_severidad', None),
                "detalles": getattr(alerta_proc, 'detalles', None)
            }
            self.controlador_alertas.crear_alerta(
                mensaje=mensaje,
                tipo=TipoAlerta.PROCESO,
                severidad=severidad,
                fuente="PROCESOS",
                datos=datos
            )
