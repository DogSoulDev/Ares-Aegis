
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
- **Internacionalización lista**: todos los textos de la interfaz están centralizados en `interfaz/textos.py` para facilitar traducción y coherencia.
- **Logging profesional**: todos los eventos, advertencias y errores críticos se registran en consola y en el archivo `ares_aegis.log`.
- **Accesibilidad y UX**: tooltips descriptivos, feedback visual y accesibilidad reforzada en todos los paneles y botones.
- **Automatización total**: el usuario solo elige la opción, el sistema analiza, interpreta y presenta todo de forma clara y visual.
- **No requiere APIs externas ni registros**: toda la lógica y análisis es local y privado.
- **Interfaz gráfica minimalista y moderna** (PySide6), con paneles para cada área de seguridad.
- **Código limpio, modular y profesional**: sin archivos duplicados ni rutas obsoletas. Uso de `pathlib` para rutas robustas.
- **Preparado para CI/CD**: incluye script `test_ci.sh` para pruebas y linting automáticos.



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
4. (Opcional) Ejecuta el script de test y linting:
   ```bash
   bash test_ci.sh
   ```
5. Ejecuta la aplicación:
   ```bash
   python3 antivirus_kali/principal.py
   ```
   
   Si quieres acceder a todas las funciones avanzadas (requiere privilegios de administrador/root):
   
   - Desde la interfaz, pulsa "Loguearte como root" y sigue el diálogo seguro de autenticación (pkexec).
   - O ejecuta directamente desde terminal:
     ```bash
     pkexec ./antivirus_kali/ares-aegis-wrapper.sh
     ```
   - Si usas un paquete .deb, el lanzador gráfico usará este flujo automáticamente.
   
   El wrapper bash garantiza privacidad total: solo ejecuta localmente, no almacena ni transmite contraseñas ni datos.



## Uso

- Navega por los paneles para escanear el sistema, verificar la integridad, analizar la red, gestionar IOCs y más.
- Exporta el informe PDF profesional desde el panel de escaneo avanzado.
- Escanea los QR del informe para restaurar el sistema o enviar feedback anónimo.
- Todos los eventos importantes quedan registrados en el archivo `ares_aegis.log` para auditoría y soporte.

### Ejemplo de uso

1. Abre la aplicación con `python3 antivirus_kali/principal.py`.
2. Selecciona el panel de escaneo que desees (sistema, red, integridad, etc.).
3. Haz clic en "Iniciar escaneo" y espera el resultado.
4. Consulta la consola integrada para información detallada y logs.
5. Exporta el informe PDF si lo necesitas.



## Buenas prácticas y principios

- **Privacidad y autonomía**: todo el análisis es local, sin enviar datos fuera.
- **Visual y didáctico**: cada informe y panel está diseñado para ser claro, visual y fácil de interpretar.
- **Automatización total**: el usuario no necesita conocimientos técnicos ni realizar pasos complejos.
- **Código profesional y mantenible**: estructura limpia, modular y sin duplicidades.
- **Accesibilidad y seguridad**: todos los paneles y botones cuentan con tooltips, validación de entradas y protección ante errores.
- **Preparado para internacionalización**: todos los textos están centralizados y listos para traducir.
- **Logging profesional**: auditoría y soporte facilitados por logs automáticos.



## Estructura del proyecto

```
Ares-Aegis/
├── antivirus_kali/
│   ├── __init__.py
│   ├── main.py
│   ├── principal.py
│   ├── config.py
│   ├── configuracion.py
│   ├── requirements.txt
│   ├── controladores/
│   ├── informes/
│   ├── interfaz/
│   ├── nucleo/
│   ├── recursos/
│   ├── utilidades/
│   └── tests/
├── assets/
├── test_ci.sh
└── README.md
```

## FAQ


**¿Funciona en cualquier distribución Linux?**

Ares Aegis está optimizado para Kali Linux, pero puede funcionar en otras distribuciones basadas en Debian. Se recomienda probar y reportar cualquier incompatibilidad.

**¿Se envía información fuera del equipo?**

No. Todo el análisis y los informes se generan localmente. No se envía ningún dato a servidores externos. El flujo de privilegios con pkexec y el wrapper bash es seguro y estándar en Linux: tu contraseña nunca sale de tu equipo.

**¿Cómo puedo traducir la interfaz?**

Todos los textos están centralizados en `interfaz/textos.py`. Puedes crear un archivo de traducción y modificar los textos fácilmente.

**¿Dónde encuentro los logs?**

En el archivo `ares_aegis.log` en el directorio raíz del proyecto.

**¿Cómo contribuyo o reporto un bug?**

Puedes abrir un issue en GitHub o escanear el QR de feedback que aparece en los informes PDF.

## Créditos


Desarrollado íntegramente por DogSoulDev. Refactorizado, modernizado y editado con ayuda de GPT-4.1 (OpenAI Copilot). No existen colaboradores ni terceros: todo el código, lógica, interfaz y documentación han sido realizados exclusivamente por el autor y editados por IA bajo su supervisión.

¿Ideas, sugerencias o problemas? Escanea el QR de feedback en tu informe o abre un issue en GitHub.

---

Ares Aegis: Seguridad, arte y disciplina para tu sistema Kali Linux.

## Contacto

- GitHub: [DogSoulDev/Ares-Aegis](https://github.com/DogSoulDev/Ares-Aegis)
- Email: dogsouldev@protonmail.com
