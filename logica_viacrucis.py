import json
import time

def generar_datos_viacrucis(seleccionados, num_turnos, autocompletar):
    pool = sorted(seleccionados, key=lambda x: x.get('altura', 0), reverse=True)
    turnos = {}
    
    for i in range(num_turnos):
        t_name = f"Tramo {i+1}"
        personas_turno = []
        if autocompletar and pool:
            start = (i * 8) % max(len(pool), 1) if pool else 0
            for j in range(8):
                if pool:
                    idx = (start + j) % len(pool)
                    personas_turno.append(pool[idx].copy())
                else:
                    personas_turno.append({"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})
        else:
            personas_turno = [{"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1} for _ in range(8)]
            
        turnos[t_name] = distribuir_estructura(personas_turno)
        
    return {"tipo_procesion": "via_crucis", "ViaCrucis": turnos}

def distribuir_estructura(personas):
    varas = ["Izquierda", "Derecha"]
    # ESTRUCTURA ARREGLADA: Varal -> Sección (Igual que en el Trono principal)
    res = {v: {"Delante": [], "Detras": []} for v in varas}
    
    reales = [p for p in personas if p.get('altura', 0) > 0]
    huecos = [p for p in personas if p.get('altura', 0) == 0]
    
    # Delante
    reales.sort(key=lambda x: x.get('altura', 0), reverse=True)
    for _ in range(2):
        fila = []
        for _ in range(2): 
            fila.append(reales.pop(0) if reales else huecos.pop(0) if huecos else {"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})
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
        
    # Detras
    reales.sort(key=lambda x: x.get('altura', 0))
    for _ in range(2):
        fila = []
        for _ in range(2): 
            fila.append(reales.pop(0) if reales else huecos.pop(0) if huecos else {"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1})
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

def generar_html_viacrucis(datos_gen, master_list, seleccionados_ids):
    turnos_json = json.dumps(datos_gen)
    master_json = json.dumps(master_list)
    sel_json = json.dumps(seleccionados_ids)
    marca_tiempo = str(int(time.time()))

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Vía Crucis - Gestor de Turnos</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #0c0209; color: #f8f0f5; padding: 20px; }}
            .controles {{ position: sticky; top: 0; background: #1a0514; padding: 15px; z-index: 100; border-bottom: 2px solid #d4af37; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }}
            
            .turno-container {{ background: #1a0514; padding: 20px; margin-bottom: 40px; border-radius: 15px; border: 1px solid #3d0c2e; box-shadow: 0 0 15px rgba(212, 175, 55, 0.05); }}
            .turno-container h2 {{ color: #d4af37; text-transform: uppercase; letter-spacing: 2px; border-bottom: 1px solid #3d0c2e; padding-bottom: 10px; }}
            .grid-cruz {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; max-width: 700px; margin: 0 auto; }}
            .vara {{ background: #23061b; padding: 15px; border-radius: 10px; border-top: 5px solid #d4af37; }}
            .vara h3 {{ color: #e8d08c; margin: 0 0 10px 0; font-size: 14px; text-align: center; }}
            .seccion {{ background: #160311; padding: 10px; margin: 10px 0; border-radius: 5px; min-height: 80px; border: 1px dashed #4a1038; }}
            
            .costalero {{ background: #3d0c2e; border: 1px solid #571342; margin: 5px 0; padding: 8px; border-radius: 4px; cursor: move; display: flex; justify-content: space-between; align-items: center; font-size: 11px; transition: 0.3s; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }}
            .costalero.vacio {{ border: 1px dashed #571342; background: #0c0209; color: #884d72; cursor: default; flex-direction: column; align-items: stretch; text-shadow: none; overflow: visible; position: relative; }}
            
            .btn-control {{ background: #3d0c2e; color: #f8f0f5; border: 1px solid #d4af37; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 12px; margin-left: 5px; text-transform: uppercase; transition: 0.3s; }}
            .btn-control:hover {{ background: #571342; box-shadow: 0 0 8px rgba(212, 175, 55, 0.4); }}
            .btn-export {{ background: #d4af37; color: #000; border-color: #b5952f; }}
            .btn-export:hover {{ background: #b5952f; color:#000; }}
            .btn-danger {{ background: #b30000; border-color: #ff4d4d; }}
            .btn-danger:hover {{ background: #ff4d4d; color: #fff; box-shadow: 0 0 8px rgba(255, 77, 77, 0.4); }}
            
            input.search-p {{ background: #0c0209; border: 1px solid #3d0c2e; color: #d4af37; padding: 5px; width: 100%; font-size: 10px; border-radius: 3px; outline: none; box-sizing: border-box; }}
            input.search-p:focus {{ border-color: #d4af37; }}
            .sugerencias {{ background: #1a0514; border: 1px solid #d4af37; max-height: 100px; overflow-y: auto; position: absolute; z-index: 999; width: 100%; top: 100%; left: 0; box-shadow: 0 4px 6px rgba(0,0,0,0.2); border-radius: 3px; }}
            .sug-item {{ padding: 6px; cursor: pointer; border-bottom: 1px solid #eee; color: #e8d08c; font-size: 11px; text-align: left; }}
            .sug-item:hover {{ background: #3d0c2e; color: #fff; font-weight: bold; }}
            
            /* PANEL LATERAL CENSO */
            #sidebar-toggle {{
                position: fixed; right: 0; top: 50%; transform: translateY(-50%);
                background: #d4af37; color: #0c0209; border: none; cursor: pointer;
                padding: 12px 7px; border-radius: 8px 0 0 8px; z-index: 200;
                font-size: 11px; font-weight: bold; writing-mode: vertical-rl;
                letter-spacing: 1px; transition: right 0.3s ease; box-shadow: -3px 0 8px rgba(0,0,0,0.4);
            }}
            #sidebar-toggle.abierto {{ right: 290px; }}
            #sidebar {{
                position: fixed; right: 0; top: 0; height: 100vh; width: 290px;
                background: #1a0514; border-left: 2px solid #d4af37;
                z-index: 150; transform: translateX(100%);
                transition: transform 0.3s ease;
                display: flex; flex-direction: column; overflow: hidden;
                box-shadow: -5px 0 20px rgba(0,0,0,0.6);
            }}
            #sidebar.abierto {{ transform: translateX(0); }}
            #sidebar-header {{ padding: 15px; border-bottom: 1px solid #3d0c2e; background: #23061b; }}
            #sidebar-header h3 {{ color: #d4af37; margin: 0 0 10px 0; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }}
            #sidebar-search {{
                width: 100%; background: #0c0209; border: 1px solid #3d0c2e;
                color: #d4af37; padding: 8px; border-radius: 4px; font-size: 12px;
                outline: none; box-sizing: border-box;
            }}
            #sidebar-search:focus {{ border-color: #d4af37; }}
            #sidebar-contador {{ font-size: 10px; color: #a37c95; margin-top: 6px; }}
            #sidebar-lista {{ flex: 1; overflow-y: auto; padding: 8px; }}
            .sidebar-item {{
                background: #3d0c2e; border: 1px solid #571342; margin: 3px 0;
                padding: 7px 10px; border-radius: 4px; cursor: grab;
                font-size: 11px; color: #f8f0f5;
                display: flex; justify-content: space-between; align-items: center;
                transition: background 0.2s; text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
                user-select: none;
            }}
            .sidebar-item:hover {{ background: #571342; border-color: #d4af37; }}
            .sidebar-item.ya-asignado {{ opacity: 0.38; border-style: dashed; cursor: grab; }}
        </style>
    </head>
    <body>
        <button id="sidebar-toggle" onclick="toggleSidebar()">👥 CENSO</button>
        <div id="sidebar">
            <div id="sidebar-header">
                <h3>👥 Costaleros — Vía Crucis</h3>
                <input type="text" id="sidebar-search" placeholder="Busca nombre o altura en todo el censo..." oninput="renderSidebar()">
                <div id="sidebar-contador"></div>
            </div>
            <div id="sidebar-lista"></div>
        </div>
        
        <div class="controles">
            <div>
                <div style="font-size:18px; font-weight:bold; color:#d4af37;">VÍA CRUCIS - GESTOR DE TURNOS</div>
                <div style="font-size:11px; color:#a37c95; margin-top: 3px;">Indicador de preferencia de hombro: ✅ Hombro Correcto</div>
            </div>
            <div>
                <button class="btn-control btn-danger" onclick="vaciarCuadrante()">🗑️ VACIAR CUADRANTE</button>
                <button class="btn-control btn-export" onclick="descargarDatosJSON()">💾 DESCARGAR DATOS</button>
            </div>
        </div>

        <div id="app" style="margin-top: 30px;"></div>

        <script>
            const TS_PYTHON = "{marca_tiempo}";
            const DATOS_INICIALES = {turnos_json};
            const MASTER_LIST = {master_json};
            const SELECCIONADOS_IDS = {sel_json};
            
            let datos = {{}};

            function init() {{
                let savedTs = localStorage.getItem('viacrucis_ts');
                let savedDatos = localStorage.getItem('viacrucis_datos');
                if (savedDatos && savedTs === TS_PYTHON) {{
                    datos = JSON.parse(savedDatos);
                }} else {{
                    datos = JSON.parse(JSON.stringify(DATOS_INICIALES));
                    localStorage.setItem('viacrucis_ts', TS_PYTHON);
                    localStorage.setItem('viacrucis_datos', JSON.stringify(datos));
                }}
                render();
            }}

            function guardarMemoria() {{
                localStorage.setItem('viacrucis_datos', JSON.stringify(datos));
            }}

            function descargarDatosJSON() {{
                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(datos, null, 2));
                const dlAnchorElem = document.createElement('a');
                dlAnchorElem.setAttribute("href", dataStr);
                dlAnchorElem.setAttribute("download", "Distribucion_ViaCrucis.json");
                document.body.appendChild(dlAnchorElem);
                dlAnchorElem.click();
                dlAnchorElem.remove();
            }}

            function vaciarCuadrante() {{
                if(confirm("⚠️ ¿VACIAR el cuadrante completo?")) {{
                    for (let t of Object.keys(datos.ViaCrucis)) {{
                        for (let v of ["Izquierda", "Derecha"]) {{
                            for (let sec of ["Delante", "Detras"]) {{
                                for (let i = 0; i < datos.ViaCrucis[t][v][sec].length; i++) {{
                                    datos.ViaCrucis[t][v][sec][i] = {{"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1}};
                                }}
                            }}
                        }}
                    }}
                    render(); guardarMemoria();
                }}
            }}

            function vaciarTurno(idT) {{
                if(confirm(`⚠️ ¿Vaciar solo el ${{idT}}?`)) {{
                    for (let v of ["Izquierda", "Derecha"]) {{
                        for (let sec of ["Delante", "Detras"]) {{
                            for (let i = 0; i < datos.ViaCrucis[idT][v][sec].length; i++) {{
                                datos.ViaCrucis[idT][v][sec][i] = {{"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1}};
                            }}
                        }}
                    }}
                    render(); guardarMemoria();
                }}
            }}

            function render() {{
                const app = document.getElementById('app');
                app.innerHTML = '';
                
                let htmlInfo = `
                <div style="background:#23061b; padding:15px; border-left:5px solid #d4af37; margin-bottom:20px; border-radius:4px;">
                    <h3 style="margin:0; color:#d4af37;">⛪ ESTRUCTURA DEL VÍA CRUCIS</h3>
                    <p style="margin: 8px 0 0 0; font-size: 13px; color: #e8d08c; line-height: 1.6;">
                        Se compone de <b>4 varales</b> en total: 2 varales delanteros y 2 varales traseros.<br>
                        Cada varal es portado por <b>2 costaleros</b> (total: 8 costaleros por relevo).
                    </p>
                </div>
                `;
                app.innerHTML += htmlInfo;
                
                for (const [idT, varas] of Object.entries(datos.ViaCrucis)) {{
                    let html = `<div class="turno-container"><h2 style="display:flex; justify-content:space-between; align-items:center;">${{idT}} <button class="btn-control btn-danger" style="font-size:10px; padding:4px 12px; text-transform:none; letter-spacing:0;" onclick="vaciarTurno('${{idT}}')">🗑️ Vaciar tramo</button></h2><div class="grid-cruz">`;
                    
                    const ordenVaras = ["Izquierda", "Derecha"];
                    for (const vNom of ordenVaras) {{
                        const vData = varas[vNom];
                        html += `<div class="vara"><h3>VARAL ${{vNom.toUpperCase()}}</h3>`;
                        
                        ["Delante", "Detras"].forEach(sec => {{
                            html += `<div style="text-align:center; padding-top:10px; margin-bottom:15px; color:#e8d08c; font-size:12px; font-weight:bold; border-bottom:1px dashed #3d0c2e; padding-bottom:5px;">
                                ${{sec === "Delante" ? "▲ DELANTE ▲" : "▼ DETRÁS ▼"}}
                            </div>`;
                            
                            html += `<div class="seccion" ondragover="allow(event)">`;
                            vData[sec].forEach((p, i) => {{
                                const esVacio = p.altura === 0;
                                let tickHombro = ''; let prefLetra = '';

                                if (!esVacio) {{
                                    let pref = (p.pref_hombro || "").toLowerCase().trim();
                                    if (pref.includes("derech")) {{
                                        prefLetra = ' <span style="color:#888; font-size:9px;">(D)</span>';
                                        if (vNom === "Izquierda") tickHombro = ' <span title="Correcto" style="font-size:11px;">✅</span>';
                                        else tickHombro = ' <span title="Incorrecto" style="font-size:11px;">❌</span>';
                                    }} else if (pref.includes("izquierd")) {{
                                        prefLetra = ' <span style="color:#888; font-size:9px;">(I)</span>';
                                        if (vNom === "Derecha") tickHombro = ' <span title="Correcto" style="font-size:11px;">✅</span>';
                                        else tickHombro = ' <span title="Incorrecto" style="font-size:11px;">❌</span>';
                                    }} else {{
                                        tickHombro = ' <span style="font-size:11px;">✅</span>';
                                    }}
                                }}

                                html += `
                                    <div class="costalero ${{esVacio ? 'vacio' : ''}}" 
                                         draggable="${{!esVacio}}" ondragstart="drag(event, '${{idT}}', '${{vNom}}', '${{sec}}', ${{i}})" ondrop="drop(event, '${{idT}}', '${{vNom}}', '${{sec}}', ${{i}})">
                                        ${{esVacio ? 
                                            `<input type="text" class="search-p" placeholder="Buscar..." onkeyup="buscarMini(event, '${{idT}}','${{vNom}}','${{sec}}',${{i}})">
                                             <div id="sug-${{idT}}-${{vNom}}-${{sec}}-${{i}}" class="sugerencias" style="display:none"></div>` :
                                            `<span>
                                                <button style="background:none; border:none; color:#ff4757; cursor:pointer; padding:0 5px 0 0;" onclick="eliminar('${{idT}}','${{vNom}}','${{sec}}',${{i}})">🗑️</button>
                                                <span>${{p.nombre}}${{prefLetra}} ${{tickHombro}}</span>
                                            </span>
                                            <span><span style="color:#d4af37; font-weight:bold;">${{p.altura}}cm</span></span>`
                                        }}
                                    </div>`;
                            }});
                            html += `</div>`;
                        }});
                        html += `</div>`;
                    }}
                    html += `</div></div>`;
                    
                    // ESTA ERA LA LÍNEA QUE FALTABA Y DEJABA LA PANTALLA EN NEGRO
                    app.innerHTML += html; 
                }}
            }}

            function buscarMini(ev, t, v, s, i) {{
                function normalizar(st) {{ return st.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); }}
                const val = normalizar(ev.target.value.trim());
                const sugDiv = document.getElementById(`sug-${{t}}-${{v}}-${{s}}-${{i}}`);
                if(val.length < 2) {{ sugDiv.style.display = 'none'; return; }}
                
                const matches = MASTER_LIST.filter(p => normalizar(p.nombre).includes(val) || (p.altura && p.altura.toString().includes(val))).slice(0, 8);
                
                sugDiv.innerHTML = '';
                if(matches.length > 0) {{
                    sugDiv.style.display = 'block';
                    matches.forEach(m => {{
                        const div = document.createElement('div');
                        div.className = 'sug-item';
                        div.innerHTML = `${{m.nombre}} (${{m.altura}}cm)`;
                        div.onclick = () => {{ datos.ViaCrucis[t][v][s][i] = {{...m}}; render(); guardarMemoria(); }};
                        sugDiv.appendChild(div);
                    }});
                }} else sugDiv.style.display = 'none';
            }}

            let dragging = null;
            function allow(ev) {{ ev.preventDefault(); }}
            function drag(ev, t, v, s, i) {{ dragging = {{ source: 'slot', t, v, s, i }}; }}
            function drop(ev, t, v, s, i) {{
                ev.preventDefault();
                if (!dragging) return;
                if (dragging.source === 'sidebar') {{
                    datos.ViaCrucis[t][v][s][i] = {{...dragging.persona}};
                }} else {{
                    let orig = datos.ViaCrucis[dragging.t][dragging.v][dragging.s][dragging.i];
                    datos.ViaCrucis[dragging.t][dragging.v][dragging.s][dragging.i] = datos.ViaCrucis[t][v][s][i];
                    datos.ViaCrucis[t][v][s][i] = orig;
                }}
                render(); guardarMemoria();
                if (sidebarAbierto) renderSidebar();
            }}
            
            function eliminar(t, v, s, i) {{
                datos.ViaCrucis[t][v][s][i] = {{"nombre": "HUECO LIBRE", "altura": 0, "peso": 0, "id": -1}};
                render(); guardarMemoria();
                if (sidebarAbierto) renderSidebar();
            }}

            // PANEL LATERAL CENSO
            let sidebarAbierto = false;
            function toggleSidebar() {{
                sidebarAbierto = !sidebarAbierto;
                document.getElementById('sidebar').classList.toggle('abierto', sidebarAbierto);
                document.getElementById('sidebar-toggle').classList.toggle('abierto', sidebarAbierto);
                document.getElementById('sidebar-toggle').textContent = sidebarAbierto ? '✕ CERRAR' : '👥 CENSO';
                if (sidebarAbierto) renderSidebar();
            }}

            function normalizarSidebar(s) {{ return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); }}

            function getIdsAsignados() {{
                const ids = new Set();
                for (let t of Object.values(datos.ViaCrucis)) {{
                    for (let v of Object.values(t)) {{
                        for (let sec of ['Delante', 'Detras']) {{
                            if (v[sec]) {{
                                v[sec].forEach(p => {{ if (p.id && p.id !== -1) ids.add(p.id); }});
                            }}
                        }}
                    }}
                }}
                return ids;
            }}

            function renderSidebar() {{
                const val = normalizarSidebar(document.getElementById('sidebar-search').value.trim());
                const idsAsig = getIdsAsignados();
                
                let lista = MASTER_LIST;
                if (!val) {{
                    lista = lista.filter(p => SELECCIONADOS_IDS.includes(p.id));
                }} else {{
                    lista = lista.filter(p => normalizarSidebar(p.nombre).includes(val) || (p.altura && p.altura.toString().includes(val)));
                }}
                
                lista.sort((a, b) => {{
                    const aA = idsAsig.has(a.id), bA = idsAsig.has(b.id);
                    if (aA !== bA) return aA ? 1 : -1;
                    return b.altura - a.altura;
                }});
                
                const div = document.getElementById('sidebar-lista');
                div.innerHTML = '';
                lista.forEach(p => {{
                    const yaAsig = idsAsig.has(p.id);
                    const item = document.createElement('div');
                    item.className = 'sidebar-item' + (yaAsig ? ' ya-asignado' : '');
                    item.draggable = true;
                    item.title = yaAsig ? 'Ya asignado' : 'Arrastra a cualquier hueco';
                    
                    let prefLetra = '';
                    let pref = (p.pref_hombro || "").toLowerCase().trim();
                    if (pref.includes("derech")) prefLetra = ' <span style="color:#888; font-size:10px;">(D)</span>';
                    else if (pref.includes("izquierd")) prefLetra = ' <span style="color:#888; font-size:10px;">(I)</span>';
                    
                    item.innerHTML = `<span>${{p.nombre}}${{prefLetra}}</span><span style="color:#d4af37;font-weight:bold;">${{p.altura}}cm</span>`;
                    item.ondragstart = () => {{ dragging = {{ source: 'sidebar', persona: {{...p}} }}; }};
                    div.appendChild(item);
                }});
                
                const asig = MASTER_LIST.filter(p => idsAsig.has(p.id)).length;
                document.getElementById('sidebar-contador').textContent = `${{asig}} asignados actualmente`;
            }}

            window.onload = init; 
        </script>
    </body>
    </html>
    """
    with open("visualizador_viacrucis.html", "w", encoding="utf-8") as f: 
        f.write(html)