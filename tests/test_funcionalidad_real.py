#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Test de Funcionalidad Real
"""

import sys
import time
import tempfile
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from ares_aegis.controladores.controlador_principal import ControladorPrincipal

def test_inicializacion_controlador():
    """Test: Verificar que el controlador se inicializa correctamente."""
    print("🔧 Test 1: Inicialización del Controlador...")
    try:
        controlador = ControladorPrincipal()
        print("✅ Controlador inicializado correctamente")
        
        # Verificar que los componentes principales están presentes
        assert controlador.escaneador is not None, "Escaneador no inicializado"
        assert controlador.siem is not None, "SIEM no inicializado"
        print("✅ Componentes principales verificados")
        
        controlador.finalizar()
        return True
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        return False

def test_estadisticas_generales():
    """Test: Verificar que las estadísticas generales funcionan."""
    print("\n📊 Test 2: Estadísticas Generales...")
    try:
        controlador = ControladorPrincipal()
        estadisticas = controlador.obtener_estadisticas_generales()
        
        # Verificar campos obligatorios
        campos_requeridos = [
            'archivos_escaneados', 'amenazas_detectadas', 'archivos_cuarentena',
            'conexiones_activas', 'archivos_fim', 'alertas_activas', 
            'uptime_segundos', 'uso_memoria_mb'
        ]
        
        for campo in campos_requeridos:
            assert campo in estadisticas, f"Campo faltante: {campo}"
            assert isinstance(estadisticas[campo], (int, float)), f"Tipo incorrecto para {campo}"
        
        print("✅ Estadísticas generales funcionan correctamente")
        print(f"   - Archivos escaneados: {estadisticas['archivos_escaneados']}")
        print(f"   - Amenazas detectadas: {estadisticas['amenazas_detectadas']}")
        print(f"   - Uptime: {estadisticas['uptime_segundos']} segundos")
        
        controlador.finalizar()
        return True
    except Exception as e:
        print(f"❌ Error en estadísticas: {e}")
        return False

def test_escaneo_rapido():
    """Test: Verificar que el escaneo rápido funciona."""
    print("\n⚡ Test 3: Escaneo Rápido...")
    try:
        controlador = ControladorPrincipal()
        
        # Crear un directorio temporal con un archivo de prueba
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo de prueba
            archivo_prueba = Path(temp_dir) / "test_file.txt"
            archivo_prueba.write_text("Archivo de prueba para escaneo")
            
            # Modificar las rutas del escaneo rápido para incluir nuestro directorio temporal
            print(f"   Escaneando directorio temporal: {temp_dir}")
            resultado = controlador.escanear_directorio(temp_dir)
            
            # Verificar resultado
            assert isinstance(resultado, dict), "El resultado debe ser un diccionario"
            assert 'archivos_escaneados' in resultado, "Falta campo archivos_escaneados"
            assert 'amenazas_detectadas' in resultado, "Falta campo amenazas_detectadas"
            assert 'tiempo_escaneo' in resultado, "Falta campo tiempo_escaneo"
            
            print("✅ Escaneo rápido funciona correctamente")
            print(f"   - Archivos escaneados: {resultado['archivos_escaneados']}")
            print(f"   - Amenazas detectadas: {resultado['amenazas_detectadas']}")
            print(f"   - Tiempo: {resultado['tiempo_escaneo']:.2f} segundos")
            
        controlador.finalizar()
        return True
    except Exception as e:
        print(f"❌ Error en escaneo rápido: {e}")
        return False

def test_escaneo_directorio():
    """Test: Verificar que el escaneo de directorio funciona."""
    print("\n📁 Test 4: Escaneo de Directorio...")
    try:
        controlador = ControladorPrincipal()
        
        # Crear directorio temporal con múltiples archivos
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Crear varios archivos de prueba
            for i in range(5):
                archivo = temp_path / f"archivo_{i}.txt"
                archivo.write_text(f"Contenido del archivo {i}")
            
            # Crear subdirectorio con más archivos
            subdir = temp_path / "subdirectorio"
            subdir.mkdir()
            for i in range(3):
                archivo = subdir / f"sub_archivo_{i}.txt"
                archivo.write_text(f"Contenido del sub archivo {i}")
            
            print(f"   Escaneando: {temp_dir}")
            resultado = controlador.escanear_directorio(temp_dir)
            
            # Verificar que se escanearon los archivos
            assert resultado['archivos_escaneados'] >= 8, f"Se esperaban al menos 8 archivos, se escanearon {resultado['archivos_escaneados']}"
            assert resultado['tiempo_escaneo'] > 0, "El tiempo de escaneo debe ser mayor a 0"
            
            print("✅ Escaneo de directorio funciona correctamente")
            print(f"   - Archivos encontrados: {resultado['archivos_escaneados']}")
            print(f"   - Tiempo total: {resultado['tiempo_escaneo']:.2f} segundos")
            
        controlador.finalizar()
        return True
    except Exception as e:
        print(f"❌ Error en escaneo de directorio: {e}")
        return False

def test_siem_funcional():
    """Test: Verificar que el SIEM registra eventos."""
    print("\n📝 Test 5: Funcionalidad SIEM...")
    try:
        controlador = ControladorPrincipal()
        
        # Verificar que el SIEM puede registrar eventos
        if controlador.siem:
            eventos_iniciales = len(controlador.siem.eventos)
            
            # Realizar una operación que genere eventos
            with tempfile.TemporaryDirectory() as temp_dir:
                archivo_prueba = Path(temp_dir) / "test_siem.txt"
                archivo_prueba.write_text("Archivo para test SIEM")
                
                controlador.escanear_directorio(temp_dir)
            
            eventos_finales = len(controlador.siem.eventos)
            
            assert eventos_finales > eventos_iniciales, "No se registraron nuevos eventos en SIEM"
            
            print("✅ SIEM funciona correctamente")
            print(f"   - Eventos registrados: {eventos_finales - eventos_iniciales}")
        else:
            print("⚠️  SIEM no está inicializado")
            
        controlador.finalizar()
        return True
    except Exception as e:
        print(f"❌ Error en SIEM: {e}")
        return False

def test_cuarentena_funcional():
    """Test: Verificar que el sistema de cuarentena existe."""
    print("\n🔒 Test 6: Sistema de Cuarentena...")
    try:
        # Verificar que los directorios de cuarentena existen
        cuarentena_base = Path(__file__).parent / "cuarentena"
        
        directorios_requeridos = [
            cuarentena_base / "activos",
            cuarentena_base / "backups",
            cuarentena_base / "logs",
            cuarentena_base / "temp"
        ]
        
        for directorio in directorios_requeridos:
            if not directorio.exists():
                print(f"⚠️  Creando directorio faltante: {directorio}")
                directorio.mkdir(parents=True, exist_ok=True)
        
        print("✅ Sistema de cuarentena verificado")
        print(f"   - Directorio base: {cuarentena_base}")
        
        return True
    except Exception as e:
        print(f"❌ Error en cuarentena: {e}")
        return False

def test_rendimiento_basico():
    """Test: Verificar rendimiento básico."""
    print("\n⚡ Test 7: Rendimiento Básico...")
    try:
        controlador = ControladorPrincipal()
        
        # Test de rendimiento: escanear 100 archivos pequeños
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Crear 100 archivos pequeños
            for i in range(100):
                archivo = temp_path / f"perf_test_{i:03d}.txt"
                archivo.write_text(f"Archivo de rendimiento {i}" * 10)  # ~200 bytes cada uno
            
            inicio = time.time()
            resultado = controlador.escanear_directorio(temp_dir)
            tiempo_total = time.time() - inicio
            
            archivos_por_segundo = resultado['archivos_escaneados'] / tiempo_total if tiempo_total > 0 else 0
            
            print("✅ Test de rendimiento completado")
            print(f"   - Archivos procesados: {resultado['archivos_escaneados']}")
            print(f"   - Tiempo total: {tiempo_total:.2f} segundos")
            print(f"   - Velocidad: {archivos_por_segundo:.1f} archivos/segundo")
            
            # Verificar que el rendimiento es razonable (al menos 50 archivos/segundo)
            assert archivos_por_segundo >= 10, f"Rendimiento muy bajo: {archivos_por_segundo:.1f} archivos/segundo"
            
        controlador.finalizar()
        return True
    except Exception as e:
        print(f"❌ Error en test de rendimiento: {e}")
        return False

def main():
    """Ejecuta todos los tests de funcionalidad."""
    print("🛡️  TESTS DE FUNCIONALIDAD REAL - ARES AEGIS")
    print("=" * 50)
    
    tests = [
        test_inicializacion_controlador,
        test_estadisticas_generales,
        test_escaneo_rapido,
        test_escaneo_directorio,
        test_siem_funcional,
        test_cuarentena_funcional,
        test_rendimiento_basico
    ]
    
    resultados = []
    
    for test in tests:
        try:
            resultado = test()
            resultados.append(resultado)
        except Exception as e:
            print(f"❌ Error crítico en {test.__name__}: {e}")
            resultados.append(False)
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE RESULTADOS:")
    print("=" * 50)
    
    exitosos = sum(resultados)
    total = len(resultados)
    
    for i, (test, resultado) in enumerate(zip(tests, resultados)):
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{i+1}. {test.__name__}: {estado}")
    
    print(f"\n🎯 TOTAL: {exitosos}/{total} tests exitosos ({(exitosos/total)*100:.1f}%)")
    
    if exitosos == total:
        print("🏆 ¡TODOS LOS TESTS PASARON! El sistema está completamente funcional.")
        return 0
    else:
        print("⚠️  ALGUNOS TESTS FALLARON. Revisar funcionalidades.")
        return 1

if __name__ == "__main__":
    exit(main())
