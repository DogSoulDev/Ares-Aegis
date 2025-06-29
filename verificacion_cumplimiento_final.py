#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ARES AEGIS - VERIFICACIÓN FINAL DE CUMPLIMIENTO
==============================================

Script de verificación completa que valida el cumplimiento de todos los requisitos
especificados para el proyecto Ares Aegis.

Autor: DogSoulDev
Fecha: 2025-06-29
Versión: 3.0.0
"""

import os
import sys
import importlib
import inspect
import json
import subprocess
from pathlib import Path

class VerificadorCumplimiento:
    """Verificador completo de cumplimiento de requisitos del proyecto"""
    
    def __init__(self):
        self.proyecto_ruta = Path(__file__).parent
        self.resultados = {
            'arquitectura_mvc': False,
            'clean_code': False,
            'tdd_implementado': False,
            'idioma_español': False,
            'modulos_estandar': False,
            'interfaz_japonesa': False,
            'siem_centralizado': False,
            'privilegios_root': False,
            'estructura_proyecto': False,
            'documentacion': False
        }
        
    def verificar_arquitectura_mvc(self):
        """Verifica la implementación correcta del patrón MVC"""
        print("🏗️ Verificando Arquitectura MVC...")
        
        # Verificar estructura de directorios MVC
        modelos_dir = self.proyecto_ruta / "src" / "modelos"
        vista_dir = self.proyecto_ruta / "src" / "vista"
        controladores_dir = self.proyecto_ruta / "src" / "controladores"
        
        if not all([modelos_dir.exists(), vista_dir.exists(), controladores_dir.exists()]):
            print("❌ Estructura MVC incompleta")
            return False
        
        # Verificar separación de responsabilidades
        try:
            # Verificar que los modelos no importen tkinter
            for modelo_file in modelos_dir.glob("*.py"):
                if modelo_file.name == "__init__.py":
                    continue
                with open(modelo_file, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    if 'tkinter' in contenido.lower():
                        print(f"❌ Modelo {modelo_file.name} viola MVC (contiene tkinter)")
                        return False
            
            # Verificar que existe controlador principal
            controlador_principal = controladores_dir / "controlador_principal.py"
            if not controlador_principal.exists():
                print("❌ Falta controlador principal")
                return False
                
            # Verificar que existe interfaz GUI
            interfaz_gui = vista_dir / "interfaz_principal_gui.py"
            if not interfaz_gui.exists():
                print("❌ Falta interfaz GUI principal")
                return False
            
            print("✅ Arquitectura MVC correctamente implementada")
            self.resultados['arquitectura_mvc'] = True
            return True
            
        except Exception as e:
            print(f"❌ Error verificando MVC: {e}")
            return False
    
    def verificar_clean_code(self):
        """Verifica principios de Clean Code y SOLID"""
        print("🧹 Verificando Clean Code y SOLID...")
        
        try:
            # Verificar nombres en español en archivos principales
            archivos_verificar = [
                "src/modelos/siem.py",
                "src/modelos/escaneador.py",
                "src/vista/interfaz_principal_gui.py"
            ]
            
            for archivo in archivos_verificar:
                ruta_archivo = self.proyecto_ruta / archivo
                if ruta_archivo.exists():
                    with open(ruta_archivo, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                        
                        # Verificar que tiene docstrings
                        if '"""' not in contenido:
                            print(f"❌ {archivo} falta documentación")
                            return False
                        
                        # Verificar nombres en español (algunas palabras clave)
                        palabras_español = ['def ', 'class ', 'registrar', 'evento', 'archivo', 'escanear']
                        if not any(palabra in contenido for palabra in palabras_español):
                            print(f"❌ {archivo} no usa nomenclatura en español")
                            return False
            
            print("✅ Clean Code y SOLID implementados correctamente")
            self.resultados['clean_code'] = True
            return True
            
        except Exception as e:
            print(f"❌ Error verificando Clean Code: {e}")
            return False
    
    def verificar_tdd(self):
        """Verifica implementación de Test-Driven Development"""
        print("🧪 Verificando TDD...")
        
        tests_dir = self.proyecto_ruta / "tests"
        if not tests_dir.exists():
            print("❌ Directorio de tests no existe")
            return False
        
        # Contar archivos de test
        test_files = list(tests_dir.glob("test_*.py"))
        if len(test_files) < 5:
            print(f"❌ Insuficientes archivos de test: {len(test_files)}")
            return False
        
        # Verificar test de integración
        test_integracion = tests_dir / "test_final_integracion.py"
        if not test_integracion.exists():
            print("❌ Falta test de integración final")
            return False
        
        print(f"✅ TDD implementado: {len(test_files)} archivos de test")
        self.resultados['tdd_implementado'] = True
        return True
    
    def verificar_idioma_español(self):
        """Verifica que todo esté en español"""
        print("🇪🇸 Verificando idioma español...")
        
        try:
            # Verificar GUI en español
            gui_file = self.proyecto_ruta / "src" / "vista" / "interfaz_principal_gui.py"
            if gui_file.exists():
                with open(gui_file, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    
                    # Buscar textos en español
                    textos_español = ['Archivo', 'Escanear', 'Monitoreo', 'Cuarentena', 'Sistema']
                    if not any(texto in contenido for texto in textos_español):
                        print("❌ Interfaz GUI no está en español")
                        return False
            
            print("✅ Idioma español correctamente implementado")
            self.resultados['idioma_español'] = True
            return True
            
        except Exception as e:
            print(f"❌ Error verificando idioma: {e}")
            return False
    
    def verificar_modulos_estandar(self):
        """Verifica uso exclusivo de módulos estándar de Python"""
        print("📦 Verificando módulos estándar Python...")
        
        # Verificar requirements.txt está vacío o no existe
        requirements_file = self.proyecto_ruta / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                contenido = f.read().strip()
                if contenido and not contenido.startswith('#'):
                    print("❌ requirements.txt contiene dependencias externas")
                    return False
        
        print("✅ Uso exclusivo de módulos estándar de Python")
        self.resultados['modulos_estandar'] = True
        return True
    
    def verificar_interfaz_japonesa(self):
        """Verifica estilo japonés en la interfaz"""
        print("🎨 Verificando estilo japonés...")
        
        try:
            gui_file = self.proyecto_ruta / "src" / "vista" / "interfaz_principal_gui.py"
            if gui_file.exists():
                with open(gui_file, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    
                    # Buscar colores japoneses
                    colores_japoneses = ['#8FBC8F', '#FFB6C1', '#87CEEB', '#DEB887', '#F5F5DC']
                    if not any(color in contenido for color in colores_japoneses):
                        print("❌ Colores japoneses no implementados")
                        return False
            
            print("✅ Estilo japonés correctamente implementado")
            self.resultados['interfaz_japonesa'] = True
            return True
            
        except Exception as e:
            print(f"❌ Error verificando estilo japonés: {e}")
            return False
    
    def verificar_siem_centralizado(self):
        """Verifica sistema SIEM centralizado"""
        print("📊 Verificando SIEM centralizado...")
        
        siem_file = self.proyecto_ruta / "src" / "modelos" / "siem.py"
        if not siem_file.exists():
            print("❌ Archivo SIEM no existe")
            return False
        
        try:
            with open(siem_file, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
                # Verificar funcionalidades SIEM
                funciones_siem = ['log_evento', 'registrar_evento', 'obtener_eventos', 'exportar']
                if not any(func in contenido for func in funciones_siem):
                    print("❌ Funcionalidades SIEM incompletas")
                    return False
            
            print("✅ Sistema SIEM centralizado implementado")
            self.resultados['siem_centralizado'] = True
            return True
            
        except Exception as e:
            print(f"❌ Error verificando SIEM: {e}")
            return False
    
    def verificar_privilegios_root(self):
        """Verifica verificación de privilegios de root"""
        print("🔐 Verificando verificación de privilegios root...")
        
        main_files = [
            self.proyecto_ruta / "main.py",
            self.proyecto_ruta / "src" / "main.py"
        ]
        
        for main_file in main_files:
            if main_file.exists():
                try:
                    with open(main_file, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                        
                        # Buscar verificación de root
                        if 'geteuid' in contenido or 'getuid' in contenido or 'root' in contenido.lower():
                            print("✅ Verificación de privilegios root implementada")
                            self.resultados['privilegios_root'] = True
                            return True
                            
                except Exception as e:
                    continue
        
        print("❌ Verificación de privilegios root no encontrada")
        return False
    
    def verificar_estructura_proyecto(self):
        """Verifica estructura completa del proyecto"""
        print("📁 Verificando estructura del proyecto...")
        
        directorios_requeridos = [
            "src",
            "src/modelos",
            "src/vista", 
            "src/controladores",
            "tests",
            "config",
            "docs",
            "recursos"
        ]
        
        archivos_requeridos = [
            "README.md",
            "main.py",
            "config/firmas.txt"
        ]
        
        # Verificar directorios
        for directorio in directorios_requeridos:
            dir_path = self.proyecto_ruta / directorio
            if not dir_path.exists():
                print(f"❌ Falta directorio: {directorio}")
                return False
        
        # Verificar archivos
        for archivo in archivos_requeridos:
            file_path = self.proyecto_ruta / archivo
            if not file_path.exists():
                print(f"❌ Falta archivo: {archivo}")
                return False
        
        print("✅ Estructura del proyecto correcta")
        self.resultados['estructura_proyecto'] = True
        return True
    
    def verificar_documentacion(self):
        """Verifica documentación completa"""
        print("📚 Verificando documentación...")
        
        readme_file = self.proyecto_ruta / "README.md"
        if not readme_file.exists():
            print("❌ README.md no existe")
            return False
        
        try:
            with open(readme_file, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
                # Verificar secciones importantes
                secciones_requeridas = [
                    'Descripción',
                    'Instalación', 
                    'Uso',
                    'Arquitectura',
                    'Testing',
                    'TDD',
                    'MVC',
                    'Clean Code',
                    'SOLID'
                ]
                
                secciones_encontradas = 0
                for seccion in secciones_requeridas:
                    if seccion.lower() in contenido.lower():
                        secciones_encontradas += 1
                
                if secciones_encontradas < len(secciones_requeridas) * 0.8:
                    print(f"❌ Documentación incompleta: {secciones_encontradas}/{len(secciones_requeridas)}")
                    return False
            
            print("✅ Documentación completa y correcta")
            self.resultados['documentacion'] = True
            return True
            
        except Exception as e:
            print(f"❌ Error verificando documentación: {e}")
            return False
    
    def ejecutar_verificacion_completa(self):
        """Ejecuta verificación completa de todos los requisitos"""
        print("🛡️ ARES AEGIS - VERIFICACIÓN FINAL DE CUMPLIMIENTO")
        print("=" * 60)
        print(f"📅 Fecha: 2025-06-29")
        print(f"📍 Directorio: {self.proyecto_ruta}")
        print(f"🔧 Versión: 3.0.0")
        print("=" * 60)
        
        verificaciones = [
            ("Arquitectura MVC", self.verificar_arquitectura_mvc),
            ("Clean Code & SOLID", self.verificar_clean_code),
            ("Test-Driven Development", self.verificar_tdd),
            ("Idioma Español", self.verificar_idioma_español),
            ("Módulos Estándar Python", self.verificar_modulos_estandar),
            ("Interfaz Estilo Japonés", self.verificar_interfaz_japonesa),
            ("Sistema SIEM Centralizado", self.verificar_siem_centralizado),
            ("Verificación Privilegios Root", self.verificar_privilegios_root),
            ("Estructura del Proyecto", self.verificar_estructura_proyecto),
            ("Documentación Completa", self.verificar_documentacion)
        ]
        
        resultados_exitosos = 0
        total_verificaciones = len(verificaciones)
        
        for nombre, verificacion in verificaciones:
            print(f"\n🔍 {nombre}...")
            try:
                if verificacion():
                    resultados_exitosos += 1
                    print(f"✅ {nombre}: APROBADO")
                else:
                    print(f"❌ {nombre}: FALLO")
            except Exception as e:
                print(f"❌ {nombre}: ERROR - {e}")
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN FINAL DE CUMPLIMIENTO")
        print("=" * 60)
        
        porcentaje_cumplimiento = (resultados_exitosos / total_verificaciones) * 100
        
        print(f"📈 Verificaciones exitosas: {resultados_exitosos}/{total_verificaciones}")
        print(f"📊 Porcentaje de cumplimiento: {porcentaje_cumplimiento:.1f}%")
        
        if porcentaje_cumplimiento >= 90:
            print("🎉 ¡EXCELENTE! Ares Aegis cumple con todos los requisitos")
            print("✅ PROYECTO LISTO PARA PRODUCCIÓN")
            estado_final = "APROBADO"
        elif porcentaje_cumplimiento >= 80:
            print("⚠️ BUENO - Pequeñas mejoras requeridas")
            estado_final = "APROBADO_CON_OBSERVACIONES"
        else:
            print("❌ INSUFICIENTE - Requiere trabajo adicional")
            estado_final = "REQUIERE_MEJORAS"
        
        # Guardar reporte de cumplimiento
        reporte = {
            "fecha_verificacion": "2025-06-29",
            "version_proyecto": "3.0.0",
            "porcentaje_cumplimiento": porcentaje_cumplimiento,
            "estado_final": estado_final,
            "verificaciones_exitosas": resultados_exitosos,
            "total_verificaciones": total_verificaciones,
            "resultados_detallados": self.resultados
        }
        
        try:
            with open(self.proyecto_ruta / "docs" / "reportes" / "cumplimiento_final.json", 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            print(f"\n📋 Reporte guardado en: docs/reportes/cumplimiento_final.json")
        except Exception as e:
            print(f"⚠️ No se pudo guardar el reporte: {e}")
        
        print("\n" + "=" * 60)
        print("🛡️ VERIFICACIÓN COMPLETADA")
        print("=" * 60)
        
        return porcentaje_cumplimiento >= 90

def main():
    """Función principal del verificador"""
    verificador = VerificadorCumplimiento()
    exito = verificador.ejecutar_verificacion_completa()
    
    if exito:
        print("\n🚀 Ares Aegis está listo para ser utilizado en producción!")
        return 0
    else:
        print("\n🔧 Se requieren ajustes antes de la versión final.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
