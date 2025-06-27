"""
Módulo para la validación de integridad de herramientas de Kali Linux.
Descarga y compara hashes oficiales de binarios críticos, explica resultados y recomienda acciones.
"""

import os
import hashlib
import requests

class ValidadorIntegridad:
    def __init__(self, rutas_herramientas, referencia_hashes=None, url_hashes=None):
        """
        rutas_herramientas: lista de rutas a binarios a validar
        referencia_hashes: diccionario {ruta: hash} (opcional)
        url_hashes: url de hashes oficiales de Kali (opcional)
        """
        self.rutas_herramientas = rutas_herramientas
        self.referencia_hashes = referencia_hashes or {}
        self.url_hashes = url_hashes or "https://http.kali.org/pool/main/k/kali-archive-keyring/SHA256SUMS"

    def descargar_hashes_oficiales(self):
        try:
            respuesta = requests.get(self.url_hashes, timeout=10)
            if respuesta.status_code == 200:
                hashes = {}
                for linea in respuesta.text.splitlines():
                    partes = linea.strip().split()
                    if len(partes) == 2:
                        hash_val, ruta = partes
                        hashes[ruta] = hash_val
                self.referencia_hashes.update(hashes)
                return True
            return False
        except Exception:
            return False

    def calcular_hash(self, ruta, algoritmo='sha256'):
        try:
            hash_func = hashlib.new(algoritmo)
            with open(ruta, 'rb') as f:
                for bloque in iter(lambda: f.read(4096), b''):
                    hash_func.update(bloque)
            return hash_func.hexdigest()
        except Exception:
            return None

    def validar(self):
        advertencias = []
        if not self.referencia_hashes:
            exito = self.descargar_hashes_oficiales()
            if not exito:
                advertencias.append("No se pudieron descargar los hashes oficiales de Kali. Verifique su conexión o intente más tarde.")
        resultados = {}
        for ruta in self.rutas_herramientas:
            if not os.path.exists(ruta):
                resultados[ruta] = 'No encontrado. Reinstale el paquete.'
                continue
            hash_actual = self.calcular_hash(ruta)
            hash_referencia = self.referencia_hashes.get(os.path.basename(ruta))
            if hash_referencia is None:
                resultados[ruta] = 'Sin referencia oficial. Verifique manualmente.'
                advertencias.append(f"No hay hash oficial para {ruta}. Revise manualmente.")
            elif hash_actual == hash_referencia:
                resultados[ruta] = 'Íntegro. Coincide con el hash oficial de Kali.'
            else:
                resultados[ruta] = 'Modificado. RIESGO: El binario no coincide con el oficial. Reinstale o investigue.'
        return resultados, advertencias
