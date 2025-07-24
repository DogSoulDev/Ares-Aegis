# Nmap - Network Mapper CheatSheet

## 🔍 Escaneo Básico

### Escaneo Simple
```bash
nmap [target]
nmap 192.168.1.1
nmap scanme.nmap.org
```

### Escaneo de Red
```bash
nmap 192.168.1.0/24
nmap 192.168.1.1-20
```

## 🚀 Tipos de Escaneo

### TCP SYN Scan (Stealth)
```bash
nmap -sS [target]
```

### TCP Connect Scan
```bash
nmap -sT [target]
```

### UDP Scan
```bash
nmap -sU [target]
```

### Ping Scan (No port scan)
```bash
nmap -sn [target]
```

## 🎯 Opciones de Puerto

### Escanear Puertos Específicos
```bash
nmap -p 22,80,443 [target]
nmap -p 1-100 [target]
nmap -p- [target]  # Todos los puertos
```

### Top Ports
```bash
nmap --top-ports 1000 [target]
```

## 🔧 Detección Avanzada

### Detección de OS
```bash
nmap -O [target]
```

### Detección de Servicios y Versiones
```bash
nmap -sV [target]
```

### Scripts NSE
```bash
nmap -sC [target]  # Scripts por defecto
nmap --script vuln [target]  # Scripts de vulnerabilidades
```

## ⚡ Escaneos Rápidos y Sigilosos

### Escaneo Rápido
```bash
nmap -T4 -F [target]
```

### Escaneo Sigiloso
```bash
nmap -T1 -sS [target]
```

### Evitar Detección
```bash
nmap -D RND:10 [target]  # Decoy scan
nmap -f [target]  # Fragment packets
```

## 📊 Output y Reportes

### Guardar Resultados
```bash
nmap -oN output.txt [target]
nmap -oX output.xml [target]
nmap -oA output [target]  # Todos los formatos
```

## 🛡️ Ejemplos Prácticos

### Escaneo Completo de Red
```bash
nmap -sS -sV -O -A --top-ports 1000 192.168.1.0/24
```

### Detección de Hosts Activos
```bash
nmap -sn 192.168.1.0/24
```

### Escaneo de Vulnerabilidades
```bash
nmap --script vuln,safe 192.168.1.1
```

---
**⚠️ Uso Responsable**: Solo utilizar en redes propias o con autorización explícita.
