#!/usr/bin/env python3
"""
Script de Limpieza y Verificación - Ares Aegis
Elimina archivos obsoletos y verifica la estructura del proyecto

Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados.
"""

import os
import sys
from pathlib import Path

def limpiar_archivos_obsoletos():
    """Elimina archivos obsoletos y duplicados."""
    print("🧹 INICIANDO LIMPIEZA DE ARES AEGIS")
    print("=" * 50)
    
    archivos_eliminados = 0
    
    # Lista de archivos que pueden ser obsoletos
    archivos_obsoletos = [
        "ares_aegis/modelos/sistema_reportes_notificaciones.py",  # Versión básica
        "ares_aegis/modelos/fim.py",  # Versión básica
        "ares_aegis/modelos/monitor_red.py",  # Versión básica
        "ares_aegis/modelos/gestor_cuarentena.py",  # Versión básica
        "ares_aegis/modelos/escaneador_basic.py",  # Versión básica
        "cuarentena_avanzada/",  # Directorio duplicado
        "system_logs.txt",  # Logs antiguos
        "temp_files/",  # Archivos temporales
    ]
    
    # Eliminar archivos obsoletos
    for archivo in archivos_obsoletos:
        ruta = Path(archivo)
        if ruta.exists():
            try:
                if ruta.is_file():
                    ruta.unlink()
                    print(f"🗑️  Eliminado archivo: {archivo}")
                    archivos_eliminados += 1
                elif ruta.is_dir():
                    import shutil
                    shutil.rmtree(ruta)
                    print(f"🗑️  Eliminado directorio: {archivo}")
                    archivos_eliminados += 1
            except Exception as e:
                print(f"⚠️  Error eliminando {archivo}: {e}")
    
    # Limpiar archivos de caché de Python
    print("\n🧹 Limpiando archivos de caché Python...")
    cache_eliminados = 0
    
    for root, dirs, files in os.walk("."):
        # Eliminar directorios __pycache__
        if "__pycache__" in dirs:
            cache_dir = Path(root) / "__pycache__"
            try:
                import shutil
                shutil.rmtree(cache_dir)
                print(f"🗑️  Cache eliminado: {cache_dir}")
                cache_eliminados += 1
            except Exception as e:
                print(f"⚠️  Error eliminando cache {cache_dir}: {e}")
        
        # Eliminar archivos .pyc
        for file in files:
            if file.endswith('.pyc'):
                pyc_file = Path(root) / file
                try:
                    pyc_file.unlink()
                    cache_eliminados += 1
                except Exception as e:
                    print(f"⚠️  Error eliminando {pyc_file}: {e}")
    
    print(f"\n✅ Limpieza completada:")
    print(f"   - Archivos obsoletos eliminados: {archivos_eliminados}")
    print(f"   - Archivos de caché eliminados: {cache_eliminados}")
    
    return archivos_eliminados + cache_eliminados > 0

def verificar_estructura():
    """Verifica que la estructura del proyecto sea correcta."""
    print("\n🔍 VERIFICANDO ESTRUCTURA DEL PROYECTO")
    print("=" * 50)
    
    # Estructura esperada
    estructura_esperada = {
        "ares_aegis/": "dir",
        "ares_aegis/modelos/": "dir",
        "ares_aegis/controladores/": "dir",
        "ares_aegis/vista/": "dir",
        "ares_aegis/utilidades/": "dir",
        "ares_aegis/modelos/siem.py": "file",
        "ares_aegis/modelos/escaneador.py": "file",
        "ares_aegis/modelos/fim.py": "file",
        "ares_aegis/modelos/monitor_red.py": "file",
        "ares_aegis/modelos/gestor_cuarentena.py": "file",
        "ares_aegis/modelos/respuesta_automatizada.py": "file",
        "ares_aegis/modelos/respondedor_incidentes.py": "file",
        "ares_aegis/controladores/controlador_principal.py": "file",
        "ares_aegis/controladores/controlador_respuesta_automatizada.py": "file",
        "ares_aegis/controladores/controlador_incidentes.py": "file",
        "main.py": "file",
        "README.md": "file",
        "requirements.txt": "file",
        "configuracion/": "dir",
        "recursos/": "dir",
        # "cuarentena/": "dir",  # Eliminado por unificación de cuarentena
        "logs/": "dir",
        "reportes/": "dir",
        "tests/": "dir"
    }
    
    errores = 0
    
    for ruta, tipo in estructura_esperada.items():
        path_obj = Path(ruta)
        if not path_obj.exists():
            print(f"❌ Faltante: {ruta}")
            errores += 1
        elif tipo == "dir" and not path_obj.is_dir():
            print(f"❌ Debería ser directorio: {ruta}")
            errores += 1
        elif tipo == "file" and not path_obj.is_file():
            print(f"❌ Debería ser archivo: {ruta}")
            errores += 1
        else:
            print(f"✅ OK: {ruta}")
    
    if errores == 0:
        print(f"\n🎉 Estructura del proyecto CORRECTA")
        return True
    else:
        print(f"\n⚠️  Encontrados {errores} problemas en la estructura")
        return False

def generar_reporte_limpieza():
    """Genera un reporte de la limpieza realizada."""
    print("\n📊 GENERANDO REPORTE DE LIMPIEZA")
    print("=" * 50)
    
    # Contar archivos por tipo
    stats = {
        "archivos_python": 0,
        "archivos_json": 0,
        "archivos_txt": 0,
        "directorios": 0,
        "tamaño_total": 0
    }
    
    for root, dirs, files in os.walk("."):
        stats["directorios"] += len(dirs)
        
        for file in files:
            file_path = Path(root) / file
            try:
                size = file_path.stat().st_size
                stats["tamaño_total"] += size
                
                if file.endswith('.py'):
                    stats["archivos_python"] += 1
                elif file.endswith('.json'):
                    stats["archivos_json"] += 1
                elif file.endswith('.txt'):
                    stats["archivos_txt"] += 1
            except:
                pass
    
    print(f"📁 Directorios: {stats['directorios']}")
    print(f"🐍 Archivos Python: {stats['archivos_python']}")
    print(f"📄 Archivos JSON: {stats['archivos_json']}")
    print(f"📝 Archivos TXT: {stats['archivos_txt']}")
    print(f"💾 Tamaño total: {stats['tamaño_total'] / 1024 / 1024:.2f} MB")
    
    return stats

def main():
    """Función principal del script de limpieza."""
    print("🛡️  ARES AEGIS - SCRIPT DE LIMPIEZA Y VERIFICACIÓN")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not Path("main.py").exists():
        print("❌ Error: Ejecute este script desde el directorio raíz de Ares Aegis")
        sys.exit(1)
    
    # Realizar limpieza
    limpieza_realizada = limpiar_archivos_obsoletos()
    
    # Verificar estructura
    estructura_ok = verificar_estructura()
    
    # Generar reporte
    stats = generar_reporte_limpieza()
    
    # Resultado final
    print("\n" + "=" * 60)
    if estructura_ok:
        print("🎉 ARES AEGIS - LIMPIEZA COMPLETADA EXITOSAMENTE")
        print("✅ El proyecto está listo para ejecutar")
        if limpieza_realizada:
            print("🧹 Se realizó limpieza de archivos obsoletos")
        else:
            print("✨ No se encontraron archivos obsoletos")
    else:
        print("⚠️  ARES AEGIS - PROBLEMAS DETECTADOS")
        print("❌ Revisar la estructura del proyecto")
        sys.exit(1)
    
    print("=" * 60)

if __name__ == "__main__":
    main()
