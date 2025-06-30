#!/usr/bin/env python3
"""
Test Runner Simplificado para Ares Aegis
Ejecuta todos los tests del sistema de manera confiable

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import sys
import subprocess
import time
from pathlib import Path

class SimpleTestRunner:
    """Runner simplificado y confiable para todos los tests."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.start_time = time.time()
        self.results = {}
    
    def discover_tests(self):
        """Descubre todos los archivos de test."""
        test_files = []
        for test_file in self.test_dir.glob('test_*.py'):
            if test_file.name not in ['test_runner_completo.py', 'test_runner_simple.py']:
                test_files.append(test_file)
        return sorted(test_files)
    
    def run_single_test(self, test_file):
        """Ejecuta un test individual usando subprocess."""
        print(f"\n{'='*60}")
        print(f"🧪 EJECUTANDO: {test_file.name}")
        print('='*60)
        
        try:
            # Ejecutar el test con subprocess
            result = subprocess.run([
                sys.executable, str(test_file)
            ], capture_output=True, text=True, timeout=120)
            
            # Analizar resultado
            success = result.returncode == 0
            
            print(f"📊 Código de salida: {result.returncode}")
            
            if success:
                print("✅ TESTS PASARON")
            else:
                print("❌ TESTS FALLARON")
            
            # Mostrar salida
            if result.stdout:
                print("\n📋 SALIDA:")
                print(result.stdout)
            
            if result.stderr:
                print("\n⚠️ ERRORES:")
                print(result.stderr)
            
            self.results[test_file.name] = {
                'success': success,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            return success
            
        except subprocess.TimeoutExpired:
            print("⏰ TIMEOUT - Test tomó más de 2 minutos")
            self.results[test_file.name] = {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Test timeout after 120 seconds'
            }
            return False
            
        except Exception as e:
            print(f"💥 ERROR EJECUTANDO TEST: {e}")
            self.results[test_file.name] = {
                'success': False,
                'returncode': -2,
                'stdout': '',
                'stderr': str(e)
            }
            return False
    
    def run_all_tests(self):
        """Ejecuta todos los tests."""
        print("🚀 INICIANDO TESTS DE ARES AEGIS")
        print("="*60)
        
        test_files = self.discover_tests()
        print(f"📁 Tests encontrados: {len(test_files)}")
        
        for test_file in test_files:
            print(f"   - {test_file.name}")
        
        print()
        
        successful_tests = 0
        failed_tests = 0
        
        for test_file in test_files:
            success = self.run_single_test(test_file)
            if success:
                successful_tests += 1
            else:
                failed_tests += 1
        
        # Calcular tiempo total
        total_time = time.time() - self.start_time
        
        # Mostrar resumen
        self.show_summary(successful_tests, failed_tests, total_time)
        
        return failed_tests == 0
    
    def show_summary(self, successful, failed, total_time):
        """Muestra resumen final."""
        total = successful + failed
        
        print(f"\n{'='*60}")
        print("📊 RESUMEN FINAL")
        print('='*60)
        
        print(f"⏱️  Tiempo total: {total_time:.2f} segundos")
        print(f"📁 Total de archivos: {total}")
        print(f"✅ Exitosos: {successful}")
        print(f"❌ Fallidos: {failed}")
        
        if total > 0:
            success_rate = (successful / total) * 100
            print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        print("\n📋 DETALLES POR ARCHIVO:")
        for test_name, result in self.results.items():
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {test_name}")
            if not result['success']:
                print(f"      → Código: {result['returncode']}")
                if result['stderr']:
                    error_lines = result['stderr'].split('\n')[:3]  # Primeras 3 líneas
                    for line in error_lines:
                        if line.strip():
                            print(f"      → {line.strip()}")
        
        print()
        
        if failed == 0:
            print("🎉 ¡TODOS LOS TESTS PASARON!")
            print("   El sistema está listo para producción.")
        else:
            print("⚠️  ALGUNOS TESTS FALLARON")
            print("   Revisar errores antes de continuar.")
        
        print(f"\nCódigo de salida: {1 if failed > 0 else 0}")
    
    def check_environment(self):
        """Verifica el entorno antes de ejecutar tests."""
        print("🔍 VERIFICANDO ENTORNO")
        print("-" * 30)
        
        # Python version
        python_version = sys.version_info
        print(f"🐍 Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Directorio de trabajo
        print(f"📁 Directorio: {os.getcwd()}")
        
        # Estructura del proyecto
        project_root = Path(__file__).parent.parent
        required_paths = [
            project_root / 'src',
            project_root / 'src' / 'modelos',
            project_root / 'src' / 'vista',
            project_root / 'tests'
        ]
        
        all_ok = True
        for path in required_paths:
            if path.exists():
                print(f"✅ {path.relative_to(project_root)}")
            else:
                print(f"❌ {path.relative_to(project_root)} (FALTA)")
                all_ok = False
        
        # Módulos críticos
        critical_modules = ['tkinter', 'hashlib', 'subprocess', 'unittest']
        for module in critical_modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError:
                print(f"❌ {module} (FALTA)")
                all_ok = False
        
        print()
        if all_ok:
            print("🎯 Entorno listo para ejecutar tests")
        else:
            print("⚠️  Problemas en el entorno detectados")
        
        return all_ok


def main():
    """Función principal."""
    runner = SimpleTestRunner()
    
    print("🛡️  ARES AEGIS - TEST RUNNER")
    print("="*60)
    
    # Verificar entorno
    if not runner.check_environment():
        print("❌ Entorno no está listo")
        return 1
    
    # Ejecutar tests
    success = runner.run_all_tests()
    
    return 0 if success else 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Interrumpido por el usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
