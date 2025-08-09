#!/usr/bin/env python3
"""
Emoticonos Mitológicos para Ares Aegis
Sistema de iconografía temática mitológica para mejor UX
"""


class EmoticonosMitologicos:
    """Emoticonos mitológicos para mejor UX y comprensión del usuario"""
    
    # Dioses y mitología griega
    ARES = ""              # Dios de la guerra - Escaneador/Combate
    ATHENA = "[SHIELD]"           # Diosa de la sabiduría - Protección/FIM
    HERMES = ""            # Mensajero - Monitoreo de red/Comunicaciones  
    HADES = ""             # Dios del inframundo - Cuarentena
    APOLLO = ""            # Dios de la luz - Reportes/Análisis
    ZEUS = ""              # Rey de dioses - Sistema principal
    
    # Criaturas mitológicas
    ARGOS = ""             # Gigante de 100 ojos - Monitoreo
    HYDRA = ""             # Hidra - Amenazas múltiples
    PHOENIX = ""           # Fénix - Recuperación/Restauración
    CERBERUS = ""          # Guardián del Hades - Firewall
    
    # Elementos épicos
    ESCUDO = "[SHIELD]"           # Protección general
    ESPADA = ""           # Ataque/Escaneo activo
    CORONA = ""           # Estado premium/Activo
    RAYO = ""             # Poder/Energía
    FUEGO = ""            # Destrucción/Cuarentena
    CRISTAL = ""          # Datos valiosos/Métricas
    PERGAMINO = ""        # Reportes/Logs
    FORTALEZA = "[SYSTEM]"       # Arquitectura del sistema
    BALANZA = ""         # Análisis/Evaluación
    OJO = ""             # Vigilancia/Monitoreo
    RELOJ = "⏰"            # Tiempo real
    CORAZON = ""          # Estado de salud del sistema
    
    # Estados del sistema
    ACTIVO = ""           # Sistema funcionando
    INACTIVO = ""         # Sistema detenido  
    ADVERTENCIA = ""      # Advertencia
    CRITICO = ""          # Estado crítico
    PROCESANDO = "[REFRESH]"       # En proceso
    COMPLETADO = "[OK]"       # Tarea completada
    FALLIDO = "[ERROR]"          # Operación fallida
    
    @classmethod
    def obtener_emoji_por_funcion(cls, funcion: str) -> str:
        """Obtener emoticono apropiado según la función"""
        mapeo = {
            "escaneador": cls.ARES,
            "monitor_red": cls.HERMES, 
            "fim": cls.ATHENA,
            "cuarentena": cls.HADES,
            "reportes": cls.APOLLO,
            "sistema": cls.ZEUS,
            "monitoreo": cls.ARGOS,
            "amenazas": cls.HYDRA,
            "proteccion": cls.ESCUDO,
            "analisis": cls.BALANZA,
            "tiempo_real": cls.RELOJ,
            "salud": cls.CORAZON
        }
        return mapeo.get(funcion, cls.CRISTAL)
