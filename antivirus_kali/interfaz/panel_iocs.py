"""
Panel visual de Ares Aegis para mostrar amenazas detectadas por IOCs y reputación de repositorios.
Estilo minimalista japonés, limpio y diferente.
"""


from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QListWidget, QApplication
from PySide6.QtCore import Qt, QThread, Signal, QObject



class PanelIOCs(QWidget):
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
                self.log.emit("Iniciando verificación/agregado de IOC...", "info")
                result = self.fn(*self.args, **self.kwargs)
                self.result.emit(result)
            except Exception as e:
                self.error.emit(e)
            finally:
                self.finished.emit()

    def __init__(self, controlador, panel_consola=None):
        """
        Inicializa el panel de gestión y verificación de IOCs.
        controlador: instancia de ControladorIOCs
        panel_consola: PanelConsola para logs globales
        """
        super().__init__()
        self.controlador = controlador
        self.panel_consola = panel_consola
        self.setWindowTitle("Ares Aegis - Detección de IOCs y Reputación")
        self.setStyleSheet('''
            QWidget { background: #fff; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #23272f; border-radius: 12px; }
            QLabel { font-size: 15px; }
            QListWidget { background: #f7f8fa; color: #23272f; font-size: 15px; border-radius: 8px; padding: 8px; border: 1px solid #e0e0e0; selection-background-color: #e3f2fd; selection-color: #23272f; }
            QListWidget::item { padding: 10px 12px; border-radius: 7px; margin-bottom: 2px; }
            QListWidget::item:selected { background: #c3e6ff; color: #23272f; font-weight: 700; border-left: 5px solid #2563eb; }
            QListWidget::item:hover { background: #e0e7ef; }
            QLineEdit { padding: 10px 14px; font-size: 15px; border-radius: 7px; border: 1.5px solid #e0e0e0; background: #f7f8fa; margin-bottom: 8px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; }
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
        self.entrada = QLineEdit()
        self.entrada.setPlaceholderText("Introduce hash, IP o URL para analizar...")
        self.entrada.setStyleSheet("padding: 10px 14px; font-size: 15px; border-radius: 7px; border: 1.5px solid #e0e0e0; background: #f7f8fa; margin-bottom: 8px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.resultados = QListWidget()
        self.boton_verificar = QPushButton("Verificar IOC/Reputación")
        self.boton_verificar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #3c8dbc; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_verificar.clicked.connect(self.verificar_threaded)
        self.boton_agregar = QPushButton("Agregar IOC manualmente")
        self.boton_agregar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #6A8D73; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_agregar.clicked.connect(self.agregar_ioc_threaded)
        self.label_info = QLabel("Ares Aegis: Este panel permite comprobar si un archivo, IP o dominio es malicioso según fuentes públicas.\nPuedes añadir IOCs manualmente para reforzar la protección.")
        self.label_info.setStyleSheet("font-size: 16px; font-weight: 800; color: #2563eb; margin-bottom: 8px; letter-spacing:0.5px;")
        self.label_info.setAccessibleName("Título IOCs")
        self.advertencia_label.setAccessibleName("Advertencia IOCs")
        self.resultados.setAccessibleName("Resultados IOCs")
        self.entrada.setAccessibleName("Entrada IOC")
        self.boton_verificar.setObjectName("exportar")
        self.boton_verificar.setToolTip("Verificar IOC o reputación.")
        self.boton_agregar.setObjectName("exportar")
        self.boton_agregar.setToolTip("Agregar IOC manualmente.")
        layout.addWidget(self.label_info)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.entrada)
        layout.addWidget(self.resultados)
        layout.addWidget(self.boton_verificar)
        layout.addWidget(self.boton_agregar)
        self.setLayout(layout)
        self.iocs_manuales = set()
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

    def verificar_threaded(self):
        self.run_in_thread(self._verificar, self._on_verificar)

    def _verificar(self):
        valor = self.entrada.text().strip()
        QApplication.processEvents()
        advertencias = []
        if not valor:
            return ("Introduce un valor para analizar.", [], None)
        if valor in self.iocs_manuales:
            advertencias.append("Este IOC fue marcado manualmente como malicioso. Confirma su procedencia.")
            return (f"manual-ioc: IOC manualmente marcado como malicioso.", advertencias, valor)
        try:
            import requests
        except ImportError:
            self.log("El módulo 'requests' no está instalado. El análisis puede ser incompleto.", "warning")
        resultado, advertencias_api = self.controlador.verificar_ioc(valor)
        advertencias.extend(advertencias_api)
        if "malicioso" in resultado:
            return (f"🔴 {resultado}", advertencias, valor)
        else:
            return (f"🟢 {resultado}", advertencias, valor)

    def _on_verificar(self, result):
        resultado, advertencias, valor = result
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem(resultado)
        if advertencias:
            self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
            self.advertencia_label.setText("\n".join(advertencias))
        else:
            self.advertencia_label.setText("")
        self.ultimo_resultado = {
            'valor': valor,
            'resultado': resultado,
            'advertencias': advertencias
        }
        self.boton_verificar.setEnabled(True)
        self.boton_agregar.setEnabled(True)
        self.log(f"Verificación de IOC completada: {resultado}", "info")

    def agregar_ioc_threaded(self):
        self.run_in_thread(self._agregar_ioc, self._on_agregar_ioc)

    def _agregar_ioc(self):
        valor = self.entrada.text().strip()
        QApplication.processEvents()
        if valor:
            self.iocs_manuales.add(valor)
            return (f"IOC añadido manualmente: {valor}", valor)
        return ("No se pudo agregar el IOC.", None)

    def _on_agregar_ioc(self, result):
        mensaje, valor = result
        self.resultados.clear()
        self.resultados.addItem(mensaje)
        if valor:
            self.ultimo_resultado = {
                'valor': valor,
                'resultado': mensaje,
                'advertencias': []
            }
        self.boton_verificar.setEnabled(True)
        self.boton_agregar.setEnabled(True)
        self.log(f"Agregado IOC manual: {mensaje}", "info")

    def agregar_ioc(self):
        self.agregar_ioc_threaded()

    def verificar(self):
        self.verificar_threaded()

    def agregar_ioc_sin_thread(self):
        result = self._agregar_ioc()
        self._on_agregar_ioc(result)
        return result

    def verificar_sin_thread(self):
        result = self._verificar()
        self._on_verificar(result)
        return result
