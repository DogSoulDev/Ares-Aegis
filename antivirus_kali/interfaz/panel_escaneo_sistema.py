"""
Panel visual de Ares Aegis para el escaneo del sistema operativo, carpetas y programas instalados.
Estilo minimalista japonés, limpio y diferente.
Incluye docstrings y comentarios para máxima claridad y mantenibilidad.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QApplication
from PySide6.QtCore import Qt, QThread, Signal, QObject


class PanelEscaneoSistema(QWidget):
    def __init__(self, controlador, panel_consola=None):
        """
        Inicializa el panel de escaneo avanzado del sistema.
        controlador: instancia de ControladorEscaneoSistema
        """
        super().__init__()
        self.controlador = controlador
        self.panel_consola = panel_consola  # Permite inyectar el panel de consola para logs globales
        self.setWindowTitle("Ares Aegis - Escaneo Avanzado del Sistema (Principal)")
        self.setStyleSheet('''
            QWidget { background: #fff; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #23272f; border-radius: 12px; }
            QLabel { font-size: 15px; }
            QListWidget { background: #f7f8fa; color: #23272f; font-size: 15px; border-radius: 8px; padding: 8px; border: 1px solid #e0e0e0; selection-background-color: #e3f2fd; selection-color: #23272f; }
            QListWidget::item { padding: 10px 12px; border-radius: 7px; margin-bottom: 2px; }
            QListWidget::item:selected { background: #c3e6ff; color: #23272f; font-weight: 700; border-left: 5px solid #2563eb; }
            QListWidget::item:hover { background: #e0e7ef; }
            QPushButton { background: #e0e7ef; color: #23272f; border-radius: 8px; font-size: 15px; padding: 7px 18px; font-weight: 600; border: 1px solid #cfd8dc; }
            QPushButton:hover { background: #dbeafe; color: #1e293b; }
            QPushButton:focus { outline: 2px solid #2563eb; }
            QPushButton#exportar { background: #3c8dbc; color: #fff; border-radius: 8px; font-size: 15px; padding: 7px 18px; font-weight: 600; border: 1px solid #2563eb; }
            QPushButton#exportar:hover { background: #2563eb; color: #fff; }
            QProgressBar { border-radius: 8px; background: #e0e7ef; height: 18px; font-size: 14px; color: #23272f; }
            QProgressBar::chunk { background: #2563eb; border-radius: 8px; }
        ''')
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QProgressBar
        from antivirus_kali.interfaz.style import BUTTON_STYLE, EXPORT_BUTTON_STYLE
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: 600; font-size: 14px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.advertencia_label.setWordWrap(True)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { border-radius: 8px; background: #e0e7ef; height: 18px; font-size: 14px; color: #23272f; } QProgressBar::chunk { background: #2563eb; border-radius: 8px; }")
        self.resultados = QListWidget()
        self.resultados.setStyleSheet("background: #f7f8fa; color: #23272f; font-size: 15px; border-radius: 8px; padding: 8px; border: 1px solid #e0e0e0;")
        # Título principal
        titulo = QLabel("🛡️ Ares Aegis: Escaneo avanzado del sistema operativo y programas instalados.")
        titulo.setStyleSheet("font-size: 20px; font-weight: 800; color: #2563eb; margin-bottom: 8px; letter-spacing:0.5px;")
        titulo.setAccessibleName("Título escaneo sistema")
        layout.addWidget(titulo, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.advertencia_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.resultados)
        # Botones de exportación discretos y centrados con iconos
        from PySide6.QtGui import QIcon
        export_layout = QHBoxLayout()
        export_layout.setSpacing(12)
        export_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.boton_exportar_pdf = QPushButton(QIcon.fromTheme("application-pdf"), "Exportar PDF")
        self.boton_exportar_pdf.setStyleSheet(EXPORT_BUTTON_STYLE + "QPushButton { min-width: 120px; font-size: 14px; padding: 8px 0; }")
        self.boton_exportar_pdf.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.boton_exportar_pdf.clicked.connect(self.exportar_informe_threaded)
        self.boton_exportar_pdf.setObjectName("exportar")
        self.boton_exportar_pdf.setToolTip("Exportar resultados como PDF.")
        self.boton_exportar_md = QPushButton(QIcon.fromTheme("text-markdown"), "Exportar MD")
        self.boton_exportar_md.setStyleSheet(EXPORT_BUTTON_STYLE + "QPushButton { min-width: 120px; font-size: 14px; padding: 8px 0; }")
        self.boton_exportar_md.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.boton_exportar_md.clicked.connect(self.exportar_informe_markdown_threaded)
        self.boton_exportar_md.setObjectName("exportar")
        self.boton_exportar_md.setToolTip("Exportar resultados como Markdown.")
        self.boton_exportar_txt = QPushButton(QIcon.fromTheme("text-plain"), "Exportar TXT")
        self.boton_exportar_txt.setStyleSheet(EXPORT_BUTTON_STYLE + "QPushButton { min-width: 120px; font-size: 14px; padding: 8px 0; }")
        self.boton_exportar_txt.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.boton_exportar_txt.clicked.connect(self.exportar_informe_txt_threaded)
        self.boton_exportar_txt.setObjectName("exportar")
        self.boton_exportar_txt.setToolTip("Exportar resultados como TXT.")
        export_layout.addWidget(self.boton_exportar_pdf)
        export_layout.addWidget(self.boton_exportar_md)
        export_layout.addWidget(self.boton_exportar_txt)
        layout.addLayout(export_layout)
        # Controles de análisis: Pausa y Cancelar
        self.controles_layout = QHBoxLayout()
        self.boton_pausar = QPushButton("Pausar")
        self.boton_pausar.setStyleSheet("background: #e0e7ef; color: #23272f; border-radius: 8px; font-size: 14px; padding: 6px 18px; margin: 8px 0;")
        self.boton_pausar.clicked.connect(self.pausar_analisis)
        self.boton_pausar.setToolTip("Pausar el análisis en curso.")
        self.boton_reanudar = QPushButton("Reanudar")
        self.boton_reanudar.setStyleSheet("background: #e0e7ef; color: #23272f; border-radius: 8px; font-size: 14px; padding: 6px 18px; margin: 8px 0;")
        self.boton_reanudar.clicked.connect(self.reanudar_analisis)
        self.boton_reanudar.setToolTip("Reanudar el análisis pausado.")
        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_cancelar.setStyleSheet("background: #e57373; color: #fff; border-radius: 8px; font-size: 14px; padding: 6px 18px; margin: 8px 0;")
        self.boton_cancelar.clicked.connect(self.cancelar_analisis)
        self.boton_cancelar.setToolTip("Cancelar el análisis actual.")
        self.controles_layout.addWidget(self.boton_pausar)
        self.controles_layout.addWidget(self.boton_reanudar)
        self.controles_layout.addWidget(self.boton_cancelar)
        layout.addLayout(self.controles_layout)
        self.boton_reanudar.setEnabled(False)
        self.boton_cancelar.setEnabled(True)
        self._analisis_pausado = False
        self._analisis_cancelado = False
        # Añadir atributos requeridos por el test
        self._analisis_actual = 0
        self._analisis_total = 1
        # Detectar modo limitado
        import os
        self.modo_limitado = os.environ.get('ARES_AEGIS_LIMITADO') == '1'
        if self.modo_limitado:
            self.advertencia_label.setText("⚠️ Modo limitado: Ejecuta como root para análisis completos y acceso a todas las funciones.")
        self.setLayout(layout)
        self.base_hashes = {"/bin/ls": "HASH_DE_REFERENCIA"}
        self.ultimo_resumen = None
        # Lanzar análisis esencial automáticamente al abrir el panel
        QTimer = __import__('PySide6.QtCore', fromlist=['QTimer']).QTimer
        QTimer.singleShot(500, self.analisis_esencial_automatico)

    def analisis_esencial_automatico(self):
        """
        Ejecuta automáticamente los análisis esenciales y muestra el progreso y resultados.
        """
        self.resultados.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.advertencia_label.setText("Analizando el sistema... Por favor, espera.")
        self._analisis_etapas = [
            ("Rootkits", self.controlador.escanear_rootkits),
            ("Procesos", self.controlador.escanear_procesos),
            ("Puertos", self.controlador.escanear_puertos),
            ("Servicios", self.controlador.escanear_servicios),
            ("Integridad", lambda: self.controlador.escanear_integridad(self.base_hashes)),
            ("Programas", self.controlador.obtener_programas),
        ]
        self._analisis_resultados = {}
        self._analisis_actual = 0
        self._analisis_pausado = False
        self._analisis_cancelado = False
        self._analisis_total = len(self._analisis_etapas)
        self._analisis_siguiente_etapa()

    def _analisis_siguiente_etapa(self):
        if self._analisis_cancelado:
            self.progress_bar.setVisible(False)
            self.advertencia_label.setText("Análisis cancelado por el usuario.")
            if self.panel_consola:
                self.panel_consola.log("Análisis cancelado por el usuario.", "warning")
            self.boton_pausar.setEnabled(False)
            self.boton_reanudar.setEnabled(False)
            self.boton_cancelar.setEnabled(False)
            return
        if self._analisis_pausado:
            self.advertencia_label.setText("Análisis en pausa. Pulsa 'Reanudar' para continuar.")
            self.boton_reanudar.setEnabled(True)
            self.boton_pausar.setEnabled(False)
            return
        self.boton_reanudar.setEnabled(False)
        self.boton_pausar.setEnabled(True)
        if self._analisis_actual >= self._analisis_total:
            self.progress_bar.setValue(100)
            self.progress_bar.setVisible(False)
            self.advertencia_label.setText("")
            self.ultimo_resumen = self._analisis_resultados.copy()
            # Guardar en historial
            try:
                import datetime
                from antivirus_kali.interfaz.panel_historial import guardar_historial
                entrada = {
                    'fecha': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'resumen': self.ultimo_resumen
                }
                guardar_historial(entrada)
            except Exception as e:
                if self.panel_consola:
                    self.panel_consola.log(f"No se pudo guardar el análisis en el historial: {e}", "warning")
            self.resultados.clear()
            # Mostrar resumen ejecutivo visual
            from antivirus_kali.utils.resumen import ICONS
            resumen = self.ultimo_resumen
            total_alertas = 0
            if resumen:
                self.resultados.addItem(f"{ICONS['star']}  RESUMEN EJECUTIVO DEL SISTEMA  {ICONS['star']}")
                if 'rootkits' in resumen:
                    n = len(resumen['rootkits']) if resumen['rootkits'] else 0
                    icon = ICONS['fail'] if n else ICONS['ok']
                    self.resultados.addItem(f"{icon} Rootkits detectados: {n}")
                    total_alertas += n
                if 'procesos' in resumen:
                    n = len(resumen['procesos']) if resumen['procesos'] else 0
                    icon = ICONS['fail'] if n else ICONS['ok']
                    self.resultados.addItem(f"{icon} Procesos sospechosos: {n}")
                    total_alertas += n
                if 'puertos' in resumen:
                    n = len(resumen['puertos']) if resumen['puertos'] else 0
                    icon = ICONS['warn'] if n else ICONS['ok']
                    self.resultados.addItem(f"{icon} Puertos abiertos: {n}")
                if 'servicios' in resumen:
                    n = len(resumen['servicios']) if resumen['servicios'] else 0
                    icon = ICONS['info']
                    self.resultados.addItem(f"{icon} Servicios activos: {n}")
                if 'integridad' in resumen:
                    n = len([v for v in resumen['integridad'].values() if v != 'Íntegro']) if resumen['integridad'] else 0
                    icon = ICONS['fail'] if n else ICONS['ok']
                    self.resultados.addItem(f"{icon} Binarios alterados: {n}")
                    total_alertas += n
                if 'programas' in resumen:
                    n = len(resumen['programas']) if resumen['programas'] else 0
                    icon = ICONS['info']
                    self.resultados.addItem(f"{icon} Programas instalados: {n}")
                self.resultados.addItem("")
                if total_alertas == 0:
                    self.resultados.addItem(f"{ICONS['ok']}  El sistema no presenta amenazas críticas.")
                else:
                    self.resultados.addItem(f"{ICONS['danger']}  ¡Atención! Se detectaron {total_alertas} amenazas o alteraciones.")
                self.resultados.addItem("")
                # Botón para ver detalles y recomendaciones
                from PySide6.QtWidgets import QPushButton, QListWidgetItem
                btn_detalles = QPushButton("Ver detalles y recomendaciones")
                btn_detalles.setStyleSheet("background: #e0e7ef; color: #23272f; border-radius: 8px; font-size: 14px; padding: 6px 18px; margin: 8px 0;")
                btn_detalles.clicked.connect(self.mostrar_detalles_analisis)
                item = QListWidgetItem()
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                self.resultados.addItem(item)
                self.resultados.setItemWidget(item, btn_detalles)
            else:
                self.resultados.addItem("No se pudo generar el resumen ejecutivo.")
            if self.panel_consola:
                self.panel_consola.log("Análisis esencial completado", "info")
            self.boton_pausar.setEnabled(False)
            self.boton_reanudar.setEnabled(False)
            self.boton_cancelar.setEnabled(False)
            return
    def pausar_analisis(self):
        self._analisis_pausado = True
        self.boton_pausar.setEnabled(False)
        self.boton_reanudar.setEnabled(True)
        self.advertencia_label.setText("Análisis en pausa. Pulsa 'Reanudar' para continuar.")
        if self.panel_consola:
            self.panel_consola.log("Análisis pausado por el usuario.", "info")

    def reanudar_analisis(self):
        if self._analisis_pausado:
            self._analisis_pausado = False
            self.boton_pausar.setEnabled(True)
            self.boton_reanudar.setEnabled(False)
            self.advertencia_label.setText("Reanudando análisis...")
            if self.panel_consola:
                self.panel_consola.log("Análisis reanudado.", "info")
            self._analisis_siguiente_etapa()

    def cancelar_analisis(self):
        self._analisis_cancelado = True
        self.boton_pausar.setEnabled(False)
        self.boton_reanudar.setEnabled(False)
        self.boton_cancelar.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.advertencia_label.setText("Análisis cancelado por el usuario.")
        if self.panel_consola:
            self.panel_consola.log("Análisis cancelado por el usuario.", "warning")

    def mostrar_detalles_analisis(self):
        """Muestra los detalles completos del análisis y recomendaciones."""
        self.resultados.clear()
        resumen = self.ultimo_resumen
        from antivirus_kali.utils.resumen import ICONS
        if not resumen:
            self.resultados.addItem("No hay detalles disponibles.")
            return
        self.resultados.addItem(f"{ICONS['star']}  DETALLES DEL ANÁLISIS  {ICONS['star']}")
        if 'rootkits' in resumen:
            self.resultados.addItem("\nRootkits:")
            for r in resumen['rootkits'] or []:
                self.resultados.addItem(f"  {ICONS['fail']} {r}")
            if not resumen['rootkits']:
                self.resultados.addItem(f"  {ICONS['ok']} Ningún rootkit detectado.")
        if 'procesos' in resumen:
            self.resultados.addItem("\nProcesos sospechosos:")
            for p in resumen['procesos'] or []:
                self.resultados.addItem(f"  {ICONS['fail']} {p}")
            if not resumen['procesos']:
                self.resultados.addItem(f"  {ICONS['ok']} Ningún proceso sospechoso.")
        if 'puertos' in resumen:
            self.resultados.addItem("\nPuertos abiertos:")
            for p in resumen['puertos'] or []:
                self.resultados.addItem(f"  {ICONS['warn']} {p}")
            if not resumen['puertos']:
                self.resultados.addItem(f"  {ICONS['ok']} Ningún puerto abierto relevante.")
        if 'servicios' in resumen:
            self.resultados.addItem("\nServicios activos:")
            for s in resumen['servicios'] or []:
                self.resultados.addItem(f"  {ICONS['info']} {s}")
            if not resumen['servicios']:
                self.resultados.addItem(f"  {ICONS['ok']} No hay servicios activos relevantes.")
        if 'integridad' in resumen:
            self.resultados.addItem("\nIntegridad de binarios:")
            for archivo, estado in (resumen['integridad'] or {}).items():
                icon = ICONS['ok'] if estado == 'Íntegro' else ICONS['fail']
                self.resultados.addItem(f"  {icon} {archivo}: {estado}")
            if not resumen['integridad']:
                self.resultados.addItem(f"  {ICONS['ok']} Todos los binarios críticos están íntegros.")
        if 'programas' in resumen:
            self.resultados.addItem("\nProgramas instalados:")
            for prog in (resumen['programas'] or [])[:20]:
                self.resultados.addItem(f"  {ICONS['info']} {prog}")
            if len(resumen['programas'] or []) > 20:
                self.resultados.addItem(f"  ...y {len(resumen['programas'])-20} más.")
        self.resultados.addItem("\nRecomendaciones:")
        self.resultados.addItem(f"  {ICONS['arrow']} Mantén tu sistema actualizado.")
        self.resultados.addItem(f"  {ICONS['arrow']} Investiga cualquier rootkit, proceso o binario sospechoso.")
        self.resultados.addItem(f"  {ICONS['arrow']} Revisa los puertos abiertos y servicios activos regularmente.")
        self.resultados.addItem(f"  {ICONS['arrow']} Si detectas alteraciones, reinstala desde fuentes oficiales.")
        nombre, funcion = self._analisis_etapas[self._analisis_actual]
        self.resultados.addItem(f"⏳ Analizando {nombre}...")
        if self.panel_consola:
            self.panel_consola.log(f"Iniciando análisis de {nombre}...", "info")
        QThread = __import__('PySide6.QtCore', fromlist=['QThread']).QThread
        class EtapaWorker(QObject):
            finished = Signal()
            result = Signal(object)
            error = Signal(Exception)
            def run(self):
                try:
                    resultado = funcion()
                    self.result.emit(resultado)
                except Exception as e:
                    self.error.emit(e)
                finally:
                    self.finished.emit()
        self._etapa_thread = QThread()
        self._etapa_worker = EtapaWorker()
        self._etapa_worker.moveToThread(self._etapa_thread)
        self._etapa_worker.result.connect(lambda r, n=nombre: self._analisis_etapa_completada(n, r))
        self._etapa_worker.error.connect(lambda e, n=nombre: self._analisis_etapa_error(n, e))
        self._etapa_thread.started.connect(self._etapa_worker.run)
        self._etapa_worker.finished.connect(self._etapa_thread.quit)
        self._etapa_worker.finished.connect(self._etapa_worker.deleteLater)
        self._etapa_thread.finished.connect(self._etapa_thread.deleteLater)
        self._etapa_thread.start()

    def _analisis_etapa_completada(self, nombre, resultado):
        self._analisis_resultados[nombre.lower()] = resultado
        self.resultados.addItem(f"✔️ {nombre} analizado.")
        if self.panel_consola:
            self.panel_consola.log(f"{nombre} analizado correctamente.", "info")
        self._analisis_actual += 1
        progreso = int((self._analisis_actual / self._analisis_total) * 100)
        self.progress_bar.setValue(progreso)
        self._analisis_siguiente_etapa()

    def _analisis_etapa_error(self, nombre, error):
        self.resultados.addItem(f"❌ Error al analizar {nombre}: {error}")
        if self.panel_consola:
            self.panel_consola.log(f"Error al analizar {nombre}: {error}", "error")
        self._analisis_actual += 1
        progreso = int((self._analisis_actual / self._analisis_total) * 100)
        self.progress_bar.setValue(progreso)
        self._analisis_siguiente_etapa()
    # --- THREADING Y LOGGING PROFESIONAL ---
    class Worker(QObject):
        finished = Signal()
        result = Signal(object)
        error = Signal(Exception)
        log = Signal(str, str)
        progress = Signal(int)
        def __init__(self, fn, *args, **kwargs):
            super().__init__()
            self.fn = fn
            self.args = args
            self.kwargs = kwargs
        def run(self):
            try:
                self.log.emit("Iniciando tarea...", "info")
                # Si la función acepta callback de progreso, pásalo
                if 'progress_callback' in self.fn.__code__.co_varnames:
                    result = self.fn(*self.args, progress_callback=self.progress.emit, **self.kwargs)
                else:
                    result = self.fn(*self.args, **self.kwargs)
                self.result.emit(result)
            except Exception as e:
                self.error.emit(e)
            finally:
                self.finished.emit()

    def log(self, mensaje, nivel="info"):
        if self.panel_consola:
            self.panel_consola.log(mensaje, nivel)

    def run_in_thread(self, fn, on_result, on_error=None, log_msg=None):
        thread = QThread()
        worker = self.Worker(fn)
        worker.moveToThread(thread)
        worker.result.connect(on_result)
        if on_error:
            worker.error.connect(on_error)
        worker.log.connect(self.log)
        worker.progress.connect(self.update_progress)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        thread.start()
        if log_msg:
            self.log(log_msg, "info")
        return thread

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value >= 100:
            self.progress_bar.setVisible(False)

    # --- FUNCIONES THREAD-SAFE Y LOGGING ---
    def exportar_informe_markdown_threaded(self):
        self.run_in_thread(self._exportar_informe_markdown, self._on_exportar_informe_markdown)
    def exportar_informe_txt_threaded(self):
        self.run_in_thread(self._exportar_informe_txt, self._on_exportar_informe_txt)
    def exportar_informe_threaded(self):
        self.run_in_thread(self._exportar_informe, self._on_exportar_informe)

    def _exportar_informe_markdown(self):
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        if not self.ultimo_resumen:
            self.mostrar_resumen()
        recomendaciones = [
            "Mantén tu sistema actualizado.",
            "Investiga cualquier rootkit o proceso sospechoso.",
            "Revisa los puertos abiertos y servicios activos regularmente."
        ]
        return self.controlador.exportar_informe_markdown(self.ultimo_resumen, recomendaciones=recomendaciones)

    def _exportar_informe_txt(self):
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        if not self.ultimo_resumen:
            self.mostrar_resumen()
        recomendaciones = [
            "Mantén tu sistema actualizado.",
            "Investiga cualquier rootkit o proceso sospechoso.",
            "Revisa los puertos abiertos y servicios activos regularmente."
        ]
        return self.controlador.exportar_informe_txt(self.ultimo_resumen, recomendaciones=recomendaciones)

    def _exportar_informe(self):
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        if not self.ultimo_resumen:
            self.mostrar_resumen()
        import getpass
        usuario = getpass.getuser()
        return self.controlador.exportar_informe(self.ultimo_resumen, usuario=usuario)
    def analizar_rootkits_threaded(self):
        self.run_in_thread(self.analizar_rootkits, self._on_analizar_rootkits)
    def analizar_procesos_threaded(self):
        self.run_in_thread(self.analizar_procesos, self._on_analizar_procesos)
    def analizar_puertos_threaded(self):
        self.run_in_thread(self.analizar_puertos, self._on_analizar_puertos)
    def analizar_servicios_threaded(self):
        self.run_in_thread(self.analizar_servicios, self._on_analizar_servicios)
    def analizar_integridad_threaded(self):
        self.run_in_thread(self.analizar_integridad, self._on_analizar_integridad)
    def listar_programas_threaded(self):
        self.run_in_thread(self.listar_programas, self._on_listar_programas)

    # --- CALLBACKS DE RESULTADO ---
    def _on_exportar_informe_markdown(self, result):
        self.resultados.addItem(f"Informe Markdown exportado a: {result}")
        self.log(f"Informe Markdown exportado a: {result}", "info")
    def _on_exportar_informe_txt(self, result):
        self.resultados.addItem(f"Informe TXT exportado a: {result}")
        self.log(f"Informe TXT exportado a: {result}", "info")
    def _on_exportar_informe(self, result):
        self.resultados.addItem(f"Informe PDF exportado a: {result}")
        self.log(f"Informe PDF exportado a: {result}", "info")
    def _on_analizar_rootkits(self, result):
        self.resultados.clear()
        self.resultados.addItem("Análisis de rootkits:")
        for r in result:
            self.resultados.addItem(r)
        self.progress_bar.setVisible(False)
        self.log("Análisis de rootkits completado", "info")
    def _on_analizar_procesos(self, result):
        self.resultados.clear()
        self.resultados.addItem("Procesos sospechosos:")
        for p in result:
            self.resultados.addItem(p)
        self.progress_bar.setVisible(False)
        self.log("Análisis de procesos completado", "info")
    def _on_analizar_puertos(self, result):
        self.resultados.clear()
        self.resultados.addItem("Puertos abiertos:")
        for p in result:
            self.resultados.addItem(p)
        self.progress_bar.setVisible(False)
        self.log("Análisis de puertos completado", "info")
    def _on_analizar_servicios(self, result):
        self.resultados.clear()
        self.resultados.addItem("Servicios activos:")
        for s in result:
            self.resultados.addItem(s)
        self.progress_bar.setVisible(False)
        self.log("Análisis de servicios completado", "info")
    def _on_analizar_integridad(self, result):
        self.resultados.clear()
        self.resultados.addItem("Verificación de integridad de binarios críticos:")
        if result:
            for archivo, estado in result.items():
                self.resultados.addItem(f"{archivo}: {estado}")
        else:
            self.resultados.addItem("Todos los binarios críticos están íntegros.")
        self.progress_bar.setVisible(False)
        self.log("Verificación de integridad completada", "info")
    def _on_listar_programas(self, result):
        self.resultados.clear()
        self.resultados.addItem("Programas instalados:")
        for prog in result[:100]:
            self.resultados.addItem(prog)
        if len(result) > 100:
            self.resultados.addItem(f"...y {len(result)-100} más.")
        self.progress_bar.setVisible(False)
        self.log("Listado de programas completado", "info")

    def exportar_informe_txt(self):
        """
        Exporta el informe en formato texto plano profesional.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Exportando informe TXT... Por favor, espera.")
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        try:
            if not self.ultimo_resumen:
                self.mostrar_resumen()
            recomendaciones = [
                "Mantén tu sistema actualizado.",
                "Investiga cualquier rootkit o proceso sospechoso.",
                "Revisa los puertos abiertos y servicios activos regularmente."
            ]
            ruta = self.controlador.exportar_informe_txt(self.ultimo_resumen, recomendaciones=recomendaciones)
            self.resultados.addItem(f"Informe TXT exportado a: {ruta}")
        except Exception as e:
            self.advertencia_label.setText(f"Error al exportar informe TXT: {e}")
            self.resultados.addItem("No se pudo exportar el informe TXT.")

    def mostrar_resumen(self):
        """
        Muestra un mensaje inicial y guarda el resumen general del sistema tras el análisis.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        try:
            self.ultimo_resumen = self.controlador.obtener_resumen(self.base_hashes)
            from antivirus_kali.utils.resumen import feedback_visual_terminal
            self.resultados.addItem(feedback_visual_terminal("Resumen general del sistema:", tipo="info"))
            for clave, valor in self.ultimo_resumen.items():
                if isinstance(valor, list):
                    self.resultados.addItem(feedback_visual_terminal(f"{clave.title()}: {len(valor)} elementos", tipo="ok" if not valor else "warn"))
                elif isinstance(valor, dict):
                    self.resultados.addItem(feedback_visual_terminal(f"{clave.title()}: {len(valor)} archivos verificados", tipo="info"))
                else:
                    self.resultados.addItem(feedback_visual_terminal(f"{clave.title()}: {valor}", tipo="info"))
        except Exception as e:
            from antivirus_kali.utils.resumen import feedback_visual_terminal
            self.advertencia_label.setText(feedback_visual_terminal(f"Error al obtener el resumen: {e}", tipo="fail"))
            self.resultados.addItem(feedback_visual_terminal("No se pudo obtener el resumen del sistema.", tipo="fail"))

    def analizar_rootkits(self):
        """
        Analiza rootkits y muestra resultados, guardando en el resumen.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Analizando rootkits... Por favor, espera.")
        QApplication.processEvents()
        try:
            rootkits = self.controlador.escanear_rootkits()
            self.resultados.clear()
            self.resultados.addItem("Análisis de rootkits:")
            for r in rootkits:
                self.resultados.addItem(r)
            if not self.ultimo_resumen:
                self.ultimo_resumen = {}
            self.ultimo_resumen['rootkits'] = rootkits
        except Exception as e:
            self.advertencia_label.setText(f"Error al analizar rootkits: {e}")
            self.resultados.addItem("No se pudo analizar rootkits.")

    def analizar_procesos(self):
        """
        Analiza procesos sospechosos y muestra resultados, guardando en el resumen.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Analizando procesos... Por favor, espera.")
        QApplication.processEvents()
        try:
            procesos = self.controlador.escanear_procesos()
            self.resultados.clear()
            self.resultados.addItem("Procesos sospechosos:")
            for p in procesos:
                self.resultados.addItem(p)
            if not self.ultimo_resumen:
                self.ultimo_resumen = {}
            self.ultimo_resumen['procesos'] = procesos
        except Exception as e:
            self.advertencia_label.setText(f"Error al analizar procesos: {e}")
            self.resultados.addItem("No se pudo analizar procesos.")

    def analizar_puertos(self):
        """
        Analiza puertos abiertos y muestra resultados, guardando en el resumen.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Analizando puertos abiertos... Por favor, espera.")
        QApplication.processEvents()
        try:
            puertos = self.controlador.escanear_puertos()
            self.resultados.clear()
            self.resultados.addItem("Puertos abiertos:")
            for p in puertos:
                self.resultados.addItem(p)
            if not self.ultimo_resumen:
                self.ultimo_resumen = {}
            self.ultimo_resumen['puertos'] = puertos
        except Exception as e:
            self.advertencia_label.setText(f"Error al analizar puertos: {e}")
            self.resultados.addItem("No se pudo analizar puertos.")

    def analizar_servicios(self):
        """
        Analiza servicios activos y muestra resultados, guardando en el resumen.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Analizando servicios activos... Por favor, espera.")
        QApplication.processEvents()
        try:
            servicios = self.controlador.escanear_servicios()
            self.resultados.clear()
            self.resultados.addItem("Servicios activos:")
            for s in servicios:
                self.resultados.addItem(s)
            if not self.ultimo_resumen:
                self.ultimo_resumen = {}
            self.ultimo_resumen['servicios'] = servicios
        except Exception as e:
            self.advertencia_label.setText(f"Error al analizar servicios: {e}")
            self.resultados.addItem("No se pudo analizar servicios.")

    def analizar_integridad(self):
        """
        Verifica la integridad de binarios y muestra resultados, guardando en el resumen.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Verificando integridad de binarios... Por favor, espera.")
        QApplication.processEvents()
        try:
            integridad = self.controlador.escanear_integridad(self.base_hashes)
            self.resultados.clear()
            self.resultados.addItem("Verificación de integridad de binarios críticos:")
            if integridad:
                for archivo, estado in integridad.items():
                    self.resultados.addItem(f"{archivo}: {estado}")
            else:
                self.resultados.addItem("Todos los binarios críticos están íntegros.")
            if not self.ultimo_resumen:
                self.ultimo_resumen = {}
            self.ultimo_resumen['integridad'] = integridad
        except Exception as e:
            self.advertencia_label.setText(f"Error al verificar integridad: {e}")
            self.resultados.addItem("No se pudo verificar la integridad.")

    def listar_programas(self):
        """
        Lista los programas instalados y muestra resultados, guardando en el resumen.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Listando programas instalados... Por favor, espera.")
        QApplication.processEvents()
        try:
            programas = self.controlador.obtener_programas()
            self.resultados.clear()
            self.resultados.addItem("Programas instalados:")
            for prog in programas[:100]:
                self.resultados.addItem(prog)
            if len(programas) > 100:
                self.resultados.addItem(f"...y {len(programas)-100} más.")
            if not self.ultimo_resumen:
                self.ultimo_resumen = {}
            self.ultimo_resumen['programas'] = programas
        except Exception as e:
            self.advertencia_label.setText(f"Error al listar programas: {e}")
            self.resultados.addItem("No se pudo listar los programas instalados.")

    def exportar_informe(self):
        """
        Exporta el informe PDF profesional con el último resumen disponible.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Exportando informe PDF profesional... Por favor, espera.")
        QApplication.processEvents()
        try:
            if not self.ultimo_resumen:
                self.mostrar_resumen()
            import getpass
            usuario = getpass.getuser()
            ruta = self.controlador.exportar_informe(self.ultimo_resumen, usuario=usuario)
            self.resultados.addItem(f"Informe PDF exportado a: {ruta}")
        except Exception as e:
            self.advertencia_label.setText(f"Error al exportar informe: {e}")
            self.resultados.addItem("No se pudo exportar el informe PDF.")
