# Ares Aegis: Antivirus Avanzado para Kali Linux

**Versión:** 2.0.0  
**Autor:** DogSoulDev  
**Licencia:** MIT  
**Plataforma:** Kali Linux (y otras distribuciones basadas en Debian)

[![Estado](https://img.shields.io/badge/Estado-Estable-success)](https://github.com/DogSoulDev/Ares-Aegis)
[![Versión](https://img.shields.io/badge/Versión-2.0-blue)](https://github.com/DogSoulDev/Ares-Aegis)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![Arquitectura](https://img.shields.io/badge/Arquitectura-MVC-green)](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
[![Licencia](https://img.shields.io/badge/Licencia-MIT-green)](#)

---

## Descripción

Ares Aegis es una suite de ciberseguridad robusta, altamente fiable y fácil de usar diseñada específicamente para entornos Kali Linux. El sistema implementa múltiples módulos de seguridad siguiendo las mejores prácticas de desarrollo de software, incluyendo Clean Code, patrones de diseño (MVC, DRY, SOLID) y Test-Driven Development (TDD).

La aplicación utiliza **exclusivamente módulos estándar de Python**, sin dependencias externas complejas, garantizando máxima compatibilidad y facilidad de despliegue.

## Características Principales

### 🔍 Sistema SIEM Integrado
- **Gestión Centralizada de Eventos:** Sistema SIEM completo para recolección, almacenamiento y correlación de eventos de seguridad
- **Persistencia en JSON:** Almacenamiento eficiente de eventos con capacidad de exportación
- **Filtrado Avanzado:** Búsqueda y filtrado de eventos por tipo, severidad y fecha
- **Exportación de Reportes:** Generación de informes en formato Markdown para análisis

### 🛡️ Motor de Escaneo Multicapa
- **Detección por Firmas:** Base de datos de firmas de malware actualizable
- **Análisis de Hashes:** Verificación de integridad usando SHA256, MD5 y SHA1
- **Análisis Heurístico:** Detección de comportamientos sospechosos
- **Integración ClamAV:** Soporte para motor antivirus ClamAV cuando esté disponible

### 📊 Monitoreo de Integridad (FIM)
- **Creación de Línea Base:** Establecimiento de estado conocido de archivos
- **Detección de Cambios:** Identificación automática de modificaciones no autorizadas
- **Monitoreo Continuo:** Supervisión en tiempo real de directorios críticos
- **Alertas Inmediatas:** Notificación instantánea de cambios detectados

### 🗂️ Gestión de Cuarentena
- **Aislamiento Seguro:** Cuarentena de archivos sospechosos con permisos restrictivos
- **Gestión de Metadatos:** Registro detallado de archivos en cuarentena
- **Restauración Selectiva:** Capacidad de restaurar archivos legítimos
- **Eliminación Permanente:** Borrado seguro de archivos confirmados como maliciosos

### 🔧 Integración con Herramientas Externas
- **ClamAV:** Integración nativa con el motor antivirus ClamAV
- **Herramientas de Sistema:** Uso de utilidades como nmap, netstat, ss, lsof
- **Ejecución Segura:** Manejo robusto de comandos externos con validación

### 🎨 Interfaz Gráfica con Estilo Japonés
- **Diseño Minimalista:** Interfaz limpia inspirada en la estética japonesa
- **Colores Cálidos:** Paleta de colores naturales (matcha, sakura, bambú)
- **Navegación Intuitiva:** Estructura clara y accesible
- **Completamente en Español:** Interfaz 100% localizada en castellano

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

### Instalación Rápida

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/DogSoulDev/Ares-Aegis.git
   cd Ares-Aegis
   ```

2. **Ejecutar la aplicación:**
   ```bash
   sudo python3 main.py
   ```

### Instalación desde Paquete .deb (Próximamente)

```bash
# Descargar e instalar el paquete .deb
wget https://github.com/DogSoulDev/Ares-Aegis/releases/latest/download/ares-aegis.deb
sudo dpkg -i ares-aegis.deb

# Resolver dependencias si es necesario
sudo apt-get install -f
```

## Uso

### Ejecución

```bash
# Ejecutar desde el directorio del proyecto
sudo python3 main.py

# O desde cualquier ubicación si está instalado
sudo ares-aegis
```

### Navegación de la Interfaz

La aplicación presenta una interfaz gráfica organizada en las siguientes secciones:

1. **Detección y Análisis de Archivos**
   - Escaneo individual de archivos
   - Análisis con motor interno y ClamAV
   - Cálculo de hashes criptográficos
   - Extracción de metadatos

2. **Monitoreo de Sistema y Procesos**
   - Monitoreo de integridad de archivos (FIM)
   - Supervisión de procesos del sistema
   - Análisis de conexiones de red
   - Detección de anomalías

3. **Gestión de Registros y Cuarentena**
   - Administración de archivos en cuarentena
   - Visualización de logs del sistema SIEM
   - Exportación de reportes
   - Gestión de eventos de seguridad

4. **Herramientas del Sistema**
   - Utilidades de diagnóstico
   - Integración con herramientas externas
   - Configuración del sistema
   - Herramientas de análisis avanzado

### Ejemplos de Uso

#### Escaneo de Archivo
```bash
# Desde la interfaz gráfica:
# 1. Ir a "Detección y Análisis de Archivos"
# 2. Hacer clic en "Seleccionar Archivo"
# 3. Elegir "Escanear Archivo (Interno)" o "Escanear con ClamAV"
# 4. Revisar resultados en el panel de resultados
```

#### Monitoreo de Integridad
```bash
# Desde la interfaz gráfica:
# 1. Ir a "Monitoreo de Sistema y Procesos"
# 2. Seleccionar "Crear Línea Base"
# 3. Elegir directorio a monitorear
# 4. Usar "Verificar Integridad" para detectar cambios
```

## Arquitectura del Proyecto

### Estructura de Directorios

```
Ares-Aegis/
├── main.py                        # Punto de entrada principal
├── README.md                      # Documentación principal
├── requirements.txt               # Dependencias (vacío por diseño)
├── src/                          # Código fuente principal
│   ├── __init__.py
│   ├── modelos/                  # Lógica de negocio (Modelo en MVC)
│   │   ├── __init__.py
│   │   ├── siem.py              # Sistema de gestión de eventos
│   │   ├── escaneador.py        # Motor de escaneo de archivos
│   │   ├── fim.py               # Monitoreo de integridad
│   │   ├── gestor_cuarentena.py # Gestión de cuarentena
│   │   └── integracion_externa.py # Integración con herramientas
│   └── vista/                   # Interfaz gráfica (Vista en MVC)
│       ├── __init__.py
│       └── interfaz_principal_gui.py # GUI principal
├── tests/                       # Pruebas unitarias (TDD)
│   ├── __init__.py
│   ├── test_siem.py
│   ├── test_escaneador.py
│   └── test_fim.py
├── configuracion/               # Archivos de configuración
│   └── firmas.txt              # Base de datos de firmas
└── recursos/                   # Recursos gráficos y estáticos
    ├── README.md
    ├── aresIcon.png           # Icono de la aplicación (formato PPM requerido)
    └── Ares.jpeg             # Imagen de marca (formato PPM requerido)
```

### Principios de Diseño

#### Patrón MVC (Modelo-Vista-Controlador)
- **Modelos (src/modelos/):** Lógica de negocio pura e independiente
- **Vista (src/vista/):** Interfaz gráfica con tkinter
- **Controlador:** Integrado en la vista para gestión de eventos

#### Principios SOLID
- **SRP:** Cada módulo tiene una responsabilidad específica
- **OCP:** Extensible sin modificar código existente
- **LSP:** Herencia correcta donde es aplicable
- **ISP:** Interfaces pequeñas y específicas
- **DIP:** Inyección de dependencias en lugar de instanciación directa

#### Clean Code
- Nombres descriptivos y autoexplicativos
- Funciones pequeñas y enfocadas
- Comentarios solo cuando agregan valor
- Manejo robusto de errores y excepciones

## Testing

### Ejecutar Pruebas Unitarias

```bash
# Ejecutar todas las pruebas
python3 -m unittest discover tests/

# Ejecutar prueba específica
python3 -m unittest tests.test_siem

# Ejecutar con verbosidad para más detalles
python3 -m unittest discover tests/ -v
```

### Cobertura de Pruebas

El proyecto incluye pruebas unitarias exhaustivas para:
- **Sistema SIEM:** Gestión de eventos, persistencia, filtrado y exportación
- **Escaneador:** Detección por firmas, análisis de hashes, gestión de resultados
- **FIM:** Creación de líneas base, detección de cambios, monitoreo
- **Cuarentena:** Aislamiento de archivos, gestión de metadatos, restauración
- **Integración Externa:** Ejecución de herramientas externas, manejo de errores

## Configuración

### Archivos de Configuración

#### `configuracion/firmas.txt`
Base de datos de firmas de malware con soporte para:
- **Firmas de texto simple:** Cadenas que indican presencia de malware
- **Hashes SHA256:** Identificadores únicos de archivos maliciosos conocidos
- **Expresiones regulares:** Patrones complejos para detección avanzada

Ejemplo:
```
# Firmas de texto simple
eval(base64_decode
system($_GET
<script>alert

# Hashes maliciosos (formato HASH:valor)
HASH:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

# Expresiones regulares (formato REGEX:patrón)
REGEX:eval\\s*\\(\\s*base64_decode
REGEX:<script[^>]*>.*</script>
```

### Ubicaciones de Archivos

#### En Desarrollo
- **Configuración:** `~/.ares_aegis/`
- **Logs:** `~/.ares_aegis/ares_aegis.log`
- **Cuarentena:** `~/.ares_aegis/cuarentena/`
- **Datos SIEM:** `~/.ares_aegis/siem_events.json`

#### En Producción (cuando se instale como paquete)
- **Configuración:** `/etc/ares_aegis/`
- **Logs:** `/var/log/ares_aegis/ares_aegis.log`
- **Cuarentena:** `/var/ares_aegis_cuarentena/`
- **Datos SIEM:** `/var/lib/ares_aegis/siem_events.json`

## Características Técnicas

### Estilo Visual Japonés
La interfaz implementa una **estética japonesa minimalista**:
- **Colores Naturales:** Verde matcha (#8FBC8F), azul cielo (#87CEEB), marrón cálido (#DEB887)
- **Paleta Complementaria:** Rosa sakura (#FFB6C1), crema suave (#F5F5DC)
- **Diseño Armonioso:** Espaciado uniforme, tipografía clara
- **Experiencia Zen:** Interfaz que transmite calma y eficiencia

### Logging Centralizado
- **Sistema SIEM Integrado:** Todos los eventos se registran centralmente
- **Niveles de Severidad:** INFO, WARNING, ERROR, CRITICAL
- **Persistencia Automática:** Guardado automático de eventos en JSON
- **Capacidad de Búsqueda:** Filtrado por fecha, tipo y severidad

### Exportación de Reportes
- **Formato Markdown:** Reportes legibles y estéticamente agradables
- **Estructura Clara:** Encabezados, listas y bloques de código
- **Información Completa:** Resumen ejecutivo y detalles técnicos
- **Fácil Conversión:** Compatible con generadores de PDF/HTML

## Seguridad

### Consideraciones de Seguridad
- **Privilegios de Root:** Requeridos para acceso completo al sistema
- **Validación de Entrada:** Sanitización rigurosa de todos los inputs del usuario
- **Manejo Seguro de Archivos:** Validación de rutas y verificación de permisos
- **Cuarentena Segura:** Archivos en cuarentena con permisos 600 (solo propietario)

### Buenas Prácticas Implementadas
- **Principio de Menor Privilegio:** Solo solicitar permisos necesarios
- **Validación de Comandos:** Verificación antes de ejecutar comandos externos
- **Logging de Auditoría:** Registro de todas las acciones realizadas
- **Manejo de Errores:** Gestión robusta sin exposición de información sensible

## Solución de Problemas

### Problemas Comunes

#### Error: "Permission denied"
```bash
# Problema: La aplicación no puede crear logs en /var/log/
# Solución: Ejecutar con sudo o la aplicación usará ~/.ares_aegis/
sudo python3 main.py
```

#### Error: "Module 'tkinter' not found"
```bash
# Problema: tkinter no está instalado
# Solución en Debian/Ubuntu:
sudo apt-get install python3-tk

# Solución en otras distribuciones:
# Consultar documentación específica de la distribución
```

#### Error: "ClamAV not found"
```bash
# Problema: ClamAV no está instalado (es opcional)
# Solución para instalarlo:
sudo apt-get install clamav clamav-daemon
sudo freshclam  # Actualizar definiciones
```

### Logs de Diagnóstico
En caso de problemas, revisar:
- **Logs de aplicación:** `~/.ares_aegis/ares_aegis.log` o `/var/log/ares_aegis/ares_aegis.log`
- **Eventos del SIEM:** A través de la interfaz gráfica en "Gestión de Registros"
- **Logs del sistema:** `/var/log/syslog` para errores relacionados con permisos

## Desarrollo y Contribución

### Configuración del Entorno de Desarrollo
```bash
# Clonar el repositorio
git clone https://github.com/DogSoulDev/Ares-Aegis.git
cd Ares-Aegis

# Crear rama para desarrollo
git checkout -b feature/nueva-funcionalidad

# Ejecutar pruebas antes de modificar
python3 -m unittest discover tests/ -v

# Realizar cambios siguiendo los principios del proyecto
# ...

# Ejecutar pruebas después de modificar
python3 -m unittest discover tests/ -v

# Commit y push
git add .
git commit -m "feat: Agregar nueva funcionalidad"
git push origin feature/nueva-funcionalidad
```

### Estándares de Código
- **PEP 8:** Seguir estrictamente las convenciones de Python
- **Type Hints:** Usar anotaciones de tipo en todas las funciones nuevas
- **Docstrings:** Documentar todas las clases y métodos públicos
- **Tests Unitarios:** Implementar pruebas para toda nueva funcionalidad
- **Clean Code:** Mantener funciones pequeñas y nombres descriptivos

### Guías de Contribución
1. **Fork** del repositorio
2. **Crear rama** para la nueva funcionalidad
3. **Implementar** siguiendo los principios del proyecto
4. **Escribir tests** para la nueva funcionalidad
5. **Ejecutar** todas las pruebas para verificar que no se rompe nada
6. **Documentar** los cambios en comentarios de código
7. **Crear Pull Request** con descripción detallada

## Roadmap

### Versión 2.1 (Planificada)
- [ ] **Análisis Dinámico:** Sandbox básico para análisis de comportamiento
- [ ] **Detección de Rootkits:** Motor especializado en detección de rootkits
- [ ] **Dashboard Web:** Interfaz web opcional para monitoreo remoto
- [ ] **API REST:** Endpoints para automatización e integración externa
- [ ] **Mejoras de Rendimiento:** Optimizaciones para sistemas con recursos limitados

### Versión 2.2 (Futura)
- [ ] **Machine Learning:** Detección de amenazas usando algoritmos de ML
- [ ] **Integración YARA:** Soporte para reglas YARA personalizadas
- [ ] **Threat Intelligence:** Integración con feeds de inteligencia de amenazas
- [ ] **Soporte Multi-idioma:** Localización a otros idiomas
- [ ] **Análisis Forense:** Herramientas básicas de análisis forense

### Ideas de la Comunidad
- [ ] **Plugin System:** Sistema de plugins para extensibilidad
- [ ] **Distribución Docker:** Contenedor Docker oficial
- [ ] **Integración Cloud:** Soporte para análisis en la nube
- [ ] **Mobile App:** Aplicación móvil para notificaciones
- [ ] **Enterprise Features:** Funcionalidades para entornos empresariales

## Soporte y Documentación

### Recursos de Ayuda
- **Documentación Técnica:** Este README y comentarios en código
- **Issues de GitHub:** Para reportar bugs y solicitar funcionalidades
- **Discusiones:** Para preguntas generales y discusiones técnicas
- **Wiki:** Documentación adicional y tutoriales (próximamente)

### Contacto
- **Repositorio:** https://github.com/DogSoulDev/Ares-Aegis
- **Issues:** https://github.com/DogSoulDev/Ares-Aegis/issues
- **Desarrollador:** [@DogSoulDev](https://github.com/DogSoulDev)

### Problemas Conocidos
- **Imágenes PNG/JPEG:** tkinter requiere formato PPM/GIF para imágenes
- **Permisos de Root:** Algunas funciones requieren privilegios elevados
- **ClamAV Opcional:** Funcionalidad completa requiere ClamAV instalado

## Licencia

Este proyecto está licenciado bajo la **Licencia MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

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

---

## Créditos

**Desarrollado con ❤️ por [DogSoulDev](https://github.com/DogSoulDev)**

*Ares Aegis* - Protección avanzada para sistemas Kali Linux  
*Inspirado en la filosofía del software libre y las mejores prácticas de desarrollo*

---

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-DogSoulDev%2FAres--Aegis-black?logo=github)](https://github.com/DogSoulDev/Ares-Aegis)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

**🛡️ Ares Aegis - Seguridad avanzada con arquitectura limpia 🛡️**

</div>
