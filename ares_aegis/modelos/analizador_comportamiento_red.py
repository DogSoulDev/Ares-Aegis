#!/usr/bin/env python3
"""
Analizador de Comportamiento de Red - Ares Aegis
Módulo para análisis y monitoreo del comportamiento de red

Los mensajes de este módulo siguen el estilo mitológico inspirado en Ares y la Égida.

Autor: DogSoulDev
Versión: 2.0.0 - Los Centinelas de las Rutas Etéreas
"""

import time
import socket
import subprocess
import threading
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from ..utilidades.ayuda_logging import configurar_logger_modulo


class MonitorTrafico:
    """Los Centinelas de las Rutas - Vigilan el flujo de datos por los caminos etéreos."""
    
    def __init__(self):
        """Inicializa los centinelas de las rutas etéreas."""
        self.logger = configurar_logger_modulo("monitor_trafico")
        self.conexiones_activas = {}
        self.trafico_historico = deque(maxlen=1000)
        self.alertas_activas = []
        
        self.logger.info("Los centinelas de las rutas etéreas han tomado sus posiciones")
    
    def obtener_conexiones_red(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de conexiones de red activas.
        
        Returns:
            Lista de conexiones de red detectadas
        """
        conexiones = []
        
        try:
            # Usar netstat para obtener conexiones
            resultado = subprocess.run(
                ['netstat', '-tuln'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if resultado.returncode == 0:
                for linea in resultado.stdout.split('\n')[2:]:  # Saltar cabeceras
                    if linea.strip():
                        partes = linea.split()
                        if len(partes) >= 4:
                            protocolo = partes[0]
                            direccion_local = partes[3]
                            estado = partes[5] if len(partes) > 5 else 'LISTENING'
                            
                            conexiones.append({
                                'protocolo': protocolo,
                                'direccion_local': direccion_local,
                                'estado': estado,
                                'timestamp': datetime.now().isoformat()
                            })
            
        except Exception as e:
            self.logger.error(f"Error obteniendo conexiones de red: {e}")
        
        return conexiones
    
    def analizar_puertos_sospechosos(self, conexiones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analiza puertos sospechosos en las conexiones.
        
        Args:
            conexiones: Lista de conexiones a analizar
            
        Returns:
            Lista de puertos sospechosos encontrados
        """
        puertos_sospechosos = {
            # Puertos comunes de malware
            1337: 'Elite/Hack', 31337: 'Back Orifice', 12345: 'NetBus',
            54321: 'BackOrifice 2K', 9999: 'The Portal', 40412: 'The Spy',
            50505: 'Sockets de Troie', 5742: 'WinCrash', 65000: 'Devil',
            # Puertos de servicios críticos no seguros
            23: 'Telnet (No seguro)', 21: 'FTP (Posible riesgo)',
            135: 'RPC (Vulnerable)', 139: 'NetBIOS (Riesgo)',
            445: 'SMB (Crítico)', 1433: 'SQL Server (Expuesto)',
            3389: 'RDP (Alto riesgo)', 5900: 'VNC (Sin cifrar)'
        }
        
        alertas = []
        
        for conexion in conexiones:
            direccion = conexion.get('direccion_local', '')
            try:
                if ':' in direccion:
                    puerto = int(direccion.split(':')[-1])
                    
                    if puerto in puertos_sospechosos:
                        alertas.append({
                            'puerto': puerto,
                            'descripcion': puertos_sospechosos[puerto],
                            'conexion': conexion,
                            'nivel_riesgo': 'ALTO' if puerto in [1337, 31337, 12345] else 'MEDIO',
                            'timestamp': datetime.now().isoformat()
                        })
            except (ValueError, IndexError):
                continue
        
        return alertas
    
    def detectar_patrones_anomalos(self) -> List[Dict[str, Any]]:
        """
        Detecta patrones anómalos en el tráfico de red.
        
        Returns:
            Lista de anomalías detectadas
        """
        anomalias = []
        
        if len(self.trafico_historico) < 10:
            return anomalias
        
        # Analizar frecuencia de conexiones
        conexiones_por_minuto = defaultdict(int)
        ahora = datetime.now()
        
        for registro in self.trafico_historico:
            timestamp = datetime.fromisoformat(registro.get('timestamp', ''))
            if (ahora - timestamp).total_seconds() < 300:  # Últimos 5 minutos
                minuto = timestamp.replace(second=0, microsecond=0)
                conexiones_por_minuto[minuto] += 1
        
        # Detectar picos de actividad
        promedio = sum(conexiones_por_minuto.values()) / len(conexiones_por_minuto) if conexiones_por_minuto else 0
        
        for minuto, count in conexiones_por_minuto.items():
            if count > promedio * 3:  # 3x el promedio
                anomalias.append({
                    'tipo': 'PICO_ACTIVIDAD',
                    'descripcion': f'Pico de actividad detectado: {count} conexiones',
                    'timestamp': minuto.isoformat(),
                    'severidad': 'ALTA' if count > promedio * 5 else 'MEDIA'
                })
        
        return anomalias


class AnalizadorProtocolos:
    """Los Decifradores de Protocolos - Interpretan los lenguajes de las comunicaciones etéreas."""
    
    def __init__(self):
        """Inicializa los decifradores de protocolos."""
        self.logger = configurar_logger_modulo("analizador_protocolos")
        self.protocolos_monitoreados = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'DNS']
        
        self.logger.info("Los decifradores de protocolos han abierto sus pergaminos de sabiduría")
    
    def analizar_trafico_dns(self) -> Dict[str, Any]:
        """
        Analiza el tráfico DNS en busca de comportamientos sospechosos.
        
        Returns:
            Análisis del tráfico DNS
        """
        try:
            # Simular análisis DNS (en implementación real usaríamos scapy o similar)
            consultas_dns = []
            dominios_sospechosos = [
                'tempmail', 'guerrillamail', 'mailinator', 
                'pastebin', 'hastebin', 'bit.ly'
            ]
            
            # En una implementación real, capturarías tráfico DNS
            # Por ahora, simularemos detección de patrones sospechosos
            
            return {
                'consultas_totales': len(consultas_dns),
                'dominios_sospechosos': [],
                'consultas_anomalas': [],
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error analizando tráfico DNS: {e}")
            return {'error': str(e)}
    
    def detectar_tunelizacion(self, conexiones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detecta posibles intentos de tunelización de protocolos.
        
        Args:
            conexiones: Lista de conexiones a analizar
            
        Returns:
            Lista de posibles tunelizaciones detectadas
        """
        posibles_tuneles = []
        
        # Patrones sospechosos de tunelización
        patrones_tunel = {
            'DNS_TUNNEL': {'puerto': 53, 'frecuencia_alta': True},
            'HTTP_TUNNEL': {'puerto': 80, 'conexiones_persistentes': True},
            'HTTPS_TUNNEL': {'puerto': 443, 'volumen_alto': True}
        }
        
        # Analizar conexiones en busca de patrones
        for conexion in conexiones:
            direccion = conexion.get('direccion_local', '')
            try:
                if ':' in direccion:
                    puerto = int(direccion.split(':')[-1])
                    
                    for tipo_tunel, caracteristicas in patrones_tunel.items():
                        if puerto == caracteristicas['puerto']:
                            # En implementación real, se analizarían patrones de tráfico
                            pass
            except (ValueError, IndexError):
                continue
        
        return posibles_tuneles


class AnalizadorComportamientoRed:
    """El Señor de las Comunicaciones Etéreas - Maestro de todos los análisis de red."""
    
    def __init__(self, siem=None):
        """Inicializa el señor de las comunicaciones etéreas."""
        self.logger = configurar_logger_modulo("analizador_comportamiento_red")
        self.siem = siem
        self.monitor_trafico = MonitorTrafico()
        self.analizador_protocolos = AnalizadorProtocolos()
        
        # Estado del análisis
        self.analisis_activo = False
        self.hilo_monitoreo = None
        self.estadisticas = {
            'conexiones_analizadas': 0,
            'alertas_generadas': 0,
            'anomalias_detectadas': 0,
            'inicio_monitoreo': None
        }
        
        self.logger.info("El señor de las comunicaciones etéreas ha despertado en su dominio")
    
    def iniciar_monitoreo(self) -> bool:
        """
        Inicia el monitoreo continuo del comportamiento de red.
        
        Returns:
            True si el monitoreo se inició correctamente
        """
        if self.analisis_activo:
            self.logger.warning("El monitoreo ya está activo en los dominios etéreos")
            return True
        
        try:
            self.analisis_activo = True
            self.estadisticas['inicio_monitoreo'] = datetime.now().isoformat()
            
            # Iniciar hilo de monitoreo
            self.hilo_monitoreo = threading.Thread(target=self._ciclo_monitoreo, daemon=True)
            self.hilo_monitoreo.start()
            
            self.logger.info("Iniciado el monitoreo continuo de las rutas etéreas")
            
            if self.siem:
                self.siem.log_evento('SISTEMA_INICIADO', 'Monitoreo de red activado')
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error iniciando monitoreo de red: {e}")
            return False
    
    def detener_monitoreo(self) -> bool:
        """
        Detiene el monitoreo continuo del comportamiento de red.
        
        Returns:
            True si el monitoreo se detuvo correctamente
        """
        if not self.analisis_activo:
            return True
        
        try:
            self.analisis_activo = False
            
            if self.hilo_monitoreo and self.hilo_monitoreo.is_alive():
                self.hilo_monitoreo.join(timeout=5)
            
            self.logger.info("Detenido el monitoreo de las rutas etéreas")
            
            if self.siem:
                self.siem.log_evento('SISTEMA_DETENIDO', 'Monitoreo de red desactivado')
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error deteniendo monitoreo de red: {e}")
            return False
    
    def _ciclo_monitoreo(self):
        """Ciclo principal de monitoreo de red."""
        while self.analisis_activo:
            try:
                # Obtener conexiones actuales
                conexiones = self.monitor_trafico.obtener_conexiones_red()
                self.estadisticas['conexiones_analizadas'] += len(conexiones)
                
                # Analizar puertos sospechosos
                puertos_sospechosos = self.monitor_trafico.analizar_puertos_sospechosos(conexiones)
                
                if puertos_sospechosos:
                    self.estadisticas['alertas_generadas'] += len(puertos_sospechosos)
                    for alerta in puertos_sospechosos:
                        self.logger.warning(f"Puerto sospechoso detectado: {alerta['puerto']} - {alerta['descripcion']}")
                        
                        if self.siem:
                            self.siem.log_evento('PUERTO_SOSPECHOSO', 
                                               f"Puerto {alerta['puerto']}: {alerta['descripcion']}")
                
                # Detectar anomalías
                anomalias = self.monitor_trafico.detectar_patrones_anomalos()
                
                if anomalias:
                    self.estadisticas['anomalias_detectadas'] += len(anomalias)
                    for anomalia in anomalias:
                        self.logger.warning(f"Anomalía de red detectada: {anomalia['descripcion']}")
                        
                        if self.siem:
                            self.siem.log_evento('ANOMALIA_RED', anomalia['descripcion'])
                
                # Agregar al historial
                for conexion in conexiones:
                    self.monitor_trafico.trafico_historico.append(conexion)
                
                # Pausa entre ciclos
                time.sleep(30)  # Monitorear cada 30 segundos
                
            except Exception as e:
                self.logger.error(f"Error en ciclo de monitoreo: {e}")
                time.sleep(10)  # Pausa más corta en caso de error
    
    def analisis_instantaneo(self) -> Dict[str, Any]:
        """
        Realiza un análisis instantáneo del estado actual de la red.
        
        Returns:
            Dict con el análisis completo del comportamiento de red
        """
        self.logger.info("Iniciando análisis instantáneo de las comunicaciones etéreas")
        
        inicio_tiempo = time.time()
        
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'tipo_analisis': 'instantaneo',
            'estado': 'iniciado'
        }
        
        try:
            # Obtener conexiones actuales
            conexiones = self.monitor_trafico.obtener_conexiones_red()
            resultado['conexiones'] = {
                'total': len(conexiones),
                'detalles': conexiones[:20]  # Limitar para no saturar
            }
            
            # Analizar puertos sospechosos
            puertos_sospechosos = self.monitor_trafico.analizar_puertos_sospechosos(conexiones)
            resultado['puertos_sospechosos'] = puertos_sospechosos
            
            # Analizar protocolos
            analisis_dns = self.analizador_protocolos.analizar_trafico_dns()
            resultado['analisis_dns'] = analisis_dns
            
            # Detectar tunelización
            posibles_tuneles = self.analizador_protocolos.detectar_tunelizacion(conexiones)
            resultado['tunelizacion'] = posibles_tuneles
            
            # Detectar anomalías
            anomalias = self.monitor_trafico.detectar_patrones_anomalos()
            resultado['anomalias'] = anomalias
            
            # Evaluación de riesgo
            evaluacion = self._evaluar_riesgo_red(puertos_sospechosos, anomalias, posibles_tuneles)
            resultado['evaluacion_riesgo'] = evaluacion
            
            # Estadísticas del sistema
            resultado['estadisticas'] = self.estadisticas.copy()
            
            tiempo_total = time.time() - inicio_tiempo
            resultado['tiempo_analisis'] = round(tiempo_total, 3)
            resultado['estado'] = 'completado'
            resultado['mensaje'] = 'Los secretos de las comunicaciones etéreas han sido revelados'
            
            self.logger.info(f"Análisis instantáneo completado en {tiempo_total:.3f} segundos")
            
        except Exception as e:
            resultado['estado'] = 'error'
            resultado['mensaje'] = f'Una tormenta ha perturbado el análisis etéreo: {e}'
            self.logger.error(f"Error en análisis instantáneo: {e}")
        
        return resultado
    
    def _evaluar_riesgo_red(self, puertos_sospechosos: List[Dict], 
                           anomalias: List[Dict], tuneles: List[Dict]) -> Dict[str, Any]:
        """
        Evalúa el nivel de riesgo basado en el análisis de red.
        
        Args:
            puertos_sospechosos: Lista de puertos sospechosos
            anomalias: Lista de anomalías detectadas
            tuneles: Lista de posibles tunelizaciones
            
        Returns:
            Dict con la evaluación de riesgo
        """
        puntuacion_riesgo = 0
        factores_riesgo = []
        
        # Evaluar puertos sospechosos
        for puerto in puertos_sospechosos:
            nivel = puerto.get('nivel_riesgo', 'MEDIO')
            if nivel == 'ALTO':
                puntuacion_riesgo += 5
                factores_riesgo.append(f"Puerto crítico expuesto: {puerto['puerto']}")
            else:
                puntuacion_riesgo += 2
                factores_riesgo.append(f"Puerto sospechoso: {puerto['puerto']}")
        
        # Evaluar anomalías
        for anomalia in anomalias:
            severidad = anomalia.get('severidad', 'MEDIA')
            if severidad == 'ALTA':
                puntuacion_riesgo += 4
            else:
                puntuacion_riesgo += 2
            factores_riesgo.append(f"Anomalía detectada: {anomalia['tipo']}")
        
        # Evaluar tunelización
        puntuacion_riesgo += len(tuneles) * 6
        for tunel in tuneles:
            factores_riesgo.append(f"Posible tunelización: {tunel.get('tipo', 'Desconocida')}")
        
        # Determinar nivel de riesgo
        if puntuacion_riesgo >= 15:
            nivel = "CRITICO"
            mensaje = "¡Las rutas etéreas están comprometidas! ¡Peligro inminente!"
        elif puntuacion_riesgo >= 10:
            nivel = "ALTO"
            mensaje = "Actividad sospechosa significativa en las comunicaciones etéreas"
        elif puntuacion_riesgo >= 5:
            nivel = "MEDIO"
            mensaje = "Algunas irregularidades detectadas en el flujo etéreo"
        else:
            nivel = "BAJO"
            mensaje = "Las comunicaciones etéreas fluyen en paz bajo la vigilancia divina"
        
        return {
            'nivel': nivel,
            'puntuacion': puntuacion_riesgo,
            'factores_riesgo': factores_riesgo,
            'mensaje': mensaje,
            'recomendacion': self._generar_recomendacion_red(nivel)
        }
    
    def _generar_recomendacion_red(self, nivel: str) -> str:
        """Genera recomendación basada en el nivel de riesgo de red."""
        recomendaciones = {
            "BAJO": "Mantén la vigilancia regular de las rutas etéreas",
            "MEDIO": "Incrementa la frecuencia de monitoreo y revisa configuraciones",
            "ALTO": "Implementa medidas de seguridad adicionales y bloquea puertos sospechosos",
            "CRITICO": "¡Aislamiento inmediato! Corta conexiones sospechosas y analiza compromiso"
        }
        
        return recomendaciones.get(nivel, "Consulta con los sabios de la seguridad")
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas actuales del analizador de red.
        
        Returns:
            Dict con estadísticas completas
        """
        estadisticas = self.estadisticas.copy()
        estadisticas['monitoreo_activo'] = self.analisis_activo
        estadisticas['timestamp'] = datetime.now().isoformat()
        
        if estadisticas['inicio_monitoreo']:
            inicio = datetime.fromisoformat(estadisticas['inicio_monitoreo'])
            tiempo_activo = datetime.now() - inicio
            estadisticas['tiempo_activo_segundos'] = int(tiempo_activo.total_seconds())
        
        return estadisticas
    
    def generar_reporte_red_markdown(self, analisis: Dict[str, Any]) -> str:
        """
        Genera un reporte detallado del análisis de red en formato Markdown.
        
        Args:
            analisis: Resultado del análisis de red
            
        Returns:
            Reporte en formato Markdown
        """
        md = f"# 🌐 Reporte de Análisis de Comunicaciones Etéreas\n\n"
        md += f"**Tipo de Análisis:** {analisis.get('tipo_analisis', 'Desconocido')}\n"
        md += f"**Fecha del Análisis:** {analisis.get('timestamp', 'Desconocida')}\n"
        md += f"**Estado:** {analisis.get('estado', 'Desconocido')}\n\n"
        
        if analisis.get('estado') != 'completado':
            md += f"**Mensaje:** {analisis.get('mensaje', 'Análisis incompleto')}\n"
            return md
        
        # Conexiones de red
        conexiones = analisis.get('conexiones', {})
        md += "## 🔗 Estado de las Conexiones Etéreas\n\n"
        md += f"- **Total de Conexiones:** {conexiones.get('total', 0)}\n"
        md += f"- **Tiempo de Análisis:** {analisis.get('tiempo_analisis', 0)} segundos\n\n"
        
        # Puertos sospechosos
        puertos = analisis.get('puertos_sospechosos', [])
        if puertos:
            md += "## ⚠️ Puertos Sospechosos Detectados\n\n"
            for puerto in puertos:
                md += f"- **Puerto {puerto['puerto']}:** {puerto['descripcion']} (Riesgo: {puerto['nivel_riesgo']})\n"
            md += "\n"
        
        # Anomalías
        anomalias = analisis.get('anomalias', [])
        if anomalias:
            md += "## 🚨 Anomalías en el Flujo Etéreo\n\n"
            for anomalia in anomalias:
                md += f"- **{anomalia['tipo']}:** {anomalia['descripcion']} (Severidad: {anomalia.get('severidad', 'MEDIA')})\n"
            md += "\n"
        
        # Evaluación de riesgo
        evaluacion = analisis.get('evaluacion_riesgo', {})
        if evaluacion:
            md += "## ⚔️ Juicio del Señor de las Comunicaciones\n\n"
            md += f"**Nivel de Riesgo:** {evaluacion.get('nivel', 'DESCONOCIDO')}\n"
            md += f"**Puntuación:** {evaluacion.get('puntuacion', 0)}\n"
            md += f"**Mensaje:** {evaluacion.get('mensaje', 'Sin juicio')}\n"
            md += f"**Recomendación:** {evaluacion.get('recomendacion', 'Sin recomendación')}\n\n"
            
            factores = evaluacion.get('factores_riesgo', [])
            if factores:
                md += "**Factores de Riesgo:**\n"
                for factor in factores:
                    md += f"- {factor}\n"
                md += "\n"
        
        # Estadísticas
        estadisticas = analisis.get('estadisticas', {})
        if estadisticas:
            md += "## 📊 Estadísticas del Dominio Etéreo\n\n"
            md += f"- **Conexiones Analizadas:** {estadisticas.get('conexiones_analizadas', 0)}\n"
            md += f"- **Alertas Generadas:** {estadisticas.get('alertas_generadas', 0)}\n"
            md += f"- **Anomalías Detectadas:** {estadisticas.get('anomalias_detectadas', 0)}\n"
            if estadisticas.get('inicio_monitoreo'):
                md += f"- **Inicio de Monitoreo:** {estadisticas['inicio_monitoreo']}\n"
            md += "\n"
        
        md += "---\n\n"
        md += "*Análisis completado por el Señor de las Comunicaciones Etéreas del Égida*\n"
        
        return md
