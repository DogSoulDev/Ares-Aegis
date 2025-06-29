#!/usr/bin/env python3
"""
Test Main - Verificación Rápida de Ares Aegis
Prueba básica de funcionamiento sin interfaz gráfica completa
"""

import sys
import os
import logging

# Configurar logging simple
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Añadir el directorio src al path para importaciones
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

def test_imports():
    """Prueba que todos los imports funcionen."""
    print("🔍 Probando imports...")
    
    try:
        from controladores.controlador_principal import ControladorPrincipal
        print("✅ Import ControladorPrincipal: OK")
    except Exception as e:
        print(f"❌ Import ControladorPrincipal: {e}")
        return False
    
    try:
        from vista.interfaz_principal_gui import InterfazPrincipalGUI
        print("✅ Import InterfazPrincipalGUI: OK")
    except Exception as e:
        print(f"❌ Import InterfazPrincipalGUI: {e}")
        return False
    
    return True

def test_controlador():
    """Prueba la inicialización del controlador."""
    print("🎮 Probando controlador principal...")
    
    try:
        from controladores.controlador_principal import ControladorPrincipal
        controlador = ControladorPrincipal()
        
        # Probar inicialización del sistema
        resultado = controlador.iniciar_sistema()
        if resultado:
            print("✅ Controlador inicializado: OK")
        else:
            print("⚠️  Controlador inicializado con limitaciones")
        
        return True
    except Exception as e:
        print(f"❌ Error en controlador: {e}")
        return False

def test_siem():
    """Prueba el sistema SIEM."""
    print("📊 Probando sistema SIEM...")
    
    try:
        from modelos.siem import SIEM, TipoEvento
        siem = SIEM()
        
        # Probar logging de evento
        siem.log_evento(TipoEvento.SISTEMA_EVENTO, "Test de funcionamiento")
        print("✅ SIEM funcional: OK")
        return True
    except Exception as e:
        print(f"❌ Error en SIEM: {e}")
        return False

def test_escaneador():
    """Prueba el escaneador básico."""
    print("🔍 Probando escaneador...")
    
    try:
        from modelos.siem import SIEM
        from modelos.escaneador import Escaneador
        
        siem = SIEM()
        escaneador = Escaneador(siem)
        print("✅ Escaneador inicializado: OK")
        return True
    except Exception as e:
        print(f"❌ Error en escaneador: {e}")
        return False

def main():
    """Función principal de test."""
    print("🛡️  ARES AEGIS - TEST DE FUNCIONAMIENTO")
    print("=" * 60)
    print("Autor: DogSoulDev")
    print("Versión: 2.0.0 (Test Mode)")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("SIEM", test_siem),
        ("Escaneador", test_escaneador),
        ("Controlador", test_controlador)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        print(f"\n📋 Ejecutando test: {nombre}")
        print("-" * 30)
        resultado = test_func()
        resultados.append((nombre, resultado))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    
    todos_ok = True
    for nombre, resultado in resultados:
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{estado} - {nombre}")
        if not resultado:
            todos_ok = False
    
    print("\n" + "=" * 60)
    if todos_ok:
        print("🎉 TODOS LOS TESTS PASARON")
        print("   Ares Aegis está funcionando correctamente")
        print("   Puedes ejecutar: python3 main.py")
        return 0
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
        print("   Revisar los errores reportados arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main())
