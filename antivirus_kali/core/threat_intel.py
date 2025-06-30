import requests

class InteligenciaAmenazas:
    """
    Clase para obtener indicadores de compromiso (IOCs) de feeds públicos.
    """
    @staticmethod
    def obtener_hashes_urlhaus():
        url = "https://urlhaus.abuse.ch/downloads/csv_online/"
        try:
            respuesta = requests.get(url)
            respuesta.raise_for_status()
            lineas = respuesta.text.splitlines()
            hashes = []
            for linea in lineas:
                if not linea.startswith("#"):
                    partes = linea.split(",")
                    if len(partes) > 2:
                        hashes.append(partes[2].strip())
            return hashes
        except requests.exceptions.RequestException:
            return []
