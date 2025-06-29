#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Launcher mejorado para Ares-Aegis
Con interfaz minimalista japonesa y manejo de errores robusto
"""

import sys
import os
import asyncio
import threading
import traceback
from pathlib import Path
from typing import Optional

# Añadir el directorio padre al path para importaciones
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

from antivirus_kali.utilidades.logger import SiemLogger
from antivirus_kali.utilidades.auxiliares import verificar_conectividad_red, obtener_info_sistema
from antivirus_kali.interfaz.ventana_principal_minimalista import VentanaPrincipalMinimalista


class LauncherAresAegis:
    """
    Launcher principal de Ares-Aegis con interfaz minimalista
    """
    
    def __init__(self):
        self.logger = SiemLogger(__name__)
        self.app: Optional[QApplication] = None
        self.ventana_principal: Optional[VentanaPrincipalMinimalista] = None
        
    def inicializar_aplicacion(self) -> bool:
        """Inicializa la aplicación Qt"""
        try:
            # Crear aplicación Qt
            self.app = QApplication(sys.argv)
            
            # Configurar aplicación
            self.app.setApplicationName("Ares-Aegis")
            self.app.setApplicationVersion("2.0")
            self.app.setOrganizationName("Ares-Aegis Security")
            self.app.setOrganizationDomain("ares-aegis.security")
            
            # Configurar atributos Qt
            self.app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            self.app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
            
            self.logger.info("Aplicación Qt inicializada correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando aplicación Qt: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def verificar_sistema(self) -> bool:
        """Verifica que el sistema esté listo"""
        try:
            # Verificar información del sistema
            info_sistema = obtener_info_sistema()
            self.logger.info(f"Sistema: {info_sistema.get('nombre', 'Desconocido')}")
            self.logger.info(f"Arquitectura: {info_sistema.get('arquitectura', 'Desconocida')}")
            
            # Verificar conectividad
            if verificar_conectividad_red():
                self.logger.info("Conectividad de red verificada")
            else:
                self.logger.warning("Sin conectividad de red")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error verificando sistema: {e}")
            return False
    
    def mostrar_error_critico(self, mensaje: str, detalle: str = ""):
        """Muestra un error crítico al usuario"""
        try:
            if self.app:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Error Crítico - Ares-Aegis")
                msg.setText(mensaje)
                if detalle:
                    msg.setDetailedText(detalle)
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
        except:
            # Si incluso la ventana de error falla, usar print
            print(f"ERROR CRÍTICO: {mensaje}")
            if detalle:
                print(f"Detalle: {detalle}")
    
    def crear_ventana_principal(self) -> bool:
        """Crea la ventana principal"""
        try:
            self.ventana_principal = VentanaPrincipalMinimalista()
            self.logger.info("Ventana principal creada exitosamente")
            return True
            
        except ImportError as e:
            error_msg = f"Error de importación: {e}"
            self.logger.error(error_msg)
            self.mostrar_error_critico(
                "Error de dependencias",
                f"No se pudieron cargar las dependencias necesarias:\n{error_msg}\n\nVerifique que PySide6 esté instalado correctamente."
            )
            return False
            
        except Exception as e:
            error_msg = f"Error creando ventana principal: {e}"
            self.logger.error(error_msg)
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.mostrar_error_critico(
                "Error de inicialización",
                f"No se pudo crear la interfaz principal:\n{error_msg}"
            )
            return False
    
    def ejecutar(self) -> int:
        """Ejecuta la aplicación principal"""
        codigo_salida = 1
        
        try:
            self.logger.info("=== Iniciando Ares-Aegis ===")
            
            # Verificar sistema
            if not self.verificar_sistema():
                self.logger.error("Falló la verificación del sistema")
                return 1
            
            # Inicializar aplicación
            if not self.inicializar_aplicacion():
                self.logger.error("Falló la inicialización de la aplicación")
                return 1
            
            # Crear ventana principal
            if not self.crear_ventana_principal():
                self.logger.error("Falló la creación de la ventana principal")
                return 1
            
            # Mostrar ventana
            self.ventana_principal.show()
            self.logger.info("Ventana principal mostrada")
            
            # Ejecutar loop principal
            self.logger.info("Iniciando loop principal de la aplicación")
            codigo_salida = self.app.exec()
            
            self.logger.info(f"Aplicación terminada con código: {codigo_salida}")
            
        except KeyboardInterrupt:
            self.logger.info("Aplicación interrumpida por el usuario")
            codigo_salida = 0
            
        except Exception as e:
            error_msg = f"Error crítico en ejecución: {e}"
            self.logger.error(error_msg)
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            self.mostrar_error_critico(
                "Error crítico",
                f"Se produjo un error inesperado:\n{error_msg}"
            )
            codigo_salida = 1
            
        finally:
            self.logger.info("=== Finalizando Ares-Aegis ===")
            
        return codigo_salida


def main():
    """Función principal"""
    try:
        launcher = LauncherAresAegis()
        return launcher.ejecutar()
        
    except Exception as e:
        print(f"ERROR CRÍTICO EN LAUNCHER: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
