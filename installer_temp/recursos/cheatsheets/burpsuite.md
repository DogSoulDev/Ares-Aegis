# Burp Suite CheatSheet

## 🚀 Configuración Inicial

### Configurar Proxy
1. Proxy → Options → Proxy Listeners
2. Add → 127.0.0.1:8080
3. Configurar navegador para usar proxy localhost:8080

### Certificado SSL
1. Visitar http://burp/cert
2. Descargar e instalar certificado

## 🕷️ Spider/Crawler

### Configurar Spider
```
Target → Site map → Right click → Spider this host
```

### Opciones de Spider
- Check robots.txt
- Parse comments
- Parse forms
- Follow redirections

## 🔍 Scanner

### Escaneo Pasivo
```
Target → Site map → Right click → Passively scan this host
```

### Escaneo Activo
```
Target → Site map → Right click → Actively scan this host
```

### Tipos de Vulnerabilidades
- SQL Injection
- XSS (Cross-Site Scripting)
- CSRF
- Directory Traversal
- Command Injection

## 🎯 Intruder

### Tipos de Ataque
1. **Sniper**: Un payload set, una posición
2. **Battering Ram**: Un payload set, múltiples posiciones
3. **Pitchfork**: Múltiples payload sets, posiciones correlacionadas
4. **Cluster Bomb**: Múltiples payload sets, todas las combinaciones

### Configuración de Payloads
```
Intruder → Payloads
- Simple list
- Runtime file
- Custom iterator
- Numbers
- Dates
```

### Ejemplos de Payloads
```
# SQL Injection
' OR 1=1--
' UNION SELECT null,null,null--
admin'--

# XSS
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
javascript:alert('XSS')
```

## 🕵️ Repeater

### Uso Básico
1. Interceptar request
2. Send to Repeater (Ctrl+R)
3. Modificar request
4. Send (Ctrl+Space)

### Headers Importantes
```
User-Agent: [custom]
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Originating-IP: 127.0.0.1
```

## 🔄 Proxy

### Intercept
- Intercept is on/off (Ctrl+T)
- Forward (Ctrl+F)
- Drop

### Match and Replace
```
Proxy → Options → Match and Replace
- Replace headers
- Add headers
- Modify responses
```

## 🎛️ Sequencer

### Análisis de Tokens
1. Proxy → HTTP history
2. Select request with token
3. Send to Sequencer
4. Configure token location
5. Start live capture

## 🔧 Extensiones Útiles

### BApp Store
- Logger++
- Autorize
- JSON Beautifier
- Wappalyzer
- Reflected Parameters
- Software Vulnerability Scanner

## 🎯 Metodología de Testing

### 1. Reconocimiento
```
- Spider/Crawler
- Análisis de tecnologías
- Mapeo de aplicación
```

### 2. Análisis de Autenticación
```
- Login bypass
- Password policies
- Session management
- Logout functionality
```

### 3. Autorización
```
- Privilege escalation
- Horizontal/Vertical access
- Direct object references
```

### 4. Input Validation
```
- SQL Injection
- XSS
- Command Injection
- File Upload
```

## 📊 Técnicas Avanzadas

### Session Handling Rules
```
Project options → Sessions → Session Handling Rules
- Add/update cookies
- Run macro
- Check session validity
```

### Macros
```
Project options → Sessions → Macros
- Record sequence
- Configure parameters
- Test macro
```

### Collaborator
```
Burp → Burp Collaborator client
- Generate payloads
- Poll for interactions
- Test blind vulnerabilities
```

## 🚀 Automatización

### JSON/REST API Testing
```
Content-Type: application/json
{
  "param1": "value1",
  "param2": "§payload§"
}
```

### Authentication Bypass
```
# HTTP Headers
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-Override-URL: /admin
```

---
**⚠️ Uso Responsable**: Solo para aplicaciones autorizadas y propósitos educativos.
