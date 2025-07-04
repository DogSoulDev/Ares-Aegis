# 🛡️ Ares Aegis - Sistema Avanzado de Ciberseguridad

<div align="center">
  <img src="recursos/AresAegis.png" alt="Ares Aegis Logo" width="200"/>
  
  [![Versión](https://img.shields.io/badge/versión-3.0.0-blue.svg)](https://github.com/DogSoulDev/Ares-Aegis)
  [![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
  [![Licencia](https://img.shields.io/badge/licencia-Propietaria-red.svg)](LICENSE)
  [![Estado](https://img.shields.io/badge/estado-Activo-brightgreen.svg)](https://github.com/DogSoulDev/Ares-Aegis)
</div>

## 📋 Descripción

**Ares Aegis** es un sistema avanzado de ciberseguridad desarrollado en Python que proporciona protección integral contra amenazas digitales. Implementa una **arquitectura de 8 componentes especializados** con una interfaz moderna e intuitiva para ofrecer una solución completa de protección empresarial.

### 🎯 Características Principales

- **🔍 Escaneador de Malware Avanzado** - Análisis multicapa con detección heurística
- **🌐 Monitor de Red Mejorado** - Supervisión continua con análisis de tráfico
- **⚙️ Monitor de Procesos** - Detección de comportamiento anómalo
- **🗂️ Sistema de Cuarentena Avanzado** - Aislamiento forense inteligente
- **📊 SIEM Integrado** - Sistema de información y gestión de eventos
- **🛡️ FIM Avanzado** - Monitoreo de integridad de archivos con baseline
- **🔬 Analizadores Especializados** - Módulos de análisis dedicados
- **📈 Sistema de Reportes y Notificaciones** - Informes automatizados completos

### 🏗️ Arquitectura de 8 Componentes

1. **🧠 SIEM (Sistema Central)** - Núcleo de eventos y correlación
2. **� Escaneador de Malware** - Motor de detección avanzado
3. **🌐 Monitor de Red Avanzado** - Análisis de tráfico en tiempo real
4. **⚙️ Monitor de Procesos** - Supervisión de comportamiento
5. **🛡️ FIM Avanzado** - Integridad de archivos con Kali Linux
6. **🗂️ Cuarentena Avanzada** - Sistema forense inteligente
7. **🔬 Analizadores Especializados** - Módulos de análisis dedicados
8. **📊 Reportes y Notificaciones** - Sistema de comunicación automatizado

## 🚀 Tecnologías

- **Lenguaje:** Python 3.8+ (Solo librerías estándar)
- **Interfaz:** Tkinter con componentes modernos personalizados
- **Arquitectura:** MVC (Modelo-Vista-Controlador) estricta
- **Base de Datos:** JSON para configuración y persistencia
- **Análisis:** Múltiples motores de detección especializados
- **Monitoreo:** Tiempo real con threading y análisis forense
- **Principios:** Código limpio, DRY, SOLID, documentación en español

### 🎨 Arquitectura MVC Limpia

```
ares_aegis/
├── 📁 modelos/                  # Lógica de negocio (24 componentes)
│   ├── siem.py                  # Sistema central de eventos
│   ├── escaneador.py            # Motor de malware avanzado
│   ├── monitor_red_mejorado.py  # Análisis de red en tiempo real
│   ├── fim_avanzado.py          # Integridad de archivos
│   ├── gestor_cuarentena_avanzado.py # Sistema forense
│   └── ...                      # 19 componentes especializados más
├── 📁 controladores/            # Coordinación del sistema
│   └── controlador_principal.py # Orquestador de 8 componentes
├── 📁 vista/                    # Interfaz de usuario
│   ├── interfaz_principal_gui.py # GUI moderna
│   └── interfaz_principal.py    # CLI interactiva
└── 📁 utilidades/               # Herramientas auxiliares
    ├── ayuda_logging.py         # Sistema de logs
    ├── validaciones.py          # Validación de datos
    └── temas_modernos.py        # Estilos visuales
```

## 📁 Estructura del Proyecto

```
Ares-Aegis/
├── 📄 main.py                    # Punto de entrada principal
├── 📄 requirements.txt           # Dependencias del proyecto
├── 📄 iniciar.sh                # Script de inicio rápido
├── 📁 ares_aegis/               # Código fuente principal
│   ├── 📁 controladores/        # Lógica de negocio (MVC)
│   ├── 📁 modelos/              # Modelos de datos y componentes
│   ├── 📁 vista/                # Interfaz de usuario
│   └── 📁 utilidades/           # Herramientas auxiliares
├── 📁 configuracion/            # Archivos de configuración
├── 📁 recursos/                 # Imágenes, iconos y recursos
├── 📁 cuarentena/               # Sistema de cuarentena
├── 📁 logs/                     # Archivos de registro
├── 📁 reportes/                 # Informes generados
└── 📁 tests/                    # Pruebas unitarias
```

## 🔧 Instalación

### Requisitos del Sistema

- **Sistema Operativo:** Linux (Ubuntu/Debian recomendado)
- **Python:** 3.8 o superior
- **Memoria RAM:** Mínimo 4GB, recomendado 8GB
- **Espacio en Disco:** 2GB libres
- **Permisos:** Acceso root para funciones avanzadas

### Instalación Rápida

1. **Clonar el repositorio:**
```bash
git clone https://github.com/DogSoulDev/Ares-Aegis.git
cd Ares-Aegis
```

2. **Instalar dependencias:**
```bash
pip3 install -r requirements.txt
```

3. **Configurar permisos:**
```bash
chmod +x iniciar.sh
sudo chmod +x main.py
```

4. **Ejecutar el sistema:**
```bash
sudo python3 main.py
```

## 🎮 Uso del Sistema

### Interfaz Principal

El sistema cuenta con una interfaz moderna dividida en secciones principales:

#### 🏠 Panel Principal
- **Estado del Sistema** - Monitoreo en tiempo real
- **Escaneo Rápido** - Análisis inmediato
- **Actividad Reciente** - Eventos del sistema
- **Alertas** - Notificaciones de seguridad

#### 🔍 Centro de Escaneo
- **Escaneo Rápido** - Análisis de ubicaciones críticas (2-5 min)
- **Escaneo Completo** - Análisis exhaustivo del sistema (15-45 min)
- **Escaneo Personalizado** - Análisis de directorios específicos
- **Progreso en Tiempo Real** - Visualización del proceso archivo por archivo

#### 🛡️ Monitoreo
- **Red** - Conexiones activas y tráfico
- **Procesos** - Supervisión de procesos del sistema
- **Eventos SIEM** - Registro completo de actividades
- **Estadísticas** - Métricas del sistema en tiempo real

#### 🗂️ Cuarentena
- **Gestión de Archivos** - Aislar y gestionar amenazas
- **Restauración** - Recuperar archivos seguros
- **Análisis Detallado** - Información completa de cada archivo

### Comandos Principales

```bash
# Inicio normal
sudo python3 main.py

# Inicio rápido con script
./iniciar.sh

# Modo de prueba
python3 -m pytest tests/

# Verificación del sistema
python3 verificar_proyecto.py
```

## 🔐 Características de Seguridad

### 🎯 Los 8 Componentes Especializados

#### 1. 🧠 SIEM (Sistema Central)
- **Gestión de Eventos** - Registro y correlación centralizada
- **Análisis de Patrones** - Detección de comportamientos anómalos
- **Alertas Inteligentes** - Sistema de notificaciones prioritarias
- **Auditoría Completa** - Trazabilidad total de eventos

#### 2. 🔍 Escaneador de Malware Avanzado
- **Análisis Estático** - Detección de patrones conocidos y heurísticos
- **Análisis Dinámico** - Comportamiento en tiempo real
- **Motor Multicapa** - Firmas, heurística y análisis de comportamiento
- **Base de Datos CVE** - Vulnerabilidades conocidas actualizadas

#### 3. 🌐 Monitor de Red Avanzado
- **Análisis de Tráfico** - Inspección profunda de paquetes
- **Detección de Intrusiones** - Patrones de ataque conocidos
- **Conexiones Sospechosas** - Monitoreo de comunicaciones anómalas
- **Geolocalización** - Análisis de origen de conexiones

#### 4. ⚙️ Monitor de Procesos
- **Comportamiento Anómalo** - Detección de procesos sospechosos
- **Análisis de Recursos** - Uso anormal de CPU y memoria
- **Jerarquía de Procesos** - Análisis de relaciones padre-hijo
- **Inyección de Código** - Detección de técnicas avanzadas

#### 5. 🛡️ FIM Avanzado (File Integrity Monitoring)
- **Baseline Inteligente** - Línea base automática del sistema
- **Monitoreo Kali Linux** - Rutas críticas especializadas
- **Detección de Cambios** - Modificaciones no autorizadas
- **Restauración** - Capacidad de rollback de archivos

#### 6. 🗂️ Sistema de Cuarentena Avanzado
- **Aislamiento Forense** - Preservación de evidencia
- **Análisis Profundo** - Descompilación y análisis de malware
- **Descontaminación Inteligente** - Limpieza automatizada
- **Gestión de Backups** - Respaldo antes de acciones

#### 7. 🔬 Analizadores Especializados
- **Analizador de Archivos** - Tipos de archivo y contenido
- **Analizador de Cadenas** - Extracción de strings sospechosos
- **Analizador de Comportamiento** - Patrones de ejecución
- **Visor Hexadecimal** - Análisis a nivel de bytes

#### 8. 📊 Sistema de Reportes y Notificaciones
- **Reportes Automatizados** - Generación programada
- **Múltiples Formatos** - HTML, JSON, Markdown
- **Notificaciones en Tiempo Real** - Alertas inmediatas
- **Dashboard Integral** - Métricas y estadísticas

## 📊 Tipos de Escaneo

| Tipo | Duración | Cobertura | Uso Recomendado |
|------|----------|-----------|-----------------|
| **Rápido** | 2-5 min | Ubicaciones críticas | Verificación diaria |
| **Completo** | 15-45 min | Sistema completo | Análisis semanal |
| **Personalizado** | Variable | Directorios específicos | Análisis dirigido |

## 🛠️ Configuración Avanzada

### Archivos de Configuración

- `configuracion/firmas.txt` - Firmas de malware personalizadas
- `configuracion/notificaciones.json` - Configuración de alertas
- `recursos/reglas_respuesta.json` - Reglas de respuesta automática

### Personalización

El sistema permite personalizar:
- **Umbrales de detección** - Sensibilidad del análisis
- **Reglas de cuarentena** - Criterios de aislamiento
- **Notificaciones** - Tipos y frecuencia de alertas
- **Informes** - Formato y contenido de reportes

## 📈 Monitoreo y Reportes

### Métricas del Sistema
- Archivos analizados
- Amenazas detectadas
- Tiempo de respuesta
- Uso de recursos

### Formatos de Exportación
- **HTML** - Reportes web interactivos
- **JSON** - Datos estructurados
- **TXT** - Texto plano para análisis

## 💻 Calidad del Código

### 🎯 Principios Implementados

**Ares Aegis** sigue estrictamente los principios de desarrollo de software moderno:

#### 📐 Código Limpio (Clean Code)
- **Nombres Descriptivos** - Variables y funciones autoexplicativas
- **Funciones Pequeñas** - Una responsabilidad por función
- **Comentarios Significativos** - Documentación en español
- **Sin Código Muerto** - Eliminación sistemática de código obsoleto

#### 🔄 DRY (Don't Repeat Yourself)
- **Eliminación de Duplicación** - Código reutilizable
- **Funciones Auxiliares** - Utilidades comunes centralizadas
- **Herencia Inteligente** - Aprovechamiento de POO
- **Configuración Centralizada** - Un solo punto de configuración

#### 🏗️ Principios SOLID
- **S** - Responsabilidad Única: Cada clase tiene un propósito específico
- **O** - Abierto/Cerrado: Extensible sin modificar código existente
- **L** - Sustitución de Liskov: Herencia apropiada
- **I** - Segregación de Interfaces: Interfaces específicas
- **D** - Inversión de Dependencias: Abstracciones, no concreciones

#### 🐍 Estándares Python
- **PEP 8** - Estilo de código Python oficial
- **Type Hints** - Tipado estático para mejor mantenimiento
- **Docstrings** - Documentación estándar en español
- **Solo Librerías Estándar** - Sin dependencias externas

## 🔍 Solución de Problemas

### Problemas Comunes

**Error de permisos:**
```bash
sudo chmod +x main.py
sudo python3 main.py
```

**Dependencias faltantes:**
```bash
pip3 install -r requirements.txt --upgrade
```

**Problemas de interfaz:**
```bash
sudo apt-get install python3-tk
```

### Logs del Sistema

Los registros se almacenan en:
- `/var/log/ares_aegis/ares_aegis.log` - Log principal
- `logs/` - Logs de módulos específicos
- `/var/log/ares_aegis/eventos_siem.json` - Eventos SIEM

## 👥 Contribución

Este es un proyecto propietario desarrollado por **DogSoulDev**. 

### Contacto
- **Desarrollador:** DogSoulDev
- **GitHub:** [https://github.com/DogSoulDev](https://github.com/DogSoulDev)
- **Proyecto:** [https://github.com/DogSoulDev/Ares-Aegis](https://github.com/DogSoulDev/Ares-Aegis)

## 📄 Licencia

```
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados.

Este código es propietario y confidencial. La copia, distribución 
o modificación no autorizada está estrictamente prohibida.
```

## 🔮 Roadmap

### Versión 3.1.0 (Próximamente)
- [ ] Integración con bases de datos externas
- [ ] API REST para integración
- [ ] Dashboard web
- [ ] Análisis de machine learning

### Versión 3.2.0 (Futuro)
- [ ] Soporte para Windows
- [ ] Análisis de contenedores
- [ ] Integración cloud
- [ ] Mobile app de monitoreo

---

<div align="center">
  <img src="recursos/aresIcon.png" alt="Ares Icon" width="64"/>
  
  **Ares Aegis v3.0.0** - Protección Digital Avanzada
  
  Desarrollado con ❤️ por [DogSoulDev](https://github.com/DogSoulDev)
</div>
