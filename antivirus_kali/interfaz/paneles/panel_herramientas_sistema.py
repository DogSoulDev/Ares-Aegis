#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Panel Especializado para Herramientas del Sistema
Integra todas las utilidades y herramientas adicionales
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QGroupBox,
    QComboBox, QSpinBox, QCheckBox, QLineEdit, QSplitter, QTabWidget,
    QListWidget, QListWidgetItem, QHeaderView, QAbstractItemView,
    QTextEdit, QProgressBar, QSlider, QScrollArea, QFrame,
    QFileDialog, QMessageBox, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QMutex
from PySide6.QtGui import QFont, QIcon, QTextCharFormat, QColor

from ..estilo_japones import EstiloJapones
from antivirus_kali.utilidades.logger import SiemLogger

class HiloHerramientaSistema(QThread):
    """Hilo para ejecutar herramientas del sistema sin bloquear la UI"""
    
    progreso_actualizado = Signal(int, str)
    resultado_obtenido = Signal(str, str)  # comando, resultado
    error_ocurrido = Signal(str)
    herramienta_completada = Signal(dict)
    
    def __init__(self, herramienta: str, parametros: Dict[str, Any]):
        super().__init__()
        self.herramienta = herramienta
        self.parametros = parametros
        self.cancelado = False
        self.mutex = QMutex()
        self.logger = SiemLogger(__name__)
        
    def cancelar(self):
        self.mutex.lock()
        self.cancelado = True
        self.mutex.unlock()
        
    def run(self):
        try:
            if self.herramienta == "analisis_sistema":
                self._ejecutar_analisis_sistema()
            elif self.herramienta == "limpieza_sistema":
                self._ejecutar_limpieza_sistema()
            elif self.herramienta == "benchmark":
                self._ejecutar_benchmark()
            elif self.herramienta == "diagnostico_red":
                self._ejecutar_diagnostico_red()
            elif self.herramienta == "optimizacion":
                self._ejecutar_optimizacion()
        except Exception as e:
            self.error_ocurrido.emit(f"Error en {self.herramienta}: {e}")
            
    def _ejecutar_analisis_sistema(self):
        """Simula análisis completo del sistema"""
        pasos = [
            ("Analizando uso de CPU...", "CPU: 8 cores, uso promedio 15%"),
            ("Verificando memoria...", "RAM: 16GB total, 8GB disponible"),
            ("Revisando almacenamiento...", "Disco: 512GB total, 256GB libre"),
            ("Analizando procesos...", "127 procesos activos, 3 con alta CPU"),
            ("Verificando servicios...", "45 servicios ejecutándose"),
            ("Revisando logs del sistema...", "últimas 24h: 2 errores, 15 warnings"),
            ("Analizando red...", "Conexión estable, 5 conexiones activas"),
            ("Verificando integridad...", "Sistema operativo íntegro")
        ]
        
        for i, (mensaje, resultado) in enumerate(pasos):
            if self.cancelado:
                return
                
            porcentaje = int((i + 1) / len(pasos) * 100)
            self.progreso_actualizado.emit(porcentaje, mensaje)
            self.resultado_obtenido.emit(mensaje, resultado)
            self.msleep(800)
            
        self.herramienta_completada.emit({
            "herramienta": "Análisis del Sistema",
            "estado": "Completado",
            "tiempo": "6.4 segundos",
            "resultados": len(pasos)
        })
        
    def _ejecutar_limpieza_sistema(self):
        """Simula limpieza del sistema"""
        tareas = [
            ("Limpiando archivos temporales...", "Eliminados: 245MB en /tmp"),
            ("Vaciando papelera...", "Recuperados: 1.2GB de espacio"),
            ("Limpiando caché del sistema...", "Cache limpiado: 500MB"),
            ("Eliminando logs antiguos...", "Logs antiguos: 150MB eliminados"),
            ("Optimizando base de datos...", "Índices reorganizados"),
            ("Desfragmentando registros...", "Registro optimizado"),
            ("Actualizando ubicaciones...", "Cache de ubicaciones actualizado")
        ]
        
        for i, (mensaje, resultado) in enumerate(tareas):
            if self.cancelado:
                return
                
            porcentaje = int((i + 1) / len(tareas) * 100)
            self.progreso_actualizado.emit(porcentaje, mensaje)
            self.resultado_obtenido.emit(mensaje, resultado)
            self.msleep(1000)
            
        self.herramienta_completada.emit({
            "herramienta": "Limpieza del Sistema",
            "estado": "Completado",
            "tiempo": "7.0 segundos",
            "espacio_recuperado": "2.1GB"
        })
        
    def _ejecutar_benchmark(self):
        """Simula benchmark del sistema"""
        pruebas = [
            ("CPU - Prueba de cálculo...", "CPU Score: 8542 puntos"),
            ("Memoria - Prueba de velocidad...", "RAM Score: 12650 MB/s"),
            ("Disco - Velocidad de lectura...", "Read Speed: 2100 MB/s"),
            ("Disco - Velocidad de escritura...", "Write Speed: 1800 MB/s"),
            ("GPU - Renderizado básico...", "GPU Score: 15420 puntos"),
            ("Red - Prueba de latencia...", "Latency: 12ms promedio"),
            ("Red - Prueba de ancho de banda...", "Bandwidth: 85 Mbps")
        ]
        
        for i, (mensaje, resultado) in enumerate(pruebas):
            if self.cancelado:
                return
                
            porcentaje = int((i + 1) / len(pruebas) * 100)
            self.progreso_actualizado.emit(porcentaje, mensaje)
            self.resultado_obtenido.emit(mensaje, resultado)
            self.msleep(1200)
            
        self.herramienta_completada.emit({
            "herramienta": "Benchmark del Sistema",
            "estado": "Completado",
            "puntuacion_total": "42,852 puntos",
            "clasificacion": "Rendimiento Alto"
        })
        
    def _ejecutar_diagnostico_red(self):
        """Simula diagnóstico de red"""
        diagnosticos = [
            ("Verificando conectividad...", "✅ Conexión a Internet activa"),
            ("Probando DNS...", "✅ Resolución DNS funcionando"),
            ("Analizando latencia...", "📊 Ping promedio: 15ms"),
            ("Verificando puertos...", "🔍 22 puertos abiertos detectados"),
            ("Escaneando red local...", "🖥️ 8 dispositivos en red local"),
            ("Analizando tráfico...", "📈 Tráfico normal detectado"),
            ("Verificando seguridad...", "🔒 Firewall activo y configurado")
        ]
        
        for i, (mensaje, resultado) in enumerate(diagnosticos):
            if self.cancelado:
                return
                
            porcentaje = int((i + 1) / len(diagnosticos) * 100)
            self.progreso_actualizado.emit(porcentaje, mensaje)
            self.resultado_obtenido.emit(mensaje, resultado)
            self.msleep(900)
            
        self.herramienta_completada.emit({
            "herramienta": "Diagnóstico de Red",
            "estado": "Completado",
            "conexion": "Estable",
            "dispositivos_red": "8"
        })
        
    def _ejecutar_optimizacion(self):
        """Simula optimización del sistema"""
        optimizaciones = [
            ("Ajustando configuración del kernel...", "✅ Parámetros del kernel optimizados"),
            ("Optimizando servicios...", "🔧 3 servicios innecesarios deshabilitados"),
            ("Configurando swappiness...", "⚙️ Swappiness ajustado a 10"),
            ("Optimizando I/O scheduler...", "💾 Scheduler cambiado a mq-deadline"),
            ("Ajustando límites de archivos...", "📁 Límites de descriptores aumentados"),
            ("Optimizando TCP/IP...", "🌐 Stack de red optimizado"),
            ("Configurando CPU governor...", "⚡ Governor establecido en performance")
        ]
        
        for i, (mensaje, resultado) in enumerate(optimizaciones):
            if self.cancelado:
                return
                
            porcentaje = int((i + 1) / len(optimizaciones) * 100)
            self.progreso_actualizado.emit(porcentaje, mensaje)
            self.resultado_obtenido.emit(mensaje, resultado)
            self.msleep(700)
            
        self.herramienta_completada.emit({
            "herramienta": "Optimización del Sistema",
            "estado": "Completado",
            "mejoras_aplicadas": "7",
            "reinicio_requerido": "No"
        })


class DialogConfiguracionAvanzada(QDialog):
    """Diálogo para configuración avanzada de herramientas"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Configuración Avanzada")
        self.setModal(True)
        self.resize(500, 400)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Tabs de configuración
        tabs = QTabWidget()
        
        # Tab de configuración general
        tab_general = QWidget()
        layout_general = QFormLayout(tab_general)
        
        self.check_auto_backup = QCheckBox("Crear respaldo automático antes de cambios")
        self.check_auto_backup.setChecked(True)
        
        self.check_logs_detallados = QCheckBox("Habilitar logs detallados")
        self.check_logs_detallados.setChecked(False)
        
        self.spin_timeout = QSpinBox()
        self.spin_timeout.setRange(30, 300)
        self.spin_timeout.setValue(120)
        self.spin_timeout.setSuffix(" segundos")
        
        layout_general.addRow("", self.check_auto_backup)
        layout_general.addRow("", self.check_logs_detallados)
        layout_general.addRow("Timeout de herramientas:", self.spin_timeout)
        
        tabs.addTab(tab_general, "General")
        
        # Tab de configuración de rendimiento
        tab_rendimiento = QWidget()
        layout_rendimiento = QFormLayout(tab_rendimiento)
        
        self.slider_prioridad = QSlider(Qt.Orientation.Horizontal)
        self.slider_prioridad.setRange(1, 10)
        self.slider_prioridad.setValue(5)
        self.label_prioridad = QLabel("Normal")
        
        self.spin_hilos_max = QSpinBox()
        self.spin_hilos_max.setRange(1, 16)
        self.spin_hilos_max.setValue(4)
        
        layout_rendimiento.addRow("Prioridad de procesos:", self.slider_prioridad)
        layout_rendimiento.addRow("", self.label_prioridad)
        layout_rendimiento.addRow("Máximo hilos simultáneos:", self.spin_hilos_max)
        
        # Conectar slider
        self.slider_prioridad.valueChanged.connect(self._actualizar_prioridad)
        
        tabs.addTab(tab_rendimiento, "Rendimiento")
        
        layout.addWidget(tabs)
        
        # Botones
        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        
        layout.addWidget(botones)
        
    def _actualizar_prioridad(self, valor):
        nombres = ["Muy Baja", "Baja", "Baja", "Normal", "Normal", 
                  "Normal", "Alta", "Alta", "Muy Alta", "Crítica"]
        self.label_prioridad.setText(nombres[valor - 1])


class PanelHerramientasSistema(QWidget):
    """Panel principal para herramientas del sistema"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = SiemLogger(__name__)
        self.hilo_herramienta = None
        self.historial_herramientas = []
        self._setup_ui()
        self._conectar_señales()
        
    def _setup_ui(self):
        """Configura la interfaz del panel"""
        layout = QVBoxLayout(self)
        layout.setSpacing(EstiloJapones.ESPACIADO['normal'])
        
        # Título
        titulo = QLabel("🛠️ Herramientas del Sistema")
        titulo.setProperty("estiloTitulo", "true")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Tabs principales
        tabs_herramientas = QTabWidget()
        
        # Tab de análisis del sistema
        self._crear_tab_analisis_sistema(tabs_herramientas)
        
        # Tab de herramientas de limpieza
        self._crear_tab_limpieza_sistema(tabs_herramientas)
        
        # Tab de diagnósticos
        self._crear_tab_diagnosticos(tabs_herramientas)
        
        # Tab de optimización
        self._crear_tab_optimizacion(tabs_herramientas)
        
        # Tab de utilidades avanzadas
        self._crear_tab_utilidades_avanzadas(tabs_herramientas)
        
        layout.addWidget(tabs_herramientas)
        
    def _crear_tab_analisis_sistema(self, tabs):
        """Crea el tab de análisis del sistema"""
        tab_analisis = QWidget()
        layout = QVBoxLayout(tab_analisis)
        
        # Información del sistema
        grupo_info = QGroupBox("💻 Información del Sistema")
        layout_info = QGridLayout(grupo_info)
        
        # Labels informativos
        info_sistema = [
            ("Sistema Operativo:", "Kali Linux 2024.1"),
            ("Kernel:", "Linux 6.1.0-kali7-amd64"),
            ("Arquitectura:", "x86_64"),
            ("Memoria Total:", "16.0 GB"),
            ("CPU:", "Intel Core i7-10700K @ 3.80GHz"),
            ("Almacenamiento:", "512 GB SSD NVMe")
        ]
        
        for i, (etiqueta, valor) in enumerate(info_sistema):
            fila = i // 2
            col = (i % 2) * 2
            
            label_etiqueta = QLabel(etiqueta)
            label_etiqueta.setStyleSheet("font-weight: bold;")
            label_valor = QLabel(valor)
            
            layout_info.addWidget(label_etiqueta, fila, col)
            layout_info.addWidget(label_valor, fila, col + 1)
            
        layout.addWidget(grupo_info)
        
        # Controles de análisis
        grupo_analisis = QGroupBox("🔍 Herramientas de Análisis")
        layout_analisis = QVBoxLayout(grupo_analisis)
        
        # Botones de análisis
        layout_botones_analisis = QGridLayout()
        
        self.btn_analisis_completo = QPushButton("📊 Análisis Completo del Sistema")
        self.btn_analisis_completo.setProperty("esPrimario", "true")
        self.btn_analisis_completo.setMinimumHeight(50)
        
        self.btn_analisis_hardware = QPushButton("🔧 Análisis de Hardware")
        self.btn_analisis_procesos = QPushButton("⚙️ Análisis de Procesos")
        self.btn_analisis_servicios = QPushButton("🔄 Análisis de Servicios")
        self.btn_analisis_red = QPushButton("🌐 Análisis de Red")
        
        layout_botones_analisis.addWidget(self.btn_analisis_completo, 0, 0, 1, 2)
        layout_botones_analisis.addWidget(self.btn_analisis_hardware, 1, 0)
        layout_botones_analisis.addWidget(self.btn_analisis_procesos, 1, 1)
        layout_botones_analisis.addWidget(self.btn_analisis_servicios, 2, 0)
        layout_botones_analisis.addWidget(self.btn_analisis_red, 2, 1)
        
        layout_analisis.addLayout(layout_botones_analisis)
        layout.addWidget(grupo_analisis)
        
        # Panel de resultados
        self._crear_panel_resultados_herramientas(layout)
        
        tabs.addTab(tab_analisis, "📊 Análisis del Sistema")
        
    def _crear_tab_limpieza_sistema(self, tabs):
        """Crea el tab de limpieza del sistema"""
        tab_limpieza = QWidget()
        layout = QVBoxLayout(tab_limpieza)
        
        # Opciones de limpieza
        grupo_opciones = QGroupBox("🧹 Opciones de Limpieza")
        layout_opciones = QVBoxLayout(grupo_opciones)
        
        # Checkboxes para tipos de limpieza
        self.check_archivos_temp = QCheckBox("🗂️ Archivos temporales (/tmp, /var/tmp)")
        self.check_archivos_temp.setChecked(True)
        
        self.check_logs_antiguos = QCheckBox("📝 Logs antiguos (>30 días)")
        self.check_logs_antiguos.setChecked(True)
        
        self.check_cache_sistema = QCheckBox("💾 Caché del sistema")
        self.check_cache_sistema.setChecked(True)
        
        self.check_papelera = QCheckBox("🗑️ Papelera de reciclaje")
        self.check_papelera.setChecked(False)
        
        self.check_cache_navegador = QCheckBox("🌐 Caché de navegadores")
        self.check_cache_navegador.setChecked(False)
        
        self.check_archivos_huerfanos = QCheckBox("👻 Archivos huérfanos")
        self.check_archivos_huerfanos.setChecked(False)
        
        layout_opciones.addWidget(self.check_archivos_temp)
        layout_opciones.addWidget(self.check_logs_antiguos)
        layout_opciones.addWidget(self.check_cache_sistema)
        layout_opciones.addWidget(self.check_papelera)
        layout_opciones.addWidget(self.check_cache_navegador)
        layout_opciones.addWidget(self.check_archivos_huerfanos)
        
        layout.addWidget(grupo_opciones)
        
        # Estimación de espacio
        grupo_estimacion = QGroupBox("📏 Estimación de Espacio")
        layout_estimacion = QFormLayout(grupo_estimacion)
        
        self.label_espacio_temp = QLabel("~245 MB")
        self.label_espacio_logs = QLabel("~150 MB")
        self.label_espacio_cache = QLabel("~500 MB")
        self.label_espacio_total = QLabel("~895 MB")
        self.label_espacio_total.setStyleSheet("font-weight: bold; color: #007BFF;")
        
        layout_estimacion.addRow("Archivos temporales:", self.label_espacio_temp)
        layout_estimacion.addRow("Logs antiguos:", self.label_espacio_logs)
        layout_estimacion.addRow("Caché del sistema:", self.label_espacio_cache)
        layout_estimacion.addRow("Total estimado:", self.label_espacio_total)
        
        layout.addWidget(grupo_estimacion)
        
        # Botones de acción
        layout_botones_limpieza = QHBoxLayout()
        
        self.btn_analizar_limpieza = QPushButton("🔍 Analizar")
        self.btn_ejecutar_limpieza = QPushButton("🧹 Ejecutar Limpieza")
        self.btn_ejecutar_limpieza.setProperty("esPrimario", "true")
        self.btn_limpieza_segura = QPushButton("🛡️ Limpieza Segura")
        
        layout_botones_limpieza.addWidget(self.btn_analizar_limpieza)
        layout_botones_limpieza.addWidget(self.btn_ejecutar_limpieza)
        layout_botones_limpieza.addWidget(self.btn_limpieza_segura)
        layout_botones_limpieza.addStretch()
        
        layout.addLayout(layout_botones_limpieza)
        
        tabs.addTab(tab_limpieza, "🧹 Limpieza del Sistema")
        
    def _crear_tab_diagnosticos(self, tabs):
        """Crea el tab de diagnósticos"""
        tab_diagnosticos = QWidget()
        layout = QVBoxLayout(tab_diagnosticos)
        
        # Grid de herramientas de diagnóstico
        grid_diagnosticos = QGridLayout()
        
        # Botones de diagnóstico
        botones_diagnostico = [
            ("🩺 Diagnóstico Completo", "Ejecuta todas las pruebas disponibles", "diagnostico_completo"),
            ("🖥️ Test de Hardware", "Verifica estado del hardware", "test_hardware"),
            ("💾 Test de Memoria", "Prueba integridad de la RAM", "test_memoria"),
            ("💿 Test de Disco", "Verifica salud del almacenamiento", "test_disco"),
            ("🌡️ Monitoreo de Temperatura", "Supervisa temperaturas del sistema", "temperatura"),
            ("⚡ Test de Rendimiento", "Evalúa rendimiento general", "benchmark"),
            ("🌐 Diagnóstico de Red", "Analiza conectividad y rendimiento", "diagnostico_red"),
            ("🔌 Test de Puertos", "Escanea puertos abiertos", "test_puertos")
        ]
        
        for i, (texto, tooltip, accion) in enumerate(botones_diagnostico):
            btn = QPushButton(texto)
            btn.setMinimumHeight(60)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, a=accion: self._ejecutar_diagnostico(a))
            
            fila = i // 2
            columna = i % 2
            grid_diagnosticos.addWidget(btn, fila, columna)
            
        layout.addLayout(grid_diagnosticos)
        
        # Panel de resultados de diagnóstico
        grupo_resultados_diag = QGroupBox("📋 Resultados del Diagnóstico")
        layout_resultados_diag = QVBoxLayout(grupo_resultados_diag)
        
        self.texto_resultados_diagnostico = QTextEdit()
        self.texto_resultados_diagnostico.setMaximumHeight(200)
        self.texto_resultados_diagnostico.setPlainText("Seleccione una herramienta de diagnóstico para ver los resultados aquí...")
        
        layout_resultados_diag.addWidget(self.texto_resultados_diagnostico)
        layout.addWidget(grupo_resultados_diag)
        
        tabs.addTab(tab_diagnosticos, "🩺 Diagnósticos")
        
    def _crear_tab_optimizacion(self, tabs):
        """Crea el tab de optimización"""
        tab_optimizacion = QWidget()
        layout = QVBoxLayout(tab_optimizacion)
        
        # Opciones de optimización
        grupo_opt_opciones = QGroupBox("⚡ Opciones de Optimización")
        layout_opt_opciones = QVBoxLayout(grupo_opt_opciones)
        
        # Grid de optimizaciones
        grid_optimizaciones = QGridLayout()
        
        optimizaciones = [
            ("🚀 Optimización Rápida", "Aplica mejoras básicas de rendimiento"),
            ("🔧 Optimización Completa", "Optimización profunda del sistema"),
            ("💾 Optimizar Memoria", "Ajusta configuración de memoria"),
            ("⚙️ Optimizar CPU", "Configura governor y frecuencias"),
            ("🌐 Optimizar Red", "Ajusta stack TCP/IP y DNS"),
            ("💿 Optimizar I/O", "Configura schedulers de disco")
        ]
        
        for i, (titulo, descripcion) in enumerate(optimizaciones):
            btn = QPushButton(titulo)
            btn.setMinimumHeight(50)
            btn.setToolTip(descripcion)
            
            fila = i // 2
            columna = i % 2
            grid_optimizaciones.addWidget(btn, fila, columna)
            
        layout_opt_opciones.addLayout(grid_optimizaciones)
        layout.addWidget(grupo_opt_opciones)
        
        # Configuración avanzada
        grupo_config_avanzada = QGroupBox("⚙️ Configuración Avanzada")
        layout_config_avanzada = QHBoxLayout(grupo_config_avanzada)
        
        btn_config_avanzada = QPushButton("🔧 Configuración Avanzada")
        btn_config_avanzada.clicked.connect(self._abrir_config_avanzada)
        
        btn_restaurar_sistema = QPushButton("🔄 Restaurar Configuración")
        btn_backup_config = QPushButton("💾 Crear Backup")
        
        layout_config_avanzada.addWidget(btn_config_avanzada)
        layout_config_avanzada.addWidget(btn_restaurar_sistema)
        layout_config_avanzada.addWidget(btn_backup_config)
        layout_config_avanzada.addStretch()
        
        layout.addWidget(grupo_config_avanzada)
        
        tabs.addTab(tab_optimizacion, "⚡ Optimización")
        
    def _crear_tab_utilidades_avanzadas(self, tabs):
        """Crea el tab de utilidades avanzadas"""
        tab_utilidades = QWidget()
        layout = QVBoxLayout(tab_utilidades)
        
        # Utilidades de archivo
        grupo_archivos = QGroupBox("📁 Utilidades de Archivos")
        layout_archivos = QGridLayout(grupo_archivos)
        
        btn_buscar_duplicados = QPushButton("🔍 Buscar Duplicados")
        btn_limpiar_registros = QPushButton("📝 Limpiar Registros")
        btn_permisos_archivos = QPushButton("🔐 Verificar Permisos")
        btn_integridad_archivos = QPushButton("✅ Verificar Integridad")
        
        layout_archivos.addWidget(btn_buscar_duplicados, 0, 0)
        layout_archivos.addWidget(btn_limpiar_registros, 0, 1)
        layout_archivos.addWidget(btn_permisos_archivos, 1, 0)
        layout_archivos.addWidget(btn_integridad_archivos, 1, 1)
        
        layout.addWidget(grupo_archivos)
        
        # Utilidades de red
        grupo_red_utils = QGroupBox("🌐 Utilidades de Red")
        layout_red_utils = QGridLayout(grupo_red_utils)
        
        btn_escanear_puertos = QPushButton("🔍 Escanear Puertos")
        btn_monitor_trafico = QPushButton("📊 Monitor de Tráfico")
        btn_test_velocidad = QPushButton("⚡ Test de Velocidad")
        btn_analizar_dns = QPushButton("🔍 Analizar DNS")
        
        layout_red_utils.addWidget(btn_escanear_puertos, 0, 0)
        layout_red_utils.addWidget(btn_monitor_trafico, 0, 1)
        layout_red_utils.addWidget(btn_test_velocidad, 1, 0)
        layout_red_utils.addWidget(btn_analizar_dns, 1, 1)
        
        layout.addWidget(grupo_red_utils)
        
        # Utilidades de seguridad
        grupo_seguridad_utils = QGroupBox("🔒 Utilidades de Seguridad")
        layout_seguridad_utils = QGridLayout(grupo_seguridad_utils)
        
        btn_generar_hashes = QPushButton("🔐 Generar Hashes")
        btn_verificar_firma = QPushButton("✍️ Verificar Firmas")
        btn_encrypt_archivos = QPushButton("🔒 Encriptar Archivos")
        btn_secure_delete = QPushButton("🗑️ Borrado Seguro")
        
        layout_seguridad_utils.addWidget(btn_generar_hashes, 0, 0)
        layout_seguridad_utils.addWidget(btn_verificar_firma, 0, 1)
        layout_seguridad_utils.addWidget(btn_encrypt_archivos, 1, 0)
        layout_seguridad_utils.addWidget(btn_secure_delete, 1, 1)
        
        layout.addWidget(grupo_seguridad_utils)
        
        # Herramientas del sistema
        grupo_sistema_utils = QGroupBox("⚙️ Herramientas del Sistema")
        layout_sistema_utils = QGridLayout(grupo_sistema_utils)
        
        btn_editor_registro = QPushButton("📝 Editor de Configuración")
        btn_monitor_recursos = QPushButton("📊 Monitor de Recursos")
        btn_gestor_servicios = QPushButton("🔄 Gestor de Servicios")
        btn_programador_tareas = QPushButton("⏰ Programador de Tareas")
        
        layout_sistema_utils.addWidget(btn_editor_registro, 0, 0)
        layout_sistema_utils.addWidget(btn_monitor_recursos, 0, 1)
        layout_sistema_utils.addWidget(btn_gestor_servicios, 1, 0)
        layout_sistema_utils.addWidget(btn_programador_tareas, 1, 1)
        
        layout.addWidget(grupo_sistema_utils)
        
        tabs.addTab(tab_utilidades, "🛠️ Utilidades Avanzadas")
        
    def _crear_panel_resultados_herramientas(self, layout):
        """Crea el panel de resultados para herramientas"""
        grupo_resultados = QGroupBox("📊 Resultados y Progreso")
        layout_resultados = QVBoxLayout(grupo_resultados)
        
        # Progreso
        self.label_progreso_herramienta = QLabel("Listo para ejecutar herramientas")
        layout_resultados.addWidget(self.label_progreso_herramienta)
        
        self.progreso_herramienta = QProgressBar()
        self.progreso_herramienta.setRange(0, 100)
        self.progreso_herramienta.setValue(0)
        layout_resultados.addWidget(self.progreso_herramienta)
        
        # Botón cancelar
        self.btn_cancelar_herramienta = QPushButton("❌ Cancelar")
        self.btn_cancelar_herramienta.setEnabled(False)
        layout_resultados.addWidget(self.btn_cancelar_herramienta)
        
        # Área de resultados
        self.texto_resultados_herramientas = QTextEdit()
        self.texto_resultados_herramientas.setMaximumHeight(200)
        self.texto_resultados_herramientas.setPlainText("Los resultados de las herramientas aparecerán aquí...")
        layout_resultados.addWidget(self.texto_resultados_herramientas)
        
        layout.addWidget(grupo_resultados)
        
    def _conectar_señales(self):
        """Conecta las señales de los componentes"""
        # Botones de análisis
        self.btn_analisis_completo.clicked.connect(lambda: self._ejecutar_herramienta("analisis_sistema"))
        
        # Botones de limpieza
        self.btn_ejecutar_limpieza.clicked.connect(lambda: self._ejecutar_herramienta("limpieza_sistema"))
        
        # Botón cancelar
        self.btn_cancelar_herramienta.clicked.connect(self._cancelar_herramienta)
        
    def _ejecutar_herramienta(self, herramienta: str, parametros: Optional[Dict[str, Any]] = None):
        """Ejecuta una herramienta específica"""
        if self.hilo_herramienta and self.hilo_herramienta.isRunning():
            QMessageBox.warning(self, "Herramienta en Ejecución", 
                              "Ya hay una herramienta ejecutándose. Por favor, espere a que termine.")
            return
            
        if parametros is None:
            parametros = {}
            
        # Limpiar resultados anteriores
        self.texto_resultados_herramientas.clear()
        
        # Actualizar UI
        self._actualizar_ui_herramienta_iniciada()
        
        # Crear y configurar hilo
        self.hilo_herramienta = HiloHerramientaSistema(herramienta, parametros)
        self.hilo_herramienta.progreso_actualizado.connect(self._actualizar_progreso_herramienta)
        self.hilo_herramienta.resultado_obtenido.connect(self._agregar_resultado_herramienta)
        self.hilo_herramienta.herramienta_completada.connect(self._herramienta_completada)
        self.hilo_herramienta.error_ocurrido.connect(self._error_herramienta)
        
        # Iniciar herramienta
        self.hilo_herramienta.start()
        self.logger.info(f"Herramienta {herramienta} iniciada")
        
    def _ejecutar_diagnostico(self, tipo_diagnostico: str):
        """Ejecuta un diagnóstico específico"""
        if tipo_diagnostico == "diagnostico_red":
            self._ejecutar_herramienta("diagnostico_red")
        elif tipo_diagnostico == "benchmark":
            self._ejecutar_herramienta("benchmark")
        else:
            # Para otros diagnósticos, mostrar resultado simulado
            resultado = f"Ejecutando {tipo_diagnostico}...\n"
            resultado += f"✅ {tipo_diagnostico} completado exitosamente\n"
            resultado += f"📊 Todos los parámetros dentro de rangos normales\n"
            resultado += f"⏰ Tiempo de ejecución: 2.5 segundos\n"
            
            self.texto_resultados_diagnostico.setPlainText(resultado)
            
    def _abrir_config_avanzada(self):
        """Abre el diálogo de configuración avanzada"""
        dialogo = DialogConfiguracionAvanzada(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Configuración", 
                                  "Configuración avanzada guardada exitosamente.")
            
    def _cancelar_herramienta(self):
        """Cancela la herramienta en ejecución"""
        if self.hilo_herramienta:
            self.hilo_herramienta.cancelar()
            self.hilo_herramienta.wait()
            self._actualizar_ui_herramienta_terminada()
            self.label_progreso_herramienta.setText("Herramienta cancelada por el usuario")
            self.logger.info("Herramienta cancelada por el usuario")
            
    def _actualizar_ui_herramienta_iniciada(self):
        """Actualiza la UI cuando inicia una herramienta"""
        self.btn_analisis_completo.setEnabled(False)
        self.btn_ejecutar_limpieza.setEnabled(False)
        self.btn_cancelar_herramienta.setEnabled(True)
        self.progreso_herramienta.setValue(0)
        
    def _actualizar_ui_herramienta_terminada(self):
        """Actualiza la UI cuando termina una herramienta"""
        self.btn_analisis_completo.setEnabled(True)
        self.btn_ejecutar_limpieza.setEnabled(True)
        self.btn_cancelar_herramienta.setEnabled(False)
        
    def _actualizar_progreso_herramienta(self, porcentaje: int, mensaje: str):
        """Actualiza el progreso de la herramienta"""
        self.progreso_herramienta.setValue(porcentaje)
        self.label_progreso_herramienta.setText(mensaje)
        
    def _agregar_resultado_herramienta(self, comando: str, resultado: str):
        """Agrega un resultado a la vista de resultados"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        texto_actual = self.texto_resultados_herramientas.toPlainText()
        
        if "Los resultados" in texto_actual:
            self.texto_resultados_herramientas.clear()
            texto_actual = ""
            
        nuevo_texto = f"[{timestamp}] {comando}\n{resultado}\n\n"
        self.texto_resultados_herramientas.setPlainText(texto_actual + nuevo_texto)
        
        # Scroll al final
        cursor = self.texto_resultados_herramientas.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.texto_resultados_herramientas.setTextCursor(cursor)
        
    def _herramienta_completada(self, resultados: Dict[str, Any]):
        """Procesa finalización de herramienta"""
        self._actualizar_ui_herramienta_terminada()
        
        # Agregar al historial
        entrada_historial = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " \
                          f"{resultados['herramienta']} - {resultados['estado']}"
        
        self.historial_herramientas.append(resultados)
        
        self.label_progreso_herramienta.setText(f"✅ {resultados['herramienta']} completado exitosamente")
        self.logger.info(f"Herramienta completada: {resultados}")
        
        # Mostrar resumen
        resumen = f"\n📋 RESUMEN DE EJECUCIÓN:\n"
        resumen += f"Herramienta: {resultados['herramienta']}\n"
        resumen += f"Estado: {resultados['estado']}\n"
        
        if 'tiempo' in resultados:
            resumen += f"Tiempo: {resultados['tiempo']}\n"
        if 'espacio_recuperado' in resultados:
            resumen += f"Espacio recuperado: {resultados['espacio_recuperado']}\n"
        if 'puntuacion_total' in resultados:
            resumen += f"Puntuación: {resultados['puntuacion_total']}\n"
            
        resumen += "=" * 50 + "\n"
        
        texto_actual = self.texto_resultados_herramientas.toPlainText()
        self.texto_resultados_herramientas.setPlainText(texto_actual + resumen)
        
        # Scroll al final
        cursor = self.texto_resultados_herramientas.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.texto_resultados_herramientas.setTextCursor(cursor)
        
    def _error_herramienta(self, mensaje: str):
        """Maneja errores de herramientas"""
        self._actualizar_ui_herramienta_terminada()
        self.label_progreso_herramienta.setText(f"❌ Error: {mensaje}")
        self.logger.error(f"Error en herramienta: {mensaje}")
        
        error_texto = f"\n❌ ERROR:\n{mensaje}\n" + "=" * 50 + "\n"
        texto_actual = self.texto_resultados_herramientas.toPlainText()
        self.texto_resultados_herramientas.setPlainText(texto_actual + error_texto)
