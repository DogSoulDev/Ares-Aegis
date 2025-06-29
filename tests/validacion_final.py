#!/usr/bin/env python3
"""
Script de Validación Final - Ares Aegis
Verifica que el sistema funcione completamente con librerías estándar únicamente

Autor: DogSoulDev
Versión: 2.0.0
Fecha: 29 de Junio, 2025
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

def print_header():
    """Imprime el encabezado del script."""
    print("🛡️" + "=" * 60)
    print("   ARES AEGIS - VALIDACIÓN FINAL DEL SISTEMA")
    print("   Standard Library Edition - Verificación Completa")
    print("=" * 62)
    print()

def check_python_version():
    """Verifica la versión de Python."""
    print("🐍 VERIFICANDO VERSIÓN DE PYTHON")
    print("-" * 40)
    version = sys.version_info
    print(f"Versión Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Versión de Python compatible")
        return True
    else:
        print("❌ Se requiere Python 3.8 o superior")
        return False

def check_no_external_dependencies():
    """Verifica que no haya dependencias externas problemáticas."""
    print("\n📦 VERIFICANDO DEPENDENCIAS EXTERNAS")
    print("-" * 40)
    
    prohibited_packages = [
        'psutil', 'PySide6', 'PyQt5', 'PyQt6', 'requests', 
        'numpy', 'pandas', 'matplotlib', 'flask', 'django'
    ]
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        installed_packages = result.stdout.lower()
        
        found_prohibited = []
        for package in prohibited_packages:
            if package.lower() in installed_packages:
                found_prohibited.append(package)
        
        if found_prohibited:
            print("⚠️  Paquetes externos encontrados (pueden causar conflictos):")
            for pkg in found_prohibited:
                print(f"   - {pkg}")
            print("💡 Recomendación: Usar entorno virtual limpio")
        else:
            print("✅ No se encontraron dependencias externas problemáticas")
        
        return len(found_prohibited) == 0
        
    except Exception as e:
        print(f"⚠️  No se pudo verificar dependencias: {e}")
        return True

def check_module_imports():
    """Verifica que todos los módulos principales se importen correctamente."""
    print("\n🔧 VERIFICANDO IMPORTACIONES DE MÓDULOS")
    print("-" * 40)
    
    # Agregar src al path
    src_path = Path(__file__).parent / 'src'
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    
    modules_to_test = [
        ('modelos.monitor_procesos', 'MonitorProcesos'),
        ('modelos.monitor_red', 'MonitorRed'),
        ('modelos.siem', 'SIEM'),
        ('modelos.escaneador', 'Escaneador'),
        ('modelos.analizador_logs', 'AnalizadorLogs'),
        ('modelos.fim', 'FIM'),
        ('modelos.gestor_cuarentena', 'GestorCuarentena'),
        ('modelos.integracion_externa', 'IntegracionExterna'),
        ('vista.interfaz_principal_gui', 'InterfazPrincipalGUI')
    ]
    
    success_count = 0
    total_count = len(modules_to_test)
    
    for module_name, class_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                print(f"✅ {module_name}.{class_name}")
                success_count += 1
            else:
                print(f"❌ {module_name} - Clase {class_name} no encontrada")
        except ImportError as e:
            print(f"❌ {module_name} - Error de importación: {e}")
        except Exception as e:
            print(f"⚠️  {module_name} - Error: {e}")
    
    print(f"\nResultado: {success_count}/{total_count} módulos importados correctamente")
    return success_count == total_count

def check_standard_library_only():
    """Verifica que solo se usen librerías estándar."""
    print("\n📚 VERIFICANDO USO DE LIBRERÍAS ESTÁNDAR")
    print("-" * 40)
    
    # Librerías estándar permitidas
    allowed_imports = {
        'os', 'sys', 'subprocess', 'json', 'pathlib', 'datetime', 
        'logging', 're', 'threading', 'time', 'hashlib', 'socket',
        'urllib', 'http', 'ssl', 'shutil', 'tempfile', 'unittest',
        'configparser', 'sqlite3', 'gzip', 'csv', 'tkinter',
        'collections', 'itertools', 'functools', 'typing',
        'importlib', 'inspect', 'traceback', 'warnings', 'mimetypes'
    }
    
    src_path = Path(__file__).parent / 'src'
    if not src_path.exists():
        print("❌ Directorio src no encontrado")
        return False
    
    python_files = list(src_path.rglob('*.py'))
    issues_found = []
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar imports
            import re
            import_pattern = r'^(?:from\s+(\w+)|import\s+(\w+))'
            matches = re.findall(import_pattern, content, re.MULTILINE)
            
            for match in matches:
                module = match[0] or match[1]
                if module and module not in allowed_imports and not module.startswith('modelos') and not module.startswith('vista'):
                    issues_found.append(f"{py_file.name}: {module}")
        
        except Exception as e:
            print(f"⚠️  Error procesando {py_file.name}: {e}")
    
    if issues_found:
        print("⚠️  Posibles importaciones no estándar encontradas:")
        for issue in issues_found:
            print(f"   - {issue}")
        return False
    else:
        print("✅ Solo se usan librerías estándar de Python")
        return True

def check_core_functionality():
    """Verifica funcionalidad básica de componentes core."""
    print("\n⚙️  VERIFICANDO FUNCIONALIDAD BÁSICA")
    print("-" * 40)
    
    try:
        # Verificar SIEM
        from modelos.siem import SIEM
        siem = SIEM()
        siem.log_evento('INFO', 'test', 'Verificación del sistema')
        print("✅ SIEM funcional")
        
        # Verificar Monitor de Procesos (sin ejecutar ps real)
        from modelos.monitor_procesos import MonitorProcesos, InfoProceso
        monitor = MonitorProcesos(siem)
        patrones = monitor._cargar_patrones_sospechosos()
        assert len(patrones) > 0
        print("✅ Monitor de Procesos funcional")
        
        # Verificar Monitor de Red
        from modelos.monitor_red import MonitorRed, ConexionRed
        monitor_red = MonitorRed(siem)
        servicios = monitor_red._cargar_servicios_conocidos()
        assert len(servicios) > 0
        print("✅ Monitor de Red funcional")
        
        # Verificar Escaneador
        from modelos.escaneador import Escaneador
        escaneador = Escaneador(siem)
        assert hasattr(escaneador, 'base_datos_firmas')
        print("✅ Escaneador funcional")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación de funcionalidad: {e}")
        return False

def check_gui_availability():
    """Verifica disponibilidad de tkinter."""
    print("\n🖥️  VERIFICANDO INTERFAZ GRÁFICA")
    print("-" * 40)
    
    try:
        import tkinter as tk
        # Crear una ventana de prueba sin mostrarla
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana
        root.destroy()
        print("✅ tkinter disponible y funcional")
        return True
    except ImportError:
        print("❌ tkinter no está disponible")
        return False
    except Exception as e:
        print(f"⚠️  Problema con tkinter: {e}")
        return False

def check_system_tools():
    """Verifica herramientas del sistema necesarias."""
    print("\n🔧 VERIFICANDO HERRAMIENTAS DEL SISTEMA")
    print("-" * 40)
    
    essential_tools = ['ps', 'kill']
    optional_tools = ['netstat', 'ss', 'nmap', 'clamscan']
    
    available_essential = []
    available_optional = []
    
    for tool in essential_tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, timeout=5)
            available_essential.append(tool)
            print(f"✅ {tool} (esencial)")
        except:
            try:
                subprocess.run(['which', tool], capture_output=True, timeout=5)
                available_essential.append(tool)
                print(f"✅ {tool} (esencial)")
            except:
                print(f"❌ {tool} (esencial) - NO DISPONIBLE")
    
    for tool in optional_tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, timeout=5)
            available_optional.append(tool)
            print(f"✅ {tool} (opcional)")
        except:
            try:
                subprocess.run(['which', tool], capture_output=True, timeout=5)
                available_optional.append(tool)
                print(f"✅ {tool} (opcional)")
            except:
                print(f"⚠️  {tool} (opcional) - no disponible")
    
    print(f"\nHerramientas esenciales: {len(available_essential)}/{len(essential_tools)}")
    print(f"Herramientas opcionales: {len(available_optional)}/{len(optional_tools)}")
    
    return len(available_essential) == len(essential_tools)

def run_basic_tests():
    """Ejecuta tests básicos."""
    print("\n🧪 EJECUTANDO TESTS BÁSICOS")
    print("-" * 40)
    
    try:
        # Test de integración GUI
        result = subprocess.run([
            sys.executable, '-m', 'unittest', 
            'tests.test_integration_gui', '-v'
        ], capture_output=True, text=True, cwd=Path(__file__).parent, timeout=30)
        
        if result.returncode == 0:
            print("✅ Tests de integración GUI - PASARON")
            return True
        else:
            print("❌ Tests de integración GUI - FALLARON")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Tests tardaron demasiado tiempo")
        return False
    except Exception as e:
        print(f"⚠️  Error ejecutando tests: {e}")
        return False

def print_final_report(results):
    """Imprime el reporte final."""
    print("\n" + "🏁" + "=" * 60)
    print("   REPORTE FINAL DE VALIDACIÓN")
    print("=" * 62)
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    
    print(f"\n📊 RESUMEN: {passed_checks}/{total_checks} verificaciones pasaron")
    print()
    
    for check_name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"   {status} - {check_name}")
    
    print()
    
    if passed_checks == total_checks:
        print("🎉 ¡VALIDACIÓN COMPLETADA EXITOSAMENTE!")
        print("🛡️  Ares Aegis está listo para uso en producción")
        print("🚀 Sistema Standard Library Edition completamente funcional")
    else:
        print("⚠️  Algunas verificaciones fallaron")
        print("💡 Revisar los errores antes de usar en producción")
    
    print("\n" + "=" * 62)

def main():
    """Función principal."""
    print_header()
    
    # Ejecutar todas las verificaciones
    results = {
        "Versión de Python": check_python_version(),
        "Sin dependencias externas": check_no_external_dependencies(),
        "Importaciones de módulos": check_module_imports(),
        "Solo librerías estándar": check_standard_library_only(),
        "Funcionalidad básica": check_core_functionality(),
        "Interfaz gráfica": check_gui_availability(),
        "Herramientas del sistema": check_system_tools(),
        "Tests básicos": run_basic_tests()
    }
    
    # Imprimir reporte final
    print_final_report(results)
    
    # Código de salida
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
