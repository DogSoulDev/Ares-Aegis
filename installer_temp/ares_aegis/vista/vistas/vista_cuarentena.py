#!/usr/bin/env python3
"""
Vista Cuarentena para Ares Aegis
Interfaz del módulo de cuarentena
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import os
from datetime import datetime
from ..componentes_ui.emoticonos_mitologicos import EmoticonosMitologicos
from ..componentes_ui.sistema_ayuda import SistemaAyuda

class VistaCuarentena:
    """Vista para gestión de archivos en cuarentena"""
    
    def __init__(self, contenedor_padre, controlador, colores):
        self.contenedor_padre = contenedor_padre
        self.controlador = controlador
        self.colores = colores
        self.logger = logging.getLogger('ares_aegis.vista.vista_cuarentena')
        
        # Variables de UI
        self.total_archivos_var = None
        self.tamaño_total_var = None
        self.tree_cuarentena = None
        self.frame_scroll = None
        
        # Frame contenedor principal
        self.container = None
        
        # Sistema de ayuda
        self.sistema_ayuda = SistemaAyuda(colores)
        
    def mostrar_informacion(self):
        """Mostrar información de ayuda sobre la Cuarentena"""
        info_text = """🛡️ CUARENTENA DE ARCHIVOS - INFORMACIÓN

🔒 FUNCIONALIDADES PRINCIPALES:
• Aislamiento seguro de archivos sospechosos
• Gestión completa de archivos en cuarentena
• Restauración segura de archivos legítimos
• Eliminación permanente de amenazas

⚡ OPERACIONES DISPONIBLES:
• Mover archivos a cuarentena
• Restaurar archivos desde cuarentena
• Eliminar archivos permanentemente
• Analizar archivos aislados

🎯 GESTIÓN DE CUARENTENA:
• Lista de archivos en cuarentena
• Información detallada de cada archivo
• Fecha y hora de cuarentena
• Razón del aislamiento

🔧 CÓMO USAR:
1. Los archivos se mueven automáticamente desde el escaneador
2. Revisa la lista de archivos en cuarentena
3. Analiza cada archivo antes de decidir
4. Restaura archivos legítimos o elimina amenazas

⚠️ PRISIÓN DE HADES:
• Aislamiento total del sistema
• Sin acceso desde aplicaciones
• Backup de metadatos original
• Historial de operaciones

📊 ESTADO DE ARCHIVOS:
• 🔒 EN CUARENTENA: Aislado de forma segura
• 📅 FECHA: Momento del aislamiento
• 📂 ORIGEN: Ubicación original del archivo
• ⚠️ MOTIVO: Razón del aislamiento

💡 RECOMENDACIONES DE SEGURIDAD:
• Analiza cuidadosamente antes de restaurar
• Mantén archivos sospechosos aislados
• Elimina permanentemente las amenazas confirmadas
• Revisa periódicamente la cuarentena

🔐 SEGURIDAD DEL SISTEMA:
• Los archivos en cuarentena no pueden ejecutarse
• Aislamiento completo del sistema operativo
• Backup automático de información original
• Registro de todas las operaciones"""
        
        messagebox.showinfo("Información - Cuarentena de Archivos", info_text)
        
    def crear_vista(self, area_contenido=None):
        """Crear vista de cuarentena"""
        try:
            # Limpiar contenedor padre
            for widget in self.contenedor_padre.winfo_children():
                widget.destroy()
            
            # Frame principal
            self.frame_principal = tk.Frame(self.contenedor_padre, bg=self.colores.fondo_secundario)
            self.frame_principal.pack(fill='both', expand=True, padx=15, pady=15)
                
            # Configurar grid del frame principal con mejores proporciones
            self.frame_principal.grid_rowconfigure(0, weight=0)  # Header fijo
            self.frame_principal.grid_rowconfigure(1, weight=1)  # Contenido expandible
            self.frame_principal.grid_columnconfigure(0, weight=1)
            
            # Header
            self._crear_header_cuarentena()
            
            # Container principal con scroll
            container = tk.Frame(self.frame_principal, bg=self.colores.fondo_secundario)
            container.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)
            
            # Canvas y scrollbar
            canvas = tk.Canvas(container, bg=self.colores.fondo_secundario, highlightthickness=0)
            scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
            
            self.frame_scroll = tk.Frame(canvas, bg=self.colores.fondo_secundario)
            self.frame_scroll.grid_columnconfigure(0, weight=1)
            
            # Configurar scroll
            canvas.create_window((0, 0), window=self.frame_scroll, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Grid para canvas y scrollbar
            canvas.grid(row=0, column=0, sticky='nsew')
            scrollbar.grid(row=0, column=1, sticky='ns')
            
            # Panel de control
            self._crear_panel_control()
            
            # Lista de archivos en cuarentena
            self._crear_lista_cuarentena()
            
            # Panel de acciones
            self._crear_panel_acciones()
            
            # Cargar archivos de cuarentena
            self._cargar_archivos_cuarentena()
            
            # Bind mouse wheel
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind("<MouseWheel>", _on_mousewheel)
            
            # Update scroll region
            def _configure_scroll_region(event=None):
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            self.frame_scroll.bind("<Configure>", _configure_scroll_region)
            
            self.logger.info("Vista cuarentena creada exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error creando vista cuarentena: {e}")
            messagebox.showerror("Error", f"Error al crear vista de cuarentena: {e}")
    
    def _crear_header_cuarentena(self):
        """Crear header de cuarentena con diseño centrado"""
        header = tk.Frame(self.frame_principal, bg=self.colores.fondo_terciario, height=85)
        header.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)
        header.grid_rowconfigure(0, weight=1)
        
        # Título centrado
        tk.Label(header,
                text=f"🔒 {EmoticonosMitologicos.HADES} Prisión de Hades - Gestión de Cuarentena",
                font=('Consolas', 16, 'bold'),
                fg=self.colores.acento_primario,
                bg=self.colores.fondo_terciario).grid(row=0, column=0, pady=15)
        
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
        """Crear panel de control de cuarentena con grid responsive"""
        control_frame = tk.LabelFrame(self.frame_scroll,
                                    text=f"⚙️ {EmoticonosMitologicos.HADES} Control de Cuarentena",
                                    bg=self.colores.fondo_secundario,
                                    fg=self.colores.acento_primario,
                                    font=('Consolas', 12, 'bold'),
                                    padx=20, pady=15)
        control_frame.grid(row=0, column=0, sticky='ew', padx=20, pady=10)
        control_frame.grid_columnconfigure(0, weight=1)
        
        # Estadísticas de cuarentena
        stats_frame = tk.Frame(control_frame, bg=self.colores.fondo_secundario)
        stats_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        
        self.total_archivos_var = tk.StringVar(value="0")
        self.tamaño_total_var = tk.StringVar(value="0 MB")
        
        tk.Label(stats_frame,
                text=f"📊 {EmoticonosMitologicos.CRISTAL} Estadísticas:",
                font=('Consolas', 10, 'bold'),
                fg=self.colores.texto_primario,
                bg=self.colores.fondo_secundario).pack(anchor='w')
        
        stats_info = tk.Frame(stats_frame, bg=self.colores.fondo_secundario)
        stats_info.pack(fill='x', pady=(5, 0))
        
        tk.Label(stats_info,
                text="Archivos en cuarentena:",
                font=('Consolas', 9),
                fg=self.colores.texto_secundario,
                bg=self.colores.fondo_secundario).pack(side='left')
        
        tk.Label(stats_info,
                textvariable=self.total_archivos_var,
                font=('Consolas', 9, 'bold'),
                fg=self.colores.acento_secundario,
                bg=self.colores.fondo_secundario).pack(side='left', padx=(5, 20))
        
        tk.Label(stats_info,
                text="Tamaño total:",
                font=('Consolas', 9),
                fg=self.colores.texto_secundario,
                bg=self.colores.fondo_secundario).pack(side='left')
        
        tk.Label(stats_info,
                textvariable=self.tamaño_total_var,
                font=('Consolas', 9, 'bold'),
                fg=self.colores.acento_secundario,
                bg=self.colores.fondo_secundario).pack(side='left', padx=(5, 0))
        
        # Botón para agregar archivo manualmente
        tk.Button(control_frame,
                 text=f"📜 {EmoticonosMitologicos.PERGAMINO} Agregar archivo a cuarentena",
                 command=self._agregar_archivo_cuarentena,
                 bg=self.colores.acento_primario,
                 fg=self.colores.fondo_primario,
                 font=('Consolas', 10, 'bold'),
                 cursor='hand2').grid(row=1, column=0, pady=10)
    
    def _crear_lista_cuarentena(self):
        """Crear lista de archivos en cuarentena"""
        lista_frame = tk.LabelFrame(self.frame_scroll,
                                  text=f"📋 {EmoticonosMitologicos.PERGAMINO} Archivos en Cuarentena",
                                  bg=self.colores.fondo_secundario,
                                  fg=self.colores.acento_primario,
                                  font=('Consolas', 12, 'bold'))
        lista_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
        lista_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview para mostrar archivos
        tree_frame = tk.Frame(lista_frame, bg=self.colores.fondo_secundario)
        tree_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Configurar columnas
        columnas = ('nombre', 'fecha', 'tamaño', 'amenaza', 'ruta_original')
        self.tree_cuarentena = ttk.Treeview(tree_frame, columns=columnas, show='headings', height=10)
        
        # Definir encabezados
        self.tree_cuarentena.heading('nombre', text='Nombre del Archivo')
        self.tree_cuarentena.heading('fecha', text='Fecha de Cuarentena')
        self.tree_cuarentena.heading('tamaño', text='Tamaño')
        self.tree_cuarentena.heading('amenaza', text='Tipo de Amenaza')
        self.tree_cuarentena.heading('ruta_original', text='Ruta Original')
        
        # Configurar columnas
        self.tree_cuarentena.column('nombre', width=200, minwidth=150)
        self.tree_cuarentena.column('fecha', width=120, minwidth=100)
        self.tree_cuarentena.column('tamaño', width=80, minwidth=60)
        self.tree_cuarentena.column('amenaza', width=150, minwidth=100)
        self.tree_cuarentena.column('ruta_original', width=300, minwidth=200)
        
        # Scrollbar para treeview
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_cuarentena.yview)
        self.tree_cuarentena.configure(yscrollcommand=tree_scrollbar.set)
        
        # Grid para treeview y scrollbar
        self.tree_cuarentena.grid(row=0, column=0, sticky='nsew')
        tree_scrollbar.grid(row=0, column=1, sticky='ns')
    
    def _crear_panel_acciones(self):
        """Crear panel de acciones para archivos en cuarentena"""
        acciones_frame = tk.LabelFrame(self.frame_scroll,
                                     text=f"⚔️ {EmoticonosMitologicos.ARES} Acciones de Cuarentena",
                                     bg=self.colores.fondo_secundario,
                                     fg=self.colores.acento_primario,
                                     font=('Consolas', 12, 'bold'))
        acciones_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        # Configurar grid para 4 botones
        acciones_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Botones de acción
        tk.Button(acciones_frame,
                 text=f"🔓 {EmoticonosMitologicos.ATHENA} Restaurar archivo",
                 command=self._restaurar_archivo,
                 bg=self.colores.acento_secundario,
                 fg=self.colores.fondo_primario,
                 font=('Consolas', 10, 'bold'),
                 cursor='hand2').grid(row=0, column=0, padx=5, pady=10, sticky='ew')
        
        tk.Button(acciones_frame,
                 text=f"🛡️ Ignorar archivo",
                 command=self._ignorar_archivo,
                 bg=self.colores.naranja_fuego,
                 fg=self.colores.fondo_primario,
                 font=('Consolas', 10, 'bold'),
                 cursor='hand2').grid(row=0, column=1, padx=5, pady=10, sticky='ew')
        
        tk.Button(acciones_frame,
                 text=f"🗑️ {EmoticonosMitologicos.HADES} Eliminar permanentemente",
                 command=self._eliminar_archivo_permanente,
                 bg='#d32f2f',
                 fg=self.colores.fondo_primario,
                 font=('Consolas', 10, 'bold'),
                 cursor='hand2').grid(row=0, column=2, padx=5, pady=10, sticky='ew')
        
        tk.Button(acciones_frame,
                 text=f"🔍 {EmoticonosMitologicos.CRISTAL} Ver detalles",
                 command=self._ver_detalles_archivo,
                 bg=self.colores.acento_terciario,
                 fg=self.colores.fondo_primario,
                 font=('Consolas', 10, 'bold'),
                 cursor='hand2').grid(row=0, column=3, padx=5, pady=10, sticky='ew')
    
    def _cargar_archivos_cuarentena(self):
        """Cargar y mostrar archivos en cuarentena"""
        try:
            # Limpiar treeview
            for item in self.tree_cuarentena.get_children():
                self.tree_cuarentena.delete(item)
            
            # Obtener archivos de cuarentena del controlador
            if hasattr(self.controlador, 'gestor_cuarentena') and self.controlador.gestor_cuarentena:
                archivos = self.controlador.gestor_cuarentena.listar_archivos_cuarentena()
                
                total_archivos = len(archivos)
                tamaño_total = 0
                
                for archivo in archivos:
                    # Insertar en treeview
                    self.tree_cuarentena.insert('', 'end', values=(
                        archivo.get('nombre', 'Desconocido'),
                        archivo.get('fecha_cuarentena', 'N/A'),
                        archivo.get('tamaño', 'N/A'),
                        archivo.get('tipo_amenaza', 'Desconocido'),
                        archivo.get('ruta_original', 'N/A')
                    ))
                    
                    # Sumar tamaño
                    try:
                        tamaño_total += int(archivo.get('tamaño_bytes', 0))
                    except (ValueError, TypeError):
                        pass
                
                # Actualizar estadísticas
                self.total_archivos_var.set(str(total_archivos))
                self.tamaño_total_var.set(f"{tamaño_total / (1024*1024):.2f} MB")
            else:
                # Si no hay gestor de cuarentena, mostrar 0
                self.total_archivos_var.set("0")
                self.tamaño_total_var.set("0 MB")
                
        except Exception as e:
            self.logger.error(f"Error cargando archivos de cuarentena: {e}")
    
    def _agregar_archivo_cuarentena(self):
        """Agregar archivo manualmente a cuarentena"""
        try:
            archivo = filedialog.askopenfilename(
                title="Seleccionar archivo para agregar a cuarentena",
                filetypes=[("Todos los archivos", "*.*")]
            )
            
            if archivo:
                if hasattr(self.controlador, 'gestor_cuarentena') and self.controlador.gestor_cuarentena:
                    resultado = self.controlador.gestor_cuarentena.poner_en_cuarentena(
                        archivo, "Agregado manualmente por el usuario"
                    )
                    
                    if resultado:
                        messagebox.showinfo("Éxito", f"Archivo {os.path.basename(archivo)} agregado a cuarentena")
                        self._cargar_archivos_cuarentena()
                    else:
                        messagebox.showerror("Error", "No se pudo agregar el archivo a cuarentena")
                else:
                    messagebox.showwarning("Advertencia", "Gestor de cuarentena no disponible")
                    
        except Exception as e:
            self.logger.error(f"Error agregando archivo a cuarentena: {e}")
            messagebox.showerror("Error", f"Error al agregar archivo: {e}")
    
    def _restaurar_archivo(self):
        """Restaurar archivo seleccionado de cuarentena"""
        try:
            seleccion = self.tree_cuarentena.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un archivo para restaurar")
                return
            
            item = self.tree_cuarentena.item(seleccion[0])
            nombre_archivo = item['values'][0]
            
            # Confirmar restauración
            if messagebox.askyesno("Confirmar", f"¿Restaurar el archivo '{nombre_archivo}'?"):
                if hasattr(self.controlador, 'gestor_cuarentena') and self.controlador.gestor_cuarentena:
                    resultado = self.controlador.gestor_cuarentena.restaurar_archivo(nombre_archivo)
                    
                    if resultado:
                        messagebox.showinfo("Éxito", f"Archivo '{nombre_archivo}' restaurado exitosamente")
                        self._cargar_archivos_cuarentena()
                    else:
                        messagebox.showerror("Error", "No se pudo restaurar el archivo")
                else:
                    messagebox.showwarning("Advertencia", "Gestor de cuarentena no disponible")
                    
        except Exception as e:
            self.logger.error(f"Error restaurando archivo: {e}")
            messagebox.showerror("Error", f"Error al restaurar archivo: {e}")
    
    def _ignorar_archivo(self):
        """Ignorar archivo - agregarlo a lista blanca para futuras detecciones"""
        try:
            seleccion = self.tree_cuarentena.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un archivo para ignorar")
                return
            
            item = self.tree_cuarentena.item(seleccion[0])
            nombre_archivo = item['values'][0]
            
            # Confirmar acción de ignorar
            respuesta = messagebox.askyesno("🛡️ Confirmar Ignorar Archivo", 
                                          f"¿Ignorar futuras detecciones del archivo '{nombre_archivo}'?\n\n"
                                          "El archivo será:\n"
                                          "• Restaurado a su ubicación original\n"
                                          "• Agregado a la lista blanca de archivos ignorados\n"
                                          "• No será detectado en futuras auditorías\n\n"
                                          "⚠️ Solo use esta opción si está seguro de que el archivo es seguro.")
            
            if respuesta:
                try:
                    # Restaurar archivo primero
                    if hasattr(self.controlador, 'gestor_cuarentena') and self.controlador.gestor_cuarentena:
                        resultado = self.controlador.gestor_cuarentena.restaurar_archivo(nombre_archivo)
                        
                        if resultado:
                            # Agregar a lista blanca (implementar según la arquitectura del sistema)
                            self._agregar_a_lista_blanca(nombre_archivo)
                            
                            messagebox.showinfo("✅ Archivo Ignorado", 
                                              f"Archivo '{nombre_archivo}' restaurado e ignorado exitosamente.\n"
                                              "No será detectado en futuras auditorías.")
                            self._cargar_archivos_cuarentena()
                        else:
                            messagebox.showerror("Error", "No se pudo restaurar el archivo")
                    else:
                        messagebox.showwarning("Advertencia", "Gestor de cuarentena no disponible")
                        
                except Exception as e:
                    self.logger.error(f"Error procesando archivo ignorado: {e}")
                    messagebox.showerror("Error", f"Error al procesar archivo: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error ignorando archivo: {e}")
            messagebox.showerror("Error", f"Error al ignorar archivo: {e}")
    
    def _agregar_a_lista_blanca(self, nombre_archivo):
        """Agregar archivo a lista blanca del sistema"""
        try:
            # Crear archivo de lista blanca si no existe
            lista_blanca_path = "configuracion/archivos_ignorados.txt"
            os.makedirs(os.path.dirname(lista_blanca_path), exist_ok=True)
            
            # Leer lista existente
            archivos_ignorados = set()
            if os.path.exists(lista_blanca_path):
                with open(lista_blanca_path, 'r', encoding='utf-8') as f:
                    archivos_ignorados = set(line.strip() for line in f if line.strip())
            
            # Agregar nuevo archivo
            archivos_ignorados.add(nombre_archivo)
            
            # Guardar lista actualizada
            with open(lista_blanca_path, 'w', encoding='utf-8') as f:
                for archivo in sorted(archivos_ignorados):
                    f.write(f"{archivo}\n")
            
            self.logger.info(f"Archivo '{nombre_archivo}' agregado a lista blanca")
            
        except Exception as e:
            self.logger.error(f"Error agregando archivo a lista blanca: {e}")
            raise
    
    def _eliminar_archivo_permanente(self):
        """Eliminar archivo permanentemente de cuarentena"""
        try:
            seleccion = self.tree_cuarentena.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un archivo para eliminar")
                return
            
            item = self.tree_cuarentena.item(seleccion[0])
            nombre_archivo = item['values'][0]
            
            # Confirmar eliminación
            if messagebox.askyesno("⚠️ Confirmar Eliminación", 
                                 f"¿Eliminar PERMANENTEMENTE el archivo '{nombre_archivo}'?\n\n"
                                 "Esta acción NO se puede deshacer."):
                if hasattr(self.controlador, 'gestor_cuarentena') and self.controlador.gestor_cuarentena:
                    resultado = self.controlador.gestor_cuarentena.eliminar_archivo_permanente(nombre_archivo)
                    
                    if resultado:
                        messagebox.showinfo("Éxito", f"Archivo '{nombre_archivo}' eliminado permanentemente")
                        self._cargar_archivos_cuarentena()
                    else:
                        messagebox.showerror("Error", "No se pudo eliminar el archivo")
                else:
                    messagebox.showwarning("Advertencia", "Gestor de cuarentena no disponible")
                    
        except Exception as e:
            self.logger.error(f"Error eliminando archivo: {e}")
            messagebox.showerror("Error", f"Error al eliminar archivo: {e}")
    
    def _ver_detalles_archivo(self):
        """Ver detalles del archivo seleccionado"""
        try:
            seleccion = self.tree_cuarentena.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un archivo para ver detalles")
                return
            
            item = self.tree_cuarentena.item(seleccion[0])
            valores = item['values']
            
            # Crear ventana de detalles
            ventana_detalles = tk.Toplevel()
            ventana_detalles.title(f"Detalles - {valores[0]}")
            ventana_detalles.geometry("500x400")
            ventana_detalles.configure(bg=self.colores.fondo_secundario)
            
            # Texto con detalles
            texto_detalles = tk.Text(ventana_detalles, 
                                   bg=self.colores.fondo_primario,
                                   fg=self.colores.texto_primario,
                                   font=('Consolas', 10),
                                   wrap='word')
            texto_detalles.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Información del archivo
            detalles = f"""
🔒 DETALLES DEL ARCHIVO EN CUARENTENA

📄 Nombre: {valores[0]}
📅 Fecha de cuarentena: {valores[1]}
📊 Tamaño: {valores[2]}
⚠️ Tipo de amenaza: {valores[3]}
📂 Ruta original: {valores[4]}

═══════════════════════════════════

🛡️ Estado: En cuarentena
🏛️ Sistema: Ares Aegis - Prisión de Hades
⚔️ Protección: Activa
            """
            
            texto_detalles.insert('1.0', detalles)
            texto_detalles.configure(state='disabled')
            
        except Exception as e:
            self.logger.error(f"Error mostrando detalles: {e}")
            messagebox.showerror("Error", f"Error al mostrar detalles: {e}")
