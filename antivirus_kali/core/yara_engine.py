import yara

class MotorYARA:
    """
    Motor para escaneo de archivos usando reglas YARA.
    """
    @staticmethod
    def escanear(ruta_archivo, ruta_reglas):
        try:
            reglas = yara.compile(filepath=ruta_reglas)
            coincidencias = reglas.match(filepath=ruta_archivo)
            if coincidencias:
                return {"estado": "coincidencia", "coincidencias": coincidencias}
            else:
                return {"estado": "limpio", "coincidencias": []}
        except yara.Error as e:
            return {"estado": "error", "salida": str(e)}
        except FileNotFoundError:
            return {"estado": "error", "salida": "Archivo de reglas YARA o archivo a escanear no encontrado."}
