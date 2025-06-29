# Ares Aegis: Antivirus Avanzado para Kali Linux

**Versión:** 3.0.0  
**Autor:** DogSoulDev  
**Licencia:** MIT  
**Plataforma:** Kali Linux (y otras distribuciones basadas en Debian)  
**Arquitectura:** MVC (Modelo-Vista-Controlador)  
**Idioma:** Español (Interfaz 100% localizada)

[![Estado](https://img.shields.io/badge/Estado-Producción-success)](https://github.com/DogSoulDev/Ares-Aegis)
[![Versión](https://img.shields.io/badge/Versión-3.0-blue)](https://github.com/DogSoulDev/Ares-Aegis)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![Arquitectura](https://img.shields.io/badge/Arquitectura-MVC-green)](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
[![Licencia](https://img.shields.io/badge/Licencia-MIT-green)](#)
[![Clean Code](https://img.shields.io/badge/Clean%20Code-✓-brightgreen)](#)
[![TDD](https://img.shields.io/badge/TDD-✓-brightgreen)](#)

---

## Descripción

Ares Aegis es una **suite de ciberseguridad completa y profesional**, diseñada específicamente para entornos Kali Linux y sistemas de seguridad. El proyecto representa un sistema de protección avanzado que combina múltiples motores de detección, análisis dinámico, monitoreo en tiempo real y gestión centralizada de eventos de seguridad.

**Características Distintivas:**
- ✅ **100% Python nativo** - Sin dependencias externas complejas
- ✅ **Arquitectura MVC profesional** - Separación clara de responsabilidades  
- ✅ **Clean Code & SOLID** - Código mantenible y extensible
- ✅ **TDD (Test-Driven Development)** - Cobertura completa de pruebas
- ✅ **Interfaz estilo japonés** - Diseño minimalista y armonioso
- ✅ **SIEM integrado** - Sistema de gestión de eventos centralizado
- ✅ **Múltiples motores de análisis** - Detección multicapa avanzada

El sistema está diseñado siguiendo las mejores prácticas de la industria del software, implementando patrones de diseño robustos (MVC, DRY, SOLID) y metodologías de desarrollo profesional (TDD, Clean Code). Ares Aegis no es solo un antivirus: es una plataforma completa de ciberseguridad.

## Características Principales

### �️ Sistema SIEM Centralizado
- **Gestión Profesional de Eventos:** Sistema SIEM completo para recolección, correlación y análisis de eventos
- **Persistencia Robusta:** Almacenamiento eficiente en JSON con respaldo automático
- **Análisis Temporal:** Filtrado avanzado por fecha, severidad y categorías
- **Exportación Profesional:** Reportes en Markdown con estructura empresarial
- **Dashboard Integrado:** Visualización en tiempo real de eventos de seguridad

### � Motores de Análisis Multicapa
- **Análisis Estático:** Detección por firmas, hashes y patrones conocidos
- **Análisis Dinámico:** Monitoreo de comportamiento y análisis heurístico  
- **Análisis de Cadenas:** Extracción y análisis de strings sospechosos
- **Análisis de Archivos:** Metadatos, estructura y propiedades avanzadas
- **Integración ClamAV:** Motor antivirus externo cuando esté disponible
- **Detección de Vulnerabilidades:** Escaneador especializado en CVEs

### 📊 Monitoreo Integral del Sistema
- **FIM (File Integrity Monitoring):** Detección de cambios no autorizados
- **Monitoreo de Procesos:** Análisis de comportamiento y anomalías
- **Monitoreo de Red:** Supervisión de conexiones y tráfico
- **Análisis de Logs:** Procesamiento inteligente de logs del sistema
- **Detección de Intrusiones:** Identificación de actividades sospechosas

### 🗂️ Gestión Avanzada de Cuarentena
- **Aislamiento Seguro:** Cuarentena con permisos restrictivos (600)
- **Metadatos Completos:** Registro detallado de origen, fecha y motivo
- **Restauración Selectiva:** Recuperación segura de falsos positivos
- **Eliminación Forense:** Borrado seguro con verificación criptográfica

### 🤖 Automatización y Respuesta
- **Automatización de Respuestas:** Acciones automáticas ante detecciones
- **Respuesta a Incidentes:** Flujos de trabajo automatizados
- **Análisis Comportamental:** Detección de patrones anómalos
- **Orquestación de Herramientas:** Integración con herramientas externas

### 🎨 Interfaz Gráfica Profesional
- **Estilo Japonés Minimalista:** Diseño inspirado en la estética wabi-sabi
- **Paleta Natural:** Colores matcha, sakura, bambú y tierra
- **UX/UI Optimizada:** Navegación intuitiva y accesible
- **Localización Completa:** 100% en español castellano
- **Responsive Design:** Adaptable a diferentes resoluciones

## Requisitos del Sistema

### Requisitos Obligatorios
- **Sistema Operativo:** Kali Linux (recomendado) o distribución basada en Debian/Ubuntu
- **Python:** Python 3.8 o superior
- **Privilegios:** Acceso root (sudo) requerido para funciones avanzadas
- **Espacio en Disco:** Mínimo 50 MB libres para instalación y logs

### Dependencias Opcionales
- **ClamAV:** Para funcionalidad de escaneo antivirus externo
- **nmap:** Para escaneo de puertos y servicios de red
- **netstat/ss:** Para monitoreo de conexiones de red
- **lsof:** Para análisis de archivos abiertos

### Nota Importante
Ares Aegis está diseñado para funcionar **exclusivamente con módulos estándar de Python**. No requiere instalación de librerías externas de Python.

## Instalación

### ⚡ Instalación Rápida (Recomendada)

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/DogSoulDev/Ares-Aegis.git
   cd Ares-Aegis
   ```

2. **Ejecutar directamente:**
   ```bash
   # Asegurar permisos de ejecución
   chmod +x main.py
   
   # Ejecutar con privilegios de administrador
   sudo python3 main.py
   ```

3. **Verificar instalación (opcional):**
   ```bash
   # Ejecutar test de integración rápido
   python3 tests/test_final_integracion.py
   ```

### 📦 Instalación con Verificación Completa

```bash
# 1. Clonar y acceder al proyecto
git clone https://github.com/DogSoulDev/Ares-Aegis.git
cd Ares-Aegis

# 2. Verificar requisitos del sistema
python3 --version  # Debe ser 3.8+
which python3      # Verificar ubicación de Python

# 3. Verificar estructura del proyecto
ls -la src/modelos src/vista src/controladores tests/

# 4. Ejecutar suite completa de pruebas
python3 -m unittest discover tests/ -v

# 5. Ejecutar aplicación
sudo python3 main.py
```

### 🔧 Instalación de Dependencias Opcionales

```bash
# ClamAV (Motor antivirus externo - OPCIONAL)
sudo apt-get update
sudo apt-get install clamav clamav-daemon
sudo freshclam  # Actualizar definiciones

# Herramientas de red (OPCIONALES pero recomendadas)
sudo apt-get install nmap netcat-openbsd lsof

# Tkinter (si no está incluido en Python)
sudo apt-get install python3-tk

# Herramientas de desarrollo (para contribuidores)
sudo apt-get install git python3-pip python3-venv
```

## Uso y Navegación

### 🚀 Ejecución del Programa

```bash
# Ejecutar desde el directorio del proyecto
sudo python3 main.py

# O desde el directorio src/
sudo python3 src/main.py

# Verificación de privilegios automática al inicio
```

⚠️ **Importante:** Ares Aegis requiere privilegios de root para acceder a funciones críticas del sistema. El programa verifica automáticamente los privilegios al inicio y mostrará un mensaje de error si no se ejecuta con `sudo`.

### 🎌 Interfaz con Estilo Japonés

La aplicación presenta una interfaz gráfica con **estética japonesa minimalista** organizada en menús intuitivos:

#### Paleta de Colores Implementada
- **🍃 Verde Matcha:** `#8FBC8F` - Elementos principales y botones
- **🌸 Rosa Sakura:** `#FFB6C1` - Acentos y elementos de atención
- **🌤️ Azul Cielo:** `#87CEEB` - Fondos y áreas de contenido
- **🌾 Marrón Cálido:** `#DEB887` - Elementos de navegación
- **🍚 Crema Natural:** `#F5F5DC` - Fondos suaves y paneles

#### Estructura de Navegación

**1. 🔍 Detección y Análisis de Archivos**
```
├── Seleccionar Archivo Individual
├── Escaneo con Motor Interno
├── Escaneo con ClamAV (si está disponible)
├── Análisis de Metadatos y Hashes
├── Extracción de Cadenas de Texto
└── Análisis Dinámico en Sandbox
```

**2. 📊 Monitoreo de Sistema y Procesos**
```
├── Monitor de Integridad de Archivos (FIM)
│   ├── Crear Línea Base
│   ├── Verificar Cambios
│   └── Monitoreo Continuo
├── Monitor de Procesos del Sistema
├── Monitor de Conexiones de Red
├── Análisis de Comportamiento de Procesos
└── Escaneador de Vulnerabilidades
```

**3. 📋 Gestión de Registros y Cuarentena**
```
├── Visualizador de Eventos SIEM
│   ├── Filtrado por Fecha/Tipo/Severidad
│   ├── Búsqueda de Eventos
│   └── Exportación de Reportes
├── Gestor de Cuarentena
│   ├── Listar Archivos en Cuarentena
│   ├── Restaurar Archivos
│   └── Eliminación Permanente
└── Análisis de Logs del Sistema
```

**4. 🛠️ Herramientas y Automatización**
```
├── Automatización de Respuestas
│   ├── Configurar Reglas
│   ├── Acciones Automáticas
│   └── Gestión de Políticas
├── Respondedor de Incidentes
├── Información del Sistema
└── Configuración Avanzada
```

### 📤 Exportación de Reportes

Ares Aegis incluye funcionalidad avanzada de exportación de reportes en **formato Markdown**:

```markdown
# Reporte de Seguridad - Ares Aegis
**Fecha:** 2025-06-29 15:30:45
**Sistema:** Kali Linux

## Resumen Ejecutivo
- Archivos analizados: 1,247
- Amenazas detectadas: 3
- Archivos en cuarentena: 2
- Eventos SIEM registrados: 156

## Detecciones Importantes
### 🚨 Alta Severidad
- **Archivo:** `/tmp/malware_sample.exe`
- **Tipo:** Malware conocido (hash coincidente)
- **Acción:** Movido a cuarentena

## Recomendaciones
1. Revisar archivos en cuarentena
2. Actualizar base de firmas
3. Ejecutar escaneo completo del sistema
```

## Metodología TDD y Testing

### 🧪 Test-Driven Development (TDD)

Ares Aegis implementa **TDD riguroso** para garantizar calidad y confiabilidad:

#### Ciclo TDD Implementado
1. **🔴 RED:** Escribir test que falle para nueva funcionalidad
2. **🟢 GREEN:** Escribir código mínimo para que el test pase  
3. **♻️ REFACTOR:** Mejorar código manteniendo tests pasando
4. **📝 DOCUMENT:** Documentar funcionalidad y casos de uso

### Ejecución de Pruebas

```bash
# Ejecutar toda la suite de pruebas
python3 -m unittest discover tests/ -v

# Ejecutar tests específicos por módulo
python3 -m unittest tests.test_siem -v
python3 -m unittest tests.test_escaneador -v
python3 -m unittest tests.test_analizador_archivos -v

# Ejecutar test de integración completa
python3 tests/test_final_integracion.py

# Ejecutar runner completo con reporte detallado
python3 tests/test_runner_completo.py
```

### 📊 Cobertura de Pruebas Exhaustiva

#### Modelos Core (100% Coverage)
- ✅ **test_siem.py:** Sistema de eventos, persistencia, filtrado, exportación
- ✅ **test_escaneador.py:** Detección por firmas, hashes, análisis de archivos
- ✅ **test_analizador_archivos.py:** Metadatos, cálculo de hashes, propiedades
- ✅ **test_analizador_cadenas.py:** Extracción de strings, filtrado por longitud
- ✅ **test_analizador_logs.py:** Procesamiento de logs, detección de patrones
- ✅ **test_monitor_red.py:** Conexiones activas, resolución de procesos
- ✅ **test_monitor_procesos.py:** Información de procesos, filtrado, búsqueda
- ✅ **test_escaneador_vulnerabilidades.py:** Detección de CVEs, configuraciones

#### Tests de Integración
- ✅ **test_integration_gui.py:** Integración completa GUI-Modelos
- ✅ **test_final_integracion.py:** Verificación arquitectura MVC completa

#### Técnicas de Testing Implementadas
- **🎭 Mocking:** Simulación de recursos del sistema para tests aislados
- **📁 Archivos Temporales:** Tests seguros sin afectar sistema anfitrión
- **🔄 Setup/Teardown:** Limpieza automática después de cada test
- **🚫 No Root Required:** Tests ejecutables sin privilegios administrativos

### Configuración y Archivos

#### 📁 Configuración del Sistema

**`config/firmas.txt` - Base de Datos de Firmas**
```bash
# Firmas de texto simple (malware conocido)
eval(base64_decode
system($_GET
<script>alert
<?php system($_POST

# Hashes SHA256 de archivos maliciosos
HASH:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
HASH:a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3

# Expresiones regulares para detección avanzada
REGEX:eval\\s*\\(\\s*base64_decode
REGEX:<script[^>]*>.*alert.*</script>
REGEX:system\\s*\\(\\s*\\$_(GET|POST|REQUEST)
```

#### 📍 Ubicaciones de Archivos

**Modo Desarrollo:**
```bash
~/.ares_aegis/
├── config/
│   └── firmas.txt              # Firmas personalizadas
├── logs/
│   └── ares_aegis.log         # Logs de aplicación
├── cuarentena/                # Archivos en cuarentena
└── siem_events.json          # Base de datos SIEM
```

**Modo Producción (instalación .deb):**
```bash
/etc/ares_aegis/              # Configuración sistema
/var/log/ares_aegis/          # Logs del sistema  
/var/ares_aegis_cuarentena/   # Cuarentena sistema
/var/lib/ares_aegis/          # Datos persistentes
/usr/share/ares_aegis/        # Recursos gráficos
```

## Arquitectura del Proyecto

### Estructura de Directorios

```
Ares-Aegis/
├── main.py                          # Punto de entrada principal
├── README.md                        # Documentación principal (este archivo)
├── requirements.txt                 # Dependencias vacías (solo módulos estándar)
├── .gitignore                      # Control de versiones
├── src/                            # Código fuente principal (Arquitectura MVC)
│   ├── __init__.py
│   ├── main.py                     # Launcher interno de la aplicación
│   ├── modelos/                    # MODELOS - Lógica de negocio pura
│   │   ├── __init__.py
│   │   ├── siem.py                 # Sistema de gestión de eventos centralizado
│   │   ├── escaneador.py           # Motor de escaneo de archivos y firmas
│   │   ├── fim.py                  # Monitoreo de integridad de archivos (FIM)
│   │   ├── cuarentena.py          # Gestión de cuarentena de archivos
│   │   ├── integracion_externa.py # Integración con herramientas externas
│   │   ├── analizador_archivos.py # Análisis de metadatos y hashes
│   │   ├── analizador_cadenas.py  # Extracción de strings de archivos
│   │   ├── analizador_logs.py     # Análisis de logs del sistema
│   │   ├── analizador_dinamico.py # Mini-sandbox para análisis dinámico
│   │   ├── analizador_comportamiento_procesos.py # Detección de anomalías
│   │   ├── escaneador_vulnerabilidades.py # Scanner de vulnerabilidades
│   │   ├── monitor_red.py         # Monitoreo de conexiones de red
│   │   ├── monitor_procesos.py    # Monitoreo de procesos del sistema
│   │   ├── monitor_integridad.py  # Monitor de integridad avanzado
│   │   ├── automatizacion_respuesta.py # Automatización de respuestas
│   │   └── respondedor_incidentes.py   # Respuesta directa a incidentes
│   ├── vista/                     # VISTA - Interfaz gráfica de usuario
│   │   ├── __init__.py
│   │   └── interfaz_principal_gui.py # GUI principal con estilo japonés
│   └── controladores/             # CONTROLADORES - Lógica de control
│       ├── __init__.py
│       └── controlador_principal.py # Controlador principal MVC
├── tests/                         # Suite de pruebas TDD
│   ├── __init__.py
│   ├── test_siem.py              # Tests del sistema SIEM
│   ├── test_escaneador.py        # Tests del motor de escaneo
│   ├── test_analizador_archivos.py # Tests del analizador de archivos
│   ├── test_analizador_cadenas.py  # Tests del analizador de strings
│   ├── test_analizador_logs.py     # Tests del analizador de logs
│   ├── test_monitor_red.py         # Tests del monitor de red
│   ├── test_monitor_procesos.py    # Tests del monitor de procesos
│   ├── test_escaneador_vulnerabilidades.py # Tests del scanner de CVEs
│   ├── test_integration_gui.py     # Tests de integración GUI
│   ├── test_final_integracion.py   # Test final de integración completa
│   └── test_runner_completo.py     # Runner para toda la suite de tests
├── config/                        # Configuración del sistema
│   └── firmas.txt                # Base de datos de firmas de malware
├── docs/                         # Documentación del proyecto
│   ├── manuales/                 # Manuales técnicos y de usuario
│   │   └── README_DOCUMENTACION.md # Documentación técnica adicional
│   └── reportes/                 # Reportes de estado del proyecto
└── recursos/                     # Recursos gráficos y estáticos
    ├── README.md                 # Información sobre recursos
    ├── aresIcon.png             # Icono principal (convertir a PPM/GIF)
    └── Ares.jpeg               # Imagen de marca (convertir a PPM/GIF)
```

### Principios de Arquitectura MVC

#### Separación de Responsabilidades
- **Modelos (`src/modelos/`):** Contienen toda la lógica de negocio, manipulación de datos y funcionalidades core del sistema de ciberseguridad. Son completamente independientes de la interfaz gráfica.
- **Vista (`src/vista/`):** Maneja exclusivamente la presentación e interfaz de usuario con tkinter. No contiene lógica de negocio.
- **Controladores (`src/controladores/`):** Coordinan las interacciones entre la Vista y los Modelos, validando entradas y orquestando operaciones.

#### Inyección de Dependencias
El sistema implementa DIP (Dependency Inversion Principle) mediante inyección de dependencias:
```python
# Los controladores reciben instancias de modelos, no los crean internamente
controlador = ControladorPrincipal(
    siem=SIEM(),
    escaneador=Escaneador(),
    monitor_red=MonitorRed(),
    # ... otros modelos
)
```

#### Principios SOLID Implementados
- **SRP (Single Responsibility Principle):** Cada módulo tiene una responsabilidad única y bien definida
- **OCP (Open/Closed Principle):** Extensible sin modificar código existente mediante configuración y abstracciones
- **LSP (Liskov Substitution Principle):** Herencia correcta cuando es aplicable
- **ISP (Interface Segregation Principle):** Interfaces pequeñas y específicas para cada cliente
- **DIP (Dependency Inversion Principle):** Inyección de dependencias en lugar de instanciación directa

#### Clean Code y TDD
- **Nombres Descriptivos:** Variables, funciones y clases autoexplicativas en español
- **Funciones Pequeñas:** Cada función cumple una única responsabilidad
- **Test-Driven Development:** Pruebas unitarias exhaustivas para cada módulo
- **Documentación Integrada:** Docstrings en español para toda función pública
- **Manejo Robusto de Errores:** Gestión granular de excepciones con logging

## Requisitos del Sistema

### ⚙️ Requisitos Obligatorios
- **Sistema Operativo:** Kali Linux (recomendado) o distribución Debian/Ubuntu
- **Python:** Python 3.8 o superior (solo módulos estándar)
- **Privilegios:** Acceso root/sudo (verificado automáticamente al inicio)
- **Memoria RAM:** Mínimo 512 MB disponibles
- **Espacio en Disco:** 100 MB libres para instalación, logs y cuarentena
- **Interfaz Gráfica:** X11 o Wayland para GUI con tkinter

### 🔧 Dependencias del Sistema (Opcionales)
```bash
# Herramientas de análisis externo (OPCIONALES)
sudo apt-get update
sudo apt-get install -y \
    clamav clamav-daemon \    # Motor antivirus externo
    nmap \                    # Escaneo de puertos y servicios
    netcat-openbsd \         # Herramientas de red
    lsof \                   # Análisis de archivos abiertos
    ss \                     # Estadísticas de socket
    python3-tk               # Tkinter (si no está incluido)
```

### 📋 Nota Importante sobre Dependencias
**Ares Aegis está diseñado para funcionar exclusivamente con módulos estándar de Python.** No requiere instalación de librerías externas de Python (`pip install`). Las herramientas opcionales del sistema mejoran las capacidades pero no son esenciales para el funcionamiento básico.

## Características Técnicas Avanzadas

### 🎨 Sistema de Estilizado Japonés

La interfaz implementa una **filosofía de diseño wabi-sabi** (belleza en la imperfección y simplicidad):

```python
# Paleta de colores implementada en la GUI
COLORES_JAPONESES = {
    'fondo_principal': '#F5F5DC',      # Crema natural (papel de arroz)
    'verde_matcha': '#8FBC8F',         # Verde suave principal
    'rosa_sakura': '#FFB6C1',          # Rosa delicado para acentos
    'azul_cielo': '#87CEEB',           # Azul suave para áreas de contenido
    'marron_calido': '#DEB887',        # Marrón tierra para navegación
    'texto_principal': '#2F4F4F',      # Gris oscuro para legibilidad
    'bordes_sutiles': '#D3D3D3'        # Gris claro para separadores
}
```

**Principios de Diseño:**
- ✨ **Minimalismo:** Espacios en blanco, elementos simples
- 🌱 **Naturaleza:** Colores inspirados en elementos naturales
- ⚖️ **Equilibrio:** Composición armoniosa sin elementos estridentes
- 🧘 **Serenidad:** Interfaz que transmite calma y concentración

### 🔒 Sistema SIEM Centralizado

**Arquitectura del SIEM:**
```python
# Estructura de eventos SIEM
{
    "timestamp": "2025-06-29T15:30:45.123456",
    "tipo": "DETECCION_MALWARE",
    "severidad": "CRITICA",
    "origen": "EscaneadorArchivos",
    "mensaje": "Malware detectado en archivo sospechoso",
    "detalles": {
        "archivo": "/tmp/malware.exe",
        "hash_sha256": "e3b0c44298fc...",
        "firma_coincidente": "eval(base64_decode",
        "accion_tomada": "CUARENTENA"
    },
    "host": "kali-linux",
    "usuario": "root"
}
```

**Capacidades SIEM:**
- 📊 **Correlación de Eventos:** Análisis de patrones temporales
- 🔍 **Filtrado Avanzado:** Por tipo, severidad, origen y fechas
- 📈 **Análisis Temporal:** Detección de tendencias y anomalías
- 💾 **Persistencia Robusta:** Almacenamiento JSON con respaldo automático
- 📋 **Exportación Profesional:** Reportes en Markdown estructurado

### 🛡️ Motores de Detección Multicapa

**1. Motor de Firmas Estáticas**
```python
# Tipos de firmas soportadas
TIPOS_FIRMAS = {
    'TEXTO_SIMPLE': 'Cadenas de texto conocidas',
    'HASH_SHA256': 'Hashes criptográficos de archivos maliciosos', 
    'REGEX': 'Expresiones regulares complejas',
    'YARA_RULES': 'Reglas YARA (desarrollo futuro)'
}
```

**2. Motor de Análisis Heurístico**
- 🔍 Detección de patrones sospechosos en código
- 📊 Análisis de entropía de archivos
- 🚩 Identificación de técnicas de ofuscación
- ⚡ Detección de comportamientos anómalos

**3. Motor de Análisis Dinámico**
```python
# Capacidades del sandbox interno
SANDBOX_FEATURES = {
    'aislamiento_temporal': 'Ejecución limitada en tiempo',
    'captura_salida': 'Stdout/stderr/códigos de salida',
    'monitoreo_basico': 'Detección de actividades sospechosas',
    'recursos_limitados': 'Restricciones de CPU/memoria básicas'
}
```

### 🌐 Monitoreo Integral de Red

**Capacidades de Monitoreo:**
```python
# Fuentes de información de red monitoreadas
FUENTES_RED = {
    '/proc/net/tcp': 'Conexiones TCP activas',
    '/proc/net/udp': 'Conexiones UDP activas', 
    '/proc/net/unix': 'Sockets UNIX',
    'comando_ss': 'Estadísticas avanzadas de sockets',
    'comando_netstat': 'Estado de conexiones de red'
}
```

**Detección de Anomalías:**
- 🚨 Conexiones a IPs/puertos sospechosos
- 📡 Tráfico inusual en protocolos específicos
- 🔗 Procesos con conexiones inesperadas
- 📈 Análisis de volumen de tráfico

## Preparación para Distribución (.deb)

### 📦 Estructura para Empaquetado Debian

Ares Aegis está preparado para distribución como paquete `.deb` profesional:

```bash
# Estructura de instalación planificada
/usr/local/bin/ares-aegis           # Ejecutable principal
/etc/ares_aegis/                    # Configuración del sistema
├── firmas.txt                      # Base de firmas de malware
├── siem_config.json               # Configuración SIEM
└── automatizacion_rules.json      # Reglas de automatización

/var/log/ares_aegis/                # Logs del sistema
├── ares_aegis.log                 # Log principal
├── siem_events.json              # Base de datos SIEM
└── audit.log                     # Log de auditoría

/var/ares_aegis_cuarentena/         # Directorio de cuarentena
├── archivos/                      # Archivos en cuarentena
└── metadatos/                     # Metadatos de cuarentena

/usr/share/ares_aegis/              # Recursos del programa
├── recursos/                      # Iconos e imágenes
│   ├── aresIcon.ppm              # Icono (formato tkinter)
│   └── Ares.ppm                  # Imagen de marca
└── docs/                         # Documentación
    ├── manual_usuario.md
    └── manual_tecnico.md

/lib/systemd/system/                # Servicios del sistema
└── ares-aegis-monitor.service     # Servicio de monitoreo (futuro)
```

### 🔧 Scripts de Instalación

**Pre-instalación:**
```bash
#!/bin/bash
# debian/preinst
# Verificar requisitos del sistema
# Crear usuarios y grupos necesarios
# Preparar directorios base
```

**Post-instalación:**
```bash
#!/bin/bash  
# debian/postinst
# Configurar permisos de archivos
# Inicializar base de datos SIEM
# Registrar servicio en systemd (futuro)
# Mostrar mensaje de bienvenida
```

**Pre-eliminación:**
```bash
#!/bin/bash
# debian/prerm  
# Detener servicios en ejecución
# Respaldar configuración del usuario
# Notificar al usuario sobre datos persistentes
```

### 📋 Metadatos del Paquete

```bash
# debian/control
Package: ares-aegis
Version: 3.0.0
Section: security
Priority: optional
Architecture: all
Depends: python3 (>= 3.8), python3-tk
Recommends: clamav, nmap, lsof
Suggests: clamav-daemon, netcat-openbsd
Maintainer: DogSoulDev <dogsouldev@example.com>
Description: Suite de ciberseguridad avanzada para Kali Linux
 Ares Aegis es una suite completa de ciberseguridad que incluye:
 - Sistema SIEM centralizado
 - Múltiples motores de detección
 - Monitoreo integral del sistema  
 - Interfaz gráfica con estilo japonés
 - Arquitectura MVC profesional
Homepage: https://github.com/DogSoulDev/Ares-Aegis
```

## Seguridad y Consideraciones Técnicas

### 🔐 Modelo de Seguridad Implementado

#### Verificación de Privilegios
```python
# Verificación automática al inicio
def verificar_privilegios_root():
    """Verifica que el programa se ejecute con privilegios de administrador"""
    if os.geteuid() != 0:
        mensaje = "⚠️ ARES AEGIS REQUIERE PRIVILEGIOS DE ROOT\n\n"
        mensaje += "Ejecute el programa con sudo:\n"
        mensaje += "sudo python3 main.py"
        
        messagebox.showerror("Privilegios Insuficientes", mensaje)
        print(f"ERROR: {mensaje}")
        sys.exit(1)
```

#### Principio de Menor Privilegio
- ✅ **Verificación Granular:** Solo solicita permisos específicos cuando son necesarios
- ✅ **Validación de Rutas:** Verificación de permisos antes de operaciones críticas  
- ✅ **Manejo Seguro de Archivos:** Validación de rutas y tipos de archivo
- ✅ **Cuarentena Restrictiva:** Archivos en cuarentena con permisos 600 (solo propietario)

#### Validación de Entrada Robusta
```python
# Ejemplo de validación implementada
def validar_ruta_archivo(ruta):
    """Valida rutas de archivo para prevenir ataques de path traversal"""
    try:
        ruta_absoluta = os.path.abspath(ruta)
        if not os.path.exists(ruta_absoluta):
            raise FileNotFoundError(f"Archivo no encontrado: {ruta}")
        if not os.path.isfile(ruta_absoluta):
            raise ValueError(f"La ruta no corresponde a un archivo: {ruta}")
        return ruta_absoluta
    except Exception as e:
        logging.error(f"Error validando ruta: {e}")
        raise
```

### 🛡️ Buenas Prácticas de Seguridad

#### Manejo Seguro de Comandos Externos
```python
# Ejecución segura de comandos del sistema
def ejecutar_comando_seguro(comando, argumentos=[]):
    """Ejecuta comandos externos de forma segura con validación"""
    comandos_permitidos = ['clamscan', 'nmap', 'ss', 'netstat', 'lsof']
    
    if comando not in comandos_permitidos:
        raise ValueError(f"Comando no permitido: {comando}")
    
    # Sanitización de argumentos
    argumentos_seguros = [arg for arg in argumentos if re.match(r'^[a-zA-Z0-9\-_./]+$', arg)]
    
    try:
        resultado = subprocess.run(
            [comando] + argumentos_seguros,
            capture_output=True,
            text=True,
            timeout=30,  # Timeout para prevenir bloqueos
            check=False
        )
        return resultado
    except subprocess.TimeoutExpired:
        logging.warning(f"Timeout ejecutando comando: {comando}")
        raise
```

#### Gestión de Cuarentena Forense
```python
# Metadatos de cuarentena para auditoría forense
METADATOS_CUARENTENA = {
    'timestamp_cuarentena': '2025-06-29T15:30:45.123456',
    'ruta_original': '/tmp/archivo_sospechoso.exe',
    'hash_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    'hash_md5': '098f6bcd4621d373cade4e832627b4f6', 
    'tamaño_bytes': 1024,
    'motivo_cuarentena': 'Firma de malware coincidente: eval(base64_decode',
    'usuario_sistema': 'root',
    'permisos_originales': '755',
    'propietario_original': 'usuario:grupo'
}
```

## Solución de Problemas y FAQ

### 🚨 Problemas Comunes y Soluciones

#### Error: "Permission denied" al iniciar
```bash
# Problema: Falta de privilegios de root
# Síntoma: Mensaje de error y cierre automático del programa

# Solución:
sudo python3 main.py

# Verificación de permisos:
whoami  # Debe mostrar 'root' cuando se ejecuta con sudo
```

#### Error: "Module 'tkinter' not found"
```bash
# Problema: tkinter no está instalado en el sistema
# Síntoma: ImportError al importar tkinter

# Solución en Debian/Ubuntu/Kali:
sudo apt-get update
sudo apt-get install python3-tk

# Verificación de instalación:
python3 -c "import tkinter; print('tkinter OK')"
```

#### Error: "ClamAV not found" 
```bash
# Problema: ClamAV no está instalado (es opcional)
# Síntoma: Funcionalidad de escaneo ClamAV no disponible

# Solución (opcional):
sudo apt-get install clamav clamav-daemon
sudo freshclam  # Actualizar definiciones de virus

# Verificación:
clamscan --version
```

#### Interfaz gráfica no se muestra
```bash
# Problema: No hay servidor X11 disponible
# Síntoma: Error "cannot connect to X server"

# Solución para SSH:
ssh -X usuario@servidor  # Habilitar X11 forwarding

# Solución para contenedores:
xhost +local:  # Permitir conexiones X11 locales

# Verificación:
echo $DISPLAY  # Debe mostrar ":0" o similar
```

### 🔧 Diagnóstico del Sistema

#### Script de Verificación Automática
```bash
# Crear script de diagnóstico
cat > verificar_sistema.sh << 'EOF'
#!/bin/bash
echo "=== DIAGNÓSTICO ARES AEGIS ==="
echo "Fecha: $(date)"
echo

echo "1. Verificando Python..."
python3 --version || echo "❌ Python3 no encontrado"

echo "2. Verificando tkinter..."
python3 -c "import tkinter" 2>/dev/null && echo "✅ tkinter OK" || echo "❌ tkinter no disponible"

echo "3. Verificando privilegios..."
[ "$EUID" -eq 0 ] && echo "✅ Ejecutando como root" || echo "⚠️ Requiere sudo"

echo "4. Verificando X11..."
[ -n "$DISPLAY" ] && echo "✅ X11 disponible" || echo "❌ X11 no configurado"

echo "5. Verificando herramientas opcionales..."
which clamscan >/dev/null 2>&1 && echo "✅ ClamAV disponible" || echo "⚠️ ClamAV no instalado (opcional)"
which nmap >/dev/null 2>&1 && echo "✅ nmap disponible" || echo "⚠️ nmap no instalado (opcional)"

echo
echo "=== FIN DIAGNÓSTICO ==="
EOF

chmod +x verificar_sistema.sh
sudo ./verificar_sistema.sh
```

### 📋 Logs de Diagnóstico

#### Ubicaciones de Logs por Contexto
```bash
# Modo desarrollo
~/.ares_aegis/ares_aegis.log          # Log principal de aplicación
~/.ares_aegis/siem_events.json        # Eventos del SIEM
~/.ares_aegis/debug.log               # Logs de depuración

# Modo producción (instalación .deb)
/var/log/ares_aegis/ares_aegis.log    # Log del sistema
/var/log/ares_aegis/audit.log         # Log de auditoría
/var/log/ares_aegis/errors.log        # Solo errores críticos
```

#### Análisis de Logs en Tiempo Real
```bash
# Monitoreo de logs en tiempo real
tail -f ~/.ares_aegis/ares_aegis.log

# Filtrar solo errores
grep "ERROR\|CRITICAL" ~/.ares_aegis/ares_aegis.log

# Filtrar eventos SIEM por tipo
jq '.[] | select(.tipo=="DETECCION_MALWARE")' ~/.ares_aegis/siem_events.json
```

### 📞 Soporte y Recursos de Ayuda

#### Canales de Soporte
- 📚 **Documentación:** Este README.md y docs/manuales/
- 🐛 **Issues de GitHub:** Para reportar bugs y solicitar funcionalidades
- 💬 **Discusiones:** Para preguntas generales y ayuda técnica
- 📖 **Wiki:** Documentación adicional y tutoriales (próximamente)

#### Información para Reportar Bugs
Al reportar un problema, incluye:
```bash
# Información del sistema
uname -a                    # Versión del kernel
python3 --version          # Versión de Python
cat /etc/os-release        # Distribución Linux

# Logs relevantes (últimas 20 líneas)
tail -20 ~/.ares_aegis/ares_aegis.log

# Comando exacto que causó el error
sudo python3 main.py       # Comando utilizado

# Mensaje de error completo (captura de pantalla si es GUI)
```

## Desarrollo y Contribución

### 🚀 Configuración del Entorno de Desarrollo

#### Preparación Inicial
```bash
# 1. Clonar repositorio y configurar rama de desarrollo
git clone https://github.com/DogSoulDev/Ares-Aegis.git
cd Ares-Aegis

# 2. Crear rama para nueva funcionalidad
git checkout -b feature/nueva-funcionalidad

# 3. Verificar estructura del proyecto MVC
tree src/
├── modelos/           # Lógica de negocio
├── vista/             # Interfaz gráfica  
└── controladores/     # Coordinación MVC
```

#### Flujo de Desarrollo TDD
```bash
# 1. Ejecutar tests existentes (deben pasar todos)
python3 -m unittest discover tests/ -v

# 2. Escribir test para nueva funcionalidad (debe fallar)
cat > tests/test_nueva_funcionalidad.py << 'EOF'
import unittest
from src.modelos.nueva_funcionalidad import NuevaFuncionalidad

class TestNuevaFuncionalidad(unittest.TestCase):
    def test_nueva_funcion_debe_retornar_resultado_esperado(self):
        # Arrange
        nueva_funcionalidad = NuevaFuncionalidad()
        
        # Act
        resultado = nueva_funcionalidad.nueva_funcion()
        
        # Assert
        self.assertEqual(resultado, "resultado_esperado")
EOF

# 3. Ejecutar test (debe fallar - RED)
python3 -m unittest tests.test_nueva_funcionalidad -v

# 4. Implementar código mínimo para pasar test (GREEN)
# Editar src/modelos/nueva_funcionalidad.py

# 5. Refactorizar manteniendo tests pasando (REFACTOR)
# Mejorar código sin cambiar funcionalidad

# 6. Verificar que todos los tests siguen pasando
python3 -m unittest discover tests/ -v
```

### 📋 Estándares de Código Obligatorios

#### Convenciones de Nomenclatura (Español)
```python
# ✅ CORRECTO - Todo en español
class GestorCuarentena:
    def __init__(self):
        self.archivos_en_cuarentena = []
        self.directorio_cuarentena = "/var/ares_aegis_cuarentena"
    
    def poner_archivo_en_cuarentena(self, ruta_archivo):
        """Mueve un archivo sospechoso al directorio de cuarentena"""
        pass
    
    def restaurar_archivo_de_cuarentena(self, id_archivo):
        """Restaura un archivo de la cuarentena a su ubicación original"""
        pass

# ❌ INCORRECTO - Mezcla de idiomas
class QuarantineManager:
    def __init__(self):
        self.quarantined_files = []  # Inglés
        self.directorio_cuarentena = ""  # Español mezclado
```

#### Documentación Obligatoria
```python
def analizar_archivo_con_firmas(self, ruta_archivo: str, firmas: list) -> dict:
    """
    Analiza un archivo contra una base de datos de firmas de malware.
    
    Parámetros:
        ruta_archivo (str): Ruta absoluta al archivo a analizar
        firmas (list): Lista de firmas de malware a verificar
    
    Retorna:
        dict: Resultado del análisis con las siguientes claves:
            - 'es_malicioso' (bool): True si se detectó malware
            - 'firmas_coincidentes' (list): Lista de firmas que coincidieron
            - 'hash_sha256' (str): Hash SHA256 del archivo
            - 'tamaño_bytes' (int): Tamaño del archivo en bytes
    
    Levanta:
        FileNotFoundError: Si el archivo no existe
        PermissionError: Si no hay permisos para leer el archivo
        ValueError: Si la ruta no es válida
    
    Ejemplo:
        >>> analizador = AnalizadorArchivos()
        >>> resultado = analizador.analizar_archivo_con_firmas(
        ...     "/tmp/archivo_sospechoso.exe", 
        ...     ["eval(base64_decode", "system($_GET"]
        ... )
        >>> print(resultado['es_malicioso'])
        True
    """
    pass
```

#### Principios SOLID en Práctica
```python
# SRP - Cada clase tiene una responsabilidad única
class CalculadorHashes:
    """Se encarga únicamente del cálculo de hashes criptográficos"""
    
    def calcular_sha256(self, ruta_archivo: str) -> str:
        pass
    
    def calcular_md5(self, ruta_archivo: str) -> str:
        pass

class ValidadorArchivos:
    """Se encarga únicamente de validar archivos"""
    
    def validar_existe(self, ruta_archivo: str) -> bool:
        pass
    
    def validar_permisos_lectura(self, ruta_archivo: str) -> bool:
        pass

# DIP - Inyección de dependencias
class AnalizadorArchivos:
    def __init__(self, calculador_hashes: CalculadorHashes, 
                 validador: ValidadorArchivos):
        self.calculador_hashes = calculador_hashes
        self.validador = validador
```

### 🔄 Proceso de Contribución

#### 1. Preparación de Contribución
```bash
# Fork del repositorio en GitHub
# Clonar tu fork localmente
git clone https://github.com/TU_USUARIO/Ares-Aegis.git
cd Ares-Aegis

# Añadir repositorio original como upstream
git remote add upstream https://github.com/DogSoulDev/Ares-Aegis.git

# Crear rama para tu contribución
git checkout -b feature/descripcion-funcionalidad
```

#### 2. Desarrollo con TDD
```bash
# Escribir tests primero
# Implementar funcionalidad mínima
# Refactorizar código
# Asegurar que todos los tests pasen

python3 tests/test_final_integracion.py  # Test de integración completa
```

#### 3. Commit y Pull Request
```bash
# Commit siguiendo convenciones
git add .
git commit -m "feat: Agregar funcionalidad de análisis dinámico

- Implementar sandbox básico para ejecución controlada
- Añadir captura de stdout/stderr
- Incluir limitaciones de tiempo de ejecución
- Tests unitarios completos para todas las funciones"

# Push a tu fork
git push origin feature/descripcion-funcionalidad

# Crear Pull Request en GitHub con:
# - Descripción detallada de cambios
# - Screenshots de GUI si aplica
# - Resultados de tests
# - Documentación actualizada
```

## Roadmap de Desarrollo

### 🎯 Versión 3.1 (Q3 2025)
**Análisis Avanzado y Machine Learning**
- [ ] **Motor YARA:** Integración completa con reglas YARA personalizadas
- [ ] **Análisis de Entropía:** Detección de archivos empaquetados/ofuscados
- [ ] **ML Básico:** Algoritmos simples de detección de anomalías
- [ ] **Análisis de PE:** Parsing de headers PE para ejecutables Windows
- [ ] **Dashboard Mejorado:** Visualizaciones gráficas de eventos SIEM

### 🚀 Versión 3.2 (Q4 2025)  
**Integración Empresarial**
- [ ] **API REST:** Endpoints para automatización e integración externa
- [ ] **Base de Datos:** Soporte para PostgreSQL/SQLite además de JSON
- [ ] **Threat Intelligence:** Integración con feeds de inteligencia pública
- [ ] **Multi-idioma:** Soporte para inglés y otros idiomas
- [ ] **Configuración Avanzada:** Panel de configuración completo en GUI

### 🌟 Versión 4.0 (Q1 2026)
**Plataforma de Seguridad Completa**
- [ ] **Interfaz Web:** Dashboard web opcional para monitoreo remoto
- [ ] **Análisis Forense:** Herramientas básicas de análisis forense
- [ ] **Sandbox Avanzado:** Análisis dinámico con virtualización
- [ ] **Integración SIEM Externa:** Conectores para Splunk, ELK, QRadar
- [ ] **Mobile App:** Aplicación móvil para notificaciones y monitoreo

### 💡 Ideas de la Comunidad (Backlog)
- [ ] **Plugin System:** Arquitectura de plugins para extensibilidad
- [ ] **Distribución Docker:** Contenedor oficial multi-arquitectura
- [ ] **Cloud Integration:** Análisis en la nube con APIs públicas
- [ ] **Enterprise Features:** Multi-tenant, RBAC, auditoría avanzada
- [ ] **IoC Sharing:** Compartir indicadores de compromiso con la comunidad

## Recursos y Soporte

### 📚 Documentación Técnica
- **README Principal:** Este archivo con información completa
- **Docs Técnicos:** `docs/manuales/` para guías especializadas
- **Código Autodocumentado:** Docstrings en español en todo el código
- **Tests como Documentación:** Los tests sirven como ejemplos de uso

### 🐛 Canales de Soporte

#### Para Usuarios
- **GitHub Issues:** Reportar bugs y solicitar funcionalidades
- **GitHub Discussions:** Preguntas generales y ayuda de uso
- **Wiki (próximamente):** Tutoriales paso a paso y casos de uso

#### Para Desarrolladores  
- **Código Fuente:** Comentarios detallados en español
- **Architecture Decision Records:** Decisiones de diseño documentadas
- **Contributing Guidelines:** Guías específicas para contribuidores

### 📞 Contacto y Comunidad

**Desarrollador Principal:**
- **GitHub:** [@DogSoulDev](https://github.com/DogSoulDev)
- **Proyecto:** [Ares-Aegis Repository](https://github.com/DogSoulDev/Ares-Aegis)

**Repositorio Oficial:**
- **URL:** https://github.com/DogSoulDev/Ares-Aegis
- **Issues:** https://github.com/DogSoulDev/Ares-Aegis/issues
- **Releases:** https://github.com/DogSoulDev/Ares-Aegis/releases

### ⚠️ Problemas Conocidos y Limitaciones

#### Limitaciones Técnicas Actuales
- **Formato de Imágenes:** tkinter requiere conversión a PPM/GIF para `aresIcon.png` y `Ares.jpeg`
- **Dependencia de Root:** Funciones avanzadas requieren privilegios administrativos
- **Python Estándar:** Limitado a módulos incorporados (no pip install)
- **Plataforma:** Optimizado para Kali Linux (compatibilidad limitada en otros OS)

#### Soluciones en Desarrollo
```bash
# Conversión de imágenes para tkinter (manual requerido)
convert aresIcon.png aresIcon.ppm    # Requiere ImageMagick
convert Ares.jpeg Ares.ppm          # O usar herramientas online
```

## Licencia y Créditos

### 📄 Licencia MIT

Este proyecto está licenciado bajo la **Licencia MIT** - consulta el archivo [LICENSE](LICENSE) para detalles completos.

```
MIT License

Copyright (c) 2025 DogSoulDev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 🏆 Reconocimientos

**Desarrollado completamente por [DogSoulDev](https://github.com/DogSoulDev)**

**Principios de Desarrollo:**
- ✨ **Clean Code** - Código limpio, legible y mantenible
- 🏗️ **SOLID Principles** - Arquitectura sólida y extensible  
- 🧪 **Test-Driven Development** - Calidad garantizada por tests
- 🎨 **Japanese Aesthetic** - Diseño minimalista y armonioso
- 🔒 **Security by Design** - Seguridad integrada desde el diseño

**Inspiraciones:**
- 🇯🇵 **Filosofía Japonesa:** Wabi-sabi, minimalismo, armonía natural
- 🛡️ **Ciberseguridad:** NIST Framework, OWASP, SANS Institute
- 💻 **Clean Code:** Robert C. Martin, Martin Fowler, Kent Beck
- 🏛️ **Arquitectura:** Domain-Driven Design, MVC, Hexagonal Architecture

---

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-DogSoulDev%2FAres--Aegis-black?logo=github&style=for-the-badge)](https://github.com/DogSoulDev/Ares-Aegis)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&style=for-the-badge)](https://python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://choosealicense.com/licenses/mit/)
[![TDD](https://img.shields.io/badge/TDD-Test%20Driven-brightgreen?style=for-the-badge)](#)
[![MVC](https://img.shields.io/badge/Architecture-MVC-orange?style=for-the-badge)](#)

### 🛡️ **ARES AEGIS** 🛡️
*Protección Avanzada con Arquitectura Limpia y Estética Japonesa*

**"Seguridad que trasciende código - Arte que protege sistemas"**

---

**© 2025 DogSoulDev | Desarrollado con ❤️ para la comunidad de ciberseguridad**

</div>
