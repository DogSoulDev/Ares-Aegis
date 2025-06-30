
import subprocess
from pathlib import Path

class MotorClamAV:
    """
    Motor profesional para escaneo de archivos y directorios usando ClamAV (clamscan).
    Permite parsear resultados y obtener versión.
    """
    def __init__(self, ruta_clamscan='clamscan'):
        self.ruta_clamscan = ruta_clamscan

    def escanear(self, ruta_objetivo):
        """
        Ejecuta clamscan sobre un archivo o directorio y devuelve un resumen estructurado.
        """
        if not Path(ruta_objetivo).exists():
            return {'error': f'Ruta no encontrada: {ruta_objetivo}'}
        try:
            resultado = subprocess.run([
                self.ruta_clamscan,
                '--infected',
                '--recursive',
                '--no-summary',
                ruta_objetivo
            ], capture_output=True, text=True, check=False)
            infectados = []
            for linea in resultado.stdout.splitlines():
                if ': ' in linea:
                    archivo, estado = linea.split(': ', 1)
                    if estado.strip().upper() != 'OK':
                        infectados.append({'archivo': archivo.strip(), 'amenaza': estado.strip()})
            return {
                'infectados': infectados,
                'total_infectados': len(infectados),
                'salida': resultado.stdout,
                'codigo_retorno': resultado.returncode
            }
        except Exception as e:
            return {'error': str(e)}

    def version(self):
        try:
            resultado = subprocess.run([self.ruta_clamscan, '--version'], capture_output=True, text=True, check=False)
            return resultado.stdout.strip()
        except Exception as e:
            return f'Error obteniendo versión de ClamAV: {e}'
