import json
import time
import string

def generar_datos_personalizados(num_turnos_trono, num_turnos_cruz, num_tramos, lleva_cruz, costaleros_7):
    # Generar letras para Trono (Turno A, Turno B...)
    letras = list(string.ascii_uppercase)
    
    # TRONO: 3 varas delante, 3 varas detrás. Costaleros 6 o 7 por vara.
    plazas_por_vara = 7 if costaleros_7 else 6
    varas_trono = ["Izquierda", "Centro", "Derecha"]
    trono = {}
    
    for i in range(num_turnos_trono):
        nombre_turno = f"Turno {letras[i % len(letras)]}"
        trono[nombre_turno] = {
            "Delante": {v: [{"nombre": "HUECO LIBRE", "altura": 0, "id": -1} for _ in range(plazas_por_vara)] for v in varas_trono},
            "Detras": {v: [{"nombre": "HUECO LIBRE", "altura": 0, "id": -1} for _ in range(plazas_por_vara)] for v in varas_trono}
        }
        
    # CRUZ: 2 varas delante, 2 varas detrás. Siempre 2 costaleros por vara.
    varas_cruz = ["Izquierda", "Derecha"]
    cruz = {}
    
    if lleva_cruz:
        for i in range(num_turnos_cruz):
            nombre_turno = f"Turno {i+1}"
            cruz[nombre_turno] = {
                "Delante": {v: [{"nombre": "HUECO LIBRE", "altura": 0, "id": -1} for _ in range(2)] for v in varas_cruz},
                "Detras": {v: [{"nombre": "HUECO LIBRE", "altura": 0, "id": -1} for _ in range(2)] for v in varas_cruz}
            }

    # MAPPING (Matriz inicial de Tramos y a qué Turno apuntan). Por defecto secuencial.
    mapping = {}
    for i in range(num_tramos):
        tramo_name = f"Tramo {i+1}"
        t_trono = f"Turno {letras[i % num_turnos_trono]}" if num_turnos_trono > 0 else ""
        t_cruz = f"Turno {(i % num_turnos_cruz) + 1}" if (lleva_cruz and num_turnos_cruz > 0) else ""
        
        mapping[tramo_name] = {
            "Trono": t_trono,
            "Cruz": t_cruz
        }
        
    # INDICACIONES (Textos vacíos iniciales para cada tramo)
    indicaciones = {f"Tramo {i+1}": "" for i in range(num_tramos)}

    return {
        "tipo_procesion": "personalizada",
        "lleva_cruz": lleva_cruz,
        "costaleros_7": costaleros_7,
        "Trono": trono,
        "Cruz": cruz,
        "Mapping": mapping,
        "Indicaciones": indicaciones
    }

def generar_html_personalizado(datos_gen, master_list, lleva_cruz):
    datos_json = json.dumps(datos_gen)
    master_json = json.dumps(master_list)
    marca_tiempo = str(int(time.time()))

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Procesión Personalizada — Gestor Manual</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background:#0c0209; color:#f8f0f5; padding:20px; margin:0; }}
        .controles {{ position:sticky; top:0; background:#1a0514; padding:15px; z-index:100; border-bottom:2px solid #d4af37; display:flex; justify-content:space-between; align-items:center; box-shadow:0 4px 6px rgba(0,0,0,.5); }}
        .tabla-relevos {{ width:100%; border-collapse:collapse; margin-bottom:30px; background:#1a0514; border-radius:8px; overflow:hidden; }}
        .tabla-relevos th {{ background:#23061b; color:#d4af37; padding:12px; border-bottom:2px solid #3d0c2e; font-size:13px; }}
        .tabla-relevos td {{ padding:10px; border-bottom:1px solid #3d0c2e; text-align:center; }}
        .tabla-relevos select {{ background:#0c0209; color:#e8d08c; border:1px solid #3d0c2e; padding:5px; border-radius:4px; font-weight:bold; outline:none; }}
        .titulo-bloque {{ background:#23061b; padding:15px; border-left:5px solid #d4af37; margin:40px 0 20px; }}
        .titulo-bloque h2 {{ color:#d4af37; margin:0; font-size:20px; letter-spacing:2px; }}
        .turno-container {{ background:#1a0514; padding:20px; margin-bottom:30px; border-radius:10px; border:1px solid #3d0c2e; }}
        .turno-container h3 {{ color:#e8d08c; margin-top:0; font-size:16px; border-bottom:1px dashed #4a1038; padding-bottom:10px; display:flex; justify-content:space-between; align-items:center; }}
        .etiqueta-seccion {{ text-align:center; padding:8px; color:#d4af37; font-size:14px; font-weight:bold; letter-spacing:3px; background:#23061b; border:1px solid #d4af37; border-radius:4px; margin:15px 0; }}
        .grid-trono {{ display:grid; grid-template-columns:repeat(3,1fr); gap:15px; }}
        .grid-cruz  {{ display:grid; grid-template-columns:repeat(2,1fr); gap:15px; }}
        .vara {{ background:#160311; padding:10px; border-radius:8px; border-top:3px solid #571342; }}
        .vara-titulo {{ text-align:center; color:#a37c95; font-size:12px; margin-bottom:10px; font-weight:bold; text-transform:uppercase; }}
        
        .costalero {{ background:#3d0c2e; border:1px solid #571342; margin:5px 0; padding:8px; border-radius:4px; cursor:grab; display:flex; justify-content:space-between; align-items:center; font-size:11px; transition:.3s; text-shadow:1px 1px 2px rgba(0,0,0,.8); }}
        .costalero:active {{ cursor:grabbing; }}
        .costalero.vacio {{ border:1px dashed #571342; background:#0c0209; color:#884d72; flex-direction:column; align-items:stretch; text-shadow:none; position:relative; overflow:visible; }}
        
        .costalero.estado-dosTurnos  {{ border:1px solid #ffd700; box-shadow:inset 0 0 8px rgba(255,215,0,.25); }}
        .costalero.estado-cruzYTrono {{ border:1px solid #00d2ff; box-shadow:inset 0 0 8px rgba(0,210,255,.25); }}
        .costalero.estado-doble      {{ border:2px solid #ff4757; background:#6b0b1c; }}
        .costalero.estado-critico    {{ border:2px dashed #ff0000; background:#4a0000; animation:parpadeo 1s infinite; }}
        .txt-dosTurnos  {{ color:#ffd700; font-weight:bold; }}
        .txt-cruzYTrono {{ color:#00d2ff; font-weight:bold; }}
        .txt-doble      {{ color:#ff4757; font-weight:bold; }}
        .txt-critico    {{ color:#fff; font-weight:bold; }}
        @keyframes parpadeo {{ 50% {{ opacity:.5; }} }}
        
        .btn-accion {{ background:none; border:none; cursor:pointer; padding:0 3px; transition:.2s; }}
        .btn-accion:hover {{ opacity:.7; transform:scale(1.1); }}
        .btn-info {{ color:#3498db; font-size:13px; }}
        .btn-del  {{ color:#ff4757; font-size:12px; }}
        
        .btn-control {{ background:#3d0c2e; color:#f8f0f5; border:1px solid #d4af37; padding:8px 15px; border-radius:5px; cursor:pointer; font-weight:bold; font-size:12px; margin-left:5px; text-transform:uppercase; transition:.3s; }}
        .btn-control:hover {{ background:#571342; box-shadow:0 0 8px rgba(212,175,55,.4); }}
        .btn-export {{ background:#d4af37; color:#000; border-color:#b5952f; }}
        .btn-export:hover {{ background:#b5952f; color:#000; }}
        .btn-danger {{ background:#b30000; border-color:#ff4d4d; }}
        .btn-danger:hover {{ background:#ff4d4d; color:#fff; }}
        .btn-vacar {{ background:transparent; border:1px solid #b30000; color:#ff6b81; padding:3px 10px; border-radius:4px; cursor:pointer; font-size:11px; font-weight:bold; }}
        .btn-vacar:hover {{ background:#b30000; color:#fff; }}
        
        input.search-p {{ background:#0c0209; border:1px solid #3d0c2e; color:#d4af37; padding:5px; width:100%; font-size:10px; border-radius:3px; outline:none; box-sizing:border-box; }}
        .sugerencias {{ background:#1a0514; border:1px solid #d4af37; max-height:100px; overflow-y:auto; position:absolute; z-index:999; width:100%; top:100%; left:0; box-shadow:0 4px 6px rgba(0,0,0,.2); border-radius:3px; }}
        .sug-item {{ padding:6px; cursor:pointer; border-bottom:1px solid #3d0c2e; color:#e8d08c; font-size:11px; }}
        .sug-item:hover {{ background:#3d0c2e; color:#fff; font-weight:bold; }}
        
        .caja-indicacion {{ background:#160311; border:1px solid #3d0c2e; padding:15px; margin-bottom:15px; border-radius:8px; }}
        .caja-indicacion textarea {{ width:100%; background:#0c0209; color:#f8f0f5; border:1px solid #571342; padding:10px; border-radius:4px; outline:none; resize:vertical; min-height:60px; font-family:inherit; box-sizing:border-box; }}
        .caja-indicacion textarea:focus {{ border-color:#d4af37; }}
        
        /* SIDEBAR */
        #sidebar-toggle {{ position:fixed; right:0; top:50%; transform:translateY(-50%); background:#d4af37; color:#0c0209; border:none; cursor:pointer; padding:12px 7px; border-radius:8px 0 0 8px; z-index:200; font-size:11px; font-weight:bold; writing-mode:vertical-rl; transition:right .3s ease; box-shadow:-3px 0 8px rgba(0,0,0,.4); }}
        #sidebar-toggle.abierto {{ right:290px; }}
        #sidebar {{ position:fixed; right:0; top:0; height:100vh; width:290px; background:#1a0514; border-left:2px solid #d4af37; z-index:150; transform:translateX(100%); transition:transform .3s ease; display:flex; flex-direction:column; overflow:hidden; box-shadow:-5px 0 20px rgba(0,0,0,.6); }}
        #sidebar.abierto {{ transform:translateX(0); }}
        #sidebar-header {{ padding:15px; border-bottom:1px solid #3d0c2e; background:#23061b; }}
        #sidebar-search {{ width:100%; background:#0c0209; border:1px solid #3d0c2e; color:#d4af37; padding:8px; border-radius:4px; font-size:12px; outline:none; box-sizing:border-box; margin-top:10px; }}
        #sidebar-lista {{ flex:1; overflow-y:auto; padding:8px; }}
        .sidebar-item {{ background:#3d0c2e; border:1px solid #571342; margin:3px 0; padding:7px 10px; border-radius:4px; cursor:grab; font-size:11px; color:#f8f0f5; display:flex; justify-content:space-between; align-items:center; transition:.2s; user-select:none; }}
        .sidebar-item:hover {{ background:#571342; border-color:#d4af37; }}
        .sidebar-item.ya-asignado {{ opacity:.4; border-style:dashed; }}
        
        /* MODAL */
        .modal-overlay {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,.85); z-index:1000; justify-content:center; align-items:center; backdrop-filter:blur(3px); }}
        .modal-overlay.activo {{ display:flex; }}
        .modal-box {{ background:#1a0514; border:2px solid #d4af37; padding:28px; border-radius:12px; width:90%; max-width:580px; position:relative; max-height:85vh; overflow-y:auto; animation:slideIn .25s ease-out; }}
        .modal-close {{ position:absolute; top:12px; right:15px; background:none; border:none; color:#ff4757; font-size:24px; cursor:pointer; }}
        @keyframes slideIn {{ from {{ transform:translateY(-25px); opacity:0; }} to {{ transform:translateY(0); opacity:1; }} }}
        
        /* LEYENDA */
        .leyenda {{ display:flex; flex-wrap:wrap; gap:12px; background:#160311; padding:14px; border-radius:8px; margin-top:10px; font-size:12px; }}
        .ley-item {{ display:flex; align-items:center; gap:7px; }}
        .ley-dot {{ width:14px; height:14px; border-radius:3px; flex-shrink:0; }}
    </style>
</head>
<body>

    <div id="modal-ruta" class="modal-overlay" onclick="cerrarModalRuta(event)">
        <div class="modal-box" onclick="event.stopPropagation()">
            <button class="modal-close" onclick="cerrarModalRuta()">✖</button>
            <div id="modal-ruta-body"></div>
        </div>
    </div>

    <button id="sidebar-toggle" onclick="toggleSidebar()">👥 CENSO</button>
    <div id="sidebar">
        <div id="sidebar-header">
            <h3 style="color:#d4af37; margin:0; font-size:13px;">👥 Costaleros</h3>
            <input type="text" id="sidebar-search" placeholder="Nombre o altura..." oninput="renderSidebar()">
            <div id="sidebar-contador" style="font-size:10px; color:#a37c95; margin-top:5px;"></div>
        </div>
        <div id="sidebar-lista"></div>
    </div>

    <div class="controles">
        <div>
            <div style="font-size:18px; font-weight:bold; color:#d4af37;">⚙️ ENTORNO MANUAL PERSONALIZADO</div>
            <div style="font-size:11px; color:#a37c95; margin-top:3px;">Arrastra costaleros desde el panel derecho · Pulsa ℹ️ para ver la hoja de ruta.</div>
        </div>
        <div>
            <button class="btn-control btn-danger" onclick="vaciarTodo()">🗑️ VACIAR TODO</button>
            <button class="btn-control" onclick="abrirModalHojaRuta()">📋 HOJA DE RUTA</button>
            <button class="btn-control btn-export" onclick="descargarDatos()">💾 DESCARGAR JSON</button>
        </div>
    </div>

    <div style="max-width:960px; margin:30px auto;">
        <div class="titulo-bloque"><h2>📍 MATRIZ DE RELEVOS POR TRAMO</h2></div>
        <table class="tabla-relevos" id="tabla-mapping"></table>

        <div class="titulo-bloque"><h2>⛪ TRONO (EL CRISTO)</h2></div>
        <div id="app-trono"></div>

        { '<div class="titulo-bloque"><h2>✝ CRUZ INSIGNIA</h2></div><div id="app-cruz"></div>' if lleva_cruz else '' }

        <div class="titulo-bloque"><h2>📝 INDICACIONES POR TRAMO</h2></div>
        <div id="app-indicaciones"></div>

        <div class="titulo-bloque"><h2>⚖️ NORMAS DE LA CUADRILLA</h2></div>
        <div style="background:#160311; border:1px solid #3d0c2e; padding:15px; border-radius:8px; color:#e8d08c; font-size:13px; line-height:1.8;">
            1. Queda totalmente prohibido el uso de móviles durante la procesión.<br>
            2. Indumentaria estricta: traje oscuro y calzado negro sin logotipos visibles.<br>
            3. Puntualidad extrema en los puntos de relevo.<br>
            4. Seguir en todo momento las instrucciones de los Celadores y Capataces.
        </div>

        <div class="titulo-bloque"><h2>🎨 LEYENDA</h2></div>
        <div class="leyenda">
            <div class="ley-item"><div class="ley-dot" style="background:#3d0c2e; border:1px solid #571342;"></div><span>Normal</span></div>
            <div class="ley-item"><div class="ley-dot" style="background:#3d0c2e; border:1px solid #ffd700; box-shadow:inset 0 0 6px rgba(255,215,0,.3);"></div><span style="color:#ffd700;">Sale en 2 turnos</span></div>
            <div class="ley-item"><div class="ley-dot" style="background:#3d0c2e; border:1px solid #00d2ff; box-shadow:inset 0 0 6px rgba(0,210,255,.3);"></div><span style="color:#00d2ff;">Trono + Cruz</span></div>
            <div class="ley-item"><div class="ley-dot" style="background:#6b0b1c; border:2px solid #ff4757;"></div><span style="color:#ff4757;">Doble carga consecutiva</span></div>
            <div class="ley-item"><div class="ley-dot" style="background:#4a0000; border:2px dashed #ff0000;"></div><span style="color:#ff0000;">⚠️ CRÍTICO: 2 posiciones / Cruz y Trono a la vez</span></div>
        </div>
    </div>

<script>
    const TS          = "{marca_tiempo}";
    const DATOS_INIC  = {datos_json};
    const MASTER_LIST = {master_json};
    const LLEVA_CRUZ  = {str(lleva_cruz).lower()};
    let datos = {{}};

    /* ── INIT ── */
    function init() {{
        let savedTs   = localStorage.getItem('pers_ts_v5');
        let savedData = localStorage.getItem('pers_datos_v5');
        if (savedData && savedTs === TS) {{
            try {{
                let parsed = JSON.parse(savedData);
                if (parsed.Trono) datos = parsed;
                else throw new Error();
            }} catch(e) {{
                datos = JSON.parse(JSON.stringify(DATOS_INIC));
                guardarMemoria();
            }}
        }} else {{
            datos = JSON.parse(JSON.stringify(DATOS_INIC));
            guardarMemoria();
        }}
        render();
    }}

    function guardarMemoria() {{
        localStorage.setItem('pers_ts_v5', TS);
        localStorage.setItem('pers_datos_v5', JSON.stringify(datos));
    }}

    /* ── ESTADO GLOBAL (CRITICO, DOBLE...) ── */
    let estadoGlobal = {{}};

    function computarEstados() {{
        const est = {{}};
        function tramoNum(n) {{ return parseInt(n.replace('Tramo ', '')); }}

        let scanearBloque = (bloque, isCruz) => {{
            for (let turno in bloque) {{
                for (let sec of ['Delante', 'Detras']) {{
                    for (let vara in bloque[turno][sec]) {{
                        bloque[turno][sec][vara].forEach(p => {{
                            if (p.id !== -1) {{
                                if (!est[p.id]) est[p.id] = {{ nombre: p.nombre, tronoT: new Set(), cruzT: new Set(), tronoC: {{}}, cruzC: {{}}, tramos: [] }};
                                if (isCruz) {{
                                    est[p.id].cruzT.add(turno);
                                    est[p.id].cruzC[turno] = (est[p.id].cruzC[turno] || 0) + 1;
                                }} else {{
                                    est[p.id].tronoT.add(turno);
                                    est[p.id].tronoC[turno] = (est[p.id].tronoC[turno] || 0) + 1;
                                }}
                            }}
                        }});
                    }}
                }}
            }}
        }};

        scanearBloque(datos.Trono, false);
        if (LLEVA_CRUZ) scanearBloque(datos.Cruz, true);

        for (let pid in est) {{
            let e = est[pid];
            
            // Comprobar si está asignado 2 veces en el mismo turno (Duplicado)
            e.duplicado = false;
            for (let c in e.tronoC) if (e.tronoC[c] > 1) e.duplicado = true;
            for (let c in e.cruzC)  if (e.cruzC[c] > 1)  e.duplicado = true;

            // Calcular en qué tramos sale según la matriz
            let misTramos = new Set();
            e.choqueTramo = false; // Comprobar si sale de Trono y Cruz en el MISMO tramo
            
            for (let tramo in datos.Mapping) {{
                let num = tramoNum(tramo);
                let enT = e.tronoT.has(datos.Mapping[tramo].Trono);
                let enC = LLEVA_CRUZ && e.cruzT.has(datos.Mapping[tramo].Cruz);
                
                if (enT) misTramos.add(num);
                if (enC) misTramos.add(num);
                if (enT && enC) e.choqueTramo = true; // ⚠️ Rojo Crítico
            }}
            e.tramos = Array.from(misTramos).sort((a,b) => a - b);
        }}

        // Asignar colores/estados
        for (let pid in est) {{
            let e = est[pid];
            let tieneConsec = e.tramos.some((n, i) => i > 0 && n - e.tramos[i-1] === 1);

            if (e.duplicado || e.choqueTramo)        e.estadoStr = 'critico';
            else if (tieneConsec)                    e.estadoStr = 'doble';
            else if (e.tronoT.size > 0 && e.cruzT.size > 0) e.estadoStr = 'cruzYTrono';
            else if (e.tronoT.size > 1 || e.cruzT.size > 1) e.estadoStr = 'dosTurnos';
            else                                     e.estadoStr = 'normal';
        }}
        return est;
    }}

    /* ── CELDA HTML ── */
    function celdaHTML(p, tipo, turno, sec, vara, idx) {{
        const esVacio = (p.altura === 0 || p.id === -1);
        let prefLetra = '', claseEst = '', claseTxt = '', tickHombro = '';

        if (!esVacio) {{
            let pref = (p.pref_hombro || '').toLowerCase();
            if (pref.includes('derech')) {{
                prefLetra = ' <span style="color:#888;font-size:9px;">(D)</span>';
                if (vara === 'Izquierda') tickHombro = ' <span title="Hombro correcto">✅</span>';
                else if (vara === 'Derecha') tickHombro = ' <span title="Hombro incorrecto">❌</span>';
            }} else if (pref.includes('izquierd')) {{
                prefLetra = ' <span style="color:#888;font-size:9px;">(I)</span>';
                if (vara === 'Derecha') tickHombro = ' <span title="Hombro correcto">✅</span>';
                else if (vara === 'Izquierda') tickHombro = ' <span title="Hombro incorrecto">❌</span>';
            }}

            let est = estadoGlobal[p.id];
            if (est) {{
                const map = {{ critico:['estado-critico','txt-critico'], doble:['estado-doble','txt-doble'], cruzYTrono:['estado-cruzYTrono','txt-cruzYTrono'], dosTurnos:['estado-dosTurnos','txt-dosTurnos'] }};
                if (map[est.estadoStr]) {{ claseEst = map[est.estadoStr][0]; claseTxt = map[est.estadoStr][1]; }}
            }}
        }}

        const idSug = `sug-${{tipo}}-${{turno.replace(/ /g,'')}}-${{sec}}-${{vara}}-${{idx}}`;
        return `<div class="costalero ${{esVacio ? 'vacio' : claseEst}}"
                     draggable="${{!esVacio}}"
                     ondragstart="drag(event,'${{tipo}}','${{turno}}','${{sec}}','${{vara}}',${{idx}})"
                     ondragover="allow(event)"
                     ondrop="drop(event,'${{tipo}}','${{turno}}','${{sec}}','${{vara}}',${{idx}})">
            ${{esVacio ?
                `<input type="text" class="search-p" placeholder="Arrastrar o buscar..." onkeyup="buscarMini(event,'${{tipo}}','${{turno}}','${{sec}}','${{vara}}',${{idx}})">
                 <div id="${{idSug}}" class="sugerencias" style="display:none"></div>` :
                `<span>
                    <button class="btn-accion btn-del"  onclick="eliminar('${{tipo}}','${{turno}}','${{sec}}','${{vara}}',${{idx}})" title="Quitar">🗑️</button>
                    <button class="btn-accion btn-info" onclick="verHoja(${{p.id}})" title="Hoja de ruta">ℹ️</button>
                    <span class="${{claseTxt}}">${{p.nombre}}${{prefLetra}}${{tickHombro}}</span>
                 </span>
                 <span style="color:#d4af37;font-weight:bold;">${{p.altura}}cm</span>`
            }}
        </div>`;
    }}

    /* ── RENDER PRINCIPAL ── */
    function render() {{
        estadoGlobal = computarEstados();

        // 1. Mapping
        const tablaMap = document.getElementById('tabla-mapping');
        const optT = Object.keys(datos.Trono || {{}}).map(k => `<option value="${{k}}">${{k}}</option>`).join('');
        const optC = (LLEVA_CRUZ && datos.Cruz) ? Object.keys(datos.Cruz).map(k => `<option value="${{k}}">${{k}}</option>`).join('') : '';

        let hMap = `<tr><th>TRAMO</th><th>⛪ Turno Trono</th>${{LLEVA_CRUZ ? '<th>✝ Turno Cruz</th>' : ''}}</tr>`;
        for (let tr in datos.Mapping) {{
            let sT = datos.Mapping[tr].Trono;
            let sC = datos.Mapping[tr].Cruz;
            let selT = `<select onchange="cambiarMap('${{tr}}','Trono',this.value)">${{optT.replace(`value="${{sT}}"`,`value="${{sT}}" selected`)}}</select>`;
            let selC = LLEVA_CRUZ ? `<td><select onchange="cambiarMap('${{tr}}','Cruz',this.value)">${{optC.replace(`value="${{sC}}"`,`value="${{sC}}" selected`)}}</select></td>` : '';
            hMap += `<tr><td><b>${{tr}}</b></td><td>${{selT}}</td>${{selC}}</tr>`;
        }}
        tablaMap.innerHTML = hMap;

        // 2. Trono
        const appT = document.getElementById('app-trono');
        appT.innerHTML = '';
        for (let turno in datos.Trono) {{
            let sec = datos.Trono[turno];
            appT.innerHTML += `
            <div class="turno-container">
                <h3>${{turno}} <button class="btn-vacar" onclick="vaciarTurno('Trono','${{turno}}')">🗑️ Vaciar turno</button></h3>
                <div class="etiqueta-seccion">▲ DELANTE ▲</div>
                <div class="grid-trono">
                    <div class="vara"><div class="vara-titulo">IZQUIERDA</div>${{sec.Delante.Izquierda.map((p,i)=>celdaHTML(p,'Trono',turno,'Delante','Izquierda',i)).join('')}}</div>
                    <div class="vara"><div class="vara-titulo">CENTRO</div>${{sec.Delante.Centro.map((p,i)=>celdaHTML(p,'Trono',turno,'Delante','Centro',i)).join('')}}</div>
                    <div class="vara"><div class="vara-titulo">DERECHA</div>${{sec.Delante.Derecha.map((p,i)=>celdaHTML(p,'Trono',turno,'Delante','Derecha',i)).join('')}}</div>
                </div>
                <div class="etiqueta-seccion" style="margin-top:20px;">▼ DETRÁS ▼</div>
                <div class="grid-trono">
                    <div class="vara"><div class="vara-titulo">IZQUIERDA</div>${{sec.Detras.Izquierda.map((p,i)=>celdaHTML(p,'Trono',turno,'Detras','Izquierda',i)).join('')}}</div>
                    <div class="vara"><div class="vara-titulo">CENTRO</div>${{sec.Detras.Centro.map((p,i)=>celdaHTML(p,'Trono',turno,'Detras','Centro',i)).join('')}}</div>
                    <div class="vara"><div class="vara-titulo">DERECHA</div>${{sec.Detras.Derecha.map((p,i)=>celdaHTML(p,'Trono',turno,'Detras','Derecha',i)).join('')}}</div>
                </div>
            </div>`;
        }}

        // 3. Cruz
        if (LLEVA_CRUZ && datos.Cruz) {{
            const appC = document.getElementById('app-cruz');
            if (appC) {{
                appC.innerHTML = '';
                for (let turno in datos.Cruz) {{
                    let sec = datos.Cruz[turno];
                    appC.innerHTML += `
                    <div class="turno-container">
                        <h3>${{turno}} <button class="btn-vacar" onclick="vaciarTurno('Cruz','${{turno}}')">🗑️ Vaciar turno</button></h3>
                        <div class="etiqueta-seccion">▲ DELANTE ▲</div>
                        <div class="grid-cruz">
                            <div class="vara"><div class="vara-titulo">IZQUIERDA</div>${{sec.Delante.Izquierda.map((p,i)=>celdaHTML(p,'Cruz',turno,'Delante','Izquierda',i)).join('')}}</div>
                            <div class="vara"><div class="vara-titulo">DERECHA</div>${{sec.Delante.Derecha.map((p,i)=>celdaHTML(p,'Cruz',turno,'Delante','Derecha',i)).join('')}}</div>
                        </div>
                        <div class="etiqueta-seccion" style="margin-top:20px;">▼ DETRÁS ▼</div>
                        <div class="grid-cruz">
                            <div class="vara"><div class="vara-titulo">IZQUIERDA</div>${{sec.Detras.Izquierda.map((p,i)=>celdaHTML(p,'Cruz',turno,'Detras','Izquierda',i)).join('')}}</div>
                            <div class="vara"><div class="vara-titulo">DERECHA</div>${{sec.Detras.Derecha.map((p,i)=>celdaHTML(p,'Cruz',turno,'Detras','Derecha',i)).join('')}}</div>
                        </div>
                    </div>`;
                }}
            }}
        }}

        // 4. Indicaciones
        const appInd = document.getElementById('app-indicaciones');
        appInd.innerHTML = '';
        for (let tr in datos.Indicaciones) {{
            let tT = datos.Mapping[tr] ? datos.Mapping[tr].Trono : '';
            let tC = (LLEVA_CRUZ && datos.Mapping[tr]) ? datos.Mapping[tr].Cruz : '';
            let badge = `<span style="color:#a37c95; font-size:11px; margin-left:10px;">⛪ ${{tT}}${{tC ? ' · ✝ '+tC : ''}}</span>`;
            appInd.innerHTML += `
            <div class="caja-indicacion">
                <div style="color:#d4af37; font-weight:bold; margin-bottom:8px;">${{tr}} ${{badge}}</div>
                <textarea placeholder="Indicaciones para los celadores en este tramo..." onchange="guardarInd('${{tr}}',this.value)">${{datos.Indicaciones[tr]}}</textarea>
            </div>`;
        }}
    }}

    /* ── MODAL HOJA DE RUTA CON BUSCADOR ── */
    window.cerrarModalRuta = function(event) {{
        if (!event || event.target === document.getElementById('modal-ruta'))
            document.getElementById('modal-ruta').classList.remove('activo');
    }}

    window.abrirModalHojaRuta = function() {{
        document.getElementById('modal-ruta-body').innerHTML = `
            <h3 style="color:#d4af37; margin:0 0 12px;">📋 Hoja de Ruta Individual</h3>
            <input type="text" id="buscador-hoja" placeholder="🔍 Escribe el nombre del costalero..." onkeyup="buscarHojaRuta(this.value)" style="width:100%; padding:10px; border-radius:4px; border:1px solid #3d0c2e; background:#0c0209; color:#d4af37; outline:none; margin-bottom:15px; font-size:14px; box-sizing:border-box;">
            <div id="res-hoja-ruta" style="max-height: 400px; overflow-y: auto;">
                <p style="color:#a37c95; font-size:13px; line-height:1.6;">
                    Busca a un costalero para ver su itinerario completo, o pulsa el icono <b style="color:#3498db;">ℹ️</b> al lado de su nombre directamente en el cuadrante.
                </p>
            </div>`;
        document.getElementById('modal-ruta').classList.add('activo');
        setTimeout(() => document.getElementById('buscador-hoja').focus(), 100);
    }}

    window.buscarHojaRuta = function(val) {{
        val = normalizar(val);
        const resDiv = document.getElementById('res-hoja-ruta');
        if (val.length < 2) {{ resDiv.innerHTML = ''; return; }}
        
        const matches = MASTER_LIST.filter(p => normalizar(p.nombre).includes(val));
        if (matches.length === 0) {{
            resDiv.innerHTML = '<p style="color:#ff4757; font-size:12px;">No se encontraron costaleros.</p>';
            return;
        }}
        
        let html = '';
        matches.forEach(m => {{
            html += `<div style="background:#23061b; padding:10px; margin-bottom:5px; border-radius:4px; cursor:pointer; border-left:3px solid #d4af37; display:flex; justify-content:space-between;" onclick="verHoja(${{m.id}})">
                <b style="color:#e8d08c;">${{m.nombre}}</b> <span style="color:#a37c95; font-size:11px;">${{m.altura}} cm</span>
            </div>`;
        }});
        resDiv.innerHTML = html;
    }}

    window.verHoja = function(pid) {{
        let e = estadoGlobal[pid];
        let p = MASTER_LIST.find(x => x.id === pid) || {{}};
        let nombre = e ? e.nombre : (p.nombre || 'Desconocido');

        // Turnos a los que pertenece
        let turnosList = [];
        if (e) {{
           e.tronoT.forEach(t => turnosList.push(`⛪ ${{t}} (Trono)`));
           e.cruzT.forEach(t => turnosList.push(`✝ ${{t}} (Cruz)`));
        }}
        let turnosStr = turnosList.length > 0 ? turnosList.join(' &nbsp;|&nbsp; ') : '<span style="color:#ff4757;">Ninguno asignado</span>';

        // Tramos en los que sale este costalero
        let tramosInfo = [];
        for (let tr in datos.Mapping) {{
            let map = datos.Mapping[tr];
            let enTrono = e && e.tronoT.has(map.Trono);
            let enCruz  = e && LLEVA_CRUZ && e.cruzT.has(map.Cruz);
            
            if (enTrono || enCruz) {{
                let roles = [];
                if (enTrono) roles.push('⛪ Trono');
                if (enCruz)  roles.push('✝ Cruz');
                tramosInfo.push(`<li style="padding:10px; background:#23061b; margin-bottom:6px; border-radius:4px; border-left:4px solid #d4af37; color:#e8d08c; display:flex; justify-content:space-between; align-items:center;">
                    <span><b>${{tr}}</b></span><span style="color:#d4af37; font-weight:bold; font-size:13px;">${{roles.join(' + ')}}</span></li>`);
            }} else {{
                tramosInfo.push(`<li style="padding:10px; background:#160311; margin-bottom:6px; border-radius:4px; border-left:4px solid #571342; color:#888; display:flex; justify-content:space-between; align-items:center;">
                    <span>${{tr}}</span><span style="font-size:13px;">🕯️ Cirio (Descanso)</span></li>`);
            }}
        }}
        let tramosHTML = `<ul style="list-style:none; padding:0; margin:0;">${{tramosInfo.join('')}}</ul>`;

        const badges = {{
            critico:    `<span style="background:#4a0000;border:2px dashed #ff0000;color:#fff;padding:4px 12px;border-radius:4px;animation:parpadeo 1s infinite;display:inline-block; font-size:11px; font-weight:bold;">⚠️ CRÍTICO — Conflicto de turnos</span>`,
            doble:      `<span style="background:#6b0b1c;border:1px solid #ff4757;color:#ff4757;padding:4px 12px;border-radius:4px; font-size:11px; font-weight:bold;">🔴 Doble carga consecutiva</span>`,
            cruzYTrono: `<span style="background:#0a2a3d;border:1px solid #00d2ff;color:#00d2ff;padding:4px 12px;border-radius:4px; font-size:11px; font-weight:bold;">🔵 Lleva Trono y Cruz</span>`,
            dosTurnos:  `<span style="background:#2a2000;border:1px solid #ffd700;color:#ffd700;padding:4px 12px;border-radius:4px; font-size:11px; font-weight:bold;">🟡 Sale en 2 turnos</span>`,
            normal:     `<span style="color:#a37c95;font-size:12px;">✅ Carga óptima (Sin alertas)</span>`,
        }};
        let badge = e ? (badges[e.estadoStr] || '') : '';

        document.getElementById('modal-ruta-body').innerHTML = `
            <button onclick="abrirModalHojaRuta()" style="background:none; border:none; color:#d4af37; cursor:pointer; font-size:13px; margin-bottom:15px; padding:0;">← Volver al buscador</button>
            <div style="font-size:22px; font-weight:bold; color:#f8f0f5; margin-bottom:8px;">${{nombre}}</div>
            <div style="margin-bottom:18px;">${{badge}}</div>
            <div style="background:#160311; padding:12px; border-radius:6px; border-left:4px solid #d4af37; margin-bottom:18px;">
                <div style="color:#a37c95; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Asignado a</div>
                <div style="color:#e8d08c; font-weight:bold; font-size:13px;">${{turnosStr}}</div>
            </div>
            <div style="color:#a37c95; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">📍 Itinerario Completo</div>
            ${{tramosHTML}}`;
            
        document.getElementById('modal-ruta').classList.add('activo');
    }}

    /* ── ACCIONES ── */
    window.cambiarMap = function(tramo, tipo, val) {{ datos.Mapping[tramo][tipo] = val; guardarMemoria(); render(); }}
    window.guardarInd = function(tramo, val) {{ datos.Indicaciones[tramo] = val; guardarMemoria(); }}

    window.vaciarTodo = function() {{
        if (!confirm('⚠️ ¿Vaciar TODO el cuadrante?')) return;
        let limpia = (blq) => {{
            for (let t in blq) for (let s in blq[t]) for (let v in blq[t][s])
                blq[t][s][v] = blq[t][s][v].map(() => ({{ nombre:'HUECO LIBRE', altura:0, id:-1 }}));
        }};
        limpia(datos.Trono);
        if (LLEVA_CRUZ && datos.Cruz) limpia(datos.Cruz);
        render(); guardarMemoria(); if (sidebarAbierto) renderSidebar();
    }}

    window.vaciarTurno = function(tipo, turno) {{
        if (!confirm(`⚠️ ¿Vaciar ${{turno}} (${{tipo}})?`)) return;
        let blq = datos[tipo][turno];
        for (let s in blq) for (let v in blq[s])
            blq[s][v] = blq[s][v].map(() => ({{ nombre:'HUECO LIBRE', altura:0, id:-1 }}));
        render(); guardarMemoria(); if (sidebarAbierto) renderSidebar();
    }}

    window.descargarDatos = function() {{
        const dl = document.createElement('a');
        dl.setAttribute('href', 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(datos, null, 2)));
        dl.setAttribute('download', 'Cuadrante_Personalizado.json');
        document.body.appendChild(dl); dl.click(); dl.remove();
    }}

    window.eliminar = function(tipo, turno, sec, v, idx) {{
        datos[tipo][turno][sec][v][idx] = {{ nombre:'HUECO LIBRE', altura:0, id:-1 }};
        render(); guardarMemoria(); if (sidebarAbierto) renderSidebar();
    }}

    /* ── DRAG & DROP ── */
    let dragging = null;
    window.allow = function(ev) {{ ev.preventDefault(); }}
    window.drag = function(ev, tipo, turno, sec, v, idx) {{ 
        dragging = {{ source:'slot', tipo, turno, sec, v, idx }}; 
    }}
    
    window.drop = function(ev, tipo, turno, sec, v, idx) {{
        ev.preventDefault();
        if (!dragging) return;
        
        let target = datos[tipo][turno][sec][v][idx];
        
        if (dragging.source === 'sidebar') {{
            if (target.id !== -1 && !confirm(`El hueco ya está ocupado por ${{target.nombre}}. ¿Reemplazar?`)) return;
            datos[tipo][turno][sec][v][idx] = {{...dragging.persona}};
        }} else {{
            // Intercambio
            let orig = datos[dragging.tipo][dragging.turno][dragging.sec][dragging.v][dragging.idx];
            datos[dragging.tipo][dragging.turno][dragging.sec][dragging.v][dragging.idx] = target;
            datos[tipo][turno][sec][v][idx] = orig;
        }}
        render(); guardarMemoria(); if (sidebarAbierto) renderSidebar();
        dragging = null; // Reiniciar
    }}

    /* ── SIDEBAR ── */
    let sidebarAbierto = false;
    window.toggleSidebar = function() {{
        sidebarAbierto = !sidebarAbierto;
        document.getElementById('sidebar').classList.toggle('abierto', sidebarAbierto);
        document.getElementById('sidebar-toggle').classList.toggle('abierto', sidebarAbierto);
        document.getElementById('sidebar-toggle').textContent = sidebarAbierto ? '✕ CERRAR' : '👥 CENSO';
        if (sidebarAbierto) renderSidebar();
    }}

    function normalizar(s) {{ return s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase(); }}

    function getIdsAsig() {{
        const ids = new Set();
        let scan = (blq) => {{ for(let t in blq) for(let s in blq[t]) for(let v in blq[t][s]) blq[t][s][v].forEach(p => {{ if(p.id !== -1) ids.add(p.id); }}); }};
        if (datos && datos.Trono) scan(datos.Trono);
        if (LLEVA_CRUZ && datos && datos.Cruz) scan(datos.Cruz);
        return ids;
    }}

    window.renderSidebar = function() {{
        const val = normalizar(document.getElementById('sidebar-search').value.trim());
        const asig = getIdsAsig();
        let lista = val
            ? MASTER_LIST.filter(p => normalizar(p.nombre).includes(val) || (p.altura && p.altura.toString().includes(val)))
            : [...MASTER_LIST];
        lista.sort((a,b) => {{ let aA=asig.has(a.id), bA=asig.has(b.id); return aA!==bA ? (aA?1:-1) : b.altura-a.altura; }});
        const div = document.getElementById('sidebar-lista');
        div.innerHTML = '';
        lista.forEach(p => {{
            let ya = asig.has(p.id);
            let pref = (p.pref_hombro||'').toLowerCase();
            let pt = pref.includes('derech') ? ' <span style="color:#888;">(D)</span>' : pref.includes('izquierd') ? ' <span style="color:#888;">(I)</span>' : '';
            let item = document.createElement('div');
            item.className = 'sidebar-item' + (ya ? ' ya-asignado' : '');
            item.draggable = true;
            item.innerHTML = `<span>${{p.nombre}}${{pt}}</span><span style="color:#d4af37;">${{p.altura}}cm</span>`;
            item.ondragstart = () => {{ dragging = {{ source:'sidebar', persona:{{...p}} }}; }};
            div.appendChild(item);
        }});
        document.getElementById('sidebar-contador').textContent = `${{asig.size}} asignados`;
    }}

    /* ── MINI BUSCADOR EN HUECOS ── */
    window.buscarMini = function(ev, tipo, turno, sec, v, idx) {{
        const val = normalizar(ev.target.value.trim());
        const idSug = `sug-${{tipo}}-${{turno.replace(/ /g,'')}}-${{sec}}-${{v}}-${{idx}}`;
        const sug = document.getElementById(idSug);
        if (!sug) return;
        if (val.length < 2) {{ sug.style.display='none'; return; }}
        const matches = MASTER_LIST.filter(p => normalizar(p.nombre).includes(val) || (p.altura && p.altura.toString().includes(val))).slice(0,6);
        sug.innerHTML = '';
        if (matches.length > 0) {{
            sug.style.display = 'block';
            matches.forEach(m => {{
                let d = document.createElement('div');
                d.className = 'sug-item';
                d.textContent = `${{m.nombre}} (${{m.altura}}cm)`;
                d.onclick = () => {{ datos[tipo][turno][sec][v][idx] = {{...m}}; render(); guardarMemoria(); if(sidebarAbierto) renderSidebar(); }};
                sug.appendChild(d);
            }});
        }} else sug.style.display = 'none';
    }}

    window.onload = init;
</script>
</body>
</html>"""

    with open("visualizador_personalizado.html", "w", encoding="utf-8") as f:
        f.write(html)