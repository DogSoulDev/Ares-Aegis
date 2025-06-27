
"""
Controlador para el escaneo del sistema operativo, carpetas y programas instalados.
Conecta la lógica de escaneo con la interfaz visual.
Incluye validación de entrada y comentarios aclaratorios.
"""
from antivirus_kali.nucleo.escaneo_sistema import EscaneoSistema

class ControladorEscaneoSistema:
    def __init__(self, rutas_directorios=None):
        """
        Inicializa el controlador de escaneo.
        rutas_directorios: lista de rutas a analizar (opcional)
        """
        self.escaneo = EscaneoSistema(rutas_directorios)

    def obtener_programas(self):
        """Devuelve la lista de programas instalados."""
        return self.escaneo.obtener_programas_instalados()

    def escanear_rootkits(self):
        """Ejecuta el escaneo de rootkits."""
        return self.escaneo.escanear_rootkits()

    def escanear_procesos(self):
        """Ejecuta el escaneo de procesos sospechosos."""
        return self.escaneo.escanear_procesos_sospechosos()

    def escanear_puertos(self):
        """Ejecuta el escaneo de puertos abiertos."""
        return self.escaneo.escanear_puertos_abiertos()

    def escanear_servicios(self):
        """Ejecuta el escaneo de servicios activos."""
        return self.escaneo.escanear_servicios_activos()

    def escanear_integridad(self, base_hashes):
        """
        Verifica la integridad de binarios críticos.
        base_hashes: diccionario {ruta: hash}
        """
        if not isinstance(base_hashes, dict):
            raise ValueError("base_hashes debe ser un diccionario {ruta: hash}")
        return self.escaneo.escanear_integridad_binarios(base_hashes)

    def obtener_resumen(self, base_hashes):
        """
        Obtiene un resumen general del sistema.
        base_hashes: diccionario {ruta: hash}
        """
        if not isinstance(base_hashes, dict):
            raise ValueError("base_hashes debe ser un diccionario {ruta: hash}")
        return self.escaneo.obtener_resumen(base_hashes)

    def exportar_informe(self, resumen, ruta="/tmp/informe_ares_aegis.pdf", usuario="Desconocido"):
        """
        Exporta el informe PDF profesional.
        resumen: dict de resultados
        ruta: destino del PDF
        usuario: nombre del usuario
        """
        return self.escaneo.exportar_informe(resumen, ruta, usuario=usuario)

    def exportar_informe_markdown(self, resumen, recomendaciones=None, ruta=None):
        """
        Exporta el informe en formato Markdown profesional.
        resumen: dict de resultados
        recomendaciones: lista de strings
        ruta: destino del archivo .md
        """
        from antivirus_kali.utils.resumen import exportar_markdown
        return exportar_markdown(resumen, recomendaciones, ruta)

    def exportar_informe_txt(self, resumen, recomendaciones=None, ruta=None):
        """
        Exporta el informe en formato texto plano profesional.
        resumen: dict de resultados
        recomendaciones: lista de strings
        ruta: destino del archivo .txt
        """
        from antivirus_kali.utils.resumen import exportar_txt
        return exportar_txt(resumen, recomendaciones, ruta)
