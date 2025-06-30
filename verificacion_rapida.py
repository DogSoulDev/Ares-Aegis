#!/usr/bin/env python3
"""
Script de verificación rápida de Ares Aegis.
Ejecuta verificaciones básicas de seguridad sin interfaz gráfica.
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Añadir proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

from antivirus_kali.utilidades.logger import get_logger
from antivirus_kali.utilidades.seguridad import ValidadorSeguridad
from antivirus_kali.nucleo.escaneo_sistema import EscaneoSistema
from antivirus_kali.utilidades.auxiliares import obtener_info_sistema, formatear_tamaño

logger = get_logger("AresAegisCheck")


def mostrar_banner():
    """Muestra el banner de Ares Aegis"""
    print("""
    ╔═══════════════════════════════════════════════╗
    ║              🛡️  ARES AEGIS  🛡️               ║
    ║          Verificación Rápida de Seguridad     ║
    ║                                               ║
    ║  Sistema de Seguridad Avanzado para Linux     ║
    ╚═══════════════════════════════════════════════╝
    """)


def verificacion_rapida():
    """Ejecuta una verificación rápida del sistema"""
    print("\n🔍 Iniciando verificación rápida de seguridad...")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Información del sistema
    print("\n📊 Información del Sistema:")
    info_sistema = obtener_info_sistema()
    print(f"   • Arquitectura: {info_sistema.get('arquitectura', 'Desconocida')}")
    print(f"   • CPUs: {info_sistema.get('num_cpus', 'Desconocido')}")
    print(f"   • Memoria Total: {formatear_tamaño(info_sistema.get('memoria_total', 0))}")
    print(f"   • Memoria Disponible: {formatear_tamaño(info_sistema.get('memoria_disponible', 0))}")
    print(f"   • Uso CPU: {info_sistema.get('uso_cpu', 0):.1f}%")
    print(f"   • Procesos Activos: {info_sistema.get('procesos_activos', 'Desconocido')}")
    
    # Análisis de conexiones de red
    print("\n🌐 Análisis de Red:")
    conexiones = ValidadorSeguridad.analizar_conexiones_red()
    stats = conexiones['estadisticas']
    print(f"   • Conexiones Totales: {stats['total_conexiones']}")
    print(f"   • Conexiones Establecidas: {stats['conexiones_establecidas']}")
    print(f"   • Puertos Escuchando: {stats['conexiones_escuchando']}")
    print(f"   • Puertos Sospechosos: {stats['puertos_sospechosos']}")
    print(f"   • Conexiones Externas: {stats['conexiones_externas']}")
    print(f"   • Nivel de Riesgo Red: {conexiones['nivel_riesgo']}")
    
    if conexiones['conexiones_sospechosas']:
        print("\n   ⚠️  Conexiones Sospechosas Detectadas:")
        for conn in conexiones['conexiones_sospechosas'][:5]:  # Mostrar solo las primeras 5
            print(f"      - {conn.get('tipo', 'Desconocido')}: {conn}")
    
    # Verificación de integridad del sistema
    print("\n🔐 Verificación de Integridad:")
    integridad = ValidadorSeguridad.verificar_integridad_sistema()
    print(f"   • Nivel de Riesgo: {integridad['nivel_riesgo']}")
    print(f"   • Archivos Sistema Modificados: {len(integridad['archivos_sistema_modificados'])}")
    print(f"   • Usuarios Sospechosos: {len(integridad['usuarios_sospechosos'])}")
    
    if integridad['archivos_sistema_modificados']:
        print("\n   ⚠️  Archivos del Sistema Modificados:")
        for archivo in integridad['archivos_sistema_modificados'][:3]:
            print(f"      - {archivo['archivo']}: {archivo['problema']}")
    
    if integridad['usuarios_sospechosos']:
        print("\n   ⚠️  Usuarios Sospechosos:")
        for usuario in integridad['usuarios_sospechosos']:
            print(f"      - {usuario['usuario']}: {usuario['problema']}")
    
    return conexiones, integridad


def verificacion_completa():
    """Ejecuta una verificación completa del sistema"""
    print("\n🔍 Iniciando verificación completa de seguridad...")
    
    escaneo = EscaneoSistema()
    
    # Escaneo de procesos
    print("\n🔄 Analizando procesos...")
    procesos = escaneo.escanear_procesos_sospechosos()
    print(f"   • Total Procesos: {procesos['total_procesos']}")
    print(f"   • Procesos Sospechosos: {len(procesos.get('procesos_sospechosos', []))}")
    print(f"   • Alto Consumo CPU: {len(procesos.get('procesos_alto_consumo', []))}")
    print(f"   • Con Red Activa: {len(procesos.get('procesos_red_activa', []))}")
    
    if procesos.get('procesos_sospechosos'):
        print("\n   ⚠️  Procesos Sospechosos:")
        for proceso in procesos['procesos_sospechosos'][:3]:
            print(f"      - PID {proceso['pid']}: {proceso['nombre']} - {proceso['motivo']}")
    
    # Escaneo de puertos
    print("\n🔌 Analizando puertos...")
    puertos = escaneo.escanear_puertos_abiertos()
    stats_puertos = puertos.get('estadisticas', {})
    print(f"   • Puertos TCP Abiertos: {stats_puertos.get('total_tcp', 0)}")
    print(f"   • Puertos UDP Abiertos: {stats_puertos.get('total_udp', 0)}")
    print(f"   • Puertos Sospechosos: {stats_puertos.get('sospechosos', 0)}")
    
    if puertos.get('puertos_sospechosos'):
        print("\n   ⚠️  Puertos Sospechosos:")
        for puerto in puertos['puertos_sospechosos'][:3]:
            print(f"      - Puerto {puerto['puerto']} ({puerto['tipo']}): {puerto.get('motivo', 'N/A')}")
    
    # Escaneo de servicios
    print("\n⚙️  Analizando servicios...")
    servicios = escaneo.escanear_servicios_activos()
    stats_servicios = servicios.get('estadisticas', {})
    print(f"   • Servicios Activos: {stats_servicios.get('activos', 0)}")
    print(f"   • Servicios Fallidos: {stats_servicios.get('fallidos', 0)}")
    print(f"   • Servicios Sospechosos: {stats_servicios.get('sospechosos', 0)}")
    
    if servicios.get('servicios_sospechosos'):
        print("\n   ⚠️  Servicios Sospechosos:")
        for servicio in servicios['servicios_sospechosos'][:3]:
            print(f"      - {servicio['nombre']}: {servicio.get('descripcion', 'N/A')}")
    
    # Escaneo de rootkits
    print("\n🦠 Escaneando rootkits...")
    rootkits = escaneo.escanear_rootkits()
    print(f"   • Herramientas Ejecutadas: {', '.join(rootkits.get('herramientas_ejecutadas', []))}")
    print(f"   • Amenazas Detectadas: {len(rootkits.get('amenazas_detectadas', []))}")
    print(f"   • Estado: {rootkits.get('estado', 'DESCONOCIDO')}")
    
    if rootkits.get('amenazas_detectadas'):
        print("\n   ⚠️  Amenazas Detectadas:")
        for amenaza in rootkits['amenazas_detectadas'][:3]:
            print(f"      - {amenaza}")
    
    if rootkits.get('advertencias'):
        print("\n   ℹ️  Advertencias:")
        for advertencia in rootkits['advertencias']:
            print(f"      - {advertencia}")
    
    return procesos, puertos, servicios, rootkits


def generar_resumen(datos_verificacion):
    """Genera un resumen de la verificación"""
    print("\n" + "="*50)
    print("📋 RESUMEN DE VERIFICACIÓN")
    print("="*50)
    
    total_problemas = 0
    nivel_riesgo_global = "BAJO"
    
    # Contar problemas encontrados
    if len(datos_verificacion) >= 2:  # Verificación rápida
        conexiones, integridad = datos_verificacion[0], datos_verificacion[1]
        
        total_problemas += len(conexiones.get('conexiones_sospechosas', []))
        total_problemas += len(integridad.get('archivos_sistema_modificados', []))
        total_problemas += len(integridad.get('usuarios_sospechosos', []))
        
        if conexiones['nivel_riesgo'] in ['ALTO', 'CRITICO'] or integridad['nivel_riesgo'] in ['ALTO', 'CRITICO']:
            nivel_riesgo_global = "ALTO"
        elif conexiones['nivel_riesgo'] == 'MEDIO' or integridad['nivel_riesgo'] == 'MEDIO':
            nivel_riesgo_global = "MEDIO"
    
    if len(datos_verificacion) >= 4:  # Verificación completa
        procesos, puertos, servicios, rootkits = datos_verificacion[-4:]
        
        total_problemas += len(procesos.get('procesos_sospechosos', []))
        total_problemas += len(puertos.get('puertos_sospechosos', []))
        total_problemas += len(servicios.get('servicios_sospechosos', []))
        total_problemas += len(rootkits.get('amenazas_detectadas', []))
    
    # Determinar nivel de riesgo global
    if total_problemas > 10:
        nivel_riesgo_global = "CRITICO"
    elif total_problemas > 5:
        nivel_riesgo_global = "ALTO"
    elif total_problemas > 0:
        nivel_riesgo_global = "MEDIO"
    
    print(f"🎯 Total de Problemas Detectados: {total_problemas}")
    print(f"⚠️  Nivel de Riesgo Global: {nivel_riesgo_global}")
    
    # Recomendaciones
    print("\n💡 Recomendaciones:")
    if total_problemas == 0:
        print("   ✅ Sistema aparentemente seguro")
        print("   ✅ Mantener monitoreo regular")
        print("   ✅ Actualizar definiciones de antivirus")
    else:
        if nivel_riesgo_global == "CRITICO":
            print("   🚨 ACCIÓN INMEDIATA REQUERIDA")
            print("   🚨 Desconectar de la red si es posible")
            print("   🚨 Ejecutar limpieza profunda del sistema")
        elif nivel_riesgo_global == "ALTO":
            print("   ⚠️  Revisar y corregir problemas identificados")
            print("   ⚠️  Ejecutar escaneo completo con herramientas especializadas")
        else:
            print("   ℹ️  Investigar problemas menores detectados")
            print("   ℹ️  Incrementar frecuencia de monitoreo")
    
    print("\n" + "="*50)
    
    return {
        'total_problemas': total_problemas,
        'nivel_riesgo': nivel_riesgo_global,
        'timestamp': datetime.now().isoformat()
    }


def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(
        description="Verificación rápida de seguridad de Ares Aegis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python verificacion_rapida.py              # Verificación rápida
  python verificacion_rapida.py --completo   # Verificación completa
  python verificacion_rapida.py --silencioso # Sin banner
        """
    )
    
    parser.add_argument(
        '--completo', 
        action='store_true',
        help='Ejecutar verificación completa (incluye procesos, servicios, rootkits)'
    )
    
    parser.add_argument(
        '--silencioso',
        action='store_true', 
        help='No mostrar banner inicial'
    )
    
    parser.add_argument(
        '--guardar',
        type=str,
        help='Guardar resumen en archivo especificado'
    )
    
    args = parser.parse_args()
    
    try:
        # Mostrar banner
        if not args.silencioso:
            mostrar_banner()
        
        inicio = time.time()
        
        # Ejecutar verificación
        if args.completo:
            datos_rapida = verificacion_rapida()
            datos_completa = verificacion_completa()
            datos_verificacion = datos_rapida + datos_completa
        else:
            datos_verificacion = verificacion_rapida()
        
        # Generar resumen
        resumen = generar_resumen(datos_verificacion)
        
        tiempo_total = time.time() - inicio
        print(f"\n⏱️  Tiempo total de verificación: {tiempo_total:.2f} segundos")
        
        # Guardar resumen si se especifica
        if args.guardar:
            try:
                import json
                resumen['tiempo_verificacion'] = tiempo_total
                resumen['tipo_verificacion'] = 'completa' if args.completo else 'rapida'
                
                with open(args.guardar, 'w') as f:
                    json.dump(resumen, f, indent=2)
                print(f"📄 Resumen guardado en: {args.guardar}")
            except Exception as e:
                print(f"❌ Error guardando resumen: {e}")
        
        # Código de salida basado en nivel de riesgo
        if resumen['nivel_riesgo'] == 'CRITICO':
            return 3
        elif resumen['nivel_riesgo'] == 'ALTO':
            return 2
        elif resumen['nivel_riesgo'] == 'MEDIO':
            return 1
        else:
            return 0
            
    except KeyboardInterrupt:
        print("\n\n⚡ Verificación cancelada por el usuario")
        return 130
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        logger.error(f"Error en verificación: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
