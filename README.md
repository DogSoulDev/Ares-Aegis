# 🛡️ Ares Aegis - Sistema Antivirus y SIEM

**Versión 2.0.0** | **Autor: DogSoulDev** | **Fecha: Julio 2025**

## 📋 Descripción

Ares Aegis es un sistema antivirus y SIEM (Security Information and Event Management) completo desarrollado en Python. Inspirado en la mitología griega y con una estética japonesa, combina la potencia de detección de malware con capacidades avanzadas de monitoreo de seguridad.

## ✨ Características Principales

### 🔍 Sistema de Escaneado
- **Detección de malware** basada en firmas
- **Escaneo múltiple** de archivos y directorios
- **Más de 80 firmas** de amenazas conocidas
- **Soporte para múltiples tipos** de malware: virus, troyanos, ransomware, cryptominers

### 🛡️ SIEM Integrado
- **Registro centralizado** de eventos de seguridad
- **Búsqueda y filtrado** avanzado de eventos
- **Rotación automática** de logs
- **Exportación de reportes** en formato Markdown

### 🗂️ Sistema de Cuarentena
- **Aislamiento seguro** de archivos infectados
- **Compresión automática** con contraseña
- **Restauración controlada** de archivos
- **Gestión completa** del ciclo de vida

### 📁 Monitor de Integridad (FIM)
- **Monitoreo en tiempo real** de cambios en archivos
- **Creación de líneas base** de integridad
- **Detección de modificaciones** no autorizadas
- **Alertas automáticas** de cambios críticos

### 🌐 Monitor de Red
- **Detección de conexiones** sospechosas
- **Bloqueo automático** de IPs maliciosas
- **Monitoreo de puertos** abiertos
- **Análisis de tráfico** de red

### 🎌 Interfaz Gráfica Japonesa
- **Diseño inspirado** en Windows Defender
- **Estética japonesa** con colores tradicionales
- **Interfaz intuitiva** y fácil de usar
- **Monitoreo en tiempo real** del estado del sistema
- **File Integrity Monitoring**: Monitoreo de integridad de archivos críticos
- **Cuarentena Inteligente**: Aislamiento automático de amenazas
- **Monitoreo de Red**: Detección de conexiones y puertos sospechosos
- **Interfaz Gráfica**: GUI moderna con estética japonesa

### 📋 Requisitos Técnicos

- **Sistema Operativo**: Kali Linux o distribución basada en Debian
- **Python**: Versión 3.8 o superior
- **Dependencias**: Solo módulos estándar de Python (tkinter, logging, os, sys)
- **Privilegios**: Root para funcionalidad completa

### ⚡ Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/DogSoulDev/Ares-Aegis.git
cd Ares-Aegis

# Instalar dependencias
pip3 install -r requirements.txt

# Ejecutar aplicación
sudo python3 main.py
```

### 🏗️ Arquitectura del Proyecto

```
Ares-Aegis/
├── main.py                 # Punto de entrada principal
├── requirements.txt        # Dependencias Python
├── README.md              # Documentación técnica
├── MANUAL.md              # Manual de usuario completo
│
├── src/                   # Código fuente principal
│   ├── modelos/           # Lógica de negocio (MVC)
│   ├── vista/             # Interfaz gráfica (MVC)
│   └── controladores/     # Controladores (MVC)
│
├── config/                # Configuraciones
│   └── firmas/           # Base de datos de firmas
│
├── recursos/              # Recursos gráficos
│   ├── AresAegis.png     # Logo principal
│   └── aresIcon.png      # Icono aplicación
│
└── tests/                 # Tests unitarios
```

### 🎨 Principios de Desarrollo

- **Arquitectura**: MVC (Modelo-Vista-Controlador)
- **Metodología**: TDD (Test-Driven Development)
- **Estándares**: Clean Code y principios SOLID
- **Diseño**: Estética japonesa minimalista
- **Localización**: 100% en español

### 🔧 Componentes Técnicos

#### Modelos (`src/modelos/`)
- `siem.py`: Sistema de gestión de eventos e información
- `escaneador.py`: Motor interno de análisis de archivos
- `fim.py`: Monitoreo de integridad de archivos
- `cuarentena.py`: Sistema de cuarentena de archivos
- `integracion_externa.py`: Integración con ClamAV
- `monitor_red.py`: Monitoreo de conexiones de red

#### Vista (`src/vista/`)
- `interfaz_principal_gui.py`: Interfaz gráfica principal con tkinter

#### Controladores (`src/controladores/`)
- `controlador_principal.py`: Coordinador principal de la aplicación

### 🎯 Funcionalidades Core

1. **Detección de Amenazas**
   - Análisis de archivos y directorios
   - Detección de malware, rootkits y scripts maliciosos
   - Integración con bases de datos externas

2. **Monitoreo en Tiempo Real**
   - File Integrity Monitoring (FIM)
   - Monitoreo de procesos del sistema
   - Análisis de conexiones de red

3. **Gestión de Seguridad**
   - Cuarentena automática de amenazas
   - Sistema SIEM para auditoría
   - Reportes exportables en Markdown

4. **Interfaz de Usuario**
   - Diseño japonés con colores matcha, sakura y bamboo
   - Layout optimizado con grid tkinter
   - Manejo inteligente de imágenes y recursos

### 🛠️ Herramientas de Desarrollo

```bash
# Ejecutar tests
python3 -m pytest tests/

# Verificar calidad de código
python3 -m flake8 src/

# Generar documentación
python3 -m pydoc src.modelos.siem
```

### 📊 Configuración Avanzada

#### Variables de Entorno
```bash
export ARES_LOG_LEVEL=DEBUG
export ARES_QUARANTINE_DIR=/var/quarantine
```

#### Integración ClamAV
```bash
sudo apt install clamav clamav-daemon
sudo freshclam
```

### 🚨 Solución de Problemas

#### Error de Privilegios
```bash
sudo python3 main.py
```

#### Error de Módulos
```bash
pip3 install -r requirements.txt --force-reinstall
```

#### Error de Interfaz Gráfica
```bash
export DISPLAY=:0
xhost +local:
```

### 📈 Estado del Proyecto

- **Versión**: 2.0.0
- **Estado**: Producción estable
- **Cobertura de Tests**: Implementada
- **Documentación**: Completa (README.md + MANUAL.md)
- **Arquitectura**: MVC consolidada

### 🤝 Contribución

Este proyecto sigue los estándares de Clean Code y SOLID. Para contribuir:

1. Fork del repositorio
2. Crear branch feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### 📝 Licencia

Proyecto Open Source - Ver documentación completa en `MANUAL.md`

### 👨‍💻 Autor

**DogSoulDev** - Desarrollo y mantenimiento

---

Para instrucciones detalladas de uso, consultar `MANUAL.md`
