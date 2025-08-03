"""
Utilidades para el modelo SIEM
Clases extraídas para reducir la complejidad del modelo principal
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict, deque


class TipoEvento:
    """Tipos de eventos del sistema SIEM"""
    ESCANEO_INICIADO = "ESCANEO_INICIADO"
    ESCANEO_FINALIZADO = "ESCANEO_FINALIZADO"
    ESCANEO_INTERRUMPIDO = "ESCANEO_INTERRUMPIDO"
    ANALISIS_INICIADO = "ANALISIS_INICIADO"
    ANALISIS_COMPLETADO = "ANALISIS_COMPLETADO"
    AUDITORIA_COMPLETADA = "AUDITORIA_COMPLETADA"
    
    # Eventos de Amenazas y Seguridad
    AMENAZA_DETECTADA = "AMENAZA_DETECTADA"
    AMENAZA_BLOQUEADA = "AMENAZA_BLOQUEADA"
    AMENAZA_NEUTRALIZADA = "AMENAZA_NEUTRALIZADA"
    MALWARE_DETECTADO = "MALWARE_DETECTADO"
    VIRUS_ENCONTRADO = "VIRUS_ENCONTRADO"
    TROJAN_DETECTADO = "TROJAN_DETECTADO"
    RANSOMWARE_DETECTADO = "RANSOMWARE_DETECTADO"
    ROOTKIT_DETECTADO = "ROOTKIT_DETECTADO"
    
    # Eventos de Cuarentena
    ARCHIVO_CUARENTENA = "ARCHIVO_CUARENTENA"
    ARCHIVO_RESTAURADO = "ARCHIVO_RESTAURADO"
    CUARENTENA_LIMPIADA = "CUARENTENA_LIMPIADA"
    
    # Eventos de Integridad
    INTEGRIDAD_VIOLADA = "INTEGRIDAD_VIOLADA"
    ARCHIVO_MODIFICADO = "ARCHIVO_MODIFICADO"
    ARCHIVO_ELIMINADO = "ARCHIVO_ELIMINADO"
    ARCHIVO_CREADO = "ARCHIVO_CREADO"
    PERMISOS_MODIFICADOS = "PERMISOS_MODIFICADOS"
    
    # Eventos de Red
    CONEXION_SOSPECHOSA = "CONEXION_SOSPECHOSA"
    TRAFICO_MALICIOSO = "TRAFICO_MALICIOSO"
    IP_BLOQUEADA = "IP_BLOQUEADA"
    PUERTO_ESCANEADO = "PUERTO_ESCANEADO"
    CONEXION_NO_AUTORIZADA = "CONEXION_NO_AUTORIZADA"
    ATAQUE_DENEGACION_SERVICIO = "ATAQUE_DENEGACION_SERVICIO"
    
    # Eventos de Procesos
    PROCESO_SOSPECHOSO = "PROCESO_SOSPECHOSO"
    PROCESO_MALICIOSO = "PROCESO_MALICIOSO"
    PROCESO_TERMINADO = "PROCESO_TERMINADO"
    PROCESO_ELEVACION_PRIVILEGIOS = "PROCESO_ELEVACION_PRIVILEGIOS"
    PROCESO_INYECCION_CODIGO = "PROCESO_INYECCION_CODIGO"
    
    # Eventos de Vulnerabilidades
    VULNERABILIDAD_DETECTADA = "VULNERABILIDAD_DETECTADA"
    VULNERABILIDAD_CRITICA = "VULNERABILIDAD_CRITICA"
    EXPLOIT_DETECTADO = "EXPLOIT_DETECTADO"
    CVE_ENCONTRADA = "CVE_ENCONTRADA"
    
    # Eventos de Sistema
    SISTEMA_INICIADO = "SISTEMA_INICIADO"
    SISTEMA_DETENIDO = "SISTEMA_DETENIDO"
    SERVICIO_INICIADO = "SERVICIO_INICIADO"
    SERVICIO_DETENIDO = "SERVICIO_DETENIDO"
    CONFIGURACION_MODIFICADA = "CONFIGURACION_MODIFICADA"
    
    # Eventos de Autenticación y Acceso
    LOGIN_EXITOSO = "LOGIN_EXITOSO"
    LOGIN_FALLIDO = "LOGIN_FALLIDO"
    ACCESO_DENEGADO = "ACCESO_DENEGADO"
    SESION_EXPIRADA = "SESION_EXPIRADA"
    PRIVILEGIOS_ELEVADOS = "PRIVILEGIOS_ELEVADOS"
    
    # Eventos de Error y Advertencia
    ERROR_SISTEMA = "ERROR_SISTEMA"
    ERROR_CRITICO = "ERROR_CRITICO"
    ADVERTENCIA = "ADVERTENCIA"
    INFORMACION = "INFORMACION"
    
    # Eventos de Correlación
    PATRON_ATAQUE_DETECTADO = "PATRON_ATAQUE_DETECTADO"
    MULTIPLES_INTENTOS_ACCESO = "MULTIPLES_INTENTOS_ACCESO"
    ACTIVIDAD_ANOMALA = "ACTIVIDAD_ANOMALA"
    CORRELACION_AMENAZAS = "CORRELACION_AMENAZAS"


class NivelCriticidad:
    """Niveles de criticidad del sistema"""
    CRITICO = "CRITICO"
    ALTO = "ALTO"
    MEDIO = "MEDIO"
    BAJO = "BAJO"
    INFORMATIVO = "INFORMATIVO"


class ReglaCorrelacion:
    """Regla de correlación de eventos"""
    
    def __init__(self, nombre: str, tipos_eventos: List[str], 
                 ventana_tiempo: int = 300, umbral_eventos: int = 3,
                 accion: str = "ALERTA", descripcion: str = ""):
        self.nombre = nombre
        self.tipos_eventos = tipos_eventos
        self.ventana_tiempo = ventana_tiempo
        self.umbral_eventos = umbral_eventos
        self.accion = accion
        self.descripcion = descripcion
        self.activaciones = 0
        self.ultima_activacion = None
        self.eventos_recientes = deque(maxlen=100)
        self.activa = True  # Agregado para compatibilidad
    
    def evaluar(self, evento_actual, historial_eventos: List) -> bool:
        """Evaluar si la regla se activa con el evento actual"""
        if evento_actual.tipo not in self.tipos_eventos:
            return False
        
        # Contar eventos relacionados en la ventana de tiempo
        ahora = datetime.now()
        eventos_en_ventana = [
            e for e in historial_eventos
            if e.tipo in self.tipos_eventos and
            (ahora - e.timestamp).total_seconds() <= self.ventana_tiempo
        ]
        
        return len(eventos_en_ventana) >= self.umbral_eventos


class EventoSIEMUtils:
    """Utilidades para manejo de eventos SIEM"""
    
    @staticmethod
    def generar_id_evento() -> str:
        """Generar ID único para evento"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"evt_{timestamp}"
    
    @staticmethod
    def calcular_hash_contexto(tipo: str, mensaje: str, detalles: Dict[str, Any]) -> str:
        """Calcular hash del contexto del evento"""
        contexto = f"{tipo}:{mensaje}:{json.dumps(detalles, sort_keys=True)}"
        return hashlib.md5(contexto.encode()).hexdigest()[:8]
    
    @staticmethod
    def obtener_prioridad_numerica(nivel_criticidad: str) -> int:
        """Convertir nivel de criticidad a valor numérico"""
        niveles = {
            NivelCriticidad.CRITICO: 5,
            NivelCriticidad.ALTO: 4,
            NivelCriticidad.MEDIO: 3,
            NivelCriticidad.BAJO: 2,
            NivelCriticidad.INFORMATIVO: 1
        }
        return niveles.get(nivel_criticidad, 1)
    
    @staticmethod
    def evento_to_dict(evento) -> Dict[str, Any]:
        """Convertir evento a diccionario"""
        return {
            "id": evento.id,
            "tipo": evento.tipo,
            "mensaje": evento.mensaje,
            "timestamp": evento.timestamp.isoformat(),
            "nivel_criticidad": evento.nivel_criticidad,
            "detalles": evento.detalles,
            "contexto_hash": evento.contexto_hash,
            "fuente_ip": evento.fuente_ip,
            "usuario": evento.usuario,
            "proceso": evento.proceso,
            "correlaciones": evento.correlaciones,
            "patrones": evento.patrones
        }
    
    @staticmethod
    @staticmethod
    def evento_from_dict(data: Dict[str, Any]):
        """Crear evento desde diccionario"""
        # Esta función retorna los datos procesados para crear el evento (sin timestamp)
        return {
            'tipo': data.get('tipo', ''),
            'mensaje': data.get('mensaje', ''),
            'detalles': data.get('detalles', {}),
            'nivel_criticidad': data.get('nivel_criticidad', NivelCriticidad.INFORMATIVO),
            'fuente_ip': data.get('fuente_ip'),
            'usuario': data.get('usuario'),
            'proceso': data.get('proceso'),
            'origen': data.get('origen', 'Sistema')
            # timestamp se omite porque EventoSIEM lo crea automáticamente
        }
    
    @staticmethod
    def evento_to_markdown(evento) -> str:
        """Convertir evento a formato Markdown"""
        criticidad_emoji = {
            NivelCriticidad.CRITICO: "🔴",
            NivelCriticidad.ALTO: "🟠", 
            NivelCriticidad.MEDIO: "🟡",
            NivelCriticidad.BAJO: "🔵",
            NivelCriticidad.INFORMATIVO: "⚪"
        }
        
        emoji = criticidad_emoji.get(evento.nivel_criticidad, "⚪")
        
        markdown = f"""
## {emoji} Evento SIEM: {evento.tipo}

**ID:** `{evento.id}`  
**Timestamp:** {evento.timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Criticidad:** {evento.nivel_criticidad}  
**Mensaje:** {evento.mensaje}

### Detalles
"""
        
        if evento.detalles:
            for key, value in evento.detalles.items():
                markdown += f"- **{key}:** {value}\n"
        
        if evento.fuente_ip:
            markdown += f"\n**IP Fuente:** {evento.fuente_ip}"
        if evento.usuario:
            markdown += f"\n**Usuario:** {evento.usuario}"
        if evento.proceso:
            markdown += f"\n**Proceso:** {evento.proceso}"
            
        return markdown


class MotorCorrelacionUtils:
    """Utilidades para el motor de correlación"""
    
    @staticmethod
    def crear_reglas_predefinidas() -> List[ReglaCorrelacion]:
        """Crear reglas de correlación predefinidas"""
        reglas = []
        
        # Reglas de seguridad críticas
        reglas.extend([
            ReglaCorrelacion(
                "Múltiples Fallos de Login",
                [TipoEvento.LOGIN_FALLIDO],
                ventana_tiempo=300,
                umbral_eventos=5,
                accion="BLOQUEAR_IP",
                descripcion="Detectar intentos de fuerza bruta"
            ),
            ReglaCorrelacion(
                "Detección de Malware Múltiple",
                [TipoEvento.MALWARE_DETECTADO, TipoEvento.VIRUS_ENCONTRADO, TipoEvento.TROJAN_DETECTADO],
                ventana_tiempo=600,
                umbral_eventos=3,
                accion="CUARENTENA_AGRESIVA",
                descripcion="Múltiples detecciones de malware"
            ),
            ReglaCorrelacion(
                "Actividad de Red Sospechosa",
                [TipoEvento.CONEXION_SOSPECHOSA, TipoEvento.TRAFICO_MALICIOSO],
                ventana_tiempo=180,
                umbral_eventos=10,
                accion="MONITOREO_INTENSIVO",
                descripcion="Alto volumen de tráfico sospechoso"
            ),
            ReglaCorrelacion(
                "Escalación de Privilegios",
                [TipoEvento.PROCESO_ELEVACION_PRIVILEGIOS, TipoEvento.PRIVILEGIOS_ELEVADOS],
                ventana_tiempo=120,
                umbral_eventos=2,
                accion="ALERTA_CRITICA",
                descripcion="Posible escalación de privilegios"
            ),
            ReglaCorrelacion(
                "Modificación Masiva de Archivos",
                [TipoEvento.ARCHIVO_MODIFICADO, TipoEvento.ARCHIVO_ELIMINADO],
                ventana_tiempo=300,
                umbral_eventos=50,
                accion="RESPALDO_URGENTE",
                descripcion="Posible ransomware o modificación masiva"
            )
        ])
        
        return reglas
    
    @staticmethod
    def analizar_patron_temporal(eventos: List, ventana_minutos: int = 60) -> Dict[str, Any]:
        """Analizar patrones temporales en eventos"""
        if not eventos:
            return {}
        
        ahora = datetime.now()
        eventos_recientes = [
            e for e in eventos
            if (ahora - e.timestamp).total_seconds() <= (ventana_minutos * 60)
        ]
        
        # Contar eventos por tipo
        conteo_tipos = defaultdict(int)
        for evento in eventos_recientes:
            conteo_tipos[evento.tipo] += 1
        
        # Análisis de frecuencia
        total_eventos = len(eventos_recientes)
        if total_eventos == 0:
            return {}
        
        frecuencia_promedio = total_eventos / ventana_minutos
        
        return {
            "total_eventos": total_eventos,
            "ventana_minutos": ventana_minutos,
            "frecuencia_promedio": frecuencia_promedio,
            "tipos_mas_frecuentes": dict(sorted(conteo_tipos.items(), key=lambda x: x[1], reverse=True)[:5]),
            "posible_anomalia": frecuencia_promedio > 10  # Más de 10 eventos por minuto
        }
    
    @staticmethod
    def detectar_patrones_avanzados(eventos: List) -> List[Dict[str, Any]]:
        """Detectar patrones avanzados de ataque"""
        patrones_detectados = []
        
        if not eventos:
            return patrones_detectados
        
        # Patrón: Secuencia de reconocimiento
        tipos_reconocimiento = [
            TipoEvento.PUERTO_ESCANEADO,
            TipoEvento.CONEXION_SOSPECHOSA,
            TipoEvento.VULNERABILIDAD_DETECTADA
        ]
        
        secuencia_reconocimiento = []
        for evento in eventos[-20:]:  # Últimos 20 eventos
            if evento.tipo in tipos_reconocimiento:
                secuencia_reconocimiento.append(evento)
        
        if len(secuencia_reconocimiento) >= 3:
            patrones_detectados.append({
                "tipo": "SECUENCIA_RECONOCIMIENTO",
                "criticidad": NivelCriticidad.ALTO,
                "eventos_relacionados": len(secuencia_reconocimiento),
                "descripcion": "Posible fase de reconocimiento de ataque"
            })
        
        # Patrón: Ataque coordinado
        tipos_ataque = [
            TipoEvento.MALWARE_DETECTADO,
            TipoEvento.PROCESO_SOSPECHOSO,
            TipoEvento.ARCHIVO_MODIFICADO
        ]
        
        eventos_ataque_recientes = [
            e for e in eventos[-30:]
            if e.tipo in tipos_ataque and 
            (datetime.now() - e.timestamp).total_seconds() <= 300
        ]
        
        if len(eventos_ataque_recientes) >= 5:
            patrones_detectados.append({
                "tipo": "ATAQUE_COORDINADO",
                "criticidad": NivelCriticidad.CRITICO,
                "eventos_relacionados": len(eventos_ataque_recientes),
                "descripcion": "Múltiples vectores de ataque detectados simultáneamente"
            })
        
        return patrones_detectados


class SIEMUtils:
    """Utilidades generales para el sistema SIEM"""
    
    @staticmethod
    def validar_evento(tipo: str, mensaje: str, detalles: Dict[str, Any]) -> bool:
        """Validar que un evento sea válido"""
        if not tipo or not isinstance(tipo, str):
            return False
        if not mensaje or not isinstance(mensaje, str):
            return False
        if detalles is not None and not isinstance(detalles, dict):
            return False
        return True
    
    @staticmethod
    def limpiar_eventos_antiguos(eventos: List, dias_retencion: int = 30) -> List:
        """Limpiar eventos más antiguos que el período de retención"""
        fecha_limite = datetime.now() - timedelta(days=dias_retencion)
        return [e for e in eventos if e.timestamp >= fecha_limite]
    
    @staticmethod
    def generar_resumen_seguridad(eventos: List) -> Dict[str, Any]:
        """Generar resumen de seguridad basado en eventos"""
        if not eventos:
            return {"estado": "SIN_DATOS"}
        
        # Contar eventos por criticidad
        conteo_criticidad = defaultdict(int)
        eventos_criticos = []
        
        for evento in eventos:
            conteo_criticidad[evento.nivel_criticidad] += 1
            if evento.nivel_criticidad in [NivelCriticidad.CRITICO, NivelCriticidad.ALTO]:
                eventos_criticos.append(evento)
        
        # Determinar estado general
        if conteo_criticidad[NivelCriticidad.CRITICO] > 0:
            estado = "CRITICO"
        elif conteo_criticidad[NivelCriticidad.ALTO] > 5:
            estado = "ALTO_RIESGO"
        elif conteo_criticidad[NivelCriticidad.MEDIO] > 10:
            estado = "RIESGO_MEDIO"
        else:
            estado = "NORMAL"
        
        return {
            "estado": estado,
            "total_eventos": len(eventos),
            "eventos_criticos": conteo_criticidad[NivelCriticidad.CRITICO],
            "eventos_altos": conteo_criticidad[NivelCriticidad.ALTO],
            "eventos_medios": conteo_criticidad[NivelCriticidad.MEDIO],
            "ultima_actividad": max(eventos, key=lambda e: e.timestamp).timestamp if eventos else None,
            "requiere_atencion": estado in ["CRITICO", "ALTO_RIESGO"]
        }
