from .controlador_alertas import ControladorAlertas
from .controlador_alertas_fim import ControladorAlertasFIM
from .controlador_alertas_procesos import ControladorAlertasProcesos
from .controlador_alertas_red_comportamiento import ControladorAlertasRedComportamiento
from .controlador_alertas_siem import ControladorAlertasSIEM

class OrquestadorAlertas:
    """Orquestador central para ejecutar todos los controladores de integración de alertas de manera eficiente."""
    def __init__(self, controladores: dict):
        """
        controladores: dict con claves ('fim', 'procesos', 'red', 'siem') y valores instancias de controladores
        """
        self.controladores = controladores

    def ejecutar_todos(self):
        """Ejecuta todos los controladores de integración de alertas registrados."""
        if 'fim' in self.controladores:
            self.controladores['fim'].verificar_integridad()
        if 'procesos' in self.controladores:
            self.controladores['procesos'].verificar_alertas_procesos()
        if 'red' in self.controladores:
            self.controladores['red'].verificar_alertas_red()
        if 'siem' in self.controladores:
            self.controladores['siem'].verificar_eventos_siem()

    def ejecutar(self, clave):
        """Ejecuta un controlador específico por clave ('fim', 'procesos', 'red', 'siem')."""
        if clave in self.controladores:
            metodo = {
                'fim': 'verificar_integridad',
                'procesos': 'verificar_alertas_procesos',
                'red': 'verificar_alertas_red',
                'siem': 'verificar_eventos_siem'
            }.get(clave)
            if metodo and hasattr(self.controladores[clave], metodo):
                getattr(self.controladores[clave], metodo)()
