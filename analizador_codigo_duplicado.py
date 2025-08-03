#!/usr/bin/env python3
"""
Analizador de código duplicado para Ares Aegis
FASE 1: Identificación de duplicaciones y problemas estructurales
"""

import os
import re
import hashlib
from collections import defaultdict
from pathlib import Path

class AnalizadorCodigoDuplicado:
    """Analizador para identificar código duplicado y problemas estructurales"""
    
    def __init__(self, directorio_proyecto):
        self.directorio = Path(directorio_proyecto)
        self.archivos_python = []
        self.duplicaciones = {
            'imports': defaultdict(list),
            'clases': defaultdict(list),
            'metodos': defaultdict(list),
            'patrones_comunes': defaultdict(list)
        }
        self.problemas_estructurales = []
        
    def analizar_proyecto(self):
        """Análisis completo del proyecto"""
        print("🔍 FASE 1: AUDITORÍA DE CÓDIGO DUPLICADO")
        print("=" * 60)
        
        # 1. Recopilar archivos Python
        self._recopilar_archivos()
        
        # 2. Analizar imports duplicados
        self._analizar_imports()
        
        # 3. Analizar clases similares
        self._analizar_clases()
        
        # 4. Analizar métodos duplicados
        self._analizar_metodos()
        
        # 5. Detectar patrones estructurales
        self._detectar_patrones_estructurales()
        
        # 6. Generar reporte
        self._generar_reporte()
        
    def _recopilar_archivos(self):
        """Recopilar todos los archivos Python del proyecto"""
        for ruta in self.directorio.rglob("*.py"):
            if "__pycache__" not in str(ruta):
                self.archivos_python.append(ruta)
        
        print(f"📁 Archivos Python encontrados: {len(self.archivos_python)}")
    
    def _analizar_imports(self):
        """Identificar imports duplicados y redundantes"""
        print("\n🔸 Analizando imports...")
        
        import_patterns = defaultdict(list)
        
        for archivo in self.archivos_python:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    
                # Buscar imports
                imports = re.findall(r'^(import .+|from .+ import .+)$', contenido, re.MULTILINE)
                
                for imp in imports:
                    import_patterns[imp].append(str(archivo))
                    
            except Exception as e:
                continue
        
        # Identificar imports comunes (posibles candidatos para consolidación)
        for imp, archivos in import_patterns.items():
            if len(archivos) >= 3:  # Aparece en 3 o más archivos
                self.duplicaciones['imports'][imp] = archivos
    
    def _analizar_clases(self):
        """Identificar clases con patrones similares"""
        print("🔸 Analizando estructuras de clases...")
        
        patrones_clases = defaultdict(list)
        
        for archivo in self.archivos_python:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    
                # Buscar definiciones de clases y sus métodos
                clases = re.findall(r'class\s+(\w+).*?:', contenido)
                metodos_init = re.findall(r'def\s+__init__\(self[^)]*\):', contenido)
                metodos_mostrar_info = re.findall(r'def\s+mostrar_informacion\(', contenido)
                
                # Crear firma de la clase
                firma_clase = {
                    'archivo': str(archivo),
                    'clases': clases,
                    'tiene_init': len(metodos_init) > 0,
                    'tiene_mostrar_info': len(metodos_mostrar_info) > 0,
                    'num_metodos': len(re.findall(r'def\s+\w+\(', contenido))
                }
                
                # Agrupar por patrones similares
                if clases:
                    patron_key = f"clases_{len(clases)}_init_{firma_clase['tiene_init']}_info_{firma_clase['tiene_mostrar_info']}"
                    patrones_clases[patron_key].append(firma_clase)
                    
            except Exception as e:
                continue
        
        # Identificar patrones duplicados
        for patron, archivos in patrones_clases.items():
            if len(archivos) >= 3:
                self.duplicaciones['clases'][patron] = archivos
    
    def _analizar_metodos(self):
        """Identificar métodos duplicados o muy similares"""
        print("🔸 Analizando métodos duplicados...")
        
        metodos_comunes = [
            'mostrar_informacion',
            '__init__',
            'crear_vista',
            'crear_interfaz',
            'actualizar_datos',
            'limpiar_pantalla'
        ]
        
        for metodo in metodos_comunes:
            archivos_con_metodo = []
            
            for archivo in self.archivos_python:
                try:
                    with open(archivo, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                        
                    if f'def {metodo}(' in contenido:
                        archivos_con_metodo.append(str(archivo))
                        
                except Exception as e:
                    continue
            
            if len(archivos_con_metodo) >= 3:
                self.duplicaciones['metodos'][metodo] = archivos_con_metodo
    
    def _detectar_patrones_estructurales(self):
        """Detectar problemas estructurales en el código"""
        print("🔸 Detectando problemas estructurales...")
        
        for archivo in self.archivos_python:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    lineas = contenido.split('\n')
                
                # Verificar problemas comunes
                problemas_archivo = []
                
                # 1. Imports al final del archivo
                import_lineas = [i for i, linea in enumerate(lineas) if 'import ' in linea]
                if import_lineas:
                    ultimo_import = max(import_lineas)
                    if ultimo_import > 20:  # Imports después de línea 20
                        problemas_archivo.append("Imports tardíos detectados")
                
                # 2. Clases muy largas (más de 500 líneas)
                if len(lineas) > 500:
                    problemas_archivo.append(f"Archivo muy largo: {len(lineas)} líneas")
                
                # 3. Métodos muy largos
                metodos_largos = re.findall(r'def\s+\w+\([^)]*\):.*?(?=def\s|\nclass\s|\Z)', contenido, re.DOTALL)
                for metodo in metodos_largos:
                    if len(metodo.split('\n')) > 50:
                        problemas_archivo.append("Método muy largo detectado")
                        break
                
                # 4. Imports duplicados en el mismo archivo
                imports_unicos = set()
                imports_duplicados = []
                for linea in lineas:
                    if linea.strip().startswith(('import ', 'from ')):
                        if linea.strip() in imports_unicos:
                            imports_duplicados.append(linea.strip())
                        imports_unicos.add(linea.strip())
                
                if imports_duplicados:
                    problemas_archivo.append(f"Imports duplicados: {len(imports_duplicados)}")
                
                if problemas_archivo:
                    self.problemas_estructurales.append({
                        'archivo': str(archivo),
                        'problemas': problemas_archivo
                    })
                    
            except Exception as e:
                continue
    
    def _generar_reporte(self):
        """Generar reporte completo de la auditoría"""
        print("\n" + "=" * 60)
        print("📋 REPORTE DE AUDITORÍA - CÓDIGO DUPLICADO")
        print("=" * 60)
        
        # Resumen ejecutivo
        total_duplicaciones = (
            len(self.duplicaciones['imports']) +
            len(self.duplicaciones['clases']) +
            len(self.duplicaciones['metodos'])
        )
        
        print(f"\n🎯 RESUMEN EJECUTIVO:")
        print(f"   📁 Archivos analizados: {len(self.archivos_python)}")
        print(f"   🔄 Duplicaciones encontradas: {total_duplicaciones}")
        print(f"   ⚠️  Problemas estructurales: {len(self.problemas_estructurales)}")
        
        # Imports duplicados
        if self.duplicaciones['imports']:
            print(f"\n📦 IMPORTS DUPLICADOS ({len(self.duplicaciones['imports'])}):")
            for imp, archivos in list(self.duplicaciones['imports'].items())[:5]:
                print(f"   🔸 '{imp}' aparece en {len(archivos)} archivos")
                for archivo in archivos[:3]:
                    archivo_corto = archivo.split('ares_aegis')[-1] if 'ares_aegis' in archivo else archivo
                    print(f"      - ...{archivo_corto}")
                if len(archivos) > 3:
                    print(f"      - ...y {len(archivos)-3} más")
        
        # Patrones de clases duplicadas
        if self.duplicaciones['clases']:
            print(f"\n🏗️  PATRONES DE CLASES SIMILARES ({len(self.duplicaciones['clases'])}):")
            for patron, archivos in self.duplicaciones['clases'].items():
                print(f"   🔸 Patrón '{patron}' en {len(archivos)} archivos")
                for info in archivos[:3]:
                    archivo_corto = info['archivo'].split('ares_aegis')[-1] if 'ares_aegis' in info['archivo'] else info['archivo']
                    print(f"      - ...{archivo_corto}: {info['clases']}")
        
        # Métodos duplicados
        if self.duplicaciones['metodos']:
            print(f"\n🔧 MÉTODOS COMUNES ({len(self.duplicaciones['metodos'])}):")
            for metodo, archivos in self.duplicaciones['metodos'].items():
                print(f"   🔸 '{metodo}' aparece en {len(archivos)} archivos")
        
        # Problemas estructurales
        if self.problemas_estructurales:
            print(f"\n⚠️  PROBLEMAS ESTRUCTURALES ({len(self.problemas_estructurales)}):")
            for problema in self.problemas_estructurales[:5]:
                archivo_corto = problema['archivo'].split('ares_aegis')[-1] if 'ares_aegis' in problema['archivo'] else problema['archivo']
                print(f"   🔸 ...{archivo_corto}:")
                for p in problema['problemas']:
                    print(f"      - {p}")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES PRIORITARIAS:")
        print("   1. 🔗 Crear clase base Vista común para todas las vistas")
        print("   2. 📦 Consolidar imports comunes en módulo utilitario")
        print("   3. 🏗️  Refactorizar métodos mostrar_informacion duplicados")
        print("   4. 🧹 Separar archivos largos en módulos más pequeños")
        print("   5. 📋 Crear interfaces comunes para controladores")
        
        return {
            'duplicaciones': self.duplicaciones,
            'problemas_estructurales': self.problemas_estructurales,
            'total_archivos': len(self.archivos_python),
            'total_duplicaciones': total_duplicaciones
        }

if __name__ == "__main__":
    # Ejecutar análisis
    analizador = AnalizadorCodigoDuplicado(".")
    resultados = analizador.analizar_proyecto()
