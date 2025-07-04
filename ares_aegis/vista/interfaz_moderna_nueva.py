#!/usr/bin/env python3
"""
Interfaz Moderna de Ares Aegis - Archivo Principal Integrado
Sistema de Ciberseguridad con UX/UI Profesional

🛡️ INTEGRACIÓN COMPLETA DE MÓDULOS
"""

import logging
from .interfaz_moderna_base import InterfazModernaBase
from .interfaz_moderna_herramientas import InterfazModernaHerramientas


class InterfazModerna:
    """Interfaz principal que integra todos los módulos"""
    
    def __init__(self):
        """Inicializar la interfaz completa"""
        self.logger = logging.getLogger(__name__)
        
        # Inicializar interfaz base
        self.interfaz_base = InterfazModernaBase()
        
        # Inicializar módulos de herramientas
        self.herramientas = InterfazModernaHerramientas(self.interfaz_base)
        
        # Integrar navegación avanzada
        self._integrar_navegacion_avanzada()
        
        self.logger.info("Interfaz Moderna completa inicializada")
    
    def _integrar_navegacion_avanzada(self):
        """Integrar navegación con módulos avanzados"""
        # Sobrescribir métodos de navegación en la interfaz base
        self.interfaz_base.mostrar_monitoreo = self.herramientas.mostrar_monitoreo
        self.interfaz_base.mostrar_proteccion = self.herramientas.mostrar_proteccion  
        self.interfaz_base.mostrar_herramientas = self.herramientas.mostrar_herramientas
    
    def inicializar(self):
        """Inicializar la aplicación completa"""
        return self.interfaz_base.inicializar()
    
    def ejecutar(self):
        """Ejecutar la aplicación"""
        self.interfaz_base.ejecutar()
    
    # Exponer propiedades importantes
    @property
    def root(self):
        return self.interfaz_base.root
    
    @property
    def controlador(self):
        return self.interfaz_base.controlador
    
    @property
    def logger_interfaz(self):
        return self.interfaz_base.logger


# Función de conveniencia para crear y ejecutar la aplicación
def crear_y_ejecutar_interfaz():
    """Crear y ejecutar la interfaz moderna completa"""
    try:
        interfaz = InterfazModerna()
        interfaz.ejecutar()
    except Exception as e:
        import tkinter.messagebox as messagebox
        messagebox.showerror("Error Fatal", f"Error ejecutando Ares Aegis:\n{str(e)}")


if __name__ == "__main__":
    crear_y_ejecutar_interfaz()
