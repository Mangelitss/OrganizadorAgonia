import json
import math
import random

# ==========================================
# CONFIGURACIÓN TÉCNICA
# ==========================================
PESO_TRONO_KG = 2000    
LIMITE_PESO_PERSONA = 90  
NUM_TURNOS = ""         

def cargar_datos():
    try:
        with open('datos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return []

def generar_turnos_base(costaleros, n_config):
    pool = sorted(costaleros, key=lambda x: x['altura'], reverse=True)
    n_turnos = int(n_config) if n_config != "" else math.ceil(len(pool) / 36)
    
    total_huecos = n_turnos * 36
    final_pool = []
    solo_repetibles = [p for p in pool if p.get("puede_repetir", True)]
    
    for i in range(total_huecos):
        if i < len(pool):
            final_pool.append({**pool[i], "bloqueado": False})
        else:
            if solo_repetibles:
                p = solo_repetibles[i % len(solo_repetibles)].copy()
                p["nombre"] += " (R)"
                p["bloqueado"] = False
                final_pool.append(p)
            else:
                final_pool.append({"nombre": "HUECO LIBRE", "altura": 0, "bloqueado": False})

    resultado = {}
    varas = ["Izquierda", "Centro", "Derecha"]
    for t in range(n_turnos):
        id_t = f"Turno {chr(65 + t)}"
        bloque = final_pool[t*36 : (t+1)*36]
        bloque.sort(key=lambda x: x['altura'], reverse=True)
        resultado[id_t] = {v: {"Delante": [], "Detras": []} for v in varas}
        for i in range(6):
            for v in varas: resultado[id_t][v]["Delante"].append(bloque.pop(0))
        bloque.sort(key=lambda x: x['altura'])
        for i in range(6):
            for v in varas: resultado[id_t][v]["Detras"].append(bloque.pop(0))
            
    return resultado

def generar_html_interactivo(turnos, master_list):
    turnos_json = json.dumps(turnos)
    master_json = json.dumps(master_list)

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Gestor Inteligente Agonía</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #0a0a0a; color: white; padding: 20px; }}
            .controles {{ position: sticky; top: 0; background: #1a1a1a; padding: 15px; z-index: 100; border-bottom: 2px solid #333; display: flex; justify-content: space-between; }}
            .turno-container {{ background: #151515; padding: 20px; margin-bottom: 40px; border-radius: 15px; border: 1px solid #333; }}
            .grid-trono {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
            .vara {{ background: #1e1e1e; padding: 15px; border-radius: 10px; border-top: 5px solid #d35400; }}
            .seccion {{ background: #252525; padding: 10px; margin: 10px 0; border-radius: 5px; min-height: 150px; border: 1px dashed #444; }}
            .costalero {{ background: #333; margin: 5px 0; padding: 8px; border-radius: 4px; cursor: move; display: flex; justify-content: space-between; align-items: center; font-size: 11px; }}
            .costalero.vacio {{ border: 1px dashed #555; background: #111; color: #555; cursor: default; flex-direction: column; align-items: stretch; }}
            .costalero.sobrepeso {{ border: 2px solid #ff4757; background: #4a1515; }}
            .costalero.bloqueado {{ border-left: 5px solid #f1c40f; background: #2c2c00; }}
            .stats-box {{ background: #000; padding: 8px; border-radius: 4px; font-size: 10px; color: #03dac6; margin-top: 5px; border-left: 3px solid #03dac6; }}
            input.search-p {{ background: #000; border: 1px solid #444; color: #03dac6; padding: 5px; width: 100%; font-size: 10px; border-radius: 3px; outline: none; }}
            .sugerencias {{ background: #000; border: 1px solid #333; max-height: 80px; overflow-y: auto; position: absolute; z-index: 200; width: 200px; }}
            .sug-item {{ padding: 5px; cursor: pointer; border-bottom: 1px solid #222; }}
            .sug-item:hover {{ background: #222; }}
        </style>
    </head>
    <body>
        <div class="controles">
            <div style="font-size:16px; font-weight:bold; color:#d35400">LA AGONÍA - GESTIÓN TIEMPO REAL</div>
            <div style="font-size:11px; color:#aaa">Física automática | Autocompletar en huecos libres | Intercambio por arrastre</div>
        </div>
        <div id="app"></div>

        <script>
            let datos = {turnos_json};
            const MASTER_LIST = {master_json};
            const PESO_TOTAL = {PESO_TRONO_KG};
            const MAX_KG = {LIMITE_PESO_PERSONA};

            function render() {{
                const app = document.getElementById('app');
                app.innerHTML = '';
                for (const [idT, varas] of Object.entries(datos)) {{
                    let html = `<div class="turno-container"><h2>${{idT}}</h2><div class="grid-trono">`;
                    for (const vNom of ["Izquierda", "Centro", "Derecha"]) {{
                        let vData = varas[vNom];
                        const statsVara = calcularStats(vData.Delante.concat(vData.Detras));
                        html += `<div class="vara"><h3>VARA ${{vNom.toUpperCase()}}</h3>`;
                        ["Delante", "Detras"].forEach(sec => {{
                            const statsSec = calcularStats(vData[sec]);
                            html += `<div class="stats-box"><b>${{sec.toUpperCase()}}:</b> ${{statsSec.media.toFixed(1)}}cm | ${{statsSec.totalVara.toFixed(1)}}kg</div>`;
                            html += `<div class="seccion" ondragover="allow(event)">`;
                            vData[sec].forEach((p, i) => {{
                                const esVacio = p.altura === 0;
                                const esSobrepeso = p.peso >= MAX_KG;
                                html += `
                                    <div class="costalero ${{esVacio ? 'vacio' : ''}} ${{p.bloqueado ? 'bloqueado' : ''}} ${{esSobrepeso ? 'sobrepeso' : ''}}" 
                                         draggable="${{!esVacio}}" ondragstart="drag(event, '${{idT}}', '${{vNom}}', '${{sec}}', ${{i}})" ondrop="drop(event, '${{idT}}', '${{vNom}}', '${{sec}}', ${{i}})">
                                        ${{esVacio ? 
                                            `<input type="text" class="search-p" placeholder="Escribir nombre..." onkeyup="buscar(event, '${{idT}}','${{vNom}}','${{sec}}',${{i}})">
                                             <div id="sug-${{idT}}-${{vNom}}-${{sec}}-${{i}}" class="sugerencias" style="display:none"></div>` :
                                            `<span>
                                                <button style="background:none; border:none; color:#ff4757; cursor:pointer" onclick="eliminar('${{idT}}','${{vNom}}','${{sec}}',${{i}})">🗑️</button>
                                                <button style="background:none; border:none; color:white; cursor:pointer" onclick="toggle('${{idT}}','${{vNom}}','${{sec}}',${{i}})">${{p.bloqueado ? '🔒' : '🔓'}}</button>
                                                ${{p.nombre}}
                                            </span>
                                            <span><span style="color:#f1c40f">${{p.altura}}cm</span> <b style="color:#03dac6; margin-left:5px">${{p.peso.toFixed(1)}}kg</b></span>`
                                        }}
                                    </div>`;
                            }});
                            html += `</div>`;
                        }});
                        html += `<div style="text-align:center; padding:10px; border:1px solid #03dac6; border-radius:5px; font-size:12px"><b>TOTAL VARA: ${{statsVara.totalVara.toFixed(1)}} kg</b></div></div>`;
                    }}
                    app.innerHTML += html + `</div></div>`;
                }}
            }}

            function calcularStats(p_list) {{
                let filtrados = p_list.filter(p => p.altura > 0);
                let m = filtrados.length > 0 ? filtrados.reduce((a, b) => a + b.altura, 0) / filtrados.length : 0;
                let tV = 0; const base = PESO_TOTAL / 36;
                p_list.forEach(p => {{
                    if(p.altura > 0) {{
                        p.peso = Math.min(MAX_KG, Math.max(0, base + ((p.altura - m) * (base * 0.05))));
                        tV += p.peso;
                    }} else p.peso = 0;
                }});
                return {{ media: m, totalVara: tV }};
            }}

            function buscar(ev, t, v, s, i) {{
                const val = ev.target.value.toLowerCase();
                const sugDiv = document.getElementById(`sug-${{t}}-${{v}}-${{s}}-${{i}}`);
                if(val.length < 2) {{ sugDiv.style.display = 'none'; return; }}
                const matches = MASTER_LIST.filter(p => p.nombre.toLowerCase().includes(val)).slice(0, 5);
                sugDiv.innerHTML = '';
                if(matches.length > 0) {{
                    sugDiv.style.display = 'block';
                    matches.forEach(m => {{
                        const div = document.createElement('div');
                        div.className = 'sug-item';
                        div.innerHTML = `${{m.nombre}} (${{m.altura}}cm)`;
                        div.onclick = () => {{ datos[t][v][s][i] = {{...m, bloqueado: false}}; render(); }};
                        sugDiv.appendChild(div);
                    }});
                }} else sugDiv.style.display = 'none';
            }}

            let dragging = null;
            function allow(ev) {{ ev.preventDefault(); }}
            function drag(ev, t, v, s, i) {{ dragging = {{ t, v, s, i }}; }}
            function drop(ev, t, v, s, i) {{
                ev.preventDefault();
                let orig = datos[dragging.t][dragging.v][dragging.s][dragging.i];
                datos[dragging.t][dragging.v][dragging.s][dragging.i] = datos[t][v][s][i];
                datos[t][v][s][i] = orig;
                render();
            }}
            function eliminar(t, v, s, i) {{ datos[t][v][s][i] = {{"nombre": "HUECO LIBRE", "altura": 0, "bloqueado": false}}; render(); }}
            function toggle(t, v, s, i) {{ datos[t][v][s][i].bloqueado = !datos[t][v][s][i].bloqueado; render(); }}
            window.onload = render;
        </script>
    </body>
    </html>
    """
    with open("visualizador_interactivo.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    master_list = cargar_datos()
    if master_list:
        turnos = generar_turnos_base(master_list, NUM_TURNOS)
        generar_html_interactivo(turnos, master_list)
        print(">>> LISTO. Abre 'visualizador_interactivo.html'.")