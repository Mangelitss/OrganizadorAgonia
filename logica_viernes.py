import json
import math

def cargar_datos_viernes(archivo='datos.json'):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            return [d for d in datos if d.get('viernes_santo', False)]
    except Exception as e:
        print(f"Error cargando {archivo}: {e}")
        return []

def generar_cuadrillas_viernes(costaleros):
    pool = sorted(costaleros, key=lambda x: x['altura'], reverse=True)
    
    # 1. TURNO A (Élite) -> No repiten
    turno_a = pool[:36]
    for p in turno_a: p['puede_repetir'] = False
    while len(turno_a) < 36: turno_a.append({"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})
    
    # 2. TURNO B 
    turno_b = pool[36:72]
    for p in turno_b: p['puede_repetir'] = True
    while len(turno_b) < 36: turno_b.append({"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})
    
    # 3. TURNO C (Completado con B)
    turno_c = pool[72:108]
    for p in turno_c: p['puede_repetir'] = True
    
    if len(turno_c) < 36:
        repetidores_b = [p for p in turno_b if p['altura'] > 0]
        repetidores_b.sort(key=lambda x: x['altura']) # De menor a mayor
        
        idx_rep = 0
        while len(turno_c) < 36:
            if idx_rep < len(repetidores_b):
                p_rep = repetidores_b[idx_rep].copy()
                p_rep["nombre"] += " (R)"
                turno_c.append(p_rep)
                idx_rep += 1
            else:
                turno_c.append({"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})
                
    # 4. LA CRUZ (4 Turnos x 8 Plazas = 32)
    cruz_turnos = [[], [], [], []]
    
    # Obtenemos los únicos del B y C para que no se dupliquen repetidores
    b_c_list = [p for p in turno_b if p['altura'] > 0] + [p for p in turno_c if p['altura'] > 0 and not p.get('nombre', '').endswith('(R)')]
    uniques = {p['id']: p for p in b_c_list}
    disponibles_cruz = list(uniques.values())
    disponibles_cruz.sort(key=lambda x: x['altura'], reverse=True)

    def puede_coger_cruz(persona, cruz_tramo):
        tramos_cristo = []
        if any(x['id'] == persona['id'] for x in turno_b if x['altura'] > 0): tramos_cristo.extend([2, 6])
        if any(x['id'] == persona['id'] for x in turno_c if x['altura'] > 0): tramos_cristo.extend([4, 6])
        for tc in tramos_cristo:
            if abs(tc - cruz_tramo) <= 1: return False # Regla estricta: Tramo adyacente bloqueado
        return True

    # PASADA 1: Asignación Estricta (Protegiendo el descanso)
    for i in range(4):
        cruz_tramo = i + 1
        for p in disponibles_cruz:
            if len(cruz_turnos[i]) >= 8: break
            ya_en_cruz = any(any(x.get('id') == p['id'] for x in turno) for turno in cruz_turnos)
            
            if not ya_en_cruz and puede_coger_cruz(p, cruz_tramo):
                p_rep = p.copy()
                p_rep["nombre"] += " (C)"
                cruz_turnos[i].append(p_rep)

    # PASADA 2: Protocolo de Emergencia (Si un turno queda vacío, ignoramos el descanso)
    for i in range(4):
        if len(cruz_turnos[i]) < 8:
            for p in disponibles_cruz:
                if len(cruz_turnos[i]) >= 8: break
                ya_en_cruz = any(any(x.get('id') == p['id'] for x in turno) for turno in cruz_turnos)
                
                if not ya_en_cruz:
                    p_rep = p.copy()
                    p_rep["nombre"] += " (C-Doble)" # Etiqueta de Doble Carga sin descanso
                    cruz_turnos[i].append(p_rep)

    # Rellenar con huecos libres si aún así falta gente
    for i in range(4):
        while len(cruz_turnos[i]) < 8:
            cruz_turnos[i].append({"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})

    # ==========================================
    # 5. GENERADOR DE ITINERARIOS PARA BUSCADOR
    # ==========================================
    itinerarios = {}
    for p in costaleros:
        if p['altura'] == 0: continue
        name = p['nombre']
        
        in_a = any(x['id'] == p['id'] for x in turno_a if x['altura'] > 0)
        in_b = any(x['id'] == p['id'] for x in turno_b if x['altura'] > 0)
        in_c = any(x['id'] == p['id'] for x in turno_c if x['altura'] > 0)
        in_c1 = any(x['id'] == p['id'] for x in cruz_turnos[0] if x['altura'] > 0)
        in_c2 = any(x['id'] == p['id'] for x in cruz_turnos[1] if x['altura'] > 0)
        in_c3 = any(x['id'] == p['id'] for x in cruz_turnos[2] if x['altura'] > 0)
        in_c4 = any(x['id'] == p['id'] for x in cruz_turnos[3] if x['altura'] > 0)

        # Detectar si en la cruz hace doblete para avisarlo
        txt_c1 = "✝️ Cruz (T1)" + (" ⚠️ SIN DESCANSO" if any(x['id'] == p['id'] and "Doble" in x['nombre'] for x in cruz_turnos[0]) else "")
        txt_c2 = "✝️ Cruz (T2)" + (" ⚠️ SIN DESCANSO" if any(x['id'] == p['id'] and "Doble" in x['nombre'] for x in cruz_turnos[1]) else "")
        txt_c3 = "✝️ Cruz (T3)" + (" ⚠️ SIN DESCANSO" if any(x['id'] == p['id'] and "Doble" in x['nombre'] for x in cruz_turnos[2]) else "")
        txt_c4 = "✝️ Cruz (T4)" + (" ⚠️ SIN DESCANSO" if any(x['id'] == p['id'] and "Doble" in x['nombre'] for x in cruz_turnos[3]) else "")

        itinerarios[name] = [
            {"tramo": "1. Monserrate ➔ Ayto", "est": "🕍 Cristo (Turno A)" if in_a else (txt_c1 if in_c1 else "🕯️ Cirio")},
            {"tramo": "2. Ayto ➔ As de Oros", "est": "🕍 Cristo (Turno B)" if in_b else (txt_c2 if in_c2 else "🕯️ Cirio")},
            {"tramo": "3. As Oros ➔ Glorieta", "est": "🕍 Cristo (Turno A)" if in_a else (txt_c3 if in_c3 else "🕯️ Cirio")},
            {"tramo": "4. Glorieta ➔ Turismo", "est": "🕍 Cristo (Turno C)" if in_c else (txt_c4 if in_c4 else "🕯️ Cirio")},
            {"tramo": "5. Turismo ➔ Santiago", "est": "🕍 Cristo (Turno A)" if in_a else "🕯️ Cirio"},
            {"tramo": "6. Santiago ➔ Gasolinera", "est": "🕍 Cristo (B + C)" if (in_b or in_c) else "🕯️ Cirio"},
            {"tramo": "7. Gasolinera ➔ San Fco", "est": "🕍 Cristo (Turno A)" if in_a else "🕯️ Cirio"}
        ]

    def distribuir_trono(personas):
        varas = ["Izquierda", "Centro", "Derecha"]
        res = {v: {"Delante": [], "Detras": []} for v in varas}
        ps = personas.copy()
        ps.sort(key=lambda x: (x['altura'] == 0, -x['altura']))
        for _ in range(6):
            for v in varas: res[v]["Delante"].append(ps.pop(0))
        ps.sort(key=lambda x: (x['altura'] == 0, x['altura']))
        for _ in range(6):
            for v in varas: res[v]["Detras"].append(ps.pop(0))
        return res

    def distribuir_cruz(personas):
        varas = ["Izquierda", "Derecha"]
        res = {v: {"Delante": [], "Detras": []} for v in varas}
        ps = personas.copy()
        ps.sort(key=lambda x: (x['altura'] == 0, -x['altura']))
        for _ in range(2):
            for v in varas: res[v]["Delante"].append(ps.pop(0))
        ps.sort(key=lambda x: (x['altura'] == 0, x['altura']))
        for _ in range(2):
            for v in varas: res[v]["Detras"].append(ps.pop(0))
        return res

    return {
        "cuadrillas": {
            "Trono": {"Turno A": distribuir_trono(turno_a), "Turno B": distribuir_trono(turno_b), "Turno C": distribuir_trono(turno_c)},
            "Cruz": {"Turno 1": distribuir_cruz(cruz_turnos[0]), "Turno 2": distribuir_cruz(cruz_turnos[1]), "Turno 3": distribuir_cruz(cruz_turnos[2]), "Turno 4": distribuir_cruz(cruz_turnos[3])}
        },
        "itinerarios": itinerarios
    }


def generar_html_viernes(datos_completos, master_list, anio, es_par, peso_trono, peso_cruz, limite_peso):
    turnos_json = json.dumps(datos_completos["cuadrillas"])
    itinerarios_json = json.dumps(datos_completos["itinerarios"])
    master_json = json.dumps(master_list)

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Viernes Santo - La Agonía</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #0c0209; color: #f8f0f5; padding: 20px; }}
            .controles {{ position: sticky; top: 0; background: #1a0514; padding: 15px; z-index: 100; border-bottom: 2px solid #d4af37; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }}
            
            .buscador-box {{ background: #23061b; padding: 20px; margin: 20px 0; border: 1px solid #d4af37; border-radius: 8px; }}
            .buscador-box input {{ width: 100%; padding: 12px; font-size: 16px; background: #0c0209; color: #d4af37; border: 1px solid #3d0c2e; border-radius: 5px; outline: none; }}
            .itinerario-result {{ margin-top: 15px; padding: 15px; background: #160311; border-radius: 5px; border-left: 5px solid #d4af37; display: none; }}
            .itinerario-result li {{ padding: 8px 0; border-bottom: 1px dashed #3d0c2e; font-size: 14px; list-style: none; }}
            .itinerario-result li:last-child {{ border: none; }}

            .turno-container {{ background: #1a0514; padding: 20px; margin-bottom: 40px; border-radius: 15px; border: 1px solid #3d0c2e; box-shadow: 0 0 15px rgba(212, 175, 55, 0.05); }}
            .turno-container h2 {{ color: #d4af37; text-transform: uppercase; letter-spacing: 2px; border-bottom: 1px solid #3d0c2e; padding-bottom: 10px; }}
            .grid-trono {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
            .grid-cruz {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; max-width: 700px; margin: 0 auto; }}
            .vara {{ background: #23061b; padding: 15px; border-radius: 10px; border-top: 5px solid #d4af37; }}
            .vara h3 {{ color: #e8d08c; margin-top: 0; font-size: 14px; text-align: center; }}
            .seccion {{ background: #160311; padding: 10px; margin: 10px 0; border-radius: 5px; min-height: 80px; border: 1px dashed #4a1038; }}
            .costalero {{ background: #3d0c2e; border: 1px solid #571342; margin: 5px 0; padding: 8px; border-radius: 4px; cursor: move; display: flex; justify-content: space-between; align-items: center; font-size: 11px; transition: 0.3s; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }}
            .costalero.vacio {{ border: 1px dashed #571342; background: #0c0209; color: #884d72; cursor: default; flex-direction: column; align-items: stretch; text-shadow: none; }}
            .costalero.sobrepeso {{ border: 2px solid #ff4757; background: #6b0b1c; }}
            
            /* ESTILOS DE REPETIDORES */
            .costalero.repetidor-c {{ border: 1px solid #ffd700; box-shadow: inset 0 0 8px rgba(255, 215, 0, 0.2); }}
            .nombre-repetidor-c {{ color: #ffd700; font-weight: bold; font-size: 11px; }}
            
            .costalero.repetidor-cruz {{ border: 1px solid #00d2ff; box-shadow: inset 0 0 8px rgba(0, 210, 255, 0.2); }}
            .nombre-repetidor-cruz {{ color: #00d2ff; font-weight: bold; font-size: 11px; }}

            .costalero.repetidor-cruz-doble {{ border: 2px solid #ff4757; box-shadow: inset 0 0 10px rgba(255, 71, 87, 0.4); }}
            .nombre-repetidor-cruz-doble {{ color: #ff4757; font-weight: bold; font-size: 11px; }}

            .btn-control {{ background: #3d0c2e; color: #f8f0f5; border: 1px solid #d4af37; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: 0.3s; font-size: 12px; text-transform: uppercase; }}
            .btn-control:hover {{ background: #571342; box-shadow: 0 0 8px rgba(212, 175, 55, 0.4); }}
            .stats-box {{ background: #0c0209; padding: 8px; border-radius: 4px; font-size: 10px; color: #d4af37; margin-top: 5px; border-left: 3px solid #d4af37; }}
            input.search-p {{ background: #0c0209; border: 1px solid #3d0c2e; color: #d4af37; padding: 5px; width: 100%; font-size: 10px; border-radius: 3px; outline: none; }}
            .sugerencias {{ background: #1a0514; border: 1px solid #d4af37; max-height: 80px; overflow-y: auto; position: absolute; z-index: 200; width: 200px; }}
            .sug-item {{ padding: 5px; cursor: pointer; border-bottom: 1px solid #3d0c2e; color: #e8d08c; font-size: 11px; }}
            .sug-item:hover {{ background: #3d0c2e; color: #fff; }}
        </style>
    </head>
    <body>
        <div class="controles">
            <div>
                <div style="font-size:18px; font-weight:bold; color:#d4af37;">VIERNES SANTO - ORDEN PROCESIONAL</div>
                <div style="font-size:11px; color:#a37c95; margin-top: 3px;">Regla estricta de descanso aplicada (Obligación de Cirio entre cargas)</div>
            </div>
            <div>
                <button id="btn-heatmap" class="btn-control" onclick="toggleHeatmap()">🧊 Mapa Peso: OFF</button>
            </div>
        </div>

        <div class="buscador-box">
            <h3 style="margin-top:0; color:#d4af37;">🔍 BUSCADOR DE ITINERARIO PERSONAL</h3>
            <p style="font-size:12px; color:#a37c95; margin-top:-10px;">Comprueba los tramos de descanso y carga de cualquier costalero/a. Si hay falta de personal, el programa asume doble carga de emergencia.</p>
            <input type="text" placeholder="Escribe el nombre de un costalero/a..." onkeyup="buscarItinerario(event)">
            <div id="resultado-itinerario" class="itinerario-result"></div>
        </div>
        
        <div style="margin-top:10px; padding:15px; border:1px dashed #3d0c2e; font-size:13px; background:#160311;">
            <b style="color:#e8d08c;">LEYENDA DE COLORES:</b><br><br>
            <span style="color:#ffd700; margin-right:20px; font-weight:bold;">■ Amarillo: Repite en Turno C (Viene del B)</span>
            <span style="color:#00d2ff; margin-right:20px; font-weight:bold;">■ Azul: Repite en la Cruz (Viene del B o C)</span>
            <span style="color:#ff4757; font-weight:bold;">■ Rojo (C-Doble): Carga consecutiva de Emergencia (Sin descanso)</span>
        </div>

        <div id="app"></div>

        <script>
            let datos = {turnos_json};
            const MASTER_LIST = {master_json};
            const ITINERARIOS = {itinerarios_json};
            const PESO_TRONO = {peso_trono};
            const PESO_CRUZ = {peso_cruz};
            const MAX_KG = {limite_peso};
            let heatmapActivo = false;

            // Motor del Buscador de Itinerarios
            function buscarItinerario(ev) {{
                const val = ev.target.value.toLowerCase();
                const resDiv = document.getElementById('resultado-itinerario');
                if (val.length < 3) {{ resDiv.style.display = 'none'; return; }}

                let found = null;
                for (let name of Object.keys(ITINERARIOS)) {{
                    if (name.toLowerCase().includes(val)) {{
                        found = {{ name, data: ITINERARIOS[name] }};
                        break;
                    }}
                }}

                if (found) {{
                    resDiv.style.display = 'block';
                    let html = `<h4 style="color:#d4af37; margin-bottom:10px; font-size:16px;">📋 Hoja de Ruta: ${{found.name}}</h4><ul style="margin:0; padding:0;">`;
                    found.data.forEach(t => {{
                        let isWarning = t.est.includes("SIN DESCANSO");
                        let color = t.est.includes("Cristo") ? "#e8d08c" : (t.est.includes("Cruz") ? (isWarning ? "#ff4757" : "#00d2ff") : "#884d72");
                        let icono = t.est.includes("Cirio") ? "🚶‍♂️" : "💪";
                        html += `<li>
                                    <span style="display:inline-block; width:220px; color:#a37c95;">${{t.tramo}}</span>
                                    ${{icono}} <strong style="color:${{color}}">${{t.est}}</strong>
                                 </li>`;
                    }});
                    html += `</ul>`;
                    resDiv.innerHTML = html;
                }} else {{
                    resDiv.style.display = 'none';
                }}
            }}

            function toggleHeatmap() {{
                heatmapActivo = !heatmapActivo;
                const btn = document.getElementById('btn-heatmap');
                btn.innerText = heatmapActivo ? '🔥 Mapa Peso: ON' : '🧊 Mapa Peso: OFF';
                if (heatmapActivo) {{
                    btn.style.background = '#d4af37'; btn.style.color = '#0c0209';
                }} else {{
                    btn.style.background = '#3d0c2e'; btn.style.color = '#f8f0f5';
                }}
                render();
            }}

            function getHeatmapColor(peso, tipo) {{
                if (!peso || peso === 0) return '';
                const base = tipo === 'Trono' ? PESO_TRONO / 36 : PESO_CRUZ / 8;
                const minVal = base - 10;
                let p = (peso - minVal) / (MAX_KG - minVal);
                p = Math.max(0, Math.min(1, p));
                const hue = (1 - p) * 120;
                return `hsl(${{hue}}, 80%, 30%)`;
            }}

            function render() {{
                const app = document.getElementById('app');
                app.innerHTML = '';
                
                for (const [tipo, turnos] of Object.entries(datos)) {{
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
                                
                                if (sec === "Delante") {{
                                    html += `<div class="stats-box"><b>${{sec.toUpperCase()}}:</b> ${{statsSec.media.toFixed(1)}}cm | ${{statsSec.totalVara.toFixed(1)}}kg</div>`;
                                }}
                                
                                if (sec === "Detras") {{
                                    let divTitulo = tipo === "Trono" ? "▼ TRONO ▼" : "▼ CRUZ ▼";
                                    html += `<div style="text-align:center; padding-top: 10px; margin-bottom: 5px; color:#e8d08c; font-size:12px; font-weight:bold; letter-spacing:2px; border-top: 1px dashed #3d0c2e;">${{divTitulo}}</div>`;
                                }}
                                
                                html += `<div class="seccion" ondragover="allow(event)">`;
                                
                                vData[sec].forEach((p, i) => {{
                                    const esVacio = p.altura === 0;
                                    const esSobrepeso = p.peso >= MAX_KG;
                                    
                                    // Comprobadores de colores para repetidores
                                    const esRepC = p.nombre && p.nombre.includes("(R)");
                                    const esRepCruz = p.nombre && p.nombre.includes("(C)");
                                    const esRepCruzDoble = p.nombre && p.nombre.includes("(C-Doble)");
                                    
                                    let clExtra = '';
                                    let nExtra = '';
                                    if (esRepC && !heatmapActivo) {{ clExtra = 'repetidor-c'; nExtra = 'nombre-repetidor-c'; }}
                                    if (esRepCruz && !esRepCruzDoble && !heatmapActivo) {{ clExtra = 'repetidor-cruz'; nExtra = 'nombre-repetidor-cruz'; }}
                                    if (esRepCruzDoble && !heatmapActivo) {{ clExtra = 'repetidor-cruz-doble'; nExtra = 'nombre-repetidor-cruz-doble'; }}
                                    
                                    let bgStyle = '';
                                    if (heatmapActivo && !esVacio) {{
                                        bgStyle = `background-color: ${{getHeatmapColor(p.peso, tipo)}} !important; border-color: transparent;`;
                                    }}

                                    html += `
                                        <div class="costalero ${{esVacio ? 'vacio' : ''}} ${{esSobrepeso && !heatmapActivo ? 'sobrepeso' : ''}} ${{clExtra}}" 
                                             style="${{bgStyle}}"
                                             draggable="${{!esVacio}}" ondragstart="drag(event, '${{tipo}}', '${{idT}}', '${{vNom}}', '${{sec}}', ${{i}})" ondrop="drop(event, '${{tipo}}', '${{idT}}', '${{vNom}}', '${{sec}}', ${{i}})">
                                            ${{esVacio ? 
                                                `<input type="text" class="search-p" placeholder="Escribir nombre..." onkeyup="buscarMini(event, '${{tipo}}','${{idT}}','${{vNom}}','${{sec}}',${{i}})">
                                                 <div id="sug-${{tipo}}-${{idT}}-${{vNom}}-${{sec}}-${{i}}" class="sugerencias" style="display:none"></div>` :
                                                `<span>
                                                    <button style="background:none; border:none; color:#ff4757; cursor:pointer; padding:0 5px 0 0;" onclick="eliminar('${{tipo}}','${{idT}}','${{vNom}}','${{sec}}',${{i}})">🗑️</button>
                                                    <span class="${{nExtra}}">${{p.nombre}}</span>
                                                </span>
                                                <span>
                                                    <span style="color:${{heatmapActivo ? '#fff' : '#d4af37'}}">${{p.altura}}cm</span> 
                                                    <b style="color:${{heatmapActivo ? '#fff' : '#e8d08c'}}; margin-left:5px">${{p.peso.toFixed(1)}}kg</b>
                                                </span>`
                                            }}
                                        </div>`;
                                }});
                                html += `</div>`;
                                
                                if (sec === "Detras") {{
                                    html += `<div class="stats-box"><b>${{sec.toUpperCase()}}:</b> ${{statsSec.media.toFixed(1)}}cm | ${{statsSec.totalVara.toFixed(1)}}kg</div>`;
                                }}
                            }});
                            html += `<div style="text-align:center; padding:10px; border:1px solid #d4af37; border-radius:5px; font-size:12px; color:#d4af37; margin-top:10px;"><b>TOTAL VARA: ${{statsVara.totalVara.toFixed(1)}} kg</b></div></div>`;
                        }}
                        app.innerHTML += html + `</div></div>`;
                    }}
                }}
            }}

            function calcularStats(p_list, tipo) {{
                let filtrados = p_list.filter(p => p.altura > 0);
                let m = filtrados.length > 0 ? filtrados.reduce((a, b) => a + b.altura, 0) / filtrados.length : 0;
                let tV = 0; 
                let base = tipo === 'Trono' ? PESO_TRONO / 36 : PESO_CRUZ / 8;
                
                p_list.forEach(p => {{
                    if(p.altura > 0) {{
                        p.peso = Math.min(MAX_KG, Math.max(0, base + ((p.altura - m) * (base * 0.05))));
                        tV += p.peso;
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
                        div.onclick = () => {{ datos[tipo][t][v][s][i] = {{...m}}; render(); }};
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
                render();
            }}
            
            function eliminar(tipo, t, v, s, i) {{
                const persona = datos[tipo][t][v][s][i].nombre;
                if (confirm(`¿Estás seguro de que quieres quitar a ${{persona}} de este hueco?`)) {{
                    datos[tipo][t][v][s][i] = {{"nombre": "HUECO LIBRE", "altura": 0}};
                    render();
                }}
            }}
            
            window.onload = render;
        </script>
    </body>
    </html>
    """
    with open("visualizador_viernes.html", "w", encoding="utf-8") as f: 
        f.write(html)