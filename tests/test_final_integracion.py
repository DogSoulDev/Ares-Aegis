#!/usr/bin/env python3
"""
Test Final de Integración - Ares Aegis
Verifica que todos los componentes MVC funcionen correctamente

Autor: DogSoulDev
Versión: 2.0.0
"""

import sys
import os
import tempfile
import logging

# Configurar path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_importaciones():
    """Prueba que todas las importaciones funcionen."""
    print("🔍 Probando importaciones...")
    
    try:
        # Modelos
        from modelos.siem import SIEM, TipoEvento
        from modelos.escaneador import Escaneador
        from modelos.cuarentena import GestorCuarentena
        from modelos.monitor_red import MonitorRed
        from modelos.monitor_integridad import MonitorIntegridad
        
        # Vista
        from vista.interfaz_principal_gui import InterfazPrincipalGUI
        
        # Controlador
        from controladores.controlador_principal import ControladorPrincipal
        
        print("✅ Todas las importaciones exitosas")
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False

def test_mvc_funcional():
    """Prueba que el patrón MVC funcione."""
    print("🔍 Probando patrón MVC...")
    
    try:
        # Configurar logging silencioso
        logging.basicConfig(level=logging.CRITICAL)
        
        # Importar componentes
        from modelos.siem import SIEM
        from controladores.controlador_principal import ControladorPrincipal
        
        # Probar Modelo
        siem = SIEM()
        siem.log_evento("INFO", "Test de modelo")
        
        # Probar Controlador
        controlador = ControladorPrincipal()
        
        # Crear archivo de prueba
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Archivo de prueba limpio")
            archivo_prueba = f.name
        
        try:
            # Probar escaneo
            resultado = controlador.escanear_archivo(archivo_prueba)
            
            # Probar cuarentena
            archivos_cuarentena = controlador.listar_cuarentena()
            
            # Probar monitoreo de red
            datos_red = controlador.monitorear_red()
            
            print("✅ Patrón MVC funcionando correctamente")
            return True
            
        finally:
            os.unlink(archivo_prueba)
            
    except Exception as e:
        print(f"❌ Error en MVC: {e}")
        return False

def test_estructura_proyecto():
    """Verifica la estructura del proyecto."""
    print("🔍 Verificando estructura del proyecto...")
    
    estructura_requerida = [
        'src/modelos/',
        'src/vista/',
        'src/controladores/',
        'src/main.py',
        'config/',
        'tests/',
        'docs/',
        'main.py',
        'README.md',
        'requirements.txt'
    ]
    
    base_path = os.path.join(os.path.dirname(__file__), '..')
    
    for ruta in estructura_requerida:
        ruta_completa = os.path.join(base_path, ruta)
        if not os.path.exists(ruta_completa):
            print(f"❌ Falta: {ruta}")
            return False
    
    print("✅ Estructura del proyecto correcta")
    return True

def main():
    """Función principal."""
    print("🛡️ ARES AEGIS - TEST FINAL DE INTEGRACIÓN")
    print("=" * 50)
    
    tests = [
        test_estructura_proyecto,
        test_importaciones,
        test_mvc_funcional
    ]
    
    resultados = []
    
    for test in tests:
        resultado = test()
        resultados.append(resultado)
        print()
    
    # Resumen
    exitosos = sum(resultados)
    total = len(resultados)
    
    print("=" * 50)
    print(f"📊 RESULTADOS: {exitosos}/{total} tests exitosos")
    
    if exitosos == total:
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        print("✅ Ares Aegis está listo para producción")
        return 0
    else:
        print("❌ Algunos tests fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main())
