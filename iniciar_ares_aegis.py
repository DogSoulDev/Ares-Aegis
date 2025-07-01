#!/usr/bin/env python3
"""
Ares Aegis: Antivirus Avanzado para Kali Linux
Script principal de inicio con verificación de privilegios

Autor: DogSoulDev
Versión: 2.0.0
Fecha: 2025-06-30
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

# Importar la clase principal de la interfaz
from ares_aegis.vista.interfaz_principal_gui import InterfazPrincipalGUI


def verificar_privilegios():
    """Verifica si el programa se está ejecutando con privilegios de root."""
    return os.geteuid() == 0


def mostrar_error_privilegios():
    """Muestra error de privilegios tanto en GUI como en consola."""
    mensaje_error = ("Ares Aegis requiere privilegios de ROOT para funcionar correctamente.\n"
                    "Por favor, ejecútelo con 'sudo python3 iniciar_ares_aegis.py'.")
    
    # Si hay entorno gráfico disponible, usar messagebox
    if 'DISPLAY' in os.environ:
        try:
            root = tk.Tk()
            root.withdraw()  # Ocultar la ventana principal
            messagebox.showerror("Error de Privilegios", mensaje_error)
            root.destroy()
        except Exception:
            # Si falla la GUI, usar consola
            print(f"Error: {mensaje_error}")
    else:
        # Si no hay entorno gráfico, imprimir en consola
        print(f"Error: {mensaje_error}")


def main():
    """Función principal para iniciar Ares Aegis."""
    print("🛡️  Iniciando Ares Aegis: Antivirus Avanzado para Kali Linux")
    print("=" * 60)
    
    # Verificar privilegios de root
    if not verificar_privilegios():
        print("❌ Se requieren privilegios de ROOT para ejecutar Ares Aegis")
        mostrar_error_privilegios()
        sys.exit(1)
    
    print("✅ Privilegios de ROOT confirmados")
    print("🚀 Iniciando interfaz gráfica...")
    
    try:
        # Crear ventana principal y lanzar aplicación
        ventana_raiz = tk.Tk()
        app = InterfazPrincipalGUI(ventana_raiz)
        ventana_raiz.mainloop()
        
    except KeyboardInterrupt:
        print("\n⚡ Interrupción por teclado detectada")
        print("🔒 Cerrando Ares Aegis...")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error crítico al iniciar la aplicación: {e}")
        if 'DISPLAY' in os.environ:
            try:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Error Crítico", 
                                   f"No se pudo iniciar Ares Aegis:\n{e}")
                root.destroy()
            except Exception:
                pass
        sys.exit(1)
    
    print("🔒 Ares Aegis finalizado correctamente")


if __name__ == "__main__":
    main()
