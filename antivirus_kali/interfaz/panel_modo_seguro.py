"""
Panel visual de Ares Aegis para activar/desactivar el modo pentesting seguro y ver auditoría.
Estilo minimalista japonés, limpio y diferente.
"""


from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QApplication
from PySide6.QtCore import Qt, QThread, Signal, QObject



class PanelModoSeguro(QWidget):
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
                self.log.emit("Iniciando acción de modo seguro...", "info")
                result = self.fn(*self.args, **self.kwargs)
                self.result.emit(result)
            except Exception as e:
                self.error.emit(e)
            finally:
                self.finished.emit()

    def __init__(self, controlador, panel_consola=None):
        super().__init__()
        self.controlador = controlador
        self.panel_consola = panel_consola
        self.setWindowTitle("Ares Aegis - Modo Seguro y Auditoría de Seguridad")
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
        self.label_info = QLabel(
            "Ares Aegis: Este panel permite activar protecciones rápidas para pentesting seguro:\n"
            "- Activar Modo Seguro: Habilita el firewall y bloquea conexiones no autorizadas.\n"
            "- Desactivar Modo Seguro: Desactiva el firewall temporalmente.\n"
            "- Auditar Configuración: Revisa configuraciones críticas como SSH.\n"
            "Recomendado: Mantén el modo seguro activado durante auditorías o pruebas.")
        self.label_info.setStyleSheet("font-size: 16px; font-weight: 800; color: #2563eb; margin-bottom: 8px; letter-spacing:0.5px;")
        self.label_info.setAccessibleName("Título modo seguro")
        self.boton_activar = QPushButton("Activar Modo Seguro (Firewall ON)")
        self.boton_activar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #3c8dbc; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_activar.setObjectName("exportar")
        self.boton_activar.setToolTip("Activar modo seguro (firewall ON).")
        self.boton_activar.clicked.connect(self.activar_threaded)
        self.boton_desactivar = QPushButton("Desactivar Modo Seguro (Firewall OFF)")
        self.boton_desactivar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #e67e22; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_desactivar.setObjectName("exportar")
        self.boton_desactivar.setToolTip("Desactivar modo seguro (firewall OFF).")
        self.boton_desactivar.clicked.connect(self.desactivar_threaded)
        self.boton_auditar = QPushButton("Auditar Configuración Crítica")
        self.boton_auditar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #6A8D73; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_auditar.setObjectName("exportar")
        self.boton_auditar.setToolTip("Auditar configuración crítica.")
        self.boton_auditar.clicked.connect(self.auditar_threaded)
        layout.addWidget(self.label_info)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.resultados)
        layout.addWidget(self.boton_activar)
        layout.addWidget(self.boton_desactivar)
        layout.addWidget(self.boton_auditar)
        # Detectar modo limitado
        import os
        self.modo_limitado = os.environ.get('ARES_AEGIS_LIMITADO') == '1'
        if self.modo_limitado:
            for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
                btn.setEnabled(False)
            self.advertencia_label.setText("⚠️ Modo limitado: Ejecuta como root para activar el modo seguro y auditar la configuración.")
        self.setLayout(layout)

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

    def activar_threaded(self):
        self.run_in_thread(self._activar, self._on_activar)

    def _activar(self):
        QApplication.processEvents()
        advertencia = self.controlador.activar_modo_seguro()
        return advertencia

    def _on_activar(self, advertencia):
        self.resultados.clear()
        if advertencia:
            self.resultados.addItem(f"🔴 {advertencia}")
            self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
            self.advertencia_label.setText(advertencia)
        else:
            self.resultados.addItem("🟢 Modo seguro activado: Firewall habilitado y conexiones salientes bloqueadas.")
            self.advertencia_label.setText("")
        for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
            btn.setEnabled(True)
        self.log("Modo seguro activado", "info")

    def desactivar_threaded(self):
        self.run_in_thread(self._desactivar, self._on_desactivar)

    def _desactivar(self):
        QApplication.processEvents()
        advertencia = self.controlador.desactivar_modo_seguro()
        return advertencia

    def _on_desactivar(self, advertencia):
        self.resultados.clear()
        if advertencia:
            self.resultados.addItem(f"🔴 {advertencia}")
            self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
            self.advertencia_label.setText(advertencia)
        else:
            self.resultados.addItem("🟡 Modo seguro desactivado: Firewall deshabilitado.")
            self.advertencia_label.setText("")
        for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
            btn.setEnabled(True)
        self.log("Modo seguro desactivado", "info")

    def auditar_threaded(self):
        self.run_in_thread(self._auditar, self._on_auditar)

    def _auditar(self):
        QApplication.processEvents()
        resultado, advertencia = self.controlador.auditar_configuracion()
        return (resultado, advertencia)

    def _on_auditar(self, result):
        resultado, advertencia = result
        self.resultados.clear()
        self.resultados.addItem(f"🔎 {resultado}")
        if advertencia:
            self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
            self.advertencia_label.setText(advertencia)
        else:
            self.advertencia_label.setText("")
        for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
            btn.setEnabled(True)
        self.log("Auditoría de configuración crítica completada", "info")

    def activar(self):
        from PySide6.QtWidgets import QApplication
        self.resultados.clear()
        self.advertencia_label.setText("")
        for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
            btn.setEnabled(False)
        try:
            self.resultados.addItem("⏳ Activando modo seguro... Por favor, espera.")
            QApplication.processEvents()
            advertencia = self.controlador.activar_modo_seguro()
            self.resultados.clear()
            if advertencia:
                self.resultados.addItem(f"🔴 {advertencia}")
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
                self.advertencia_label.setText(advertencia)
            else:
                self.resultados.addItem("🟢 Modo seguro activado: Firewall habilitado y conexiones salientes bloqueadas.")
                self.advertencia_label.setText("")
        finally:
            for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
                btn.setEnabled(True)

    def desactivar(self):
        from PySide6.QtWidgets import QApplication
        self.resultados.clear()
        self.advertencia_label.setText("")
        for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
            btn.setEnabled(False)
        try:
            self.resultados.addItem("⏳ Desactivando modo seguro... Por favor, espera.")
            QApplication.processEvents()
            advertencia = self.controlador.desactivar_modo_seguro()
            self.resultados.clear()
            if advertencia:
                self.resultados.addItem(f"🔴 {advertencia}")
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
                self.advertencia_label.setText(advertencia)
            else:
                self.resultados.addItem("🟡 Modo seguro desactivado: Firewall deshabilitado.")
                self.advertencia_label.setText("")
        finally:
            for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
                btn.setEnabled(True)

    def auditar(self):
        from PySide6.QtWidgets import QApplication
        self.resultados.clear()
        self.advertencia_label.setText("")
        for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
            btn.setEnabled(False)
        try:
            self.resultados.addItem("⏳ Auditando configuración... Por favor, espera.")
            QApplication.processEvents()
            resultado, advertencia = self.controlador.auditar_configuracion()
            self.resultados.clear()
        finally:
            for btn in [self.boton_activar, self.boton_desactivar, self.boton_auditar]:
                btn.setEnabled(True)
        self.resultados.addItem(f"🔎 {resultado}")
        if advertencia:
            self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
            self.advertencia_label.setText(advertencia)
        else:
            self.advertencia_label.setText("")
