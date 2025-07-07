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

# 🛡️ Ares Aegis - Plataforma Avanzada de Ciberseguridad para Kali Linux

<div align="center">
  <img src="recursos/AresAegis.png" alt="Ares Aegis Logo" width="200"/>
  <br>
  <b>Versión:</b> 3.0.0 &nbsp;|&nbsp; <b>Python:</b> 3.8+ &nbsp;|&nbsp; <b>Licencia:</b> Propietaria &nbsp;|&nbsp; <b>Estado:</b> Activo
</div>

## 📋 Descripción General

Ares Aegis es una plataforma profesional de ciberseguridad desarrollada para entornos Linux (Kali, Debian, Ubuntu) que integra los módulos y técnicas más avanzadas y de mayor impacto en la defensa digital moderna. Su arquitectura modular, interfaz moderna y enfoque forense la convierten en una solución ideal para analistas, pentesters y equipos de respuesta a incidentes.

## 🚀 Características Destacadas

- **Escaneo multicapa de malware** (estático, dinámico, heurístico)
- **Monitor de red avanzado** con análisis de tráfico y detección de intrusiones
- **Monitor de procesos** con análisis de comportamiento y recursos
- **SIEM integrado** para correlación y auditoría de eventos
- **FIM avanzado** (File Integrity Monitoring) con baseline inteligente
- **Cuarentena forense** y descontaminación automatizada
- **Analizadores especializados** (archivos, cadenas, hex, comportamiento)
- **Reportes automatizados** en HTML, JSON y TXT
- **Interfaz gráfica moderna** (Tkinter) y CLI
- **Configuración y reglas personalizables**
- **Cumplimiento de estándares Clean Code, DRY, SOLID y PEP8**

## 🏗️ Arquitectura Modular

<details>
<summary><b>Ver diagrama y estructura</b></summary>

```
Ares-Aegis/
├── main.py
├── iniciar.sh
├── requirements.txt
├── ares_aegis/
│   ├── modelos/         # 24+ módulos de análisis y detección
│   ├── controladores/   # Orquestación y lógica central
│   ├── vista/           # Interfaz gráfica y CLI
│   └── utilidades/      # Herramientas auxiliares
├── configuracion/       # Firmas, reglas, notificaciones
├── recursos/            # Imágenes, iconos, bases de datos CVE
├── cuarentena/          # Sistema de aislamiento
├── logs/                # Registros y auditoría
├── reportes/            # Informes generados
└── tests/               # Pruebas unitarias y de integración
```

</details>

## 🔧 Instalación y Puesta en Marcha

### Requisitos
- **SO:** Kali Linux, Debian, Ubuntu (recomendado)
- **Python:** 3.8 o superior
- **RAM:** 4GB mínimo (8GB recomendado)
- **Permisos:** root para funciones avanzadas

### Instalación Rápida
```bash
git clone https://github.com/DogSoulDev/Ares-Aegis.git
cd Ares-Aegis
pip3 install -r requirements.txt
chmod +x iniciar.sh
sudo chmod +x main.py
sudo python3 main.py
```

## 🎮 Uso y Comandos Principales

```bash
# Inicio normal
sudo python3 main.py
# Inicio rápido
./iniciar.sh
# Pruebas automáticas
python3 -m pytest tests/
# Verificación de integridad
python3 verificar_proyecto.py
```

## 🛡️ Componentes Clave

- **SIEM central**: correlación, alertas y auditoría
- **Escaneador avanzado**: firmas, heurística, CVE
- **Monitor de red**: tráfico, conexiones, geolocalización
- **Monitor de procesos**: anomalías, recursos, jerarquía
- **FIM**: baseline, detección de cambios, restauración
- **Cuarentena**: aislamiento, análisis, backups
- **Analizadores**: archivos, cadenas, hex, comportamiento
- **Reportes**: HTML, JSON, TXT, notificaciones

## 📈 Tipos de Escaneo

| Tipo         | Duración   | Cobertura             | Uso Recomendado      |
|--------------|------------|-----------------------|----------------------|
| Rápido       | 2-5 min    | Ubicaciones críticas  | Verificación diaria  |
| Completo     | 15-45 min  | Sistema completo      | Análisis semanal     |
| Personalizado| Variable   | Directorios específicos| Análisis dirigido   |

## 🛠️ Configuración y Personalización

- **Firmas y reglas**: `configuracion/firmas.txt`, `recursos/reglas_respuesta.json`
- **Notificaciones**: `configuracion/notificaciones.json`
- **Umbrales y alertas**: personalizables en archivos de configuración
- **Informes**: formatos y frecuencia ajustables

## 💻 Calidad y Buenas Prácticas

- **Clean Code**: nombres descriptivos, funciones pequeñas, sin código muerto
- **DRY**: reutilización, utilidades centralizadas
- **SOLID**: arquitectura extensible y mantenible
- **PEP8 y type hints**: estilo y tipado estático
- **Documentación profesional en español**

## 🔍 Solución de Problemas

- **Permisos:**
  ```bash
  sudo chmod +x main.py
  sudo python3 main.py
  ```
- **Dependencias:**
  ```bash
  pip3 install -r requirements.txt --upgrade
  ```
- **Interfaz Tkinter:**
  ```bash
  sudo apt-get install python3-tk
  ```
- **Logs:**
  - `/var/log/ares_aegis/ares_aegis.log`
  - `logs/`
  - `/var/log/ares_aegis/eventos_siem.json`

## 👤 Autor y Contacto

- **Desarrollador:** DogSoulDev
- **GitHub:** https://github.com/DogSoulDev
- **Proyecto:** https://github.com/DogSoulDev/Ares-Aegis

## 📄 Licencia

```
Copyright (c) 2025 DogSoulDev
Todos los derechos reservados.
Código propietario y confidencial. Prohibida su copia o distribución sin autorización.
```

## 🔮 Roadmap

- [ ] Integración con bases de datos externas
- [ ] API REST y dashboard web
- [ ] Machine learning y análisis avanzado
- [ ] Soporte multiplataforma (Windows, cloud, mobile)

<div align="center">
  <img src="recursos/aresIcon.png" alt="Ares Icon" width="64"/>
  <br>
  <b>Ares Aegis v3.0.0</b> - Protección Digital Avanzada<br>
  Desarrollado con ❤️ por <a href="https://github.com/DogSoulDev">DogSoulDev</a>
</div>
