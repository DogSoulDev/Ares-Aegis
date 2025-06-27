"""
Panel visual de Ares Aegis para el escaneo del sistema operativo, carpetas y programas instalados.
Estilo minimalista japonés, limpio y diferente.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QApplication
from PySide6.QtCore import Qt


class PanelEscaneoSistema(QWidget):
    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        self.setWindowTitle("Ares Aegis - Escaneo Avanzado del Sistema (Principal)")
        self.setStyleSheet("background: #f6f6f6; font-family: 'Noto Sans JP'; color: #222;")
        layout = QVBoxLayout()
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px;")
        self.advertencia_label.setWordWrap(True)
        self.resultados = QListWidget()
        self.boton_resumen = QPushButton("Resumen General del Sistema")
        self.boton_resumen.clicked.connect(self.mostrar_resumen)
        self.boton_rootkits = QPushButton("Analizar Rootkits")
        self.boton_rootkits.clicked.connect(self.analizar_rootkits)
        self.boton_procesos = QPushButton("Procesos Sospechosos")
        self.boton_procesos.clicked.connect(self.analizar_procesos)
        self.boton_puertos = QPushButton("Puertos Abiertos")
        self.boton_puertos.clicked.connect(self.analizar_puertos)
        self.boton_servicios = QPushButton("Servicios Activos")
        self.boton_servicios.clicked.connect(self.analizar_servicios)
        self.boton_integridad = QPushButton("Verificar Integridad Binarios Críticos")
        self.boton_integridad.clicked.connect(self.analizar_integridad)
        self.boton_programas = QPushButton("Listar Programas Instalados")
        self.boton_programas.clicked.connect(self.listar_programas)
        self.boton_exportar = QPushButton("Exportar Informe Completo")
        self.boton_exportar.clicked.connect(self.exportar_informe)
        layout.addWidget(QLabel("Ares Aegis: Escaneo avanzado del sistema operativo y programas instalados. Prioridad máxima de seguridad.\n"))
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.resultados)
        layout.addWidget(self.boton_resumen)
        layout.addWidget(self.boton_rootkits)
        layout.addWidget(self.boton_procesos)
        layout.addWidget(self.boton_puertos)
        layout.addWidget(self.boton_servicios)
        layout.addWidget(self.boton_integridad)
        layout.addWidget(self.boton_programas)
        layout.addWidget(self.boton_exportar)
        self.setLayout(layout)
        # Hashes de referencia de ejemplo, en producción descargar automáticamente
        self.base_hashes = {"/bin/ls": "HASH_DE_REFERENCIA"}
        self.ultimo_resumen = None

    def mostrar_resumen(self):
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Analizando el sistema... Por favor, espera.")
        QApplication.processEvents()
        resumen = self.controlador.obtener_resumen(self.base_hashes)
        self.ultimo_resumen = resumen
        self.resultados.clear()
        self.resultados.addItem("--- RESUMEN GENERAL DEL SISTEMA ---")
        advertencias = []
        # Rootkits
        rootkits = resumen.get('rootkits', [])
        if rootkits and any("INFECTED" in r or "infectado" in r.lower() for r in rootkits):
            self.resultados.addItem("[CRÍTICO] Posible rootkit detectado!")
            advertencias.append("Se recomienda ejecutar un análisis en modo seguro y revisar manualmente los binarios afectados.")
        else:
            self.resultados.addItem("[OK] Sin rootkits detectados.")
        # Procesos
        procesos = resumen.get('procesos', [])
        if procesos and "Sin procesos sospechosos detectados." not in procesos:
            self.resultados.addItem("[ADVERTENCIA] Procesos sospechosos:")
            for p in procesos:
                self.resultados.addItem(p)
            advertencias.append("Procesos sospechosos detectados. Revisa los procesos listados y considera finalizar los que no reconozcas.")
        else:
            self.resultados.addItem("[OK] Sin procesos sospechosos.")
        # Puertos
        puertos = resumen.get('puertos', [])
        self.resultados.addItem("Puertos abiertos:")
        for p in puertos:
            self.resultados.addItem(p)
        # Servicios
        servicios = resumen.get('servicios', [])
        self.resultados.addItem("Servicios activos:")
        for s in servicios[:10]:
            self.resultados.addItem(s)
        # Integridad
        integridad = resumen.get('integridad', {})
        if integridad:
            self.resultados.addItem("[ADVERTENCIA] Binarios modificados o no encontrados:")
            for archivo, estado in integridad.items():
                self.resultados.addItem(f"{archivo}: {estado}")
            advertencias.append("Algunos binarios críticos han sido modificados o no se encuentran. Reinstala el sistema o restaura desde una copia confiable.")
        else:
            self.resultados.addItem("[OK] Integridad de binarios críticos verificada.")
        # Programas
        programas = resumen.get('programas', [])
        self.resultados.addItem(f"Total de programas instalados: {len(programas)}")
        self.resultados.addItem("--- FIN DEL RESUMEN ---")
        # Feedback visual de advertencias
        if advertencias:
            self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
            self.advertencia_label.setText("\n".join(advertencias))
        else:
            self.advertencia_label.setText("")

    def analizar_rootkits(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Analizando rootkits... Por favor, espera.")
        QApplication.processEvents()
        rootkits = self.controlador.escanear_rootkits()
        self.resultados.clear()
        self.resultados.addItem("Análisis de rootkits:")
        for r in rootkits:
            self.resultados.addItem(r)

    def analizar_procesos(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Analizando procesos... Por favor, espera.")
        QApplication.processEvents()
        procesos = self.controlador.escanear_procesos()
        self.resultados.clear()
        self.resultados.addItem("Procesos sospechosos:")
        for p in procesos:
            self.resultados.addItem(p)

    def analizar_puertos(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Analizando puertos abiertos... Por favor, espera.")
        QApplication.processEvents()
        puertos = self.controlador.escanear_puertos()
        self.resultados.clear()
        self.resultados.addItem("Puertos abiertos:")
        for p in puertos:
            self.resultados.addItem(p)

    def analizar_servicios(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Analizando servicios activos... Por favor, espera.")
        QApplication.processEvents()
        servicios = self.controlador.escanear_servicios()
        self.resultados.clear()
        self.resultados.addItem("Servicios activos:")
        for s in servicios:
            self.resultados.addItem(s)

    def analizar_integridad(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Verificando integridad de binarios... Por favor, espera.")
        QApplication.processEvents()
        integridad = self.controlador.escanear_integridad(self.base_hashes)
        self.resultados.clear()
        self.resultados.addItem("Verificación de integridad de binarios críticos:")
        if integridad:
            for archivo, estado in integridad.items():
                self.resultados.addItem(f"{archivo}: {estado}")
        else:
            self.resultados.addItem("Todos los binarios críticos están íntegros.")

    def listar_programas(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Listando programas instalados... Por favor, espera.")
        QApplication.processEvents()
        programas = self.controlador.obtener_programas()
        self.resultados.clear()
        self.resultados.addItem("Programas instalados:")
        for prog in programas[:100]:
            self.resultados.addItem(prog)
        if len(programas) > 100:
            self.resultados.addItem(f"...y {len(programas)-100} más.")

    def exportar_informe(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Exportando informe PDF profesional... Por favor, espera.")
        QApplication.processEvents()
        if not self.ultimo_resumen:
            self.mostrar_resumen()
        # Se puede obtener el usuario real si se desea
        import getpass
        usuario = getpass.getuser()
        ruta = self.controlador.exportar_informe(self.ultimo_resumen, usuario=usuario)
        self.resultados.addItem(f"Informe PDF exportado a: {ruta}")
