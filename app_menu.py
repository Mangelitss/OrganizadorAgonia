import sys
import os
import json
import datetime
import webbrowser
import shutil  
import requests # AÑADIDO PARA LA CONEXIÓN A FIREBASE
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry

# Importamos las lógicas independientes
from logica_trono import cargar_datos, generar_turnos_base, generar_html_interactivo
from logica_miercoles import generar_cuadrillas_miercoles, generar_html_miercoles
from logica_viernes import generar_cuadrillas_viernes, generar_html_viernes
from logica_ensayos import generar_html_ensayo
from logica_informes import crear_html_informe
from logica_licencia import comprobar_licencia
from logica_calendario import cargar_eventos, guardar_eventos, generar_html_calendario

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
C_ROJO = "#360928"

# ==========================================
# CLASE PRINCIPAL DE LA INTERFAZ
# ==========================================
class GestorCofradeAPP:
    def __init__(self, root):
        self.root = root        

        # 1. OCULTAMOS LA VENTANA PRINCIPAL AL ARRANCAR
        self.root.withdraw()
        
        try:
            self.root.iconbitmap("icono.ico")
        except:
            pass

        self.root.title("Gestor de Turnos Cristo de la Agonía V1.0 - Ntro. Padre Jesús Nazareno")
        self.root.geometry("1280x720")
        self.root.configure(bg=C_GRIS_FONDO)
        # HACEMOS LA VENTANA PRINCIPAL REESCALABLE
        self.root.resizable(True, True)

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

        # 2. VERIFICAMOS LA SESIÓN:
        self.verificar_sesion()

    def verificar_sesion(self):
        import os, json
        archivo_sesion = "licencia_local.json"
        
        if os.path.exists(archivo_sesion):
            try:
                with open(archivo_sesion, "r") as f:
                    datos = json.load(f)
                    user = datos.get("usuario")
                    pwd = datos.get("password")
                
                valido, mensaje = comprobar_licencia(user, pwd)
                
                if valido:
                    self.root.deiconify()
                    return
            except Exception:
                pass 
                
        self.pedir_login()

    def pedir_login(self):
        self.ventana_login = tk.Toplevel(self.root)
        self.ventana_login.title("Activación de Licencia - Gestor Cofrade")
        self.ventana_login.geometry("450x600") 
        self.ventana_login.configure(bg="#23061b") 
        self.ventana_login.resizable(True, True)
        self.ventana_login.protocol("WM_DELETE_WINDOW", self.root.destroy)
        
        try:
            from PIL import Image, ImageTk
            pil_img = Image.open("bandera_tercio_npj.png")
            
            porcentaje = 30  
            
            ancho_orig, alto_orig = pil_img.size
            nuevo_ancho = int(ancho_orig * (porcentaje / 100))
            nuevo_alto = int(alto_orig * (porcentaje / 100))
            
            pil_img_rescalada = pil_img.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(pil_img_rescalada)
            
            self.ventana_login.iconphoto(False, logo_img)
            self.root.iconphoto(False, logo_img)
            
            lbl_logo = tk.Label(self.ventana_login, image=logo_img, bg="#23061b")
            lbl_logo.image = logo_img  
            lbl_logo.pack(pady=(25, 10))
        except Exception as e:
            pass

        tk.Label(self.ventana_login, text="CONTROL DE ACCESO", font=("Georgia", 18, "bold"), bg="#23061b", fg="#d4af37").pack(pady=(0, 25))
        
        tk.Label(self.ventana_login, text="Usuario (Hermandad):", font=("Georgia", 11, "bold"), bg="#23061b", fg="#e8d08c").pack(anchor="w", padx=50, pady=(0, 5))
        self.entry_user = tk.Entry(self.ventana_login, font=("Helvetica", 14), bg="#0c0209", fg="#d4af37", insertbackground="#d4af37", relief="solid", bd=1, justify="center")
        self.entry_user.pack(fill=tk.X, padx=50, ipady=6, pady=(0, 20))
        
        tk.Label(self.ventana_login, text="Contraseña de Licencia:", font=("Georgia", 11, "bold"), bg="#23061b", fg="#e8d08c").pack(anchor="w", padx=50, pady=(0, 5))
        self.entry_pass = tk.Entry(self.ventana_login, font=("Helvetica", 14), bg="#0c0209", fg="#d4af37", insertbackground="#d4af37", show="*", relief="solid", bd=1, justify="center")
        self.entry_pass.pack(fill=tk.X, padx=50, ipady=6, pady=(0, 35))
        
        btn_login = tk.Button(self.ventana_login, text="INICIAR SESIÓN", font=("Georgia", 13, "bold"), bg="#d4af37", fg="#0c0209", activebackground="#b5952f", activeforeground="#000", cursor="hand2", relief="flat", command=self.validar_acceso)
        btn_login.pack(fill=tk.X, padx=50, ipady=8, pady=(0, 20))

    def validar_acceso(self):
        usuario = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        
        if not usuario or not password:
            messagebox.showwarning("Atención", "Por favor, rellena ambos campos para verificar tu licencia.")
            return
            
        valido, mensaje = comprobar_licencia(usuario, password)
        
        if valido:
            import json
            with open("licencia_local.json", "w") as f:
                json.dump({"usuario": usuario, "password": password}, f)
                
            self.ventana_login.destroy()
            self.root.deiconify() 
            messagebox.showinfo("Éxito", "Licencia validada correctamente.\n¡Bienvenido al Gestor Cofrade!")
        else:
            messagebox.showerror("Acceso Denegado", mensaje)

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
        lbl_titulo = tk.Label(self.frame_menu, text="GESTOR\nCOSTALEROS", bg=C_MORADO, fg=C_ORO, font=("Georgia", 20, "bold"), pady=30)
        lbl_titulo.pack(fill=tk.X)
        
        opciones = [
            ("Inicio", "🏠"), 
            ("Miércoles Santo", "🕯️"), 
            ("Viernes Santo", "✝️"), 
            ("Ensayos", "📋"), 
            ("Calendario", "📅"), 
            ("Censo (Costaleros)", "👥"), 
            ("Publicar / PDF", "📤") # Cambiado el nombre de la pestaña
        ]
        
        for op, icon in opciones:
            btn = self.crear_boton_moderno(self.frame_menu, op, C_MORADO, C_MORADO_HOVER, C_BLANCO, icon=icon, command=lambda nombre=op: self.mostrar_pantalla(nombre))
            btn.pack(fill=tk.X, pady=2, padx=10)
            
        btn_salir = self.crear_boton_moderno(self.frame_menu, "SALIR DEL SISTEMA", "#ff4757", "#ff6b81", C_BLANCO, icon="❌", command=self.root.quit)
        btn_salir.pack(side=tk.BOTTOM, fill=tk.X, pady=20, padx=10)

    def mostrar_pantalla(self, nombre):
        frame_in = self.frames.get(nombre)
        if not frame_in: return
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
        self.frames["Calendario"] = self.crear_pantalla_calendario()
        self.frames["Censo (Costaleros)"] = self.crear_pantalla_censo()
        self.frames["Publicar / PDF"] = self.crear_pantalla_pdf()

    # --- PANTALLAS ---
    def crear_pantalla_inicio(self):
        f = tk.Frame(self.frame_main, bg=C_GRIS_FONDO)
        
        # --- 1. CANVAS PARA EL FONDO DINÁMICO ---
        canvas_fondo = tk.Canvas(f, bg=C_GRIS_FONDO, highlightthickness=0)
        canvas_fondo.place(relwidth=1, relheight=1)

        try:
            # Importamos ImageDraw para dibujar el "efecto cristal"
            from PIL import Image, ImageTk, ImageEnhance, ImageDraw
            import os
            
            ruta_imagen = "cristo_agonia.jpg" 
            
            if os.path.exists(ruta_imagen):
                # Convertimos a RGBA para soportar transparencias
                img_original = Image.open(ruta_imagen).convert("RGBA")
                
                def redimensionar_fondo(event):
                    if event.width < 100 or event.height < 100: return
                    
                    # 1. Ajustar el tamaño del Cristo a la ventana
                    ratio_img = img_original.width / img_original.height
                    ratio_ventana = event.width / event.height
                    
                    if ratio_ventana > ratio_img:
                        nuevo_ancho = event.width
                        nuevo_alto = int(nuevo_ancho / ratio_img)
                    else:
                        nuevo_alto = event.height
                        nuevo_ancho = int(nuevo_alto * ratio_img)
                        
                    img_redim = img_original.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
                    
                    # 2. Oscurecer el fondo un poco (50%)
                    enhancer = ImageEnhance.Brightness(img_redim)
                    img_redim = enhancer.enhance(0.5) 
                    
                    # --- 3. EL TRUCO DE LA TRANSPARENCIA ---
                    # Creamos una capa invisible del tamaño de la foto
                    capa_transparente = Image.new('RGBA', img_redim.size, (0,0,0,0))
                    draw = ImageDraw.Draw(capa_transparente)
                    
                    # Medidas de la tarjeta efecto cristal
                    card_w, card_h = 800, 250
                    img_cx, img_cy = nuevo_ancho // 2, nuevo_alto // 2
                    
                    x1 = img_cx - card_w // 2
                    y1 = img_cy - card_h // 2
                    x2 = img_cx + card_w // 2
                    y2 = img_cy + card_h // 2
                    
                    # Dibujamos un rectángulo blanco con 82% de opacidad (210) y borde dorado
                    draw.rectangle([x1, y1, x2, y2], fill=(255, 255, 255, 180), outline=(212, 175, 55, 255), width=4)
                    
                    # Fusionamos la capa semitransparente con la foto del Cristo
                    img_final = Image.alpha_composite(img_redim, capa_transparente)
                    
                    # 4. Guardar y mostrar en pantalla
                    f.img_tk = ImageTk.PhotoImage(img_final)
                    canvas_fondo.delete("all")
                    canvas_fondo.create_image(event.width/2, event.height/2, image=f.img_tk, anchor="center")
                    
                    # --- 5. DIBUJAR LOS TEXTOS FLOTANTES ---
                    cx, cy = event.width // 2, event.height // 2
                    
                    canvas_fondo.create_text(cx, cy - 60, text="Sistema de Gestión Turnos y Procesiones", font=("Cinzel", 24, "bold"), fill=C_MORADO)
                    canvas_fondo.create_text(cx, cy - 20, text="OFS Muy Ilustre Mayordomía de Ntro. Padre Jesús Nazareno", font=("Cinzel", 15), fill="#333333")
                    canvas_fondo.create_text(cx, cy + 10, text="Tercio del Cristo de la Agonía y María Magdalena", font=("Cinzel", 13), fill="#333333")
                    
                    # La línea dorada separadora
                    canvas_fondo.create_line(cx - 100, cy + 40, cx + 100, cy + 40, fill=C_ORO, width=2)
                    
                    canvas_fondo.create_text(cx, cy + 70, text="Selecciona un módulo en el menú lateral izquierdo para empezar a trabajar.", font=("Segoe UI", 12), fill="#555555")

                f.bind("<Configure>", redimensionar_fondo)
            else:
                # Sistema de seguridad por si alguna vez borras la foto sin querer
                card = tk.Frame(f, bg=C_BLANCO, padx=50, pady=50, highlightbackground=C_ORO, highlightthickness=2)
                card.place(relx=0.5, rely=0.5, anchor="center")
                tk.Label(card, text="Sistema de Gestión Turnos y Procesiones", font=("Georgia", 24, "bold"), bg=C_BLANCO, fg=C_MORADO).pack(pady=(0, 10))
                tk.Label(card, text="OFS Muy Ilustre Mayordomía de Ntro. Padre Jesús Nazareno", font=("Georgia", 15), bg=C_BLANCO, fg="#666").pack(pady=5)
                tk.Label(card, text="Tercio del Cristo de la Agonía y María Magdalena", font=("Georgia", 13), bg=C_BLANCO, fg="#666").pack(pady=5)
                tk.Frame(card, height=2, bg=C_ORO, width=200).pack(pady=20)
                tk.Label(card, text="Selecciona un módulo en el menú lateral izquierdo para empezar a trabajar.", font=("Segoe UI", 12), bg=C_BLANCO, fg="#888").pack(pady=10)

        except Exception as e:
            print("Error cargando imagen de fondo:", e)

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
        
        btn_nuevo = self.crear_boton_moderno(btn_frame, "GENERAR NUEVO CUADRANTE", C_ORO, C_ORO_HOVER, C_TEXTO, command=generar_nuevo)
        btn_nuevo.pack(side=tk.LEFT, padx=(0, 10))
        btn_abrir = self.crear_boton_moderno(btn_frame, "ABRIR CUADRANTE ANTERIOR", "#17517e", "#1f6b9c", C_BLANCO, command=abrir_anterior)
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
        btn_nuevo = self.crear_boton_moderno(btn_frame, "NUEVO ENTORNO", C_ORO, C_ORO_HOVER, C_TEXTO, command=generar_nuevo)
        btn_nuevo.pack(side=tk.LEFT, padx=(0, 10))
        btn_abrir = self.crear_boton_moderno(btn_frame, "ABRIR ANTERIOR", "#17517e", "#1f6b9c", C_BLANCO, command=abrir_anterior)
        btn_abrir.pack(side=tk.LEFT)
        return f

    def crear_pantalla_calendario(self):
        f = tk.Frame(self.frame_main, bg="#f4f6f8", padx=30, pady=30)
        
        tk.Label(f, text="📅 Calendario de Ensayos y Citas", font=("Segoe UI", 22, "bold"), bg="#f4f6f8", fg=C_MORADO).pack(anchor="w")
        
        toolbar = tk.Frame(f, bg="#f4f6f8")
        toolbar.pack(fill=tk.X, pady=15)
        
        btn_nuevo = self.crear_boton_moderno(toolbar, "➕ Añadir Cita", C_ORO, C_ORO_HOVER, C_TEXTO, command=lambda: self.abrir_formulario_evento())
        btn_nuevo.pack(side=tk.LEFT, padx=(0, 10))
        btn_editar = self.crear_boton_moderno(toolbar, "✏️ Editar", "#17517e", "#1f6b9c", C_BLANCO, command=lambda: self.abrir_formulario_evento(editar=True))
        btn_editar.pack(side=tk.LEFT, padx=10)
        btn_borrar = self.crear_boton_moderno(toolbar, "❌ Borrar", "#ff4757", "#ff6b81", C_BLANCO, command=self.borrar_evento)
        btn_borrar.pack(side=tk.LEFT, padx=10)
        
        def exportar_html():
            exito, archivo = generar_html_calendario(self.lista_eventos)
            if exito: self.abrir_navegador(archivo)
                
        btn_pdf = self.crear_boton_moderno(toolbar, "📤 Exportar PDF", C_MORADO, C_MORADO_HOVER, C_BLANCO, command=exportar_html)
        btn_pdf.pack(side=tk.RIGHT)

        frame_tabla = tk.Frame(f, bg=C_BLANCO, highlightbackground="#ccc", highlightthickness=1)
        frame_tabla.pack(fill=tk.BOTH, expand=True)
        
        columnas = ("id", "fecha", "hora", "motivo", "lugar", "indicaciones")
        self.tabla_calendario = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=15)
        
        self.tabla_calendario.heading("id", text="ID") 
        self.tabla_calendario.heading("fecha", text="Día")
        self.tabla_calendario.heading("hora", text="Hora")
        self.tabla_calendario.heading("motivo", text="Motivo / Cita")
        self.tabla_calendario.heading("lugar", text="Lugar")
        self.tabla_calendario.heading("indicaciones", text="Indicaciones")
        
        self.tabla_calendario.column("id", width=0, stretch=tk.NO)
        self.tabla_calendario.column("fecha", width=120, anchor="center")
        self.tabla_calendario.column("hora", width=80, anchor="center")
        self.tabla_calendario.column("motivo", width=200)
        self.tabla_calendario.column("lugar", width=150)
        self.tabla_calendario.column("indicaciones", width=250)
        
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_calendario.yview)
        self.tabla_calendario.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla_calendario.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.refrescar_tabla_calendario()
        return f

    def refrescar_tabla_calendario(self):
        for row in self.tabla_calendario.get_children():
            self.tabla_calendario.delete(row)
        self.lista_eventos = cargar_eventos()
        for idx, ev in enumerate(self.lista_eventos):
            self.tabla_calendario.insert("", "end", values=(idx, ev.get("fecha",""), ev.get("hora",""), ev.get("motivo",""), ev.get("lugar",""), ev.get("indicaciones","")))

    def borrar_evento(self):
        seleccionado = self.tabla_calendario.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona una cita de la tabla para borrarla.")
            return
            
        motivo = self.tabla_calendario.item(seleccionado[0])['values'][3]
        
        if messagebox.askyesno("⚠️ Confirmar Borrado", f"¿Estás seguro de eliminar el evento:\n'{motivo}'?"):
            idx = int(self.tabla_calendario.item(seleccionado[0])['values'][0])
            del self.lista_eventos[idx]
            guardar_eventos(self.lista_eventos)
            self.refrescar_tabla_calendario()

    def abrir_formulario_evento(self, editar=False):
        evento = None
        idx_editar = -1
        
        if editar:
            seleccionado = self.tabla_calendario.selection()
            if not seleccionado:
                messagebox.showwarning("Atención", "Selecciona una cita de la tabla para editar.")
                return
            idx_editar = int(self.tabla_calendario.item(seleccionado[0])['values'][0])
            evento = self.lista_eventos[idx_editar]

        top = tk.Toplevel(self.root)
        top.title("Editar Evento" if editar else "Nueva Cita / Ensayo")
        top.geometry("450x620")
        top.configure(bg=C_BLANCO)
        
        top.resizable(True, True)
        top.transient(self.root) 
        top.grab_set()

        top.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (450 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (620 // 2)
        top.geometry(f"+{x}+{y}")

        tk.Label(top, text="📅 Detalles de la Convocatoria", font=("Segoe UI", 16, "bold"), bg=C_BLANCO, fg=C_MORADO).pack(pady=(20, 15))
        
        form = tk.Frame(top, bg=C_BLANCO)
        form.pack(padx=30, fill=tk.BOTH, expand=True)

        fila_fechahora = tk.Frame(form, bg=C_BLANCO)
        fila_fechahora.pack(fill=tk.X, pady=(0, 15))

        bloque_fecha = tk.Frame(fila_fechahora, bg=C_BLANCO)
        bloque_fecha.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(bloque_fecha, text="Día del Evento:", bg=C_BLANCO, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        cal_fecha = DateEntry(bloque_fecha, background=C_MORADO, foreground='white', borderwidth=2, font=("Segoe UI", 12), date_pattern='dd/MM/yyyy', cursor="hand2")
        cal_fecha.pack(fill=tk.X)
        
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        if evento and evento.get('fecha'):
            try:
                partes = evento['fecha'].split(' de ')
                dia = int(partes[0])
                mes = meses.index(partes[1]) + 1
                anio_actual = datetime.datetime.now().year
                fecha_obj = datetime.date(anio_actual, mes, dia)
                cal_fecha.set_date(fecha_obj)
            except: pass

        bloque_hora = tk.Frame(fila_fechahora, bg=C_BLANCO)
        bloque_hora.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(bloque_hora, text="Hora:", bg=C_BLANCO, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        caja_selectores = tk.Frame(bloque_hora, bg=C_BLANCO)
        caja_selectores.pack(fill=tk.X)
        
        horas = [str(i).zfill(2) for i in range(24)]
        minutos = ["00", "15", "30", "45"]
        var_hh = tk.StringVar(value="20")
        var_mm = tk.StringVar(value="00")
        
        if evento:
            h_parts = evento.get('hora','').replace('h','').split(':')
            if len(h_parts) == 2:
                var_hh.set(h_parts[0])
                var_mm.set(h_parts[1])

        ttk.Combobox(caja_selectores, textvariable=var_hh, values=horas, width=4, font=("Segoe UI", 12), state="normal").pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Label(caja_selectores, text=":", bg=C_BLANCO, font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=2)
        ttk.Combobox(caja_selectores, textvariable=var_mm, values=minutos, width=4, font=("Segoe UI", 12), state="normal").pack(side=tk.LEFT, expand=True, fill=tk.X)

        tk.Label(form, text="Motivo (Puedes elegir o escribir uno):", bg=C_BLANCO, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        var_motivo = tk.StringVar(value=evento.get('motivo', 'Ensayo') if evento else 'Ensayo')
        combo_motivo = ttk.Combobox(form, textvariable=var_motivo, values=["Ensayo", "Reunión de Costaleros", "Mudá del Trono", "Misa de Hermandad"], font=("Segoe UI", 12))
        combo_motivo.pack(fill=tk.X, pady=(0, 15))

        tk.Label(form, text="Lugar:", bg=C_BLANCO, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        var_lugar = tk.StringVar(value=evento.get('lugar', 'San Francisco') if evento else 'San Francisco')
        combo_lugar = ttk.Combobox(form, textvariable=var_lugar, values=["San Francisco", "Santuario de Monserrate", "Casa de Hermandad", "As de Oros"], font=("Segoe UI", 12))
        combo_lugar.pack(fill=tk.X, pady=(0, 15))

        tk.Label(form, text="Indicaciones (Opcional):", bg=C_BLANCO, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        text_ind = tk.Text(form, font=("Segoe UI", 11), height=4, relief="solid", bd=1, wrap=tk.WORD)
        text_ind.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        placeholder = "Ej: Venir con calzado oscuro, ropa cómoda..."
        
        if evento and evento.get('indicaciones'):
            text_ind.insert("1.0", evento.get('indicaciones'))
            text_ind.config(fg="black")
        else:
            text_ind.insert("1.0", placeholder)
            text_ind.config(fg="grey")

        def on_focus_in(e):
            contenido = text_ind.get("1.0", "end-1c")
            if contenido == placeholder:
                text_ind.delete("1.0", tk.END)
                text_ind.config(fg="black")
                
        def on_focus_out(e):
            contenido = text_ind.get("1.0", "end-1c").strip()
            if not contenido:
                text_ind.insert("1.0", placeholder)
                text_ind.config(fg="grey")

        text_ind.bind("<FocusIn>", on_focus_in)
        text_ind.bind("<FocusOut>", on_focus_out)

        def guardar():
            mtv = var_motivo.get().strip()
            if not mtv:
                messagebox.showwarning("Atención", "Debes especificar un motivo.")
                return
            
            ind_final = text_ind.get("1.0", "end-1c").strip()
            if ind_final == placeholder:
                ind_final = ""

            fecha_seleccionada = cal_fecha.get_date()
            dia_str = str(fecha_seleccionada.day).zfill(2)
            mes_str = meses[fecha_seleccionada.month - 1]
            fecha_formateada = f"{dia_str} de {mes_str}"

            datos_evento = {
                "fecha": fecha_formateada,
                "hora": f"{var_hh.get()}:{var_mm.get()}h",
                "motivo": mtv,
                "lugar": var_lugar.get().strip(),
                "indicaciones": ind_final
            }

            if editar:
                self.lista_eventos[idx_editar] = datos_evento
            else:
                self.lista_eventos.append(datos_evento)
                
            guardar_eventos(self.lista_eventos)
            self.refrescar_tabla_calendario()
            top.destroy()

        btn_guardar = tk.Button(top, text="💾 GUARDAR EVENTO", bg=C_MORADO, fg=C_BLANCO, font=("Segoe UI", 12, "bold"), bd=0, cursor="hand2", command=guardar)
        btn_guardar.pack(fill=tk.X, padx=30, pady=(0, 20), ipady=8)


    # ==========================================
    # NUEVA PANTALLA: CENTRO DE PUBLICACIÓN
    # ==========================================
    def crear_pantalla_pdf(self):
        f = tk.Frame(self.frame_main, bg=C_GRIS_FONDO)
        card = tk.Frame(f, bg=C_BLANCO, padx=40, pady=40, highlightbackground="#e0e0e0", highlightthickness=1)
        card.place(relx=0.5, rely=0.45, anchor="center", width=700)
        
        tk.Label(card, text="📤 Centro de Exportación y Publicación", font=("Segoe UI", 22, "bold"), bg=C_BLANCO, fg=C_MORADO).pack(anchor="w", pady=(0, 10))
        tk.Label(card, text="Genera el acta oficial en PDF o publica el cuadrante en el Portal Web de la Agonía.", font=("Segoe UI", 12), bg=C_BLANCO, fg="#666").pack(anchor="w", pady=(0, 20))
        
        fila_anio = tk.Frame(card, bg=C_BLANCO)
        fila_anio.pack(fill=tk.X, pady=(0, 20))
        tk.Label(fila_anio, text="Año de la procesión a exportar:", bg=C_BLANCO, font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        entry_anio = tk.Entry(fila_anio, font=("Segoe UI", 14), width=10, bg="#f9f9f9", relief="solid", bd=1)
        entry_anio.insert(0, str(datetime.datetime.now().year))
        entry_anio.pack(side=tk.LEFT, padx=15)

        var_tipo = tk.StringVar(value="Viernes Santo")
        style = ttk.Style()
        style.configure("TRadiobutton", background=C_BLANCO, font=("Segoe UI", 12))
        
        ttk.Radiobutton(card, text="Miércoles Santo", variable=var_tipo, value="Miércoles Santo").pack(anchor="w", pady=5)
        ttk.Radiobutton(card, text="Viernes Santo", variable=var_tipo, value="Viernes Santo").pack(anchor="w", pady=5)
        
        # Variable de control del estado
        estado_exportacion = {
            "archivo_ruta": None,
            "datos_json": None,
            "revisado": False
        }

        # --- PANEL DE CONTROL DE PUBLICACIÓN (Oculto al inicio) ---
        panel_pub = tk.Frame(card, bg="#f4f6f8", bd=1, relief="solid", padx=20, pady=20)
        
        lbl_info_archivo = tk.Label(panel_pub, text="", font=("Segoe UI", 11, "bold"), bg="#f4f6f8", fg=C_MORADO)
        lbl_info_archivo.pack(anchor="w", pady=(0, 15))

        btn_vista_previa = tk.Button(panel_pub, text="👁️ 1. VISTA PREVIA E IMPRIMIR PDF", font=("Segoe UI", 12, "bold"), bg="#17517e", fg="white", cursor="hand2")
        btn_vista_previa.pack(fill=tk.X, pady=5, ipady=5)

        btn_publicar = tk.Button(panel_pub, text="🌐 2. PUBLICAR EN EL PORTAL WEB", font=("Segoe UI", 12, "bold"), bg="#27ae60", fg="white", cursor="hand2", state="disabled")
        btn_publicar.pack(fill=tk.X, pady=5, ipady=5)
        
        tk.Label(panel_pub, text="* Es obligatorio revisar la vista previa (PDF) antes de poder publicar en internet.", font=("Segoe UI", 9, "italic"), bg="#f4f6f8", fg="#666").pack(anchor="w", pady=(0,15))

        btn_despublicar = tk.Button(panel_pub, text="🗑️ DESPUBLICAR Y OCULTAR DE LA WEB", font=("Segoe UI", 10, "bold"), bg="#ff4757", fg="white", cursor="hand2")
        btn_despublicar.pack(fill=tk.X, pady=(10,0), ipady=4)

        # LÓGICA DE LOS BOTONES
        def cargar_datos():
            archivo = filedialog.askopenfilename(title="Selecciona el cuadrante final (.json)", filetypes=[("Archivos JSON", "*.json")])
            if archivo:
                try:
                    with open(archivo, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    
                    estado_exportacion["archivo_ruta"] = archivo
                    estado_exportacion["datos_json"] = datos
                    estado_exportacion["revisado"] = False
                    
                    # Validar coincidencia del archivo con la opción marcada
                    t_proc = datos.get("tipo_procesion", "")
                    if var_tipo.get() == "Viernes Santo" and t_proc != "viernes_santo":
                        messagebox.showwarning("Atención", "Has marcado Viernes Santo pero has cargado un archivo del Miércoles Santo.\nEl PDF podría generarse mal.")
                    elif var_tipo.get() == "Miércoles Santo" and t_proc != "miercoles_santo":
                        messagebox.showwarning("Atención", "Has marcado Miércoles Santo pero has cargado un archivo del Viernes Santo.\nEl PDF podría generarse mal.")
                    
                    btn_publicar.config(state="disabled") 
                    lbl_info_archivo.config(text=f"✅ Archivo cargado y listo:\n{os.path.basename(archivo)}")
                    panel_pub.pack(fill=tk.X, pady=15)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")

        def hacer_vista_previa():
            if not estado_exportacion["archivo_ruta"]:
                return
            
            anio = int(entry_anio.get()) if entry_anio.get().isdigit() else datetime.datetime.now().year
            exito, msg = crear_html_informe(var_tipo.get(), estado_exportacion["archivo_ruta"], anio)
            
            if exito:
                self.abrir_navegador(msg)
                estado_exportacion["revisado"] = True
                btn_publicar.config(state="normal") # ¡Se desbloquea el botón de publicar!
                messagebox.showinfo("Revisión Necesaria", "Se ha abierto el borrador del PDF en tu navegador.\n\nRevísalo a fondo. Si ves que está todo perfecto, vuelve aquí y pulsa el botón verde de 'PUBLICAR EN EL PORTAL WEB'.")
            else:
                messagebox.showerror("Error", f"Error al generar la vista previa: {msg}")

        def publicar():
            if not estado_exportacion["revisado"]:
                messagebox.showwarning("Aviso de Seguridad", "Por seguridad, el sistema exige que previsualices el PDF antes de mandarlo a internet.")
                return
                
            datos_subir = estado_exportacion["datos_json"]
            tipo_procesion_nube = "miercoles_santo" if var_tipo.get() == "Miércoles Santo" else "viernes_santo"
            url_firebase = f"https://licencias-gestor-cofrade-default-rtdb.europe-west1.firebasedatabase.app/cuadrantes/agonia/{tipo_procesion_nube}.json"
            
            try:
                btn_publicar.config(text="⏳ COMPROBANDO NUBE...", state="disabled")
                self.root.update()
                
                # 1. Comprobamos si ya existe una publicación previa
                resp_get = requests.get(url_firebase, timeout=5)
                
                if resp_get.status_code == 200 and resp_get.json() is not None:
                    # Ya hay algo publicado
                    confirmacion = messagebox.askyesno(
                        "⚠️ ¡ATENCIÓN: SOBREESCRITURA!", 
                        f"El sistema ha detectado que YA EXISTE un cuadrante del {var_tipo.get()} publicado en el Portal Web.\n\n¿Estás completamente seguro de que deseas SOBREESCRIBIRLO con la nueva versión que acabas de revisar?"
                    )
                    if not confirmacion:
                        btn_publicar.config(text="🌐 2. PUBLICAR EN EL PORTAL WEB", state="normal")
                        return
                else:
                    # No hay nada publicado
                    confirmacion = messagebox.askyesno(
                        "Confirmar Publicación", 
                        f"Vas a hacer público en internet el cuadrante del {var_tipo.get()}.\nLos costaleros que tengan el enlace podrán verlo.\n\n¿Deseas continuar?"
                    )
                    if not confirmacion:
                        btn_publicar.config(text="🌐 2. PUBLICAR EN EL PORTAL WEB", state="normal")
                        return

                # 2. Procedemos a publicar (PUT)
                btn_publicar.config(text="⏳ SUBIENDO A LA NUBE...")
                self.root.update()
                
                resp_put = requests.put(url_firebase, json=datos_subir, timeout=10)
                
                if resp_put.status_code == 200:
                    messagebox.showinfo("✅ Publicación Exitosa", f"¡El cuadrante del {var_tipo.get()} ya está publicado en internet de forma segura!\n\nYa puedes compartir el enlace del Portal Web con los costaleros.")
                else:
                    messagebox.showerror("Error del Servidor", f"Ocurrió un problema en la nube al subir los datos.\nCódigo de error: {resp_put.status_code}")
                    
            except Exception as e:
                messagebox.showerror("Error de Conexión", f"No se ha podido conectar con el Portal Web.\nRevisa tu conexión a internet.\n\nDetalle técnico: {str(e)}")
            finally:
                btn_publicar.config(text="🌐 2. PUBLICAR EN EL PORTAL WEB", state="normal")

        def despublicar():
            tipo_procesion_nube = "miercoles_santo" if var_tipo.get() == "Miércoles Santo" else "viernes_santo"
            url_firebase = f"https://licencias-gestor-cofrade-default-rtdb.europe-west1.firebasedatabase.app/cuadrantes/agonia/{tipo_procesion_nube}.json"
            
            confirmacion = messagebox.askyesno(
                "⚠️ Confirmar Despublicación", 
                f"Estás a punto de ELIMINAR DE INTERNET el cuadrante público del {var_tipo.get()}.\n\nLos costaleros dejarán de tener acceso al mismo y verán un aviso de 'Cuadrante no disponible'.\n\n¿Estás completamente seguro?"
            )
            
            if not confirmacion: 
                return
            
            try:
                resp_del = requests.delete(url_firebase, timeout=5)
                if resp_del.status_code == 200:
                    messagebox.showinfo("🗑️ Despublicación Correcta", f"El cuadrante del {var_tipo.get()} se ha eliminado correctamente de la web.\n\nLa información ya es privada de nuevo.")
                else:
                    messagebox.showerror("Error", f"No se pudo eliminar el archivo en la nube: {resp_del.status_code}")
            except Exception as e:
                messagebox.showerror("Error de Conexión", f"No se pudo conectar a la nube.\n{str(e)}")

        # Asignamos las funciones a los botones
        btn_vista_previa.config(command=hacer_vista_previa)
        btn_publicar.config(command=publicar)
        btn_despublicar.config(command=despublicar)

        btn_cargar = self.crear_boton_moderno(card, "📂 1º SELECCIONAR CUADRANTE (.JSON)", C_MORADO, C_MORADO_HOVER, C_BLANCO, command=cargar_datos)
        btn_cargar.pack(anchor="w", fill=tk.X)
        return f

    # --- PANTALLA CENSO ---
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
        
        btn_cargar = self.crear_boton_moderno(toolbar, "📂 Cargar Censo", "#17517e", "#1f6b9c", C_BLANCO, command=self.cargar_censo_externo)
        btn_cargar.pack(side=tk.LEFT, padx=10)
        
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

        columnas = ("ID", "Nombre", "Telefono", "Altura", "Hombro", "Miércoles", "Viernes")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre del Costalero")
        self.tree.heading("Telefono", text="Teléfono")
        self.tree.heading("Altura", text="Altura (cm)")
        self.tree.heading("Hombro", text="Preferencia")
        self.tree.heading("Miércoles", text="M. Santo")
        self.tree.heading("Viernes", text="V. Santo")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Nombre", width=220)
        self.tree.column("Telefono", width=120, anchor="center")
        self.tree.column("Altura", width=100, anchor="center")
        self.tree.column("Hombro", width=120, anchor="center")
        self.tree.column("Miércoles", width=100, anchor="center")
        self.tree.column("Viernes", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        return f

    def cargar_censo_externo(self):
        archivo_nuevo = filedialog.askopenfilename(
            title="Seleccionar archivo de Censo Local (datos.json)",
            filetypes=[("Archivos JSON", "*.json")]
        )
        if not archivo_nuevo:
            return

        confirmacion = messagebox.askyesno(
            "⚠️ Atención: Sobreescritura",
            "Vas a reemplazar el censo actual por el archivo seleccionado.\n\n"
            "El sistema creará una copia de seguridad automática del censo antiguo por precaución.\n\n"
            "¿Estás completamente seguro de querer continuar?"
        )
        if not confirmacion:
            return

        archivo_actual = CONFIG['archivo_datos']
        if os.path.exists(archivo_actual):
            fecha_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_backup = f"censo_backup_{fecha_str}.json"
            try:
                shutil.copy(archivo_actual, archivo_backup)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear la copia de seguridad: {e}")
                return

        try:
            with open(archivo_nuevo, 'r', encoding='utf-8') as f:
                nuevos_datos = json.load(f)
            
            if not isinstance(nuevos_datos, list):
                raise ValueError("El archivo no tiene la estructura de censo correcta.")

            with open(archivo_actual, 'w', encoding='utf-8') as f:
                json.dump(nuevos_datos, f, indent=4, ensure_ascii=False)
            
            self.actualizar_tabla_censo()
            
            msg = "Censo actualizado correctamente.\n\n"
            if os.path.exists(archivo_actual):
                msg += f"Se ha guardado tu censo anterior a salvo en el archivo:\n{archivo_backup}"
            messagebox.showinfo("Éxito", msg)
            
        except Exception as e:
            messagebox.showerror("Error de Formato", f"El archivo seleccionado no es válido o está dañado:\n{e}")

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
                telefono = p.get("telefono", "")
                if not hombro: hombro = "Indiferente"
                self.tree.insert("", tk.END, values=(p['id'], p['nombre'], telefono, p['altura'], hombro.capitalize(), mi, vi))

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

        top = tk.Toplevel(self.root)
        top.title("Editar Costalero" if editar else "Nuevo Costalero")
        top.geometry("400x530")
        top.configure(bg=C_BLANCO)
        
        top.resizable(True, True)
        top.transient(self.root) 
        top.grab_set()

        top.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (530 // 2)
        top.geometry(f"+{x}+{y}")

        tk.Label(top, text="📋 Ficha del Costalero", font=("Segoe UI", 16, "bold"), bg=C_BLANCO, fg=C_MORADO).pack(pady=(20, 20))

        form_frame = tk.Frame(top, bg=C_BLANCO)
        form_frame.pack(padx=40, fill=tk.BOTH, expand=True)

        tk.Label(form_frame, text="Nombre Completo:", bg=C_BLANCO, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        var_nombre = tk.StringVar(value=costalero['nombre'] if costalero else "")
        tk.Entry(form_frame, textvariable=var_nombre, font=("Segoe UI", 12), relief="solid", bd=1).pack(fill=tk.X, pady=(2, 10))

        tk.Label(form_frame, text="Teléfono:", bg=C_BLANCO, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        var_telefono = tk.StringVar(value=costalero.get('telefono', '') if costalero else "")
        tk.Entry(form_frame, textvariable=var_telefono, font=("Segoe UI", 12), relief="solid", bd=1).pack(fill=tk.X, pady=(2, 10))

        tk.Label(form_frame, text="Altura (en cm):", bg=C_BLANCO, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        var_altura = tk.StringVar(value=str(costalero['altura']) if costalero else "")
        tk.Entry(form_frame, textvariable=var_altura, font=("Segoe UI", 12), relief="solid", bd=1).pack(fill=tk.X, pady=(2, 10))

        tk.Label(form_frame, text="Preferencia de Hombro:", bg=C_BLANCO, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        var_hombro = tk.StringVar(value=costalero.get('pref_hombro', 'Indiferente') if costalero and costalero.get('pref_hombro') else "Indiferente")
        combo_hombro = ttk.Combobox(form_frame, textvariable=var_hombro, values=["Derecho", "Izquierdo", "Ambos", "Indiferente"], state="readonly", font=("Segoe UI", 11))
        combo_hombro.pack(fill=tk.X, pady=(2, 15))

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
                costalero['nombre'] = var_nombre.get().strip()
                costalero['telefono'] = var_telefono.get().strip()
                costalero['altura'] = int(var_altura.get())
                costalero['pref_hombro'] = hombro_val
                costalero['miercoles_santo'] = var_miercoles.get()
                costalero['viernes_santo'] = var_viernes.get()
            else:
                nuevo_id = max([p.get('id', 0) for p in datos], default=0) + 1
                datos.append({
                    "id": nuevo_id,
                    "nombre": var_nombre.get().strip(),
                    "telefono": var_telefono.get().strip(),
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
        btn_guardar.pack(fill=tk.X, padx=40, pady=(20, 0), ipady=8)

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
    app = GestorCofradeAPP(root)
    
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    root.mainloop()