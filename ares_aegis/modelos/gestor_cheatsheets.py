#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Gestor de Cheatsheets
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, NamedTuple, Set
from dataclasses import dataclass
from ..utilidades.ayuda_logging import configurar_logger_modulo


@dataclass
class Comando:
    """Representa un comando o técnica."""
    nombre: str
    descripcion: str
    comando: str
    ejemplo: str
    categoria: str
    tags: List[str]
    plataforma: List[str]  # linux, windows, macos, all
    nivel: str  # basico, intermedio, avanzado
    peligrosidad: str  # seguro, moderado, peligroso
    referencias: List[str]


@dataclass
class Cheatsheet:
    """Representa una hoja de referencia completa."""
    nombre: str
    descripcion: str
    categoria: str
    autor: str
    version: str
    fecha_creacion: datetime
    fecha_modificacion: datetime
    comandos: List[Comando]
    metadatos: Dict[str, Any]


class GestorCheatsheets:
    """Gestor principal de hojas de referencia."""
    
    def __init__(self):
        """Inicializa el gestor de cheatsheets."""
        self.logger = configurar_logger_modulo("gestor_cheatsheets")
        
        # Configuración de rutas
        self.directorio_cheatsheets = Path("/home/dogsoul/Ares-Aegis/recursos/cheatsheets")
        self.archivo_indice = self.directorio_cheatsheets / "indice.json"
        
        # Almacenamiento en memoria
        self.cheatsheets: Dict[str, Cheatsheet] = {}
        self.indice_comandos: Dict[str, List[str]] = {}  # tag -> lista de cheatsheet IDs
        self.categorias: Set[str] = set()
        
        # Configuración de categorías predefinidas
        self.categorias_predefinidas = {
            'reconocimiento': 'Técnicas de reconocimiento y enumeración',
            'escaneo': 'Herramientas de escaneo de redes y puertos',
            'vulnerabilidades': 'Exploración y explotación de vulnerabilidades',
            'post-explotacion': 'Técnicas post-explotación y persistencia',
            'forense': 'Análisis forense y investigación de incidentes',
            'hardening': 'Endurecimiento y configuración segura de sistemas',
            'monitoreo': 'Monitoreo y detección de amenazas',
            'respuesta': 'Respuesta a incidentes y contención',
            'herramientas': 'Herramientas de seguridad y utilidades',
            'networking': 'Comandos de red y conectividad',
            'sistema': 'Administración de sistemas y procesos',
            'logs': 'Análisis de logs y registro de eventos'
        }
        
        self.logger.info("Los Escribanos de Hermes despiertan para organizar el conocimiento")
        
        # Inicializar datos
        self._inicializar_cheatsheets()
    
    def _inicializar_cheatsheets(self):
        """Inicializa las cheatsheets predefinidas."""
        try:
            # Crear directorio si no existe
            self.directorio_cheatsheets.mkdir(parents=True, exist_ok=True)
            
            # Cargar cheatsheets existentes
            if self.archivo_indice.exists():
                self._cargar_indice()
            else:
                self._crear_cheatsheets_predefinidas()
                self._guardar_indice()
            
            self.logger.info(f"Cheatsheets inicializadas: {len(self.cheatsheets)} hojas disponibles")
            
        except Exception as e:
            self.logger.error(f"Error inicializando cheatsheets: {e}")
    
    def _crear_cheatsheets_predefinidas(self):
        """Crea cheatsheets predefinidas con comandos esenciales."""
        
        # Cheatsheet de Reconocimiento
        self._crear_cheatsheet_reconocimiento()
        
        # Cheatsheet de Escaneo de Red
        self._crear_cheatsheet_escaneo_red()
        
        # Cheatsheet de Análisis de Logs
        self._crear_cheatsheet_analisis_logs()
        
        # Cheatsheet de Forense
        self._crear_cheatsheet_forense()
        
        # Cheatsheet de Hardening
        self._crear_cheatsheet_hardening()
        
        # Cheatsheet de Respuesta a Incidentes
        self._crear_cheatsheet_respuesta_incidentes()
    
    def _crear_cheatsheet_reconocimiento(self):
        """Crea cheatsheet de técnicas de reconocimiento."""
        comandos = [
            Comando(
                nombre="Información del Sistema",
                descripcion="Obtener información básica del sistema",
                comando="uname -a",
                ejemplo="uname -a",
                categoria="reconocimiento",
                tags=["sistema", "informacion", "kernel"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man uname"]
            ),
            Comando(
                nombre="Procesos en Ejecución",
                descripcion="Listar todos los procesos activos",
                comando="ps aux",
                ejemplo="ps aux | grep -i suspicious",
                categoria="reconocimiento",
                tags=["procesos", "monitoring"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man ps"]
            ),
            Comando(
                nombre="Conexiones de Red",
                descripcion="Mostrar conexiones de red activas",
                comando="netstat -tulnp",
                ejemplo="netstat -tulnp | grep LISTEN",
                categoria="reconocimiento",
                tags=["red", "conexiones", "puertos"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man netstat"]
            ),
            Comando(
                nombre="Usuarios Conectados",
                descripcion="Ver usuarios actualmente conectados",
                comando="who -a",
                ejemplo="who -a",
                categoria="reconocimiento",
                tags=["usuarios", "sesiones"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man who"]
            ),
            Comando(
                nombre="Historial de Comandos",
                descripcion="Revisar el historial de comandos del usuario",
                comando="history",
                ejemplo="history | tail -20",
                categoria="reconocimiento",
                tags=["historial", "comandos"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man history"]
            ),
            Comando(
                nombre="Archivos con SUID",
                descripcion="Buscar archivos con bit SUID activado",
                comando="find / -perm -4000 -type f 2>/dev/null",
                ejemplo="find /usr -perm -4000 -type f 2>/dev/null",
                categoria="reconocimiento",
                tags=["suid", "privilegios", "escalada"],
                plataforma=["linux"],
                nivel="intermedio",
                peligrosidad="moderado",
                referencias=["man find"]
            )
        ]
        
        cheatsheet = Cheatsheet(
            nombre="Reconocimiento del Sistema",
            descripcion="Comandos para reconocimiento inicial del sistema",
            categoria="reconocimiento",
            autor="Ares Aegis",
            version="1.0",
            fecha_creacion=datetime.now(),
            fecha_modificacion=datetime.now(),
            comandos=comandos,
            metadatos={"prioridad": "alta", "frecuencia_uso": "diaria"}
        )
        
        self.cheatsheets["reconocimiento"] = cheatsheet
    
    def _crear_cheatsheet_escaneo_red(self):
        """Crea cheatsheet de escaneo de red."""
        comandos = [
            Comando(
                nombre="Ping de Red",
                descripcion="Verificar conectividad básica",
                comando="ping -c 4 {target}",
                ejemplo="ping -c 4 192.168.1.1",
                categoria="escaneo",
                tags=["ping", "conectividad", "red"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man ping"]
            ),
            Comando(
                nombre="Escaneo de Puertos TCP",
                descripcion="Escanear puertos TCP básicos con netcat",
                comando="nc -zv {target} {port}",
                ejemplo="nc -zv 192.168.1.1 80",
                categoria="escaneo",
                tags=["tcp", "puertos", "netcat"],
                plataforma=["linux"],
                nivel="intermedio",
                peligrosidad="moderado",
                referencias=["man nc"]
            ),
            Comando(
                nombre="Detección de Hosts Activos",
                descripcion="Detectar hosts activos en red local",
                comando="for i in {1..254}; do ping -c 1 -W 1 192.168.1.$i >/dev/null && echo \"192.168.1.$i is up\"; done",
                ejemplo="for i in {1..10}; do ping -c 1 -W 1 192.168.1.$i >/dev/null && echo \"192.168.1.$i is up\"; done",
                categoria="escaneo",
                tags=["discovery", "hosts", "ping-sweep"],
                plataforma=["linux"],
                nivel="intermedio",
                peligrosidad="moderado",
                referencias=["bash manual"]
            ),
            Comando(
                nombre="Información de Interfaz de Red",
                descripcion="Mostrar configuración de interfaces de red",
                comando="ip addr show",
                ejemplo="ip addr show eth0",
                categoria="escaneo",
                tags=["interfaz", "ip", "configuracion"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man ip"]
            ),
            Comando(
                nombre="Tabla de Enrutamiento",
                descripcion="Mostrar tabla de enrutamiento",
                comando="ip route show",
                ejemplo="ip route show",
                categoria="escaneo",
                tags=["routing", "gateway", "red"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man ip"]
            ),
            Comando(
                nombre="Servidores DNS",
                descripcion="Ver configuración DNS",
                comando="cat /etc/resolv.conf",
                ejemplo="cat /etc/resolv.conf",
                categoria="escaneo",
                tags=["dns", "configuracion"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man resolv.conf"]
            )
        ]
        
        cheatsheet = Cheatsheet(
            nombre="Escaneo de Red",
            descripcion="Comandos para escaneo y reconocimiento de red",
            categoria="escaneo",
            autor="Ares Aegis",
            version="1.0",
            fecha_creacion=datetime.now(),
            fecha_modificacion=datetime.now(),
            comandos=comandos,
            metadatos={"prioridad": "alta", "frecuencia_uso": "semanal"}
        )
        
        self.cheatsheets["escaneo-red"] = cheatsheet
    
    def _crear_cheatsheet_analisis_logs(self):
        """Crea cheatsheet de análisis de logs."""
        comandos = [
            Comando(
                nombre="Últimos Logins",
                descripcion="Ver últimos inicios de sesión",
                comando="last -n 20",
                ejemplo="last -n 20",
                categoria="logs",
                tags=["login", "usuarios", "sesiones"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man last"]
            ),
            Comando(
                nombre="Logs de Autenticación",
                descripcion="Revisar logs de autenticación SSH",
                comando="grep 'Failed password' /var/log/auth.log | tail -20",
                ejemplo="grep 'Failed password' /var/log/auth.log | tail -20",
                categoria="logs",
                tags=["ssh", "autenticacion", "fallos"],
                plataforma=["linux"],
                nivel="intermedio",
                peligrosidad="seguro",
                referencias=["man grep"]
            ),
            Comando(
                nombre="IPs con Fallos SSH",
                descripcion="Extraer IPs con intentos fallidos SSH",
                comando="grep 'Failed password' /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -nr",
                ejemplo="grep 'Failed password' /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -nr | head -10",
                categoria="logs",
                tags=["ssh", "ips", "ataques"],
                plataforma=["linux"],
                nivel="avanzado",
                peligrosidad="seguro",
                referencias=["man awk", "man sort"]
            ),
            Comando(
                nombre="Logs del Sistema",
                descripcion="Monitorear logs del sistema en tiempo real",
                comando="tail -f /var/log/syslog",
                ejemplo="tail -f /var/log/syslog | grep -i error",
                categoria="logs",
                tags=["syslog", "tiempo-real", "monitoring"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man tail"]
            ),
            Comando(
                nombre="Logs por Fecha",
                descripcion="Filtrar logs por fecha específica",
                comando="grep '$(date +\"%b %d\")' /var/log/syslog",
                ejemplo="grep 'Dec 15' /var/log/syslog",
                categoria="logs",
                tags=["fecha", "filtrado"],
                plataforma=["linux"],
                nivel="intermedio",
                peligrosidad="seguro",
                referencias=["man date", "man grep"]
            ),
            Comando(
                nombre="Comandos Sudo Ejecutados",
                descripcion="Ver comandos ejecutados con sudo",
                comando="grep 'COMMAND=' /var/log/auth.log",
                ejemplo="grep 'COMMAND=' /var/log/auth.log | tail -10",
                categoria="logs",
                tags=["sudo", "comandos", "privilegios"],
                plataforma=["linux"],
                nivel="intermedio",
                peligrosidad="seguro",
                referencias=["man grep"]
            )
        ]
        
        cheatsheet = Cheatsheet(
            nombre="Análisis de Logs",
            descripcion="Comandos para análisis y monitoreo de logs del sistema",
            categoria="logs",
            autor="Ares Aegis",
            version="1.0",
            fecha_creacion=datetime.now(),
            fecha_modificacion=datetime.now(),
            comandos=comandos,
            metadatos={"prioridad": "alta", "frecuencia_uso": "diaria"}
        )
        
        self.cheatsheets["analisis-logs"] = cheatsheet
    
    def _crear_cheatsheet_forense(self):
        """Crea cheatsheet de análisis forense."""
        comandos = [
            Comando(
                nombre="Hash MD5 de Archivo",
                descripcion="Calcular hash MD5 para verificar integridad",
                comando="md5sum {file}",
                ejemplo="md5sum /bin/bash",
                categoria="forense",
                tags=["hash", "integridad", "md5"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man md5sum"]
            ),
            Comando(
                nombre="Hash SHA256 de Archivo",
                descripcion="Calcular hash SHA256 para verificar integridad",
                comando="sha256sum {file}",
                ejemplo="sha256sum /bin/bash",
                categoria="forense",
                tags=["hash", "integridad", "sha256"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man sha256sum"]
            ),
            Comando(
                nombre="Archivos Modificados Recientemente",
                descripcion="Buscar archivos modificados en las últimas 24 horas",
                comando="find /home -type f -mtime -1 2>/dev/null",
                ejemplo="find /home -type f -mtime -1 2>/dev/null | head -20",
                categoria="forense",
                tags=["archivos", "modificacion", "timeline"],
                plataforma=["linux"],
                nivel="intermedio",
                peligrosidad="seguro",
                referencias=["man find"]
            ),
            Comando(
                nombre="Información Detallada de Archivo",
                descripcion="Obtener metadatos completos de un archivo",
                comando="stat {file}",
                ejemplo="stat /etc/passwd",
                categoria="forense",
                tags=["metadatos", "timestamps", "permisos"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man stat"]
            ),
            Comando(
                nombre="Strings en Binarios",
                descripcion="Extraer strings legibles de archivos binarios",
                comando="strings {file} | head -20",
                ejemplo="strings /bin/ls | head -20",
                categoria="forense",
                tags=["strings", "binarios", "analisis"],
                plataforma=["linux"],
                nivel="intermedio",
                peligrosidad="seguro",
                referencias=["man strings"]
            ),
            Comando(
                nombre="Archivos Abiertos por Proceso",
                descripcion="Listar archivos abiertos por un proceso específico",
                comando="lsof -p {pid}",
                ejemplo="lsof -p 1234",
                categoria="forense",
                tags=["lsof", "archivos", "procesos"],
                plataforma=["linux"],
                nivel="intermedio",
                peligrosidad="seguro",
                referencias=["man lsof"]
            )
        ]
        
        cheatsheet = Cheatsheet(
            nombre="Análisis Forense",
            descripcion="Comandos para análisis forense básico y verificación de integridad",
            categoria="forense",
            autor="Ares Aegis",
            version="1.0",
            fecha_creacion=datetime.now(),
            fecha_modificacion=datetime.now(),
            comandos=comandos,
            metadatos={"prioridad": "media", "frecuencia_uso": "ocasional"}
        )
        
        self.cheatsheets["forense"] = cheatsheet
    
    def _crear_cheatsheet_hardening(self):
        """Crea cheatsheet de hardening del sistema."""
        comandos = [
            Comando(
                nombre="Actualizar Sistema",
                descripcion="Actualizar todos los paquetes del sistema",
                comando="apt update && apt upgrade -y",
                ejemplo="sudo apt update && sudo apt upgrade -y",
                categoria="hardening",
                tags=["actualizacion", "paquetes", "seguridad"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="moderado",
                referencias=["man apt"]
            ),
            Comando(
                nombre="Configurar Firewall UFW",
                descripcion="Habilitar firewall básico con UFW",
                comando="ufw enable",
                ejemplo="sudo ufw enable && sudo ufw status",
                categoria="hardening",
                tags=["firewall", "ufw", "red"],
                plataforma=["linux"],
                nivel="intermedio",
                peligrosidad="moderado",
                referencias=["man ufw"]
            ),
            Comando(
                nombre="Deshabilitar Servicios Innecesarios",
                descripcion="Listar y deshabilitar servicios no esenciales",
                comando="systemctl list-unit-files --type=service --state=enabled",
                ejemplo="systemctl list-unit-files --type=service --state=enabled | grep -v essential",
                categoria="hardening",
                tags=["servicios", "systemd", "reduccion-superficie"],
                plataforma=["linux"],
                nivel="avanzado",
                peligrosidad="peligroso",
                referencias=["man systemctl"]
            ),
            Comando(
                nombre="Configurar SSH Seguro",
                descripcion="Verificar configuración SSH segura",
                comando="grep -E '^(PermitRootLogin|PasswordAuthentication|Port)' /etc/ssh/sshd_config",
                ejemplo="grep -E '^(PermitRootLogin|PasswordAuthentication|Port)' /etc/ssh/sshd_config",
                categoria="hardening",
                tags=["ssh", "configuracion", "acceso-remoto"],
                plataforma=["linux"],
                nivel="intermedio",
                peligrosidad="moderado",
                referencias=["man sshd_config"]
            ),
            Comando(
                nombre="Permisos de Archivos Críticos",
                descripcion="Verificar permisos de archivos sensibles",
                comando="ls -la /etc/passwd /etc/shadow /etc/group",
                ejemplo="ls -la /etc/passwd /etc/shadow /etc/group",
                categoria="hardening",
                tags=["permisos", "archivos-criticos"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="seguro",
                referencias=["man ls"]
            ),
            Comando(
                nombre="Configurar Fail2Ban",
                descripcion="Verificar estado de Fail2Ban",
                comando="fail2ban-client status",
                ejemplo="sudo fail2ban-client status sshd",
                categoria="hardening",
                tags=["fail2ban", "proteccion", "ssh"],
                plataforma=["linux"],
                nivel="intermedio",
                peligrosidad="seguro",
                referencias=["man fail2ban-client"]
            )
        ]
        
        cheatsheet = Cheatsheet(
            nombre="Hardening del Sistema",
            descripcion="Comandos para endurecimiento y configuración segura",
            categoria="hardening",
            autor="Ares Aegis",
            version="1.0",
            fecha_creacion=datetime.now(),
            fecha_modificacion=datetime.now(),
            comandos=comandos,
            metadatos={"prioridad": "alta", "frecuencia_uso": "mensual"}
        )
        
        self.cheatsheets["hardening"] = cheatsheet
    
    def _crear_cheatsheet_respuesta_incidentes(self):
        """Crea cheatsheet de respuesta a incidentes."""
        comandos = [
            Comando(
                nombre="Terminar Proceso Sospechoso",
                descripcion="Terminar un proceso por PID",
                comando="kill -TERM {pid}",
                ejemplo="kill -TERM 1234",
                categoria="respuesta",
                tags=["proceso", "terminacion", "incidente"],
                plataforma=["linux"],
                nivel="intermedio",
                peligrosidad="peligroso",
                referencias=["man kill"]
            ),
            Comando(
                nombre="Bloquear IP con iptables",
                descripcion="Bloquear una IP específica",
                comando="iptables -A INPUT -s {ip} -j DROP",
                ejemplo="sudo iptables -A INPUT -s 192.168.1.100 -j DROP",
                categoria="respuesta",
                tags=["iptables", "bloqueo", "ip"],
                plataforma=["linux"],
                nivel="avanzado",
                peligrosidad="peligroso",
                referencias=["man iptables"]
            ),
            Comando(
                nombre="Aislar Archivo Sospechoso",
                descripcion="Mover archivo a cuarentena",
                comando="mv {file} /tmp/cuarentena/",
                ejemplo="sudo mv /home/user/suspicious.bin /tmp/cuarentena/",
                categoria="respuesta",
                tags=["cuarentena", "archivo", "aislamiento"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="moderado",
                referencias=["man mv"]
            ),
            Comando(
                nombre="Desconectar Interfaz de Red",
                descripcion="Deshabilitar interfaz de red para contención",
                comando="ip link set {interface} down",
                ejemplo="sudo ip link set eth0 down",
                categoria="respuesta",
                tags=["red", "aislamiento", "contencion"],
                plataforma=["linux"],
                nivel="avanzado",
                peligrosidad="peligroso",
                referencias=["man ip"]
            ),
            Comando(
                nombre="Crear Snapshot de Memoria",
                descripcion="Crear dump de memoria para análisis",
                comando="dd if=/dev/mem of=/tmp/memory_dump.bin",
                ejemplo="sudo dd if=/dev/mem of=/tmp/memory_dump.bin count=1000",
                categoria="respuesta",
                tags=["memoria", "dump", "forense"],
                plataforma=["linux"],
                nivel="avanzado",
                peligrosidad="moderado",
                referencias=["man dd"]
            ),
            Comando(
                nombre="Cambiar Contraseña de Emergencia",
                descripcion="Cambiar contraseña de usuario comprometido",
                comando="passwd {usuario}",
                ejemplo="sudo passwd compromised_user",
                categoria="respuesta",
                tags=["password", "usuario", "compromiso"],
                plataforma=["linux"],
                nivel="basico",
                peligrosidad="moderado",
                referencias=["man passwd"]
            )
        ]
        
        cheatsheet = Cheatsheet(
            nombre="Respuesta a Incidentes",
            descripcion="Comandos de emergencia para respuesta rápida a incidentes",
            categoria="respuesta",
            autor="Ares Aegis",
            version="1.0",
            fecha_creacion=datetime.now(),
            fecha_modificacion=datetime.now(),
            comandos=comandos,
            metadatos={"prioridad": "critica", "frecuencia_uso": "emergencia"}
        )
        
        self.cheatsheets["respuesta-incidentes"] = cheatsheet
    
    def _cargar_indice(self):
        """Carga el índice de cheatsheets desde archivo."""
        try:
            with open(self.archivo_indice, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for sheet_id, sheet_data in data.get('cheatsheets', {}).items():
                comandos = []
                for cmd_data in sheet_data.get('comandos', []):
                    comando = Comando(
                        nombre=cmd_data['nombre'],
                        descripcion=cmd_data['descripcion'],
                        comando=cmd_data['comando'],
                        ejemplo=cmd_data['ejemplo'],
                        categoria=cmd_data['categoria'],
                        tags=cmd_data['tags'],
                        plataforma=cmd_data['plataforma'],
                        nivel=cmd_data['nivel'],
                        peligrosidad=cmd_data['peligrosidad'],
                        referencias=cmd_data['referencias']
                    )
                    comandos.append(comando)
                
                cheatsheet = Cheatsheet(
                    nombre=sheet_data['nombre'],
                    descripcion=sheet_data['descripcion'],
                    categoria=sheet_data['categoria'],
                    autor=sheet_data['autor'],
                    version=sheet_data['version'],
                    fecha_creacion=datetime.fromisoformat(sheet_data['fecha_creacion']),
                    fecha_modificacion=datetime.fromisoformat(sheet_data['fecha_modificacion']),
                    comandos=comandos,
                    metadatos=sheet_data.get('metadatos', {})
                )
                
                self.cheatsheets[sheet_id] = cheatsheet
            
            self._construir_indice_comandos()
            
        except Exception as e:
            self.logger.error(f"Error cargando índice: {e}")
    
    def _guardar_indice(self):
        """Guarda el índice de cheatsheets en archivo."""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'cheatsheets': {}
            }
            
            for sheet_id, cheatsheet in self.cheatsheets.items():
                comandos_data = []
                for comando in cheatsheet.comandos:
                    comandos_data.append({
                        'nombre': comando.nombre,
                        'descripcion': comando.descripcion,
                        'comando': comando.comando,
                        'ejemplo': comando.ejemplo,
                        'categoria': comando.categoria,
                        'tags': comando.tags,
                        'plataforma': comando.plataforma,
                        'nivel': comando.nivel,
                        'peligrosidad': comando.peligrosidad,
                        'referencias': comando.referencias
                    })
                
                data['cheatsheets'][sheet_id] = {
                    'nombre': cheatsheet.nombre,
                    'descripcion': cheatsheet.descripcion,
                    'categoria': cheatsheet.categoria,
                    'autor': cheatsheet.autor,
                    'version': cheatsheet.version,
                    'fecha_creacion': cheatsheet.fecha_creacion.isoformat(),
                    'fecha_modificacion': cheatsheet.fecha_modificacion.isoformat(),
                    'comandos': comandos_data,
                    'metadatos': cheatsheet.metadatos
                }
            
            with open(self.archivo_indice, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Error guardando índice: {e}")
    
    def _construir_indice_comandos(self):
        """Construye el índice de comandos por tags."""
        self.indice_comandos.clear()
        self.categorias.clear()
        
        for sheet_id, cheatsheet in self.cheatsheets.items():
            self.categorias.add(cheatsheet.categoria)
            
            for comando in cheatsheet.comandos:
                for tag in comando.tags:
                    if tag not in self.indice_comandos:
                        self.indice_comandos[tag] = []
                    self.indice_comandos[tag].append(sheet_id)
    
    def buscar_comandos(self, termino: str, categoria: Optional[str] = None, 
                       nivel: Optional[str] = None) -> List[Comando]:
        """
        Busca comandos por término, categoría y/o nivel.
        
        Args:
            termino: Término a buscar en nombre, descripción o tags
            categoria: Filtrar por categoría específica
            nivel: Filtrar por nivel (basico, intermedio, avanzado)
            
        Returns:
            Lista de comandos que coinciden con los criterios
        """
        comandos_encontrados = []
        termino_lower = termino.lower()
        
        for cheatsheet in self.cheatsheets.values():
            # Filtrar por categoría si se especifica
            if categoria and cheatsheet.categoria != categoria:
                continue
            
            for comando in cheatsheet.comandos:
                # Filtrar por nivel si se especifica
                if nivel and comando.nivel != nivel:
                    continue
                
                # Buscar término en nombre, descripción o tags
                if (termino_lower in comando.nombre.lower() or
                    termino_lower in comando.descripcion.lower() or
                    any(termino_lower in tag.lower() for tag in comando.tags)):
                    comandos_encontrados.append(comando)
        
        return comandos_encontrados
    
    def obtener_cheatsheet(self, sheet_id: str) -> Optional[Cheatsheet]:
        """
        Obtiene una cheatsheet específica por ID.
        
        Args:
            sheet_id: ID de la cheatsheet
            
        Returns:
            Cheatsheet o None si no se encuentra
        """
        return self.cheatsheets.get(sheet_id)
    
    def listar_categorias(self) -> List[str]:
        """Lista todas las categorías disponibles."""
        return sorted(list(self.categorias))
    
    def listar_cheatsheets(self) -> List[Dict[str, Any]]:
        """Lista todas las cheatsheets disponibles."""
        return [
            {
                'id': sheet_id,
                'nombre': sheet.nombre,
                'descripcion': sheet.descripcion,
                'categoria': sheet.categoria,
                'comandos_count': len(sheet.comandos),
                'fecha_modificacion': sheet.fecha_modificacion.isoformat()
            }
            for sheet_id, sheet in self.cheatsheets.items()
        ]
    
    def obtener_comandos_por_categoria(self, categoria: str) -> List[Comando]:
        """Obtiene todos los comandos de una categoría específica."""
        comandos = []
        
        for cheatsheet in self.cheatsheets.values():
            if cheatsheet.categoria == categoria:
                comandos.extend(cheatsheet.comandos)
        
        return comandos
    
    def obtener_comandos_por_tag(self, tag: str) -> List[Comando]:
        """Obtiene todos los comandos que tienen un tag específico."""
        comandos = []
        
        for cheatsheet in self.cheatsheets.values():
            for comando in cheatsheet.comandos:
                if tag.lower() in [t.lower() for t in comando.tags]:
                    comandos.append(comando)
        
        return comandos
    
    def generar_reporte_cheatsheets(self) -> str:
        """Genera un reporte completo de cheatsheets en formato Markdown."""
        md = "# 📚 Compendio de los Escribanos de Hermes\n\n"
        md += f"**Total de Cheatsheets:** {len(self.cheatsheets)}\n"
        md += f"**Categorías Disponibles:** {len(self.categorias)}\n"
        md += f"**Total de Comandos:** {sum(len(sheet.comandos) for sheet in self.cheatsheets.values())}\n"
        md += f"**Fecha de Reporte:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Índice de categorías
        md += "## 📖 Categorías Disponibles\n\n"
        for categoria in sorted(self.categorias):
            sheets_categoria = [s for s in self.cheatsheets.values() if s.categoria == categoria]
            total_comandos = sum(len(s.comandos) for s in sheets_categoria)
            descripcion = self.categorias_predefinidas.get(categoria, "Sin descripción")
            md += f"- **{categoria}** ({total_comandos} comandos): {descripcion}\n"
        md += "\n"
        
        # Cheatsheets por categoría
        for categoria in sorted(self.categorias):
            md += f"## 🔧 {categoria.title()}\n\n"
            
            sheets_categoria = [s for s in self.cheatsheets.values() if s.categoria == categoria]
            
            for sheet in sheets_categoria:
                md += f"### {sheet.nombre}\n\n"
                md += f"**Descripción:** {sheet.descripcion}\n"
                md += f"**Comandos:** {len(sheet.comandos)}\n"
                md += f"**Última Modificación:** {sheet.fecha_modificacion.strftime('%Y-%m-%d')}\n\n"
                
                # Comandos de la cheatsheet
                md += "| Comando | Descripción | Nivel | Peligrosidad |\n"
                md += "|---------|-------------|-------|-------------|\n"
                
                for comando in sheet.comandos[:10]:  # Top 10 comandos
                    emoji_nivel = {"basico": "🟢", "intermedio": "🟡", "avanzado": "🔴"}.get(comando.nivel, "⚪")
                    emoji_peligro = {"seguro": "✅", "moderado": "⚠️", "peligroso": "🚨"}.get(comando.peligrosidad, "❓")
                    
                    nombre_corto = comando.nombre[:30] + "..." if len(comando.nombre) > 30 else comando.nombre
                    desc_corta = comando.descripcion[:50] + "..." if len(comando.descripcion) > 50 else comando.descripcion
                    
                    md += f"| {nombre_corto} | {desc_corta} | {emoji_nivel} {comando.nivel} | {emoji_peligro} {comando.peligrosidad} |\n"
                
                if len(sheet.comandos) > 10:
                    md += f"| ... | ... | ... | ... |\n"
                    md += f"| **Total:** {len(sheet.comandos)} comandos | | | |\n"
                
                md += "\n"
        
        # Comandos más útiles
        md += "## ⭐ Comandos Esenciales\n\n"
        md += "### Reconocimiento Básico\n\n"
        comandos_basicos = self.buscar_comandos("", nivel="basico")[:10]
        
        for comando in comandos_basicos:
            md += f"**{comando.nombre}:**\n"
            md += f"```bash\n{comando.ejemplo}\n```\n"
            md += f"*{comando.descripcion}*\n\n"
        
        md += "---\n"
        md += "*Compendio organizado por los Escribanos de Hermes de Ares Aegis*\n"
        
        return md
    
    def exportar_cheatsheet_markdown(self, sheet_id: str) -> str:
        """Exporta una cheatsheet específica en formato Markdown."""
        cheatsheet = self.obtener_cheatsheet(sheet_id)
        if not cheatsheet:
            return "# Cheatsheet No Encontrada\n\nLa cheatsheet solicitada no existe."
        
        md = f"# {cheatsheet.nombre}\n\n"
        md += f"**Descripción:** {cheatsheet.descripcion}\n"
        md += f"**Categoría:** {cheatsheet.categoria}\n"
        md += f"**Autor:** {cheatsheet.autor}\n"
        md += f"**Versión:** {cheatsheet.version}\n"
        md += f"**Última Modificación:** {cheatsheet.fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += f"**Total de Comandos:** {len(cheatsheet.comandos)}\n\n"
        
        # Agrupar comandos por nivel
        comandos_por_nivel = {}
        for comando in cheatsheet.comandos:
            nivel = comando.nivel
            if nivel not in comandos_por_nivel:
                comandos_por_nivel[nivel] = []
            comandos_por_nivel[nivel].append(comando)
        
        # Mostrar comandos por nivel
        orden_niveles = ["basico", "intermedio", "avanzado"]
        
        for nivel in orden_niveles:
            if nivel in comandos_por_nivel:
                emoji_nivel = {"basico": "🟢", "intermedio": "🟡", "avanzado": "🔴"}.get(nivel, "⚪")
                md += f"## {emoji_nivel} Nivel {nivel.title()}\n\n"
                
                for comando in comandos_por_nivel[nivel]:
                    emoji_peligro = {"seguro": "✅", "moderado": "⚠️", "peligroso": "🚨"}.get(comando.peligrosidad, "❓")
                    
                    md += f"### {comando.nombre} {emoji_peligro}\n\n"
                    md += f"**Descripción:** {comando.descripcion}\n\n"
                    md += f"**Comando:**\n"
                    md += f"```bash\n{comando.comando}\n```\n\n"
                    md += f"**Ejemplo:**\n"
                    md += f"```bash\n{comando.ejemplo}\n```\n\n"
                    
                    if comando.tags:
                        md += f"**Tags:** {', '.join(comando.tags)}\n\n"
                    
                    if comando.plataforma:
                        md += f"**Plataforma:** {', '.join(comando.plataforma)}\n\n"
                    
                    if comando.referencias:
                        md += f"**Referencias:** {', '.join(comando.referencias)}\n\n"
                    
                    md += "---\n\n"
        
        return md
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del gestor de cheatsheets."""
        total_comandos = sum(len(sheet.comandos) for sheet in self.cheatsheets.values())
        
        # Contar por nivel
        conteo_nivel = {"basico": 0, "intermedio": 0, "avanzado": 0}
        conteo_peligrosidad = {"seguro": 0, "moderado": 0, "peligroso": 0}
        
        for cheatsheet in self.cheatsheets.values():
            for comando in cheatsheet.comandos:
                conteo_nivel[comando.nivel] += 1
                conteo_peligrosidad[comando.peligrosidad] += 1
        
        return {
            'total_cheatsheets': len(self.cheatsheets),
            'total_comandos': total_comandos,
            'total_categorias': len(self.categorias),
            'conteo_por_nivel': conteo_nivel,
            'conteo_por_peligrosidad': conteo_peligrosidad,
            'tags_disponibles': len(self.indice_comandos),
            'ultima_actualizacion': datetime.now().isoformat()
        }
