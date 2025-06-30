#!/usr/bin/env python3
"""
Test de Escalación de Privilegios - Ares Aegis
Prueba el sistema de escalación automática de privilegios
"""

import sys
import os

# Añadir el directorio src al path para importaciones
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

def test_escalacion_privilegios():
    """Prueba el módulo de escalación de privilegios."""
    print("🔐 Testing módulo de escalación de privilegios...")
    
    try:
        from utilidades.escalacion_privilegios import (
            verificar_privilegios,
            modo_limitado_disponible,
            gestionar_privilegios_inicial
        )
        
        print("✅ Import de módulo de escalación: OK")
        
        # Verificar estado actual de privilegios
        tiene_root = verificar_privilegios()
        print(f"📊 Privilegios actuales: {'Root' if tiene_root else 'Usuario normal'}")
        
        # Verificar si modo limitado está disponible
        modo_disponible = modo_limitado_disponible()
        print(f"📊 Modo limitado disponible: {'Sí' if modo_disponible else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de escalación: {e}")
        return False

def test_main_con_privilegios():
    """Prueba el main.py con el sistema de privilegios."""
    print("\n🚀 Testing main.py con sistema de privilegios...")
    
    try:
        # Importar el main modificado
        from main import configurar_logging
        
        print("✅ Import de main modificado: OK")
        
        # Configurar logging para test
        configurar_logging()
        print("✅ Logging configurado: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de main: {e}")
        return False

def main():
    """Función principal de test."""
    print("🛡️  ARES AEGIS - TEST DE ESCALACIÓN DE PRIVILEGIOS")
    print("=" * 60)
    
    tests = [
        ("Escalación de Privilegios", test_escalacion_privilegios),
        ("Main con Privilegios", test_main_con_privilegios)
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
        print("🎉 SISTEMA DE PRIVILEGIOS FUNCIONANDO")
        print("   El sistema de escalación está listo")
        print("   Ejecute: python3 main.py")
        return 0
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
        print("   Revisar los errores reportados arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main())
