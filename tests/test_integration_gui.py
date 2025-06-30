#!/usr/bin/env python3
"""
Test de integración para la interfaz GUI
Prueba la integración de los módulos de monitoreo con la GUI principal

Autor: DogSoulDev
Versión: 2.0.0
"""

import unittest
import sys
import os
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock

# Agregar src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from vista.interfaz_principal_gui import InterfazPrincipalGUI, MODULOS_MONITOREO_DISPONIBLES
except ImportError as e:
    print(f"Error importando GUI: {e}")
    sys.exit(1)


class TestIntegracionGUI(unittest.TestCase):
    """Tests de integración para la interfaz GUI."""
    
    def setUp(self):
        """Configurar test de integración."""
        self.root = tk.Tk()
        self.root.withdraw()  # Ocultar ventana durante tests
        
        # Mock del SIEM y otros módulos
        with patch('vista.interfaz_principal_gui.SIEM') as mock_siem_class:
            with patch('vista.interfaz_principal_gui.Escaneador') as mock_escaneador:
                with patch('vista.interfaz_principal_gui.FIM') as mock_fim:
                    with patch('vista.interfaz_principal_gui.GestorCuarentena') as mock_cuarentena:
                        with patch('vista.interfaz_principal_gui.IntegracionExterna') as mock_integracion:
                            # Configurar mocks
                            self.mock_siem = Mock()
                            mock_siem_class.return_value = self.mock_siem
                            
                            # Crear instancia de GUI
                            with patch('os.geteuid', return_value=0):  # Simular root
                                self.gui = InterfazPrincipalGUI(self.root)
    
    def tearDown(self):
        """Limpiar después del test."""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_inicializacion_gui(self):
        """Prueba la inicialización correcta de la GUI."""
        self.assertIsNotNone(self.gui)
        self.assertEqual(self.gui.ventana_maestra, self.root)
        self.assertIsNotNone(self.gui.siem)
        self.assertIsNotNone(self.gui.escaneador)
        self.assertIsNotNone(self.gui.fim)
        self.assertIsNotNone(self.gui.gestor_cuarentena)
        self.assertIsNotNone(self.gui.integracion_externa)
    
    def test_modulos_monitoreo_disponibles(self):
        """Prueba si los módulos de monitoreo están disponibles."""
        if MODULOS_MONITOREO_DISPONIBLES:
            self.assertTrue(hasattr(self.gui, 'monitor_procesos'))
            self.assertTrue(hasattr(self.gui, 'monitor_red'))
            self.assertTrue(hasattr(self.gui, 'analizador_logs'))
    
    def test_navegacion_menus(self):
        """Prueba la navegación entre menús."""
        # Test menú principal
        self.gui.crear_menu_principal()
        
        # Test menú de análisis
        self.gui.mostrar_menu_analisis_archivos()
        self.assertIsNotNone(self.gui.area_resultados)
        self.assertIsNotNone(self.gui.entrada_ruta_analisis)
        
        # Test menú de monitoreo
        self.gui.mostrar_menu_monitoreo()
        self.assertIsNotNone(self.gui.area_resultados)
        
        # Test menú de cuarentena
        self.gui.mostrar_menu_logs_cuarentena()
        self.assertIsNotNone(self.gui.area_resultados)
        
        # Test menú de herramientas
        self.gui.mostrar_menu_herramientas()
        self.assertIsNotNone(self.gui.area_resultados)
    
    @patch('tkinter.filedialog.askopenfilename')
    def test_seleccion_archivo(self, mock_file_dialog):
        """Prueba la selección de archivos."""
        mock_file_dialog.return_value = '/test/archivo.txt'
        
        self.gui.mostrar_menu_analisis_archivos()
        self.gui._seleccionar_archivo()
        
        self.assertEqual(self.gui.entrada_ruta_analisis.get(), '/test/archivo.txt')
        mock_file_dialog.assert_called_once()
    
    @patch('tkinter.filedialog.askdirectory')
    def test_seleccion_directorio(self, mock_dir_dialog):
        """Prueba la selección de directorios."""
        mock_dir_dialog.return_value = '/test/directorio'
        
        self.gui.mostrar_menu_analisis_archivos()
        self.gui._seleccionar_directorio()
        
        self.assertEqual(self.gui.entrada_ruta_analisis.get(), '/test/directorio')
        mock_dir_dialog.assert_called_once()
    
    def test_actualizacion_area_resultados(self):
        """Prueba la actualización del área de resultados."""
        self.gui.mostrar_menu_analisis_archivos()
        
        texto_prueba = "Test de actualización"
        self.gui._actualizar_area_resultados(texto_prueba)
        
        contenido = self.gui.area_resultados.get(1.0, tk.END)
        self.assertIn(texto_prueba, contenido)
    
    @unittest.skipUnless(MODULOS_MONITOREO_DISPONIBLES, "Módulos de monitoreo no disponibles")
    def test_monitoreo_procesos_sin_errores(self):
        """Prueba que el monitoreo de procesos no genere errores."""
        # Mock del resultado del monitoreo
        resultado_mock = {
            'estadisticas': {
                'total_procesos': 100,
                'procesos_sospechosos': 2,
                'procesos_nuevos': 1,
                'uso_cpu_promedio': 25.5,
                'memoria_total_mb': 2048.0,
                'tiempo_escaneo': 1.5
            },
            'procesos_sospechosos': [],
            'procesos_nuevos': [],
            'conexiones_red': [],
            'todos_los_procesos': []
        }
        
        # Mock del método exportar_reporte_markdown
        with patch.object(self.gui, 'monitor_procesos') as mock_monitor:
            mock_monitor.escanear_sistema.return_value = resultado_mock
            mock_monitor.exportar_reporte_markdown.return_value = '/tmp/test_report.md'
            
            self.gui.mostrar_menu_monitoreo()
            
            # No debería generar excepciones
            try:
                self.gui._iniciar_monitoreo_procesos()
                success = True
            except Exception as e:
                success = False
                print(f"Error en monitoreo de procesos: {e}")
            
            self.assertTrue(success)
    
    @unittest.skipUnless(MODULOS_MONITOREO_DISPONIBLES, "Módulos de monitoreo no disponibles")
    def test_monitoreo_red_sin_errores(self):
        """Prueba que el monitoreo de red no genere errores."""
        # Mock del resultado del monitoreo
        resultado_mock = {
            'estadisticas': {
                'total_conexiones': 50,
                'conexiones_sospechosas': 1,
                'total_puertos_abiertos': 10,
                'puertos_sospechosos': 0,
                'dispositivos_en_red': 5,
                'tiempo_escaneo': 2.0
            },
            'conexiones_sospechosas': [],
            'puertos_sospechosos': [],
            'todas_las_conexiones': [],
            'puertos_abiertos': []
        }
        
        with patch.object(self.gui, 'monitor_red') as mock_monitor:
            mock_monitor.escanear_sistema_red.return_value = resultado_mock
            mock_monitor.exportar_reporte_markdown.return_value = '/tmp/test_report.md'
            
            self.gui.mostrar_menu_monitoreo()
            
            try:
                self.gui._iniciar_monitoreo_red()
                success = True
            except Exception as e:
                success = False
                print(f"Error en monitoreo de red: {e}")
            
            self.assertTrue(success)
    
    @unittest.skipUnless(MODULOS_MONITOREO_DISPONIBLES, "Módulos de monitoreo no disponibles")
    @patch('tkinter.simpledialog.askinteger')
    def test_analisis_logs_sin_errores(self, mock_dialog):
        """Prueba que el análisis de logs no genere errores."""
        mock_dialog.return_value = 24  # 24 horas
        
        # Mock del resultado del análisis
        resultado_mock = {
            'estadisticas': {
                'total_eventos': 1000,
                'eventos_sospechosos': 5,
                'ataques_brute_force': 1,
                'archivos_procesados': 3,
                'tiempo_procesamiento': 3.2
            },
            'ataques_detectados': [],
            'eventos_sospechosos': [],
            'todos_los_eventos': []
        }
        
        with patch.object(self.gui, 'analizador_logs') as mock_analizador:
            mock_analizador.analizar_periodo.return_value = resultado_mock
            mock_analizador.exportar_reporte_markdown.return_value = '/tmp/test_report.md'
            
            self.gui.mostrar_menu_herramientas()
            
            try:
                self.gui._analizar_logs_sistema()
                success = True
            except Exception as e:
                success = False
                print(f"Error en análisis de logs: {e}")
            
            self.assertTrue(success)
    
    def test_manejo_errores_modulos_no_disponibles(self):
        """Prueba el manejo de errores cuando los módulos no están disponibles."""
        # Simular que los módulos no están disponibles
        with patch('vista.interfaz_principal_gui.MODULOS_MONITOREO_DISPONIBLES', False):
            gui_sin_modulos = self.gui
            gui_sin_modulos.mostrar_menu_monitoreo()
            
            # No debería generar errores, solo mostrar mensaje
            try:
                gui_sin_modulos._iniciar_monitoreo_procesos()
                gui_sin_modulos._iniciar_monitoreo_red()
                success = True
            except AttributeError:
                # Es esperado que no existan los atributos
                success = True
            except Exception as e:
                success = False
                print(f"Error inesperado: {e}")
            
            self.assertTrue(success)
    
    def test_exportacion_reporte_markdown(self):
        """Prueba la exportación de reportes a Markdown."""
        self.gui.mostrar_menu_analisis_archivos()
        self.gui._actualizar_area_resultados("Contenido de prueba")
        
        with patch('tkinter.filedialog.asksaveasfilename') as mock_save_dialog:
            mock_save_dialog.return_value = '/tmp/test_report.md'
            
            with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
                try:
                    self.gui._exportar_resultados_markdown()
                    success = True
                except Exception as e:
                    success = False
                    print(f"Error en exportación: {e}")
                
                self.assertTrue(success)
    
    def test_validacion_formularios(self):
        """Prueba la validación de formularios."""
        self.gui.mostrar_menu_analisis_archivos()
        
        # Test con entrada vacía
        with patch('tkinter.messagebox.showerror') as mock_error:
            self.gui._escanear_archivo_interno()
            mock_error.assert_called()
    
    def test_configuracion_estilos(self):
        """Prueba que los estilos se configuren correctamente."""
        self.assertIsNotNone(self.gui.estilo)
        
        # Verificar que algunos estilos estén configurados
        estilos_configurados = self.gui.estilo.theme_names()
        self.assertIn('alt', estilos_configurados)
    
    def test_carga_iconos_sin_errores(self):
        """Prueba que la carga de iconos no genere errores."""
        # Este test verifica que el sistema maneje gracefully la ausencia de iconos
        try:
            self.gui._cargar_icono_aplicacion()
            success = True
        except Exception as e:
            success = False
            print(f"Error cargando iconos: {e}")
        
        self.assertTrue(success)


class TestCompatibilidadSistema(unittest.TestCase):
    """Tests de compatibilidad del sistema."""
    
    def test_importaciones_disponibles(self):
        """Prueba que las importaciones básicas estén disponibles."""
        try:
            import tkinter
            import tkinter.ttk
            import tkinter.messagebox
            import tkinter.filedialog
            import tkinter.simpledialog
            from tkinter.scrolledtext import ScrolledText
            success = True
        except ImportError as e:
            success = False
            print(f"Error en importaciones: {e}")
        
        self.assertTrue(success)
    
    def test_deteccion_modulos_monitoreo(self):
        """Prueba la detección de módulos de monitoreo."""
        # Esta es una prueba informativa
        print(f"Módulos de monitoreo disponibles: {MODULOS_MONITOREO_DISPONIBLES}")
        
        if MODULOS_MONITOREO_DISPONIBLES:
            try:
                from modelos.monitor_procesos import MonitorProcesos
                from modelos.monitor_red import MonitorRed
                from modelos.analizador_logs import AnalizadorLogs
                print("✅ Todos los módulos de monitoreo importados correctamente")
            except ImportError as e:
                print(f"❌ Error importando módulos de monitoreo: {e}")
        else:
            print("ℹ️ Módulos de monitoreo no disponibles en este entorno")


if __name__ == '__main__':
    # Configurar logging para tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Configurar variables de entorno para evitar errores de display
    os.environ['DISPLAY'] = ':0.0'
    
    # Ejecutar tests con nivel de verbosidad alto
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "="*60)
    print("RESUMEN DE INTEGRACIÓN GUI")
    print("="*60)
    print(f"Módulos de monitoreo disponibles: {MODULOS_MONITOREO_DISPONIBLES}")
    print("Tests de integración completados.")
    print("La GUI debería funcionar correctamente con los módulos disponibles.")
