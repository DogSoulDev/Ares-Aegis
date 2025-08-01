#!/usr/bin/env python3
"""
Ares Aegis v4.0 - Cybersecurity Suite
Sistema de seguridad avanzado con interfaz mitológica optimizado para Kali Linux

Creado por DogSoulDev
Versión: 4.0.0 - Edición Mitológica con Colores Kali Linux
"""

import sys
import os
import logging
import tkinter as tk
import subprocess
import platform
import signal
import atexit
import threading
from pathlib import Path
from tkinter import messagebox

sys.path.insert(0, str(Path(__file__).parent))

try:
    from ares_aegis.utils.ayuda_logging import configurar_logging_completo
except ImportError:
    def configurar_logging_completo():
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

# Variables globales para manejo de cierre
interfaz_global = None
logger_global = None


def verificar_permisos_root():
    """
    Verifica si el programa se está ejecutando con permisos de administrador.
    En Kali Linux, muchas funciones de seguridad requieren permisos elevados.
    """
    if platform.system() == "Windows":
        # En Windows, verificar si se ejecuta como administrador
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        # En Linux/Unix, verificar si es root (UID 0)
        try:
            # Verificar si geteuid está disponible antes de usarlo
            geteuid_func = getattr(os, 'geteuid', None)
            if geteuid_func is not None:
                return geteuid_func() == 0
            else:
                return False
        except (AttributeError, OSError):
            # geteuid no está disponible en Windows o hay un error
            return False


def limpiar_recursos_aplicacion():
    """Función de limpieza global para recursos de la aplicación"""
    global interfaz_global, logger_global
    
    try:
        if logger_global:
            logger_global.info("🧹 Iniciando limpieza de recursos de la aplicación...")
        
        # Finalizar interfaz si está activa
        if interfaz_global:
            try:
                if hasattr(interfaz_global, '_cerrar_aplicacion'):
                    interfaz_global._cerrar_aplicacion()
                elif hasattr(interfaz_global, 'root') and interfaz_global.root:
                    try:
                        interfaz_global.root.quit()
                    except tk.TclError:
                        pass  # Ventana ya cerrada
                    try:
                        interfaz_global.root.destroy()
                    except tk.TclError:
                        pass  # Ventana ya destruida
                if logger_global:
                    logger_global.info("✅ Interfaz finalizada correctamente")
            except Exception as e:
                if logger_global:
                    logger_global.debug(f"Advertencia finalizando interfaz: {e}")
                # No es crítico si la interfaz ya se cerró
        
        # Finalizar hilos restantes
        try:
            import threading
            hilos_activos = threading.enumerate()
            hilos_daemon = [h for h in hilos_activos if h.daemon and h != threading.current_thread()]
            
            if hilos_daemon and logger_global:
                logger_global.info(f"🔄 Finalizando {len(hilos_daemon)} hilos daemon...")
                
            for hilo in hilos_daemon:
                try:
                    hilo.join(timeout=1.0)
                except:
                    pass
                    
        except Exception as e:
            if logger_global:
                logger_global.error(f"Error limpiando hilos: {e}")
        
        if logger_global:
            logger_global.info("🏛️ Limpieza de recursos completada")
            
    except Exception as e:
        if logger_global:
            logger_global.error(f"Error en limpieza de recursos: {e}")
        else:
            print(f"Error en limpieza de recursos: {e}")


def manejador_senal_cierre(signum, frame):
    """Manejador para señales de cierre del sistema"""
    global logger_global
    
    try:
        if logger_global:
            logger_global.info(f"📡 Señal {signum} recibida, iniciando cierre seguro...")
        else:
            print(f"📡 Señal {signum} recibida, cerrando aplicación...")
        
        limpiar_recursos_aplicacion()
        sys.exit(0)
        
    except Exception as e:
        if logger_global:
            logger_global.error(f"Error en manejador de señal: {e}")
        else:
            print(f"Error en manejador de señal: {e}")
        sys.exit(1)


def configurar_manejadores_senal():
    """Configurar manejadores de señales para cierre limpio"""
    try:
        # Registrar manejadores de señales (solo en sistemas Unix-like)
        if platform.system() != "Windows":
            signal.signal(signal.SIGINT, manejador_senal_cierre)   # Ctrl+C
            signal.signal(signal.SIGTERM, manejador_senal_cierre)  # Terminación
            try:
                # Verificar si SIGHUP está disponible usando getattr
                sighup_signal = getattr(signal, 'SIGHUP', None)
                if sighup_signal is not None:
                    signal.signal(sighup_signal, manejador_senal_cierre)   # Hangup
            except (AttributeError, OSError):
                pass  # SIGHUP no disponible en este sistema
        else:
            # En Windows, solo registrar SIGINT (Ctrl+C)
            signal.signal(signal.SIGINT, manejador_senal_cierre)
        
        # Registrar función de limpieza para salida normal
        atexit.register(limpiar_recursos_aplicacion)
        
    except Exception as e:
        if logger_global:
            logger_global.warning(f"No se pudieron configurar algunos manejadores de señal: {e}")


def solicitar_permisos_root():
    """
    Solicita permisos de root y reinicia la aplicación con sudo si es necesario.
    """
    if platform.system() != "Windows" and not verificar_permisos_root():
        logger = logging.getLogger(__name__)
        
        # Mostrar diálogo explicativo
        root = tk.Tk()
        root.withdraw()
        
        respuesta = messagebox.askyesno(
            "🛡️ Ares Aegis - Permisos Requeridos",
            "Ares Aegis requiere permisos de administrador para:\n\n"
            "[ACCESS] Acceder a archivos del sistema\n"
            "[MONITOR] Monitorear procesos y servicios\n"
            "[NETWORK] Analizar tráfico de red\n"
            "[AUDIT] Auditar configuraciones de seguridad\n"
            "[QUARANTINE] Gestionar cuarentena de archivos\n\n"
            "¿Deseas continuar con permisos elevados?\n"
            "(Se solicitará tu contraseña)",
            icon='question'
        )
        
        root.destroy()
        
        if respuesta:
            try:
                # Intentar ejecutar con sudo
                logger.info("[ADMIN] Solicitando permisos de administrador...")
                
                # Construir comando sudo
                python_exec = sys.executable
                script_path = os.path.abspath(__file__)
                args = [python_exec, script_path] + sys.argv[1:]
                
                # Ejecutar con sudo
                resultado = subprocess.run(['sudo'] + args, check=False)
                sys.exit(resultado.returncode)
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Error al ejecutar con sudo: {e}")
                messagebox.showerror(
                    "Error de Permisos",
                    "No se pudieron obtener permisos de administrador.\n"
                    "Algunas funciones pueden no estar disponibles."
                )
                return False
                
            except FileNotFoundError:
                logger.error("sudo no está disponible en el sistema")
                messagebox.showerror(
                    "Error de Sistema",
                    "sudo no está disponible.\n"
                    "Por favor, ejecuta el programa manualmente con:\n"
                    f"sudo python3 {script_path}"
                )
                return False
        else:
            logger.info("Usuario canceló la solicitud de permisos")
            return False
    
    return True


def verificar_entorno_kali():
    """
    Verifica si el sistema es Kali Linux y muestra información relevante.
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Verificar si es Kali Linux
        if platform.system() == "Windows":
            logger.warning("[WARNING] Ejecutándose en Windows - Ares Aegis está optimizado para Kali Linux")
            logger.warning("[WARNING] Algunas funciones pueden no estar disponibles o funcionar de forma limitada")
            return False
        elif os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                contenido = f.read()
                if 'kali' in contenido.lower():
                    logger.info("[SUCCESS] Kali Linux detectado - Optimizaciones activas")
                    return True
                else:
                    logger.warning("[WARNING] Sistema no es Kali Linux - Funciones limitadas")
                    return False
    except Exception as e:
        logger.debug(f"No se pudo verificar el sistema: {e}")
    
    return False


def mostrar_banner_inicio():
    """
    Muestra banner de inicio en la consola.
    """
    print("\033[96m" + "="*70)
    print("🛡️  ARES AEGIS v4.0 - CYBERSECURITY SUITE 🛡️")
    print("="*70)
    if platform.system() == "Windows":
        print("⚠️  ADVERTENCIA: Ejecutándose en Windows")
        print("🎯 Optimizado para Kali Linux - Funcionalidad limitada")
    else:
        print("🎯 Optimizado para Kali Linux")
    print("🔐 Suite de Seguridad Avanzada")
    print("⚡ Iniciando con permisos de administrador...")
    print("="*70 + "\033[0m")
    print()


def main():
    """Función principal de entrada con verificación de permisos automática."""
    global interfaz_global, logger_global
    
    try:
        # Mostrar banner de inicio
        mostrar_banner_inicio()
        
        # Verificar y solicitar permisos de root ANTES de cualquier otra cosa
        if not solicitar_permisos_root():
            logger_global = configurar_logging_completo()
            logger_global.warning("[WARNING] Usuario decidió continuar sin permisos de administrador")
            
            # Mostrar advertencia final
            respuesta = messagebox.askyesno(
                "⚠️ Funcionalidad Limitada",
                "🚨 ADVERTENCIA: Ares Aegis funcionará con capacidades limitadas.\n\n"
                "Sin permisos de root, las siguientes funciones NO estarán disponibles:\n"
                "• Escaneo profundo de vulnerabilidades\n"
                "• Monitoreo de archivos del sistema\n"
                "• Análisis de tráfico de red\n"
                "• Auditoría completa de PAM\n"
                "• Acceso a logs críticos del sistema\n\n"
                "¿Deseas continuar de todas formas?"
            )
            
            if not respuesta:
                print("\033[91m🛑 Ejecución cancelada por el usuario\033[0m")
                sys.exit(0)
        
        # Configurar logging
        logger_global = configurar_logging_completo()
        logger = logger_global
        
        # Configurar manejadores de señales para cierre limpio
        configurar_manejadores_senal()
        
        logger.info("=" * 60)
        logger.info("🚀 Iniciando Ares Aegis v4.0 - Cybersecurity Suite")
        logger.info("=" * 60)
        
        # Verificar entorno Kali Linux
        es_kali = verificar_entorno_kali()
        
        # Mostrar información de permisos actuales
        if verificar_permisos_root():
            logger.info("[ADMIN] Ejecutándose con permisos de administrador")
            print("\033[92m✅ Permisos de administrador activos - Funcionalidad completa\033[0m")
        else:
            logger.warning("[WARNING] Ejecutándose sin permisos de administrador")
            print("\033[93m⚠️ Funcionalidad limitada - Algunas características no disponibles\033[0m")
        
        logger.info("🎯 Cargando interfaz Escudo Divino de Ciberseguridad 4.0...")
        
        try:
            # Usar la interfaz principal (Escudo Divino de Ciberseguridad 4.0)
            from ares_aegis.vista.interfaz_principal import InterfazPrincipalAresAegis
            interfaz = InterfazPrincipalAresAegis()
            interfaz_global = interfaz  # Asignar a variable global para limpieza
            
            # Intentar cargar controlador principal
            try:
                from ares_aegis.controladores.controlador_principal import ControladorPrincipal
                controlador = ControladorPrincipal()
                # La interfaz simple maneja el controlador internamente
                interfaz.inicializar(controlador)
                logger.info("[SUCCESS] Escudo Divino de Ciberseguridad 4.0 inicializado con controlador")
            except Exception as e:
                logger.warning(f"Controlador no disponible: {e}")
                interfaz.inicializar()
                logger.info("[SUCCESS] Escudo Divino de Ciberseguridad 4.0 inicializado sin controlador")
            
            # Información adicional para Kali Linux
            if es_kali and verificar_permisos_root():
                logger.info("[SHIELD] Todas las funciones de seguridad están disponibles")
            
            # Configurar protocolo de cierre de ventana
            if hasattr(interfaz, 'root') and interfaz.root:
                interfaz.root.protocol("WM_DELETE_WINDOW", lambda: interfaz._cerrar_aplicacion())
            
            interfaz.ejecutar()
            return True
            
        except Exception as e:
            logger.error(f"Error cargando interfaz Escudo Divino: {e}")
            logger.info("🔄 No se pudo cargar la interfaz principal...")
            
            # Mostrar error y terminar
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Error crítico",
                f"No se pudo iniciar Ares Aegis:\n{e}\n\nVerifica que todos los archivos estén presentes."
            )
            return False
        
    except KeyboardInterrupt:
        print("\n⏹️ Aplicación interrumpida por el usuario")
        if logger_global:
            logger_global.info("Aplicación interrumpida por el usuario")
        limpiar_recursos_aplicacion()
        return True
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        if logger_global:
            logger_global.error(f"Error crítico en main: {e}", exc_info=True)
        try:
            messagebox.showerror("Error Crítico", 
                               f"Error inesperado en la aplicación.\nError: {e}")
        except:
            print("No se pudo mostrar el diálogo de error")
        limpiar_recursos_aplicacion()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
