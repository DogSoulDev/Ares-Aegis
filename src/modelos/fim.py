"""
Módulo de Monitoreo de Integridad de Archivos (FIM)
Sistema para detectar cambios en archivos críticos del sistema.

Este módulo permite crear líneas base de integridad y detectar
modificaciones, adiciones y eliminaciones de archivos.
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime

from .siem import SIEM, TipoEvento


class InfoArchivo:
    """Clase para almacenar información de integridad de un archivo."""
    
    def __init__(self, ruta: str):
        """
        Inicializa la información del archivo.
        
        Args:
            ruta: Ruta del archivo
        """
        self.ruta = ruta
        self.existe = os.path.exists(ruta)
        
        if self.existe and os.path.isfile(ruta):
            stat_info = os.stat(ruta)
            self.tamano = stat_info.st_size
            self.mtime = stat_info.st_mtime
            self.permisos = oct(stat_info.st_mode)[-3:]
            self.uid = stat_info.st_uid
            self.gid = stat_info.st_gid
            self.hash_sha256 = self._calcular_hash()
        else:
            self.tamano = 0
            self.mtime = 0
            self.permisos = "000"
            self.uid = 0
            self.gid = 0
            self.hash_sha256 = ""
        
        self.timestamp_verificacion = datetime.now()
    
    def _calcular_hash(self) -> str:
        """Calcula el hash SHA256 del archivo."""
        try:
            with open(self.ruta, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la información a diccionario para serialización."""
        return {
            "ruta": self.ruta,
            "existe": self.existe,
            "tamano": self.tamano,
            "mtime": self.mtime,
            "permisos": self.permisos,
            "uid": self.uid,
            "gid": self.gid,
            "hash_sha256": self.hash_sha256,
            "timestamp_verificacion": self.timestamp_verificacion.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InfoArchivo':
        """Crea una instancia desde un diccionario."""
        info = cls.__new__(cls)
        info.ruta = data["ruta"]
        info.existe = data["existe"]
        info.tamano = data["tamano"]
        info.mtime = data["mtime"]
        info.permisos = data["permisos"]
        info.uid = data["uid"]
        info.gid = data["gid"]
        info.hash_sha256 = data["hash_sha256"]
        info.timestamp_verificacion = datetime.fromisoformat(data["timestamp_verificacion"])
        return info
    
    def __eq__(self, other: object) -> bool:
        """Compara dos instancias de InfoArchivo."""
        if not isinstance(other, InfoArchivo):
            return False
        
        return (self.existe == other.existe and
                self.tamano == other.tamano and
                self.permisos == other.permisos and
                self.uid == other.uid and
                self.gid == other.gid and
                self.hash_sha256 == other.hash_sha256)


class TipoCambio:
    """Constantes para tipos de cambios detectados."""
    ARCHIVO_MODIFICADO = "ARCHIVO_MODIFICADO"
    ARCHIVO_AGREGADO = "ARCHIVO_AGREGADO"
    ARCHIVO_ELIMINADO = "ARCHIVO_ELIMINADO"
    PERMISOS_CAMBIADOS = "PERMISOS_CAMBIADOS"
    PROPIETARIO_CAMBIADO = "PROPIETARIO_CAMBIADO"


class CambioDetectado:
    """Clase para representar un cambio detectado en el FIM."""
    
    def __init__(self, tipo: str, archivo: str, info_anterior: Optional[InfoArchivo] = None,
                 info_actual: Optional[InfoArchivo] = None, detalles: Optional[str] = None):
        """
        Inicializa un cambio detectado.
        
        Args:
            tipo: Tipo de cambio (usar constantes de TipoCambio)
            archivo: Ruta del archivo afectado
            info_anterior: Información anterior del archivo
            info_actual: Información actual del archivo
            detalles: Detalles adicionales del cambio
        """
        self.tipo = tipo
        self.archivo = archivo
        self.info_anterior = info_anterior
        self.info_actual = info_actual
        self.detalles = detalles
        self.timestamp = datetime.now()
    
    def to_markdown(self) -> str:
        """Convierte el cambio a formato Markdown."""
        markdown = f"### Cambio Detectado: `{os.path.basename(self.archivo)}`\n\n"
        markdown += f"- **Tipo:** `{self.tipo}`\n"
        markdown += f"- **Archivo:** `{self.archivo}`\n"
        markdown += f"- **Timestamp:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if self.detalles:
            markdown += f"- **Detalles:** {self.detalles}\n"
        
        if self.info_anterior and self.info_actual:
            markdown += "\n**Comparación:**\n"
            
            if self.info_anterior.hash_sha256 != self.info_actual.hash_sha256:
                markdown += f"- Hash SHA256: `{self.info_anterior.hash_sha256}` → `{self.info_actual.hash_sha256}`\n"
            
            if self.info_anterior.tamano != self.info_actual.tamano:
                markdown += f"- Tamaño: {self.info_anterior.tamano} → {self.info_actual.tamano} bytes\n"
            
            if self.info_anterior.permisos != self.info_actual.permisos:
                markdown += f"- Permisos: {self.info_anterior.permisos} → {self.info_actual.permisos}\n"
            
            if self.info_anterior.uid != self.info_actual.uid or self.info_anterior.gid != self.info_actual.gid:
                markdown += f"- Propietario: {self.info_anterior.uid}:{self.info_anterior.gid} → {self.info_actual.uid}:{self.info_actual.gid}\n"
        
        markdown += "\n"
        return markdown


class FIM:
    """Sistema de Monitoreo de Integridad de Archivos."""
    
    def __init__(self, siem: SIEM, archivo_baseline: Optional[Path] = None):
        """
        Inicializa el FIM.
        
        Args:
            siem: Instancia del SIEM para logging
            archivo_baseline: Archivo para almacenar la línea base
        """
        self.siem = siem
        self.logger = logging.getLogger(__name__)
        
        if archivo_baseline is None:
            try:
                config_dir = Path("/etc/ares_aegis")
                config_dir.mkdir(parents=True, exist_ok=True)
                self.archivo_baseline = config_dir / "fim_baseline.json"
            except PermissionError:
                # Fallback para desarrollo
                config_dir = Path.home() / ".ares_aegis"
                config_dir.mkdir(exist_ok=True)
                self.archivo_baseline = config_dir / "fim_baseline.json"
        else:
            self.archivo_baseline = archivo_baseline
        
        self.baseline: Dict[str, InfoArchivo] = {}
        self.directorios_monitoreados: Set[str] = set()
        
        # Directorios críticos por defecto en Kali Linux
        self.directorios_criticos = {
            "/etc/passwd", "/etc/shadow", "/etc/group", "/etc/gshadow",
            "/etc/hosts", "/etc/resolv.conf", "/etc/fstab", "/etc/crontab",
            "/etc/ssh/sshd_config", "/etc/sudoers", "/boot/grub/grub.cfg",
            "/etc/systemd/system", "/usr/bin", "/usr/sbin", "/bin", "/sbin"
        }
        
        self._cargar_baseline()
        self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, "FIM inicializado",
                           {"archivo_baseline": str(self.archivo_baseline)})
    
    def crear_baseline(self, rutas: List[str], incluir_criticos: bool = True) -> Dict[str, Any]:
        """
        Crea una nueva línea base de integridad.
        
        Args:
            rutas: Lista de rutas a incluir en la línea base
            incluir_criticos: Si incluir directorios críticos predeterminados
            
        Returns:
            Diccionario con estadísticas de la línea base creada
        """
        self.logger.info("Creando nueva línea base de integridad")
        self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, "Iniciando creación de línea base FIM")
        
        # Limpiar baseline existente
        self.baseline.clear()
        self.directorios_monitoreados.clear()
        
        # Agregar rutas especificadas
        rutas_a_procesar = set(rutas)
        
        # Agregar directorios críticos si se solicita
        if incluir_criticos:
            rutas_a_procesar.update(self.directorios_criticos)
        
        archivos_procesados = 0
        errores = 0
        
        for ruta in rutas_a_procesar:
            try:
                if os.path.isfile(ruta):
                    # Es un archivo individual
                    info_archivo = InfoArchivo(ruta)
                    self.baseline[ruta] = info_archivo
                    archivos_procesados += 1
                    
                elif os.path.isdir(ruta):
                    # Es un directorio
                    self.directorios_monitoreados.add(ruta)
                    archivos_en_directorio = self._procesar_directorio(ruta)
                    archivos_procesados += archivos_en_directorio
                    
                else:
                    self.logger.warning(f"Ruta no encontrada: {ruta}")
                    
            except Exception as e:
                self.logger.error(f"Error procesando {ruta}: {e}")
                errores += 1
        
        # Guardar línea base
        self._guardar_baseline()
        
        estadisticas = {
            "archivos_procesados": archivos_procesados,
            "directorios_monitoreados": len(self.directorios_monitoreados),
            "errores": errores,
            "timestamp": datetime.now(),
            "total_archivos_baseline": len(self.baseline)
        }
        
        self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, "Línea base FIM creada",
                           estadisticas)
        
        return estadisticas
    
    def verificar_integridad(self) -> List[CambioDetectado]:
        """
        Verifica la integridad actual contra la línea base.
        
        Returns:
            Lista de cambios detectados
        """
        self.logger.info("Iniciando verificación de integridad")
        self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, "Iniciando verificación FIM")
        
        if not self.baseline:
            raise ValueError("No hay línea base configurada. Cree una línea base primero.")
        
        cambios_detectados = []
        archivos_verificados = 0
        
        # Verificar archivos en la línea base
        for ruta, info_baseline in self.baseline.items():
            try:
                info_actual = InfoArchivo(ruta)
                archivos_verificados += 1
                
                # Verificar si el archivo fue eliminado
                if not info_actual.existe:
                    cambio = CambioDetectado(
                        TipoCambio.ARCHIVO_ELIMINADO,
                        ruta,
                        info_baseline,
                        info_actual,
                        "El archivo ya no existe"
                    )
                    cambios_detectados.append(cambio)
                    continue
                
                # Verificar cambios en el archivo
                cambios_archivo = self._comparar_archivos(ruta, info_baseline, info_actual)
                cambios_detectados.extend(cambios_archivo)
                
            except Exception as e:
                self.logger.error(f"Error verificando {ruta}: {e}")
        
        # Verificar archivos nuevos en directorios monitoreados
        for directorio in self.directorios_monitoreados:
            try:
                archivos_nuevos = self._detectar_archivos_nuevos(directorio)
                for archivo_nuevo in archivos_nuevos:
                    cambio = CambioDetectado(
                        TipoCambio.ARCHIVO_AGREGADO,
                        archivo_nuevo,
                        detalles="Archivo nuevo detectado"
                    )
                    cambios_detectados.append(cambio)
            except Exception as e:
                self.logger.error(f"Error verificando directorio {directorio}: {e}")
        
        # Registrar cambios en el SIEM
        for cambio in cambios_detectados:
            self.siem.log_evento(TipoEvento.INTEGRIDAD_ARCHIVO,
                               f"Cambio FIM detectado: {cambio.tipo}",
                               {"archivo": cambio.archivo, "detalles": cambio.detalles})
        
        self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, "Verificación FIM completada",
                           {"archivos_verificados": archivos_verificados,
                            "cambios_detectados": len(cambios_detectados)})
        
        return cambios_detectados
    
    def _procesar_directorio(self, directorio: str) -> int:
        """Procesa todos los archivos en un directorio para la línea base."""
        archivos_procesados = 0
        
        try:
            for root, dirs, files in os.walk(directorio):
                for archivo in files:
                    ruta_completa = os.path.join(root, archivo)
                    try:
                        info_archivo = InfoArchivo(ruta_completa)
                        self.baseline[ruta_completa] = info_archivo
                        archivos_procesados += 1
                    except Exception as e:
                        self.logger.warning(f"Error procesando archivo {ruta_completa}: {e}")
        except Exception as e:
            self.logger.error(f"Error procesando directorio {directorio}: {e}")
        
        return archivos_procesados
    
    def _comparar_archivos(self, ruta: str, info_baseline: InfoArchivo, 
                          info_actual: InfoArchivo) -> List[CambioDetectado]:
        """Compara la información de un archivo entre la línea base y el estado actual."""
        cambios = []
        
        # Verificar cambio de contenido (hash)
        if info_baseline.hash_sha256 != info_actual.hash_sha256:
            cambio = CambioDetectado(
                TipoCambio.ARCHIVO_MODIFICADO,
                ruta,
                info_baseline,
                info_actual,
                "Contenido del archivo modificado"
            )
            cambios.append(cambio)
        
        # Verificar cambio de permisos
        if info_baseline.permisos != info_actual.permisos:
            cambio = CambioDetectado(
                TipoCambio.PERMISOS_CAMBIADOS,
                ruta,
                info_baseline,
                info_actual,
                f"Permisos cambiados de {info_baseline.permisos} a {info_actual.permisos}"
            )
            cambios.append(cambio)
        
        # Verificar cambio de propietario
        if (info_baseline.uid != info_actual.uid or 
            info_baseline.gid != info_actual.gid):
            cambio = CambioDetectado(
                TipoCambio.PROPIETARIO_CAMBIADO,
                ruta,
                info_baseline,
                info_actual,
                f"Propietario cambiado de {info_baseline.uid}:{info_baseline.gid} "
                f"a {info_actual.uid}:{info_actual.gid}"
            )
            cambios.append(cambio)
        
        return cambios
    
    def _detectar_archivos_nuevos(self, directorio: str) -> List[str]:
        """Detecta archivos nuevos en un directorio monitoreado."""
        archivos_nuevos = []
        
        try:
            for root, dirs, files in os.walk(directorio):
                for archivo in files:
                    ruta_completa = os.path.join(root, archivo)
                    if ruta_completa not in self.baseline:
                        archivos_nuevos.append(ruta_completa)
        except Exception as e:
            self.logger.error(f"Error detectando archivos nuevos en {directorio}: {e}")
        
        return archivos_nuevos
    
    def _cargar_baseline(self):
        """Carga la línea base desde el archivo de persistencia."""
        try:
            if self.archivo_baseline.exists():
                with open(self.archivo_baseline, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.directorios_monitoreados = set(data.get("directorios_monitoreados", []))
                
                baseline_data = data.get("baseline", {})
                for ruta, info_dict in baseline_data.items():
                    self.baseline[ruta] = InfoArchivo.from_dict(info_dict)
                
                self.logger.info(f"Línea base cargada: {len(self.baseline)} archivos")
        except Exception as e:
            self.logger.error(f"Error cargando línea base: {e}")
    
    def _guardar_baseline(self):
        """Guarda la línea base en el archivo de persistencia."""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "directorios_monitoreados": list(self.directorios_monitoreados),
                "baseline": {ruta: info.to_dict() for ruta, info in self.baseline.items()}
            }
            
            with open(self.archivo_baseline, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Línea base guardada: {len(self.baseline)} archivos")
        except Exception as e:
            self.logger.error(f"Error guardando línea base: {e}")
    
    def generar_reporte_markdown(self, cambios: List[CambioDetectado]) -> str:
        """
        Genera un reporte en Markdown de los cambios detectados.
        
        Args:
            cambios: Lista de cambios detectados
            
        Returns:
            String con el reporte en formato Markdown
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        markdown = f"# Reporte de Monitoreo de Integridad (FIM)\n\n"
        markdown += f"**Fecha:** {timestamp}\n"
        markdown += f"**Archivos en línea base:** {len(self.baseline)}\n"
        markdown += f"**Directorios monitoreados:** {len(self.directorios_monitoreados)}\n"
        markdown += f"**Cambios detectados:** {len(cambios)}\n\n"
        
        if not cambios:
            markdown += "## ✅ Estado: INTEGRIDAD MANTENIDA\n\n"
            markdown += "No se detectaron cambios en los archivos monitoreados.\n\n"
        else:
            markdown += "## ⚠️ Estado: CAMBIOS DETECTADOS\n\n"
            
            # Agrupar cambios por tipo
            cambios_por_tipo = {}
            for cambio in cambios:
                if cambio.tipo not in cambios_por_tipo:
                    cambios_por_tipo[cambio.tipo] = []
                cambios_por_tipo[cambio.tipo].append(cambio)
            
            # Mostrar resumen
            markdown += "### Resumen de Cambios\n\n"
            for tipo, lista_cambios in cambios_por_tipo.items():
                markdown += f"- **{tipo}:** {len(lista_cambios)} archivos\n"
            markdown += "\n"
            
            # Mostrar detalles de cada cambio
            markdown += "### Detalles de Cambios\n\n"
            for cambio in cambios:
                markdown += cambio.to_markdown()
        
        return markdown
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del FIM."""
        return {
            "archivos_en_baseline": len(self.baseline),
            "directorios_monitoreados": len(self.directorios_monitoreados),
            "archivo_baseline": str(self.archivo_baseline),
            "directorios_criticos_incluidos": len(self.directorios_criticos & 
                                                  self.directorios_monitoreados)
        }
