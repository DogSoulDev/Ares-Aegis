"""
Módulo para el análisis de red y detección de honeypots/evil twins.
Utiliza scapy para analizar servicios y certificados sospechosos.
"""


import os
import subprocess


class AnalizadorRed:
    def __init__(self, rango_red):
        self.rango_red = rango_red

    def es_root(self):
        return os.geteuid() == 0

    def escanear_dispositivos(self):
        dispositivos = []
        advertencias = []
        if self.es_root():
            try:
                from scapy.layers.l2 import arping
                respuesta, _ = arping(self.rango_red, verbose=0)
                for _, recibido in respuesta:
                    dispositivos.append({'ip': recibido.psrc, 'mac': recibido.hwsrc})
            except ImportError:
                advertencias.append("Scapy no está instalado. Instala el paquete 'scapy' para análisis avanzado.")
            except PermissionError:
                advertencias.append("Permiso denegado al usar Scapy. Ejecuta como root para análisis avanzado.")
            except Exception as e:
                advertencias.append(f"Error al usar scapy: {e}. Intentando método alternativo.")
            # Intentar método alternativo aunque sea root
            try:
                resultado = subprocess.check_output(['arp', '-a'], text=True)
                for linea in resultado.splitlines():
                    partes = linea.split()
                    if len(partes) >= 4:
                        ip = partes[1].strip('()')
                        mac = partes[3]
                        dispositivos.append({'ip': ip, 'mac': mac})
            except FileNotFoundError:
                advertencias.append("El comando 'arp' no está disponible. Instala el paquete 'net-tools'.")
            except Exception as e2:
                advertencias.append(f"Error al usar arp: {e2}")
        else:
            try:
                resultado = subprocess.check_output(['arp', '-a'], text=True)
                for linea in resultado.splitlines():
                    partes = linea.split()
                    if len(partes) >= 4:
                        ip = partes[1].strip('()')
                        mac = partes[3]
                        dispositivos.append({'ip': ip, 'mac': mac})
            except FileNotFoundError:
                advertencias.append("El comando 'arp' no está disponible. Instala el paquete 'net-tools'.")
            except Exception as e:
                advertencias.append(f"Error al usar arp: {e}")
        return dispositivos, advertencias

    def fingerprint_dispositivo(self, ip):
        # Fingerprinting básico: banner grab, TTL, puertos comunes
        info = {}
        try:
            import socket
            sock = socket.socket()
            sock.settimeout(1)
            for puerto in [22, 23, 80, 443, 3306]:
                try:
                    sock.connect((ip, puerto))
                    info[f"puerto_{puerto}"] = "abierto"
                except Exception:
                    info[f"puerto_{puerto}"] = "cerrado"
            sock.close()
        except Exception:
            pass
        return info

    def detectar_honeypots(self):
        dispositivos, advertencias = self.escanear_dispositivos()
        sospechosos = []
        explicaciones = []
        if not self.es_root():
            advertencias.append('El escaneo avanzado requiere permisos de root. Ejecute el programa con "sudo" para resultados completos.')
        for disp in dispositivos:
            # Heurística: MACs genéricas, IPs raras, puertos abiertos inusuales
            mac = disp.get('mac', '')
            ip = disp.get('ip', '')
            fingerprint = self.fingerprint_dispositivo(ip)
            if mac.startswith('00:00:00') or mac.startswith('de:ad:be:ef'):
                sospechosos.append(disp)
                explicaciones.append(f"Dispositivo {ip} tiene MAC sospechosa: {mac}")
            elif any(fingerprint.get(f"puerto_{p}") == "abierto" for p in [23, 3306]):
                sospechosos.append(disp)
                explicaciones.append(f"Dispositivo {ip} tiene puertos inusuales abiertos (ej: Telnet/MySQL)")
        return sospechosos, advertencias, explicaciones
