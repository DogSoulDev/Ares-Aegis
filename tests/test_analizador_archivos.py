#!/usr/bin/env python3
"""
Tests para el Analizador de Archivos
Pruebas completas para metadatos, hashes y análisis de archivos.

Autor: DogSoulDev
"""

import unittest
import tempfile
import os
import hashlib
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime
import sys

# Añadir el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modelos.analizador_archivos import AnalizadorArchivos, MetadatosArchivo, HashesArchivo
from src.modelos.siem import SIEM


class TestMetadatosArchivo(unittest.TestCase):
    """Tests para la clase MetadatosArchivo."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "archivo_test.txt")
        
        # Crear archivo de prueba
        with open(self.test_file, 'w') as f:
            f.write("Contenido de prueba para el archivo de test")
    
    def tearDown(self):
        """Limpieza después de cada test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_metadatos_archivo_existente(self):
        """Test de extracción de metadatos de archivo existente."""
        metadatos = MetadatosArchivo(self.test_file)
        
        self.assertTrue(metadatos.existe)
        self.assertEqual(metadatos.nombre, "archivo_test.txt")
        self.assertEqual(metadatos.extension, ".txt")
        self.assertTrue(metadatos.tamaño_bytes > 0)
        self.assertTrue(metadatos.es_archivo_regular)
        self.assertFalse(metadatos.es_directorio)
        self.assertIsNotNone(metadatos.fecha_modificacion)
        self.assertIsNotNone(metadatos.fecha_acceso)
        self.assertIsNotNone(metadatos.fecha_creacion)
    
    def test_metadatos_archivo_inexistente(self):
        """Test de metadatos para archivo que no existe."""
        archivo_inexistente = os.path.join(self.temp_dir, "no_existe.txt")
        metadatos = MetadatosArchivo(archivo_inexistente)
        
        self.assertFalse(metadatos.existe)
        self.assertEqual(metadatos.tamaño_bytes, 0)
        self.assertFalse(metadatos.es_archivo_regular)
        self.assertEqual(metadatos.error_acceso, "Archivo no accesible")
    
    def test_metadatos_directorio(self):
        """Test de metadatos para un directorio."""
        metadatos = MetadatosArchivo(self.temp_dir)
        
        self.assertTrue(metadatos.existe)
        self.assertTrue(metadatos.es_directorio)
        self.assertFalse(metadatos.es_archivo_regular)
    
    def test_to_dict(self):
        """Test de conversión de metadatos a diccionario."""
        metadatos = MetadatosArchivo(self.test_file)
        datos_dict = metadatos.to_dict()
        
        self.assertIsInstance(datos_dict, dict)
        self.assertIn('ruta_archivo', datos_dict)
        self.assertIn('existe', datos_dict)
        self.assertIn('nombre', datos_dict)
        self.assertIn('tamaño', datos_dict)
        self.assertIn('fechas', datos_dict)
        self.assertIn('permisos', datos_dict)
        self.assertIn('tipo_archivo', datos_dict)
        self.assertTrue(datos_dict['existe'])
    
    def test_permisos_archivo(self):
        """Test de detección de permisos de archivo."""
        metadatos = MetadatosArchivo(self.test_file)
        
        self.assertIsNotNone(metadatos.permisos_octal)
        self.assertIsNotNone(metadatos.permisos_legibles)
        self.assertTrue(metadatos.es_legible)
        # En sistemas Unix, los archivos nuevos suelen ser escribibles por defecto
        self.assertTrue(metadatos.es_escribible)


class TestHashesArchivo(unittest.TestCase):
    """Tests para la clase HashesArchivo."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "hash_test.txt")
        self.contenido_test = "Contenido específico para calcular hashes"
        
        # Crear archivo de prueba
        with open(self.test_file, 'w') as f:
            f.write(self.contenido_test)
    
    def tearDown(self):
        """Limpieza después de cada test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_calculo_todos_hashes(self):
        """Test de cálculo de todos los tipos de hash."""
        calculador = HashesArchivo(self.test_file)
        hashes = calculador.calcular_todos_los_hashes()
        
        self.assertIn('md5', hashes)
        self.assertIn('sha1', hashes)
        self.assertIn('sha256', hashes)
        self.assertIn('sha512', hashes)
        
        # Verificar que los hashes no están vacíos
        for algoritmo, hash_valor in hashes.items():
            self.assertNotEqual(hash_valor, '')
            self.assertIsInstance(hash_valor, str)
    
    def test_hash_especifico_md5(self):
        """Test de cálculo de hash MD5 específico."""
        calculador = HashesArchivo(self.test_file)
        hash_md5 = calculador.calcular_hash_especifico('md5')
        
        # Calcular hash esperado manualmente
        hash_esperado = hashlib.md5(self.contenido_test.encode()).hexdigest()
        
        self.assertEqual(hash_md5, hash_esperado)
    
    def test_hash_especifico_sha256(self):
        """Test de cálculo de hash SHA256 específico."""
        calculador = HashesArchivo(self.test_file)
        hash_sha256 = calculador.calcular_hash_especifico('sha256')
        
        # Calcular hash esperado manualmente
        hash_esperado = hashlib.sha256(self.contenido_test.encode()).hexdigest()
        
        self.assertEqual(hash_sha256, hash_esperado)
    
    def test_algoritmo_no_soportado(self):
        """Test de manejo de algoritmo de hash no soportado."""
        calculador = HashesArchivo(self.test_file)
        
        with self.assertRaises(ValueError):
            calculador.calcular_hash_especifico('algoritmo_inexistente')
    
    def test_archivo_inexistente(self):
        """Test de manejo de archivo inexistente para cálculo de hash."""
        archivo_inexistente = os.path.join(self.temp_dir, "no_existe.txt")
        calculador = HashesArchivo(archivo_inexistente)
        
        hashes = calculador.calcular_todos_los_hashes()
        
        # Todos los hashes deben estar vacíos
        for hash_valor in hashes.values():
            self.assertEqual(hash_valor, '')
        
        self.assertIsNotNone(calculador.error)
    
    def test_tiempo_calculo_registrado(self):
        """Test de que se registra el tiempo de cálculo."""
        calculador = HashesArchivo(self.test_file)
        calculador.calcular_todos_los_hashes()
        
        self.assertGreater(calculador.tiempo_calculo, 0)
        self.assertIsInstance(calculador.tiempo_calculo, float)


class TestAnalizadorArchivos(unittest.TestCase):
    """Tests para la clase AnalizadorArchivos."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "analisis_test.txt")
        self.siem_mock = Mock(spec=SIEM)
        
        # Crear archivo de prueba
        with open(self.test_file, 'w') as f:
            f.write("Contenido para análisis completo del archivo")
        
        self.analizador = AnalizadorArchivos(siem=self.siem_mock)
    
    def tearDown(self):
        """Limpieza después de cada test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analisis_completo_archivo(self):
        """Test de análisis completo de un archivo."""
        resultado = self.analizador.analizar_archivo_completo(self.test_file)
        
        self.assertIn('timestamp_analisis', resultado)
        self.assertIn('metadatos', resultado)
        self.assertIn('hashes', resultado)
        self.assertIn('analisis_completado', resultado)
        
        self.assertTrue(resultado['analisis_completado'])
        self.assertTrue(resultado['metadatos']['existe'])
        
        # Verificar que se calcularon los hashes
        hashes = resultado['hashes']
        self.assertIn('md5', hashes)
        self.assertIn('sha256', hashes)
        self.assertNotEqual(hashes['md5'], '')
    
    def test_analisis_archivo_inexistente(self):
        """Test de análisis de archivo que no existe."""
        archivo_inexistente = os.path.join(self.temp_dir, "no_existe.txt")
        resultado = self.analizador.analizar_archivo_completo(archivo_inexistente)
        
        self.assertFalse(resultado['metadatos']['existe'])
        self.assertFalse(resultado['analisis_completado'])
        # No deben calcularse hashes para archivos inexistentes
        self.assertEqual(resultado['hashes'], {})
    
    def test_analisis_directorio(self):
        """Test de análisis de directorio completo."""
        # Crear varios archivos de prueba
        archivos_test = ['archivo1.txt', 'archivo2.py', 'archivo3.log']
        for nombre_archivo in archivos_test:
            ruta_archivo = os.path.join(self.temp_dir, nombre_archivo)
            with open(ruta_archivo, 'w') as f:
                f.write(f"Contenido de {nombre_archivo}")
        
        resultados = self.analizador.analizar_directorio(self.temp_dir)
        
        # Debe incluir todos los archivos creados + el archivo original del setUp
        self.assertGreaterEqual(len(resultados), len(archivos_test))
        
        # Verificar que cada resultado tiene la estructura correcta
        for resultado in resultados:
            self.assertIn('metadatos', resultado)
            self.assertIn('hashes', resultado)
            self.assertIn('timestamp_analisis', resultado)
    
    def test_analisis_directorio_recursivo(self):
        """Test de análisis recursivo de directorio."""
        # Crear subdirectorio con archivos
        subdir = os.path.join(self.temp_dir, "subdirectorio")
        os.makedirs(subdir)
        
        archivo_subdir = os.path.join(subdir, "archivo_sub.txt")
        with open(archivo_subdir, 'w') as f:
            f.write("Archivo en subdirectorio")
        
        resultados_no_recursivo = self.analizador.analizar_directorio(self.temp_dir, recursivo=False)
        resultados_recursivo = self.analizador.analizar_directorio(self.temp_dir, recursivo=True)
        
        # El análisis recursivo debe encontrar más archivos
        self.assertGreater(len(resultados_recursivo), len(resultados_no_recursivo))
    
    def test_comparacion_hashes(self):
        """Test de comparación de hashes."""
        hash1 = "abcd1234"
        hash2 = "ABCD1234"  # Mismo hash en mayúsculas
        hash3 = "efgh5678"
        
        self.assertTrue(self.analizador.comparar_hashes(hash1, hash2))
        self.assertFalse(self.analizador.comparar_hashes(hash1, hash3))
    
    def test_verificacion_integridad_archivo(self):
        """Test de verificación de integridad contra hash conocido."""
        # Calcular hash del archivo de prueba
        with open(self.test_file, 'rb') as f:
            contenido = f.read()
            hash_esperado = hashlib.sha256(contenido).hexdigest()
        
        # Verificar que el archivo coincide con su propio hash
        resultado = self.analizador.verificar_archivo_contra_hash(
            self.test_file, hash_esperado, 'sha256'
        )
        
        self.assertTrue(resultado)
        
        # Verificar que no coincide con un hash diferente
        hash_falso = "0123456789abcdef" * 4  # Hash falso de 64 caracteres
        resultado_falso = self.analizador.verificar_archivo_contra_hash(
            self.test_file, hash_falso, 'sha256'
        )
        
        self.assertFalse(resultado_falso)
    
    def test_integracion_siem_logging(self):
        """Test de integración con SIEM para logging."""
        self.analizador.analizar_archivo_completo(self.test_file)
        
        # Verificar que se llamó al SIEM para logging
        self.siem_mock.log_evento.assert_called()
        
        # Verificar que se registraron eventos INFO
        llamadas = self.siem_mock.log_evento.call_args_list
        eventos_info = [call for call in llamadas if call[0][0] == 'INFO']
        self.assertGreater(len(eventos_info), 0)
    
    def test_analizador_sin_siem(self):
        """Test de funcionamiento sin SIEM."""
        analizador_sin_siem = AnalizadorArchivos()
        resultado = analizador_sin_siem.analizar_archivo_completo(self.test_file)
        
        # Debe funcionar normalmente sin SIEM
        self.assertIn('metadatos', resultado)
        self.assertIn('hashes', resultado)
        self.assertTrue(resultado['analisis_completado'])
    
    def test_generar_reporte_markdown(self):
        """Test de generación de reporte en formato Markdown."""
        resultado = self.analizador.analizar_archivo_completo(self.test_file)
        reporte = self.analizador.generar_reporte_markdown(resultado)
        
        self.assertIsInstance(reporte, str)
        self.assertIn("# Análisis de Archivo:", reporte)
        self.assertIn("## Información General", reporte)
        self.assertIn("## Hashes Criptográficos", reporte)
        self.assertIn("*Análisis realizado el", reporte)
        
        # Verificar que contiene información específica del archivo
        nombre_archivo = resultado['metadatos']['nombre']
        self.assertIn(nombre_archivo, reporte)


class TestIntegracionCompleta(unittest.TestCase):
    """Tests de integración completa del sistema."""
    
    def setUp(self):
        """Configuración inicial para tests de integración."""
        self.temp_dir = tempfile.mkdtemp()
        self.siem = SIEM()
        self.analizador = AnalizadorArchivos(siem=self.siem)
    
    def tearDown(self):
        """Limpieza después de cada test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_flujo_completo_analisis(self):
        """Test del flujo completo de análisis de archivos."""
        # Crear archivo de prueba
        archivo_test = os.path.join(self.temp_dir, "flujo_completo.txt")
        contenido = "Archivo para test de flujo completo de análisis"
        
        with open(archivo_test, 'w') as f:
            f.write(contenido)
        
        # Realizar análisis completo
        resultado = self.analizador.analizar_archivo_completo(archivo_test)
        
        # Verificar estructura completa del resultado
        self.assertTrue(resultado['analisis_completado'])
        
        metadatos = resultado['metadatos']
        self.assertEqual(metadatos['nombre'], "flujo_completo.txt")
        self.assertTrue(metadatos['existe'])
        self.assertEqual(metadatos['extension'], ".txt")
        
        hashes = resultado['hashes']
        self.assertIn('sha256', hashes)
        
        # Verificar integridad usando el hash calculado
        hash_sha256 = hashes['sha256']
        verificacion = self.analizador.verificar_archivo_contra_hash(
            archivo_test, hash_sha256, 'sha256'
        )
        self.assertTrue(verificacion)
        
        # Generar reporte
        reporte = self.analizador.generar_reporte_markdown(resultado)
        self.assertIn("flujo_completo.txt", reporte)
        self.assertIn(hash_sha256, reporte)


if __name__ == '__main__':
    unittest.main(verbosity=2)
