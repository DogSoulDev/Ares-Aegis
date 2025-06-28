import subprocess

class MotorClamAV:
    """
    Motor para escaneo de archivos usando ClamAV (clamscan).
    """
    @staticmethod
    def escanear(ruta_archivo):
        try:
            resultado = subprocess.run(['clamscan', ruta_archivo], capture_output=True, text=True, check=True)
            if "Infected files: 0" in resultado.stdout:
                return {"estado": "limpio", "salida": resultado.stdout}
            else:
                return {"estado": "infectado", "salida": resultado.stdout}
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                return {"estado": "infectado", "salida": e.stdout}
            else:
                return {"estado": "error", "salida": e.stderr}
        except FileNotFoundError:
            return {"estado": "error", "salida": "ClamAV no encontrado. Instala clamscan."}
