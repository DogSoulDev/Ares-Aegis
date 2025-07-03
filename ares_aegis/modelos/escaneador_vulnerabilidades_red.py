#!/usr/bin/env python3
"""
Escaneador de Vulnerabilidades de Red - Ares Aegis
Módulo para escaneo de vulnerabilidades de red y análisis de puertos

Los mensajes de este módulo siguen el estilo mitológico inspirado en Ares y la Égida.

Autor: DogSoulDev
Versión: 2.0.0 - El Explorador de los Senderos Etéreos
"""

import socket
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from ..utilidades.ayuda_logging import configurar_logger_modulo


class ExploradorPuertos:
    """El Explorador de Puertas - Examina las entradas y salidas del reino digital."""
    
    def __init__(self):
        """Inicializa el explorador de las puertas etéreas."""
        self.logger = configurar_logger_modulo("explorador_puertos")
        
        # Puertos comunes y su significado divino
        self.puertos_conocidos = {
            21: "FTP - El heraldo de archivos antiguos",
            22: "SSH - El guardián de la conexión segura", 
            23: "Telnet - El mensajero desnudo y vulnerable",
            25: "SMTP - El portador de cartas digitales",
            53: "DNS - El oráculo de los nombres",
            80: "HTTP - El pregonero de la web",
            110: "POP3 - El recolector de mensajes",
            143: "IMAP - El organizador de correspondencia",
            443: "HTTPS - El mensajero con sello de encriptación",
            993: "IMAPS - El recolector protegido",
            995: "POP3S - El recolector con escudo",
            3306: "MySQL - El guardián de bases de datos",
            5432: "PostgreSQL - El oráculo de tablas",
            6379: "Redis - El guardián de memoria rápida",
            1433: "MSSQL - El custodio de Microsoft",
            3389: "RDP - La puerta remota de Windows",
            5900: "VNC - El ojo remoto",
            8080: "HTTP-Alt - El pregonero alternativo",
            8443: "HTTPS-Alt - El mensajero alternativo seguro"
        }
        
        self.logger.info("El explorador de puertas ha abierto su mapa de los senderos etéreos")
    
    def escanear_puerto(self, host: str, puerto: int, timeout: int = 3) -> Dict[str, Any]:
        """
        Examina una puerta específica del reino digital.
        
        Args:
            host: Dirección del reino a examinar
            puerto: Número de la puerta a explorar
            timeout: Tiempo de espera divino
            
        Returns:
            Dict con información sobre el estado de la puerta
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                resultado = sock.connect_ex((host, puerto))
                
                if resultado == 0:
                    # Puerto abierto
                    servicio = self.puertos_conocidos.get(puerto, "Guardián desconocido")
                    return {
                        'puerto': puerto,
                        'estado': 'ABIERTO',
                        'host': host,
                        'servicio': servicio,
                        'mensaje': f"La puerta {puerto} está abierta - {servicio}",
                        'nivel_riesgo': self._evaluar_riesgo_puerto(puerto)
                    }
                else:
                    return {
                        'puerto': puerto,
                        'estado': 'CERRADO',
                        'host': host,
                        'mensaje': f"La puerta {puerto} permanece sellada"
                    }
        
        except socket.timeout:
            return {
                'puerto': puerto,
                'estado': 'TIMEOUT',
                'host': host,
                'mensaje': f"La puerta {puerto} no responde a los llamados divinos"
            }
        
        except Exception as e:
            return {
                'puerto': puerto,
                'estado': 'ERROR',
                'host': host,
                'mensaje': f"Una tormenta impide examinar la puerta {puerto}: {e}"
            }
    
    def escanear_rango_puertos(self, host: str, puertos: List[int], max_hilos: int = 50) -> List[Dict[str, Any]]:
        """
        Examina múltiples puertas del reino usando exploradores paralelos.
        
        Args:
            host: Dirección del reino a examinar
            puertos: Lista de puertas a explorar
            max_hilos: Número máximo de exploradores simultáneos
            
        Returns:
            Lista con resultados de cada puerta examinada
        """
        resultados = []
        
        self.logger.info(f"Iniciando exploración de {len(puertos)} puertas en {host}")
        
        with ThreadPoolExecutor(max_workers=max_hilos) as executor:
            # Enviar tareas a los exploradores
            futuros = {
                executor.submit(self.escanear_puerto, host, puerto): puerto 
                for puerto in puertos
            }
            
            # Recoger resultados conforme se completan
            for futuro in as_completed(futuros):
                try:
                    resultado = futuro.result(timeout=10)
                    resultados.append(resultado)
                except Exception as e:
                    puerto = futuros[futuro]
                    resultados.append({
                        'puerto': puerto,
                        'estado': 'ERROR',
                        'host': host,
                        'mensaje': f"El explorador falló examinando la puerta {puerto}: {e}"
                    })
        
        # Ordenar resultados por número de puerto
        resultados.sort(key=lambda x: x['puerto'])
        
        self.logger.info(f"Exploración completada en {host}: {len(resultados)} puertas examinadas")
        return resultados
    
    def escaneo_rapido_puertos_comunes(self, host: str) -> Dict[str, Any]:
        """
        Realiza un escaneo rápido de puertas comúnmente conocidas.
        
        Args:
            host: Dirección del reino a examinar
            
        Returns:
            Dict con resultados del escaneo rápido
        """
        puertos_comunes = list(self.puertos_conocidos.keys())
        
        inicio_tiempo = time.time()
        resultados = self.escanear_rango_puertos(host, puertos_comunes)
        tiempo_total = time.time() - inicio_tiempo
        
        # Analizar resultados
        puertas_abiertas = [r for r in resultados if r['estado'] == 'ABIERTO']
        puertas_riesgosas = [r for r in puertas_abiertas if r.get('nivel_riesgo') in ['ALTO', 'CRITICO']]
        
        return {
            'host': host,
            'tiempo_escaneo': round(tiempo_total, 2),
            'puertas_examinadas': len(resultados),
            'puertas_abiertas': len(puertas_abiertas),
            'puertas_riesgosas': len(puertas_riesgosas),
            'detalles_puertas': resultados,
            'puertas_alto_riesgo': puertas_riesgosas,
            'mensaje_resumen': self._generar_mensaje_resumen(len(puertas_abiertas), len(puertas_riesgosas))
        }
    
    def _evaluar_riesgo_puerto(self, puerto: int) -> str:
        """Evalúa el nivel de riesgo de un puerto específico."""
        puertos_criticos = [23, 21, 512, 513, 514]  # Telnet, FTP, rsh services
        puertos_alto_riesgo = [3389, 5900, 1433, 3306, 6379]  # RDP, VNC, Databases
        puertos_medio_riesgo = [22, 25, 110, 143, 993, 995]  # SSH, Mail services
        
        if puerto in puertos_criticos:
            return 'CRITICO'
        elif puerto in puertos_alto_riesgo:
            return 'ALTO'
        elif puerto in puertos_medio_riesgo:
            return 'MEDIO'
        else:
            return 'BAJO'
    
    def _generar_mensaje_resumen(self, puertas_abiertas: int, puertas_riesgosas: int) -> str:
        """Genera mensaje resumen del escaneo."""
        if puertas_riesgosas > 3:
            return f"¡PELIGRO! {puertas_abiertas} puertas abiertas, {puertas_riesgosas} con alto riesgo - el reino está expuesto"
        elif puertas_riesgosas > 0:
            return f"PRECAUCIÓN: {puertas_abiertas} puertas abiertas, {puertas_riesgosas} requieren atención divina"
        elif puertas_abiertas > 10:
            return f"El reino tiene {puertas_abiertas} puertas abiertas - considera cerrar las innecesarias"
        else:
            return f"El reino está bien protegido: {puertas_abiertas} puertas abiertas sin riesgos graves"


class DetectorVulnerabilidadesRed:
    """El Detector de Grietas en los Senderos - Identifica debilidades en la red."""
    
    def __init__(self):
        """Inicializa el detector de grietas en los senderos etéreos."""
        self.logger = configurar_logger_modulo("detector_vulnerabilidades_red")
        self.explorador_puertos = ExploradorPuertos()
        
        # Configuraciones inseguras conocidas
        self.vulnerabilidades_conocidas = {
            'telnet_abierto': {
                'puertos': [23],
                'nivel': 'CRITICO',
                'descripcion': 'Telnet transmite credenciales sin protección divina',
                'recomendacion': 'Desactivar Telnet y usar SSH con la bendición de la encriptación'
            },
            'ftp_abierto': {
                'puertos': [21],
                'nivel': 'ALTO',
                'descripcion': 'FTP puede exponer credenciales a miradas impías',
                'recomendacion': 'Usar SFTP o FTPS con protección encriptada'
            },
            'servicios_r_abiertos': {
                'puertos': [512, 513, 514],
                'nivel': 'CRITICO',
                'descripcion': 'Servicios R (rsh, rlogin, rexec) son peligrosamente vulnerables',
                'recomendacion': 'Eliminar servicios R y usar SSH exclusivamente'
            },
            'bases_datos_expuestas': {
                'puertos': [3306, 5432, 1433, 6379, 27017],
                'nivel': 'ALTO',
                'descripcion': 'Bases de datos accesibles externamente',
                'recomendacion': 'Configurar firewall para acceso solo desde redes confiables'
            },
            'acceso_remoto_expuesto': {
                'puertos': [3389, 5900],
                'nivel': 'ALTO',
                'descripcion': 'Servicios de acceso remoto expuestos',
                'recomendacion': 'Usar VPN o limitar acceso por IP'
            }
        }
        
        self.logger.info("El detector de grietas en los senderos ha calibrado sus sensores divinos")
    
    def analizar_vulnerabilidades_host(self, host: str) -> Dict[str, Any]:
        """
        Analiza vulnerabilidades específicas de un host.
        
        Args:
            host: Dirección del host a analizar
            
        Returns:
            Dict con análisis de vulnerabilidades
        """
        self.logger.info(f"Iniciando análisis de vulnerabilidades para {host}")
        
        # Realizar escaneo de puertos
        escaneo_resultado = self.explorador_puertos.escaneo_rapido_puertos_comunes(host)
        puertas_abiertas = [p for p in escaneo_resultado['detalles_puertas'] if p['estado'] == 'ABIERTO']
        
        # Detectar vulnerabilidades específicas
        vulnerabilidades_detectadas = []
        
        for vuln_id, vuln_info in self.vulnerabilidades_conocidas.items():
            puertos_vulnerables = []
            
            for puerto_info in puertas_abiertas:
                if puerto_info['puerto'] in vuln_info['puertos']:
                    puertos_vulnerables.append(puerto_info['puerto'])
            
            if puertos_vulnerables:
                vulnerabilidades_detectadas.append({
                    'id': vuln_id,
                    'nivel': vuln_info['nivel'],
                    'descripcion': vuln_info['descripcion'],
                    'recomendacion': vuln_info['recomendacion'],
                    'puertos_afectados': puertos_vulnerables,
                    'mensaje': f"Vulnerabilidad detectada: {vuln_info['descripcion']}"
                })
        
        # Analizar configuraciones adicionales
        config_inseguras = self._analizar_configuraciones_red(host, puertas_abiertas)
        
        # Evaluar riesgo general
        nivel_riesgo_general = self._evaluar_riesgo_general(vulnerabilidades_detectadas, config_inseguras)
        
        return {
            'host': host,
            'timestamp': datetime.now().isoformat(),
            'escaneo_puertos': escaneo_resultado,
            'vulnerabilidades_detectadas': len(vulnerabilidades_detectadas),
            'configuraciones_inseguras': len(config_inseguras),
            'nivel_riesgo_general': nivel_riesgo_general,
            'detalles_vulnerabilidades': vulnerabilidades_detectadas,
            'configuraciones_problematicas': config_inseguras,
            'mensaje_general': self._generar_mensaje_general(len(vulnerabilidades_detectadas), nivel_riesgo_general),
            'recomendaciones_prioritarias': self._generar_recomendaciones_prioritarias(vulnerabilidades_detectadas)
        }
    
    def _analizar_configuraciones_red(self, host: str, puertas_abiertas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analiza configuraciones de red potencialmente inseguras."""
        configuraciones_problematicas = []
        
        # Verificar demasiados puertos abiertos
        if len(puertas_abiertas) > 15:
            configuraciones_problematicas.append({
                'tipo': 'demasiados_puertos',
                'nivel': 'MEDIO',
                'descripcion': f"El reino tiene {len(puertas_abiertas)} puertas abiertas - superficie de ataque amplia",
                'recomendacion': 'Cerrar puertos innecesarios para reducir la superficie de ataque'
            })
        
        # Verificar puertos en rangos peligrosos
        puertos_altos = [p['puerto'] for p in puertas_abiertas if p['puerto'] > 10000]
        if len(puertos_altos) > 5:
            configuraciones_problematicas.append({
                'tipo': 'puertos_altos_sospechosos',
                'nivel': 'MEDIO',
                'descripcion': f"Múltiples puertos altos abiertos: {puertos_altos[:5]}...",
                'recomendacion': 'Verificar la legitimidad de servicios en puertos altos'
            })
        
        # Verificar combinaciones peligrosas
        puertos_numeros = [p['puerto'] for p in puertas_abiertas]
        
        if 22 in puertos_numeros and 23 in puertos_numeros:
            configuraciones_problematicas.append({
                'tipo': 'ssh_telnet_simultaneo',
                'nivel': 'ALTO',
                'descripcion': 'SSH y Telnet activos simultáneamente',
                'recomendacion': 'Desactivar Telnet y usar solo SSH para acceso remoto'
            })
        
        if any(p in puertos_numeros for p in [3306, 5432, 1433]) and 22 not in puertos_numeros:
            configuraciones_problematicas.append({
                'tipo': 'base_datos_sin_ssh',
                'nivel': 'ALTO',
                'descripcion': 'Base de datos expuesta sin túnel SSH disponible',
                'recomendacion': 'Configurar SSH para crear túneles seguros hacia la base de datos'
            })
        
        return configuraciones_problematicas
    
    def _evaluar_riesgo_general(self, vulnerabilidades: List[Dict[str, Any]], configuraciones: List[Dict[str, Any]]) -> str:
        """Evalúa el nivel de riesgo general del host."""
        puntuacion_riesgo = 0
        
        # Puntuar vulnerabilidades
        for vuln in vulnerabilidades:
            if vuln['nivel'] == 'CRITICO':
                puntuacion_riesgo += 10
            elif vuln['nivel'] == 'ALTO':
                puntuacion_riesgo += 6
            elif vuln['nivel'] == 'MEDIO':
                puntuacion_riesgo += 3
            else:
                puntuacion_riesgo += 1
        
        # Puntuar configuraciones
        for config in configuraciones:
            if config['nivel'] == 'ALTO':
                puntuacion_riesgo += 4
            elif config['nivel'] == 'MEDIO':
                puntuacion_riesgo += 2
            else:
                puntuacion_riesgo += 1
        
        # Determinar nivel
        if puntuacion_riesgo >= 20:
            return 'CRITICO'
        elif puntuacion_riesgo >= 12:
            return 'ALTO'
        elif puntuacion_riesgo >= 6:
            return 'MEDIO'
        else:
            return 'BAJO'
    
    def _generar_mensaje_general(self, num_vulnerabilidades: int, nivel_riesgo: str) -> str:
        """Genera mensaje general sobre el estado de seguridad."""
        mensajes = {
            'CRITICO': f"¡ALERTA MÁXIMA! {num_vulnerabilidades} vulnerabilidades críticas comprometen gravemente el reino",
            'ALTO': f"¡PELIGRO! {num_vulnerabilidades} vulnerabilidades requieren acción inmediata",
            'MEDIO': f"PRECAUCIÓN: {num_vulnerabilidades} vulnerabilidades requieren atención",
            'BAJO': f"El reino está relativamente seguro con {num_vulnerabilidades} problemas menores"
        }
        
        return mensajes.get(nivel_riesgo, f"Estado desconocido: {num_vulnerabilidades} vulnerabilidades")
    
    def _generar_recomendaciones_prioritarias(self, vulnerabilidades: List[Dict[str, Any]]) -> List[str]:
        """Genera lista de recomendaciones prioritarias."""
        recomendaciones = []
        
        # Ordenar vulnerabilidades por prioridad
        vulnerabilidades_ordenadas = sorted(
            vulnerabilidades, 
            key=lambda x: {'CRITICO': 4, 'ALTO': 3, 'MEDIO': 2, 'BAJO': 1}.get(x['nivel'], 0),
            reverse=True
        )
        
        for vuln in vulnerabilidades_ordenadas[:5]:  # Top 5 prioritarias
            recomendaciones.append(f"[{vuln['nivel']}] {vuln['recomendacion']}")
        
        return recomendaciones
    
    def escanear_red_local(self, red_cidr: str = "192.168.1.0/24") -> Dict[str, Any]:
        """
        Escanea una red local completa buscando hosts y vulnerabilidades.
        
        Args:
            red_cidr: Red en formato CIDR a escanear
            
        Returns:
            Dict con resultados del escaneo de red
        """
        self.logger.info(f"Iniciando escaneo de red local: {red_cidr}")
        
        # Descubrir hosts activos primero
        hosts_activos = self._descubrir_hosts_activos(red_cidr)
        
        # Analizar cada host activo
        resultados_hosts = []
        
        for host in hosts_activos:
            try:
                analisis_host = self.analizar_vulnerabilidades_host(host)
                resultados_hosts.append(analisis_host)
            except Exception as e:
                self.logger.error(f"Error analizando host {host}: {e}")
                resultados_hosts.append({
                    'host': host,
                    'error': True,
                    'mensaje': f"Error en análisis: {e}"
                })
        
        # Generar resumen de red
        hosts_con_vulnerabilidades = [h for h in resultados_hosts if h.get('vulnerabilidades_detectadas', 0) > 0]
        hosts_alto_riesgo = [h for h in resultados_hosts if h.get('nivel_riesgo_general') in ['ALTO', 'CRITICO']]
        
        return {
            'red_escaneada': red_cidr,
            'timestamp': datetime.now().isoformat(),
            'hosts_descubiertos': len(hosts_activos),
            'hosts_analizados': len(resultados_hosts),
            'hosts_con_vulnerabilidades': len(hosts_con_vulnerabilidades),
            'hosts_alto_riesgo': len(hosts_alto_riesgo),
            'detalles_hosts': resultados_hosts,
            'hosts_problematicos': hosts_alto_riesgo,
            'mensaje_resumen': self._generar_mensaje_resumen_red(len(hosts_activos), len(hosts_con_vulnerabilidades), len(hosts_alto_riesgo))
        }
    
    def _descubrir_hosts_activos(self, red_cidr: str) -> List[str]:
        """Descubre hosts activos en una red usando ping."""
        hosts_activos = []
        
        try:
            # Usar nmap si está disponible para descubrimiento rápido
            resultado_nmap = subprocess.run(
                ['nmap', '-sn', red_cidr],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if resultado_nmap.returncode == 0:
                lineas = resultado_nmap.stdout.split('\n')
                for linea in lineas:
                    if 'Nmap scan report for' in linea:
                        # Extraer IP
                        partes = linea.split()
                        if len(partes) >= 5:
                            ip = partes[4].strip('()')
                            hosts_activos.append(ip)
            else:
                # Fallback: ping manual a algunos hosts comunes
                self.logger.warning("nmap no disponible, usando método alternativo")
                base_ip = red_cidr.split('/')[0].rsplit('.', 1)[0]
                
                for i in range(1, 255):
                    ip = f"{base_ip}.{i}"
                    try:
                        resultado_ping = subprocess.run(
                            ['ping', '-c', '1', '-W', '1', ip],
                            capture_output=True,
                            timeout=2
                        )
                        
                        if resultado_ping.returncode == 0:
                            hosts_activos.append(ip)
                    except:
                        continue
        
        except Exception as e:
            self.logger.error(f"Error en descubrimiento de hosts: {e}")
        
        self.logger.info(f"Descubiertos {len(hosts_activos)} hosts activos en {red_cidr}")
        return hosts_activos
    
    def _generar_mensaje_resumen_red(self, hosts_totales: int, hosts_vulnerables: int, hosts_alto_riesgo: int) -> str:
        """Genera mensaje resumen del escaneo de red."""
        if hosts_alto_riesgo > 0:
            return f"¡REINO EN PELIGRO! {hosts_alto_riesgo} de {hosts_totales} hosts presentan riesgo alto o crítico"
        elif hosts_vulnerables > hosts_totales // 2:
            return f"MÚLTIPLES VULNERABILIDADES: {hosts_vulnerables} de {hosts_totales} hosts requieren atención"
        elif hosts_vulnerables > 0:
            return f"ALGUNAS DEBILIDADES: {hosts_vulnerables} de {hosts_totales} hosts tienen vulnerabilidades menores"
        else:
            return f"RED SEGURA: {hosts_totales} hosts escaneados sin vulnerabilidades críticas"


class EscaneadorVulnerabilidadesRed:
    """Orquestador principal para escaneo de vulnerabilidades de red."""
    
    def __init__(self):
        """Inicializa el orquestador de escaneo de vulnerabilidades de red."""
        self.logger = configurar_logger_modulo("escaneador_vulnerabilidades_red")
        self.detector = DetectorVulnerabilidadesRed()
        
        self.logger.info("El orquestador de vulnerabilidades de red ha despertado en el templo digital")
    
    def escaneo_completo_red(self, targets: List[str] = None) -> Dict[str, Any]:
        """
        Realiza un escaneo completo de vulnerabilidades de red.
        
        Args:
            targets: Lista de hosts/redes a escanear. Si None, escanea la red local
            
        Returns:
            Dict con resultados completos del escaneo
        """
        if targets is None:
            targets = ["192.168.1.0/24", "127.0.0.1"]
        
        self.logger.info(f"Iniciando escaneo completo de {len(targets)} objetivos")
        
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'targets_escaneados': len(targets),
            'resultados_individuales': [],
            'vulnerabilidades_totales': 0,
            'hosts_comprometidos': 0,
            'nivel_riesgo_general': 'BAJO'
        }
        
        try:
            for target in targets:
                if '/' in target:
                    # Es una red CIDR
                    resultado_red = self.detector.escanear_red_local(target)
                    resultado['resultados_individuales'].append(resultado_red)
                    
                    # Acumular estadísticas
                    resultado['vulnerabilidades_totales'] += resultado_red.get('hosts_con_vulnerabilidades', 0)
                    resultado['hosts_comprometidos'] += resultado_red.get('hosts_alto_riesgo', 0)
                else:
                    # Es un host individual
                    resultado_host = self.detector.analizar_vulnerabilidades_host(target)
                    resultado['resultados_individuales'].append(resultado_host)
                    
                    # Acumular estadísticas
                    if resultado_host.get('vulnerabilidades_detectadas', 0) > 0:
                        resultado['vulnerabilidades_totales'] += 1
                    
                    if resultado_host.get('nivel_riesgo_general') in ['ALTO', 'CRITICO']:
                        resultado['hosts_comprometidos'] += 1
            
            # Evaluar riesgo general
            if resultado['hosts_comprometidos'] > len(targets) // 2:
                resultado['nivel_riesgo_general'] = 'CRITICO'
            elif resultado['hosts_comprometidos'] > 0:
                resultado['nivel_riesgo_general'] = 'ALTO'
            elif resultado['vulnerabilidades_totales'] > 0:
                resultado['nivel_riesgo_general'] = 'MEDIO'
            
            resultado['mensaje_general'] = self._generar_mensaje_escaneo_completo(resultado)
            resultado['recomendaciones_generales'] = self._generar_recomendaciones_generales(resultado)
            
            self.logger.info(f"Escaneo completo finalizado: {resultado['vulnerabilidades_totales']} vulnerabilidades encontradas")
        
        except Exception as e:
            resultado['error'] = True
            resultado['mensaje'] = f"Error en escaneo completo: {e}"
            self.logger.error(f"Error en escaneo completo de red: {e}")
        
        return resultado
    
    def _generar_mensaje_escaneo_completo(self, resultado: Dict[str, Any]) -> str:
        """Genera mensaje general del escaneo completo."""
        nivel = resultado['nivel_riesgo_general']
        vulnerabilidades = resultado['vulnerabilidades_totales']
        comprometidos = resultado['hosts_comprometidos']
        
        mensajes = {
            'CRITICO': f"¡REINO BAJO ASEDIO! {comprometidos} hosts comprometidos de {resultado['targets_escaneados']} - ACCIÓN INMEDIATA REQUERIDA",
            'ALTO': f"AMENAZA SERIA: {comprometidos} hosts de alto riesgo detectados - Intervención necesaria",
            'MEDIO': f"VIGILANCIA REQUERIDA: {vulnerabilidades} vulnerabilidades detectadas en la red",
            'BAJO': "La red permanece bajo la protección del Égida - Sin amenazas críticas detectadas"
        }
        
        return mensajes.get(nivel, f"Estado de la red: {vulnerabilidades} problemas detectados")
    
    def _generar_recomendaciones_generales(self, resultado: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones generales basadas en el escaneo."""
        recomendaciones = []
        
        if resultado['hosts_comprometidos'] > 0:
            recomendaciones.append("PRIORIDAD CRÍTICA: Atender inmediatamente hosts de alto riesgo")
        
        if resultado['vulnerabilidades_totales'] > 0:
            recomendaciones.append("Implementar parches de seguridad en sistemas vulnerables")
        
        recomendaciones.extend([
            "Configurar firewall para limitar puertos expuestos",
            "Implementar monitoreo continuo de red",
            "Realizar escaneos regulares de vulnerabilidades",
            "Mantener inventario actualizado de servicios de red"
        ])
        
        return recomendaciones
    
    def generar_reporte_vulnerabilidades_red_markdown(self, resultado: Dict[str, Any]) -> str:
        """
        Genera reporte detallado de vulnerabilidades de red en formato Markdown.
        
        Args:
            resultado: Resultado del escaneo de vulnerabilidades de red
            
        Returns:
            Reporte en formato Markdown
        """
        md = "# 🌐 Reporte de Vulnerabilidades de Red\n\n"
        md += f"**Fecha de Escaneo:** {resultado['timestamp']}\n"
        md += f"**Targets Escaneados:** {resultado['targets_escaneados']}\n"
        md += f"**Nivel de Riesgo General:** {resultado['nivel_riesgo_general']}\n"
        md += f"**Hosts Comprometidos:** {resultado['hosts_comprometidos']}\n"
        md += f"**Vulnerabilidades Totales:** {resultado['vulnerabilidades_totales']}\n\n"
        
        md += f"## 📊 Resumen Ejecutivo\n\n"
        md += f"{resultado.get('mensaje_general', 'Sin mensaje general')}\n\n"
        
        # Recomendaciones generales
        recomendaciones = resultado.get('recomendaciones_generales', [])
        if recomendaciones:
            md += "## ⚔️ Decretos del Égida (Recomendaciones)\n\n"
            for recom in recomendaciones:
                md += f"- {recom}\n"
            md += "\n"
        
        # Detalles por target
        resultados_individuales = resultado.get('resultados_individuales', [])
        if resultados_individuales:
            md += "## 🎯 Análisis Detallado por Objetivo\n\n"
            
            for i, target_resultado in enumerate(resultados_individuales, 1):
                if 'red_escaneada' in target_resultado:
                    # Es resultado de red
                    md += f"### {i}. Red: {target_resultado['red_escaneada']}\n\n"
                    md += f"- **Hosts Descubiertos:** {target_resultado.get('hosts_descubiertos', 0)}\n"
                    md += f"- **Hosts con Vulnerabilidades:** {target_resultado.get('hosts_con_vulnerabilidades', 0)}\n"
                    md += f"- **Hosts de Alto Riesgo:** {target_resultado.get('hosts_alto_riesgo', 0)}\n"
                    md += f"- **Mensaje:** {target_resultado.get('mensaje_resumen', 'Sin información')}\n\n"
                    
                    # Hosts problemáticos
                    hosts_problematicos = target_resultado.get('hosts_problematicos', [])
                    if hosts_problematicos:
                        md += "**Hosts Críticos:**\n"
                        for host_info in hosts_problematicos[:5]:  # Mostrar solo los primeros 5
                            md += f"- **{host_info['host']}**: {host_info.get('mensaje_general', 'Sin información')}\n"
                        md += "\n"
                
                else:
                    # Es resultado de host individual
                    host = target_resultado.get('host', 'Host desconocido')
                    md += f"### {i}. Host: {host}\n\n"
                    
                    if target_resultado.get('error'):
                        md += f"- **Error:** {target_resultado.get('mensaje', 'Error desconocido')}\n\n"
                    else:
                        md += f"- **Nivel de Riesgo:** {target_resultado.get('nivel_riesgo_general', 'DESCONOCIDO')}\n"
                        md += f"- **Vulnerabilidades:** {target_resultado.get('vulnerabilidades_detectadas', 0)}\n"
                        md += f"- **Mensaje:** {target_resultado.get('mensaje_general', 'Sin información')}\n\n"
                        
                        # Vulnerabilidades específicas
                        vulnerabilidades = target_resultado.get('detalles_vulnerabilidades', [])
                        if vulnerabilidades:
                            md += "**Vulnerabilidades Detectadas:**\n"
                            for vuln in vulnerabilidades[:3]:  # Mostrar solo las primeras 3
                                md += f"- **[{vuln['nivel']}]** {vuln['descripcion']}\n"
                            if len(vulnerabilidades) > 3:
                                md += f"- *... y {len(vulnerabilidades) - 3} más*\n"
                            md += "\n"
        
        md += "---\n\n"
        md += "*Escaneo completado por el Explorador de los Senderos Etéreos del Égida*\n"
        
        return md
