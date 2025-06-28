from .clamav_engine import MotorClamAV
from .yara_engine import MotorYARA
from .threat_intel import InteligenciaAmenazas
from .hash_db import BaseDatosHashes

class MotorEscaneo:
    def __init__(self, ruta_reglas_yara=None, base_hashes=None):
        self.ruta_reglas_yara = ruta_reglas_yara
        self.base_hashes = base_hashes or BaseDatosHashes()

    def escanear_archivo(self, ruta_archivo):
        resultados = {}
        resultados['clamav'] = MotorClamAV.escanear(ruta_archivo)
        if self.ruta_reglas_yara:
            resultados['yara'] = MotorYARA.escanear(ruta_archivo, self.ruta_reglas_yara)
        resultados['hashes'] = self.base_hashes.comprobar_archivo(ruta_archivo)
        # Puedes añadir más motores aquí
        return resultados
