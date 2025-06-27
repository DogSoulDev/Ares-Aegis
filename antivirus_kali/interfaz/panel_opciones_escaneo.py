from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QFileDialog, QMessageBox, QStyle
from PySide6.QtCore import Qt

class PanelOpcionesEscaneo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ares Aegis - Opciones Avanzadas de Escaneo")
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
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("Opciones Avanzadas de Escaneo", self)
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        titulo.setAccessibleName("Título opciones escaneo")
        layout.addWidget(titulo)
        
        # Lista de carpetas
        self.lista_carpetas = QListWidget(self)
        self.lista_carpetas.setToolTip("Carpetas seleccionadas para escaneo avanzado.")
        layout.addWidget(self.lista_carpetas)
        
        # Botones
        boton_agregar = QPushButton("Agregar Carpeta", self)
        boton_agregar.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        boton_agregar.setToolTip("Agregar una carpeta a la lista de escaneo.")
        layout.addWidget(boton_agregar)
        
        boton_eliminar = QPushButton("Eliminar Carpeta", self)
        boton_eliminar.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton))
        boton_eliminar.setToolTip("Eliminar la carpeta seleccionada de la lista.")
        layout.addWidget(boton_eliminar)
        
        boton_exportar = QPushButton("Exportar Lista", self)
        boton_exportar.setObjectName("exportar")
        boton_exportar.setToolTip("Exportar la lista de carpetas seleccionadas.")
        layout.addWidget(boton_exportar)
        
        # Conectar señales
        boton_agregar.clicked.connect(self.agregar_carpetas)
        boton_eliminar.clicked.connect(self.eliminar_carpetas)
        boton_exportar.clicked.connect(self.exportar_lista)
        
        self.setLayout(layout)
    
    def agregar_carpetas(self):
        # Lógica para agregar carpetas
        pass
    
    def eliminar_carpetas(self):
        # Lógica para eliminar carpetas
        pass
    
    def exportar_lista(self):
        # Lógica para exportar lista de carpetas
        pass
