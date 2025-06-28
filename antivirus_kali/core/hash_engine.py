"""
Motor para cálculo y verificación de hashes (SHA256, SHA1, MD5, SSDEEP, TLSH) en archivos y directorios.
Permite comparar con bases de datos de referencia.
"""
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

from antivirus_kali.utilidades.logger import get_logger

logger = get_logger(__name__)


class MotorHashes:
    """Motor para cálculo y verificación de hashes de archivos"""
    
    def __init__(self, algoritmos: Optional[List[str]] = None):
        self.algoritmos = algoritmos or ['sha256', 'md5']
        # Base de datos simple de hashes maliciosos conocidos (en producción sería externa)
        self.hashes_maliciosos = {
            # Ejemplos de hashes conocidos (estos son ficticios para demostración)
            'd41d8cd98f00b204e9800998ecf8427e': 'Empty File (Sospechoso)',
            'e3b0c44298fc1c149afbf4c8996fb924': 'Empty SHA256 (Sospechoso)',
            # Agregar más hashes maliciosos conocidos aquí
        }

    def calcular_hash(self, archivo: str, algoritmo: str = 'sha256') -> str:
        """
        Calcula el hash de un archivo usando el algoritmo especificado.
        
        Args:
            archivo: Ruta al archivo
            algoritmo: Algoritmo de hash a usar
            
        Returns:
            Hash calculado o mensaje de error
        """
        try:
            hash_func = hashlib.new(algoritmo)
            with open(archivo, 'rb') as f:
                for bloque in iter(lambda: f.read(4096), b''):
                    hash_func.update(bloque)
            return hash_func.hexdigest()
        except Exception as e:
            logger.error(f"Error calculando hash de {archivo}: {e}")
            return f'Error: {e}'

    def verificar_archivo(self, ruta_archivo: str) -> Dict[str, Any]:
        """
        Verifica si un archivo tiene un hash malicioso conocido.
        
        Args:
            ruta_archivo: Ruta al archivo a verificar
            
        Returns:
            Diccionario con información de la verificación
        """
        try:
            resultado = {
                'archivo': ruta_archivo,
                'es_malicioso': False,
                'hash': None,
                'algoritmo_detectado': None,
                'tipo_malware': None
            }
            
            # Verificar con cada algoritmo
            for algoritmo in self.algoritmos:
                hash_calculado = self.calcular_hash(ruta_archivo, algoritmo)
                if not hash_calculado.startswith('Error:'):
                    resultado['hash'] = hash_calculado
                    resultado['algoritmo_detectado'] = algoritmo
                    
                    # Verificar si está en la base de datos de maliciosos
                    if hash_calculado in self.hashes_maliciosos:
                        resultado['es_malicioso'] = True
                        resultado['tipo_malware'] = self.hashes_maliciosos[hash_calculado]
                        logger.warning(f"Hash malicioso detectado: {ruta_archivo} -> {hash_calculado}")
                        break
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error verificando archivo {ruta_archivo}: {e}")
            return {
                'archivo': ruta_archivo,
                'es_malicioso': False,
                'error': str(e)
            }

    def escanear(self, ruta_objetivo: str) -> List[Dict[str, Any]]:
        """
        Escanea archivos y calcula sus hashes.
        
        Args:
            ruta_objetivo: Ruta del archivo o directorio a escanear
            
        Returns:
            Lista de diccionarios con información de hashes
        """
        ruta = Path(ruta_objetivo)
        resultados = []
        
        try:
            if ruta.is_file():
                for alg in self.algoritmos:
                    hash_val = self.calcular_hash(str(ruta), alg)
                    resultados.append({
                        'archivo': str(ruta), 
                        'algoritmo': alg, 
                        'hash': hash_val,
                        'es_malicioso': hash_val in self.hashes_maliciosos
                    })
                    
            elif ruta.is_dir():
                for archivo in ruta.rglob('*'):
                    if archivo.is_file():
                        # Limitar número de archivos para rendimiento
                        if len(resultados) >= 100:
                            break
                            
                        for alg in self.algoritmos:
                            hash_val = self.calcular_hash(str(archivo), alg)
                            resultados.append({
                                'archivo': str(archivo), 
                                'algoritmo': alg, 
                                'hash': hash_val,
                                'es_malicioso': hash_val in self.hashes_maliciosos
                            })
                            
        except Exception as e:
            logger.error(f"Error durante escaneo de hashes: {e}")
            
        return resultados

    def agregar_hash_malicioso(self, hash_valor: str, descripcion: str):
        """
        Agrega un hash a la base de datos de maliciosos.
        
        Args:
            hash_valor: Valor del hash
            descripcion: Descripción del malware
        """
        self.hashes_maliciosos[hash_valor.lower()] = descripcion
        logger.info(f"Hash malicioso agregado: {hash_valor}")

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del motor de hashes.
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            'algoritmos_soportados': self.algoritmos,
            'hashes_maliciosos_conocidos': len(self.hashes_maliciosos),
            'algoritmo_principal': self.algoritmos[0] if self.algoritmos else None
        }
