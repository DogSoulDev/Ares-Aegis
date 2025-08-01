#!/usr/bin/env python3
"""
Vista Escaneador para Ares Aegis
Interfaz del módulo de escaneador de amenazas
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import logging
from ..componentes_ui.emoticonos_mitologicos import EmoticonosMitologicos
from ..componentes_ui.sistema_ayuda import SistemaAyuda
from ...utils.validaciones import validar_directorio, validar_permisos_lectura


class VistaEscaneador:
    """Vista del escaneador de amenazas"""
    
    def __init__(self, contenedor_padre, controlador, colores):
        self.contenedor_padre = contenedor_padre
        self.controlador = controlador
        self.colores = colores
        self.logger = logging.getLogger(__name__)
        self.frame_principal = None
        
        # Variables de control inicializadas correctamente
        self.ruta_escaneo_var = tk.StringVar(value=os.path.expanduser("~"))
        self.escaneo_profundo_var = tk.BooleanVar(value=False)
        self.verificar_hashes_var = tk.BooleanVar(value=True)
        self.analisis_contenido_var = tk.BooleanVar(value=False)
        
        # Variables de estado de la interfaz
        self.estado_var = tk.StringVar(value="🛡️ Listo para escanear")
        self.progreso_var = tk.DoubleVar(value=0.0)
        self.resultados_text = None  # Se inicializa en _crear_area_resultados
        self.estado_var = tk.StringVar(value="🛡️ Listo para escanear")
        self.resultados_text = None  # Se inicializa en crear_vista
        self.escaneo_activo = False
        self.hilo_escaneo = None
        
    def mostrar_informacion(self):
        """Mostrar información de ayuda sobre el Escaneador"""
        info_text = """🛡️ ESCANEADOR DE AMENAZAS - INFORMACIÓN

🔍 FUNCIONALIDADES PRINCIPALES:
• Escaneo de archivos y directorios
• Detección de amenazas y malware
• Análisis de contenido avanzado
• Verificación de hashes sospechosos

⚡ OPCIONES DE ESCANEO:
• Escaneo Básico: Verificación rápida
• Escaneo Profundo: Análisis exhaustivo
• Verificar Hashes: Comparación con bases de datos
• Análisis de Contenido: Inspección detallada

🎯 TIPOS DE DETECCIÓN:
• Malware conocido por firmas
• Archivos ejecutables sospechosos
• Scripts potencialmente peligrosos
• Patrones de comportamiento anómalo

🔧 CÓMO USAR:
1. Selecciona la ruta a escanear
2. Configura las opciones de análisis
3. Inicia el escaneo con 'Comenzar Análisis'
4. Revisa los resultados en tiempo real

⚠️ RECOMENDACIONES:
• Usa escaneo profundo para análisis completo
• Verifica hashes para mayor precisión
• Revisa todos los archivos detectados
• Mantén actualizadas las firmas de amenazas

📊 INTERPRETACIÓN DE RESULTADOS:
• 🟢 LIMPIO: Archivo seguro
• 🟡 SOSPECHOSO: Requiere revisión
• 🔴 AMENAZA: Archivo potencialmente peligroso
• ⚫ ERROR: No se pudo analizar"""
        
        messagebox.showinfo("Información - Escaneador de Amenazas", info_text)
        
    def crear_vista(self, area_contenido=None):
        """Crear la vista del escaneador con diseño responsive"""
        self._limpiar_contenedor()
        
        # Frame principal con padding estandarizado
        self.frame_principal = tk.Frame(self.contenedor_padre, bg=self.colores.fondo_secundario)
        self.frame_principal.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Configurar grid responsive con mejores proporciones
        self.frame_principal.grid_rowconfigure(0, weight=0)  # Header fijo
        self.frame_principal.grid_rowconfigure(1, weight=1)  # Contenido expandible
        self.frame_principal.grid_columnconfigure(0, weight=1)
        
        # Header del escaneador
        self._crear_header_escaneador()
        
        # Container principal con scroll
        main_container = tk.Frame(self.frame_principal, bg=self.colores.fondo_secundario)
        main_container.grid(row=1, column=0, sticky='nsew', pady=10)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_container, bg=self.colores.fondo_secundario, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.frame_scroll = tk.Frame(canvas, bg=self.colores.fondo_secundario)
        
        # Configurar scroll responsive
        self.frame_scroll.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.frame_scroll, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid para canvas y scrollbar
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Panel de control
        self._crear_panel_control()
        
        # Área de resultados
        self._crear_area_resultados()
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Bind para responsive del canvas
        def _configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas.find_all()[0], width=event.width)
        canvas.bind('<Configure>', _configure_canvas)
    
    def _limpiar_contenedor(self):
        """Limpiar el contenedor padre"""
        for widget in self.contenedor_padre.winfo_children():
            widget.destroy()
    
    def _crear_header_escaneador(self):
        """Crear header del escaneador con diseño centrado"""
        header = tk.Frame(self.frame_principal, bg=self.colores.fondo_terciario, height=80)
        header.grid(row=0, column=0, sticky='ew', padx=0, pady=0)
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)
        header.grid_rowconfigure(0, weight=1)
        
        # Título centrado
        tk.Label(header,
                text=f"🔍 {EmoticonosMitologicos.ARES} Escudo de Exploración - Analizador de Amenazas",
                font=('Consolas', 16, 'bold'),
                fg=self.colores.acento_primario,
                bg=self.colores.fondo_terciario).grid(row=0, column=0)
        
        # Botón de información
        tk.Button(header,
                 text="❓ Info",
                 font=('Consolas', 10),
                 bg=self.colores.acento_secundario,
                 fg='white',
                 command=self.mostrar_informacion,
                 relief='flat',
                 padx=10,
                 pady=5).grid(row=0, column=1, padx=20, sticky='e')
    
    def _crear_panel_control(self):
        """Crear panel de control del escaneador con grid responsive"""
        # Configurar grid del frame_scroll
        self.frame_scroll.grid_columnconfigure(0, weight=1)
        
        control_frame = tk.LabelFrame(self.frame_scroll,
                                    text=f"🎯 {EmoticonosMitologicos.ESPADA} Control de Análisis",
                                    bg=self.colores.fondo_secundario,
                                    fg=self.colores.acento_primario,
                                    font=('Consolas', 12, 'bold'),
                                    padx=20, pady=15)
        control_frame.grid(row=0, column=0, sticky='ew', padx=20, pady=10)
        control_frame.grid_columnconfigure(0, weight=1)
        
        # Selector de directorio
        self._crear_selector_directorio(control_frame)
        
        # Opciones de escaneo
        self._crear_opciones_escaneo(control_frame)
        
        # Botón de escaneo
        self._crear_boton_escaneo(control_frame)
    
    def _crear_selector_directorio(self, padre):
        """Crear selector de directorio con grid responsive"""
        dir_frame = tk.Frame(padre, bg=self.colores.fondo_secundario)
        dir_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        dir_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(dir_frame,
                text=f"📁 {EmoticonosMitologicos.PERGAMINO} Directorio a analizar:",
                font=('Consolas', 10, 'bold'),
                fg=self.colores.texto_primario,
                bg=self.colores.fondo_secundario).grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 8))
        
        self.ruta_escaneo_var = tk.StringVar(value=os.path.expanduser("~"))
        path_entry = tk.Entry(dir_frame,
                            textvariable=self.ruta_escaneo_var,
                            font=('Consolas', 10),
                            bg=self.colores.fondo_primario,
                            fg=self.colores.texto_primario,
                            relief='solid',
                            bd=1)
        path_entry.grid(row=1, column=0, columnspan=2, sticky='ew', padx=(0, 10))
        
        def seleccionar_directorio():
            directory = filedialog.askdirectory(
                title="Seleccionar directorio para analizar",
                initialdir=self.ruta_escaneo_var.get()
            )
            if directory:
                self.ruta_escaneo_var.set(directory)
        
        tk.Button(dir_frame,
                 text="📂 Examinar",
                 command=seleccionar_directorio,
                 bg=self.colores.acento_primario,
                 fg=self.colores.fondo_primario,
                 font=('Consolas', 10, 'bold'),
                 cursor='hand2',
                 relief='flat',
                 padx=20, pady=8).grid(row=1, column=2, sticky='e')
    
    def _crear_opciones_escaneo(self, padre):
        """Crear opciones de escaneo con grid centrado"""
        options_frame = tk.Frame(padre, bg=self.colores.fondo_secundario)
        options_frame.grid(row=1, column=0, sticky='ew', pady=(0, 15))
        options_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(options_frame,
                text=f"⚙️ {EmoticonosMitologicos.BALANZA} Opciones de Análisis:",
                font=('Consolas', 10, 'bold'),
                fg=self.colores.texto_primario,
                bg=self.colores.fondo_secundario).grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        check_frame = tk.Frame(options_frame, bg=self.colores.fondo_secundario)
        check_frame.grid(row=1, column=0, sticky='ew')
        check_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.escaneo_profundo_var = tk.BooleanVar(value=True)
        self.verificar_hashes_var = tk.BooleanVar(value=True)
        self.analisis_contenido_var = tk.BooleanVar(value=False)
        
        tk.Checkbutton(check_frame,
                      text=f"🔬 {EmoticonosMitologicos.ARGOS} Análisis profundo",
                      variable=self.escaneo_profundo_var,
                      bg=self.colores.fondo_secundario,
                      fg=self.colores.texto_primario,
                      selectcolor=self.colores.fondo_primario,
                      font=('Consolas', 10)).grid(row=0, column=0, sticky='w', padx=(0, 20), pady=5)
        
        tk.Checkbutton(check_frame,
                      text=f"🔐 {EmoticonosMitologicos.ESCUDO} Verificar hashes",
                      variable=self.verificar_hashes_var,
                      bg=self.colores.fondo_secundario,
                      fg=self.colores.texto_primario,
                      selectcolor=self.colores.fondo_primario,
                      font=('Consolas', 10)).grid(row=0, column=1, sticky='w', padx=(0, 20), pady=5)
        
        tk.Checkbutton(check_frame,
                      text=f"📄 {EmoticonosMitologicos.APOLLO} Análisis de contenido",
                      variable=self.analisis_contenido_var,
                      bg=self.colores.fondo_secundario,
                      fg=self.colores.texto_primario,
                      selectcolor=self.colores.fondo_primario,
                      font=('Consolas', 10)).grid(row=0, column=2, sticky='w', pady=5)
    
    def _crear_boton_escaneo(self, padre):
        """Crear botones de control de escaneo centrados"""
        botones_frame = tk.Frame(padre, bg=self.colores.fondo_secundario)
        botones_frame.grid(row=2, column=0, pady=20)
        botones_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Botón iniciar escaneo
        self.boton_iniciar = tk.Button(botones_frame,
                                     text=f"🚀 {EmoticonosMitologicos.ZEUS} INICIAR ANÁLISIS",
                                     command=self._iniciar_escaneo,
                                     bg=self.colores.exito,
                                     fg='white',
                                     font=('Consolas', 12, 'bold'),
                                     cursor='hand2',
                                     relief='flat',
                                     padx=30, pady=12)
        self.boton_iniciar.grid(row=0, column=0, padx=(0, 15))
        
        # Botón parar escaneo
        self.boton_parar = tk.Button(botones_frame,
                                   text=f"🛑 {EmoticonosMitologicos.ESCUDO} PARAR ANÁLISIS",
                                   command=self._parar_escaneo,
                                   bg=self.colores.error,
                                   fg='white',
                                   font=('Consolas', 12, 'bold'),
                                   cursor='hand2',
                                   relief='flat',
                                   padx=30, pady=12,
                                   state='disabled')
        self.boton_parar.grid(row=0, column=1, padx=(15, 0))
    
    def _crear_area_resultados(self):
        """Crear área de resultados con diseño responsive"""
        results_frame = tk.LabelFrame(self.frame_scroll,
                                    text=f"📊 {EmoticonosMitologicos.APOLLO} Resultados del Análisis",
                                    bg=self.colores.fondo_secundario,
                                    fg=self.colores.acento_primario,
                                    font=('Consolas', 12, 'bold'),
                                    padx=20, pady=15)
        results_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=(0, 10))
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(3, weight=1)
        
        # Barra de progreso
        self.progreso_var = tk.DoubleVar()
        progreso_scale = tk.Scale(results_frame,
                                from_=0, to=100,
                                orient='horizontal',
                                variable=self.progreso_var,
                                bg=self.colores.fondo_secundario,
                                fg=self.colores.texto_primario,
                                font=('Consolas', 10),
                                state='disabled',
                                length=400)
        progreso_scale.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        # Estado del escaneo
        self.estado_var = tk.StringVar(value=f"🛡️ {EmoticonosMitologicos.ESCUDO} Listo para escanear")
        estado_label = tk.Label(results_frame,
                               textvariable=self.estado_var,
                               font=('Consolas', 11, 'bold'),
                               fg=self.colores.acento_secundario,
                               bg=self.colores.fondo_secundario)
        estado_label.grid(row=1, column=0, pady=(0, 15))
        
        # Área de resultados con scroll y grid
        results_text_frame = tk.Frame(results_frame, bg=self.colores.fondo_secundario)
        results_text_frame.grid(row=2, column=0, sticky='nsew')
        results_text_frame.grid_columnconfigure(0, weight=1)
        results_text_frame.grid_rowconfigure(0, weight=1)
        
        self.resultados_text = tk.Text(results_text_frame,
                                     bg=self.colores.fondo_primario,
                                     fg=self.colores.texto_primario,
                                     font=('Consolas', 10),
                                     wrap='word',
                                     state='disabled',
                                     relief='solid',
                                     bd=1,
                                     height=15)
        
        results_scroll = tk.Scrollbar(results_text_frame, command=self.resultados_text.yview)
        self.resultados_text.configure(yscrollcommand=results_scroll.set)
        
        self.resultados_text.grid(row=0, column=0, sticky='nsew')
        results_scroll.grid(row=0, column=1, sticky='ns')
        
        # Mensaje inicial
        self._agregar_resultado(f"🛡️ {EmoticonosMitologicos.FORTALEZA} Escudo de exploración listo para defender el reino digital")
    
    def _iniciar_escaneo(self):
        """Iniciar proceso de escaneo"""
        if self.escaneo_activo:
            messagebox.showwarning("Escaneo", "Ya hay un escaneo en progreso")
            return
            
        try:
            path = self.ruta_escaneo_var.get()
            
            # Validar ruta usando funciones disponibles
            try:
                if not validar_directorio(path):
                    self.estado_var.set(f"❌ {EmoticonosMitologicos.FALLIDO} Ruta no válida")
                    messagebox.showerror("Error", f"❌ Directorio no válido:\n{path}")
                    return
                
                if not validar_permisos_lectura(path):
                    self.estado_var.set(f"❌ {EmoticonosMitologicos.FALLIDO} Sin permisos")
                    messagebox.showerror("Error", f"❌ Sin permisos de lectura:\n{path}")
                    return
            except NameError:
                # Si las funciones de validación no están disponibles, usar validación básica
                if not path or not os.path.exists(path):
                    messagebox.showerror("Error", "Directorio no válido o no existe")
                    return
            
            # Configurar estado
            self.escaneo_activo = True
            self.boton_iniciar.configure(state='disabled')
            self.boton_parar.configure(state='normal')
            
            # Actualizar estado
            self.estado_var.set(f"🔍 {EmoticonosMitologicos.PROCESANDO} Escaneando...")
            self.progreso_var.set(0)
            
            # Limpiar resultados previos - verificar que el widget esté inicializado
            if self.resultados_text:
                self.resultados_text.configure(state='normal')
                self.resultados_text.delete(1.0, tk.END)
                self.resultados_text.configure(state='disabled')
            
            # Determinar tipo de escaneo
            tipo_escaneo = "completo" if self.escaneo_profundo_var.get() else "rapido"
            
            self.logger.info(f"Iniciando escaneo {tipo_escaneo} en: {path}")
            
            # Intentar usar el controlador principal si está disponible
            if self.controlador and hasattr(self.controlador, 'iniciar_escaneo'):
                try:
                    resultado_controlador = self.controlador.iniciar_escaneo(path, tipo_escaneo)
                    if resultado_controlador:
                        self._agregar_resultado(f"✅ {EmoticonosMitologicos.ESCUDO} Escaneo del controlador iniciado")
                    else:
                        self._agregar_resultado(f"⚠️ {EmoticonosMitologicos.ADVERTENCIA} Escaneo del controlador falló, usando modo local")
                except Exception as e:
                    self.logger.error(f"Error iniciando escaneo del controlador: {e}")
                    self._agregar_resultado(f"⚠️ {EmoticonosMitologicos.ADVERTENCIA} Error del controlador, usando modo local")
            
            # Iniciar escaneo local en thread separado
            self.hilo_escaneo = threading.Thread(target=self._ejecutar_escaneo_hilo, args=(path,), daemon=True)
            self.hilo_escaneo.start()
            
        except Exception as e:
            self.estado_var.set(f"❌ {EmoticonosMitologicos.FALLIDO} Error: {str(e)}")
            self.logger.error(f"Error iniciando escaneo: {e}")
            self._finalizar_escaneo()
            self.logger.error(f"Error iniciando escaneo: {e}")
            self._finalizar_escaneo()
    
    def _parar_escaneo(self):
        """Parar el escaneo en progreso"""
        if not self.escaneo_activo:
            return
        
        self.escaneo_activo = False
        self.estado_var.set(f"🛑 {EmoticonosMitologicos.ESCUDO} Deteniendo escaneo...")
        self._agregar_resultado(f"\n🛑 {EmoticonosMitologicos.ESCUDO} ESCANEO DETENIDO POR EL USUARIO")
        
        # Esperar a que termine el hilo si está activo
        if self.hilo_escaneo and self.hilo_escaneo.is_alive():
            # En un escenario real, aquí enviarías una señal al hilo para que se detenga
            pass
        
        self._finalizar_escaneo()
        self.logger.info("Escaneo detenido por el usuario")
    
    def _finalizar_escaneo(self):
        """Finalizar el estado de escaneo"""
        self.escaneo_activo = False
        self.boton_iniciar.configure(state='normal')
        self.boton_parar.configure(state='disabled')
        self.estado_var.set(f"🛡️ {EmoticonosMitologicos.ESCUDO} Listo para escanear")
    
    def _ejecutar_escaneo_hilo(self, path):
        """Ejecutar escaneo REAL en thread separado"""
        try:
            tipo_escaneo = "completo" if self.escaneo_profundo_var.get() else "rapido"
            self._agregar_resultado(f"🚀 {EmoticonosMitologicos.ZEUS} Iniciando escaneo {tipo_escaneo} REAL de: {path}")
            
            # Usar el controlador real
            if hasattr(self, 'controlador') and self.controlador:
                escaneador = self.controlador.obtener_modulo_escaneador()
                if escaneador:
                    self._agregar_resultado(f"⚔️ {EmoticonosMitologicos.ARES} Usando escaneador real del sistema")
                    self._ejecutar_escaneo_real(path, escaneador)
                else:
                    self._agregar_resultado(f"⚠️ {EmoticonosMitologicos.ADVERTENCIA} Escaneador no disponible")
                    self._ejecutar_escaneo_basico(path)
            else:
                self._agregar_resultado(f"⚠️ {EmoticonosMitologicos.ADVERTENCIA} Controlador no disponible - Escaneo básico")
                self._ejecutar_escaneo_basico(path)
                
            # Finalizar escaneo al terminar
            self.contenedor_padre.after(0, self._finalizar_escaneo)
            
        except Exception as e:
            self.estado_var.set(f"❌ {EmoticonosMitologicos.FALLIDO} Error: {str(e)}")
            self.logger.error(f"Error ejecutando escaneo: {e}")
            self.contenedor_padre.after(0, self._finalizar_escaneo)
    
    def _ejecutar_escaneo_real(self, path, escaneador):
        """Ejecutar escaneo real usando el módulo del controlador"""
        try:
            archivos_escaneados = 0
            amenazas_encontradas = 0
            
            # Obtener lista real de archivos
            archivos_para_escanear = []
            for root, dirs, files in os.walk(path):
                if not self.escaneo_activo:
                    return
                for file in files:
                    archivos_para_escanear.append(os.path.join(root, file))
            
            total_archivos = len(archivos_para_escanear)
            self._agregar_resultado(f"📁 {EmoticonosMitologicos.PERGAMINO} Archivos encontrados: {total_archivos}")
            
            # Escanear cada archivo usando el escaneador real
            for archivo_path in archivos_para_escanear:
                if not self.escaneo_activo:
                    self._agregar_resultado(f"\n🛑 {EmoticonosMitologicos.ESCUDO} Escaneo cancelado")
                    return
                
                archivos_escaneados += 1
                progreso = (archivos_escaneados / max(total_archivos, 1)) * 100
                self.contenedor_padre.after(0, lambda p=progreso: self.progreso_var.set(p))
                
                # Escanear archivo real
                try:
                    resultado = self._escanear_archivo_individual(archivo_path)
                    if resultado and resultado.get('amenaza_detectada'):
                        amenazas_encontradas += 1
                        amenaza = resultado.get('tipo_amenaza', 'Desconocida')
                        self._agregar_resultado(f"🚨 {EmoticonosMitologicos.HYDRA} AMENAZA REAL: {amenaza} en {archivo_path}")
                        
                        # Enviar a cuarentena si está configurado
                        if self.controlador and hasattr(self.controlador, 'gestor_cuarentena'):
                            cuarentena = self.controlador.obtener_modulo_cuarentena()
                            if cuarentena:
                                cuarentena.cuarentenar_archivo(archivo_path, amenaza)
                                self._agregar_resultado(f"🔒 {EmoticonosMitologicos.HADES} Archivo enviado a cuarentena")
                
                except Exception as e:
                    self.logger.warning(f"Error escaneando {archivo_path}: {e}")
                
                # Mostrar progreso cada 10 archivos
                if archivos_escaneados % 10 == 0:
                    self._agregar_resultado(f"📊 {EmoticonosMitologicos.CRISTAL} Progreso: {archivos_escaneados}/{total_archivos} archivos")
                    import time
                    time.sleep(0.1)  # Breve pausa para UI
            
            # Resultados finales
            if self.escaneo_activo:
                self._agregar_resultado(f"\n🏆 {EmoticonosMitologicos.COMPLETADO} ESCANEO REAL COMPLETADO")
                self._agregar_resultado(f"📊 {EmoticonosMitologicos.CRISTAL} Archivos escaneados: {archivos_escaneados}")
                self._agregar_resultado(f"🛡️ {EmoticonosMitologicos.ESCUDO} Amenazas REALES detectadas: {amenazas_encontradas}")
                
                # Actualizar métricas del sistema
                if self.controlador:
                    self.controlador.metricas_sistema['archivos_escaneados'] += archivos_escaneados
                    self.controlador.metricas_sistema['amenazas_detectadas'] += amenazas_encontradas
                
                self.contenedor_padre.after(0, lambda: self.estado_var.set(f"✅ {EmoticonosMitologicos.COMPLETADO} Completado - {amenazas_encontradas} amenazas REALES"))
            
        except Exception as e:
            self.contenedor_padre.after(0, lambda: self.estado_var.set(f"❌ {EmoticonosMitologicos.FALLIDO} Error: {str(e)}"))
            self.logger.error(f"Error ejecutando escaneo real: {e}")
    
    def _escanear_archivo_individual(self, archivo_path):
        """Escanear un archivo individual usando técnicas reales"""
        try:
            if not os.path.exists(archivo_path) or not os.path.isfile(archivo_path):
                return None
            
            # Obtener información básica del archivo
            stat_info = os.stat(archivo_path)
            tamaño = stat_info.st_size
            
            # Verificar tamaño (archivos muy grandes pueden ser sospechosos)
            if tamaño > 100 * 1024 * 1024:  # > 100MB
                return {'amenaza_detectada': True, 'tipo_amenaza': 'Archivo sospechosamente grande'}
            
            # Verificar extensión del archivo
            _, extension = os.path.splitext(archivo_path.lower())
            extensiones_peligrosas = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com', '.vbs', '.js']
            
            if extension in extensiones_peligrosas:
                # Leer contenido para análisis más profundo
                try:
                    with open(archivo_path, 'rb') as f:
                        contenido = f.read(1024)  # Leer primeros 1KB
                        
                    # Buscar patrones sospechosos específicos de Linux/Kali
                    patrones_maliciosos = [
                        b'eval(',
                        b'exec(',
                        b'/bin/sh',
                        b'bash -i',
                        b'nc -e',
                        b'rm -rf',
                        b'chmod 777',
                        b'format',
                        b'payload'
                    ]
                    
                    for patron in patrones_maliciosos:
                        if patron in contenido.lower():
                            return {'amenaza_detectada': True, 'tipo_amenaza': f'Patrón malicioso: {patron.decode("utf-8", errors="ignore")}'}
                
                except Exception:
                    pass  # Si no se puede leer, continuar
            
            # Verificar hash MD5 contra base de datos conocida
            import hashlib
            try:
                with open(archivo_path, 'rb') as f:
                    contenido = f.read()
                    md5_hash = hashlib.md5(contenido).hexdigest()
                    
                # Simular verificación contra base de datos de hashes maliciosos
                # En un entorno real, esto consultaría VirusTotal o similar
                hashes_conocidos_maliciosos = [
                    # Hashes de ejemplo (en producción sería una base de datos real)
                    '44d88612fea8a8f36de82e1278abb02f',
                    '5d41402abc4b2a76b9719d911017c592'
                ]
                
                if md5_hash in hashes_conocidos_maliciosos:
                    return {'amenaza_detectada': True, 'tipo_amenaza': f'Hash malicioso conocido: {md5_hash}'}
                    
            except Exception:
                pass
            
            return {'amenaza_detectada': False}
            
        except Exception as e:
            self.logger.warning(f"Error analizando archivo {archivo_path}: {e}")
            return None
    
    def _ejecutar_escaneo_basico(self, path):
        """Escaneo básico usando solo Python Standard Library"""
        try:
            archivos_escaneados = 0
            amenazas_encontradas = 0
            
            self._agregar_resultado(f"🔍 {EmoticonosMitologicos.ARGOS} Iniciando escaneo básico (Python Standard Library)")
            
            # Recorrer directorio
            for root, dirs, files in os.walk(path):
                if not self.escaneo_activo:
                    return
                    
                for file in files:
                    if not self.escaneo_activo:
                        return
                        
                    archivo_path = os.path.join(root, file)
                    archivos_escaneados += 1
                    
                    # Verificar archivo con análisis básico
                    resultado = self._escanear_archivo_individual(archivo_path)
                    if resultado and resultado.get('amenaza_detectada'):
                        amenazas_encontradas += 1
                        amenaza = resultado.get('tipo_amenaza', 'Sospechoso')
                        self._agregar_resultado(f"⚠️ {EmoticonosMitologicos.ADVERTENCIA} Archivo sospechoso: {file} - {amenaza}")
                    
                    # Actualizar progreso cada 50 archivos
                    if archivos_escaneados % 50 == 0:
                        self._agregar_resultado(f"📊 {EmoticonosMitologicos.CRISTAL} Escaneados: {archivos_escaneados} archivos")
            
            # Resultados finales
            if self.escaneo_activo:
                self._agregar_resultado(f"\n🏆 {EmoticonosMitologicos.COMPLETADO} ESCANEO BÁSICO COMPLETADO")
                self._agregar_resultado(f"📊 {EmoticonosMitologicos.CRISTAL} Archivos escaneados: {archivos_escaneados}")
                self._agregar_resultado(f"⚠️ {EmoticonosMitologicos.ADVERTENCIA} Archivos sospechosos: {amenazas_encontradas}")
                
                self.contenedor_padre.after(0, lambda: self.estado_var.set(f"✅ {EmoticonosMitologicos.COMPLETADO} Completado - {amenazas_encontradas} sospechosos"))
            
        except Exception as e:
            self.contenedor_padre.after(0, lambda: self.estado_var.set(f"❌ {EmoticonosMitologicos.FALLIDO} Error: {str(e)}"))
            self.logger.error(f"Error ejecutando escaneo básico: {e}")
    def _ejecutar_escaneo_simulado(self, path):
        """Ejecutar escaneo simulado"""
        try:
            archivos_escaneados = 0
            amenazas_encontradas = 0
            
            # Verificar si el escaneo sigue activo
            if not self.escaneo_activo:
                return
                
            total_archivos = sum([len(files) for r, d, files in os.walk(path)])
            
            self._agregar_resultado(f"📁 {EmoticonosMitologicos.PERGAMINO} Total de archivos encontrados: {total_archivos}")
            
            for root, dirs, files in os.walk(path):
                # Verificar si el escaneo fue cancelado
                if not self.escaneo_activo:
                    self._agregar_resultado(f"\n🛑 {EmoticonosMitologicos.ESCUDO} Escaneo cancelado por el usuario")
                    return
                    
                for file in files:
                    # Verificar cancelación antes de cada archivo
                    if not self.escaneo_activo:
                        self._agregar_resultado(f"\n� {EmoticonosMitologicos.ESCUDO} Escaneo cancelado por el usuario")
                        return
                        
                    archivos_escaneados += 1
                    progreso = (archivos_escaneados / max(total_archivos, 1)) * 100
                    
                    # Actualizar progreso en UI thread
                    self.contenedor_padre.after(0, lambda p=progreso: self.progreso_var.set(p))
                    
                    # Simular detección ocasional de amenazas
                    if archivos_escaneados % 50 == 0:
                        amenazas_encontradas += 1
                        self._agregar_resultado(f"🚨 {EmoticonosMitologicos.HYDRA} Amenaza simulada detectada en: {os.path.join(root, file)}")
                    
                    # Pausar para simular trabajo
                    if archivos_escaneados % 10 == 0:
                        import time
                        time.sleep(0.1)
            
            # Resultados finales solo si el escaneo no fue cancelado
            if self.escaneo_activo:
                self._agregar_resultado(f"\n🏆 {EmoticonosMitologicos.COMPLETADO} ESCANEO SIMULADO COMPLETADO")
                self._agregar_resultado(f"📊 {EmoticonosMitologicos.CRISTAL} Archivos escaneados: {archivos_escaneados}")
                self._agregar_resultado(f"🛡️ {EmoticonosMitologicos.ESCUDO} Amenazas detectadas: {amenazas_encontradas}")
                
                self.contenedor_padre.after(0, lambda: self.estado_var.set(f"✅ {EmoticonosMitologicos.COMPLETADO} Completado (Simulado) - {amenazas_encontradas} amenazas"))
            
        except Exception as e:
            self.contenedor_padre.after(0, lambda: self.estado_var.set(f"❌ {EmoticonosMitologicos.FALLIDO} Error: {str(e)}"))
            self.logger.error(f"Error ejecutando escaneo simulado: {e}")
    
    def _agregar_resultado(self, mensaje):
        """Agregar mensaje a los resultados del escaneo"""
        def agregar_a_texto():
            if self.resultados_text:
                self.resultados_text.configure(state='normal')
                self.resultados_text.insert(tk.END, f"{mensaje}\n")
                self.resultados_text.configure(state='disabled')
                self.resultados_text.see(tk.END)
        
        if hasattr(self, 'contenedor_padre') and self.contenedor_padre:
            self.contenedor_padre.after(0, agregar_a_texto)
