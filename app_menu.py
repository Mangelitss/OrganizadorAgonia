import sys
import os
import datetime

# Importamos las 4 lógicas independientes
from logica_trono import cargar_datos, generar_turnos_base, generar_html_interactivo
from logica_miercoles import cargar_datos_miercoles, generar_cuadrillas_miercoles, generar_html_miercoles
from logica_viernes import cargar_datos_viernes, generar_cuadrillas_viernes, generar_html_viernes
from logica_ensayos import generar_html_ensayo

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

def menu_principal():
    while True:
        limpiar_pantalla()
        print("==================================================")
        print("⚜️ GESTOR COFRADE - SISTEMA CENTRAL ⚜️")
        print("==================================================")
        print("[1] 💻 Simulador Web (Prueba Libre)")
        print("[2] 🕯️ Gestión de Procesiones (Fechas Oficiales)")
        print("[3] 📋 Organizador de Ensayos (En vivo)")
        print("[0] ❌ Salir del Sistema")
        print("==================================================")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == '1':
            submenu_simulador()
        elif opcion == '2':
            submenu_procesiones()
        elif opcion == '3':
            gestion_ensayos()
        elif opcion == '0':
            print("\nCerrando sistema... ¡Buen ensayo!")
            sys.exit()
        else:
            print("\n❌ Opción no válida. Inténtalo de nuevo.")
            input("Pulsa Enter para continuar...")

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

def modulo_en_construccion(nombre_modulo):
    limpiar_pantalla()
    print(f"⚠️ MÓDULO EN MANTENIMIENTO: {nombre_modulo}")
    input("\nPulsa Enter para volver...")

if __name__ == "__main__":
    menu_principal()