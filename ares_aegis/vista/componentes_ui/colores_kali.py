#!/usr/bin/env python3
"""
Colores Kali Linux para Ares Aegis
Paleta de colores estilo Kali Linux para excelente legibilidad
"""


class ColoresKaliLinux:
    """
    Paleta de colores profesional inspirada en herramientas de ciberseguridad
    Diseño terminal hacker con máximo contraste y estilo profesional
    """
    
    def __init__(self):
        # === BASE OSCURA PROFESIONAL ===
        # Inspirado en terminales, VS Code Dark, Metasploit Console
        self.negro_profundo = "#0A0A0A"         # Negro absoluto para máximo contraste
        self.negro_carbono = "#1A1A1A"          # Gris carbón para paneles principales
        self.gris_pizarra = "#2D2D2D"           # Gris pizarra para elementos activos
        self.gris_hierro = "#3C3C3C"            # Gris hierro para separadores
        self.gris_titanio = "#4A4A4A"           # Gris titanio para elementos hover
        
        # === VERDES PROFESIONALES ===
        # Inspirado en Matrix, terminales Linux, herramientas de hacking
        self.verde_fosforescente = "#39FF14"    # Verde fosforescente brillante (alertas críticas)
        self.verde_terminal = "#00FF41"         # Verde terminal Kali clásico
        self.verde_esmeralda = "#00C851"        # Verde esmeralda (éxitos)
        self.verde_bosque = "#228B22"           # Verde bosque (elementos secundarios)
        self.verde_oliva = "#355E3B"            # Verde oliva (fondos suaves)
        
        # === ACENTOS PROFESIONALES ===
        # Inspirado en herramientas como Burp Suite, Wireshark, Nmap
        self.azul_electrico = "#007ACC"         # Azul VS Code (información)
        self.azul_acero = "#4682B4"             # Azul acero (datos técnicos)
        self.cyan_brillante = "#00FFFF"         # Cyan brillante (monitoreo activo)
        self.purpura_neon = "#B266FF"           # Púrpura neón (elementos especiales)
        self.magenta_laser = "#FF00FF"          # Magenta láser (destacados)
        self.naranja_fuego = "#FF6B35"          # Naranja fuego (títulos principales)
        self.naranja_titanio = "#FF8C42"        # Naranja titanio (acentos especiales)
        
        # === COLORES DE TEXTO ===
        # Máxima legibilidad en pantallas oscuras
        self.blanco_hueso = "#F8F8F2"           # Blanco ligeramente cálido
        self.gris_platino = "#CFCFCF"           # Gris platino para texto secundario
        self.gris_plata = "#A8A8A8"             # Gris plata para elementos deshabilitados
        self.gris_mercurio = "#808080"          # Gris mercurio para hints
        
        # === ESTADOS DEL SISTEMA ===
        # Inspirado en dashboards de seguridad y SOCs
        self.rojo_critico = "#FF073A"           # Rojo crítico (amenazas altas)
        self.rojo_sangre = "#DC143C"            # Rojo sangre (vulnerabilidades)
        self.naranja_alto = "#FF8C00"           # Naranja alto (alertas medias)
        self.amarillo_medio = "#FFD700"         # Amarillo medio (advertencias)
        self.azul_bajo = "#4169E1"              # Azul bajo (información)
        
        # === ELEMENTOS ESPECIALES ===
        # Para efectos visuales y elementos interactivos
        self.sombra_profunda = "#000000"        # Negro puro para sombras
        self.brillo_suave = "#FFFFFF"           # Blanco puro para brillos
        self.transparente_verde = "#00FF4120"   # Verde transparente para overlays
        self.transparente_rojo = "#FF073A20"    # Rojo transparente para alertas
        
        # === MAPEO PARA COMPATIBILIDAD ===
        # Mantener compatibilidad con código existente
        self.fondo_primario = self.negro_profundo
        self.fondo_secundario = self.negro_carbono
        self.fondo_terciario = self.gris_pizarra
        self.fondo_emergente = self.gris_hierro
        
        self.texto_primario = self.blanco_hueso
        self.texto_secundario = self.gris_platino
        self.texto_terciario = self.gris_plata
        
        self.acento_primario = self.verde_terminal
        self.acento_secundario = self.cyan_brillante
        self.acento_terciario = self.purpura_neon
        
        self.exito = self.verde_esmeralda
        self.advertencia = self.amarillo_medio
        self.error = self.rojo_critico
        self.peligro = self.rojo_sangre  # Agregando color peligro
        self.info = self.azul_electrico
        
        self.borde_activo = self.verde_terminal
        self.borde_inactivo = self.gris_hierro
        self.boton_hover = self.verde_bosque
        self.seleccion = self.verde_oliva
        
        # === COLORES ESPECÍFICOS PARA CIBERSEGURIDAD ===
        # Para elementos específicos de herramientas de seguridad
        self.scan_activo = self.verde_fosforescente
        self.scan_completado = self.verde_esmeralda
        self.amenaza_detectada = self.rojo_critico
        self.amenaza_critica = self.rojo_sangre
        self.sistema_seguro = self.verde_terminal
        self.monitoreo_activo = self.cyan_brillante
        self.archivo_cuarentena = self.naranja_alto
        self.proceso_sospechoso = self.amarillo_medio
        self.conexion_maliciosa = self.magenta_laser
        self.vulnerabilidad_alta = self.rojo_critico
        self.vulnerabilidad_media = self.naranja_alto
        self.vulnerabilidad_baja = self.amarillo_medio
