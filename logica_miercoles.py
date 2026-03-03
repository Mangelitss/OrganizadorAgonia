import json
import math

def cargar_datos_miercoles(archivo='datos.json'):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            # Filtramos estrictamente a los que están marcados para el Miércoles Santo
            return [d for d in datos if d.get('miercoles_santo', False)]
    except Exception as e:
        print(f"Error cargando {archivo}: {e}")
        return []

def generar_cuadrillas_miercoles(costaleros):
    pool = sorted(costaleros, key=lambda x: x['altura'], reverse=True)
    
    # Necesitamos 72 para el Trono + 16 para la Cruz = 88 personas mínimo.
    # Rellenamos con huecos libres si faltan personas.
    while len(pool) < 88:
        pool.append({"nombre": "HUECO LIBRE", "altura": 0, "peso": 0})
        
    turno_a_personas = pool[:36]
    turno_b_personas = pool[36:72]
    cruz_1_personas = pool[72:80]
    cruz_2_personas = pool[80:88]

    # Distribución 3 varales (Trono)
    def distribuir_trono(personas):
        varas = ["Izquierda", "Centro", "Derecha"]
        res = {v: {"Delante": [], "Detras": []} for v in varas}
        
        personas.sort(key=lambda x: (x['altura'] == 0, -x['altura']))
        for _ in range(6):
            for v in varas: res[v]["Delante"].append(personas.pop(0))
            
        personas.sort(key=lambda x: (x['altura'] == 0, x['altura']))
        for _ in range(6):
            for v in varas: res[v]["Detras"].append(personas.pop(0))
        return res

    # Distribución 2 varales (Cruz)
    def distribuir_cruz(personas):
        varas = ["Izquierda", "Derecha"]
        res = {v: {"Delante": [], "Detras": []} for v in varas}
        
        personas.sort(key=lambda x: (x['altura'] == 0, -x['altura']))
        for _ in range(2):
            for v in varas: res[v]["Delante"].append(personas.pop(0))
            
        personas.sort(key=lambda x: (x['altura'] == 0, x['altura']))
        for _ in range(2):
            for v in varas: res[v]["Detras"].append(personas.pop(0))
        return res

    return {
        "Trono": {
            "Turno A": distribuir_trono(turno_a_personas),
            "Turno B": distribuir_trono(turno_b_personas)
        },
        "Cruz": {
            "Turno 1": distribuir_cruz(cruz_1_personas),
            "Turno 2": distribuir_cruz(cruz_2_personas)
        }
    }

def generar_html_miercoles(datos_cuadrillas, master_list, anio, es_par, peso_trono, peso_cruz, limite_peso):
    turnos_json = json.dumps(datos_cuadrillas)
    master_json = json.dumps(master_list)

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Miércoles Santo - La Agonía</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #0c0209; color: #f8f0f5; padding: 20px; }}
            .controles {{ position: sticky; top: 0; background: #1a0514; padding: 15px; z-index: 100; border-bottom: 2px solid #d4af37; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }}
            .info-ruta {{ background: #23061b; padding: 15px; border-left: 5px solid #d4af37; margin-bottom: 20px; border-radius: 4px; }}
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
                <div style="font-size:18px; font-weight:bold; color:#d4af37;">MIÉRCOLES SANTO - ORDEN PROCESIONAL</div>
                <div style="font-size:11px; color:#a37c95; margin-top: 3px;">Simulación interactiva de Trono y Cruz</div>
            </div>
            <div>
                <button id="btn-heatmap" class="btn-control" onclick="toggleHeatmap()">🧊 Mapa Peso: OFF</button>
            </div>
        </div>
        
        <div class="info-ruta">
            <h3 style="margin:0; color:#d4af37;">📅 AÑO {anio} ({'PAR' if es_par else 'IMPAR'})</h3>
            <p style="margin: 8px 0 0 0; font-size: 13px; color: #e8d08c; line-height: 1.6;">
                {'📍 <b>TRONO:</b> Sale <b>Turno B</b> (San Francisco ➔ Gasolinera) | Releva <b>Turno A</b> (Gasolinera ➔ Monserrate)<br>' if es_par else '📍 <b>TRONO:</b> Sale <b>Turno A</b> (San Francisco ➔ Gasolinera) | Releva <b>Turno B</b> (Gasolinera ➔ Monserrate)<br>'}
                ✝️ <b>CRUZ:</b> Sale <b>Turno 1</b> (San Francisco ➔ Monserrate) | Releva <b>Turno 2</b> (Monserrate ➔ Encierro)
            </p>
        </div>

        <div id="app"></div>

        <script>
            let datos = {turnos_json};
            const MASTER_LIST = {master_json};
            const PESO_TRONO = {peso_trono};
            const PESO_CRUZ = {peso_cruz};
            const MAX_KG = {limite_peso};
            let heatmapActivo = false;

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
                    let tituloBloque = tipo === "Trono" ? "🕍 TRONO PRINCIPAL (72 Plazas)" : "✝️ LA CRUZ (16 Plazas)";
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
                                    
                                    let bgStyle = '';
                                    if (heatmapActivo && !esVacio) {{
                                        bgStyle = `background-color: ${{getHeatmapColor(p.peso, tipo)}} !important; border-color: transparent;`;
                                    }}

                                    html += `
                                        <div class="costalero ${{esVacio ? 'vacio' : ''}} ${{esSobrepeso && !heatmapActivo ? 'sobrepeso' : ''}}" 
                                             style="${{bgStyle}}"
                                             draggable="${{!esVacio}}" ondragstart="drag(event, '${{tipo}}', '${{idT}}', '${{vNom}}', '${{sec}}', ${{i}})" ondrop="drop(event, '${{tipo}}', '${{idT}}', '${{vNom}}', '${{sec}}', ${{i}})">
                                            ${{esVacio ? 
                                                `<input type="text" class="search-p" placeholder="Escribir nombre..." onkeyup="buscar(event, '${{tipo}}','${{idT}}','${{vNom}}','${{sec}}',${{i}})">
                                                 <div id="sug-${{tipo}}-${{idT}}-${{vNom}}-${{sec}}-${{i}}" class="sugerencias" style="display:none"></div>` :
                                                `<span>
                                                    <button style="background:none; border:none; color:#ff4757; cursor:pointer; padding:0 5px 0 0;" onclick="eliminar('${{tipo}}','${{idT}}','${{vNom}}','${{sec}}',${{i}})">🗑️</button>
                                                    ${{p.nombre}}
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

            function buscar(ev, tipo, t, v, s, i) {{
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
    with open("visualizador_miercoles.html", "w", encoding="utf-8") as f: 
        f.write(html)