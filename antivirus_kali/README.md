# Ares Aegis

Antivirus modular, visual y automatizado para Kali Linux. 

## Características principales

- **Escaneo avanzado** de rootkits, procesos, puertos, servicios, integridad de binarios y programas instalados.
- **Generación de informes PDF profesionales y visuales**:
  - Portada con branding, icono circular y QR de soporte.
  - Panel visual de riesgo global (gauge).
  - Resumen ejecutivo automático y recomendaciones personalizadas.
  - Tablas visuales con iconos y colores para cada sección.
  - QR de restauración rápida y feedback anónimo.
  - Pie de página motivacional y paginación.
- **Experiencia 100% automatizada**: el usuario solo elige la opción, el sistema analiza, interpreta y presenta todo de forma clara y visual.
- **No requiere APIs externas ni registros**: toda la lógica y análisis es local y privado.
- **Interfaz gráfica minimalista y moderna** (PySide6), con paneles para cada área de seguridad.
- **Código limpio, modular y profesional**: sin archivos duplicados ni rutas obsoletas.

## Instalación

1. Clona el repositorio y entra en la carpeta:
   ```bash
   git clone https://github.com/DogSoulDev/Ares-Aegis.git
   cd Ares-Aegis
   ```
2. Crea y activa el entorno virtual:
   ```bash
   python3 -m venv antivirus_kali/.venv
   source antivirus_kali/.venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install --upgrade pip
   pip install -r antivirus_kali/requirements.txt
   pip install qrcode[pil]
   ```
4. Ejecuta la aplicación:
   ```bash
   python3 antivirus_kali/principal.py
   ```

## Uso

- Navega por los paneles para escanear el sistema, verificar integridad, analizar red, gestionar IOCs y más.
- Exporta el informe PDF profesional desde el panel de escaneo avanzado.
- Escanea los QR del informe para restaurar el sistema o enviar feedback anónimo.

## Buenas prácticas y principios

- **Privacidad y autonomía**: todo el análisis es local, sin enviar datos fuera.
- **Visual y didáctico**: cada informe y panel está diseñado para ser claro, visual y fácil de interpretar.
- **Automatización total**: el usuario no necesita conocimientos técnicos ni realizar pasos complejos.
- **Código profesional y mantenible**: estructura limpia, modular y sin duplicidades.

## Créditos

Desarrollado por DogSoulDev y colaboradores. 

¿Ideas, sugerencias o problemas? Escanea el QR de feedback en tu informe o abre un issue en GitHub.

---

Ares Aegis: Seguridad, arte y disciplina para tu sistema Kali Linux.
