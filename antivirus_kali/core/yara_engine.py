
import yara
from pathlib import Path

class MotorYARA:
    """
    Motor profesional para escaneo de archivos y directorios usando reglas YARA.
    Permite cargar reglas y escanear objetivos de forma eficiente.
    """
    def __init__(self, archivo_reglas):
        self.archivo_reglas = archivo_reglas
        self.reglas = None
        self.cargar_reglas()

    def cargar_reglas(self):
        if Path(self.archivo_reglas).exists():
            self.reglas = yara.compile(filepath=self.archivo_reglas)
        else:
            self.reglas = None

    def escanear(self, ruta_objetivo):
        """
        Escanea un archivo o directorio usando las reglas YARA cargadas.
        """
        if not self.reglas:
            return {'error': 'No se han cargado reglas YARA.'}
        ruta = Path(ruta_objetivo)
        if not ruta.exists():
            return {'error': f'Ruta no encontrada: {ruta_objetivo}'}
        resultados = []
        if ruta.is_file():
            matches = self.reglas.match(filepath=str(ruta))
            for match in matches:
                resultados.append({'archivo': str(ruta), 'regla': match.rule, 'tags': match.tags, 'meta': match.meta})
        elif ruta.is_dir():
            for archivo in ruta.rglob('*'):
                if archivo.is_file():
                    matches = self.reglas.match(filepath=str(archivo))
                    for match in matches:
                        resultados.append({'archivo': str(archivo), 'regla': match.rule, 'tags': match.tags, 'meta': match.meta})
        return {'coincidencias': resultados, 'total': len(resultados)}
