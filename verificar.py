#!/usr/bin/env python3
"""
Script de verificación final para Ares Aegis
Confirma que no hay dependencias externas y todo está limpio
"""

import os
import sys
import ast
import subprocess
from pathlib import Path

# Dependencias externas a buscar
DEPENDENCIAS_PROHIBIDAS = {
    'psutil', 'PIL', 'PyQt5', 'PyQt6', 'requests', 
    'numpy', 'pandas', 'matplotlib', 'opencv-cv2',
    'selenium', 'beautifulsoup4', 'lxml'
}

def verificar_imports_archivo(archivo_path):
    """Verificar imports en un archivo Python"""
    dependencias_encontradas = set()
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Parsear el AST para encontrar imports
        tree = ast.parse(contenido)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    modulo = alias.name.split('.')[0]
                    if modulo in DEPENDENCIAS_PROHIBIDAS:
                        dependencias_encontradas.add(modulo)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    modulo = node.module.split('.')[0]
                    if modulo in DEPENDENCIAS_PROHIBIDAS:
                        dependencias_encontradas.add(modulo)
    
    except Exception as e:
        print(f"⚠️  Error analizando {archivo_path}: {e}")
    
    return dependencias_encontradas

def verificar_pip_list():
    """Verificar que no hay paquetes externos instalados"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=freeze'], 
                              capture_output=True, text=True, check=True)
        
        paquetes = []
        for linea in result.stdout.strip().split('\n'):
            if '==' in linea:
                paquete = linea.split('==')[0].lower()
                if paquete != 'pip':
                    paquetes.append(paquete)
        
        return paquetes
    except Exception as e:
        print(f"⚠️  Error verificando pip list: {e}")
        return []

def main():
    """Función principal de verificación"""
    print("🔍 Iniciando verificación final de Ares Aegis...")
    print("=" * 60)
    
    # Verificar estructura del proyecto
    proyecto_root = Path(__file__).parent
    archivos_python = list(proyecto_root.rglob("*.py"))
    archivos_proyecto = [f for f in archivos_python if '.venv' not in str(f) and '__pycache__' not in str(f)]
    
    print(f"📁 Archivos Python encontrados: {len(archivos_proyecto)}")
    
    # Verificar imports en cada archivo
    print("\n🔍 Verificando imports...")
    dependencias_encontradas = set()
    archivos_problematicos = []
    
    for archivo in archivos_proyecto:
        deps = verificar_imports_archivo(archivo)
        if deps:
            dependencias_encontradas.update(deps)
            archivos_problematicos.append((archivo, deps))
    
    # Verificar pip list
    print("\n📦 Verificando paquetes instalados...")
    paquetes_instalados = verificar_pip_list()
    
    # Reportar resultados
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DE VERIFICACIÓN")
    print("=" * 60)
    
    if dependencias_encontradas:
        print(f"❌ DEPENDENCIAS EXTERNAS ENCONTRADAS: {dependencias_encontradas}")
        print("\n📁 Archivos problemáticos:")
        for archivo, deps in archivos_problematicos:
            print(f"   - {archivo}: {deps}")
    else:
        print("✅ NINGUNA DEPENDENCIA EXTERNA en código Python")
    
    if paquetes_instalados:
        print(f"\n⚠️  PAQUETES INSTALADOS (además de pip): {paquetes_instalados}")
    else:
        print("\n✅ SOLO PIP INSTALADO - Sin paquetes externos")
    
    # Verificar archivos de prueba opcionales
    archivos_test_opcionales = [
        'test_moderno_simple.py',
        'demo_interfaz_moderna.py'
    ]
    
    print(f"\n🧪 Verificando archivos de test opcionales...")
    archivos_test_encontrados = 0
    for test_file in archivos_test_opcionales:
        test_path = proyecto_root / test_file
        if test_path.exists():
            print(f"✅ {test_file} - PRESENTE")
            archivos_test_encontrados += 1
        else:
            print(f"ℹ️ {test_file} - OPCIONAL (no presente)")
    
    if archivos_test_encontrados > 0:
        print(f"📝 {archivos_test_encontrados} archivo(s) de test opcional(es) encontrado(s)")
    else:
        print("📝 Sin archivos de test opcionales (esto es normal)")
    
    # Verificar archivos eliminados
    archivos_eliminados = [
        'test_metricas_tiempo_real.py',
        'test_moderno.py',
        'limpiar_codigo.py'
    ]
    
    print(f"\n🗑️  Verificando archivos obsoletos eliminados...")
    for archivo in archivos_eliminados:
        archivo_path = proyecto_root / archivo
        if not archivo_path.exists():
            print(f"✅ {archivo} - ELIMINADO")
        else:
            print(f"❌ {archivo} - AÚN PRESENTE")
    
    # Resumen final
    print("\n" + "=" * 60)
    if not dependencias_encontradas and not paquetes_instalados:
        print("🎉 ¡VERIFICACIÓN EXITOSA!")
        print("✅ Ares Aegis está limpio y usa solo librerías estándar")
        print("✅ Sin dependencias externas")
        print("✅ Listo para usar")
        return True
    else:
        print("❌ VERIFICACIÓN FALLIDA")
        print("⚠️  Se encontraron problemas que necesitan corrección")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
