import sys
import os
import json
import datetime
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Importamos las lógicas independientes
from logica_trono import cargar_datos, generar_turnos_base, generar_html_interactivo
from logica_miercoles import generar_cuadrillas_miercoles, generar_html_miercoles
from logica_viernes import generar_cuadrillas_viernes, generar_html_viernes
from logica_ensayos import generar_html_ensayo
from logica_informes import crear_html_informe

# ==========================================
# CONFIGURACIÓN Y COLORES
# ==========================================
CONFIG = {
    "peso_trono_kg": 2000,
    "peso_cruz_kg": 200,      
    "limite_peso_persona": 90,
    "plazas_turno_a": 36,
    "archivo_datos": "datos.json"
}

# Paleta Mayordomía "Modern UI"
C_MORADO = "#4F1243"
C_MORADO_HOVER = "#7a1b67"
C_MORADO_BG = "#2a0a23"
C_ORO = "#d4af37"
C_ORO_HOVER = "#b5952f"
C_BLANCO = "#ffffff"
C_GRIS_FONDO = "#f0f2f5"
C_TEXTO = "#333333"

# ==========================================
# CLASE PRINCIPAL DE LA INTERFAZ
# ==========================================
class GestorCofradeAPP:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Turnos Cristo de la Agonía V1.0 - Ntro. Padre Jesús Nazareno")
        self.root.geometry("1280x720") ## 1050x650 anterior
        self.root.configure(bg=C_GRIS_FONDO)
        self.root.resizable(False, False)

        # Variables de estado
        self.current_frame = None
        self.frames = {}
        
        # Contenedores Principales
        self.frame_menu = tk.Frame(self.root, bg=C_MORADO, width=250)
        self.frame_menu.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_menu.pack_propagate(False) 
        
        self.frame_main = tk.Frame(self.root, bg=C_GRIS_FONDO)
        self.frame_main.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.crear_menu_lateral()
        self.crear_pantallas()
        self.mostrar_pantalla("Inicio")

    # --- UTILIDADES ---
    def guardar_censo(self, datos):
        try:
            with open(CONFIG['archivo_datos'], 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
            return False

    def abrir_navegador(self, archivo_html):
        """Abre el archivo HTML en el navegador por defecto del sistema"""
        ruta_absoluta = os.path.abspath(archivo_html)
        webbrowser.open(f"file://{ruta_absoluta}")

    def crear_boton_moderno(self, parent, text, bg_color, hover_color, text_color, icon="", command=None, width=30):
        btn_frame = tk.Frame(parent, bg=bg_color, cursor="hand2")
        lbl = tk.Label(btn_frame, text=f"{icon}  {text}" if icon else text, 
                       bg=bg_color, fg=text_color, font=("Segoe UI", 11, "bold"))
        lbl.pack(pady=12, padx=20)
        
        def on_enter(e):
            btn_frame['bg'] = hover_color
            lbl['bg'] = hover_color
        def on_leave(e):
            btn_frame['bg'] = bg_color
            lbl['bg'] = bg_color
            
        btn_frame.bind("<Enter>", on_enter)
        btn_frame.bind("<Leave>", on_leave)
        lbl.bind("<Enter>", on_enter)
        lbl.bind("<Leave>", on_leave)
        
        if command:
            btn_frame.bind("<Button-1>", lambda e: command())
            lbl.bind("<Button-1>", lambda e: command())
            
        return btn_frame

    # --- NAVEGACIÓN Y ANIMACIÓN ---
    def crear_menu_lateral(self):
        lbl_titulo = tk.Label(self.frame_menu, text="GESTOR\nCOSTALEROS", bg=C_MORADO, fg=C_ORO, font=("Cinzel", 20, "bold"), pady=30)
        lbl_titulo.pack(fill=tk.X)
        
        opciones = [
            ("Inicio", "🏠"), 
            ("Miércoles Santo", "🕯️"), 
            ("Viernes Santo", "✝️"), 
            ("Ensayos", "📋"), 
            ("Censo (Costaleros)", "👥"), 
            ("Exportar PDF", "📄")
        ]
        
        for op, icon in opciones:
            btn = self.crear_boton_moderno(self.frame_menu, op, C_MORADO, C_MORADO_HOVER, C_BLANCO, icon=icon, command=lambda nombre=op: self.mostrar_pantalla(nombre))
            btn.pack(fill=tk.X, pady=2, padx=10)
            
        btn_salir = self.crear_boton_moderno(self.frame_menu, "SALIR DEL SISTEMA", "#ff4757", "#ff6b81", C_BLANCO, icon="❌", command=self.root.quit)
        btn_salir.pack(side=tk.BOTTOM, fill=tk.X, pady=20, padx=10)

    def mostrar_pantalla(self, nombre):
        frame_in = self.frames[nombre]
        if self.current_frame == frame_in: return
        if self.current_frame: self.current_frame.place_forget()
        self.current_frame = frame_in
        
        if nombre == "Censo (Costaleros)":
            self.actualizar_tabla_censo()

        def slide(step):
            if step > 0:
                relx = step * 0.01
                frame_in.place(relx=relx, rely=0, relwidth=1, relheight=1)
                self.root.after(10, slide, step - 1)
            else:
                frame_in.place(relx=0.0, rely=0, relwidth=1, relheight=1)
                
        slide(10)

    def crear_pantallas(self):
        self.frames["Inicio"] = self.crear_pantalla_inicio()
        self.frames["Miércoles Santo"] = self.crear_pantalla_procesion("Miércoles Santo", "visualizador_miercoles.html", generar_cuadrillas_miercoles, generar_html_miercoles, True)
        self.frames["Viernes Santo"] = self.crear_pantalla_procesion("Viernes Santo", "visualizador_viernes.html", generar_cuadrillas_viernes, generar_html_viernes, True)
        self.frames["Ensayos"] = self.crear_pantalla_ensayos()
        self.frames["Censo (Costaleros)"] = self.crear_pantalla_censo()
        self.frames["Exportar PDF"] = self.crear_pantalla_pdf()

    # --- PANTALLAS ---
    def crear_pantalla_inicio(self):
        f = tk.Frame(self.frame_main, bg=C_GRIS_FONDO)
        card = tk.Frame(f, bg=C_BLANCO, padx=50, pady=50, highlightbackground="#e0e0e0", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(card, text="Sistema de Gestión Turnos Cristo de la Agonía", font=("Segoe UI", 26, "bold"), bg=C_BLANCO, fg=C_MORADO).pack(pady=(0, 10))
        tk.Label(card, text="OFS Muy Ilustre Mayordomía de Ntro. Padre Jesús Nazareno", font=("Segoe UI", 14), bg=C_BLANCO, fg="#666").pack(pady=5)
        tk.Frame(card, height=2, bg=C_ORO, width=100).pack(pady=20)
        tk.Label(card, text="Selecciona un módulo en el menú lateral izquierdo para empezar a trabajar.", font=("Segoe UI", 12), bg=C_BLANCO, fg="#888").pack(pady=10)
        return f

    def crear_pantalla_procesion(self, titulo, html_file, func_generar, func_html, necesita_es_par):
        f = tk.Frame(self.frame_main, bg=C_GRIS_FONDO)
        card = tk.Frame(f, bg=C_BLANCO, padx=40, pady=40, highlightbackground="#e0e0e0", highlightthickness=1)
        card.place(relx=0.5, rely=0.45, anchor="center", width=650)
        
        tk.Label(card, text=f"Procesión: {titulo}", font=("Segoe UI", 22, "bold"), bg=C_BLANCO, fg=C_MORADO).pack(anchor="w", pady=(0, 20))
        
        fila_anio = tk.Frame(card, bg=C_BLANCO)
        fila_anio.pack(fill=tk.X, pady=(0, 30))
        tk.Label(fila_anio, text="Año de la procesión:", bg=C_BLANCO, font=("Segoe UI", 12)).pack(side=tk.LEFT)
        entry_anio = tk.Entry(fila_anio, font=("Segoe UI", 14), width=10, bg="#f9f9f9", relief="solid", bd=1)
        entry_anio.insert(0, str(datetime.datetime.now().year))
        entry_anio.pack(side=tk.LEFT, padx=15)

        def generar_nuevo():
            anio = int(entry_anio.get()) if entry_anio.get().isdigit() else datetime.datetime.now().year
            es_par = (anio % 2 == 0)
            master_list = cargar_datos(CONFIG['archivo_datos'])
            
            if "Miércoles" in titulo: master_list = [p for p in master_list if p.get('miercoles_santo', False)]
            else: master_list = [p for p in master_list if p.get('viernes_santo', False)]
                
            if not master_list:
                messagebox.showwarning("Aviso", f"No hay costaleros asignados para el {titulo}.")
                return
            
            if necesita_es_par: datos = func_generar(master_list, es_par)
            else: datos = func_generar(master_list)
                
            func_html(datos, master_list, anio, es_par, CONFIG['peso_trono_kg'], CONFIG['peso_cruz_kg'], CONFIG['limite_peso_persona'])
            self.abrir_navegador(html_file)

        def abrir_anterior():
            if os.path.exists(html_file): self.abrir_navegador(html_file)
            else:
                resp = messagebox.askyesno("No encontrado", f"No existe ningún entorno web previo guardado.\n\n¿Quieres generar una plantilla base nueva ahora?")
                if resp: generar_nuevo()

        btn_frame = tk.Frame(card, bg=C_BLANCO)
        btn_frame.pack(fill=tk.X, pady=10)
        
        btn_nuevo = self.crear_boton_moderno(btn_frame, "✨ GENERAR NUEVO CUADRANTE", C_ORO, C_ORO_HOVER, C_TEXTO, command=generar_nuevo)
        btn_nuevo.pack(side=tk.LEFT, padx=(0, 10))
        btn_abrir = self.crear_boton_moderno(btn_frame, "🌐 ABRIR CUADRANTE ANTERIOR", "#17517e", "#1f6b9c", C_BLANCO, command=abrir_anterior)
        btn_abrir.pack(side=tk.LEFT)
        tk.Label(card, text="* Generar un nuevo cuadrante sobreescribirá la ultima modificación sin guardar.", font=("Segoe UI", 10, "italic"), bg=C_BLANCO, fg="#888").pack(anchor="w", pady=(30, 0))
        return f

    def crear_pantalla_ensayos(self):
        f = tk.Frame(self.frame_main, bg=C_GRIS_FONDO)
        card = tk.Frame(f, bg=C_BLANCO, padx=40, pady=40, highlightbackground="#e0e0e0", highlightthickness=1)
        card.place(relx=0.5, rely=0.45, anchor="center", width=650)
        
        tk.Label(card, text="Organizador de Ensayos", font=("Segoe UI", 22, "bold"), bg=C_BLANCO, fg=C_MORADO).pack(anchor="w", pady=(0, 20))
        
        fila_turnos = tk.Frame(card, bg=C_BLANCO)
        fila_turnos.pack(fill=tk.X, pady=(0, 30))
        tk.Label(fila_turnos, text="Número de Turnos (Ej: 2 para 72 costaleros):", bg=C_BLANCO, font=("Segoe UI", 12)).pack(side=tk.LEFT)
        entry_turnos = tk.Entry(fila_turnos, font=("Segoe UI", 14), width=8, bg="#f9f9f9", relief="solid", bd=1)
        entry_turnos.insert(0, "2")
        entry_turnos.pack(side=tk.LEFT, padx=15)
        
        def generar_nuevo():
            turnos = int(entry_turnos.get()) if entry_turnos.get().isdigit() else 2
            master_list = cargar_datos(CONFIG['archivo_datos'])
            generar_html_ensayo(turnos, master_list, CONFIG['peso_trono_kg'], CONFIG['limite_peso_persona'])
            self.abrir_navegador("visualizador_ensayos.html")
            
        def abrir_anterior():
            if os.path.exists("visualizador_ensayos.html"): self.abrir_navegador("visualizador_ensayos.html")
            else:
                resp = messagebox.askyesno("No encontrado", "No existe ningún entorno de ensayo.\n\n¿Quieres crear el entorno ahora?")
                if resp: generar_nuevo()

        btn_frame = tk.Frame(card, bg=C_BLANCO)
        btn_frame.pack(fill=tk.X, pady=10)
        btn_nuevo = self.crear_boton_moderno(btn_frame, "✨ NUEVO ENTORNO", C_ORO, C_ORO_HOVER, C_TEXTO, command=generar_nuevo)
        btn_nuevo.pack(side=tk.LEFT, padx=(0, 10))
        btn_abrir = self.crear_boton_moderno(btn_frame, "🌐 ABRIR ANTERIOR", "#17517e", "#1f6b9c", C_BLANCO, command=abrir_anterior)
        btn_abrir.pack(side=tk.LEFT)
        return f

    def crear_pantalla_pdf(self):
        f = tk.Frame(self.frame_main, bg=C_GRIS_FONDO)
        card = tk.Frame(f, bg=C_BLANCO, padx=40, pady=40, highlightbackground="#e0e0e0", highlightthickness=1)
        card.place(relx=0.5, rely=0.45, anchor="center", width=650)
        
        tk.Label(card, text="Generador de PDF Oficial", font=("Segoe UI", 22, "bold"), bg=C_BLANCO, fg=C_MORADO).pack(anchor="w", pady=(0, 10))
        tk.Label(card, text="Selecciona para qué procesión vas a generar el informe oficial.", font=("Segoe UI", 12), bg=C_BLANCO, fg="#666").pack(anchor="w", pady=(0, 20))
        
        # NUEVO: Cajón para introducir el Año
        fila_anio = tk.Frame(card, bg=C_BLANCO)
        fila_anio.pack(fill=tk.X, pady=(0, 20))
        tk.Label(fila_anio, text="Año del cuadrante a exportar:", bg=C_BLANCO, font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        entry_anio = tk.Entry(fila_anio, font=("Segoe UI", 14), width=10, bg="#f9f9f9", relief="solid", bd=1)
        entry_anio.insert(0, str(datetime.datetime.now().year))
        entry_anio.pack(side=tk.LEFT, padx=15)

        var_tipo = tk.StringVar(value="Viernes Santo")
        style = ttk.Style()
        style.configure("TRadiobutton", background=C_BLANCO, font=("Segoe UI", 12))
        
        ttk.Radiobutton(card, text="Miércoles Santo", variable=var_tipo, value="Miércoles Santo").pack(anchor="w", pady=5)
        ttk.Radiobutton(card, text="Viernes Santo", variable=var_tipo, value="Viernes Santo").pack(anchor="w", pady=5)
        ttk.Radiobutton(card, text="Procesión Extraordinaria", variable=var_tipo, value="Procesión Extraordinaria").pack(anchor="w", pady=(5,30))

        def generar():
            archivo = filedialog.askopenfilename(title="Selecciona el archivo JSON descargado de la web", filetypes=[("Archivos JSON", "*.json")])
            if archivo:
                # Capturamos el año y se lo enviamos a la lógica
                anio = int(entry_anio.get()) if entry_anio.get().isdigit() else datetime.datetime.now().year
                exito, msg = crear_html_informe(var_tipo.get(), archivo, anio)
                if exito: self.abrir_navegador(msg)
                else: messagebox.showerror("Error", f"Error al generar: {msg}")

        btn_generar = self.crear_boton_moderno(card, "📂 SELECCIONAR JSON Y GENERAR PDF", C_MORADO, C_MORADO_HOVER, C_BLANCO, command=generar)
        btn_generar.pack(anchor="w")
        return f

    # --- PANTALLA CENSO (CRUD INTERACTIVO) ---
    def crear_pantalla_censo(self):
        f = tk.Frame(self.frame_main, bg=C_GRIS_FONDO, padx=30, pady=30)
        tk.Label(f, text="Gestión del Censo General", font=("Segoe UI", 22, "bold"), bg=C_GRIS_FONDO, fg=C_MORADO).pack(anchor="w")
        
        toolbar = tk.Frame(f, bg=C_GRIS_FONDO)
        toolbar.pack(fill=tk.X, pady=15)
        
        btn_nuevo = self.crear_boton_moderno(toolbar, "➕ Nuevo", "#27ae60", "#2ecc71", C_BLANCO, command=lambda: self.abrir_formulario_costalero())
        btn_nuevo.pack(side=tk.LEFT, padx=(0, 10))
        btn_editar = self.crear_boton_moderno(toolbar, "✏️ Editar", C_ORO, C_ORO_HOVER, C_TEXTO, command=lambda: self.abrir_formulario_costalero(editar=True))
        btn_editar.pack(side=tk.LEFT, padx=10)
        btn_borrar = self.crear_boton_moderno(toolbar, "❌ Borrar", "#ff4757", "#ff6b81", C_BLANCO, command=self.borrar_costalero)
        btn_borrar.pack(side=tk.LEFT, padx=10)
        
        search_frame = tk.Frame(toolbar, bg=C_GRIS_FONDO)
        search_frame.pack(side=tk.RIGHT)
        tk.Label(search_frame, text="🔍 Buscar:", bg=C_GRIS_FONDO, font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0,5))
        self.entry_busqueda = tk.Entry(search_frame, font=("Segoe UI", 11), width=25, relief="solid", bd=1)
        self.entry_busqueda.pack(side=tk.LEFT)
        self.entry_busqueda.bind("<KeyRelease>", self.actualizar_tabla_censo)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=('Segoe UI', 11, 'bold'), background=C_ORO, foreground=C_TEXTO, relief="flat")
        style.configure("Treeview", font=('Segoe UI', 11), rowheight=30, background=C_BLANCO, fieldbackground=C_BLANCO, borderwidth=0)
        style.map('Treeview', background=[('selected', C_MORADO)], foreground=[('selected', C_BLANCO)])

        frame_tabla = tk.Frame(f, bg=C_BLANCO, highlightbackground="#e0e0e0", highlightthickness=1)
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        columnas = ("ID", "Nombre", "Altura", "Hombro", "Miércoles", "Viernes")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre del Costalero")
        self.tree.heading("Altura", text="Altura (cm)")
        self.tree.heading("Hombro", text="Preferencia")
        self.tree.heading("Miércoles", text="M. Santo")
        self.tree.heading("Viernes", text="V. Santo")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Nombre", width=250)
        self.tree.column("Altura", width=100, anchor="center")
        self.tree.column("Hombro", width=120, anchor="center")
        self.tree.column("Miércoles", width=100, anchor="center")
        self.tree.column("Viernes", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        return f

    def actualizar_tabla_censo(self, event=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        datos = cargar_datos(CONFIG['archivo_datos'])
        filtro = self.entry_busqueda.get().lower() if hasattr(self, 'entry_busqueda') else ""
        datos.sort(key=lambda x: x.get('nombre', ''))
        
        for p in datos:
            if filtro in p.get('nombre', '').lower() or str(p.get('id', '')) == filtro:
                mi = "✅" if p.get("miercoles_santo") else "❌"
                vi = "✅" if p.get("viernes_santo") else "❌"
                hombro = p.get("pref_hombro", "")
                if not hombro: hombro = "Indiferente"
                self.tree.insert("", tk.END, values=(p['id'], p['nombre'], p['altura'], hombro.capitalize(), mi, vi))

    # ==========================================
    # NUEVO FORMULARIO POP-UP UNIFICADO (NUEVO/EDITAR)
    # ==========================================
    def abrir_formulario_costalero(self, editar=False):
        datos = cargar_datos(CONFIG['archivo_datos'])
        costalero = None
        
        if editar:
            seleccion = self.tree.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Selecciona un costalero de la lista para editar.")
                return
            pid = self.tree.item(seleccion[0])['values'][0]
            costalero = next((x for x in datos if x['id'] == pid), None)
            if not costalero: return

        # Crear ventana Modal (Pop-up)
        top = tk.Toplevel(self.root)
        top.title("Editar Costalero" if editar else "Nuevo Costalero")
        top.geometry("400x480")
        top.configure(bg=C_BLANCO)
        top.resizable(False, False)
        top.transient(self.root) 
        top.grab_set() # Bloquea la ventana principal hasta que se cierre esta

        # Centrar ventana
        top.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (480 // 2)
        top.geometry(f"+{x}+{y}")

        # Título interno
        tk.Label(top, text="📋 Ficha del Costalero", font=("Segoe UI", 16, "bold"), bg=C_BLANCO, fg=C_MORADO).pack(pady=(20, 20))

        # Contenedor del formulario
        form_frame = tk.Frame(top, bg=C_BLANCO)
        form_frame.pack(padx=40, fill=tk.X)

        # Campos
        tk.Label(form_frame, text="Nombre Completo:", bg=C_BLANCO, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        var_nombre = tk.StringVar(value=costalero['nombre'] if costalero else "")
        tk.Entry(form_frame, textvariable=var_nombre, font=("Segoe UI", 12), relief="solid", bd=1).pack(fill=tk.X, pady=(2, 15))

        tk.Label(form_frame, text="Altura (en cm):", bg=C_BLANCO, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        var_altura = tk.StringVar(value=str(costalero['altura']) if costalero else "")
        tk.Entry(form_frame, textvariable=var_altura, font=("Segoe UI", 12), relief="solid", bd=1).pack(fill=tk.X, pady=(2, 15))

        tk.Label(form_frame, text="Preferencia de Hombro:", bg=C_BLANCO, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        var_hombro = tk.StringVar(value=costalero.get('pref_hombro', 'Indiferente') if costalero and costalero.get('pref_hombro') else "Indiferente")
        combo_hombro = ttk.Combobox(form_frame, textvariable=var_hombro, values=["Derecho", "Izquierdo", "Ambos", "Indiferente"], state="readonly", font=("Segoe UI", 11))
        combo_hombro.pack(fill=tk.X, pady=(2, 20))

        # Checkboxes Procesiones
        tk.Label(form_frame, text="Disponibilidad para procesionar:", bg=C_BLANCO, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        var_miercoles = tk.BooleanVar(value=costalero.get('miercoles_santo', True) if costalero else True)
        var_viernes = tk.BooleanVar(value=costalero.get('viernes_santo', True) if costalero else True)
        
        chk_style = ttk.Style()
        chk_style.configure("TCheckbutton", background=C_BLANCO, font=("Segoe UI", 11))
        
        ttk.Checkbutton(form_frame, text="Sale el Miércoles Santo", variable=var_miercoles).pack(anchor="w", pady=2)
        ttk.Checkbutton(form_frame, text="Sale el Viernes Santo", variable=var_viernes).pack(anchor="w", pady=2)

        def guardar():
            if not var_nombre.get().strip() or not var_altura.get().isdigit():
                messagebox.showwarning("Error", "Revisa los campos. El nombre no puede estar vacío y la altura debe ser un número.")
                return
            
            hombro_val = var_hombro.get()
            if hombro_val == "Indiferente": hombro_val = ""

            if editar:
                # Modificamos el existente
                costalero['nombre'] = var_nombre.get().strip()
                costalero['altura'] = int(var_altura.get())
                costalero['pref_hombro'] = hombro_val
                costalero['miercoles_santo'] = var_miercoles.get()
                costalero['viernes_santo'] = var_viernes.get()
            else:
                # Creamos uno nuevo
                nuevo_id = max([p.get('id', 0) for p in datos], default=0) + 1
                datos.append({
                    "id": nuevo_id,
                    "nombre": var_nombre.get().strip(),
                    "altura": int(var_altura.get()),
                    "pref_hombro": hombro_val,
                    "puede_repetir": True,
                    "miercoles_santo": var_miercoles.get(),
                    "viernes_santo": var_viernes.get()
                })

            if self.guardar_censo(datos):
                self.actualizar_tabla_censo()
                top.destroy()

        btn_guardar = tk.Button(top, text="💾 GUARDAR CAMBIOS", bg=C_MORADO, fg=C_BLANCO, font=("Segoe UI", 12, "bold"), bd=0, cursor="hand2", command=guardar)
        btn_guardar.pack(fill=tk.X, padx=40, pady=(25, 0), ipady=8)

    def borrar_costalero(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un costalero de la lista haciendo clic sobre él.")
            return
            
        item = self.tree.item(seleccion[0])
        pid = item['values'][0]
        nombre = item['values'][1]
        
        if messagebox.askyesno("⚠️ Confirmar Borrado", f"¿Estás completamente seguro de querer dar de baja a {nombre}?\n\nEsta acción no se puede deshacer."):
            datos = cargar_datos(CONFIG['archivo_datos'])
            datos = [x for x in datos if x.get('id') != pid]
            self.guardar_censo(datos)
            self.actualizar_tabla_censo()

# ==========================================
# INICIO DE LA APLICACIÓN
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    
    try: root.iconbitmap('favicon.ico')
    except: pass

    app = GestorCofradeAPP(root)
    
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    root.mainloop()