#!/usr/bin/env python3
"""
Test básico del sistema Ares Aegis
Verifica que todos los componentes se puedan importar y funcionen correctamente
"""

import sys
import os
import tempfile
from pathlib import Path

# Añadir el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Prueba que todos los módulos se puedan importar correctamente."""
    print("🧪 Iniciando pruebas de importación...")
    
    try:
        # Probar imports de modelos
        from ares_aegis.modelos.siem import SIEM, TipoEvento
        from ares_aegis.modelos.escaneador import Escaneador
        from ares_aegis.modelos.fim import FIM
        from ares_aegis.modelos.monitor_red import MonitorRed
        from ares_aegis.modelos.cuarentena import Cuarentena
        
        print("✅ Modelos importados correctamente")
        
        # Probar import del controlador
        from ares_aegis.controladores.controlador_principal import ControladorPrincipal
        print("✅ Controlador importado correctamente")
        
        # Probar import de utilidades
        from ares_aegis.utilidades.ayuda_logging import configurar_logger_modulo
        from ares_aegis.utilidades.validacion_rutas import validar_ruta_archivo
        print("✅ Utilidades importadas correctamente")
        
        # Probar import de vista (sin ejecutar la GUI)
        from ares_aegis.vista.interfaz_principal_gui import InterfazPrincipalGUI, TemaJapones
        print("✅ Vista importada correctamente")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_siem_basico():
    """Prueba básica del SIEM."""
    print("\n🧪 Probando SIEM...")
    
    try:
        from ares_aegis.modelos.siem import SIEM, TipoEvento
        
        siem = SIEM()
        
        # Registrar un evento de prueba
        siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Prueba del sistema",
            {"test": True},
            "BAJO"
        )
        
        # Buscar eventos
        eventos = siem.buscar_eventos(limite=1)
        assert len(eventos) >= 1, "No se encontraron eventos"
        
        print("✅ SIEM funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en SIEM: {e}")
        return False

def test_escaneador_basico():
    """Prueba básica del escaneador."""
    print("\n🧪 Probando Escaneador...")
    
    try:
        from ares_aegis.modelos.siem import SIEM
        from ares_aegis.modelos.escaneador import Escaneador
        
        siem = SIEM()
        escaneador = Escaneador(siem)
        
        # Crear archivo temporal para escanear
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Este es un archivo de prueba sin malware")
            temp_file = f.name
        
        try:
            # Escanear el archivo temporal
            resultado = escaneador.escanear_multiples_rutas([os.path.dirname(temp_file)])
            
            assert 'archivos_escaneados' in resultado, "Resultado de escaneo inválido"
            assert resultado['archivos_escaneados'] >= 0, "Contador de archivos inválido"
            
            print("✅ Escaneador funcionando correctamente")
            return True
            
        finally:
            # Limpiar archivo temporal
            os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ Error en Escaneador: {e}")
        return False

def test_controlador_basico():
    """Prueba básica del controlador principal."""
    print("\n🧪 Probando Controlador Principal...")
    
    try:
        from ares_aegis.controladores.controlador_principal import ControladorPrincipal
        
        controlador = ControladorPrincipal()
        
        # Verificar que se inicializó correctamente
        assert controlador.sistema_iniciado, "Sistema no inicializado"
        assert controlador.siem is not None, "SIEM no inicializado"
        assert controlador.escaneador is not None, "Escaneador no inicializado"
        
        # Obtener estadísticas
        stats = controlador.obtener_estadisticas_generales()
        assert 'sistema_iniciado' in stats, "Estadísticas incompletas"
        
        # Verificar estado
        estado = controlador.verificar_estado_sistema()
        assert estado['sistema_iniciado'], "Estado del sistema incorrecto"
        
        # Finalizar controlador
        controlador.finalizar()
        
        print("✅ Controlador Principal funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en Controlador: {e}")
        return False

def main():
    """Función principal de pruebas."""
    print("🛡️ Pruebas del Sistema Ares Aegis")
    print("=" * 40)
    
    resultados = []
    
    # Ejecutar pruebas
    resultados.append(test_imports())
    resultados.append(test_siem_basico())
    resultados.append(test_escaneador_basico())
    resultados.append(test_controlador_basico())
    
    # Resumen
    exitos = sum(resultados)
    total = len(resultados)
    
    print(f"\n📊 Resumen de Pruebas:")
    print(f"✅ Exitosas: {exitos}/{total}")
    print(f"❌ Fallidas: {total - exitos}/{total}")
    
    if exitos == total:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("🛡️ Ares Aegis está listo para usarse")
        return 0
    else:
        print(f"\n⚠️ {total - exitos} pruebas fallaron")
        print("🔧 Revisa los errores arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main())
