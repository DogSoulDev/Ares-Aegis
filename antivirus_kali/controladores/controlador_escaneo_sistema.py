"""
Controlador para el escaneo del sistema operativo, carpetas y programas instalados.
Conecta la lógica de escaneo con la interfaz visual.
"""
from antivirus_kali.nucleo.escaneo_sistema import EscaneoSistema


class ControladorEscaneoSistema:
    def __init__(self, rutas_directorios=None):
        self.escaneo = EscaneoSistema(rutas_directorios)

    def obtener_programas(self):
        return self.escaneo.obtener_programas_instalados()

    def escanear_rootkits(self):
        return self.escaneo.escanear_rootkits()

    def escanear_procesos(self):
        return self.escaneo.escanear_procesos_sospechosos()

    def escanear_puertos(self):
        return self.escaneo.escanear_puertos_abiertos()

    def escanear_servicios(self):
        return self.escaneo.escanear_servicios_activos()

    def escanear_integridad(self, base_hashes):
        return self.escaneo.escanear_integridad_binarios(base_hashes)

    def obtener_resumen(self, base_hashes):
        return self.escaneo.obtener_resumen(base_hashes)

    def exportar_informe(self, resumen, ruta="/tmp/informe_ares_aegis.pdf", usuario="Desconocido"):
        return self.escaneo.exportar_informe(resumen, ruta, usuario=usuario)
