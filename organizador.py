import math

# --- CONFIGURACIÓN DE PARÁMETROS ---
# "" para que el programa decida, o un número (ej: 3) para forzar turnos
NUM_TURNOS = "" 
# True para obligar a que haya 6 personas por vara (rellena con "HUECO VACÍO" o repetidos)
FORZAR_6_HUECOS = True 

def generar_turnos(costaleros, n_turnos_config, forzar_6):
    """
    Lógica principal de organización. 
    Prioridad: Nivelación del trono (simetría de alturas).
    """
    VARAS = ["Izquierda", "Centro", "Derecha"]
    SECCIONES = ["Delante", "Detrás"]
    HUECOS_POR_SECCION = 6
    PUESTOS_POR_TURNO = 36

    # 1. Determinar número de turnos
    if n_turnos_config == "":
        n_turnos = math.ceil(len(costaleros) / PUESTOS_POR_TURNO)
    else:
        n_turnos = int(n_turnos_config)

    # 2. Preparar el pool de datos (Ordenado por altura para nivelar)
    # Ordenamos de mayor a menor para colocar a los más altos en los puestos clave
    pool = sorted(costaleros, key=lambda x: x['altura'], reverse=True)
    
    # Manejo de repeticiones si faltan personas para cubrir los turnos
    total_necesario = n_turnos * PUESTOS_POR_TURNO
    while len(pool) < total_necesario:
        # Clonamos empezando por los que más se necesitan para cuadrar alturas
        pool.append({**pool[len(pool) % len(costaleros)], "nombre": f"{pool[len(pool) % len(costaleros)]['nombre']} (R)"})

    # 3. Creación de la estructura de turnos
    resultado = {}
    
    for t in range(n_turnos):
        id_turno = f"Turno {chr(65 + t)}"
        resultado[id_turno] = {v: {s: [] for s in SECCIONES} for v in VARAS}
        
        # Selección del bloque de 36 personas para este turno
        bloque = pool[t * PUESTOS_POR_TURNO : (t + 1) * PUESTOS_POR_TURNO]
        
        # Sub-bloques: Los 18 más altos para DELANTE, los 18 siguientes para DETRÁS
        bloque_delante = bloque[:18]
        bloque_detras = bloque[18:]

        # Función interna para distribuir en las 3 varas de forma nivelada
        def distribuir_seccion(personas, seccion_nombre, turno_ref):
            # Usamos un patrón de distribución 0, 1, 2, 2, 1, 0... para equilibrar varas
            indices_varas = [0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0]
            for i, p in enumerate(personas):
                vara_target = VARAS[indices_varas[i]]
                resultado[turno_ref][vara_target][seccion_nombre].append(p)

        distribuir_seccion(bloque_delante, "Delante", id_turno)
        distribuir_seccion(bloque_detras, "Detrás", id_turno)

    return resultado

def visualizar_consola(turnos_dict):
    """Muestra el resultado final de forma esquemática"""
    for id_t, contenido in turnos_dict.items():
        print(f"\n{'='*60}\n ESTRUCTURA: {id_t}\n{'='*60}")
        for vara in ["Izquierda", "Centro", "Derecha"]:
            print(f"\n--- VARA {vara.upper()} ---")
            for sec in ["Delante", "Detrás"]:
                personas = contenido[vara][sec]
                alturas = [p['altura'] for p in personas]
                media = sum(alturas)/len(alturas) if alturas else 0
                print(f"  > {sec} (Media: {media:.1f} cm):")
                for i, p in enumerate(personas):
                    print(f"    {i+1}. {p['nombre'][:20]:<20} | {p['altura']} cm")

# --- LÓGICA DE INICIO ---
# Aquí es donde importarías tu datos.js (o lo cargarías vía json.load)
if __name__ == "__main__":
    # Simulando la importación de costaleros desde tu archivo externo
    from datos import COSTALEROS # Asumiendo que conviertes el .js a un formato legible por python
    
    turnos_finales = generar_turnos(COSTALEROS, NUM_TURNOS, FORZAR_6_HUECOS)
    visualizar_consola(turnos_finales)