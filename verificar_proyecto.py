#!/usr/bin/env python3
"""
Script de Verificación del Proyecto Ares Aegis
Valida la estructura, dependencias y funcionalidad básica
"""

import os
import sys
import importlib.util
from pathlib import Path

def verificar_estructura():
    """Verifica que la estructura del proyecto sea correcta."""
    print("🔍 Verificando estructura del proyecto...")
    
    estructura_requerida = {
        'main.py': 'Punto de entrada principal',
        'README.md': 'Documentación técnica',
        'MANUAL.md': 'Manual de usuario',
        'requirements.txt': 'Dependencias',
        'src/': 'Código fuente principal',
        'src/modelos/': 'Lógica de negocio',
        'src/vista/': 'Interfaz gráfica',
        'src/controladores/': 'Controladores MVC',
        'config/': 'Configuraciones',
        'config/firmas/': 'Base de datos de firmas',
        'recursos/': 'Recursos gráficos',
        'tests/': 'Tests unitarios'
    }
    
    base_path = Path('.')
    errores = []
    
    for ruta, descripcion in estructura_requerida.items():
        path_completo = base_path / ruta
        if path_completo.exists():
            print(f"  ✅ {ruta} - {descripcion}")
        else:
            print(f"  ❌ {ruta} - {descripcion} (FALTANTE)")
            errores.append(ruta)
    
    return len(errores) == 0

def verificar_archivos_clave():
    """Verifica que los archivos clave existan y tengan contenido."""
    print("\n📁 Verificando archivos clave...")
    
    archivos_clave = {
        'main.py': 100,  # mínimo 100 bytes
        'src/vista/interfaz_principal_gui.py': 500,
        'src/controladores/controlador_principal.py': 200,
        'config/firmas/firmas.txt': 10
    }
    
    errores = []
    
    for archivo, tamaño_min in archivos_clave.items():
        path = Path(archivo)
        if path.exists():
            tamaño = path.stat().st_size
            if tamaño >= tamaño_min:
                print(f"  ✅ {archivo} ({tamaño} bytes)")
            else:
                print(f"  ⚠️  {archivo} ({tamaño} bytes - muy pequeño)")
                errores.append(archivo)
        else:
            print(f"  ❌ {archivo} (no existe)")
            errores.append(archivo)
    
    return len(errores) == 0

def verificar_imports():
    """Verifica que los imports principales funcionen."""
    print("\n🐍 Verificando imports de Python...")
    
    # Agregar src al path
    src_path = Path('src').absolute()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    modulos_test = [
        ('tkinter', 'Interfaz gráfica'),
        ('subprocess', 'Ejecución de comandos'),
        ('hashlib', 'Cálculo de hashes'),
        ('json', 'Serialización JSON'),
        ('sqlite3', 'Base de datos'),
        ('threading', 'Multihilo'),
        ('logging', 'Sistema de logs')
    ]
    
    errores = []
    
    for modulo, descripcion in modulos_test:
        try:
            importlib.import_module(modulo)
            print(f"  ✅ {modulo} - {descripcion}")
        except ImportError:
            print(f"  ❌ {modulo} - {descripcion} (NO DISPONIBLE)")
            errores.append(modulo)
    
    return len(errores) == 0

def verificar_recursos():
    """Verifica que los recursos gráficos existan."""
    print("\n🎨 Verificando recursos gráficos...")
    
    recursos = [
        'recursos/AresAegis.png',
        'recursos/aresIcon.png'
    ]
    
    errores = []
    
    for recurso in recursos:
        path = Path(recurso)
        if path.exists():
            tamaño = path.stat().st_size
            print(f"  ✅ {recurso} ({tamaño} bytes)")
        else:
            print(f"  ❌ {recurso} (no existe)")
            errores.append(recurso)
    
    return len(errores) == 0

def verificar_documentacion():
    """Verifica que la documentación esté completa."""
    print("\n📚 Verificando documentación...")
    
    docs = {
        'README.md': 2000,  # README técnico
        'MANUAL.md': 10000,  # Manual completo
        'recursos/README.md': 100  # Documentación de recursos
    }
    
    errores = []
    
    for doc, tamaño_min in docs.items():
        path = Path(doc)
        if path.exists():
            tamaño = path.stat().st_size
            if tamaño >= tamaño_min:
                print(f"  ✅ {doc} ({tamaño} bytes)")
            else:
                print(f"  ⚠️  {doc} ({tamaño} bytes - contenido insuficiente)")
        else:
            print(f"  ❌ {doc} (no existe)")
            errores.append(doc)
    
    return len(errores) == 0

def main():
    """Función principal de verificación."""
    print("🛡️  VERIFICACIÓN DEL PROYECTO ARES AEGIS")
    print("=" * 50)
    
    tests = [
        ("Estructura del Proyecto", verificar_estructura),
        ("Archivos Clave", verificar_archivos_clave),
        ("Imports de Python", verificar_imports),
        ("Recursos Gráficos", verificar_recursos),
        ("Documentación", verificar_documentacion)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        print(f"\n📋 {nombre}")
        print("-" * 30)
        resultado = test_func()
        resultados.append((nombre, resultado))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    todos_ok = True
    for nombre, resultado in resultados:
        estado = "✅ OK" if resultado else "❌ ERROR"
        print(f"{estado} - {nombre}")
        if not resultado:
            todos_ok = False
    
    print("\n" + "=" * 50)
    if todos_ok:
        print("🎉 PROYECTO COMPLETAMENTE VERIFICADO")
        print("   Ares Aegis está listo para ejecutar")
        return 0
    else:
        print("⚠️  SE ENCONTRARON PROBLEMAS")
        print("   Revisar los errores reportados arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main())
