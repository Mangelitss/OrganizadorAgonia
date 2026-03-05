import json
import time

def cargar_datos_viernes(archivo='datos.json'):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            return [d for d in datos if d.get('viernes_santo', False)]
    except Exception as e:
        print(f"Error cargando {archivo}: {e}")
        return []

def generar_cuadrillas_viernes(costaleros):
    pool = sorted(costaleros, key=lambda x: x.get('altura', 0), reverse=True)
    
    turno_a = pool[:36]
    while len(turno_a) < 36: turno_a.append({"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})
    
    turno_b = pool[36:72]
    while len(turno_b) < 36: turno_b.append({"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})
    
    turno_c = pool[72:108]
    if len(turno_c) < 36:
        repetidores_b = [p for p in turno_b if p.get('id', -1) != -1]
        repetidores_b.sort(key=lambda x: x.get('altura', 0)) 
        idx_rep = 0
        while len(turno_c) < 36:
            if idx_rep < len(repetidores_b):
                p_rep = repetidores_b[idx_rep].copy()
                p_rep["nombre"] = p_rep.get("nombre", "") + " (R)"
                turno_c.append(p_rep)
                idx_rep += 1
            else:
                turno_c.append({"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})
                
    cruz_turnos = [[], [], [], []]
    
    disp_b = [p.copy() for p in turno_b if p.get('id', -1) != -1]
    disp_c = [p.copy() for p in turno_c if p.get('id', -1) != -1 and not p.get('nombre', '').endswith('(R)')]
    
    disp_b.sort(key=lambda x: x.get('altura', 0), reverse=True)
    disp_c.sort(key=lambda x: x.get('altura', 0), reverse=True)

    def extraer_seguro(lista, cantidad):
        res = []
        while len(res) < cantidad and len(lista) > 0: res.append(lista.pop(0))
        return res

    cruz_turnos[1].extend(extraer_seguro(disp_c, 8)) 
    cruz_turnos[3].extend(extraer_seguro(disp_b, 8)) 
    cruz_turnos[0].extend(extraer_seguro(disp_c, 8)) 
    
    cruz_turnos[2].extend(extraer_seguro(disp_b, 4))
    cruz_turnos[2].extend(extraer_seguro(disp_c, 4))

    for i in range(4):
        while len(cruz_turnos[i]) < 8: 
            cruz_turnos[i].append({"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})

    for t in [0, 1, 3]:
        for p in cruz_turnos[t]: 
            if p.get('id', -1) != -1: p['nombre'] = p.get('nombre', '') + " (C)"
            
    for p in cruz_turnos[2]: 
        if p.get('id', -1) != -1: p['nombre'] = p.get('nombre', '') + " (C-Doble)"

    ids_cruz_normal = {p.get('id', -1) for t in [0, 1, 3] for p in cruz_turnos[t] if p.get('id', -1) != -1}
    ids_cruz_doble = {p.get('id', -1) for p in cruz_turnos[2] if p.get('id', -1) != -1}

    for p in turno_b:
        if p.get('id', -1) in ids_cruz_doble: p['nombre'] = p.get('nombre', '') + " (C-Doble)"
        elif p.get('id', -1) in ids_cruz_normal: p['nombre'] = p.get('nombre', '') + " (C)"
        
    for p in turno_c:
        if p.get('id', -1) != -1 and "(R)" not in p.get('nombre', ''):
            if p.get('id', -1) in ids_cruz_doble: p['nombre'] = p.get('nombre', '') + " (C-Doble)"
            elif p.get('id', -1) in ids_cruz_normal: p['nombre'] = p.get('nombre', '') + " (C)"

    def distribuir_trono(personas):
        varas = ["Izquierda", "Centro", "Derecha"]
        res = {v: {"Delante": [], "Detras": []} for v in varas}
        reales = [p for p in personas if p.get('altura', 0) > 0]
        huecos = [p for p in personas if p.get('altura', 0) == 0]
        reales.sort(key=lambda x: x.get('altura', 0), reverse=True)
        
        for _ in range(6):
            fila = []
            for _ in range(3): fila.append(reales.pop(0) if reales else huecos.pop(0) if huecos else {"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})
            asig = {"Izquierda": None, "Centro": None, "Derecha": None}
            libres = []
            for p in fila:
                pref = str(p.get('pref_hombro', '')).lower()
                if 'derech' in pref and asig["Izquierda"] is None: asig["Izquierda"] = p
                elif 'izquierd' in pref and asig["Derecha"] is None: asig["Derecha"] = p
                elif 'ambos' in pref and asig["Centro"] is None: asig["Centro"] = p
                else: libres.append(p)
            for v in varas:
                if asig[v] is None and libres: asig[v] = libres.pop(0)
            for v in varas: res[v]["Delante"].append(asig[v])
            
        reales.sort(key=lambda x: x.get('altura', 0))
        for _ in range(6):
            fila = []
            for _ in range(3): fila.append(reales.pop(0) if reales else huecos.pop(0) if huecos else {"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})
            asig = {"Izquierda": None, "Centro": None, "Derecha": None}
            libres = []
            for p in fila:
                pref = str(p.get('pref_hombro', '')).lower()
                if 'derech' in pref and asig["Izquierda"] is None: asig["Izquierda"] = p
                elif 'izquierd' in pref and asig["Derecha"] is None: asig["Derecha"] = p
                elif 'ambos' in pref and asig["Centro"] is None: asig["Centro"] = p
                else: libres.append(p)
            for v in varas:
                if asig[v] is None and libres: asig[v] = libres.pop(0)
            for v in varas: res[v]["Detras"].append(asig[v])
        return res

    def distribuir_cruz(personas):
        varas = ["Izquierda", "Derecha"]
        res = {v: {"Delante": [], "Detras": []} for v in varas}
        reales = [p for p in personas if p.get('altura', 0) > 0]
        huecos = [p for p in personas if p.get('altura', 0) == 0]
        
        reales.sort(key=lambda x: x.get('altura', 0), reverse=True)
        for _ in range(2):
            fila = []
            for _ in range(2): fila.append(reales.pop(0) if reales else huecos.pop(0) if huecos else {"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})
            asig = {"Izquierda": None, "Derecha": None}
            libres = []
            for p in fila:
                pref = str(p.get('pref_hombro', '')).lower()
                if 'derech' in pref and asig["Izquierda"] is None: asig["Izquierda"] = p
                elif 'izquierd' in pref and asig["Derecha"] is None: asig["Derecha"] = p
                else: libres.append(p)
            for v in varas:
                if asig[v] is None and libres: asig[v] = libres.pop(0)
            for v in varas: res[v]["Delante"].append(asig[v])
            
        reales.sort(key=lambda x: x.get('altura', 0))
        for _ in range(2):
            fila = []
            for _ in range(2): fila.append(reales.pop(0) if reales else huecos.pop(0) if huecos else {"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})
            asig = {"Izquierda": None, "Derecha": None}
            libres = []
            for p in fila:
                pref = str(p.get('pref_hombro', '')).lower()
                if 'derech' in pref and asig["Izquierda"] is None: asig["Izquierda"] = p
                elif 'izquierd' in pref and asig["Derecha"] is None: asig["Derecha"] = p
                else: libres.append(p)
            for v in varas:
                if asig[v] is None and libres: asig[v] = libres.pop(0)
            for v in varas: res[v]["Detras"].append(asig[v])
        return res

    # Incorporamos el "Sello" de procesión
    return {
        "tipo_procesion": "viernes_santo",
        "Trono": {"Turno A": distribuir_trono(turno_a), "Turno B": distribuir_trono(turno_b), "Turno C": distribuir_trono(turno_c)},
        "Cruz": {"Turno 1": distribuir_cruz(cruz_turnos[0]), "Turno 2": distribuir_cruz(cruz_turnos[1]), "Turno 3": distribuir_cruz(cruz_turnos[2]), "Turno 4": distribuir_cruz(cruz_turnos[3])}
    }


def generar_html_viernes(datos_completos, master_list, anio, es_par, peso_trono, peso_cruz, limite_peso):
    turnos_json = json.dumps(datos_completos)
    master_json = json.dumps(master_list)
    marca_tiempo = str(int(time.time()))

    try:
        with open('datos.json', 'r', encoding='utf-8') as f:
            censo_completo = f.read().strip()
            if not censo_completo: censo_completo = "[]"
    except:
        censo_completo = "[]"

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Viernes Santo - Gestor de Procesión</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #0c0209; color: #f8f0f5; padding: 20px; }}
            .controles {{ position: sticky; top: 0; background: #1a0514; padding: 15px; z-index: 100; border-bottom: 2px solid #d4af37; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }}
            
            .alerta-box {{ background: #b30000; color: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; border: 2px solid #ff4d4d; display: none; font-weight: bold; box-shadow: 0 0 15px rgba(255,0,0,0.5); }}
            .alerta-box ul {{ margin: 10px 0 0 0; padding-left: 20px; font-weight: normal; }}

            .buscador-box {{ background: #23061b; padding: 20px; margin: 20px 0; border: 1px solid #d4af37; border-radius: 8px; }}
            .buscador-box input {{ width: 100%; padding: 12px; font-size: 16px; background: #0c0209; color: #d4af37; border: 1px solid #3d0c2e; border-radius: 5px; outline: none; }}
            .itinerario-result {{ margin-top: 15px; display: none; }}
            
            .bloque-ruta {{ background: #160311; padding: 15px; border-radius: 5px; border-left: 5px solid #d4af37; margin-bottom: 10px; }}
            .bloque-ruta h5 {{ margin: 0 0 8px 0; color: #e8d08c; font-size: 14px; border-bottom: 1px solid #3d0c2e; padding-bottom: 5px; text-transform: uppercase; letter-spacing: 1px; }}
            .bloque-ruta ul {{ margin: 0; padding: 0; list-style: none; }}
            .bloque-ruta li {{ padding: 8px 0; border-bottom: 1px dashed #3d0c2e; font-size: 13px; display: flex; }}
            .tramo-label {{ width: 220px; color: #a37c95; flex-shrink: 0; }}

            .turno-container {{ background: #1a0514; padding: 20px; margin-bottom: 40px; border-radius: 15px; border: 1px solid #3d0c2e; box-shadow: 0 0 15px rgba(212, 175, 55, 0.05); }}
            .turno-container h2 {{ color: #d4af37; text-transform: uppercase; letter-spacing: 2px; border-bottom: 1px solid #3d0c2e; padding-bottom: 10px; }}
            .grid-trono {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
            .grid-cruz {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; max-width: 700px; margin: 0 auto; }}
            .vara {{ background: #23061b; padding: 15px; border-radius: 10px; border-top: 5px solid #d4af37; }}
            .vara h3 {{ color: #e8d08c; margin: 0 0 10px 0; font-size: 14px; text-align: center; }}
            .seccion {{ background: #160311; padding: 10px; margin: 10px 0; border-radius: 5px; min-height: 80px; border: 1px dashed #4a1038; }}
            
            .costalero {{ background: #3d0c2e; border: 1px solid #571342; margin: 5px 0; padding: 8px; border-radius: 4px; cursor: move; display: flex; justify-content: space-between; align-items: center; font-size: 11px; transition: 0.3s; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }}
            .costalero.vacio {{ border: 1px dashed #571342; background: #0c0209; color: #884d72; cursor: default; flex-direction: column; align-items: stretch; text-shadow: none; overflow: visible; position: relative; }}
            .costalero.sobrepeso {{ border: 2px solid #ff4757; background: #6b0b1c; }}
            
            .costalero.dyn-rep-c {{ border: 1px solid #ffd700; box-shadow: inset 0 0 8px rgba(255, 215, 0, 0.2); }}
            .costalero.dyn-rep-cruz {{ border: 1px solid #00d2ff; box-shadow: inset 0 0 8px rgba(0, 210, 255, 0.2); }}
            .costalero.dyn-rep-doble {{ border: 2px solid #ff4757; box-shadow: inset 0 0 10px rgba(255, 71, 87, 0.4); }}
            .costalero.dyn-conflicto {{ border: 2px dashed #ff0000; background: #4a0000; animation: parpadeo 1s infinite; }}
            .dyn-text-conflicto {{ color: #fff; font-weight: bold; font-size: 12px; text-shadow: none; }}

            .modal-overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 1000; justify-content: center; align-items: center; backdrop-filter: blur(3px); }}
            .modal-content {{ background: #1a0514; border: 2px solid #d4af37; padding: 25px; border-radius: 12px; width: 90%; max-width: 600px; position: relative; animation: slideIn 0.3s ease-out; }}
            .modal-close {{ position: absolute; top: 15px; right: 15px; background: none; border: none; color: #ff4757; font-size: 24px; cursor: pointer; transition: 0.2s; }}
            .modal-close:hover {{ transform: scale(1.2); }}
            
            @keyframes parpadeo {{ 50% {{ opacity: 0.5; }} }}
            @keyframes slideIn {{ from {{ transform: translateY(-30px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}

            .btn-control {{ background: #3d0c2e; color: #f8f0f5; border: 1px solid #d4af37; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 12px; margin-left: 5px; text-transform: uppercase; transition: 0.3s; }}
            .btn-control:hover {{ background: #571342; box-shadow: 0 0 8px rgba(212, 175, 55, 0.4); }}
            .btn-export {{ background: #d4af37; color: #000; border-color: #b5952f; }}
            .btn-export:hover {{ background: #b5952f; color:#000; }}
            .btn-load {{ background: #17517e; border-color: #2980b9; }}
            .btn-load:hover {{ background: #1f6b9c; }}
            
            .stats-box {{ background: #0c0209; padding: 8px; border-radius: 4px; font-size: 10px; color: #d4af37; margin-top: 5px; border-left: 3px solid #d4af37; }}
            input.search-p {{ background: #0c0209; border: 1px solid #3d0c2e; color: #d4af37; padding: 5px; width: 100%; font-size: 10px; border-radius: 3px; outline: none; box-sizing: border-box; }}
            input.search-p:focus {{ border-color: #d4af37; }}
            .sugerencias {{ background: #1a0514; border: 1px solid #d4af37; max-height: 100px; overflow-y: auto; position: absolute; z-index: 999; width: 100%; top: 100%; left: 0; box-shadow: 0 4px 6px rgba(0,0,0,0.2); border-radius: 3px; }}
            .sug-item {{ padding: 6px; cursor: pointer; border-bottom: 1px solid #eee; color: #e8d08c; font-size: 11px; text-align: left; }}
            .sug-item:hover {{ background: #3d0c2e; color: #fff; font-weight: bold; }}
            
            /* CSS arreglado para que los textos no rompan la caja */
            textarea.indicaciones-input {{ width: 100%; background: #0c0209; color: #d4af37; border: 1px solid #3d0c2e; border-radius: 5px; padding: 8px; font-family: inherit; margin-bottom: 10px; outline: none; resize: vertical; box-sizing: border-box; font-size:12px; }}
            textarea.indicaciones-input:focus {{ border-color: #d4af37; }}
            .texto-indicaciones {{ font-size: 12px; color: #f8f0f5; white-space: pre-wrap; font-family: inherit; line-height: 1.5; word-wrap: break-word; overflow-wrap: break-word; word-break: break-word; margin:0; }}
        </style>
    </head>
    <body>
        <div class="controles">
            <div>
                <div style="font-size:18px; font-weight:bold; color:#d4af37;">VIERNES SANTO - MOTOR DINÁMICO</div>
                <div style="font-size:11px; color:#a37c95; margin-top: 3px;">Auditor de Censo Activado | ✅ Hombro Correcto</div>
            </div>
            <div>
                <input type="file" id="file-input" accept=".json" style="display: none;" onchange="cargarJSON(event)">
                <button class="btn-control btn-load" onclick="document.getElementById('file-input').click()">📂 CARGAR JSON</button>
                <button id="btn-heatmap" class="btn-control" onclick="toggleHeatmap()">🧊 Mapa Peso: OFF</button>
                <button class="btn-control btn-export" onclick="descargarDatosJSON()">💾 DESCARGAR DATOS</button>
            </div>
        </div>

        <div id="modal-info" class="modal-overlay" onclick="cerrarModal(event)">
            <div class="modal-content" onclick="event.stopPropagation()">
                <button class="modal-close" onclick="cerrarModal()">✖</button>
                <div id="modal-body"></div>
            </div>
        </div>

        <div id="modal-indicaciones" class="modal-overlay" onclick="cerrarModalIndicaciones(event)">
            <div class="modal-content" onclick="event.stopPropagation()" style="max-height: 90vh; overflow-y: auto;">
                <button class="modal-close" onclick="cerrarModalIndicaciones()">✖</button>
                <h3 style="color:#d4af37; margin-top:0; border-bottom:1px solid #3d0c2e; padding-bottom:10px;">📝 Editar Indicaciones y Normativa (Viernes)</h3>
                
                <label style="color:#e8d08c; font-size:13px; font-weight:bold;">⚠️ Tramo 1 (Monserrate ➔ Ayto):</label>
                <textarea id="text-tramo1" class="indicaciones-input" style="height: 55px;" placeholder="Ej: Atención a la salida..."></textarea>
                
                <label style="color:#e8d08c; font-size:13px; font-weight:bold;">⚠️ Tramo 2 (Ayto ➔ As de Oros):</label>
                <textarea id="text-tramo2" class="indicaciones-input" style="height: 55px;" placeholder="Ej: Giro en Plaza Nueva..."></textarea>
                
                <label style="color:#e8d08c; font-size:13px; font-weight:bold;">⚠️ Tramo 3 (As Oros ➔ Glorieta):</label>
                <textarea id="text-tramo3" class="indicaciones-input" style="height: 55px;" placeholder="Ej: Mantener el paso firme..."></textarea>
                
                <label style="color:#e8d08c; font-size:13px; font-weight:bold;">⚠️ Tramo 4 y Regreso:</label>
                <textarea id="text-tramo4" class="indicaciones-input" style="height: 55px;" placeholder="Ej: Relevos en la Gasolinera..."></textarea>
                
                <label style="color:#e8d08c; font-size:13px; font-weight:bold;">📜 Normativa de la Cuadrilla:</label>
                <textarea id="text-normativa" class="indicaciones-input" style="height: 80px;" placeholder="Escribe aquí las normas generales o avisos del Capataz..."></textarea>
                
                <button onclick="guardarIndicaciones()" style="width:100%; background:#d4af37; color:#000; font-weight:bold; font-size: 14px; padding:12px; border:none; border-radius:5px; cursor:pointer; margin-top:5px; text-transform: uppercase;">💾 Guardar Notas en el Cuadrante</button>
            </div>
        </div>

        <div id="panel-alertas" class="alerta-box">
            ⚠️ ¡ALERTA CRÍTICA! Imposibilidad física detectada:
            <ul id="lista-alertas"></ul>
        </div>
        
        <div class="buscador-box">
            <h3 style="margin-top:0; color:#d4af37;">🔍 BUSCADOR EN TIEMPO REAL</h3>
            <p style="font-size:12px; color:#a37c95; margin-top:-10px;">Busca el itinerario de alguien escribiendo, o pulsa el icono ℹ️ al lado de su nombre abajo.</p>
            <input type="text" id="input-buscador" placeholder="Escribe el nombre de un costalero/a..." onkeyup="actualizarBuscador()">
            <div id="resultado-itinerario" class="itinerario-result"></div>
        </div>
        
        <div style="margin-top:10px; padding:15px; border:1px dashed #3d0c2e; font-size:13px; background:#160311;">
            <b style="color:#e8d08c;">LEYENDA AUTOMÁTICA:</b><br><br>
            <span style="color:#ffd700; margin-right:20px; font-weight:bold;">■ Amarillo: Repite Cristo (Turno B + C)</span>
            <span style="color:#00d2ff; margin-right:20px; font-weight:bold;">■ Azul: Carga Alterna (Trono y Cruz)</span>
            <span style="color:#ff4757; margin-right:20px; font-weight:bold;">■ Rojo: Sobreesfuerzo (Carga Seguido)</span>
            <span style="color:#ffffff; background:#b30000; padding:2px 5px; font-weight:bold; border:1px dashed white;">■ ROJO PARPADEANTE: Imposible / Baja Censo / No Sale</span>
        </div>

        <div id="app"></div>
        
        <div id="indicaciones-container"></div>

        <script>
            const TS_PYTHON = "{marca_tiempo}";
            const DATOS_INICIALES = {turnos_json};
            const MASTER_LIST = {master_json};
            const CENSO_COMPLETO = {censo_completo}; 
            const DIA_PROCESION = 'viernes_santo';
            
            const PESO_TRONO = {peso_trono};
            const PESO_CRUZ = {peso_cruz};
            const MAX_KG = {limite_peso};
            
            let datos = {{}};
            let estadoGlobal = {{}};
            let heatmapActivo = false;
            
            const TRAMOS = {{
                "Trono": {{ "Turno A": [1, 3, 5, 7], "Turno B": [2, 6], "Turno C": [4, 6] }},
                "Cruz": {{ "Turno 1": [1], "Turno 2": [2], "Turno 3": [3], "Turno 4": [4] }}
            }};

            function init() {{
                let savedTs = localStorage.getItem('viernes_santo_ts');
                let savedDatos = localStorage.getItem('viernes_santo_datos');
                if (savedDatos && savedTs === TS_PYTHON) {{
                    datos = JSON.parse(savedDatos);
                }} else {{
                    datos = JSON.parse(JSON.stringify(DATOS_INICIALES));
                    localStorage.setItem('viernes_santo_ts', TS_PYTHON);
                    localStorage.setItem('viernes_santo_datos', JSON.stringify(datos));
                }}
                
                datos.tipo_procesion = "viernes_santo";
                if(!datos.indicaciones) {{
                    datos.indicaciones = {{ tramo1: "", tramo2: "", tramo3: "", tramo4: "", normativa: "" }};
                }}
                
                render();
            }}

            function guardarMemoria() {{
                datos.tipo_procesion = "viernes_santo";
                localStorage.setItem('viernes_santo_datos', JSON.stringify(datos));
            }}

            function descargarDatosJSON() {{
                datos.tipo_procesion = "viernes_santo";
                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(datos, null, 2));
                const dlAnchorElem = document.createElement('a');
                dlAnchorElem.setAttribute("href", dataStr);
                dlAnchorElem.setAttribute("download", "Distribucion_Viernes_Definitiva.json");
                document.body.appendChild(dlAnchorElem);
                dlAnchorElem.click();
                dlAnchorElem.remove();
            }}

            function cargarJSON(event) {{
                const file = event.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = function(e) {{
                    try {{
                        const loadedData = JSON.parse(e.target.result);
                        
                        // BLOQUEO ANTIDESPISTES: Detecta si es de otro día
                        if (loadedData.tipo_procesion && loadedData.tipo_procesion !== "viernes_santo") {{
                            alert("❌ ERROR: Este archivo pertenece a otra procesión. No puedes cargarlo en la vista del Viernes Santo.");
                            event.target.value = '';
                            return;
                        }} else if (!loadedData.tipo_procesion && loadedData.Trono && !loadedData.Trono["Turno C"]) {{
                            alert("❌ ERROR: Este archivo parece pertenecer al Miércoles Santo. No puedes cargarlo en la vista del Viernes Santo.");
                            event.target.value = '';
                            return;
                        }}

                        if(loadedData.Trono && loadedData.Cruz) {{
                            let msgBorrados = [];
                            let msgNoSalen = [];

                            // AUDITORÍA DEL CENSO
                            for (let tipo of ["Trono", "Cruz"]) {{
                                if (!loadedData[tipo]) continue;
                                for (let t of Object.keys(loadedData[tipo])) {{
                                    for (let v of Object.keys(loadedData[tipo][t])) {{
                                        for (let sec of ["Delante", "Detras"]) {{
                                            for (let i = 0; i < loadedData[tipo][t][v][sec].length; i++) {{
                                                let p = loadedData[tipo][t][v][sec][i];
                                                if (p.id && p.id !== -1) {{
                                                    let personaCenso = CENSO_COMPLETO.find(c => c.id === p.id);
                                                    if (!personaCenso) {{
                                                        msgBorrados.push(`- ${{p.nombre}}`);
                                                        loadedData[tipo][t][v][sec][i] = {{ "nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1 }};
                                                    }} else {{
                                                        p.altura = personaCenso.altura;
                                                        p.pref_hombro = personaCenso.pref_hombro;
                                                        if (!personaCenso[DIA_PROCESION]) {{
                                                            msgNoSalen.push(`- ${{p.nombre}}`);
                                                        }}
                                                    }}
                                                }}
                                            }}
                                        }}
                                    }}
                                }}
                            }}

                            let alertaFinal = "";
                            if (msgBorrados.length > 0) {{
                                alertaFinal += "⚠️ EL CENSO SE HA MODIFICADO:\\nLas siguientes personas ya no aparecen en la base de datos oficial y sus huecos han sido liberados automáticamente:\\n" + msgBorrados.join("\\n") + "\\n\\n";
                            }}
                            if (msgNoSalen.length > 0) {{
                                alertaFinal += "⚠️ PERSONAS QUE NO SALEN HOY:\\n(Aparecerán parpadeando en ROJO en el cuadrante)\\n" + msgNoSalen.join("\\n") + "\\n\\n";
                            }}

                            if (alertaFinal !== "") {{
                                alert(alertaFinal);
                            }} else {{
                                alert("✅ Configuración cargada correctamente. Todo el personal está al día en el censo.");
                            }}

                            datos = loadedData;
                            datos.tipo_procesion = "viernes_santo";
                            if(!datos.indicaciones) datos.indicaciones = {{ tramo1: "", tramo2: "", tramo3: "", tramo4: "", normativa: "" }};
                            
                            guardarMemoria();
                            render();
                        }} else {{
                            alert("❌ Archivo JSON inválido.");
                        }}
                    }} catch (error) {{
                        alert("❌ Error al leer el archivo JSON.");
                    }}
                    event.target.value = '';
                }};
                reader.readAsText(file);
            }}

            function analizarEstado() {{
                let stats = {{}};
                let alertasCriticas = [];

                for (let tipo of ["Trono", "Cruz"]) {{
                    if (!datos[tipo]) continue;
                    for (let t of Object.keys(datos[tipo])) {{
                        for (let v of Object.keys(datos[tipo][t])) {{
                            for (let sec of ["Delante", "Detras"]) {{
                                datos[tipo][t][v][sec].forEach(p => {{
                                    if (p.id && p.id !== -1) {{
                                        if (!stats[p.id]) stats[p.id] = {{ nombre: p.nombre, cristo: [], cruz: [] }};
                                        if (tipo === "Trono") stats[p.id].cristo.push(t);
                                        if (tipo === "Cruz") stats[p.id].cruz.push(t);
                                    }}
                                }});
                            }}
                        }}
                    }}
                }}

                for (let id in stats) {{
                    let s = stats[id];
                    s.estadoStr = "normal";
                    
                    let cristoArr = [];
                    s.cristo.forEach(t => cristoArr.push(...(TRAMOS.Trono[t] || [])));
                    let cristoUniq = [...new Set(cristoArr)]; 
                    
                    let cruzArr = [];
                    s.cruz.forEach(t => cruzArr.push(...(TRAMOS.Cruz[t] || [])));
                    let cruzUniq = [...new Set(cruzArr)];
                    
                    let allTramos = [...new Set([...cristoUniq, ...cruzUniq])].sort((a,b) => a - b);
                    s.tramos = allTramos; 

                    let tieneConflicto = false;
                    let tieneDoble = false;

                    let cristoTurnosUnicos = [...new Set(s.cristo)];
                    
                    if (s.cristo.length > cristoTurnosUnicos.length || s.cruz.length > [...new Set(s.cruz)].length) {{
                        tieneConflicto = true;
                        alertasCriticas.push(`<b>${{s.nombre}}</b> duplicado en un mismo turno.`);
                    }}

                    let interseccion = cristoUniq.filter(t => cruzUniq.includes(t));
                    if (interseccion.length > 0) {{
                        tieneConflicto = true;
                        alertasCriticas.push(`<b>${{s.nombre}}</b> en Trono y Cruz a la vez (Tramo ${{interseccion.join(', ')}}).`);
                    }}

                    for (let i = 0; i < allTramos.length - 1; i++) {{
                        if (allTramos[i+1] - allTramos[i] === 1) tieneDoble = true;
                    }}
                    if (allTramos.filter(t => t <= 4).length > 2) tieneDoble = true;

                    let personaCenso = CENSO_COMPLETO.find(c => c.id == id);
                    if (!personaCenso) {{
                        s.estadoStr = "baja_censo";
                    }} else if (!personaCenso[DIA_PROCESION]) {{
                        s.estadoStr = "no_procesiona";
                    }} else if (tieneConflicto) {{
                        s.estadoStr = "conflicto";
                    }} else if (cruzUniq.length > 0 && cristoUniq.length > 0) {{
                        s.estadoStr = tieneDoble ? "doble" : "repCruz"; 
                    }} else if (cristoTurnosUnicos.length >= 2) {{
                        s.estadoStr = tieneDoble ? "doble" : "repC";
                    }}
                }}
                estadoGlobal = stats;

                let panel = document.getElementById("panel-alertas");
                let lista = document.getElementById("lista-alertas");
                if (alertasCriticas.length > 0) {{
                    lista.innerHTML = alertasCriticas.map(e => `<li>- ${{e}}</li>`).join("");
                    panel.style.display = "block";
                }} else {{
                    panel.style.display = "none";
                }}
            }}

            // ==========================================
            // LÓGICA DE NOTAS E INDICACIONES (4 TRAMOS)
            // ==========================================
            function abrirModalIndicaciones() {{
                if(!datos.indicaciones) datos.indicaciones = {{ tramo1: "", tramo2: "", tramo3: "", tramo4: "", normativa: "" }};
                document.getElementById('text-tramo1').value = datos.indicaciones.tramo1 || "";
                document.getElementById('text-tramo2').value = datos.indicaciones.tramo2 || "";
                document.getElementById('text-tramo3').value = datos.indicaciones.tramo3 || "";
                document.getElementById('text-tramo4').value = datos.indicaciones.tramo4 || "";
                document.getElementById('text-normativa').value = datos.indicaciones.normativa || "";
                document.getElementById('modal-indicaciones').style.display = 'flex';
            }}

            function cerrarModalIndicaciones(ev) {{
                if (!ev || ev.target.id === 'modal-indicaciones' || ev.target.className === 'modal-close') {{
                    document.getElementById('modal-indicaciones').style.display = 'none';
                }}
            }}

            function guardarIndicaciones() {{
                if(!datos.indicaciones) datos.indicaciones = {{}};
                datos.indicaciones.tramo1 = document.getElementById('text-tramo1').value;
                datos.indicaciones.tramo2 = document.getElementById('text-tramo2').value;
                datos.indicaciones.tramo3 = document.getElementById('text-tramo3').value;
                datos.indicaciones.tramo4 = document.getElementById('text-tramo4').value;
                datos.indicaciones.normativa = document.getElementById('text-normativa').value;
                
                guardarMemoria();
                renderIndicaciones(); 
                cerrarModalIndicaciones();
            }}

            function renderIndicaciones() {{
                if(!datos.indicaciones) datos.indicaciones = {{ tramo1: "", tramo2: "", tramo3: "", tramo4: "", normativa: "" }};
                
                let container = document.getElementById('indicaciones-container');
                container.innerHTML = `
                    <div class="turno-container" style="margin-top: 40px; border-color: #5c164e; box-shadow: 0 0 15px rgba(92, 22, 78, 0.15);">
                        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid #3d0c2e; padding-bottom: 10px; margin-bottom: 15px;">
                            <h2 style="margin:0; border:none; padding:0; color:#d4af37; text-transform: uppercase; letter-spacing: 2px;">📝 INDICACIONES Y NORMATIVA</h2>
                            <button class="btn-control" onclick="abrirModalIndicaciones()" style="background:#5c164e; border-color:#d4af37; color:#fff;">✏️ EDITAR TEXTOS</button>
                        </div>
                        
                        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                            <div style="background:#160311; padding:12px; border-radius:8px; border-left:4px solid #d4af37;">
                                <h4 style="color:#e8d08c; margin-top:0; font-size:13px;">⚠️ T1: Monserrate ➔ Ayto</h4>
                                <p class="texto-indicaciones">${{datos.indicaciones.tramo1 || "<i style='color:#a37c95;'>(Sin indicaciones)</i>"}}</p>
                            </div>
                            <div style="background:#160311; padding:12px; border-radius:8px; border-left:4px solid #d4af37;">
                                <h4 style="color:#e8d08c; margin-top:0; font-size:13px;">⚠️ T2: Ayto ➔ As de Oros</h4>
                                <p class="texto-indicaciones">${{datos.indicaciones.tramo2 || "<i style='color:#a37c95;'>(Sin indicaciones)</i>"}}</p>
                            </div>
                            <div style="background:#160311; padding:12px; border-radius:8px; border-left:4px solid #d4af37;">
                                <h4 style="color:#e8d08c; margin-top:0; font-size:13px;">⚠️ T3: As Oros ➔ Glorieta</h4>
                                <p class="texto-indicaciones">${{datos.indicaciones.tramo3 || "<i style='color:#a37c95;'>(Sin indicaciones)</i>"}}</p>
                            </div>
                            <div style="background:#160311; padding:12px; border-radius:8px; border-left:4px solid #d4af37;">
                                <h4 style="color:#e8d08c; margin-top:0; font-size:13px;">⚠️ T4 y Regreso</h4>
                                <p class="texto-indicaciones">${{datos.indicaciones.tramo4 || "<i style='color:#a37c95;'>(Sin indicaciones)</i>"}}</p>
                            </div>
                        </div>
                        
                        <div style="background:#160311; padding:15px; border-radius:8px; border-left:4px solid #5c164e; margin-top:15px;">
                            <h4 style="color:#e8d08c; margin-top:0;">📜 Normativa de la Cuadrilla</h4>
                            <p class="texto-indicaciones">${{datos.indicaciones.normativa || "<i style='color:#a37c95;'>(Sin normativa especificada)</i>"}}</p>
                        </div>
                    </div>
                `;
            }}

            // Resto de la lógica
            function abrirInfoModal(id) {{
                let st = estadoGlobal[id];
                if (!st) return;
                let tOcupados = st.tramos;
                let html = `<h4 style="color:#d4af37; margin-top:0; margin-bottom:15px; font-size:18px;">📋 Hoja de Ruta: ${{st.nombre.replace(" (R)","").replace(" (C)","").replace(" (C-Doble)","")}}</h4>`;
                html += `<div class="bloque-ruta"><h5>🌟 PROCESIÓN</h5><ul>`;
                [
                    {{ num: 1, txt: "1. Monserrate ➔ Ayto" }},
                    {{ num: 2, txt: "2. Ayto ➔ As de Oros" }},
                    {{ num: 3, txt: "3. As Oros ➔ Glorieta" }},
                    {{ num: 4, txt: "4. Glorieta ➔ Turismo" }}
                ].forEach(tr => {{ html += generarFilaTramo(tr, st, tOcupados); }});
                html += `</ul></div>`;
                
                html += `<div class="bloque-ruta"><h5>🏠 REGRESO (Solo Trono)</h5><ul>`;
                [
                    {{ num: 5, txt: "5. Turismo ➔ Santiago" }},
                    {{ num: 6, txt: "6. Santiago ➔ Gasolinera" }},
                    {{ num: 7, txt: "7. Gasolinera ➔ San Fco" }}
                ].forEach(tr => {{ html += generarFilaTramo(tr, st, tOcupados); }});
                html += `</ul></div>`;
                document.getElementById('modal-body').innerHTML = html;
                document.getElementById('modal-info').style.display = 'flex';
            }}

            function cerrarModal(ev) {{
                if (!ev || ev.target.id === 'modal-info' || ev.target.className === 'modal-close') {{
                    document.getElementById('modal-info').style.display = 'none';
                }}
            }}

            function actualizarBuscador() {{
                const val = document.getElementById('input-buscador').value.toLowerCase();
                const resDiv = document.getElementById('resultado-itinerario');
                if (val.length < 3) {{ resDiv.style.display = 'none'; return; }}

                let idFound = null;
                for (let id in estadoGlobal) {{
                    if (estadoGlobal[id].nombre.toLowerCase().includes(val)) {{ idFound = id; break; }}
                }}

                if (idFound) {{
                    let st = estadoGlobal[idFound];
                    let tOcupados = st.tramos;
                    resDiv.style.display = 'block';
                    let html = `<h4 style="color:#d4af37; margin-bottom:10px; font-size:16px;">📋 Hoja de Ruta Viva: ${{st.nombre.replace(" (R)","").replace(" (C)","").replace(" (C-Doble)","")}}</h4>`;
                    html += `<div class="bloque-ruta"><h5>🌟 PROCESIÓN</h5><ul>`;
                    [
                        {{ num: 1, txt: "1. Monserrate ➔ Ayto" }},
                        {{ num: 2, txt: "2. Ayto ➔ As de Oros" }},
                        {{ num: 3, txt: "3. As Oros ➔ Glorieta" }},
                        {{ num: 4, txt: "4. Glorieta ➔ Turismo" }}
                    ].forEach(tr => {{ html += generarFilaTramo(tr, st, tOcupados); }});
                    html += `</ul></div>`;
                    html += `<div class="bloque-ruta"><h5>🏠 REGRESO (SOLO TRONO)</h5><ul>`;
                    [
                        {{ num: 5, txt: "5. Turismo ➔ Santiago" }},
                        {{ num: 6, txt: "6. Santiago ➔ Gasolinera" }},
                        {{ num: 7, txt: "7. Gasolinera ➔ San Fco" }}
                    ].forEach(tr => {{ html += generarFilaTramo(tr, st, tOcupados); }});
                    html += `</ul></div>`;
                    resDiv.innerHTML = html;
                }} else {{
                    resDiv.style.display = 'none';
                }}
            }}

            function generarFilaTramo(tr, st, tOcupados) {{
                let label = "🕯️ <strong style='color:#884d72'>Cirio (Descanso)</strong>";
                let enCristo = [];
                st.cristo.forEach(t => {{ if((TRAMOS.Trono[t]||[]).includes(tr.num)) enCristo.push(t); }});
                let enCruz = [];
                st.cruz.forEach(t => {{ if((TRAMOS.Cruz[t]||[]).includes(tr.num)) enCruz.push(t); }});

                if (enCristo.length > 0 && enCruz.length > 0) {{
                    label = `💥 <strong style='color:#ff0000; animation: parpadeo 1s infinite;'>¡IMPOSIBLE! (${{enCristo.join('+')}} y ${{enCruz.join('+')}})</strong>`;
                }} else if (enCristo.length > 0) {{
                    label = `💪 <strong style='color:#e8d08c'>🕍 Trono (${{enCristo.join(" + ")}})</strong>`;
                }} else if (enCruz.length > 0) {{
                    let sinDescanso = tOcupados.includes(tr.num - 1) || tOcupados.includes(tr.num + 1);
                    let sobrecarga = tOcupados.filter(t => t <= 4).length > 2;
                    if (sinDescanso || sobrecarga) {{ label = `⚠️ <strong style='color:#ff4757'>✝️ Cruz (${{enCruz.join('+')}}) [SOBREESFUERZO]</strong>`; }} 
                    else {{ label = `💪 <strong style='color:#00d2ff'>✝️ Cruz (${{enCruz.join('+')}})</strong>`; }}
                }}
                return `<li><span class="tramo-label">${{tr.txt}}</span> ${{label}}</li>`;
            }}

            function toggleHeatmap() {{
                heatmapActivo = !heatmapActivo;
                const btn = document.getElementById('btn-heatmap');
                btn.innerText = heatmapActivo ? '🔥 Mapa Peso: ON' : '🧊 Mapa Peso: OFF';
                if (heatmapActivo) {{ btn.style.background = '#d4af37'; btn.style.color = '#0c0209'; }} 
                else {{ btn.style.background = '#3d0c2e'; btn.style.color = '#f8f0f5'; }}
                render();
            }}

            function getHeatmapColor(peso, tipo) {{
                if (!peso || peso === 0) return '';
                const base = tipo === 'Trono' ? PESO_TRONO / 36 : PESO_CRUZ / 8;
                const minVal = base - 10;
                let p = (peso - minVal) / (MAX_KG - minVal);
                p = Math.max(0, Math.min(1, p));
                return `hsl(${{(1 - p) * 120}}, 80%, 30%)`;
            }}

            function render() {{
                analizarEstado(); 
                actualizarBuscador(); 
                
                const app = document.getElementById('app');
                app.innerHTML = '';
                
                for (const [tipo, turnos] of Object.entries(datos)) {{
                    if(tipo === "indicaciones" || tipo === "tipo_procesion") continue; 
                    
                    let tituloBloque = tipo === "Trono" ? "🕍 TRONO PRINCIPAL" : "✝️ LA CRUZ (4 Turnos)";
                    app.innerHTML += `<h1 style="color:#d4af37; border-bottom: 2px solid #d4af37; padding-bottom:10px; margin-top:40px;">${{tituloBloque}}</h1>`;
                    
                    for (const [idT, varas] of Object.entries(turnos)) {{
                        let gridClass = tipo === "Cruz" ? "grid-cruz" : "grid-trono";
                        let html = `<div class="turno-container"><h2>${{idT}}</h2><div class="${{gridClass}}">`;
                        
                        for (const [vNom, vData] of Object.entries(varas)) {{
                            const statsVara = calcularStats(vData.Delante.concat(vData.Detras), tipo);
                            html += `<div class="vara"><h3>VARA ${{vNom.toUpperCase()}}</h3>`;
                            
                            ["Delante", "Detras"].forEach(sec => {{
                                const statsSec = calcularStats(vData[sec], tipo);
                                if (sec === "Delante") html += `<div class="stats-box"><b>${{sec.toUpperCase()}}:</b> ${{statsSec.media.toFixed(1)}}cm | ${{statsSec.totalVara.toFixed(1)}}kg</div>`;
                                if (sec === "Detras") html += `<div style="text-align:center; padding-top:10px; margin-bottom:5px; color:#e8d08c; font-size:12px; font-weight:bold; letter-spacing:2px; border-top:1px dashed #3d0c2e;">${{tipo === "Trono" ? "▼ TRONO ▼" : "▼ CRUZ ▼"}}</div>`;
                                
                                html += `<div class="seccion" ondragover="allow(event)">`;
                                vData[sec].forEach((p, i) => {{
                                    const esVacio = p.altura === 0;
                                    const esSobrepeso = p.peso >= MAX_KG;
                                    
                                    let clExtra = ''; let nExtra = ''; let tagFinal = ''; let tickHombro = '';

                                    if (!esVacio) {{
                                        let pref = (p.pref_hombro || "").toLowerCase().trim();
                                        if (pref !== "") {{
                                            if (pref.includes("derech")) {{
                                                if (vNom === "Izquierda") tickHombro = ' <span title="Hombro correcto" style="font-size:12px;">✅</span>';
                                                else tickHombro = ' <span title="Hombro INCORRECTO" style="font-size:12px;">❌</span>';
                                            }} else if (pref.includes("izquierd")) {{
                                                if (vNom === "Derecha") tickHombro = ' <span title="Hombro correcto" style="font-size:12px;">✅</span>';
                                                else tickHombro = ' <span title="Hombro INCORRECTO" style="font-size:12px;">❌</span>';
                                            }} else if (pref.includes("ambos")) {{
                                                tickHombro = ' <span title="Hombro correcto" style="font-size:12px;">✅</span>';
                                            }}
                                        }}

                                        if (estadoGlobal[p.id]) {{
                                            let est = estadoGlobal[p.id].estadoStr;
                                            if (est === "baja_censo") {{ clExtra = 'dyn-conflicto'; nExtra = 'dyn-text-conflicto'; tagFinal = ' [BAJA]'; }} 
                                            else if (est === "no_procesiona") {{ clExtra = 'dyn-conflicto'; nExtra = 'dyn-text-conflicto'; tagFinal = ' [NO SALE]'; }} 
                                            else if (est === "conflicto") {{ clExtra = 'dyn-conflicto'; nExtra = 'dyn-text-conflicto'; tagFinal = ' [CRÍTICO]'; }} 
                                            else if (est === "doble") {{ clExtra = 'dyn-rep-doble'; nExtra = 'dyn-text-doble'; tagFinal = ' (Sobrecarga)'; }} 
                                            else if (est === "repCruz") {{ clExtra = 'dyn-rep-cruz'; nExtra = 'dyn-text-cruz'; tagFinal = ' (Cruz)'; }} 
                                            else if (est === "repC") {{ clExtra = 'dyn-rep-c'; nExtra = 'dyn-text-c'; tagFinal = ' (Doble)'; }}
                                        }}
                                    }}
                                    
                                    let bgStyle = (heatmapActivo && !esVacio) ? `background-color: ${{getHeatmapColor(p.peso, tipo)}} !important; border-color: transparent;` : '';

                                    html += `
                                        <div class="costalero ${{esVacio ? 'vacio' : ''}} ${{esSobrepeso && !heatmapActivo ? 'sobrepeso' : ''}} ${{clExtra}}" 
                                             style="${{bgStyle}}" title="Hombro: ${{p.pref_hombro || 'Indiferente'}}"
                                             draggable="${{!esVacio}}" ondragstart="drag(event, '${{tipo}}', '${{idT}}', '${{vNom}}', '${{sec}}', ${{i}})" ondrop="drop(event, '${{tipo}}', '${{idT}}', '${{vNom}}', '${{sec}}', ${{i}})">
                                            ${{esVacio ? 
                                                `<input type="text" class="search-p" placeholder="Escribir nombre..." onkeyup="buscarMini(event, '${{tipo}}','${{idT}}','${{vNom}}','${{sec}}',${{i}})">
                                                 <div id="sug-${{tipo}}-${{idT}}-${{vNom}}-${{sec}}-${{i}}" class="sugerencias" style="display:none"></div>` :
                                                `<span>
                                                    <button style="background:none; border:none; color:#00d2ff; cursor:pointer; padding:0 5px 0 0; font-size:14px;" onclick="abrirInfoModal(${{p.id}}); event.stopPropagation();">ℹ️</button>
                                                    <button style="background:none; border:none; color:#ff4757; cursor:pointer; padding:0 5px 0 0;" onclick="eliminar('${{tipo}}','${{idT}}','${{vNom}}','${{sec}}',${{i}})">🗑️</button>
                                                    <span class="${{nExtra}}">${{p.nombre}} ${{tickHombro}} ${{tagFinal}}</span>
                                                </span>
                                                <span><span style="color:${{heatmapActivo?'#fff':'#d4af37'}}">${{p.altura}}cm</span> <b style="color:${{heatmapActivo?'#fff':'#e8d08c'}}; margin-left:5px">${{p.peso.toFixed(1)}}kg</b></span>`
                                            }}
                                        </div>`;
                                }});
                                html += `</div>`;
                                if (sec === "Detras") html += `<div class="stats-box"><b>${{sec.toUpperCase()}}:</b> ${{statsSec.media.toFixed(1)}}cm | ${{statsSec.totalVara.toFixed(1)}}kg</div>`;
                            }});
                            html += `<div style="text-align:center; padding:10px; border:1px solid #d4af37; border-radius:5px; font-size:12px; color:#d4af37; margin-top:10px;"><b>TOTAL VARA: ${{statsVara.totalVara.toFixed(1)}} kg</b></div></div>`;
                        }}
                        app.innerHTML += html + `</div></div>`;
                    }}
                }}
                
                renderIndicaciones();
            }}

            function calcularStats(p_list, tipo) {{
                let filtrados = p_list.filter(p => p.altura > 0);
                let m = filtrados.length > 0 ? filtrados.reduce((a, b) => a + b.altura, 0) / filtrados.length : 0;
                let tV = 0; let base = tipo === 'Trono' ? PESO_TRONO / 36 : PESO_CRUZ / 8;
                p_list.forEach(p => {{
                    if(p.altura > 0) {{ p.peso = Math.min(MAX_KG, Math.max(0, base + ((p.altura - m) * (base * 0.05)))); tV += p.peso;
                    }} else p.peso = 0;
                }});
                return {{ media: m, totalVara: tV }};
            }}

            function buscarMini(ev, tipo, t, v, s, i) {{
                const val = ev.target.value.toLowerCase();
                const sugDiv = document.getElementById(`sug-${{tipo}}-${{t}}-${{v}}-${{s}}-${{i}}`);
                if(val.length < 2) {{ sugDiv.style.display = 'none'; return; }}
                const matches = MASTER_LIST.filter(p => p.nombre.toLowerCase().includes(val)).slice(0, 5);
                sugDiv.innerHTML = '';
                if(matches.length > 0) {{
                    sugDiv.style.display = 'block';
                    matches.forEach(m => {{
                        const div = document.createElement('div');
                        div.className = 'sug-item';
                        div.innerHTML = `${{m.nombre}} (${{m.altura}}cm)`;
                        div.onclick = () => {{ datos[tipo][t][v][s][i] = {{...m}}; render(); guardarMemoria(); }};
                        sugDiv.appendChild(div);
                    }});
                }} else sugDiv.style.display = 'none';
            }}

            let dragging = null;
            function allow(ev) {{ ev.preventDefault(); }}
            function drag(ev, tipo, t, v, s, i) {{ dragging = {{ tipo, t, v, s, i }}; }}
            function drop(ev, tipo, t, v, s, i) {{
                ev.preventDefault();
                let orig = datos[dragging.tipo][dragging.t][dragging.v][dragging.s][dragging.i];
                datos[dragging.tipo][dragging.t][dragging.v][dragging.s][dragging.i] = datos[tipo][t][v][s][i];
                datos[tipo][t][v][s][i] = orig;
                render(); guardarMemoria(); 
            }}
            function eliminar(tipo, t, v, s, i) {{
                if (confirm(`¿Quitar a esta persona?`)) {{
                    datos[tipo][t][v][s][i] = {{"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1}};
                    render(); guardarMemoria(); 
                }}
            }}
            window.onload = init; 
        </script>
    </body>
    </html>
    """
    with open("visualizador_viernes.html", "w", encoding="utf-8") as f: 
        f.write(html)