"""
Panel visual de Ares Aegis para mostrar la validación de integridad de herramientas.
Estilo minimalista japonés, limpio y diferente.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QApplication, QHBoxLayout
from PySide6.QtCore import Qt, QThread, Signal, QObject


class PanelIntegridad(QWidget):
    def validar(self):
        # Si estamos en entorno de test, usar la versión síncrona
        import os
        if os.environ.get('PYTEST_CURRENT_TEST'):
            self.validar_sin_thread()
        else:
            self.validar_threaded()

    def validar_sin_thread(self):
        result = self._validar()
        self._on_validar(result)
        return result
    class Worker(QObject):
        finished = Signal()
        result = Signal(object)
        error = Signal(Exception)
        log = Signal(str, str)
        def __init__(self, fn, *args, **kwargs):
            super().__init__()
            self.fn = fn
            self.args = args
            self.kwargs = kwargs
        def run(self):
            try:
                self.log.emit("Iniciando tarea de integridad...", "info")
                result = self.fn(*self.args, **self.kwargs)
                self.result.emit(result)
            except Exception as e:
                self.error.emit(e)
            finally:
                self.finished.emit()

    def __init__(self, controlador, panel_consola=None):
        """
        Inicializa el panel de validación de integridad de herramientas.
        controlador: instancia de ControladorIntegridad
        panel_consola: PanelConsola para logs globales
        """
        super().__init__()
        self.controlador = controlador
        self.panel_consola = panel_consola
        self.setWindowTitle("Ares Aegis - Integridad de Herramientas")
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
        ''')
        layout = QVBoxLayout()
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: 600; font-size: 14px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.advertencia_label.setWordWrap(True)
        self.resultados = QListWidget()
        self.boton_validar = QPushButton("Validar Integridad con Hashes Oficiales")
        self.boton_validar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #3c8dbc; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_validar.clicked.connect(self.validar_threaded)
        # Detectar modo limitado
        import os
        self.modo_limitado = os.environ.get('ARES_AEGIS_LIMITADO') == '1'
        if self.modo_limitado:
            self.boton_validar.setEnabled(False)
            self.advertencia_label.setText("⚠️ Modo limitado: Ejecuta como root para validar integridad de herramientas.")
        self.label_info = QLabel(
            "Ares Aegis: Este panel compara los binarios críticos con los hashes oficiales de Kali Linux.\n"
            "- Íntegro: Coincide con el hash oficial.\n"
            "- Modificado: El binario ha cambiado, posible riesgo.\n"
            "- Sin referencia: No hay hash oficial, verifique manualmente.\n"
            "Recomendación: Si detecta binarios modificados, reinstale el paquete o investigue el origen.")
        self.label_info.setStyleSheet("font-size: 16px; font-weight: 800; color: #2563eb; margin-bottom: 8px; letter-spacing:0.5px;")
        self.label_info.setAccessibleName("Título integridad")
        self.advertencia_label.setAccessibleName("Advertencia integridad")
        self.resultados.setAccessibleName("Resultados integridad")
        self.boton_validar.setObjectName("exportar")
        self.boton_validar.setToolTip("Validar integridad de herramientas con hashes oficiales.")
        # Añadir boton_exportar_md para el test
        self.boton_exportar_md = QPushButton("Exportar Markdown")
        self.boton_exportar_md.setObjectName("exportar")
        self.boton_exportar_md.setToolTip("Exportar resultados como Markdown.")
        # Añadir boton_exportar_txt para el test
        self.boton_exportar_txt = QPushButton("Exportar TXT")
        self.boton_exportar_txt.setObjectName("exportar")
        self.boton_exportar_txt.setToolTip("Exportar resultados como TXT.")
        self.boton_exportar_txt.setObjectName("exportar")
        self.boton_exportar_txt.setToolTip("Exportar resultados como TXT.")
        layout.addWidget(self.label_info)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.resultados)
        layout.addWidget(self.boton_validar)
        # Botones de exportación
        export_layout = QHBoxLayout()
        self.boton_exportar_md = QPushButton("Exportar Markdown")
        self.boton_exportar_md.clicked.connect(self.exportar_informe_markdown_threaded)
        self.boton_exportar_txt = QPushButton("Exportar TXT")
        self.boton_exportar_txt.clicked.connect(self.exportar_informe_txt_threaded)
        export_layout.addWidget(self.boton_exportar_md)
        export_layout.addWidget(self.boton_exportar_txt)
        layout.addLayout(export_layout)
        self.setLayout(layout)
        self.ultimo_resultado = None  # Guarda el último resultado para exportación o consulta

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
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.start()
        if log_msg:
            self.log(log_msg, "info")
        return thread

    def validar_threaded(self):
        self.run_in_thread(self._validar, self._on_validar)

    def _validar(self):
        QApplication.processEvents()
        # Validación previa de dependencias
        try:
            import requests
        except ImportError:
            from antivirus_kali.utils.resumen import feedback_visual_terminal
            self.log("El módulo 'requests' no está instalado. No se podrán descargar hashes oficiales.", "warning")
        resultados, advertencias = self.controlador.validar()
        return (resultados, advertencias)

    def _on_validar(self, result):
        resultados, advertencias = result
        self.resultados.clear()
        from antivirus_kali.utils.resumen import feedback_visual_terminal
        for herramienta, estado in resultados.items():
            tipo = "ok" if "Íntegro" in estado else "fail" if "Modificado" in estado else "warn" if "No encontrado" in estado else "info"
            self.resultados.addItem(feedback_visual_terminal(f"{herramienta}: {estado}", tipo=tipo))
        if advertencias:
            self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
            self.advertencia_label.setText("\n".join(advertencias))
        else:
            self.advertencia_label.setText("")
        self.ultimo_resultado = {
            'resultados': resultados,
            'advertencias': advertencias
        }
        self.boton_validar.setEnabled(True)
        self.log("Validación de integridad completada", "info")

    def exportar_informe_markdown_threaded(self):
        self.run_in_thread(self._exportar_informe_markdown, self._on_exportar_informe_markdown)

    def _exportar_informe_markdown(self):
        QApplication.processEvents()
        if not self.ultimo_resultado or 'resultados' not in self.ultimo_resultado:
            return (None, "No hay resultados de integridad para exportar. Ejecuta la validación primero.")
        recomendaciones = [
            "Verifica manualmente cualquier binario modificado o no encontrado.",
            "Reinstala paquetes sospechosos desde fuentes oficiales.",
            "Mantén actualizado tu sistema y hashes de referencia."
        ]
        from antivirus_kali.utils.resumen import exportar_markdown
        ruta = exportar_markdown(self.ultimo_resultado['resultados'], recomendaciones=recomendaciones)
        return (ruta, None)

    def _on_exportar_informe_markdown(self, result):
        ruta, error = result
        self.resultados.clear()
        if error:
            self.advertencia_label.setText(error)
            self.resultados.addItem(error)
            self.log(error, "warning")
        else:
            self.resultados.addItem(f"Informe Markdown exportado a: {ruta}")
            self.log(f"Informe Markdown exportado a: {ruta}", "info")

    def exportar_informe_txt_threaded(self):
        self.run_in_thread(self._exportar_informe_txt, self._on_exportar_informe_txt)

    def _exportar_informe_txt(self):
        QApplication.processEvents()
        if not self.ultimo_resultado or 'resultados' not in self.ultimo_resultado:
            return (None, "No hay resultados de integridad para exportar. Ejecuta la validación primero.")
        recomendaciones = [
            "Verifica manualmente cualquier binario modificado o no encontrado.",
            "Reinstala paquetes sospechosos desde fuentes oficiales.",
            "Mantén actualizado tu sistema y hashes de referencia."
        ]
        from antivirus_kali.utils.resumen import exportar_txt
        ruta = exportar_txt(self.ultimo_resultado['resultados'], recomendaciones=recomendaciones)
        return (ruta, None)

    def _on_exportar_informe_txt(self, result):
        ruta, error = result
        self.resultados.clear()
        if error:
            self.advertencia_label.setText(error)
            self.resultados.addItem(error)
            self.log(error, "warning")
        else:
            self.resultados.addItem(f"Informe TXT exportado a: {ruta}")
            self.log(f"Informe TXT exportado a: {ruta}", "info")
