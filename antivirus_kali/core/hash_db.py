import hashlib

class BaseDatosHashes:
    def __init__(self, conjunto_hashes=None):
        self.conjunto_hashes = set(conjunto_hashes) if conjunto_hashes else set()

    def agregar_hash(self, hash_valor):
        self.conjunto_hashes.add(hash_valor)

    def comprobar_archivo(self, ruta_archivo, algoritmo='sha256'):
        h = hashlib.new(algoritmo)
        try:
            with open(ruta_archivo, 'rb') as f:
                while trozo := f.read(8192):
                    h.update(trozo)
            return h.hexdigest() in self.conjunto_hashes
        except Exception:
            return False
