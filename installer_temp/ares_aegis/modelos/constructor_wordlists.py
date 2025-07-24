#!/usr/bin/env python3
"""
Constructor de Wordlists para Ares Aegis
Sistema simplificado para generar y manejar wordlists
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
from ..utils.ayuda_logging import configurar_logger_modulo


class ConstructorWordlists:
    """
    Constructor de Wordlists Simplificado para Ares Aegis
    
    Características:
    - Gestión de listas base de palabras
    - Generación de combinaciones
    - Aplicación de mutaciones y filtros
    - Exportación de wordlists
    """
    
    def __init__(self):
        """Inicializar el constructor de wordlists"""
        self.logger = configurar_logger_modulo('constructor_wordlists')
        
        # Configurar directorios
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.directorio_datos = os.path.join(base_dir, 'data', 'wordlists')
        os.makedirs(self.directorio_datos, exist_ok=True)
        
        # Archivos de configuración
        self.archivo_listas_base = os.path.join(self.directorio_datos, 'listas_base.json')
        
        # Cargar datos
        self.listas_base = self._cargar_json(self.archivo_listas_base, {})
        self._cargar_wordlists_descargadas()
        
        self.logger.info('Constructor de Wordlists inicializado')
    
    def _cargar_json(self, archivo, default):
        """Cargar archivo JSON con manejo de errores"""
        try:
            if os.path.exists(archivo) and os.path.getsize(archivo) > 0:
                with open(archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f'Error cargando {archivo}: {e}')
        return default
    
    def _guardar_json(self, datos, archivo):
        """Guardar datos en archivo JSON"""
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False, sort_keys=True)
            return True
        except Exception as e:
            self.logger.error(f'Error guardando {archivo}: {e}')
            return False
    
    def _cargar_wordlists_descargadas(self):
        """Cargar wordlists desde archivos .txt en el directorio"""
        try:
            wordlists_cargadas = 0
            for archivo in os.listdir(self.directorio_datos):
                if archivo.endswith('.txt') and not archivo.startswith('.'):
                    ruta_completa = os.path.join(self.directorio_datos, archivo)
                    if os.path.isfile(ruta_completa):
                        nombre_lista = archivo.replace('.txt', '')
                        if nombre_lista not in self.listas_base:
                            try:
                                with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
                                    palabras = [linea.strip() for linea in f if linea.strip() and not linea.startswith('#')]
                                
                                # Limitar tamaño para evitar memoria excesiva
                                if len(palabras) > 10000:
                                    palabras = palabras[:10000]
                                
                                if palabras:
                                    self.listas_base[nombre_lista] = palabras
                                    wordlists_cargadas += 1
                                    self.logger.info(f'Wordlist cargada: {nombre_lista} ({len(palabras)} palabras)')
                            except Exception as e:
                                self.logger.warning(f'Error cargando {archivo}: {e}')
            
            if wordlists_cargadas > 0:
                self._guardar_json(self.listas_base, self.archivo_listas_base)
                self.logger.info(f'{wordlists_cargadas} wordlists cargadas automáticamente')
                
        except Exception as e:
            self.logger.error(f'Error cargando wordlists: {e}')
    
    def obtener_listas_base(self):
        """Obtener todas las listas base disponibles"""
        return self.listas_base.copy()
    
    def obtener_nombres_listas_base(self):
        """Obtener nombres de las listas base"""
        return list(self.listas_base.keys())
    
    def crear_lista_base(self, nombre, palabras):
        """Crear una nueva lista base"""
        try:
            palabras_limpias = list(set([p.strip() for p in palabras if p.strip()]))
            self.listas_base[nombre] = palabras_limpias
            
            if self._guardar_json(self.listas_base, self.archivo_listas_base):
                self.logger.info(f'Lista base {nombre} creada con {len(palabras_limpias)} palabras')
                return True
            return False
        except Exception as e:
            self.logger.error(f'Error creando lista base: {e}')
            return False
    
    def generar_combinaciones(self, listas_nombres, tipo='concatenacion'):
        """Generar combinaciones de palabras de diferentes listas"""
        try:
            if tipo == 'concatenacion':
                resultado = []
                for nombre in listas_nombres:
                    if nombre in self.listas_base:
                        resultado.extend(self.listas_base[nombre])
                return list(set(resultado))  # Eliminar duplicados
            return []
        except Exception as e:
            self.logger.error(f'Error generando combinaciones: {e}')
            return []
    
    def aplicar_mutaciones(self, palabras, opciones):
        """Aplicar mutaciones a las palabras"""
        try:
            resultado = list(palabras)
            
            for palabra in palabras:
                if opciones.get('mayusculas'):
                    resultado.append(palabra.upper())
                if opciones.get('minusculas'):
                    resultado.append(palabra.lower())
                if opciones.get('capitalizar'):
                    resultado.append(palabra.capitalize())
                if opciones.get('numeros'):
                    for i in range(10):
                        resultado.append(f"{palabra}{i}")
                if opciones.get('reverso'):
                    resultado.append(palabra[::-1])
                if opciones.get('duplicar'):
                    resultado.append(palabra + palabra)
            
            return list(set(resultado))  # Eliminar duplicados
        except Exception as e:
            self.logger.error(f'Error aplicando mutaciones: {e}')
            return palabras
    
    def aplicar_filtros(self, palabras, filtros):
        """Aplicar filtros a las palabras"""
        try:
            resultado = []
            min_len = filtros.get('min_len', 0)
            max_len = filtros.get('max_len', 999)
            contiene = filtros.get('contiene', '')
            no_contiene = filtros.get('no_contiene', '')
            
            for palabra in palabras:
                # Filtrar por longitud
                if len(palabra) < min_len or len(palabra) > max_len:
                    continue
                
                # Filtrar por contenido
                if contiene and contiene not in palabra:
                    continue
                if no_contiene and no_contiene in palabra:
                    continue
                
                resultado.append(palabra)
            
            return resultado
        except Exception as e:
            self.logger.error(f'Error aplicando filtros: {e}')
            return palabras
    
    def exportar_wordlist(self, palabras, nombre_archivo):
        """Exportar la wordlist a un archivo"""
        try:
            # Crear directorio de generadas si no existe
            directorio_generadas = os.path.join(self.directorio_datos, 'generadas')
            os.makedirs(directorio_generadas, exist_ok=True)
            
            archivo_path = os.path.join(directorio_generadas, f'{nombre_archivo}.txt')
            
            with open(archivo_path, 'w', encoding='utf-8') as f:
                for palabra in palabras:
                    f.write(f'{palabra}\n')
            
            self.logger.info(f'Wordlist exportada: {archivo_path}')
            return True
        except Exception as e:
            self.logger.error(f'Error exportando wordlist: {e}')
            return False
    
    # Métodos adicionales para compatibilidad
    def obtener_recetas(self):
        """Obtiene todas las recetas guardadas (método de compatibilidad)"""
        return {}
    
    def guardar_receta(self, nombre, configuracion, descripcion=""):
        """Guarda una receta de configuración (método de compatibilidad)"""
        return True
    
    def cargar_receta(self, nombre):
        """Carga una receta específica (método de compatibilidad)"""
        return {}
    
    def obtener_historial(self, limite=20):
        """Obtiene el historial de generaciones (método de compatibilidad)"""
        return []
    
    def agregar_al_historial(self, entrada):
        """Agrega una entrada al historial (método de compatibilidad)"""
        return True


# Exportar la clase
__all__ = ['ConstructorWordlists']
