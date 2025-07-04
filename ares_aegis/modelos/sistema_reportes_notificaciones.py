#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Sistema de Reportes y Notificaciones
"""

import json
import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ..utilidades.ayuda_logging import configurar_logger_modulo


def obtener_ruta_logs_local() -> str:
    """Obtiene la ruta local de logs para este módulo."""
    return str(Path(__file__).parent.parent.parent / 'logs')

# Importaciones opcionales para funcionalidades de email
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart  
    from email.mime.base import MIMEBase
    from email import encoders
    EMAIL_DISPONIBLE = True
except ImportError:
    EMAIL_DISPONIBLE = False


class HeraldoNotificaciones:
    """El Heraldo Divino - Mensajero que lleva noticias a través de todos los reinos."""
    
    def __init__(self):
        """Inicializa el heraldo de las notificaciones celestiales."""
        self.logger = configurar_logger_modulo("heraldo_notificaciones")
        
        # Configuración del reino de notificaciones
        self.config_notificaciones = {
            'email_habilitado': False,
            'smtp_servidor': 'smtp.gmail.com',
            'smtp_puerto': 587,
            'email_origen': '',
            'email_password': '',
            'emails_destino': [],
            'telegram_habilitado': False,
            'telegram_token': '',
            'telegram_chat_id': '',
            'notificaciones_desktop': True,
            'webhook_url': '',
            'niveles_notificacion': ['CRITICO', 'ALTO', 'MEDIO']
        }
        
        # Plantillas de mensajes épicos
        self.plantillas_mensajes = {
            'CRITICO': {
                'titulo': '🚨 ALERTA MÁXIMA DEL ÉGIDA',
                'prefijo': '⚔️ BATALLA CRÍTICA',
                'emoji': '🔥',
                'color': '#FF0000'
            },
            'ALTO': {
                'titulo': '⚠️ ADVERTENCIA DEL OLIMPO',
                'prefijo': '🛡️ DEFENSA NECESARIA',
                'emoji': '⚡',
                'color': '#FF8C00'
            },
            'MEDIO': {
                'titulo': 'ℹ️ MENSAJE DEL TEMPLO',
                'prefijo': '👁️ VIGILANCIA DIVINA',
                'emoji': '🔔',
                'color': '#32CD32'
            },
            'BAJO': {
                'titulo': '📋 REPORTE DEL REINO',
                'prefijo': '📜 CRÓNICA DIARIA',
                'emoji': '📝',
                'color': '#1E90FF'
            }
        }
        
        self.cargar_configuracion()
        self.logger.info("El heraldo divino ha desplegado sus alas para llevar mensajes por el éter")
    
    def cargar_configuracion(self):
        """Carga la configuración de notificaciones desde archivo sagrado."""
        config_path = Path(obtener_ruta_logs_local()).parent / 'configuracion' / 'notificaciones.json'
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_cargada = json.load(f)
                    self.config_notificaciones.update(config_cargada)
                    self.logger.info("Configuración de notificaciones cargada desde el archivo sagrado")
            else:
                self.guardar_configuracion()
                self.logger.info("Archivo de configuración creado con valores por defecto divinos")
        
        except Exception as e:
            self.logger.error(f"Error cargando configuración de notificaciones: {e}")
    
    def guardar_configuracion(self):
        """Guarda la configuración actual en el archivo sagrado."""
        config_path = Path(obtener_ruta_logs_local()).parent / 'configuracion' / 'notificaciones.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_notificaciones, f, indent=2, ensure_ascii=False)
            self.logger.info("Configuración guardada en el pergamino digital")
        except Exception as e:
            self.logger.error(f"Error guardando configuración: {e}")
    
    def configurar_email(self, servidor: str, puerto: int, email: str, password: str, destinos: List[str]):
        """
        Configura el sistema de correo divino.
        
        Args:
            servidor: Servidor SMTP del reino celestial
            puerto: Puerto de comunicación etérea
            email: Dirección del heraldo emisor
            password: Clave secreta del poder
            destinos: Lista de receptores dignos
        """
        self.config_notificaciones.update({
            'email_habilitado': True,
            'smtp_servidor': servidor,
            'smtp_puerto': puerto,
            'email_origen': email,
            'email_password': password,
            'emails_destino': destinos
        })
        
        self.guardar_configuracion()
        self.logger.info(f"Sistema de correo divino configurado para {len(destinos)} receptores")
    
    def configurar_telegram(self, token: str, chat_id: str):
        """
        Configura el sistema de mensajería instantánea.
        
        Args:
            token: Token sagrado del bot
            chat_id: ID del canal de comunicación
        """
        self.config_notificaciones.update({
            'telegram_habilitado': True,
            'telegram_token': token,
            'telegram_chat_id': chat_id
        })
        
        self.guardar_configuracion()
        self.logger.info("Sistema de mensajería instantánea configurado")
    
    def enviar_notificacion(self, nivel: str, titulo: str, mensaje: str, detalles: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Envía una notificación épica a través de todos los canales configurados.
        
        Args:
            nivel: Nivel de importancia (CRITICO, ALTO, MEDIO, BAJO)
            titulo: Título del mensaje heroico
            mensaje: Contenido del mensaje divino
            detalles: Información adicional del evento
            
        Returns:
            Dict con resultados del envío
        """
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'nivel': nivel,
            'titulo': titulo,
            'mensaje': mensaje,
            'canales_enviados': [],
            'errores': []
        }
        
        # Verificar si el nivel debe ser notificado
        if nivel not in self.config_notificaciones['niveles_notificacion']:
            resultado['mensaje_resultado'] = f"Nivel {nivel} no configurado para notificación"
            return resultado
        
        try:
            plantilla = self.plantillas_mensajes.get(nivel, self.plantillas_mensajes['MEDIO'])
            mensaje_formateado = self._formatear_mensaje(plantilla, titulo, mensaje, detalles)
            
            # Enviar por email si está configurado
            if self.config_notificaciones['email_habilitado']:
                resultado_email = self._enviar_email(mensaje_formateado, nivel)
                if resultado_email['exito']:
                    resultado['canales_enviados'].append('email')
                else:
                    resultado['errores'].append(f"Email: {resultado_email['error']}")
            
            # Enviar por Telegram si está configurado
            if self.config_notificaciones['telegram_habilitado']:
                resultado_telegram = self._enviar_telegram(mensaje_formateado, nivel)
                if resultado_telegram['exito']:
                    resultado['canales_enviados'].append('telegram')
                else:
                    resultado['errores'].append(f"Telegram: {resultado_telegram['error']}")
            
            # Notificación de escritorio
            if self.config_notificaciones['notificaciones_desktop']:
                resultado_desktop = self._enviar_notificacion_desktop(plantilla, titulo, mensaje)
                if resultado_desktop['exito']:
                    resultado['canales_enviados'].append('desktop')
                else:
                    resultado['errores'].append(f"Desktop: {resultado_desktop['error']}")
            
            # Webhook si está configurado
            if self.config_notificaciones.get('webhook_url'):
                resultado_webhook = self._enviar_webhook(mensaje_formateado, nivel, detalles)
                if resultado_webhook['exito']:
                    resultado['canales_enviados'].append('webhook')
                else:
                    resultado['errores'].append(f"Webhook: {resultado_webhook['error']}")
            
            self.logger.info(f"Notificación enviada por {len(resultado['canales_enviados'])} canales")
        
        except Exception as e:
            resultado['errores'].append(f"Error general: {e}")
            self.logger.error(f"Error enviando notificación: {e}")
        
        return resultado
    
    def _formatear_mensaje(self, plantilla: Dict, titulo: str, mensaje: str, detalles: Optional[Dict] = None) -> Dict[str, str]:
        """Formatea el mensaje usando la plantilla épica."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        mensaje_formateado = {
            'titulo_completo': f"{plantilla['emoji']} {plantilla['titulo']} {plantilla['emoji']}",
            'encabezado': f"{plantilla['prefijo']}: {titulo}",
            'cuerpo': mensaje,
            'pie': f"⏰ Tiempo divino: {timestamp}\n🏛️ Templo: Ares Égida v2.0.0",
            'texto_completo': f"{plantilla['prefijo']}: {titulo}\n\n{mensaje}\n\n⏰ {timestamp}\n🏛️ Ares Égida v2.0.0"
        }
        
        if detalles:
            detalles_texto = "\n".join([f"📋 {k}: {v}" for k, v in detalles.items()])
            mensaje_formateado['cuerpo'] += f"\n\n📊 DETALLES DIVINOS:\n{detalles_texto}"
            mensaje_formateado['texto_completo'] += f"\n\nDETALLES:\n{detalles_texto}"
        
        return mensaje_formateado
    
    def _enviar_email(self, mensaje_formateado: Dict[str, str], nivel: str) -> Dict[str, Any]:
        """Envía notificación por correo electrónico."""
        if not EMAIL_DISPONIBLE:
            return {'exito': False, 'error': 'Módulos de email no disponibles'}
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config_notificaciones['email_origen']
            msg['Subject'] = mensaje_formateado['titulo_completo']
            
            # Crear contenido HTML épico
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f0f0f0; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;">
                        <h1 style="margin: 0; font-size: 24px;">{mensaje_formateado['titulo_completo']}</h1>
                    </div>
                    <div style="padding: 30px;">
                        <h2 style="color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;">{mensaje_formateado['encabezado']}</h2>
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                            {mensaje_formateado['cuerpo'].replace('\n', '<br>')}
                        </div>
                        <div style="margin-top: 30px; text-align: center; color: #666; font-size: 14px;">
                            {mensaje_formateado['pie'].replace('\n', '<br>')}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Enviar a todos los destinatarios
            with smtplib.SMTP(self.config_notificaciones['smtp_servidor'], self.config_notificaciones['smtp_puerto']) as server:
                server.starttls()
                server.login(self.config_notificaciones['email_origen'], self.config_notificaciones['email_password'])
                
                for destinatario in self.config_notificaciones['emails_destino']:
                    msg['To'] = destinatario
                    server.send_message(msg)
                    del msg['To']
            
            return {'exito': True, 'mensaje': f"Email enviado a {len(self.config_notificaciones['emails_destino'])} destinatarios"}
        
        except Exception as e:
            return {'exito': False, 'error': str(e)}
    
    def _enviar_telegram(self, mensaje_formateado: Dict[str, str], nivel: str) -> Dict[str, Any]:
        """Envía notificación por Telegram."""
        try:
            # Verificar si requests está disponible
            try:
                import requests
            except ImportError:
                return {'exito': False, 'error': 'Módulo requests no disponible - Instalar con: pip install requests'}
            
            url = f"https://api.telegram.org/bot{self.config_notificaciones['telegram_token']}/sendMessage"
            
            # Formatear mensaje para Telegram
            texto_telegram = f"*{mensaje_formateado['titulo_completo']}*\n\n"
            texto_telegram += f"*{mensaje_formateado['encabezado']}*\n\n"
            texto_telegram += f"{mensaje_formateado['cuerpo']}\n\n"
            texto_telegram += f"_{mensaje_formateado['pie']}_"
            
            payload = {
                'chat_id': self.config_notificaciones['telegram_chat_id'],
                'text': texto_telegram,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {'exito': True, 'mensaje': 'Mensaje enviado por Telegram'}
            else:
                return {'exito': False, 'error': f"Error HTTP {response.status_code}"}
        
        except Exception as e:
            return {'exito': False, 'error': str(e)}
    
    def _enviar_notificacion_desktop(self, plantilla: Dict, titulo: str, mensaje: str) -> Dict[str, Any]:
        """Envía notificación al escritorio usando notify-send."""
        try:
            comando = [
                'notify-send',
                '--urgency=critical' if plantilla['titulo'].startswith('🚨') else '--urgency=normal',
                '--icon=security-high',
                f"{plantilla['emoji']} {titulo}",
                mensaje[:200] + '...' if len(mensaje) > 200 else mensaje
            ]
            
            resultado = subprocess.run(comando, capture_output=True, timeout=5)
            
            if resultado.returncode == 0:
                return {'exito': True, 'mensaje': 'Notificación desktop enviada'}
            else:
                return {'exito': False, 'error': f"Error en notify-send: {resultado.stderr.decode()}"}
        
        except FileNotFoundError:
            return {'exito': False, 'error': 'notify-send no disponible en el sistema'}
        except Exception as e:
            return {'exito': False, 'error': str(e)}
    
    def _enviar_webhook(self, mensaje_formateado: Dict[str, str], nivel: str, detalles: Optional[Dict] = None) -> Dict[str, Any]:
        """Envía notificación a webhook personalizado."""
        try:
            # Verificar si requests está disponible
            try:
                import requests
            except ImportError:
                return {'exito': False, 'error': 'Módulo requests no disponible - Instalar con: pip install requests'}
            
            payload = {
                'timestamp': datetime.now().isoformat(),
                'nivel': nivel,
                'titulo': mensaje_formateado['titulo_completo'],
                'mensaje': mensaje_formateado['texto_completo'],
                'detalles': detalles or {},
                'origen': 'Ares-Aegis-v2.0.0'
            }
            
            response = requests.post(
                self.config_notificaciones['webhook_url'],
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201, 202]:
                return {'exito': True, 'mensaje': 'Webhook enviado exitosamente'}
            else:
                return {'exito': False, 'error': f"Error HTTP {response.status_code}"}
        
        except Exception as e:
            return {'exito': False, 'error': str(e)}


class GeneradorReportesEpicos:
    """El Cronista del Égida - Creador de reportes épicos y documentos sagrados."""
    
    def __init__(self):
        """Inicializa el cronista de los reportes épicos."""
        self.logger = configurar_logger_modulo("generador_reportes")
        self.heraldo = HeraldoNotificaciones()
        
        # Rutas de los templos de documentos
        self.directorio_reportes = Path(obtener_ruta_logs_local()).parent / 'reportes'
        self.directorio_reportes.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("El cronista épico ha abierto sus pergaminos para escribir la historia del reino")
    
    def generar_reporte_diario(self, fecha: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Genera un reporte épico de las actividades diarias del reino.
        
        Args:
            fecha: Fecha específica para el reporte. Si None, usa hoy
            
        Returns:
            Dict con información del reporte generado
        """
        if fecha is None:
            fecha = datetime.now()
        
        fecha_str = fecha.strftime("%Y-%m-%d")
        self.logger.info(f"Generando reporte épico del día {fecha_str}")
        
        try:
            # Recopilar datos del día
            datos_reporte = self._recopilar_datos_diarios(fecha)
            
            # Generar contenido del reporte
            contenido_markdown = self._generar_contenido_reporte_diario(datos_reporte, fecha)
            
            # Guardar reporte
            nombre_archivo = f"reporte_diario_{fecha_str}.md"
            ruta_archivo = self.directorio_reportes / nombre_archivo
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido_markdown)
            
            # Generar resumen para notificación
            resumen = self._generar_resumen_diario(datos_reporte)
            
            # Enviar notificación si hay eventos importantes
            if datos_reporte['eventos_criticos'] > 0:
                self.heraldo.enviar_notificacion(
                    'CRITICO',
                    f"Reporte Diario - {datos_reporte['eventos_criticos']} Eventos Críticos",
                    resumen,
                    {'archivo_reporte': str(ruta_archivo)}
                )
            elif datos_reporte['eventos_totales'] > 100:
                self.heraldo.enviar_notificacion(
                    'ALTO',
                    f"Reporte Diario - Alta Actividad ({datos_reporte['eventos_totales']} eventos)",
                    resumen,
                    {'archivo_reporte': str(ruta_archivo)}
                )
            
            return {
                'exito': True,
                'fecha': fecha_str,
                'archivo_reporte': str(ruta_archivo),
                'datos_reporte': datos_reporte,
                'resumen': resumen,
                'mensaje': f"Reporte épico del día {fecha_str} creado exitosamente"
            }
        
        except Exception as e:
            error_msg = f"Error generando reporte diario: {e}"
            self.logger.error(error_msg)
            return {
                'exito': False,
                'error': error_msg,
                'fecha': fecha_str
            }
    
    def _recopilar_datos_diarios(self, fecha: datetime) -> Dict[str, Any]:
        """Recopila datos de actividad del día especificado."""
        datos = {
            'fecha': fecha,
            'eventos_totales': 0,
            'eventos_criticos': 0,
            'eventos_altos': 0,
            'eventos_medios': 0,
            'amenazas_detectadas': 0,
            'archivos_cuarentena': 0,
            'cambios_integridad': 0,
            'conexiones_bloqueadas': 0,
            'errores_sistema': 0,
            'tiempo_actividad': '00:00:00',
            'rendimiento_sistema': 'OPTIMO'
        }
        
        try:
            # Leer logs del día especificado
            ruta_logs = Path(obtener_ruta_logs_local())
            fecha_str = fecha.strftime("%Y-%m-%d")
            
            # Buscar archivos de log del día
            archivos_log = list(ruta_logs.glob(f"*{fecha_str}*"))
            archivos_log.extend(ruta_logs.glob("*.log"))  # Logs generales
            
            for archivo_log in archivos_log:
                try:
                    with open(archivo_log, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                        
                        # Contar eventos por nivel
                        datos['eventos_criticos'] += contenido.count('CRITICAL')
                        datos['eventos_altos'] += contenido.count('ERROR')
                        datos['eventos_medios'] += contenido.count('WARNING')
                        datos['eventos_totales'] += contenido.count('INFO')
                        
                        # Buscar patrones específicos
                        datos['amenazas_detectadas'] += contenido.count('amenaza detectada')
                        datos['archivos_cuarentena'] += contenido.count('archivo enviado a cuarentena')
                        datos['cambios_integridad'] += contenido.count('cambio de integridad')
                        datos['conexiones_bloqueadas'] += contenido.count('conexión bloqueada')
                
                except Exception as e:
                    self.logger.error(f"Error leyendo archivo de log {archivo_log}: {e}")
            
            # Calcular métricas adicionales
            datos['eventos_totales'] = datos['eventos_criticos'] + datos['eventos_altos'] + datos['eventos_medios']
            
            if datos['eventos_criticos'] > 10:
                datos['rendimiento_sistema'] = 'CRITICO'
            elif datos['eventos_altos'] > 20:
                datos['rendimiento_sistema'] = 'DEGRADADO'
            elif datos['eventos_medios'] > 50:
                datos['rendimiento_sistema'] = 'ACEPTABLE'
        
        except Exception as e:
            self.logger.error(f"Error recopilando datos diarios: {e}")
        
        return datos
    
    def _generar_contenido_reporte_diario(self, datos: Dict[str, Any], fecha: datetime) -> str:
        """Genera el contenido en Markdown del reporte diario épico."""
        fecha_str = fecha.strftime("%Y-%m-%d")
        dia_semana = fecha.strftime("%A")
        
        md = f"""# 🏛️ Crónica Épica del Reino Digital - {fecha_str}

*📅 {dia_semana} en la Era del Égida | ⚔️ Reporte del Guardián Supremo*

---

## 🌅 Resumen del Amanecer a la Medianoche

En este día glorioso de {fecha_str}, el Égida Sagrado ha mantenido vigilancia constante sobre el reino digital, registrando cada evento en los pergaminos eternos de la historia.

### 📊 Estadísticas del Reino

| 📈 Métrica Divina | 🔢 Valor | 📝 Interpretación |
|-------------------|----------|------------------|
| **⚡ Eventos Totales** | {datos['eventos_totales']} | {self._interpretar_eventos_totales(datos['eventos_totales'])} |
| **🔥 Eventos Críticos** | {datos['eventos_criticos']} | {self._interpretar_eventos_criticos(datos['eventos_criticos'])} |
| **⚠️ Eventos de Alerta** | {datos['eventos_altos']} | {self._interpretar_eventos_altos(datos['eventos_altos'])} |
| **ℹ️ Eventos de Vigilancia** | {datos['eventos_medios']} | {self._interpretar_eventos_medios(datos['eventos_medios'])} |
| **🛡️ Rendimiento General** | {datos['rendimiento_sistema']} | {self._interpretar_rendimiento(datos['rendimiento_sistema'])} |

### ⚔️ Batallas Libradas Contra las Tinieblas

| 🎯 Tipo de Amenaza | 🔢 Cantidad | 📊 Estado |
|-------------------|-------------|-----------|
| **🐛 Demonios Detectados** | {datos['amenazas_detectadas']} | {self._generar_barra_progreso(datos['amenazas_detectadas'], 50)} |
| **⛓️ Prisioneros en Tártaro** | {datos['archivos_cuarentena']} | {self._generar_barra_progreso(datos['archivos_cuarentena'], 20)} |
| **👁️ Cambios de Integridad** | {datos['cambios_integridad']} | {self._generar_barra_progreso(datos['cambios_integridad'], 30)} |
| **🚫 Conexiones Denegadas** | {datos['conexiones_bloqueadas']} | {self._generar_barra_progreso(datos['conexiones_bloqueadas'], 100)} |

---

## 🏆 Logros del Día

### ✨ Victorias Destacadas

{self._generar_logros_diarios(datos)}

### 📋 Tareas Completadas por los Guardianes

- **🔍 Escaneos Realizados**: Vigilancia constante de archivos y directorios
- **🛡️ Integridad Verificada**: Monitoreo continuo de archivos críticos
- **🌐 Red Protegida**: Análisis de conexiones y bloqueo de amenazas
- **📜 Eventos Registrados**: Documentación completa en los pergaminos eternos

---

## ⚠️ Desafíos Enfrentados

{self._generar_desafios_diarios(datos)}

---

## 🔮 Profecías para el Mañana

Basado en los patrones observados en este día sagrado, los oráculos del Égida predicen:

{self._generar_predicciones(datos)}

---

## 📜 Decreto Final del Día

{self._generar_decreto_final(datos)}

---

*📝 Crónica completada por el Cronista del Égida*  
*⏰ Generado automáticamente el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*  
*🏛️ Ares Égida v2.0.0 - "El Despertar del Égida"*

---

> *"Que cada día fortalezca el escudo, que cada evento enseñe sabiduría, y que la protección del Égida sea eterna sobre este reino digital."*

"""
        return md
    
    def _generar_resumen_diario(self, datos: Dict[str, Any]) -> str:
        """Genera un resumen conciso para notificaciones."""
        estado = "🏆 REINO SEGURO"
        
        if datos['eventos_criticos'] > 5:
            estado = "🚨 ALTO RIESGO"
        elif datos['eventos_criticos'] > 0:
            estado = "⚠️ VIGILANCIA REQUERIDA"
        elif datos['eventos_altos'] > 10:
            estado = "📋 ACTIVIDAD MODERADA"
        
        resumen = f"""
{estado}

📊 MÉTRICAS DEL DÍA:
• Eventos totales: {datos['eventos_totales']}
• Amenazas detectadas: {datos['amenazas_detectadas']}
• Archivos en cuarentena: {datos['archivos_cuarentena']}
• Estado del reino: {datos['rendimiento_sistema']}

{self._generar_mensaje_conclusion(datos)}
        """.strip()
        
        return resumen
    
    def _interpretar_eventos_totales(self, total: int) -> str:
        """Interpreta el número total de eventos."""
        if total > 1000:
            return "Reino extremadamente activo - Vigilancia máxima"
        elif total > 500:
            return "Alta actividad en el reino digital"
        elif total > 100:
            return "Actividad normal del reino"
        elif total > 10:
            return "Día tranquilo en el Olimpo"
        else:
            return "Paz absoluta reina en el reino"
    
    def _interpretar_eventos_criticos(self, criticos: int) -> str:
        """Interpreta el número de eventos críticos."""
        if criticos > 10:
            return "⚔️ BATALLA INTENSA - Acción inmediata requerida"
        elif criticos > 5:
            return "🛡️ DEFENSA ACTIVA - Monitoreo aumentado"
        elif criticos > 0:
            return "👁️ VIGILANCIA ALERTA - Situación controlada"
        else:
            return "🕊️ PAZ DIVINA - Sin amenazas detectadas"
    
    def _interpretar_eventos_altos(self, altos: int) -> str:
        """Interpreta el número de eventos de alta prioridad."""
        if altos > 20:
            return "Múltiples desafíos enfrentados"
        elif altos > 10:
            return "Actividad de alerta moderada"
        elif altos > 0:
            return "Algunos eventos requirieron atención"
        else:
            return "Operación sin sobresaltos"
    
    def _interpretar_eventos_medios(self, medios: int) -> str:
        """Interpreta el número de eventos de prioridad media."""
        if medios > 50:
            return "Reino muy vigilado y protegido"
        elif medios > 20:
            return "Vigilancia activa del territorio"
        elif medios > 0:
            return "Monitoreo rutinario completado"
        else:
            return "Silencio total en las comunicaciones"
    
    def _interpretar_rendimiento(self, rendimiento: str) -> str:
        """Interpreta el estado general del rendimiento."""
        interpretaciones = {
            'CRITICO': "🔥 ESTADO CRÍTICO - Intervención urgente necesaria",
            'DEGRADADO': "⚠️ RENDIMIENTO COMPROMETIDO - Optimización requerida",
            'ACEPTABLE': "📊 FUNCIONAMIENTO NORMAL - Monitoreo continuo",
            'OPTIMO': "⚡ RENDIMIENTO DIVINO - Égida funcionando perfectamente"
        }
        return interpretaciones.get(rendimiento, "Estado desconocido")
    
    def _generar_barra_progreso(self, valor: int, maximo: int) -> str:
        """Genera una barra de progreso visual ASCII."""
        if maximo == 0:
            porcentaje = 0
        else:
            porcentaje = min(100, (valor / maximo) * 100)
        
        bloques_llenos = int(porcentaje / 10)
        barra = "█" * bloques_llenos + "░" * (10 - bloques_llenos)
        
        if porcentaje > 80:
            emoji = "🔴"
        elif porcentaje > 50:
            emoji = "🟡"
        else:
            emoji = "🟢"
        
        return f"{emoji} {barra} {porcentaje:.1f}%"
    
    def _generar_logros_diarios(self, datos: Dict[str, Any]) -> str:
        """Genera la sección de logros del día."""
        logros = []
        
        if datos['eventos_criticos'] == 0:
            logros.append("🏆 **Día Sin Batallas**: Ningún evento crítico registrado")
        
        if datos['amenazas_detectadas'] > 0:
            logros.append(f"⚔️ **Cazador de Demonios**: {datos['amenazas_detectadas']} amenazas neutralizadas")
        
        if datos['archivos_cuarentena'] > 0:
            logros.append(f"⛓️ **Carcelero Divino**: {datos['archivos_cuarentena']} entidades malévolas encerradas")
        
        if datos['conexiones_bloqueadas'] > 50:
            logros.append(f"🚫 **Guardian de Puertas**: {datos['conexiones_bloqueadas']} conexiones denegadas")
        
        if not logros:
            logros.append("🕊️ **Día de Paz**: El reino disfrutó de tranquilidad absoluta")
        
        return "\n".join([f"- {logro}" for logro in logros])
    
    def _generar_desafios_diarios(self, datos: Dict[str, Any]) -> str:
        """Genera la sección de desafíos enfrentados."""
        if datos['eventos_criticos'] > 0:
            return f"""
### 🔥 Batallas Críticas Libradas

Durante este día, el Égida enfrentó **{datos['eventos_criticos']} batallas críticas** que pusieron a prueba la resistencia del reino. Cada desafío fue superado con la fuerza divina de la protección ancestral.

**Estrategias Empleadas:**
- Respuesta automática a amenazas
- Aislamiento inmediato de entidades malévolas
- Refuerzo de barreras defensivas
- Documentación exhaustiva para aprendizaje futuro
"""
        elif datos['eventos_altos'] > 0:
            return f"""
### ⚠️ Desafíos Menores Resueltos

El día presentó **{datos['eventos_altos']} situaciones** que requirieron la atención de los guardianes. Todas fueron resueltas con sabiduría y eficiencia.
"""
        else:
            return """
### 🕊️ Día de Armonía Total

No se presentaron desafíos significativos. El reino disfrutó de un día de paz y armonía bajo la protección constante del Égida.
"""
    
    def _generar_predicciones(self, datos: Dict[str, Any]) -> str:
        """Genera predicciones para el día siguiente."""
        predicciones = []
        
        if datos['eventos_criticos'] > 5:
            predicciones.append("⚠️ **Alta Vigilancia Requerida**: Posible continuación de actividad intensa")
        
        if datos['amenazas_detectadas'] > 10:
            predicciones.append("🛡️ **Reforzar Defensas**: Incrementar frecuencia de escaneos")
        
        if datos['cambios_integridad'] > 20:
            predicciones.append("👁️ **Monitoreo Intensivo**: Vigilar archivos críticos más frecuentemente")
        
        if not predicciones:
            predicciones.append("🌟 **Día Prometedor**: Se espera continuación de la estabilidad actual")
        
        return "\n".join([f"- {prediccion}" for prediccion in predicciones])
    
    def _generar_decreto_final(self, datos: Dict[str, Any]) -> str:
        """Genera el decreto final del día."""
        if datos['eventos_criticos'] > 10:
            return """
Por decreto del Consejo del Égida, este día queda registrado como **DÍA DE BATALLA INTENSA**. 
Los guardianes han demostrado valor excepcional en la defensa del reino. 
Que sus esfuerzos sean recordados en los anales de la historia digital.
"""
        elif datos['eventos_criticos'] > 0:
            return """
Por la gracia del Égida, este día queda marcado como **DÍA DE VIGILANCIA EXITOSA**. 
Las amenazas fueron neutralizadas y el reino permanece seguro. 
Que la protección divina continúe siendo nuestro escudo.
"""
        else:
            return """
Con la bendición de los dioses del Olimpo Digital, este día se declara como **DÍA DE PAZ DIVINA**. 
El reino ha conocido la tranquilidad bajo la protección eterna del Égida. 
Que muchos días como este adornen nuestro futuro.
"""
    
    def _generar_mensaje_conclusion(self, datos: Dict[str, Any]) -> str:
        """Genera mensaje de conclusión para el resumen."""
        if datos['eventos_criticos'] > 5:
            return "🚨 Requiere atención inmediata del administrador"
        elif datos['eventos_criticos'] > 0:
            return "⚠️ Monitoreo cercano recomendado"
        elif datos['amenazas_detectadas'] > 0:
            return "🛡️ Sistema funcionando correctamente - amenazas neutralizadas"
        else:
            return "✅ Reino en perfecto estado de seguridad"


class SistemaReportesNotificaciones:
    """Sistema completo de reportes y notificaciones del Égida."""
    
    def __init__(self, siem=None):
        """Inicializa el sistema completo de reportes."""
        self.logger = configurar_logger_modulo("sistema_reportes")
        self.siem = siem
        self.generador = GeneradorReportesEpicos()
        self.heraldo = HeraldoNotificaciones()
        
        self.logger.info("Sistema completo de reportes y notificaciones iniciado")
    
    def configurar_notificaciones_email(self, servidor: str, puerto: int, email: str, password: str, destinos: List[str]):
        """Configura las notificaciones por email."""
        self.heraldo.configurar_email(servidor, puerto, email, password, destinos)
    
    def configurar_notificaciones_telegram(self, token: str, chat_id: str):
        """Configura las notificaciones por Telegram."""
        self.heraldo.configurar_telegram(token, chat_id)
    
    def enviar_alerta_critica(self, titulo: str, mensaje: str, detalles: Optional[Dict] = None):
        """Envía una alerta crítica inmediata."""
        return self.heraldo.enviar_notificacion('CRITICO', titulo, mensaje, detalles)
    
    def enviar_notificacion_info(self, titulo: str, mensaje: str, detalles: Optional[Dict] = None):
        """Envía una notificación informativa."""
        return self.heraldo.enviar_notificacion('MEDIO', titulo, mensaje, detalles)
    
    def generar_y_enviar_reporte_diario(self, fecha: Optional[datetime] = None) -> Dict[str, Any]:
        """Genera el reporte diario y envía notificación si es necesario."""
        resultado_reporte = self.generador.generar_reporte_diario(fecha)
        
        if resultado_reporte['exito']:
            self.logger.info(f"Reporte diario generado: {resultado_reporte['archivo_reporte']}")
        else:
            self.logger.error(f"Error generando reporte diario: {resultado_reporte['error']}")
        
        return resultado_reporte
