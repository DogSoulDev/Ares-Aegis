#!/usr/bin/env python3
"""
Gestor de Cheatsheets para Ares Aegis
Sistema de gestión de hojas de trucos integrado
"""

import json
import logging
from pathlib import Path


class GestorCheatsheets:
    """Gestor de cheatsheets integrado para consulta rápida"""
    
    def __init__(self, ruta_base_cheatsheets):
        self.ruta_base = Path(ruta_base_cheatsheets)
        self.logger = logging.getLogger(__name__)
        self.cheatsheets_cargados = {}
        self._cargar_indice()
    
    def _cargar_indice(self):
        """Cargar índice de cheatsheets disponibles"""
        try:
            archivo_indice = self.ruta_base / "indice.json"
            if archivo_indice.exists():
                with open(archivo_indice, 'r', encoding='utf-8') as f:
                    self.indice = json.load(f)
                self.logger.info(f"📚 Índice de cheatsheets cargado: {len(self.indice.get('cheatsheets', {}))} disponibles")
            else:
                self.indice = {"cheatsheets": {}}
                self.logger.warning("⚠️ No se encontró índice de cheatsheets")
        except Exception as e:
            self.logger.error(f"Error cargando índice de cheatsheets: {e}")
            self.indice = {"cheatsheets": {}}
    
    def obtener_cheatsheet(self, nombre):
        """Obtener contenido de un cheatsheet específico"""
        if nombre in self.cheatsheets_cargados:
            return self.cheatsheets_cargados[nombre]
        
        try:
            cheatsheet_info = self.indice["cheatsheets"].get(nombre)
            if not cheatsheet_info:
                return None
            
            archivo = cheatsheet_info.get("archivo", cheatsheet_info.get("ruta"))
            ruta_archivo = self.ruta_base / archivo
            
            if ruta_archivo.exists():
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    if archivo.endswith('.json'):
                        contenido = json.load(f)
                    else:
                        contenido = f.read()
                
                self.cheatsheets_cargados[nombre] = contenido
                return contenido
            else:
                self.logger.warning(f"⚠️ Archivo cheatsheet no encontrado: {ruta_archivo}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error cargando cheatsheet {nombre}: {e}")
            return None
    
    def listar_cheatsheets(self):
        """Obtener lista de cheatsheets disponibles"""
        return self.indice.get("cheatsheets", {})
