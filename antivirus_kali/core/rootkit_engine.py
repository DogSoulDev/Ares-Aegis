"""
Motor para escaneo de rootkits usando rkhunter o chkrootkit desde Python.
Lanza el comando como subproceso y parsea la salida.
"""
import subprocess

class MotorRootkits:
    def __init__(self, herramienta='rkhunter'):
        self.herramienta = herramienta

    def escanear(self):
        """
        Ejecuta rkhunter o chkrootkit y devuelve los resultados parseados.
        """
        try:
            resultado = subprocess.run([
                self.herramienta,
                '--check',
                '--sk',
                '--nocolors',
                '--rwo'
            ], capture_output=True, text=True, check=False)
            hallazgos = []
            for linea in resultado.stdout.splitlines():
                if 'Warning:' in linea or 'Found:' in linea or 'INFECTED' in linea:
                    hallazgos.append(linea.strip())
            return {
                'hallazgos': hallazgos,
                'total_hallazgos': len(hallazgos),
                'salida': resultado.stdout,
                'codigo_retorno': resultado.returncode
            }
        except Exception as e:
            return {'error': str(e)}
