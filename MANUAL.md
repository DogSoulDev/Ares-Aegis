# Manual de Usuario - Ares Aegis

## 🛡️ Ares Aegis: Antivirus Avanzado para Kali Linux

### Índice
1. [Instalación y Configuración](#instalación-y-configuración)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Uso de la Interfaz Gráfica](#uso-de-la-interfaz-gráfica)
4. [Funcionalidades Principales](#funcionalidades-principales)
5. [Configuración Avanzada](#configuración-avanzada)
6. [Solución de Problemas](#solución-de-problemas)

---

## Instalación y Configuración

### Requisitos Previos
- **Sistema Operativo:** Kali Linux (recomendado) o cualquier distribución basada en Debian
- **Python:** Versión 3.8 o superior
- **Privilegios:** Acceso root para funcionalidad completa

### Instalación Rápida
```bash
# Clonar el repositorio
git clone https://github.com/DogSoulDev/Ares-Aegis.git
cd Ares-Aegis

# Instalar dependencias
pip3 install -r requirements.txt

# Ejecutar el programa
sudo python3 main.py
```

---

## Estructura del Proyecto

```
Ares-Aegis/
├── main.py                    # Punto de entrada principal
├── requirements.txt           # Dependencias del proyecto
├── README.md                 # Documentación del proyecto
├── MANUAL.md                 # Manual de usuario (este archivo)
│
├── src/                      # Código fuente principal
│   ├── __init__.py
│   ├── modelos/              # Modelos de datos y lógica de negocio
│   │   ├── __init__.py
│   │   ├── siem.py           # Sistema SIEM (log de eventos)
│   │   ├── escaneador.py     # Motor de escaneo de archivos
│   │   ├── fim.py            # File Integrity Monitoring
│   │   ├── cuarentena.py     # Gestión de cuarentena
│   │   ├── integracion_externa.py  # Integración con ClamAV
│   │   └── monitor_red.py    # Monitoreo de red
│   │
│   ├── vista/                # Interfaz gráfica
│   │   ├── __init__.py
│   │   └── interfaz_principal_gui.py  # Interfaz principal
│   │
│   └── controladores/        # Controladores MVC
│       ├── __init__.py
│       └── controlador_principal.py  # Controlador principal
│
├── config/                   # Archivos de configuración
│   └── firmas/
│       └── firmas.txt        # Base de datos de firmas de malware
│
├── recursos/                 # Recursos gráficos
│   ├── README.md             # Documentación de recursos
│   ├── AresAegis.png         # Logo principal del programa
│   └── aresIcon.png          # Icono de la aplicación
│
└── tests/                    # Tests unitarios y de integración
    ├── __init__.py
    └── test_*.py             # Archivos de prueba
```

### Descripción de Componentes

#### 📁 src/modelos/
- **siem.py**: Sistema de Information and Event Management para logging centralizado
- **escaneador.py**: Motor interno de análisis de archivos con detección de patrones
- **fim.py**: File Integrity Monitoring para detectar cambios en archivos críticos
- **cuarentena.py**: Sistema de cuarentena para aislar archivos sospechosos
- **integracion_externa.py**: Integración con herramientas externas como ClamAV
- **monitor_red.py**: Monitoreo de conexiones de red y puertos sospechosos

#### 📁 src/vista/
- **interfaz_principal_gui.py**: Interfaz gráfica principal con diseño japonés minimalista

#### 📁 src/controladores/
- **controlador_principal.py**: Controlador principal que coordina toda la aplicación

---

## Uso de la Interfaz Gráfica

### Pantalla Principal
Al iniciar Ares Aegis, se presenta el menú principal con las siguientes opciones:

#### 🔍 Detección y Análisis de Archivos
**Propósito**: Escanear archivos y directorios en busca de amenazas

**Opciones disponibles**:
- **Seleccionar Archivo/Directorio**: Usar el explorador para elegir qué analizar
- **Escanear Archivo (Interno)**: Usar el motor interno de Ares Aegis
- **Escanear Directorio (Interno)**: Análisis recursivo de directorios
- **Escanear con ClamAV**: Usar el motor externo ClamAV (si está instalado)

**Resultados**: Se muestran en tiempo real con:
- Estado de cada archivo escaneado
- Amenazas detectadas con nivel de riesgo
- Recomendaciones de acción
- Opción de exportar resultados a Markdown

#### 📊 Monitoreo de Sistema y Procesos
**Propósito**: Vigilancia en tiempo real del sistema

**Funcionalidades**:
- **FIM (File Integrity Monitoring)**:
  - Crear línea base de archivos críticos
  - Verificar integridad y detectar cambios
- **Monitoreo de Procesos**: Análisis de procesos en ejecución
- **Monitoreo de Red**:
  - Detectar conexiones sospechosas
  - Identificar puertos en escucha no autorizados
  - Análisis de tráfico de red

#### 🗂️ Gestión de Registros y Cuarentena
**Propósito**: Administrar archivos en cuarentena y logs del sistema

**Opciones**:
- **Listar Archivos en Cuarentena**: Ver archivos aislados
- **Limpiar Cuarentena Antigua**: Eliminar archivos antiguos por días
- **Exportar Log SIEM**: Generar reportes de eventos del sistema

#### 🛠️ Herramientas del Sistema
**Propósito**: Utilities y herramientas de mantenimiento

**Funcionalidades**:
- **Verificar Herramientas Disponibles**: Comprobar ClamAV y otras tools
- **Actualizar ClamAV**: Actualizar base de datos de firmas
- **Analizar Logs del Sistema**: Revisar logs del sistema operativo

---

## Funcionalidades Principales

### 1. Motor de Escaneo Interno
- **Algoritmo**: Análisis basado en patrones y heurística
- **Detección**: Malware, rootkits, scripts maliciosos
- **Formatos soportados**: Todos los tipos de archivo
- **Velocidad**: Optimizado para análisis rápido

### 2. Integración con ClamAV
- **Requisito**: ClamAV debe estar instalado (`sudo apt install clamav`)
- **Ventaja**: Base de datos actualizada de virus
- **Uso**: Complementa el motor interno

### 3. Sistema SIEM
- **Logging centralizado** de todos los eventos
- **Categorías**: Sistema, GUI, Errores, Amenazas
- **Exportación**: Reportes en formato Markdown
- **Tiempo real**: Eventos registrados instantáneamente

### 4. File Integrity Monitoring (FIM)
- **Línea base**: Snapshot inicial de archivos críticos
- **Monitoreo**: Detección de cambios en tiempo real
- **Algoritmo**: Hashes SHA-256 para verificación
- **Directorios**: `/etc`, `/bin`, `/usr/bin` y personalizados

### 5. Cuarentena Inteligente
- **Aislamiento** automático de archivos peligrosos
- **Metadatos** preservados para análisis forense
- **Limpieza** automática por antigüedad
- **Restauración** selectiva posible

### 6. Monitoreo de Red
- **Conexiones activas**: TCP/UDP en tiempo real
- **Puertos sospechosos**: Detección de servicios no autorizados
- **Procesos**: Identificación de aplicaciones que usan la red
- **Alertas**: Notificaciones de actividad anómala

---

## Configuración Avanzada

### Archivos de Configuración

#### config/firmas/firmas.txt
Contiene las firmas de malware para el motor interno:
```
# Formato: nombre_amenaza:patron_hexadecimal:descripcion
Trojan.Generic:4D5A90000300000004000000FFFF:Executable sospechoso
Malware.Script:3C3F706870:Script PHP malicioso
```

### Variables de Entorno
```bash
export ARES_LOG_LEVEL=DEBUG    # Nivel de logging (DEBUG, INFO, WARNING, ERROR)
export ARES_QUARANTINE_DIR=/var/quarantine  # Directorio de cuarentena personalizado
```

### Configuración de Privilegios
Para uso en entornos de producción, crear un usuario específico:
```bash
sudo useradd -m -s /bin/bash ares-aegis
sudo usermod -aG sudo ares-aegis
```

---

## Solución de Problemas

### Errores Comunes

#### "Requiere privilegios de root"
**Solución**: Ejecutar con `sudo python3 main.py`

#### "No se puede cargar ClamAV"
**Solución**: 
```bash
sudo apt update
sudo apt install clamav clamav-daemon
sudo freshclam
```

#### "Error de importación de módulos"
**Solución**: Verificar que Python 3.8+ esté instalado y reinstalar dependencias
```bash
pip3 install -r requirements.txt --force-reinstall
```

#### "Interfaz gráfica no aparece"
**Solución**: Verificar que X11 esté disponible
```bash
echo $DISPLAY
xhost +local:
```

### Rendimiento

#### Escaneo Lento
- Reducir el tamaño del directorio a escanear
- Usar exclusiones para archivos grandes innecesarios
- Verificar espacio en disco disponible

#### Alto Uso de Memoria
- Limitar el número de archivos escaneados simultáneamente
- Cerrar aplicaciones innecesarias
- Verificar logs para memory leaks

### Logs y Debugging

#### Ubicación de Logs
- **Principal**: `ares_aegis.log` en el directorio del programa
- **Sistema**: `/var/log/syslog` para eventos del sistema

#### Habilitar Debug Mode
```bash
export ARES_LOG_LEVEL=DEBUG
sudo python3 main.py
```

---

## Contacto y Soporte

- **Autor**: DogSoulDev
- **Versión**: 2.0.0
- **Repositorio**: https://github.com/DogSoulDev/Ares-Aegis
- **Licencia**: Open Source

Para reportar bugs o sugerir mejoras, usar el sistema de issues del repositorio GitHub.
