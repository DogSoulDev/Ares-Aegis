#!/usr/bin/env python3
"""
Verificador de Importaciones - Ares Aegis
Script para verificar que todos los componentes se pueden importar correctamente
"""

import sys
from pathlib import Path

def verificar_importaciones():
    """Verifica que todos los componentes se puedan importar."""
    errores = []
    componentes_verificados = []
    
    print("🔍 VERIFICANDO IMPORTACIONES DE ARES AEGIS")
    print("=" * 50)
    
    # Lista de componentes a verificar
    componentes = [
        ("SIEM", "ares_aegis.modelos.siem", "SIEM"),
        ("Escaneador", "ares_aegis.modelos.escaneador", "EscaneadorMalware"),
        ("FIM Avanzado", "ares_aegis.modelos.fim", "FIMAvanzado"),
        ("Monitor Red", "ares_aegis.modelos.monitor_red", "MonitorRed"),
        ("Cuarentena", "ares_aegis.modelos.gestor_cuarentena", "GestorCuarentenaAvanzado"),
        ("Monitor Procesos", "ares_aegis.modelos.monitor_procesos", "MonitorProcesos"),
        ("Analizador Dinámico", "ares_aegis.modelos.analizador_dinamico", "AnalizadorDinamico"),
        ("Analizador Archivos", "ares_aegis.modelos.analizador_archivos", "AnalizadorArchivos"),
        ("Analizador Cadenas", "ares_aegis.modelos.analizador_cadenas", "AnalizadorCadenas"),
        # ("Reportes", "ares_aegis.modelos.sistema_reportes_notificaciones_avanzado", "SistemaReportesNotificaciones"),  # TODO: Implementar
        ("Controlador Principal", "ares_aegis.controladores.controlador_principal", "ControladorPrincipal")
    ]
    
    for nombre, modulo, clase in componentes:
        try:
            print(f"📦 Verificando {nombre}...", end=" ")
            mod = __import__(modulo, fromlist=[clase])
            cls = getattr(mod, clase)
            print("✅ OK")
            componentes_verificados.append(nombre)
        except Exception as e:
            print(f"❌ ERROR: {e}")
            errores.append((nombre, str(e)))
    
    print("\n" + "=" * 50)
    print(f"✅ Componentes verificados: {len(componentes_verificados)}")
    print(f"❌ Errores encontrados: {len(errores)}")
    
    if errores:
        print("\n🚨 ERRORES DETECTADOS:")
        for nombre, error in errores:
            print(f"   - {nombre}: {error}")
        return False
    else:
        print("\n🎉 TODOS LOS COMPONENTES SE IMPORTAN CORRECTAMENTE")
        return True

if __name__ == "__main__":
    if verificar_importaciones():
        print("\n🛡️ ARES AEGIS - SISTEMA LISTO PARA EJECUTAR")
        sys.exit(0)
    else:
        print("\n⚠️ ARES AEGIS - ERRORES DETECTADOS, REVISAR CÓDIGO")
        sys.exit(1)
