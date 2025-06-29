#!/usr/bin/env python3
"""
Analizador de Logs del Sistema
Módulo para análisis y procesamiento de logs del sistema

Autor: DogSoulDev
Versión: 2.0.0
"""

import re
import gzip
import os
from typing import List, Dict, Optional, Any, Iterator
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter


class EventoLog:
    """Representa un evento extraído de los logs del sistema."""
    
    def __init__(self, timestamp: datetime, nivel: str, fuente: str, 
                 mensaje: str, archivo_origen: str):
        self.timestamp = timestamp
        self.nivel = nivel
        self.fuente = fuente
        self.mensaje = mensaje
        self.archivo_origen = archivo_origen
        self.sospechoso = False
        self.razones_sospecha: List[str] = []
        self.categoria = 'General'
        
    def marcar_como_sospechoso(self, razon: str) -> None:
        """Marca el evento como sospechoso."""
        self.sospechoso = True
        if razon not in self.razones_sospecha:
            self.razones_sospecha.append(razon)
    
    def asignar_categoria(self, categoria: str) -> None:
        """Asigna una categoría al evento."""
        self.categoria = categoria
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'nivel': self.nivel,
            'fuente': self.fuente,
            'mensaje': self.mensaje,
            'archivo_origen': self.archivo_origen,
            'categoria': self.categoria,
            'sospechoso': self.sospechoso,
            'razones_sospecha': self.razones_sospecha
        }


class AnalizadorLogs:
    """Analizador de logs del sistema para detección de eventos de seguridad."""
    
    def __init__(self, siem_instance=None):
        self.siem = siem_instance
        self.patrones_sospechosos = self._cargar_patrones_sospechosos()
        self.rutas_logs = self._cargar_rutas_logs()
        self.palabras_clave_seguridad = self._cargar_palabras_clave()
        self.cache_eventos = {}
        
    def _cargar_rutas_logs(self) -> List[str]:
        """Carga las rutas de archivos de log del sistema."""
        rutas_base = [
            '/var/log/auth.log',
            '/var/log/syslog',
            '/var/log/kern.log',
            '/var/log/daemon.log',
            '/var/log/user.log',
            '/var/log/messages',
            '/var/log/secure',
            '/var/log/apache2/access.log',
            '/var/log/apache2/error.log',
            '/var/log/nginx/access.log',
            '/var/log/nginx/error.log',
            '/var/log/ssh/sshd.log',
            '/var/log/fail2ban.log'
        ]
        
        # Filtrar solo archivos que existen
        rutas_existentes = []
        for ruta in rutas_base:
            if os.path.exists(ruta):
                rutas_existentes.append(ruta)
        
        return rutas_existentes
    
    def _cargar_patrones_sospechosos(self) -> Dict[str, List[str]]:
        """Carga patrones regex para detectar actividad sospechosa."""
        return {
            'autenticacion_fallida': [
                r'Failed password for .* from (\d+\.\d+\.\d+\.\d+)',
                r'authentication failure.*user=(\w+)',
                r'Invalid user (\w+) from (\d+\.\d+\.\d+\.\d+)',
                r'refused connect from (\d+\.\d+\.\d+\.\d+)'
            ],
            'escalada_privilegios': [
                r'COMMAND=(.*)',
                r'su:.*session opened for user (\w+)',
                r'usermod.*-aG.*sudo.*(\w+)',
                r'passwd:.*password changed for (\w+)'
            ],
            'acceso_root': [
                r'Accepted.*for root from (\d+\.\d+\.\d+\.\d+)',
                r'ROOT LOGIN.*tty(\d+)',
                r'su:.*session opened for user root'
            ],
            'conexiones_red': [
                r'connection from (\d+\.\d+\.\d+\.\d+)',
                r'connect from (\d+\.\d+\.\d+\.\d+)',
                r'accepted connection.*(\d+\.\d+\.\d+\.\d+)'
            ],
            'cambios_sistema': [
                r'systemctl.*start.*(\w+)',
                r'systemctl.*stop.*(\w+)',
                r'installed.*package.*(\w+)',
                r'removed.*package.*(\w+)'
            ],
            'errores_criticos': [
                r'kernel:.*Oops',
                r'kernel:.*panic',
                r'segfault at',
                r'Out of memory',
                r'filesystem.*error'
            ],
            'actividad_malware': [
                r'\.exe.*executed',
                r'base64.*decode',
                r'eval.*\(',
                r'nc.*-l.*-p',
                r'python.*-c.*import',
                r'wget.*http.*\.sh',
                r'curl.*\|.*sh'
            ]
        }
    
    def _cargar_palabras_clave(self) -> List[str]:
        """Carga palabras clave relacionadas con seguridad."""
        return [
            # Autenticación y acceso
            'failed', 'invalid', 'denied', 'refused', 'unauthorized',
            'authentication', 'login', 'logout', 'sudo', 'su',
            
            # Red y conexiones
            'connection', 'connect', 'disconnect', 'port', 'firewall',
            'iptables', 'ssh', 'ftp', 'http', 'https',
            
            # Sistema
            'error', 'warning', 'critical', 'alert', 'emergency',
            'kernel', 'panic', 'oops', 'segfault',
            
            # Seguridad
            'malware', 'virus', 'trojan', 'backdoor', 'rootkit',
            'exploit', 'attack', 'intrusion', 'breach', 'compromise',
            
            # Herramientas
            'nmap', 'metasploit', 'netcat', 'nc', 'wget', 'curl',
            'base64', 'python', 'perl', 'bash', 'sh'
        ]
    
    def leer_archivo_log(self, ruta_archivo: str, lineas_max: int = 10000) -> Iterator[str]:
        """Lee un archivo de log, manejando compresión automáticamente."""
        try:
            if ruta_archivo.endswith('.gz'):
                with gzip.open(ruta_archivo, 'rt', encoding='utf-8', errors='ignore') as f:
                    for i, linea in enumerate(f):
                        if i >= lineas_max:
                            break
                        yield linea.strip()
            else:
                with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, linea in enumerate(f):
                        if i >= lineas_max:
                            break
                        yield linea.strip()
                        
        except (IOError, OSError) as e:
            if self.siem:
                self.siem.registrar_evento(
                    'ERROR',
                    'analizador_logs',
                    f'Error al leer archivo {ruta_archivo}: {e}'
                )
    
    def parsear_linea_syslog(self, linea: str, archivo_origen: str) -> Optional[EventoLog]:
        """Parsea una línea de syslog estándar."""
        # Patrón típico de syslog: MMM DD HH:MM:SS hostname programa[pid]: mensaje
        patron_syslog = r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+([^:\[\]]+)(?:\[(\d+)\])?:\s*(.*)$'
        
        match = re.match(patron_syslog, linea)
        if match:
            fecha_str, hostname, programa, pid, mensaje = match.groups()
            
            # Convertir fecha (agregar año actual)
            try:
                fecha_completa = f"{datetime.now().year} {fecha_str}"
                timestamp = datetime.strptime(fecha_completa, "%Y %b %d %H:%M:%S")
            except ValueError:
                timestamp = datetime.now()
            
            # Determinar nivel basado en palabras clave
            mensaje_lower = mensaje.lower()
            if any(keyword in mensaje_lower for keyword in ['error', 'failed', 'failure']):
                nivel = 'ERROR'
            elif any(keyword in mensaje_lower for keyword in ['warning', 'warn']):
                nivel = 'WARNING'
            elif any(keyword in mensaje_lower for keyword in ['critical', 'crit', 'panic']):
                nivel = 'CRITICAL'
            else:
                nivel = 'INFO'
            
            evento = EventoLog(
                timestamp=timestamp,
                nivel=nivel,
                fuente=programa,
                mensaje=mensaje,
                archivo_origen=archivo_origen
            )
            
            return evento
        
        return None
    
    def analizar_eventos_sospechosos(self, eventos: List[EventoLog]) -> List[EventoLog]:
        """Analiza eventos para detectar actividad sospechosa."""
        eventos_sospechosos = []
        
        for evento in eventos:
            mensaje_lower = evento.mensaje.lower()
            
            # Verificar patrones sospechosos
            for categoria, patrones in self.patrones_sospechosos.items():
                for patron in patrones:
                    if re.search(patron, evento.mensaje, re.IGNORECASE):
                        evento.marcar_como_sospechoso(f'Patrón {categoria}: {patron}')
                        evento.asignar_categoria(categoria)
            
            # Verificar palabras clave de seguridad
            for palabra_clave in self.palabras_clave_seguridad:
                if palabra_clave in mensaje_lower:
                    if evento.nivel in ['ERROR', 'WARNING', 'CRITICAL']:
                        evento.marcar_como_sospechoso(f'Palabra clave de seguridad: {palabra_clave}')
            
            # Análisis específico por tipo de archivo
            if 'auth.log' in evento.archivo_origen:
                if any(term in mensaje_lower for term in ['failed', 'invalid', 'denied']):
                    evento.marcar_como_sospechoso('Evento de autenticación fallida')
                    evento.asignar_categoria('autenticacion')
            
            elif 'kern.log' in evento.archivo_origen:
                if any(term in mensaje_lower for term in ['oops', 'panic', 'segfault']):
                    evento.marcar_como_sospechoso('Error crítico del kernel')
                    evento.asignar_categoria('kernel')
            
            if evento.sospechoso:
                eventos_sospechosos.append(evento)
        
        return eventos_sospechosos
    
    def detectar_ataques_brute_force(self, eventos: List[EventoLog], 
                                   ventana_tiempo: int = 300) -> List[Dict[str, Any]]:
        """Detecta ataques de fuerza bruta analizando intentos fallidos."""
        ataques = []
        eventos_auth = [e for e in eventos if 'auth' in e.categoria.lower() or 'autenticacion' in e.categoria.lower()]
        
        # Agrupar por IP origen
        intentos_por_ip = defaultdict(list)
        
        for evento in eventos_auth:
            if 'failed' in evento.mensaje.lower():
                # Extraer IP del mensaje
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', evento.mensaje)
                if ip_match:
                    ip = ip_match.group(1)
                    intentos_por_ip[ip].append(evento)
        
        # Detectar ataques por ventana de tiempo
        for ip, intentos in intentos_por_ip.items():
            if len(intentos) >= 5:  # Umbral de intentos
                # Verificar si están dentro de la ventana de tiempo
                intentos_ordenados = sorted(intentos, key=lambda x: x.timestamp)
                primer_intento = intentos_ordenados[0].timestamp
                ultimo_intento = intentos_ordenados[-1].timestamp
                
                if (ultimo_intento - primer_intento).total_seconds() <= ventana_tiempo:
                    ataque = {
                        'ip_origen': ip,
                        'intentos_totales': len(intentos),
                        'primer_intento': primer_intento.isoformat(),
                        'ultimo_intento': ultimo_intento.isoformat(),
                        'duracion_segundos': (ultimo_intento - primer_intento).total_seconds(),
                        'tipo': 'brute_force',
                        'eventos': [e.to_dict() for e in intentos]
                    }
                    ataques.append(ataque)
        
        return ataques
    
    def analizar_periodo(self, horas_atras: int = 24) -> Dict[str, Any]:
        """Analiza logs del sistema en un período específico."""
        inicio = datetime.now()
        fecha_limite = datetime.now() - timedelta(hours=horas_atras)
        
        todos_los_eventos = []
        archivos_procesados = 0
        
        # Procesar cada archivo de log
        for ruta_log in self.rutas_logs:
            try:
                eventos_archivo = []
                
                for linea in self.leer_archivo_log(ruta_log, lineas_max=50000):
                    if not linea.strip():
                        continue
                    
                    evento = self.parsear_linea_syslog(linea, ruta_log)
                    if evento and evento.timestamp >= fecha_limite:
                        eventos_archivo.append(evento)
                
                todos_los_eventos.extend(eventos_archivo)
                archivos_procesados += 1
                
                if self.siem:
                    self.siem.registrar_evento(
                        'INFO',
                        'analizador_logs',
                        f'Procesado {ruta_log}: {len(eventos_archivo)} eventos'
                    )
                    
            except Exception as e:
                if self.siem:
                    self.siem.registrar_evento(
                        'ERROR',
                        'analizador_logs',
                        f'Error procesando {ruta_log}: {e}'
                    )
                continue
        
        # Analizar eventos sospechosos
        eventos_sospechosos = self.analizar_eventos_sospechosos(todos_los_eventos)
        
        # Detectar ataques de fuerza bruta
        ataques_brute_force = self.detectar_ataques_brute_force(todos_los_eventos)
        
        # Generar estadísticas
        contadores_nivel = Counter(e.nivel for e in todos_los_eventos)
        contadores_fuente = Counter(e.fuente for e in todos_los_eventos)
        contadores_categoria = Counter(e.categoria for e in eventos_sospechosos)
        
        estadisticas = {
            'total_eventos': len(todos_los_eventos),
            'eventos_sospechosos': len(eventos_sospechosos),
            'ataques_brute_force': len(ataques_brute_force),
            'archivos_procesados': archivos_procesados,
            'periodo_horas': horas_atras,
            'eventos_por_nivel': dict(contadores_nivel),
            'eventos_por_fuente': dict(contadores_fuente.most_common(10)),
            'categorias_sospechosas': dict(contadores_categoria),
            'tiempo_procesamiento': (datetime.now() - inicio).total_seconds()
        }
        
        resultado = {
            'timestamp': inicio.isoformat(),
            'periodo_analizado': {
                'desde': fecha_limite.isoformat(),
                'hasta': inicio.isoformat(),
                'horas': horas_atras
            },
            'estadisticas': estadisticas,
            'eventos_sospechosos': [e.to_dict() for e in eventos_sospechosos],
            'ataques_detectados': ataques_brute_force,
            'resumen_por_archivo': {
                ruta: sum(1 for e in todos_los_eventos if e.archivo_origen == ruta)
                for ruta in self.rutas_logs
            }
        }
        
        # Registrar en SIEM
        if self.siem:
            if eventos_sospechosos:
                self.siem.registrar_evento(
                    'WARNING',
                    'analizador_logs',
                    f'Análisis completado: {len(eventos_sospechosos)} eventos sospechosos detectados'
                )
            
            if ataques_brute_force:
                self.siem.registrar_evento(
                    'CRITICAL',
                    'analizador_logs',
                    f'Detectados {len(ataques_brute_force)} ataques de fuerza bruta'
                )
            
            self.siem.registrar_evento(
                'INFO',
                'analizador_logs',
                f'Análisis de logs completado: {len(todos_los_eventos)} eventos procesados'
            )
        
        return resultado
    
    def buscar_patrones_personalizados(self, patron: str, horas_atras: int = 24) -> List[EventoLog]:
        """Busca eventos que coincidan con un patrón personalizado."""
        eventos_encontrados = []
        fecha_limite = datetime.now() - timedelta(hours=horas_atras)
        
        for ruta_log in self.rutas_logs:
            try:
                for linea in self.leer_archivo_log(ruta_log):
                    if re.search(patron, linea, re.IGNORECASE):
                        evento = self.parsear_linea_syslog(linea, ruta_log)
                        if evento and evento.timestamp >= fecha_limite:
                            evento.marcar_como_sospechoso(f'Patrón personalizado: {patron}')
                            eventos_encontrados.append(evento)
            except Exception as e:
                if self.siem:
                    self.siem.registrar_evento(
                        'ERROR',
                        'analizador_logs',
                        f'Error buscando patrón en {ruta_log}: {e}'
                    )
        
        return eventos_encontrados
    
    def exportar_reporte_markdown(self, resultado_analisis: Dict[str, Any],
                                 ruta_archivo: Optional[str] = None) -> str:
        """Exporta el resultado del análisis a formato Markdown."""
        if not ruta_archivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_archivo = f"reporte_logs_{timestamp}.md"
        
        estadisticas = resultado_analisis['estadisticas']
        eventos_sospechosos = resultado_analisis['eventos_sospechosos']
        ataques_detectados = resultado_analisis['ataques_detectados']
        
        contenido = f"""# Reporte de Análisis de Logs - Ares Aegis

## Resumen Ejecutivo

**Fecha del Análisis:** {resultado_analisis['timestamp']}  
**Período Analizado:** {resultado_analisis['periodo_analizado']['horas']} horas  
**Desde:** {resultado_analisis['periodo_analizado']['desde']}  
**Hasta:** {resultado_analisis['periodo_analizado']['hasta']}

### Estadísticas Generales

- **Total de Eventos:** {estadisticas['total_eventos']:,}
- **Eventos Sospechosos:** {estadisticas['eventos_sospechosos']}
- **Ataques de Fuerza Bruta:** {estadisticas['ataques_brute_force']}
- **Archivos Procesados:** {estadisticas['archivos_procesados']}
- **Tiempo de Procesamiento:** {estadisticas['tiempo_procesamiento']:.2f} segundos

### Distribución por Nivel de Severidad

"""
        
        for nivel, cantidad in estadisticas['eventos_por_nivel'].items():
            contenido += f"- **{nivel}:** {cantidad:,} eventos\n"
        
        contenido += """

## Ataques Detectados

"""
        
        if ataques_detectados:
            for i, ataque in enumerate(ataques_detectados, 1):
                contenido += f"""### Ataque #{i}: Fuerza Bruta desde {ataque['ip_origen']}

- **IP Origen:** {ataque['ip_origen']}
- **Intentos Totales:** {ataque['intentos_totales']}
- **Primer Intento:** {ataque['primer_intento']}
- **Último Intento:** {ataque['ultimo_intento']}
- **Duración:** {ataque['duracion_segundos']:.0f} segundos

"""
        else:
            contenido += "✅ No se detectaron ataques de fuerza bruta en el período analizado.\n"
        
        contenido += """

## Eventos Sospechosos por Categoría

"""
        
        if estadisticas['categorias_sospechosas']:
            for categoria, cantidad in estadisticas['categorias_sospechosas'].items():
                contenido += f"- **{categoria.replace('_', ' ').title()}:** {cantidad} eventos\n"
        else:
            contenido += "✅ No se detectaron eventos sospechosos por categoría.\n"
        
        contenido += """

## Top 10 Fuentes de Eventos

"""
        
        for fuente, cantidad in list(estadisticas['eventos_por_fuente'].items())[:10]:
            contenido += f"- **{fuente}:** {cantidad:,} eventos\n"
        
        contenido += """

## Eventos Sospechosos Detallados

"""
        
        if eventos_sospechosos:
            # Agrupar por categoría
            eventos_por_categoria = defaultdict(list)
            for evento in eventos_sospechosos:
                eventos_por_categoria[evento['categoria']].append(evento)
            
            for categoria, eventos_cat in eventos_por_categoria.items():
                contenido += f"""### {categoria.replace('_', ' ').title()}

"""
                for evento in eventos_cat[:5]:  # Limitar a 5 por categoría
                    contenido += f"""#### {evento['timestamp']} - {evento['fuente']}
- **Nivel:** {evento['nivel']}
- **Mensaje:** `{evento['mensaje'][:100]}{'...' if len(evento['mensaje']) > 100 else ''}`
- **Razones:** {', '.join(evento['razones_sospecha'])}

"""
                
                if len(eventos_cat) > 5:
                    contenido += f"*Mostrando 5 de {len(eventos_cat)} eventos en esta categoría.*\n\n"
        else:
            contenido += "✅ No se detectaron eventos sospechosos en el período analizado.\n"
        
        contenido += """

## Archivos de Log Procesados

"""
        
        for archivo, eventos_count in resultado_analisis['resumen_por_archivo'].items():
            if eventos_count > 0:
                contenido += f"- **{archivo}:** {eventos_count:,} eventos\n"
        
        contenido += """

## Recomendaciones

"""
        
        if ataques_detectados:
            contenido += """### 🚨 Acción Inmediata Requerida
1. **Bloquear IPs** identificadas en ataques de fuerza bruta
2. **Revisar cuentas** objetivo de los ataques
3. **Implementar fail2ban** o herramientas similares
4. **Fortificar autenticación** (2FA, políticas de contraseñas)

"""
        
        if eventos_sospechosos:
            contenido += """### ⚠️ Investigación Recomendada
1. **Revisar eventos sospechosos** identificados
2. **Correlacionar actividad** entre diferentes fuentes
3. **Verificar integridad** del sistema
4. **Auditar accesos** y cambios recientes

"""
        
        contenido += """### ✅ Mejores Prácticas
- Implementar monitoreo continuo de logs
- Configurar alertas automáticas para eventos críticos
- Mantener logs centralizados y respaldados
- Revisar y actualizar patrones de detección regularmente
- Implementar rotación adecuada de logs

### 🔧 Herramientas Recomendadas
- **fail2ban** - Protección contra fuerza bruta
- **logwatch** - Análisis automático de logs
- **rsyslog** - Centralización de logs
- **elk stack** - Análisis avanzado de logs
- **ossec** - HIDS con análisis de logs

---

*Reporte generado por Ares Aegis - Antivirus Avanzado para Kali Linux*  
*Para más información sobre análisis de logs, consulte la documentación.*
"""
        
        # Guardar archivo
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
        except Exception as e:
            if self.siem:
                self.siem.registrar_evento(
                    'ERROR',
                    'analizador_logs',
                    f'Error al exportar reporte: {e}'
                )
            raise
        
        return ruta_archivo


# Función principal para uso desde línea de comandos
def main():
    """Función principal para ejecutar el analizador desde línea de comandos."""
    analizador = AnalizadorLogs()
    resultado = analizador.analizar_periodo(horas_atras=24)
    
    print("=== Análisis de Logs del Sistema - Ares Aegis ===")
    print(f"Total de eventos: {resultado['estadisticas']['total_eventos']:,}")
    print(f"Eventos sospechosos: {resultado['estadisticas']['eventos_sospechosos']}")
    print(f"Ataques detectados: {resultado['estadisticas']['ataques_brute_force']}")
    
    if resultado['ataques_detectados']:
        print("\n🚨 ATAQUES DETECTADOS:")
        for ataque in resultado['ataques_detectados']:
            print(f"  - Fuerza bruta desde {ataque['ip_origen']}: {ataque['intentos_totales']} intentos")
    
    if resultado['eventos_sospechosos']:
        print(f"\n⚠️ EVENTOS SOSPECHOSOS (mostrando primeros 5):")
        for evento in resultado['eventos_sospechosos'][:5]:
            print(f"  - {evento['timestamp']}: {evento['mensaje'][:60]}...")
    
    # Exportar reporte
    archivo_reporte = analizador.exportar_reporte_markdown(resultado)
    print(f"\n📄 Reporte exportado a: {archivo_reporte}")


if __name__ == "__main__":
    main()
