# 🏛️ ARES AEGIS - ARSENAL DE WORDLISTS 🏛️

> *"Conocimiento es poder, y las wordlists son el arsenal del guerrero digital"*

Generado automáticamente el 2025-07-22 23:40:51

## 📋 ÍNDICE COMPLETO DE WORDLISTS

### 🔐 **CONTRASEÑAS** (Password Cracking)
| Wordlist | Tamaño | Efectividad | Uso Principal |
|----------|--------|-------------|---------------|
| `rockyou_top10k.txt` | ~10,000 | ⭐⭐⭐⭐⭐ | Auditorías rápidas, CTFs |
| `passwords_worst_500.txt` | ~500 | ⭐⭐⭐ | Primeras pruebas, validación básica |
| `combinaciones_basicas.txt` | ~2,000 | ⭐⭐⭐ | Patrones corporativos, locales |

**🛠️ Herramientas compatibles:** Hydra, John the Ripper, Hashcat, Medusa

### 🌐 **SUBDOMINIOS** (Subdomain Enumeration)
| Wordlist | Tamaño | Efectividad | Uso Principal |
|----------|--------|-------------|---------------|
| `seclists_subdomains.txt` | ~5,000 | ⭐⭐⭐⭐⭐ | Reconocimiento completo |

**🛠️ Herramientas compatibles:** Gobuster, FFuF, Amass, Subfinder

### 📁 **DIRECTORIOS WEB** (Web Fuzzing)
| Wordlist | Tamaño | Efectividad | Uso Principal |
|----------|--------|-------------|---------------|
| `seclists_directories.txt` | ~4,750 | ⭐⭐⭐⭐⭐ | Fuzzing web completo |
| `web_extensions.txt` | ~200 | ⭐⭐⭐ | Descubrimiento de archivos |

**🛠️ Herramientas compatibles:** Gobuster, FFuF, Wfuzz, Dirb

### 👤 **USUARIOS** (User Enumeration)
| Wordlist | Tamaño | Efectividad | Uso Principal |
|----------|--------|-------------|---------------|
| `seclists_usernames.txt` | ~10,713 | ⭐⭐⭐⭐ | Enumeración de usuarios |

**🛠️ Herramientas compatibles:** Hydra, Enum4linux, RPCclient

### 🔌 **APIs** (API Discovery)
| Wordlist | Tamaño | Efectividad | Uso Principal |
|----------|--------|-------------|---------------|
| `api_endpoints.txt` | ~5,000 | ⭐⭐⭐⭐ | Descubrimiento de APIs |

**🛠️ Herramientas compatibles:** FFuF, Wfuzz, Gobuster

### 📚 **DICCIONARIOS** (Language-Specific)
| Wordlist | Tamaño | Efectividad | Uso Principal |
|----------|--------|-------------|---------------|
| `palabras_españolas.txt` | ~15,000 | ⭐⭐⭐ | Ataques localizados (ESP) |
| `numeros_comunes.txt` | ~1,000 | ⭐⭐ | Patrones numéricos |
| `simbolos_especiales.txt` | ~100 | ⭐⭐ | Mutaciones de contraseñas |

## 🚀 **CONFIGURACIONES PREDEFINIDAS**

### ⚡ **Fuzzing Web Básico** (10-30 min)
```bash
# Gobuster
gobuster dir -u http://target.com -w seclists_directories.txt -x php,html,txt

# FFuF
ffuf -u http://target.com/FUZZ -w seclists_directories.txt
```

### 🔍 **Enumeración Subdominios** (5-15 min)
```bash
# Gobuster DNS
gobuster dns -d target.com -w seclists_subdomains.txt

# FFuF Subdominios
ffuf -u https://FUZZ.target.com -w seclists_subdomains.txt
```

### 🔑 **Ataque Contraseñas Rápido** (<5 min)
```bash
# Hydra SSH
hydra -L seclists_usernames.txt -P rockyou_top10k.txt ssh://target.com

# John the Ripper
john --wordlist=rockyou_top10k.txt hashes.txt
```

### 🎯 **Reconocimiento Completo** (30-60 min)
```bash
# Secuencia completa
gobuster dns -d target.com -w seclists_subdomains.txt
gobuster dir -u http://target.com -w seclists_directories.txt
hydra -L seclists_usernames.txt -P rockyou_top10k.txt ssh://target.com
ffuf -u http://target.com/FUZZ -w api_endpoints.txt
```

## 📊 **ESTADÍSTICAS DE EFECTIVIDAD**

| Wordlist | Tasa de Éxito | Casos de Uso | Tiempo Promedio |
|----------|---------------|--------------|-----------------|
| RockYou Top 10K | 85% | Auditorías, CTFs | < 5 min |
| SecLists Directories | 70% | Pentesting web | 10-30 min |
| SecLists Subdomains | 60% | Reconocimiento | 5-15 min |
| API Endpoints | 45% | Bug Bounty | 15-45 min |

## 🛠️ **HERRAMIENTAS KALI LINUX**

### Gobuster
```bash
apt install gobuster
gobuster dir -u http://target.com -w seclists_directories.txt -x php,html,txt
```

### FFuF
```bash
apt install ffuf
ffuf -u http://target.com/FUZZ -w seclists_directories.txt
```

### Hydra
```bash
apt install hydra
hydra -L users.txt -P rockyou_top10k.txt ssh://target.com
```

### Wfuzz
```bash
apt install wfuzz
wfuzz -c -z file,seclists_directories.txt http://target.com/FUZZ
```

## ⚡ **CONSEJOS DE OPTIMIZACIÓN**

### 🎯 **Efectividad**
- Usa wordlists específicas según el objetivo
- Combina múltiples listas pequeñas vs una grande
- Filtra por códigos HTTP relevantes (200, 301, 403)
- Ajusta threads según la capacidad del objetivo

### 🛡️ **Buenas Prácticas**
- **SIEMPRE** obtén autorización antes de usar
- Documenta todos los hallazgos
- Usa rate limiting para evitar detección
- Combina automatización con análisis manual

### 🎨 **Personalización**
- Crea wordlists basadas en información del objetivo
- Usa `cewl` para generar listas desde sitios web
- Combina nombres, fechas y patrones de la organización
- Mantén actualizadas con nuevos patrones

## 📁 **ARCHIVOS DE CONFIGURACIÓN**

- `wordlists_config.json` - Metadatos completos y configuraciones
- `listas_base.json` - Datos de wordlists (41,476 líneas)
- `generadas/` - Wordlists generadas automáticamente

## 📦 **WORDLISTS REMOTAS DESCARGADAS**

- **seclists_usernames.txt**: Nombres comunes de SecLists
  - Líneas: 10,713 | Tamaño: 75,127 bytes
  - Fuente: danielmiessler/SecLists

- **seclists_directories.txt**: Directorios web comunes  
  - Líneas: 4,750 | Tamaño: 38,500 bytes
  - Fuente: danielmiessler/SecLists

- **seclists_subdomains.txt**: Top subdominios para fuzzing
  - Líneas: 4,989 | Tamaño: 33,566 bytes
  - Fuente: danielmiessler/SecLists

- **rockyou_top10k.txt**: Top 10K passwords comunes
  - Líneas: 10,000 | Tamaño: 73,017 bytes  
  - Fuente: danielmiessler/SecLists

- **passwords_worst_500.txt**: 500 peores passwords
  - Líneas: 499 | Tamaño: 3,491 bytes
  - Fuente: danielmiessler/SecLists

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
