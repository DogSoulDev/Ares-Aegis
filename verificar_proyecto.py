#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🛡️ Verificación del Sistema Ares Aegis
📅 Fecha: 3 de Julio, 2025
👤 Autor: DogSoulDev
🔰 Versión: 2.0.0

🌸 Script de verificación rápida del sistema 🌸
"""

import sys
import os
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verificar_importaciones():
    """🔍 Verifica que todas las importaciones funcionen correctamente"""
    print("🔍 Verificando importaciones de módulos...")
    
    try:
        # Importar el controlador principal
        from ares_aegis.controladores.controlador_principal import ControladorPrincipal
        print("✅ ControladorPrincipal - Importado exitosamente")
        
        # Verificar que se puede instanciar
        controlador = ControladorPrincipal()
        print("✅ ControladorPrincipal - Instanciado exitosamente")
        
        # Verificar estado del sistema
        estado = controlador.verificar_estado_sistema()
        print(f"✅ Estado del sistema: {estado['sistema_iniciado']}")
        
        # Verificar estadísticas
        stats = controlador.obtener_estadisticas_generales()
        print(f"✅ Estadísticas disponibles: {len(stats)} métricas")
        
        # Finalizar controlador
        controlador.finalizar()
        print("✅ ControladorPrincipal - Finalizado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def verificar_estructura_proyecto():
    """🏗️ Verifica la estructura del proyecto"""
    print("\n🏗️ Verificando estructura del proyecto...")
    
    directorios_requeridos = [
        "ares_aegis",
        "ares_aegis/modelos",
        "ares_aegis/controladores", 
        "ares_aegis/vista",
        "ares_aegis/utilidades",
        "configuracion",
        "logs",
        "cuarentena",
        "recursos",
        "reportes"
    ]
    
    archivos_requeridos = [
        "main.py",
        "iniciar.sh",
        "requirements.txt",
        "ares_aegis/controladores/controlador_principal.py",
        "ares_aegis/vista/interfaz_principal_gui.py"
    ]
    
    todo_ok = True
    
    # Verificar directorios
    for directorio in directorios_requeridos:
        if Path(directorio).exists():
            print(f"✅ Directorio: {directorio}")
        else:
            print(f"❌ Directorio faltante: {directorio}")
            todo_ok = False
    
    # Verificar archivos
    for archivo in archivos_requeridos:
        if Path(archivo).exists():
            print(f"✅ Archivo: {archivo}")
        else:
            print(f"❌ Archivo faltante: {archivo}")
            todo_ok = False
    
    return todo_ok

def main():
    """🚀 Función principal de verificación"""
    print("🛡️ VERIFICACIÓN DEL SISTEMA ARES AEGIS")
    print("=" * 50)
    
    # Verificar estructura
    estructura_ok = verificar_estructura_proyecto()
    
    # Verificar importaciones
    importaciones_ok = verificar_importaciones()
    
    print("\n" + "=" * 50)
    if estructura_ok and importaciones_ok:
        print("🎉 ¡VERIFICACIÓN EXITOSA!")
        print("✅ Ares Aegis está listo para proteger el reino")
        print("🌸 Todos los dioses del Olimpo han respondido al llamado")
        return True
    else:
        print("⚠️ VERIFICACIÓN FALLIDA")
        print("❌ Algunos componentes requieren atención")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
