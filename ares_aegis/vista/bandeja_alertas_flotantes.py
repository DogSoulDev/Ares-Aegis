# Bandeja de Alertas Flotantes para Ares Aegis
# Implementación solo con librerías estándar de Python (Tkinter)

import tkinter as tk
import threading
import time

class BandejaAlertasFlotantes:
    def __init__(self, root):
        self.root = root
        self.alertas = []
        self.alerta_windows = []
        self.lock = threading.Lock()

    def mostrar_alerta(self, mensaje, tipo="info", duracion=5000, icono=None):
        """Muestra una alerta flotante animada en la esquina inferior derecha, con icono y cierre manual"""
        colores = {
            "info": ("#1b2d1f", "#69db7c", "🟢"),
            "advertencia": ("#2d251b", "#ffd93d", "🟡"),
            "critico": ("#2d1b1b", "#ff6b6b", "🔴")
        }
        bg, fg, icono_def = colores.get(tipo, ("#1b2d1f", "#69db7c", "🟢"))
        icono = icono or icono_def
        # Limitar máximo de alertas visibles
        max_alertas = 4
        if len(self.alerta_windows) >= max_alertas:
            self._cerrar_alerta(self.alerta_windows[0])
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg=bg)
        # Header con icono y botón cerrar
        header = tk.Frame(win, bg=bg)
        header.pack(fill="x", padx=2, pady=(2,0))
        icon_label = tk.Label(header, text=icono, bg=bg, fg=fg, font=("Segoe UI", 16, "bold"))
        icon_label.pack(side="left", padx=(8,2))
        btn_cerrar = tk.Button(header, text="✖", command=lambda: self._cerrar_alerta(win), bg=bg, fg=fg, borderwidth=0, font=("Segoe UI", 10, "bold"), activebackground=bg, activeforeground=fg, cursor="hand2")
        btn_cerrar.pack(side="right", padx=(0,6))
        # Mensaje
        label = tk.Label(win, text=mensaje, bg=bg, fg=fg, font=("Segoe UI", 11, "bold"), padx=18, pady=10, wraplength=260, justify="left")
        label.pack(fill="x")
        # Posicionar en la esquina inferior derecha
        self.root.update_idletasks()
        ancho = win.winfo_reqwidth()
        alto = win.winfo_reqheight()
        x = self.root.winfo_x() + self.root.winfo_width() - ancho - 30
        y = self.root.winfo_y() + self.root.winfo_height() - alto - 30 - (len(self.alerta_windows) * (alto + 10))
        win.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.alerta_windows.append(win)
        # Animación de fade-in
        win.attributes("-alpha", 0.0)
        self._fade_in(win)
        # Cerrar después de duración
        win.after(duracion, lambda: self._cerrar_alerta(win))

    def _fade_in(self, win, alpha=0.0):
        if alpha < 1.0:
            win.attributes("-alpha", alpha)
            win.after(20, lambda: self._fade_in(win, alpha + 0.1))
        else:
            win.attributes("-alpha", 1.0)

    def _cerrar_alerta(self, win):
        self._fade_out(win)
        # Reposicionar las alertas restantes tras cerrar una
        self.root.after(250, self._recolocar_alertas)

    def _recolocar_alertas(self):
        # Reposiciona todas las alertas abiertas para mantener el stacking
        self.root.update_idletasks()
        for idx, win in enumerate(self.alerta_windows):
            ancho = win.winfo_reqwidth()
            alto = win.winfo_reqheight()
            x = self.root.winfo_x() + self.root.winfo_width() - ancho - 30
            y = self.root.winfo_y() + self.root.winfo_height() - alto - 30 - (idx * (alto + 10))
            win.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _fade_out(self, win, alpha=1.0):
        if alpha > 0.0:
            win.attributes("-alpha", alpha)
            win.after(20, lambda: self._fade_out(win, alpha - 0.1))
        else:
            win.destroy()
            if win in self.alerta_windows:
                self.alerta_windows.remove(win)

# Uso: desde la interfaz principal, crear una instancia y llamar mostrar_alerta()
