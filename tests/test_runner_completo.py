#!/usr/bin/env python3
"""
Test Runner Completo para Ares Aegis
Ejecuta todos los tests del sistema y genera un reporte completo

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import sys
import unittest
import time
import traceback
from pathlib import Path

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class ColoredTestResult(unittest.TextTestResult):
    """Resultado de tests con colores para mejor visualización."""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_results = {
            'passed': [],
            'failed': [],
            'errors': [],
            'skipped': []
        }
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.test_results['passed'].append(test)
        if self.verbosity > 1:
            self.stream.write(f"✅ {test._testMethodName}\n")
    
    def addError(self, test, err):
        super().addError(test, err)
        self.test_results['errors'].append((test, err))
        if self.verbosity > 1:
            self.stream.write(f"❌ {test._testMethodName} (ERROR)\n")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.test_results['failed'].append((test, err))
        if self.verbosity > 1:
            self.stream.write(f"❌ {test._testMethodName} (FAIL)\n")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.test_results['skipped'].append((test, reason))
        if self.verbosity > 1:
            self.stream.write(f"⏭️  {test._testMethodName} (SKIP: {reason})\n")


class AresAegisTestRunner:
    """Runner principal para todos los tests de Ares Aegis."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.start_time = None
        self.end_time = None
        self.total_results = {
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0
        }
    
    def discover_tests(self):
        """Descubre todos los archivos de test."""
        test_files = []
        for test_file in self.test_dir.glob('test_*.py'):
            if test_file.name != 'test_runner_completo.py':  # Evitar auto-incluirse
                test_files.append(test_file)
        return sorted(test_files)
    
    def run_single_test_file(self, test_file):
        """Ejecuta un archivo de test individual."""
        print(f"\n{'='*60}")
        print(f"EJECUTANDO: {test_file.name}")
        print('='*60)
        
        try:
            # Importar el módulo de test usando importlib
            import importlib.util
            
            spec = importlib.util.spec_from_file_location(
                test_file.stem, test_file
            )
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            # Crear suite de tests
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # Ejecutar tests
            runner = unittest.TextTestRunner(
                verbosity=2,
                resultclass=ColoredTestResult
            )
            result = runner.run(suite)
            
            # Acumular resultados
            self.total_results['passed'] += len(result.test_results['passed'])
            self.total_results['failed'] += len(result.test_results['failed'])
            self.total_results['errors'] += len(result.test_results['errors'])
            self.total_results['skipped'] += len(result.test_results['skipped'])
            
            return result
            
        except Exception as e:
            print(f"❌ Error ejecutando {test_file.name}: {e}")
            traceback.print_exc()
            self.total_results['errors'] += 1
            return None
    
    def run_all_tests(self):
        """Ejecuta todos los tests descubiertos."""
        print("🚀 INICIANDO EJECUCIÓN COMPLETA DE TESTS DE ARES AEGIS")
        print("="*70)
        
        self.start_time = time.time()
        
        test_files = self.discover_tests()
        print(f"📁 Archivos de test encontrados: {len(test_files)}")
        
        for test_file in test_files:
            print(f"   - {test_file.name}")
        
        results = []
        for test_file in test_files:
            result = self.run_single_test_file(test_file)
            results.append((test_file, result))
        
        self.end_time = time.time()
        
        return results
    
    def generate_summary_report(self, results):
        """Genera reporte resumen de todos los tests."""
        duration = self.end_time - self.start_time
        
        print(f"\n{'='*70}")
        print("📊 RESUMEN FINAL DE TESTS")
        print('='*70)
        
        print(f"⏱️  Tiempo total de ejecución: {duration:.2f} segundos")
        print(f"📁 Archivos de test ejecutados: {len(results)}")
        print()
        
        print("📈 ESTADÍSTICAS GENERALES:")
        total_tests = sum(self.total_results.values())
        print(f"   Total de tests: {total_tests}")
        print(f"   ✅ Pasaron: {self.total_results['passed']}")
        print(f"   ❌ Fallaron: {self.total_results['failed']}")
        print(f"   💥 Errores: {self.total_results['errors']}")
        print(f"   ⏭️  Omitidos: {self.total_results['skipped']}")
        
        if total_tests > 0:
            success_rate = (self.total_results['passed'] / total_tests) * 100
            print(f"   📊 Tasa de éxito: {success_rate:.1f}%")
        
        print()
        
        # Detalles por archivo
        print("📋 DETALLES POR ARCHIVO:")
        for test_file, result in results:
            if result:
                passed = len(result.test_results['passed'])
                failed = len(result.test_results['failed'])
                errors = len(result.test_results['errors'])
                skipped = len(result.test_results['skipped'])
                total_file = passed + failed + errors + skipped
                
                status = "✅" if (failed + errors) == 0 else "❌"
                print(f"   {status} {test_file.name}: {passed}/{total_file} tests pasaron")
                
                if failed > 0 or errors > 0:
                    print(f"      → {failed} fallaron, {errors} errores")
            else:
                print(f"   💥 {test_file.name}: Error de ejecución")
        
        print()
        
        # Recomendaciones
        print("💡 RECOMENDACIONES:")
        if self.total_results['failed'] > 0:
            print("   - Revisar tests fallidos y corregir código fuente")
        if self.total_results['errors'] > 0:
            print("   - Revisar errores de configuración y dependencias")
        if self.total_results['skipped'] > 0:
            print("   - Verificar dependencias opcionales para tests omitidos")
        
        if (self.total_results['failed'] + self.total_results['errors']) == 0:
            print("   🎉 ¡Todos los tests pasaron! El sistema está listo.")
        
        return success_rate if total_tests > 0 else 0
    
    def export_junit_xml(self, results, output_file="test_results.xml"):
        """Exporta resultados en formato JUnit XML para CI/CD."""
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.Element("testsuites")
            root.set("tests", str(sum(self.total_results.values())))
            root.set("failures", str(self.total_results['failed']))
            root.set("errors", str(self.total_results['errors']))
            root.set("time", str(self.end_time - self.start_time))
            
            for test_file, result in results:
                if not result:
                    continue
                    
                testsuite = ET.SubElement(root, "testsuite")
                testsuite.set("name", test_file.stem)
                testsuite.set("tests", str(result.testsRun))
                testsuite.set("failures", str(len(result.failures)))
                testsuite.set("errors", str(len(result.errors)))
                
                # Agregar casos de test exitosos
                for test in result.test_results['passed']:
                    testcase = ET.SubElement(testsuite, "testcase")
                    testcase.set("classname", test.__class__.__name__)
                    testcase.set("name", test._testMethodName)
                
                # Agregar fallos
                for test, traceback_info in result.failures:
                    testcase = ET.SubElement(testsuite, "testcase")
                    testcase.set("classname", test.__class__.__name__)
                    testcase.set("name", test._testMethodName)
                    failure = ET.SubElement(testcase, "failure")
                    failure.text = str(traceback_info[1])
                
                # Agregar errores
                for test, traceback_info in result.errors:
                    testcase = ET.SubElement(testsuite, "testcase")
                    testcase.set("classname", test.__class__.__name__)
                    testcase.set("name", test._testMethodName)
                    error = ET.SubElement(testcase, "error")
                    error.text = str(traceback_info[1])
            
            tree = ET.ElementTree(root)
            tree.write(output_file, encoding='utf-8', xml_declaration=True)
            print(f"📄 Reporte JUnit XML exportado a: {output_file}")
            
        except Exception as e:
            print(f"⚠️  No se pudo exportar reporte JUnit XML: {e}")
    
    def check_system_requirements(self):
        """Verifica los requisitos del sistema antes de ejecutar tests."""
        print("🔍 VERIFICANDO REQUISITOS DEL SISTEMA")
        print("-" * 40)
        
        requirements_ok = True
        
        # Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (se requiere 3.8+)")
            requirements_ok = False
        
        # Módulos estándar
        standard_modules = ['tkinter', 'hashlib', 'subprocess', 'pathlib', 'datetime', 'json']
        for module in standard_modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError:
                print(f"❌ {module} (requerido)")
                requirements_ok = False
        
        # Módulos opcionales
        optional_modules = ['psutil']
        for module in optional_modules:
            try:
                __import__(module)
                print(f"✅ {module} (opcional)")
            except ImportError:
                print(f"⚠️  {module} (opcional, funcionalidad limitada)")
        
        # Verificar estructura de directorios
        required_dirs = ['src', 'src/modelos', 'src/vista', 'tests']
        project_root = Path(__file__).parent.parent
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists():
                print(f"✅ {dir_name}/")
            else:
                print(f"❌ {dir_name}/ (directorio requerido)")
                requirements_ok = False
        
        print()
        if requirements_ok:
            print("🎉 Todos los requisitos básicos están disponibles")
        else:
            print("⚠️  Algunos requisitos no están disponibles")
        
        return requirements_ok


def main():
    """Función principal del test runner."""
    runner = AresAegisTestRunner()
    
    # Verificar requisitos
    if not runner.check_system_requirements():
        print("\n❌ No se pueden ejecutar todos los tests debido a requisitos faltantes")
        print("   Continuando con tests disponibles...")
    
    # Ejecutar todos los tests
    results = runner.run_all_tests()
    
    # Generar reporte
    success_rate = runner.generate_summary_report(results)
    
    # Exportar XML para CI/CD
    runner.export_junit_xml(results)
    
    # Código de salida basado en resultados
    if (runner.total_results['failed'] + runner.total_results['errors']) == 0:
        print("\n🎉 TODOS LOS TESTS PASARON - SISTEMA LISTO")
        exit_code = 0
    else:
        print(f"\n⚠️  HAY {runner.total_results['failed'] + runner.total_results['errors']} TESTS CON PROBLEMAS")
        exit_code = 1
    
    print(f"\nCódigo de salida: {exit_code}")
    return exit_code


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Runner Completo para Ares Aegis')
    parser.add_argument('--xml-output', default='test_results.xml',
                       help='Archivo de salida para reporte JUnit XML')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Salida verbose')
    
    args = parser.parse_args()
    
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Ejecución interrumpida por el usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        traceback.print_exc()
        sys.exit(2)
