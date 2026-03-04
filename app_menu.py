import sys
import os
import datetime
import json
import tkinter as tk
from tkinter import filedialog

# Importamos las lógicas independientes
from logica_trono import cargar_datos, generar_turnos_base, generar_html_interactivo
from logica_miercoles import cargar_datos_miercoles, generar_cuadrillas_miercoles, generar_html_miercoles
from logica_viernes import cargar_datos_viernes, generar_cuadrillas_viernes, generar_html_viernes
from logica_ensayos import generar_html_ensayo
from logica_informes import crear_html_informe

# ==========================================
# VARIABLES GLOBALES
# ==========================================
CONFIG = {
    "peso_trono_kg": 2000,
    "peso_cruz_kg": 200,      
    "limite_peso_persona": 90,
    "plazas_turno_a": 36,
    "archivo_datos": "datos.json"
}

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def guardar_censo(datos):
    """Guarda la lista completa de costaleros sobreescribiendo datos.json"""
    try:
        with open(CONFIG['archivo_datos'], 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        print("\n✅ ¡Base de datos (datos.json) actualizada y guardada correctamente!")
    except Exception as e:
        print(f"\n❌ Error al guardar el archivo: {e}")

def buscar_costalero(datos, busqueda):
    """Busca por ID o por coincidencia de nombre y devuelve la lista de coincidencias"""
    if busqueda.isdigit():
        return [p for p in datos if p.get('id') == int(busqueda)]
    else:
        return [p for p in datos if busqueda.lower() in p['nombre'].lower()]

# ==========================================
# MENÚS PRINCIPALES
# ==========================================
def menu_principal():
    while True:
        limpiar_pantalla()
        print("==================================================")
        print("⚜️ GESTOR COFRADE - SISTEMA CENTRAL ⚜️")
        print("==================================================")
        print("[1] 💻 Simulador Web (Prueba Libre)")
        print("[2] 🕯️ Gestión de Procesiones (Fechas Oficiales)")
        print("[3] 📋 Organizador de Ensayos (En vivo)")
        print("[4] 👥 Gestión del Censo (Añadir/Modificar)")
        print("[5] 📄 Exportar PDF Oficial (Para WhatsApp)")
        print("[0] ❌ Salir del Sistema")
        print("==================================================")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == '1':
            submenu_simulador()
        elif opcion == '2':
            submenu_procesiones()
        elif opcion == '3':
            gestion_ensayos()
        elif opcion == '4':
            submenu_censo()
        elif opcion == '5':
            submenu_informes()
        elif opcion == '0':
            print("\nCerrando sistema... ¡Buen ensayo!")
            sys.exit()
        else:
            print("\n❌ Opción no válida. Inténtalo de nuevo.")
            input("Pulsa Enter para continuar...")

def submenu_censo():
    """Gestor CRUD para el archivo datos.json"""
    while True:
        limpiar_pantalla()
        datos_actuales = cargar_datos(CONFIG['archivo_datos'])
        
        print("==================================================")
        print(f"👥 GESTIÓN DEL CENSO ({len(datos_actuales)} costaleros totales)")
        print("==================================================")
        print("[1] ➕ Añadir nuevo costalero (Alta)")
        print("[2] 🔍 Buscar / Ver lista de costaleros")
        print("[3] ✏️ Modificar costalero existente")
        print("[4] ❌ Eliminar costalero (Baja)")
        print("[0] ⬅️ Volver al Menú Principal")
        print("==================================================")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == '1':
            print("\n--- NUEVO COSTALERO ---")
            nombre = input("Nombre completo: ").strip()
            altura_str = input("Altura (en cm, ej: 175): ").strip()
            hombro = input("Preferencia de hombro (Izquierdo/Derecho/Ambos) [Enter para dejar en blanco]: ").strip()
            
            if nombre and altura_str.isdigit():
                nuevo_id = max([p.get('id', 0) for p in datos_actuales], default=0) + 1
                nuevo_costalero = {
                    "id": nuevo_id,
                    "nombre": nombre,
                    "altura": int(altura_str),
                    "pref_hombro": hombro,
                    "puede_repetir": True,
                    "miercoles_santo": True,
                    "viernes_santo": True
                }
                datos_actuales.append(nuevo_costalero)
                guardar_censo(datos_actuales)
            else:
                print("❌ Datos inválidos. La altura debe ser un número y el nombre no puede estar vacío.")
            input("Pulsa Enter para continuar...")
            
        elif opcion == '2':
            print("\n--- BUSCADOR DEL CENSO ---")
            termino = input("Escribe un nombre para buscar (o pulsa Enter para ver a todos): ").strip().lower()
            
            print("\nRESULTADOS:")
            encontrados = [p for p in datos_actuales if termino in p['nombre'].lower()]
            encontrados.sort(key=lambda x: x['nombre'])
            
            for p in encontrados:
                mi = "✅" if p.get("miercoles_santo", False) else "❌"
                vi = "✅" if p.get("viernes_santo", False) else "❌"
                hombro = p.get('pref_hombro', 'N/A')
                if not hombro: hombro = 'N/A'
                print(f"[ID: {p['id']:>3}] {p['nombre']:<25} | {p['altura']}cm | Hombro: {hombro:<9} | Miér: {mi} | Vier: {vi}")
                
            print(f"\nMostrando {len(encontrados)} resultados.")
            input("Pulsa Enter para continuar...")
            
        elif opcion == '3':
            print("\n--- MODIFICAR COSTALERO ---")
            busqueda = input("Introduce el ID numérico o el NOMBRE del costalero a modificar: ").strip()
            
            if busqueda:
                encontrados = buscar_costalero(datos_actuales, busqueda)
                
                if len(encontrados) == 0:
                    print("❌ No se ha encontrado a nadie con ese dato.")
                elif len(encontrados) > 1:
                    print("⚠️ Se han encontrado varios costaleros con ese nombre. Por favor, usa su ID numérico:")
                    for p in encontrados:
                        print(f"  - [ID: {p['id']}] {p['nombre']}")
                else:
                    costalero = encontrados[0]
                    print(f"\nEditando a: {costalero['nombre']} (Actual: {costalero['altura']}cm)")
                    print("*(Pulsa ENTER sin escribir nada para mantener el valor actual)*")
                    
                    n_nombre = input(f"Nuevo nombre [{costalero['nombre']}]: ").strip()
                    n_altura = input(f"Nueva altura en cm [{costalero['altura']}]: ").strip()
                    
                    hombro_actual = costalero.get('pref_hombro', '')
                    n_hombro = input(f"Preferencia de hombro (Izquierdo/Derecho/Ambos) [{hombro_actual}]: ").strip()
                    
                    n_mi = input(f"¿Sale Miércoles Santo? (S/N) [{'S' if costalero.get('miercoles_santo') else 'N'}]: ").strip().upper()
                    n_vi = input(f"¿Sale Viernes Santo? (S/N) [{'S' if costalero.get('viernes_santo') else 'N'}]: ").strip().upper()
                    
                    if n_nombre: costalero['nombre'] = n_nombre
                    if n_altura.isdigit(): costalero['altura'] = int(n_altura)
                    if n_hombro: costalero['pref_hombro'] = n_hombro
                    if n_mi == 'S': costalero['miercoles_santo'] = True
                    elif n_mi == 'N': costalero['miercoles_santo'] = False
                    if n_vi == 'S': costalero['viernes_santo'] = True
                    elif n_vi == 'N': costalero['viernes_santo'] = False
                    
                    guardar_censo(datos_actuales)
            input("Pulsa Enter para continuar...")
            
        elif opcion == '4':
            print("\n--- ELIMINAR COSTALERO (BAJA) ---")
            busqueda = input("Introduce el ID numérico o el NOMBRE del costalero a borrar: ").strip()
            
            if busqueda:
                encontrados = buscar_costalero(datos_actuales, busqueda)
                
                if len(encontrados) == 0:
                    print("❌ No se ha encontrado a nadie con ese dato.")
                elif len(encontrados) > 1:
                    print("⚠️ Se han encontrado varios costaleros con ese nombre. Por favor, usa su ID numérico:")
                    for p in encontrados:
                        print(f"  - [ID: {p['id']}] {p['nombre']}")
                else:
                    costalero = encontrados[0]
                    seguro = input(f"⚠️ ¿Estás COMPLETAMENTE SEGURO de querer borrar a {costalero['nombre']}? (S/N): ").strip().upper()
                    if seguro == 'S':
                        datos_actuales = [p for p in datos_actuales if p.get('id') != costalero['id']]
                        guardar_censo(datos_actuales)
                        print(f"🗑️ Costalero borrado con éxito.")
                    else:
                        print("Operación cancelada.")
            input("Pulsa Enter para continuar...")
            
        elif opcion == '0':
            break

def submenu_simulador():
    while True:
        limpiar_pantalla()
        print("==================================================")
        print("💻 SIMULADOR WEB - MODO LIBRE")
        print("==================================================")
        print(f"[1] Configurar Peso del Trono     (Actual: {CONFIG['peso_trono_kg']} kg)")
        print(f"[2] Configurar Plazas Bloque A    (Actual: {CONFIG['plazas_turno_a']})")
        print(f"[3] 🚀 GENERAR SIMULADOR HTML")
        print("[0] ⬅️ Volver al Menú Principal")
        print("==================================================")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == '1':
            val = input("\nIntroduce peso estimado del trono en kg: ")
            if val.isdigit(): CONFIG['peso_trono_kg'] = int(val)
        elif opcion == '2':
            val = input("\nIntroduce plazas para el Turno A (Máx 36): ")
            if val.isdigit(): CONFIG['plazas_turno_a'] = int(val)
        elif opcion == '3':
            master_list = cargar_datos(CONFIG['archivo_datos'])
            turnos = generar_turnos_base(master_list, "", CONFIG['plazas_turno_a'])
            generar_html_interactivo(turnos, master_list, CONFIG['peso_trono_kg'], CONFIG['limite_peso_persona'])
            print("\n✅ ¡LISTO! Visualizador generado.")
            print("Abre el archivo 'visualizador_interactivo.html' en tu navegador.")
            input("\nPulsa Enter para continuar...")
        elif opcion == '0':
            break 

def submenu_procesiones():
    while True:
        limpiar_pantalla()
        print("==================================================")
        print("🕯️ GESTIÓN DE PROCESIONES OFICIALES")
        print("==================================================")
        print("[1] Miércoles Santo (Trono + Cruz)")
        print("[2] Viernes Santo (3 Turnos + 4 Cruces)")
        print("[0] ⬅️ Volver al Menú Principal")
        print("==================================================")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == '1':
            gestion_miercoles_santo()
        elif opcion == '2':
            gestion_viernes_santo()
        elif opcion == '0':
            break

def gestion_miercoles_santo():
    limpiar_pantalla()
    print("==================================================")
    print("📅 CONFIGURACIÓN: MIÉRCOLES SANTO")
    print("==================================================")
    
    anio_input = input("Introduce el año de la procesión (Ej: 2026) o pulsa Enter para año actual: ")
    anio_manual = int(anio_input) if anio_input.isdigit() else datetime.datetime.now().year
    
    master_list = cargar_datos_miercoles(CONFIG['archivo_datos'])
    if not master_list: return
        
    datos_cuadrillas = generar_cuadrillas_miercoles(master_list)
    generar_html_miercoles(datos_cuadrillas, master_list, anio_manual, (anio_manual % 2 == 0), CONFIG['peso_trono_kg'], CONFIG['peso_cruz_kg'], CONFIG['limite_peso_persona'])
    
    print("\n✅ Visualizador del Miércoles Santo generado en 'visualizador_miercoles.html'")
    input("\nPulsa Enter para continuar...")

def gestion_viernes_santo():
    limpiar_pantalla()
    print("==================================================")
    print("📅 CONFIGURACIÓN: VIERNES SANTO")
    print("==================================================")
    
    anio_input = input("Introduce el año de la procesión (Ej: 2026) o pulsa Enter para año actual: ")
    anio_manual = int(anio_input) if anio_input.isdigit() else datetime.datetime.now().year
    es_par = (anio_manual % 2 == 0)
    
    print("\nCargando censo filtrado para el Viernes Santo...")
    master_list = cargar_datos_viernes(CONFIG['archivo_datos'])
    
    if not master_list:
        print("❌ Error: No hay personas marcadas para el Viernes Santo.")
        input("\nPulsa Enter para continuar...")
        return
        
    print(f"✅ Encontrados {len(master_list)} costaleros/as disponibles.")
    print("🧠 Calculando físicas, turnos A/B/C y organizando las 4 Cruces con descansos obligatorios...")
    
    datos_completos = generar_cuadrillas_viernes(master_list)
    
    generar_html_viernes(
        datos_completos=datos_completos,
        master_list=master_list,
        anio=anio_manual,
        es_par=es_par,
        peso_trono=CONFIG['peso_trono_kg'],
        peso_cruz=CONFIG['peso_cruz_kg'],
        limite_peso=CONFIG['limite_peso_persona']
    )
    
    print("\n✅ ¡LISTO! Visualizador del Viernes Santo generado.")
    print("Abre el archivo 'visualizador_viernes.html' en tu navegador.")
    input("\nPulsa Enter para continuar...")

def gestion_ensayos():
    limpiar_pantalla()
    print("==================================================")
    print("📋 ORGANIZADOR DE ENSAYOS DINÁMICO")
    print("==================================================")
    val = input("¿Cuántos turnos (de 36 plazas) quieres crear para el ensayo?: ")
    
    if val.isdigit() and int(val) > 0:
        num_turnos = int(val)
        print("\nCargando censo general de costaleros...")
        master_list = cargar_datos(CONFIG['archivo_datos'])
        
        if not master_list:
            print("❌ Error: No se encontró el censo de datos.json.")
            input("Pulsa Enter para volver...")
            return
            
        print("Preparando el entorno interactivo...")
        generar_html_ensayo(num_turnos, master_list, CONFIG['peso_trono_kg'], CONFIG['limite_peso_persona'])
        print("\n✅ ¡MÓDULO DE ENSAYO CREADO!")
        print("Abre el archivo 'visualizador_ensayos.html' en tu navegador.")
        print("💡 Toda la gestión (añadir personas y auto-organizar) se hace en la web.")
    else:
        print("\n❌ Número no válido. Debes introducir un número (ej: 2).")
        
    input("\nPulsa Enter para continuar...")

def submenu_informes():
    while True:
        limpiar_pantalla()
        print("==================================================")
        print("📄 GENERADOR DE INFORMES (PDF PARA WHATSAPP)")
        print("==================================================")
        print("💡 Instrucciones: Primero debes ir a 'Gestión de Procesiones',")
        print("configurar el trono en la web y darle al botón dorado de")
        print("'💾 DESCARGAR DATOS'. Luego entraremos aquí para seleccionarlo.")
        print("--------------------------------------------------")
        print("[1] Miércoles Santo")
        print("[2] Viernes Santo")
        print("[3] Procesión Extraordinaria")
        print("[0] ⬅️ Volver al Menú Principal")
        print("==================================================")
        
        opcion = input("Selecciona qué procesión vas a generar: ")
        
        if opcion in ['1', '2', '3']:
            tipo = ""
            if opcion == '1': tipo = "Miércoles Santo"
            elif opcion == '2': tipo = "Viernes Santo"
            elif opcion == '3': tipo = "Procesión Extraordinaria"
            
            print(f"\nHas seleccionado: {tipo}")
            print("\n⏳ Abriendo el explorador de archivos...")
            print("(Si no ves la ventana, busca el icono de Python o la ventana detrás de tu terminal)")
            
            # Inicializamos Tkinter pero ocultamos la ventana principal blanca
            root = tk.Tk()
            root.withdraw()
            
            # En Mac a veces las ventanas salen detrás, esto fuerza a que salga por encima
            root.call('wm', 'attributes', '.', '-topmost', True)
            
            # Abrimos el cuadro de diálogo para que elijas el archivo
            archivo = filedialog.askopenfilename(
                title="Selecciona el archivo JSON descargado de la web",
                filetypes=[("Archivos de Datos JSON", "*.json"), ("Todos los archivos", "*.*")]
            )
            
            if archivo:
                # Extraemos el nombre final del archivo para que la consola se vea limpia
                nombre_archivo = os.path.basename(archivo)
                print(f"\n📁 Archivo seleccionado: {nombre_archivo}")
                
                exito, msg = crear_html_informe(tipo, archivo)
                
                if exito:
                    print("\n✅ ¡Informe maquetado con éxito!")
                    print(f"👉 Abre el archivo '{msg}' en tu navegador para ver el resultado y descargar el PDF.")
                else:
                    print(f"\n❌ Error al leer el archivo: {msg}")
            else:
                print("\n⚠️ Operación cancelada. No has seleccionado ningún archivo.")
            
            input("\nPulsa Enter para continuar...")
        elif opcion == '0':
            break
        else:
            print("\n❌ Opción no válida.")
            input("Pulsa Enter para continuar...")

if __name__ == "__main__":
    menu_principal()