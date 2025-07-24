# 🛡️ ARES AEGIS v4.0 - GUÍA DE INSTALACIÓN PARA KALI LINUX

## 🚀 **3 FORMAS FÁCILES DE INSTALAR**

---

## 📦 **OPCIÓN 1: INSTALADOR AUTOCONTENIDO (.run)** ⭐ **RECOMENDADO**

### ✨ **¡SÚPER FÁCIL! Solo 1 archivo**

1. **Crear el instalador autocontenido:**
   ```bash
   # En Windows/desarrollo:
   chmod +x create_installer.sh
   ./create_installer.sh
   ```

2. **Transferir a Kali Linux:**
   ```bash
   scp ares-aegis-installer.run user@kali-ip:~/
   ```

3. **Instalar en Kali Linux:**
   ```bash
   chmod +x ares-aegis-installer.run
   sudo ./ares-aegis-installer.run
   ```

4. **¡LISTO! Ejecutar:**
   ```bash
   ares-aegis
   # O desde: Aplicaciones → Security → Ares Aegis
   ```

### 🗑️ **Para desinstalar:**
```bash
sudo ./ares-aegis-installer.run --uninstall
```

---

## 🐍 **OPCIÓN 2: INSTALADOR PYTHON** 

### ✅ **Multiplataforma y simple**

1. **Transferir el proyecto completo a Kali Linux**

2. **Ejecutar el instalador Python:**
   ```bash
   cd Ares-Aegis
   sudo python3 installer.py
   ```

3. **¡LISTO! Ejecutar:**
   ```bash
   ares-aegis
   ```

### 🗑️ **Para desinstalar:**
```bash
sudo python3 installer.py --uninstall
```

---

## 📦 **OPCIÓN 3: PAQUETE .DEB TRADICIONAL**

### 🔧 **Para usuarios avanzados**

1. **Transferir el proyecto completo a Kali Linux**

2. **Construir el paquete .deb:**
   ```bash
   cd Ares-Aegis
   chmod +x build_deb.sh
   ./build_deb.sh
   ```

3. **Instalar el .deb:**
   ```bash
   sudo dpkg -i ares-aegis_4.0.0_all.deb
   sudo apt-get install -f  # Si hay dependencias faltantes
   ```

---

## 🎯 **¿QUÉ OPCIÓN ELEGIR?**

| Opción | Facilidad | Archivos a transferir | Recomendado para |
|--------|-----------|----------------------|------------------|
| **Instalador .run** | ⭐⭐⭐⭐⭐ | 1 archivo | **Todos los usuarios** |
| **Instalador Python** | ⭐⭐⭐⭐ | Proyecto completo | Usuarios de Python |
| **Paquete .deb** | ⭐⭐⭐ | Proyecto completo | Usuarios avanzados |

---

## 🔐 **CARACTERÍSTICAS INCLUIDAS EN TODAS LAS OPCIONES:**

✅ **Gestión automática de permisos root**
- Solicita permisos automáticamente usando `pkexec` o `sudo`
- Explica al usuario por qué se necesitan permisos
- Modo degradado si se rechazan permisos

✅ **Integración completa con Kali Linux**
- Iconos en `/usr/share/pixmaps/`
- Entrada en el menú: Aplicaciones → Security → Ares Aegis
- Launcher inteligente: `/usr/bin/ares-aegis`

✅ **Funcionalidades de ciberseguridad completas**
- 🔍 Escaneo de vulnerabilidades del sistema
- 📁 Monitoreo de integridad de archivos (FIM)
- 🌐 Monitor de red en tiempo real
- 🔒 Auditoría de autenticación PAM
- 🚨 Sistema SIEM integrado
- 🛡️ Constructor de wordlists avanzado
- 📊 Generación de reportes detallados

---

## 🚀 **DESPUÉS DE LA INSTALACIÓN:**

### **Ejecutar Ares Aegis:**
```bash
# Desde terminal (solicita permisos automáticamente):
ares-aegis

# Con permisos explícitos:
sudo ares-aegis

# Desde menú gráfico:
# Aplicaciones → Security → Ares Aegis
```

### **Verificar instalación:**
```bash
# Verificar que el comando está disponible:
which ares-aegis

# Verificar archivos instalados:
ls -la /opt/ares-aegis/
ls -la /usr/share/applications/ares-aegis.desktop
```

---

## ⚠️ **REQUISITOS DEL SISTEMA:**

- **Sistema Operativo:** Kali Linux (recomendado) o Debian/Ubuntu
- **Python:** 3.8 o superior (incluido en Kali Linux)
- **Dependencias:** `python3-tk` (se instala automáticamente)
- **Permisos:** Root/sudo (para funcionalidad completa)
- **Espacio:** ~50 MB

---

## 🔧 **SOLUCIÓN DE PROBLEMAS:**

### **Error: "No se encontró python3"**
```bash
sudo apt-get update
sudo apt-get install python3 python3-tk
```

### **Error: "Permisos insuficientes"**
```bash
# Asegúrate de usar sudo:
sudo ./instalador
```

### **Error: "No se encontraron archivos del proyecto"**
```bash
# Asegúrate de estar en la carpeta correcta:
ls -la main.py ares_aegis/
```

### **Reinstalar completamente:**
```bash
# Desinstalar primero:
sudo ./installer.py --uninstall
# Luego instalar de nuevo:
sudo ./installer.py
```

---

## 🆘 **SOPORTE:**

- **GitHub:** https://github.com/DogSoulDev/Ares-Aegis
- **Issues:** https://github.com/DogSoulDev/Ares-Aegis/issues
- **Documentación:** Ver archivos `README.md` y `DISTRIBUCIÓN_COMPLETADA.md`

---

## 🎉 **¡DISFRUTA ARES AEGIS!**

Una vez instalado, tendrás acceso a una suite completa de herramientas de ciberseguridad diseñada específicamente para profesionales de pentesting en Kali Linux.

**🛡️ Desarrollado por DogSoulDev - Suite de Ciberseguridad Profesional**
