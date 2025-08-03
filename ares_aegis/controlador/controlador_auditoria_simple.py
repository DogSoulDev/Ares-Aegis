#!/usr/bin/env python3
"""
Controlador de Auditoría Simple para Ares Aegis
===============================================

Controlador simplificado que funciona correctamente sin los problemas
de compatibilidad de las versiones complejas.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List

from ..modelo.modelo_auditor_autenticacion import AuditorPAM
from ..utils.utils_ayuda_logging import configurar_logger_modulo


class ControladorAuditoriaSimple:
    """Controlador simple y funcional para auditorías PAM."""
    
    def __init__(self):
        """Inicializa el controlador simple."""
        self.logger = configurar_logger_modulo("controlador_auditoria_simple")
        self.auditor_pam = AuditorPAM()
        
        self.logger.info("🛡️ Controlador de Auditoría Simple inicializado")
    
    def ejecutar_auditoria_pam(self) -> Dict[str, Any]:
        """
        Ejecuta una auditoría PAM simple y retorna los resultados.
        
        Returns:
            Diccionario con los resultados de la auditoría
        """
        try:
            self.logger.info("🔐 Iniciando auditoría PAM simple...")
            
            # Ejecutar auditoría
            hallazgos = self.auditor_pam.auditar_configuracion_completa()
            
            # Clasificar hallazgos por prioridad
            clasificacion = {
                'criticos': [],
                'altos': [],
                'medios': [],
                'bajos': []
            }
            
            for h in hallazgos:
                prioridad = h.prioridad.value.lower()
                if prioridad == 'critica':
                    clasificacion['criticos'].append(h)
                elif prioridad == 'alta':
                    clasificacion['altos'].append(h)
                elif prioridad == 'media':
                    clasificacion['medios'].append(h)
                else:
                    clasificacion['bajos'].append(h)
            
            # Crear respuesta
            resultado = {
                "exito": True,
                "fecha_auditoria": datetime.now().isoformat(),
                "total_hallazgos": len(hallazgos),
                "clasificacion": {
                    "criticos": len(clasificacion['criticos']),
                    "altos": len(clasificacion['altos']),
                    "medios": len(clasificacion['medios']),
                    "bajos": len(clasificacion['bajos'])
                },
                "hallazgos_detallados": [
                    {
                        "tipo": getattr(h, 'tipo_pam', 'General'),
                        "descripcion": h.detalle_especifico,
                        "prioridad": h.prioridad.value,
                        "recomendacion": h.recomendacion,
                        "archivo_afectado": h.ruta_afectada
                    }
                    for h in hallazgos
                ],
                "resumen": f"Auditoría PAM completada: {len(clasificacion['criticos'])} críticos, {len(clasificacion['altos'])} altos"
            }
            
            self.logger.info(f"✅ Auditoría PAM completada: {len(hallazgos)} hallazgos encontrados")
            return resultado
            
        except Exception as e:
            self.logger.error(f"❌ Error en auditoría PAM: {e}")
            return {
                "exito": False,
                "error": str(e),
                "fecha_auditoria": datetime.now().isoformat(),
                "total_hallazgos": 0,
                "clasificacion": {
                    "criticos": 0,
                    "altos": 0,
                    "medios": 0,
                    "bajos": 0
                },
                "hallazgos_detallados": [],
                "resumen": f"Error en auditoría: {str(e)}"
            }
