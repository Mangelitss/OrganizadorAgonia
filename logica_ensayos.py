import json

def generar_html_ensayo(num_turnos, master_list, peso_trono, limite_peso):
    master_json = json.dumps(master_list)

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Organizador de Ensayos - La Agonía</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
        <style>
            /* PALETA CLARA - MAYORDOMÍA */
            :root {{
                --bg-main: #f4f6f8;
                --bg-panel: #ffffff;
                --color-granate: #5c164e; /* Morado Nazareno */
                --color-oro: #d4af37;
                --color-oro-oscuro: #b5952f;
                --text-dark: #333333;
                --text-muted: #666666;
                --border-color: #e0e0e0;
            }}

            body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg-main); color: var(--text-dark); margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}
            
            /* HEADER */
            .header {{ background: var(--bg-panel); padding: 15px 25px; border-bottom: 4px solid var(--color-granate); display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.05); z-index: 100; flex-shrink: 0; }}
            .header-info h1 {{ margin: 0; font-size: 20px; color: var(--color-granate); text-transform: uppercase; letter-spacing: 1px; }}
            .header-info p {{ margin: 3px 0 0 0; font-size: 12px; color: var(--text-muted); font-weight: 500; }}
            
            .controles-btn {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
            .fecha-input {{ background: #fff; border: 1px solid var(--border-color); color: var(--text-dark); padding: 8px; border-radius: 5px; outline: none; font-family: inherit; }}
            
            .btn-control {{ background: #fff; color: var(--color-granate); border: 1px solid var(--color-granate); padding: 8px 12px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: 0.3s; font-size: 11px; text-transform: uppercase; }}
            .btn-control:hover {{ background: var(--color-granate); color: #fff; box-shadow: 0 4px 8px rgba(92, 22, 78, 0.2); }}
            
            .btn-accion {{ background: var(--color-oro); color: #fff; border-color: var(--color-oro-oscuro); }}
            .btn-accion:hover {{ background: var(--color-oro-oscuro); color: #fff; box-shadow: 0 4px 8px rgba(212, 175, 55, 0.3); border-color: var(--color-oro-oscuro); }}
            
            .btn-peligro {{ background: #fff; border-color: #ff4757; color: #ff4757; }}
            .btn-peligro:hover {{ background: #ff4757; color: #fff; }}
            
            .btn-load {{ background: #17517e; border-color: #2980b9; color: #fff; }}
            .btn-load:hover {{ background: #1f6b9c; color: #fff; box-shadow: 0 0 10px rgba(41, 128, 185, 0.6); border-color: #2980b9; }}
            
            .btn-pdf {{ background: #5c164e; color: #fff; border-color: #5c164e; }}
            .btn-pdf:hover {{ background: #7a1b67; color: #fff; }}

            /* MAIN LAYOUT */
            .main-container {{ display: flex; flex-grow: 1; overflow: hidden; }}
            
            /* ZONA IZQUIERDA (TRONOS 60%) */
            .zona-tronos {{ flex: 6; overflow-y: auto; padding: 25px; background: var(--bg-main); }}
            
            /* ZONA DERECHA (MENU LATERAL 40%) */
            .zona-menu {{ flex: 4; background: var(--bg-panel); border-left: 1px solid var(--border-color); display: flex; flex-direction: column; overflow: hidden; transition: 0.3s; max-width: 450px; box-shadow: -5px 0 15px rgba(0,0,0,0.02); }}
            .zona-menu.oculto {{ flex: 0; max-width: 0; border-left: none; }}
            
            /* PANELES DEL MENU LATERAL */
            .panel-buscador {{ padding: 20px; background: #fafafa; border-bottom: 1px solid var(--border-color); }}
            .panel-buscador h3 {{ margin: 0 0 10px 0; color: var(--color-granate); font-size: 15px; }}
            .buscador-input {{ width: 100%; padding: 10px; font-size: 14px; background: #fff; color: var(--text-dark); border: 1px solid #ccc; border-radius: 5px; outline: none; box-sizing: border-box; transition: border-color 0.3s; }}
            .buscador-input:focus {{ border-color: var(--color-granate); }}
            
            .resultados-busqueda {{ max-height: 150px; overflow-y: auto; background: #fff; margin-top: 5px; border-radius: 5px; border: 1px solid var(--border-color); }}
            .resultado-item {{ padding: 10px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; font-size: 13px; }}
            .resultado-item:hover {{ background: #f0f4f8; }}
            .btn-add {{ background: var(--color-oro); color: #fff; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; font-weight: bold; font-size: 11px; }}
            .btn-add:hover {{ background: var(--color-oro-oscuro); }}
            
            .panel-asistentes {{ flex-grow: 1; padding: 20px; overflow-y: auto; }}
            .panel-asistentes h3 {{ margin: 0 0 15px 0; color: var(--color-granate); font-size: 15px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--bg-main); padding-bottom: 10px; }}
            .contador-asist {{ background: var(--color-granate); color: #fff; padding: 2px 10px; border-radius: 12px; font-size: 12px; }}
            .lista-asistentes {{ list-style: none; padding: 0; margin: 0; }}
            .asistente-item {{ background: #fff; padding: 10px 12px; margin-bottom: 8px; border-radius: 4px; border: 1px solid var(--border-color); border-left: 4px solid var(--color-oro); display: flex; justify-content: space-between; align-items: center; font-size: 13px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
            .btn-remove {{ background: transparent; color: #ff4757; border: 1px solid #ff4757; padding: 3px 8px; border-radius: 3px; cursor: pointer; transition: 0.2s; font-weight: bold; }}
            .btn-remove:hover {{ background: #ff4757; color: #fff; }}

            /* ESTILOS DEL TRONO */
            .turno-container {{ background: var(--bg-panel); padding: 25px; margin-bottom: 40px; border-radius: 15px; border: 1px solid var(--border-color); box-shadow: 0 8px 20px rgba(0,0,0,0.04); }}
            .turno-container h2 {{ color: var(--color-granate); text-transform: uppercase; letter-spacing: 2px; border-bottom: 2px solid var(--color-oro); padding-bottom: 10px; margin-top: 0; }}
            .grid-trono {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
            .vara {{ background: #fafafa; padding: 15px; border-radius: 8px; border-top: 5px solid var(--color-granate); border: left: 1px solid var(--border-color); border-right: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); }}
            .vara h3 {{ color: var(--color-granate); margin: 0 0 15px 0; font-size: 14px; text-align: center; font-weight: 800; }}
            .seccion {{ background: #ffffff; padding: 10px; margin: 10px 0; border-radius: 5px; min-height: 60px; border: 1px dashed #b0b0b0; }}
            .stats-box {{ background: #fdfdfd; padding: 8px; border-radius: 4px; font-size: 11px; color: var(--color-granate); margin-bottom: 8px; border-left: 3px solid var(--color-oro); border-top: 1px solid #eee; border-right: 1px solid #eee; border-bottom: 1px solid #eee; }}
            
            .costalero {{ background: #ffffff; border: 1px solid #dcdcdc; margin: 6px 0; padding: 8px; border-radius: 4px; cursor: move; display: flex; justify-content: space-between; align-items: center; font-size: 12px; transition: 0.3s; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }}
            .costalero.vacio {{ border: 1px dashed #b0b0b0; background: #fafafa; color: #888; cursor: default; justify-content: center; box-shadow: none; }}
            .costalero.sobrepeso {{ border: 2px solid #ff4757; background: #fff0f2; }}
            
            .btn-basura {{ background:none; border:none; cursor:pointer; padding:0 5px 0 0; font-size: 14px; }}
            .btn-basura:hover {{ transform: scale(1.2); }}

        </style>
    </head>
    <body>
        
        <div class="header">
            <div class="header-info">
                <h1>📋 GESTIÓN DE ENSAYOS</h1>
                <p>Modo interactivo y generación de actas PDF</p>
            </div>
            <div class="controles-btn">
                <input type="date" id="fecha-ensayo" class="fecha-input" onchange="guardarEstado()">
                
                <input type="file" id="file-input" accept=".json" style="display: none;" onchange="cargarJSON(event)">
                <button class="btn-control btn-load" onclick="document.getElementById('file-input').click()">📂 CARGAR JSON</button>
                <button class="btn-control btn-accion" onclick="descargarDatosJSON()">💾 DESCARGAR JSON</button>
                
                <button class="btn-control btn-peligro" onclick="resetearEnsayo()">🗑️ VACIAR ENSAYO</button>
                <button class="btn-control" onclick="toggleMenu()">↔️ OCULTAR MENÚ</button>
                <button class="btn-control btn-accion" onclick="distribuirAsistentes()">⚡ AUTO-DISTRIBUIR</button>
                <button class="btn-control btn-pdf" id="btn-generar-pdf" onclick="exportarAsistenciaPDF()">📄 EXPORTAR ACTA PDF</button>
            </div>
        </div>

        <div class="main-container">
            <div class="zona-tronos" id="grid-app"></div>

            <div class="zona-menu" id="panel-lateral">
                <div class="panel-buscador">
                    <h3>➕ Pasar Lista (Añadir)</h3>
                    <input type="text" id="input-busqueda" class="buscador-input" placeholder="Buscar por nombre o altura..." onkeyup="buscarEnCenso()">
                    <div id="resultados-busqueda" class="resultados-busqueda"></div>
                </div>
                
                <div class="panel-asistentes">
                    <h3>
                        Lista de Asistencia
                        <span class="contador-asist" id="contador-asistentes">0</span>
                    </h3>
                    <ul class="lista-asistentes" id="lista-asistentes-ui"></ul>
                </div>
            </div>
        </div>

        <div id="pdf-container" style="display:none;"></div>

        <script>
            const MASTER_LIST = {master_json};
            const NUM_TURNOS = {num_turnos};
            const PESO_TRONO = {peso_trono};
            const MAX_KG = {limite_peso};
            
            let asistentes = []; 
            let turnosData = {{}};  
            let heatmapActivo = false;

            // ==========================================
            // SISTEMA DE AUTOGUARDADO Y ARCHIVOS JSON
            // ==========================================
            function guardarEstado() {{
                localStorage.setItem('ensayo_asistentes_agonia', JSON.stringify(asistentes));
                localStorage.setItem('ensayo_turnos_agonia', JSON.stringify(turnosData));
                localStorage.setItem('ensayo_fecha_agonia', document.getElementById('fecha-ensayo').value);
            }}

            function cargarEstado() {{
                let savedAsistentes = localStorage.getItem('ensayo_asistentes_agonia');
                let savedTurnos = localStorage.getItem('ensayo_turnos_agonia');
                let savedFecha = localStorage.getItem('ensayo_fecha_agonia');
                
                if (savedAsistentes && savedTurnos) {{
                    asistentes = JSON.parse(savedAsistentes);
                    turnosData = JSON.parse(savedTurnos);
                    if(savedFecha) document.getElementById('fecha-ensayo').value = savedFecha;
                    
                    renderPanelAsistentes();
                    renderGrid();
                    return true;
                }}
                return false;
            }}

            function descargarDatosJSON() {{
                let exportData = {{
                    fecha: document.getElementById('fecha-ensayo').value,
                    asistentes: asistentes,
                    turnosData: turnosData
                }};
                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
                const dlAnchorElem = document.createElement('a');
                dlAnchorElem.setAttribute("href", dataStr);
                
                let fechaFormateada = exportData.fecha ? exportData.fecha : "SinFecha";
                dlAnchorElem.setAttribute("download", `Configuracion_Ensayo_${{fechaFormateada}}.json`);
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
                        const data = JSON.parse(e.target.result);
                        if(data.turnosData && data.asistentes) {{
                            turnosData = data.turnosData;
                            asistentes = data.asistentes;
                            if(data.fecha) document.getElementById('fecha-ensayo').value = data.fecha;
                            
                            guardarEstado();
                            renderPanelAsistentes();
                            renderGrid();
                            alert("✅ Configuración de ensayo cargada correctamente.");
                        }} else {{
                            alert("❌ El archivo no parece ser un ensayo válido.");
                        }}
                    }} catch (error) {{
                        alert("❌ Error al leer el archivo JSON.");
                    }}
                    event.target.value = '';
                }};
                reader.readAsText(file);
            }}

            function resetearEnsayo() {{
                if (confirm("⚠️ ¿Estás seguro de vaciar el ensayo? Perderás la lista actual si no has descargado el JSON.")) {{
                    localStorage.removeItem('ensayo_asistentes_agonia');
                    localStorage.removeItem('ensayo_turnos_agonia');
                    localStorage.removeItem('ensayo_fecha_agonia');
                    asistentes = [];
                    turnosData = {{}};
                    document.getElementById('fecha-ensayo').valueAsDate = new Date();
                    inicializarTurnos();
                    renderPanelAsistentes();
                }}
            }}

            // ==========================================
            // LÓGICA CORE DEL ENSAYO
            // ==========================================
            function inicializarTurnos() {{
                let letras = ["A", "B", "C", "D", "E", "F"];
                for(let i=0; i<NUM_TURNOS; i++) {{
                    let nombreT = "Turno " + (letras[i] || (i+1));
                    turnosData[nombreT] = {{
                        "Izquierda": {{ "Delante": Array(6).fill(null).map(hueco), "Detras": Array(6).fill(null).map(hueco) }},
                        "Centro": {{ "Delante": Array(6).fill(null).map(hueco), "Detras": Array(6).fill(null).map(hueco) }},
                        "Derecha": {{ "Delante": Array(6).fill(null).map(hueco), "Detras": Array(6).fill(null).map(hueco) }}
                    }};
                }}
                renderGrid();
                guardarEstado();
            }}

            function hueco() {{ return {{nombre: "HUECO LIBRE", altura: 0, peso: 0, id: -1}}; }}

            function toggleMenu() {{ document.getElementById('panel-lateral').classList.toggle('oculto'); }}

            function buscarEnCenso() {{
                const val = document.getElementById('input-busqueda').value.toLowerCase();
                const resDiv = document.getElementById('resultados-busqueda');
                if (val.length < 2) {{ resDiv.innerHTML = ''; return; }}

                const matches = MASTER_LIST.filter(p => p.nombre.toLowerCase().includes(val) || p.altura.toString().includes(val));
                
                let html = '';
                matches.forEach(m => {{
                    let yaEsta = asistentes.some(a => a.id === m.id);
                    if(!yaEsta) {{
                        html += `
                        <div class="resultado-item">
                            <span>${{m.nombre}} <b style="color:var(--color-granate)">(${{m.altura}}cm)</b></span>
                            <button class="btn-add" onclick='añadirAsistente(${{JSON.stringify(m)}})'>AÑADIR</button>
                        </div>`;
                    }}
                }});
                resDiv.innerHTML = html;
            }}

            function añadirAsistente(persona) {{
                asistentes.push(persona);
                document.getElementById('input-busqueda').value = '';
                document.getElementById('resultados-busqueda').innerHTML = '';
                renderPanelAsistentes();
                guardarEstado(); 
            }}

            function quitarAsistente(id) {{
                asistentes = asistentes.filter(a => a.id !== id);
                for (let t in turnosData) {{
                    for (let v in turnosData[t]) {{
                        for (let sec in turnosData[t][v]) {{
                            let arr = turnosData[t][v][sec];
                            for(let i=0; i<arr.length; i++) {{
                                if(arr[i].id === id) arr[i] = hueco();
                            }}
                        }}
                    }}
                }}
                renderPanelAsistentes();
                renderGrid();
                guardarEstado();
            }}

            function renderPanelAsistentes() {{
                asistentes.sort((a,b) => b.altura - a.altura);
                document.getElementById('contador-asistentes').innerText = asistentes.length;
                let html = '';
                asistentes.forEach(a => {{
                    html += `
                    <li class="asistente-item">
                        <span><b>${{a.nombre}}</b> <span style="color:var(--text-muted)">(${{a.altura}}cm)</span></span>
                        <button class="btn-remove" onclick="quitarAsistente(${{a.id}})">X</button>
                    </li>`;
                }});
                document.getElementById('lista-asistentes-ui').innerHTML = html;
            }}

            function distribuirAsistentes() {{
                if (asistentes.length === 0) {{
                    alert("No hay asistentes. Pasa lista primero.");
                    return;
                }}

                let ordenados = [...asistentes].sort((a,b) => b.altura - a.altura);
                let turnosNombres = Object.keys(turnosData);
                
                turnosNombres.forEach((idT, index) => {{
                    let chunk = ordenados.slice(index * 36, (index + 1) * 36);
                    while(chunk.length < 36) chunk.push(hueco()); 
                    
                    let varas = ["Izquierda", "Centro", "Derecha"];
                    let tData = {{
                        "Izquierda": {{Delante:[], Detras:[]}},
                        "Centro": {{Delante:[], Detras:[]}},
                        "Derecha": {{Delante:[], Detras:[]}}
                    }};
                    
                    let ps = chunk.slice();
                    ps.sort((a,b) => (a.altura===0?1:0) - (b.altura===0?1:0) || b.altura - a.altura);
                    for(let i=0; i<6; i++) {{ varas.forEach(v => tData[v].Delante.push(ps.shift())); }}
                    
                    ps.sort((a,b) => (a.altura===0?1:0) - (b.altura===0?1:0) || a.altura - b.altura);
                    for(let i=0; i<6; i++) {{ varas.forEach(v => tData[v].Detras.push(ps.shift())); }}
                    
                    turnosData[idT] = tData;
                }});
                
                renderGrid();
                guardarEstado();
            }}

            function renderGrid() {{
                const app = document.getElementById('grid-app');
                app.innerHTML = '';
                
                for (const [idT, varas] of Object.entries(turnosData)) {{
                    let html = `<div class="turno-container"><h2>${{idT}}</h2><div class="grid-trono">`;
                    
                    for (const [vNom, vData] of Object.entries(varas)) {{
                        const statsVara = calcularStats(vData.Delante.concat(vData.Detras));
                        
                        html += `<div class="vara"><h3>VARA ${{vNom.toUpperCase()}}</h3>`;
                        ["Delante", "Detras"].forEach(sec => {{
                            const statsSec = calcularStats(vData[sec]);
                            
                            if (sec === "Delante") html += `<div class="stats-box"><b>${{sec.toUpperCase()}}:</b> ${{statsSec.media.toFixed(1)}}cm | ${{statsSec.totalVara.toFixed(1)}}kg</div>`;
                            if (sec === "Detras") html += `<div style="text-align:center; padding-top: 15px; margin-bottom: 10px; color:var(--color-granate); font-size:12px; font-weight:bold; letter-spacing:2px; border-top: 1px solid var(--border-color);">▼ TRONO ▼</div>`;
                            
                            html += `<div class="seccion" ondragover="allow(event)">`;
                            
                            vData[sec].forEach((p, i) => {{
                                const esVacio = p.altura === 0;
                                const esSobrepeso = p.peso >= MAX_KG;
                                
                                let tickHombro = '';
                                if (!esVacio) {{
                                    let pref = (p.pref_hombro || "").toLowerCase().trim();
                                    if (pref !== "") {{
                                        if (pref.includes("derech")) {{
                                            if (vNom === "Izquierda") tickHombro = ' <span title="Hombro correcto" style="font-size:11px;">✅</span>';
                                            else tickHombro = ' <span title="Hombro INCORRECTO" style="font-size:11px;">❌</span>';
                                        }} else if (pref.includes("izquierd")) {{
                                            if (vNom === "Derecha") tickHombro = ' <span title="Hombro correcto" style="font-size:11px;">✅</span>';
                                            else tickHombro = ' <span title="Hombro INCORRECTO" style="font-size:11px;">❌</span>';
                                        }} else if (pref.includes("ambos")) {{
                                            tickHombro = ' <span title="Hombro correcto" style="font-size:11px;">✅</span>';
                                        }}
                                    }}
                                }}
                                
                                html += `
                                    <div class="costalero ${{esVacio ? 'vacio' : ''}} ${{esSobrepeso ? 'sobrepeso' : ''}}" 
                                         draggable="${{!esVacio}}" ondragstart="drag(event, '${{idT}}', '${{vNom}}', '${{sec}}', ${{i}})" ondrop="drop(event, '${{idT}}', '${{vNom}}', '${{sec}}', ${{i}})">
                                        ${{esVacio ? 
                                            `<span>HUECO LIBRE</span>` :
                                            `<span>
                                                <button class="btn-basura" style="color:#ff4757;" onclick="vaciarHueco('${{idT}}','${{vNom}}','${{sec}}',${{i}})">🗑️</button>
                                                <b style="color:var(--text-dark)">${{p.nombre}} ${{tickHombro}}</b>
                                            </span>
                                            <span>
                                                <span style="color:var(--text-dark)">${{p.altura}}cm</span> 
                                                <b style="color:var(--color-granate); margin-left:5px">${{p.peso.toFixed(1)}}kg</b>
                                            </span>`
                                        }}
                                    </div>`;
                            }});
                            html += `</div>`;
                            if (sec === "Detras") html += `<div class="stats-box"><b>${{sec.toUpperCase()}}:</b> ${{statsSec.media.toFixed(1)}}cm | ${{statsSec.totalVara.toFixed(1)}}kg</div>`;
                        }});
                        html += `<div style="text-align:center; padding:10px; background:#fff; border:1px solid var(--color-oro); border-radius:5px; font-size:12px; color:var(--color-granate); margin-top:15px; font-weight:bold;">TOTAL VARA: ${{statsVara.totalVara.toFixed(1)}} kg</div></div>`;
                    }}
                    app.innerHTML += html + `</div></div>`;
                }}
            }}

            function calcularStats(p_list) {{
                let filtrados = p_list.filter(p => p.altura > 0);
                let m = filtrados.length > 0 ? filtrados.reduce((a, b) => a + b.altura, 0) / filtrados.length : 0;
                let tV = 0; const base = PESO_TRONO / 36;
                p_list.forEach(p => {{
                    if(p.altura > 0) {{
                        p.peso = Math.min(MAX_KG, Math.max(0, base + ((p.altura - m) * (base * 0.05))));
                        tV += p.peso;
                    }} else p.peso = 0;
                }});
                return {{ media: m, totalVara: tV }};
            }}

            let dragging = null;
            function allow(ev) {{ ev.preventDefault(); }}
            function drag(ev, t, v, s, i) {{ dragging = {{ t, v, s, i }}; }}
            function drop(ev, t, v, s, i) {{
                ev.preventDefault();
                let orig = turnosData[dragging.t][dragging.v][dragging.s][dragging.i];
                turnosData[dragging.t][dragging.v][dragging.s][dragging.i] = turnosData[t][v][s][i];
                turnosData[t][v][s][i] = orig;
                renderGrid();
                guardarEstado();
            }}
            function vaciarHueco(t, v, s, i) {{
                turnosData[t][v][s][i] = hueco();
                renderGrid();
                guardarEstado();
            }}

            // ==========================================
            // EXPORTACIÓN A PDF (ESTILO MAYORDOMÍA)
            // ==========================================
            function exportarAsistenciaPDF() {{
                if(asistentes.length === 0) {{
                    alert("El ensayo está vacío. Añade costaleros primero.");
                    return;
                }}
                
                const btn = document.getElementById('btn-generar-pdf');
                btn.innerText = "⏳ GENERANDO ACTA...";
                
                let fechaInput = document.getElementById("fecha-ensayo").value;
                let fechaFormateada = fechaInput ? fechaInput.split('-').reverse().join('/') : new Date().toLocaleDateString();
                
                // CONSTRUCCIÓN DEL HTML PARA EL PDF
                let htmlPDF = `
                <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; padding: 20px;">
                    
                    <div style="text-align: center; border-bottom: 2px solid #5c164e; padding-bottom: 15px; margin-bottom: 20px;">
                        <img src="bandera_tercio_npj.jpg" alt="Logo" style="width: 80px; height: auto; margin-bottom: 10px;" onerror="this.style.display='none'">
                        <h1 style="color: #5c164e; margin: 0; font-size: 20px; text-transform: uppercase;">OFS Muy Ilustre Mayordomía Ntro. Padre Jesús Nazareno</h1>
                        <h2 style="color: #b5952f; margin: 5px 0; font-size: 16px; text-transform: uppercase;">Acta Oficial de Ensayo</h2>
                        <p style="margin: 5px 0 0 0; font-size: 13px; font-weight: bold; color: #666;">Fecha del Ensayo: ${{fechaFormateada}}</p>
                    </div>

                    <h3 style="color: #5c164e; border-bottom: 1px solid #d4af37; padding-bottom: 5px; font-size: 16px;">1. LISTADO DE ASISTENCIA (${{asistentes.length}} Costaleros)</h3>
                    <ul style="column-count: 3; column-gap: 20px; list-style:none; padding:0; margin:0 0 30px 0; font-size: 11px;">
                `;
                
                let asisNombres = [...asistentes].sort((a,b) => a.nombre.localeCompare(b.nombre));
                asisNombres.forEach(a => {{
                    htmlPDF += `<li style="padding: 4px 0; border-bottom: 1px solid #eee;">
                                    <b>${{a.nombre}}</b> <span style="color:#888;">(${{a.altura}}cm)</span>
                                </li>`;
                }});
                
                htmlPDF += `</ul>`;

                // SECCIÓN 2: DISTRIBUCIÓN
                htmlPDF += `<h3 style="color: #5c164e; border-bottom: 1px solid #d4af37; padding-bottom: 5px; font-size: 16px; page-break-before: always;">2. DISTRIBUCIÓN DEL TRONO</h3>`;
                
                for (const [idT, varas] of Object.entries(turnosData)) {{
                    htmlPDF += `
                    <div style="border: 1px solid #d4af37; border-radius: 8px; margin-bottom: 25px; page-break-inside: avoid;">
                        <h3 style="background: #5c164e; color: #fff; padding: 8px; margin: 0; font-size: 14px; text-transform: uppercase; text-align: center;">${{idT}}</h3>
                        <div style="display: flex; width: 100%;">
                    `;
                    
                    for (const [vNom, vData] of Object.entries(varas)) {{
                        htmlPDF += `
                            <div style="flex: 1; padding: 10px; border-right: 1px solid #eee;">
                                <h4 style="text-align: center; color: #5c164e; border-bottom: 2px solid #d4af37; padding-bottom: 5px; margin: 0 0 10px 0; font-size: 12px; font-weight: bold; text-transform: uppercase;">VARA ${{vNom}}</h4>
                        `;
                        
                        ["Delante", "Detras"].forEach(sec => {{
                            if(sec === "Delante") htmlPDF += `<div style="font-size: 10px; color: #5c164e; text-align: center; margin-bottom: 5px; font-weight: bold; background: #eee; padding: 3px; border-radius: 3px;">▲ DELANTE ▲</div>`;
                            if(sec === "Detras") htmlPDF += `<div style="font-size: 10px; color: #fff; text-align: center; margin: 8px 0; font-weight: bold; background: #5c164e; padding: 3px; border-radius: 3px;">▼ TRONO ▼</div>`;
                            
                            htmlPDF += `<ul style="list-style: none; padding: 0; margin: 0; font-size: 10px;">`;
                            vData[sec].forEach(p => {{
                                let esVacio = p.altura === 0;
                                if(esVacio) {{
                                    htmlPDF += `<li style="padding: 4px; margin-bottom: 2px; text-align:center; border: 1px dashed #ccc; background: #fafafa; color: #aaa; font-style: italic;">-- Hueco Libre --</li>`;
                                }} else {{
                                    htmlPDF += `<li style="padding: 4px; margin-bottom: 2px; border: 1px solid #ddd; display: flex; justify-content: space-between;">
                                                    <b>${{p.nombre}}</b> <span style="color:#666;">${{p.altura}}cm</span>
                                                </li>`;
                                }}
                            }});
                            htmlPDF += `</ul>`;
                            
                            if(sec === "Detras") htmlPDF += `<div style="font-size: 10px; color: #5c164e; text-align: center; margin-top: 5px; font-weight: bold; background: #eee; padding: 3px; border-radius: 3px;">▼ DETRÁS ▼</div>`;
                        }});
                        htmlPDF += `</div>`;
                    }}
                    htmlPDF += `</div></div>`;
                }}
                htmlPDF += `</div>`;

                const container = document.getElementById('pdf-container');
                container.innerHTML = htmlPDF;
                container.style.display = 'block';

                const opciones = {{
                    margin:       10,
                    filename:     `Acta_Ensayo_${{fechaFormateada.replace(/\\//g,'-')}}.pdf`,
                    image:        {{ type: 'jpeg', quality: 0.98 }},
                    html2canvas:  {{ scale: 2, useCORS: true }},
                    jsPDF:        {{ unit: 'mm', format: 'a4', orientation: 'portrait' }}
                }};
                
                html2pdf().set(opciones).from(container).save().then(() => {{
                    container.style.display = 'none';
                    btn.innerText = "📄 EXPORTAR ACTA PDF";
                }});
            }}

            window.onload = () => {{
                let cargado = cargarEstado();
                if(!cargado) {{
                    document.getElementById('fecha-ensayo').valueAsDate = new Date();
                    inicializarTurnos();
                }}
            }};
        </script>
    </body>
    </html>
    """
    with open("visualizador_ensayos.html", "w", encoding="utf-8") as f: 
        f.write(html)