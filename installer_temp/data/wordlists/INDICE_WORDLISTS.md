# Índice de Wordlists - Ares Aegis

Generado automáticamente el 2025-07-22 23:40:51

## Wordlists Remotas Descargadas

- **seclists_usernames.txt**: Nombres comunes de SecLists
  - Líneas: 10,713
  - Tamaño: 75,127 bytes
  - Fuente: https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/Names/names.txt

- **seclists_directories.txt**: Directorios web comunes
  - Líneas: 4,750
  - Tamaño: 38,500 bytes
  - Fuente: https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt

- **seclists_subdomains.txt**: Top subdominios para fuzzing
  - Líneas: 4,989
  - Tamaño: 33,566 bytes
  - Fuente: https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt

- **rockyou_top10k.txt**: Top 10K passwords comunes
  - Líneas: 10,000
  - Tamaño: 73,017 bytes
  - Fuente: https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt

- **passwords_worst_500.txt**: 500 peores passwords
  - Líneas: 499
  - Tamaño: 3,491 bytes
  - Fuente: https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/500-worst-passwords.txt

- **web_extensions.txt**: Extensiones de archivos web
  - Líneas: 43
  - Tamaño: 227 bytes
  - Fuente: https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/web-extensions.txt

- **api_endpoints.txt**: Endpoints de API comunes
  - Líneas: 269
  - Tamaño: 4,123 bytes
  - Fuente: https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/api/api-endpoints.txt

## Wordlists Locales Generadas

- **numeros_comunes.txt**: Números comunes (años, fechas, etc.)
  - Líneas: 10,013
  - Tamaño: 60,065 bytes
  - Generado localmente

- **palabras_españolas.txt**: Palabras comunes en español
  - Líneas: 107
  - Tamaño: 898 bytes
  - Generado localmente

- **combinaciones_basicas.txt**: Combinaciones básicas de caracteres
  - Líneas: 656
  - Tamaño: 2,651 bytes
  - Generado localmente

- **simbolos_especiales.txt**: Símbolos especiales para passwords
  - Líneas: 104
  - Tamaño: 386 bytes
  - Generado localmente

## Uso en Ares Aegis

Estas wordlists están disponibles automáticamente en el Constructor de Wordlists de Ares Aegis.
Puede seleccionar múltiples listas, aplicar mutaciones y filtros para crear wordlists personalizadas.

## Categorías

- **Passwords**: rockyou_top10k.txt, seclists_passwords_top1m.txt, common_passwords_12m.txt
- **Usernames**: seclists_usernames.txt, palabras_españolas.txt
- **Web Fuzzing**: seclists_directories.txt, fuzzdb_directories.txt, api_endpoints.txt
- **Subdomain Fuzzing**: seclists_subdomains.txt
- **Números**: numeros_comunes.txt
- **Símbolos**: simbolos_especiales.txt
- **Payloads**: payloads_sqli.txt
- **General**: english_words.txt, combinaciones_basicas.txt
