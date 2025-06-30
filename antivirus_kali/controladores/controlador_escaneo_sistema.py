

"""
Controlador profesional para el análisis de sistema.
Orquesta los motores de ClamAV, YARA, rootkits y hashes, y expone métodos para la interfaz.
"""
from antivirus_kali.core.scan_engine import MotorEscaneo

class ControladorEscaneoSistema:
    def __init__(self, reglas_yara=None, algoritmos_hash=None, herramienta_rootkits='rkhunter'):
        self.motor = MotorEscaneo(reglas_yara, algoritmos_hash, herramienta_rootkits)

    def escanear_todo(self, ruta_objetivo):
        """
        Ejecuta todos los motores y devuelve un resumen profesional.
        """
        return self.motor.resumen_profesional(ruta_objetivo)

    def escanear_clamav(self, ruta_objetivo):
        return self.motor.clamav.escanear(ruta_objetivo)

    def escanear_yara(self, ruta_objetivo):
        if self.motor.yara:
            return self.motor.yara.escanear(ruta_objetivo)
        return {'error': 'No hay reglas YARA configuradas.'}

    def escanear_rootkits(self):
        return self.motor.rootkits.escanear()

    def escanear_hashes(self, ruta_objetivo):
        return self.motor.hashes.escanear(ruta_objetivo)
