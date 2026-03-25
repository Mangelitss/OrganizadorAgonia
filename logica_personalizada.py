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
            "Delante": {v: [{"nombre": "HUECO LIBRE", "altura": 0, "id": -1, "bloqueado": False} for _ in range(plazas_por_vara)] for v in varas_trono},
            "Detras": {v: [{"nombre": "HUECO LIBRE", "altura": 0, "id": -1, "bloqueado": False} for _ in range(plazas_por_vara)] for v in varas_trono}
        }
        
    # CRUZ: 2 varas delante, 2 varas detrás. Siempre 2 costaleros por vara.
    varas_cruz = ["Izquierda", "Derecha"]
    cruz = {}
    
    if lleva_cruz:
        for i in range(num_turnos_cruz):
            nombre_turno = f"Turno {i+1}"
            cruz[nombre_turno] = {
                "Delante": {v: [{"nombre": "HUECO LIBRE", "altura": 0, "id": -1, "bloqueado": False} for _ in range(2)] for v in varas_cruz},
                "Detras": {v: [{"nombre": "HUECO LIBRE", "altura": 0, "id": -1, "bloqueado": False} for _ in range(2)] for v in varas_cruz}
            }

    # MAPPING (Matriz inicial de Tramos y a qué Turno apuntan)
    mapping = {}
    for i in range(num_tramos):
        tramo_name = f"Tramo {i+1}"
        t_trono = f"Turno {letras[i % num_turnos_trono]}" if num_turnos_trono > 0 else ""
        t_cruz = f"Turno {(i % num_turnos_cruz) + 1}" if (lleva_cruz and num_turnos_cruz > 0) else ""
        
        mapping[tramo_name] = {
            "Ruta": "",
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
        .tabla-relevos th {{ background:#23061b; color:#d4af37; padding:12px; border-bottom:2px solid #3d0c2e; font-size:13px; text-transform: uppercase; }}
        .tabla-relevos td {{ padding:10px; border-bottom:1px solid #3d0c2e; text-align:center; }}
        .tabla-relevos select {{ background:#0c0209; color:#e8d08c; border:1px solid #3d0c2e; padding:6px; border-radius:4px; font-weight:bold; outline:none; width: 100%; }}
        
        .titulo-bloque {{ background:#23061b; padding:15px; border-left:5px solid #d4af37; margin:40px 0 20px; }}
        .titulo-bloque h2 {{ color:#d4af37; margin:0; font-size:20px; letter-spacing:2px; }}
        
        .turno-container {{ background:#1a0514; padding:20px; margin-bottom:30px; border-radius:10px; border:1px solid #3d0c2e; }}
        .turno-container h3 {{ color:#e8d08c; margin-top:0; font-size:16px; border-bottom:1px dashed #4a1038; padding-bottom:10px; display:flex; justify-content:space-between; align-items:center; }}
        
        .grid-trono {{ display:grid; grid-template-columns:repeat(3,1fr); gap:15px; }}
        .grid-cruz  {{ display:grid; grid-template-columns:repeat(2,1fr); gap:15px; }}
        .vara {{ background:#160311; padding:10px; border-radius:8px; border-top:3px solid #571342; }}
        .vara-titulo {{ text-align:center; color:#a37c95; font-size:14px; margin-bottom:10px; font-weight:bold; text-transform:uppercase; border-bottom: 1px solid #3d0c2e; padding-bottom: 5px; }}
        
        .sep-delante {{ font-size: 10px; color: #d4af37; text-align: center; margin: 10px 0 5px 0; font-weight: bold; letter-spacing: 1px; }}
        .sep-mid {{ font-size: 11px; color: #fff; text-align: center; margin: 10px 0; font-weight: bold; background: #5c164e; padding: 5px; border-radius: 3px; letter-spacing: 2px; box-shadow: 0 2px 4px rgba(0,0,0,0.5); }}
        .sep-detras {{ font-size: 10px; color: #d4af37; text-align: center; margin: 5px 0 10px 0; font-weight: bold; letter-spacing: 1px; }}
        
        .costalero {{ background:#3d0c2e; border:1px solid #571342; margin:5px 0; padding:8px; border-radius:4px; cursor:grab; display:flex; justify-content:space-between; align-items:center; font-size:11px; transition:.3s; text-shadow:1px 1px 2px rgba(0,0,0,.8); position:relative; }}
        .costalero:active {{ cursor:grabbing; }}
        .costalero.vacio {{ border:1px dashed #571342; background:#0c0209; color:#884d72; flex-direction:column; align-items:stretch; text-shadow:none; overflow:visible; }}
        
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
        
        .btn-vacar {{ background:transparent; border:1px solid #b30000; color:#ff6b81; padding:4px 10px; border-radius:4px; cursor:pointer; font-size:11px; font-weight:bold; transition: 0.2s; }}
        .btn-vacar:hover {{ background:#b30000; color:#fff; }}
        
        /* BOTONES COPIAR PEGAR Y BLOQUEAR */
        .btn-copiar {{ background:transparent; border:1px solid #3498db; color:#3498db; padding:4px 10px; border-radius:4px; cursor:pointer; font-size:11px; font-weight:bold; transition: 0.2s; }}
        .btn-copiar:hover {{ background:#3498db; color:#fff; }}
        
        .btn-pegar {{ background:transparent; border:1px solid #27ae60; color:#27ae60; padding:4px 10px; border-radius:4px; cursor:not-allowed; font-size:11px; font-weight:bold; opacity: 0.4; transition: 0.2s; }}
        .btn-pegar.activo {{ opacity: 1; cursor: pointer; animation: pulseVerde 2s infinite; }}
        .btn-pegar.activo:hover {{ background:#27ae60; color:#fff; }}
        @keyframes pulseVerde {{ 0% {{ box-shadow:0 0 0 0 rgba(39,174,96,0.6); }} 70% {{ box-shadow:0 0 0 6px rgba(39,174,96,0); }} 100% {{ box-shadow:0 0 0 0 rgba(39,174,96,0); }} }}

        .btn-lock-turn {{ background:transparent; border:1px solid #e8d08c; color:#e8d08c; padding:4px 10px; border-radius:4px; cursor:pointer; font-size:11px; font-weight:bold; transition: 0.2s; }}
        .btn-lock-turn:hover {{ background:#e8d08c; color:#0c0209; }}
        
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
            <input type="file" id="file-input" accept=".json" style="display: none;" onchange="cargarJSON(event)">
            <button class="btn-control btn-danger" onclick="vaciarTodo()">🗑️ VACIAR TODO</button>
            <button class="btn-control" onclick="abrirModalHojaRuta()">📋 RUTA DE COSTALERO</button>
            <button class="btn-control" onclick="document.getElementById('file-input').click()">📂 CARGAR</button>
            <button class="btn-control btn-export" onclick="descargarDatos()">💾 JSON</button>
            <button class="btn-control" style="background:#5c164e; border-color:#d4af37;" onclick="exportarPDF()">📤 EXPORTAR A PDF</button>
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
            <div class="ley-item"><div class="ley-dot" style="background:#4a0000; border:2px dashed #ff0000;"></div><span style="color:#ff0000;">⚠️ CRÍTICO: 2 posiciones o Cruz/Trono en mismo tramo</span></div>
        </div>
    </div>

<script>
    const TS          = "{marca_tiempo}";
    const DATOS_INIC  = {datos_json};
    const MASTER_LIST = {master_json};
    const LLEVA_CRUZ  = {str(lleva_cruz).lower()};
    let datos = {{}};
    let portapapeles = null; 

    /* ── INIT ── */
    function init() {{
        let savedTs   = localStorage.getItem('pers_ts_v12');
        let savedData = localStorage.getItem('pers_datos_v12');
        
        if (savedData && savedTs === TS) {{
            try {{
                let parsed = JSON.parse(savedData);
                if (parsed.Trono) {{
                    datos = parsed;
                }} else {{
                    throw new Error("Estructura corrupta");
                }}
            }} catch(e) {{
                datos = JSON.parse(JSON.stringify(DATOS_INIC));
                localStorage.setItem('pers_ts_v12', TS);
                localStorage.setItem('pers_datos_v12', JSON.stringify(datos));
            }}
        }} else {{
            datos = JSON.parse(JSON.stringify(DATOS_INIC));
            localStorage.setItem('pers_ts_v12', TS);
            localStorage.setItem('pers_datos_v12', JSON.stringify(datos));
        }}
        render();
    }}

    function guardarMemoria() {{
        localStorage.setItem('pers_datos_v12', JSON.stringify(datos));
    }}

    /* ── CARGAR JSON ── */
    window.cargarJSON = function(event) {{
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(e) {{
            try {{
                let loaded = JSON.parse(e.target.result);
                if (loaded.Trono && loaded.Mapping) {{
                    datos = loaded;
                    guardarMemoria();
                    render();
                    if (sidebarAbierto) renderSidebar();
                    alert("✅ Cuadrante cargado correctamente.");
                }} else {{
                    alert("❌ El archivo JSON no tiene la estructura correcta para esta procesión personalizada.");
                }}
            }} catch(err) {{
                alert("❌ Error al leer el archivo JSON.");
            }}
        }};
        reader.readAsText(file);
        event.target.value = '';
    }};

    /* ── COPIAR Y PEGAR TURNO ── */
    window.copiarTurno = function(tipo, turno) {{
        portapapeles = {{
            tipo: tipo,
            datos: JSON.parse(JSON.stringify(datos[tipo][turno]))
        }};
        
        let toast = document.createElement('div');
        toast.textContent = `📋 ${{turno}} de ${{tipo}} copiado al portapapeles`;
        toast.style.cssText = "position:fixed; bottom:30px; left:50%; transform:translateX(-50%); background:#27ae60; color:#fff; padding:12px 24px; border-radius:30px; font-weight:bold; box-shadow:0 4px 10px rgba(0,0,0,0.5); z-index:9999;";
        document.body.appendChild(toast);
        setTimeout(() => document.body.removeChild(toast), 3000);
        
        render(); 
    }};

    window.pegarTurno = function(tipo, turno) {{
        if (!portapapeles || portapapeles.tipo !== tipo) return;
        
        if (confirm(`⚠️ Vas a SOBREESCRIBIR por completo el ${{turno}} de ${{tipo}} con los datos copiados.\n\n(Se respetarán y copiarán los candados exactamente igual que en el original).\n\n¿Estás seguro?`)) {{
            datos[tipo][turno] = JSON.parse(JSON.stringify(portapapeles.datos));
            guardarMemoria();
            render();
            if (sidebarAbierto) renderSidebar();
        }}
    }};

    /* ── BLOQUEO MASIVO INTELIGENTE ── */
    window.toggleLockTurno = function(tipo, turno) {{
        let blq = datos[tipo][turno];
        
        // 1. Comprobar si están TODOS bloqueados
        let todosBloqueados = true;
        for (let s in blq) {{
            for (let v in blq[s]) {{
                blq[s][v].forEach(p => {{
                    if (!p.bloqueado) todosBloqueados = false;
                }});
            }}
        }}
        
        // 2. Si todos están bloqueados -> Soltar todos. Si falta alguno -> Bloquear todos.
        let nuevoEstado = !todosBloqueados;
        
        for (let s in blq) {{
            for (let v in blq[s]) {{
                blq[s][v].forEach(p => {{
                    p.bloqueado = nuevoEstado;
                }});
            }}
        }}
        
        guardarMemoria();
        render();
    }};

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
            e.choqueTramo = false; 
            
            for (let tramo in datos.Mapping) {{
                let num = tramoNum(tramo);
                let enT = e.tronoT.has(datos.Mapping[tramo].Trono);
                let enC = LLEVA_CRUZ && e.cruzT.has(datos.Mapping[tramo].Cruz);
                
                if (enT) misTramos.add(num);
                if (enC) misTramos.add(num);
                if (enT && enC) e.choqueTramo = true; // ⚠️ Rojo Crítico
            }}
            e.tramos = Array.from(misTramos).sort((a,b) => a - b);
            
            // Para poder exportar correctamente a JSON los Sets
            e.tronoArr = Array.from(e.tronoT);
            e.cruzArr = Array.from(e.cruzT);
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
        let isLocked = p.bloqueado || false;

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
        let dragAttr = isLocked ? 'false' : (!esVacio).toString();
        let lockBtn = `<button class="btn-accion" onclick="toggleLock('${{tipo}}','${{turno}}','${{sec}}','${{vara}}',${{idx}})" title="Bloquear / Desbloquear hueco">${{isLocked ? '🔒' : '🔓'}}</button>`;

        return `<div class="costalero ${{esVacio ? 'vacio' : claseEst}}" ${{isLocked ? 'style="border-color:#d4af37; background:#1a0514;"' : ''}}
                     draggable="${{dragAttr}}"
                     ondragstart="drag(event,'${{tipo}}','${{turno}}','${{sec}}','${{vara}}',${{idx}})"
                     ondragover="allow(event)"
                     ondrop="drop(event,'${{tipo}}','${{turno}}','${{sec}}','${{vara}}',${{idx}})">
            ${{esVacio ?
                `<div style="display:flex; width:100%; gap:5px;">
                    <input type="text" class="search-p" placeholder="Arrastrar o buscar..." onkeyup="buscarMini(event,'${{tipo}}','${{turno}}','${{sec}}','${{vara}}',${{idx}})" ${{isLocked ? 'disabled' : ''}}>
                    ${{lockBtn}}
                 </div>
                 <div id="${{idSug}}" class="sugerencias" style="display:none"></div>` :
                `<span>
                    <button class="btn-accion btn-del"  onclick="eliminar('${{tipo}}','${{turno}}','${{sec}}','${{vara}}',${{idx}})" title="Quitar">🗑️</button>
                    <button class="btn-accion btn-info" onclick="verHoja(${{p.id}})" title="Hoja de ruta">ℹ️</button>
                    ${{lockBtn}}
                    <span class="${{claseTxt}}">${{p.nombre}}${{prefLetra}}${{tickHombro}}</span>
                 </span>
                 <span style="color:#d4af37;font-weight:bold;">${{p.altura}}cm</span>`
            }}
        </div>`;
    }}

    /* ── RENDER PRINCIPAL ── */
    window.cambiarMap = function(tramo, tipo, val) {{ datos.Mapping[tramo][tipo] = val; guardarMemoria(); render(); }}
    window.cambiarRuta = function(tramo, val) {{ datos.Mapping[tramo].Ruta = val; guardarMemoria(); }}

    function render() {{
        estadoGlobal = computarEstados();

        // 1. Mapping
        const tablaMap = document.getElementById('tabla-mapping');
        const optT = Object.keys(datos.Trono || {{}}).map(k => `<option value="${{k}}">${{k}}</option>`).join('');
        const optC = (LLEVA_CRUZ && datos.Cruz) ? Object.keys(datos.Cruz).map(k => `<option value="${{k}}">${{k}}</option>`).join('') : '';

        let hMap = `<tr><th style="width:90px;">TRAMO</th><th>📍 RECORRIDO (Opcional)</th><th>⛪ Turno Trono</th>${{LLEVA_CRUZ ? '<th>✝ Turno Cruz</th>' : ''}}</tr>`;
        for (let tr in datos.Mapping) {{
            let sT = datos.Mapping[tr].Trono;
            let sC = datos.Mapping[tr].Cruz;
            let sR = datos.Mapping[tr].Ruta || '';
            
            let inpR = `<input type="text" value="${{sR}}" placeholder="Ej: De San Francisco a Catedral..." oninput="cambiarRuta('${{tr}}', this.value)" style="width:95%; background:#0c0209; border:1px solid #3d0c2e; color:#e8d08c; padding:6px; border-radius:4px; font-size:12px; outline:none;">`;
            let selT = `<select onchange="cambiarMap('${{tr}}','Trono',this.value)">${{optT.replace(`value="${{sT}}"`,`value="${{sT}}" selected`)}}</select>`;
            let selC = LLEVA_CRUZ ? `<td><select onchange="cambiarMap('${{tr}}','Cruz',this.value)">${{optC.replace(`value="${{sC}}"`,`value="${{sC}}" selected`)}}</select></td>` : '';
            
            hMap += `<tr><td><b>${{tr}}</b></td><td>${{inpR}}</td><td>${{selT}}</td>${{selC}}</tr>`;
        }}
        tablaMap.innerHTML = hMap;

        // GENERAR BOTONES DE CONTROL DE TURNO (Copia, Pega, Bloqueo, Vaciar)
        let btnsControl = (tipo, turno) => {{
            let activo = (portapapeles && portapapeles.tipo === tipo) ? 'activo' : '';
            let disabled = (portapapeles && portapapeles.tipo === tipo) ? '' : 'disabled';
            
            // Analizar si están todos bloqueados para cambiar el botón
            let blq = datos[tipo][turno];
            let todosBloqueados = true;
            for (let s in blq) {{
                for (let v in blq[s]) {{
                    blq[s][v].forEach(p => {{ if (!p.bloqueado) todosBloqueados = false; }});
                }}
            }}
            let txtLock = todosBloqueados ? '🔓 Soltar Turno' : '🔒 Fijar Turno';
            
            return `
            <div style="display:flex; gap:8px;">
                <button class="btn-copiar" onclick="copiarTurno('${{tipo}}','${{turno}}')" title="Copiar este turno">📄 Copiar</button>
                <button class="btn-pegar ${{activo}}" onclick="pegarTurno('${{tipo}}','${{turno}}')" title="Pegar datos" ${{disabled}}>📋 Pegar</button>
                <button class="btn-lock-turn" onclick="toggleLockTurno('${{tipo}}','${{turno}}')">${{txtLock}}</button>
                <button class="btn-vacar" onclick="vaciarTurno('${{tipo}}','${{turno}}')" title="Vacía solo los huecos que NO tienen candado">🗑️ Vaciar</button>
            </div>`;
        }};

        // 2. Trono
        const appT = document.getElementById('app-trono');
        appT.innerHTML = '';
        for (let turno in datos.Trono) {{
            let sec = datos.Trono[turno];
            let listV = ['Izquierda', 'Centro', 'Derecha'].map(vara => `
                <div class="varal">
                    <div class="vara-titulo">${{vara}}</div>
                    <div class="sep-delante">▲ DELANTE ▲</div>
                    ${{sec.Delante[vara].map((p,i)=>celdaHTML(p,'Trono',turno,'Delante',vara,i)).join('')}}
                    <div class="sep-mid">CRISTO</div>
                    ${{sec.Detras[vara].map((p,i)=>celdaHTML(p,'Trono',turno,'Detras',vara,i)).join('')}}
                    <div class="sep-detras">▼ DETRÁS ▼</div>
                </div>
            `).join('');

            appT.innerHTML += `
            <div class="turno-container">
                <h3>${{turno}} ${{btnsControl('Trono', turno)}}</h3>
                <div class="grid-trono">
                    ${{listV}}
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
                    let listV = ['Izquierda', 'Derecha'].map(vara => `
                        <div class="varal">
                            <div class="vara-titulo">${{vara}}</div>
                            <div class="sep-delante">▲ DELANTE ▲</div>
                            ${{sec.Delante[vara].map((p,i)=>celdaHTML(p,'Cruz',turno,'Delante',vara,i)).join('')}}
                            <div class="sep-mid">CRUZ</div>
                            ${{sec.Detras[vara].map((p,i)=>celdaHTML(p,'Cruz',turno,'Detras',vara,i)).join('')}}
                            <div class="sep-detras">▼ DETRÁS ▼</div>
                        </div>
                    `).join('');

                    appC.innerHTML += `
                    <div class="turno-container">
                        <h3>${{turno}} ${{btnsControl('Cruz', turno)}}</h3>
                        <div class="grid-cruz">
                            ${{listV}}
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
           e.tronoArr.forEach(t => turnosList.push(`⛪ ${{t}} (Trono)`));
           e.cruzArr.forEach(t => turnosList.push(`✝ ${{t}} (Cruz)`));
        }}
        let turnosStr = turnosList.length > 0 ? turnosList.join(' &nbsp;|&nbsp; ') : '<span style="color:#ff4757;">Ninguno asignado</span>';

        // Tramos en los que sale este costalero
        let tramosInfo = [];
        for (let tr in datos.Mapping) {{
            let map = datos.Mapping[tr];
            let enTrono = e && e.tronoArr.includes(map.Trono);
            let enCruz  = e && LLEVA_CRUZ && e.cruzArr.includes(map.Cruz);
            
            // Si el tramo tiene nombre de ruta en el JSON
            let trLabel = `<b>${{tr}}</b>${{map.Ruta ? `<br><span style="font-size:10px;color:#a37c95;font-weight:normal;">${{map.Ruta}}</span>` : ''}}`;

            if (enTrono || enCruz) {{
                let roles = [];
                if (enTrono) roles.push('⛪ Trono');
                if (enCruz)  roles.push('✝ Cruz');
                tramosInfo.push(`<li style="padding:10px; background:#23061b; margin-bottom:6px; border-radius:4px; border-left:4px solid #d4af37; color:#e8d08c; display:flex; justify-content:space-between; align-items:center;">
                    <span>${{trLabel}}</span><span style="color:#d4af37; font-weight:bold; font-size:13px; text-align:right;">${{roles.join(' + ')}}</span></li>`);
            }} else {{
                tramosInfo.push(`<li style="padding:10px; background:#160311; margin-bottom:6px; border-radius:4px; border-left:4px solid #571342; color:#888; display:flex; justify-content:space-between; align-items:center;">
                    <span>${{trLabel}}</span><span style="font-size:13px;">🕯️ Cirio (Descanso)</span></li>`);
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
    window.guardarInd = function(tramo, val) {{ datos.Indicaciones[tramo] = val; guardarMemoria(); }}
    window.toggleLock = function(tipo, turno, sec, vara, idx) {{ 
        datos[tipo][turno][sec][vara][idx].bloqueado = !datos[tipo][turno][sec][vara][idx].bloqueado; 
        guardarMemoria(); render(); 
    }}

    window.vaciarTodo = function() {{
        if (!confirm(`⚠️ ¿Vaciar TODO el cuadrante? \n\n(Se respetarán todos los huecos bloqueados 🔒)`)) return;
        let limpia = (blq) => {{
            for (let t in blq) for (let s in blq[t]) for (let v in blq[t][s])
                blq[t][s][v] = blq[t][s][v].map(p => p.bloqueado ? p : ({{ nombre:'HUECO LIBRE', altura:0, id:-1, bloqueado:false }}));
        }};
        limpia(datos.Trono);
        if (LLEVA_CRUZ && datos.Cruz) limpia(datos.Cruz);
        render(); guardarMemoria(); if (sidebarAbierto) renderSidebar();
    }}

    window.vaciarTurno = function(tipo, turno) {{
        if (!confirm(`⚠️ ¿Vaciar el ${{turno}} de ${{tipo}}?\n\n(Se respetarán todos los huecos bloqueados 🔒)`)) return;
        let blq = datos[tipo][turno];
        for (let s in blq) for (let v in blq[s])
            blq[s][v] = blq[s][v].map(p => p.bloqueado ? p : ({{ nombre:'HUECO LIBRE', altura:0, id:-1, bloqueado:false }}));
        render(); guardarMemoria(); if (sidebarAbierto) renderSidebar();
    }}

    window.descargarDatos = function() {{
        const dl = document.createElement('a');
        dl.setAttribute('href', 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(datos, null, 2)));
        dl.setAttribute('download', 'Cuadrante_Personalizado.json');
        document.body.appendChild(dl); dl.click(); dl.remove();
    }}

    window.eliminar = function(tipo, turno, sec, v, idx) {{
        if (datos[tipo][turno][sec][v][idx].bloqueado) {{
            alert("🔒 Desbloquea la posición primero para poder eliminarla.");
            return;
        }}
        datos[tipo][turno][sec][v][idx] = {{ nombre:'HUECO LIBRE', altura:0, id:-1, bloqueado:false }};
        render(); guardarMemoria(); if (sidebarAbierto) renderSidebar();
    }}

    /* ── EXPORTAR A PDF (INFORME OFICIAL) ── */
    window.exportarPDF = function() {{
        window.exportDataForPDF = {{ estadoGlobal: estadoGlobal, datos: datos, lleva_cruz: LLEVA_CRUZ, master: MASTER_LIST }};
        
        let anio = new Date().getFullYear();
        let fecha_hoy = new Date().toLocaleDateString('es-ES');
        
        let html_pdf = `<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Informe Oficial - Personalizada ${{anio}}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=Open+Sans:wght@400;600;800&display=swap');
        body {{ font-family: 'Open Sans', Arial, sans-serif; background: #f4f6f8; color: #333; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #fff; padding: 40px; box-shadow: 0 0 15px rgba(0,0,0,0.1); border-top: 8px solid #5c164e; position: relative; }}
        .web-controls {{ display: flex; flex-direction: column; align-items: center; gap: 15px; margin-bottom: 30px; background: #1a0514; padding: 20px; border-radius: 8px; border: 1px solid #d4af37; }}
        .buscador-box {{ width: 100%; max-width: 600px; text-align: center; }}
        .buscador-box input {{ width: 100%; padding: 12px; font-size: 16px; background: #0c0209; color: #d4af37; border: 1px solid #3d0c2e; border-radius: 5px; outline: none; }}
        .itinerario-result {{ margin-top: 15px; padding: 15px; background: #23061b; border-radius: 5px; border-left: 5px solid #d4af37; display: none; color: #f8f0f5; text-align: left; }}
        .itinerario-result ul {{ list-style: none; padding: 0; margin: 0; }}
        .itinerario-result li {{ padding: 8px 0; border-bottom: 1px dashed #3d0c2e; font-size: 13px; display: flex; justify-content:space-between; }}
        .tramo-label {{ width: 220px; color: #a37c95; flex-shrink: 0; }}
        .btn-pdf {{ background: #5c164e; color: #fff; text-align: center; padding: 12px 25px; border-radius: 5px; font-weight: bold; cursor: pointer; border: none; font-size: 14px; text-transform: uppercase; box-shadow: 0 4px 6px rgba(92, 22, 78, 0.3); transition: 0.3s; width: 100%; max-width: 350px; }}
        .btn-pdf:hover {{ background: #7a1b67; transform: translateY(-2px); }}
        .header {{ text-align: center; border-bottom: 2px solid #e0e0e0; padding-bottom: 20px; margin-bottom: 20px; }}
        .logo-img {{ width: 100px; height: auto; margin-bottom: 10px; }}
        .header h1 {{ color: #4a148c; margin: 0; font-size: 20px; text-transform: uppercase; letter-spacing: 1px; font-family: 'Cinzel', serif; font-weight: 600; }}
        .header h2 {{ color: #b5952f; margin: 5px 0; font-size: 16px; text-transform: uppercase; letter-spacing: 2px; }}
        .sello-anio {{ position: absolute; top: 30px; right: 40px; background: #5c164e; color: #fff; padding: 8px 15px; font-size: 16px; font-weight: bold; border-radius: 5px; letter-spacing: 2px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        .leyenda {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; font-size: 11px; font-weight: bold; background: #fafafa; padding: 10px; border-radius: 5px; border: 1px solid #eee; flex-wrap: wrap; }}
        .leyenda-item {{ display: flex; align-items: center; gap: 5px; }}
        .caja {{ width: 12px; height: 12px; border-radius: 3px; display: inline-block; border: 1px solid rgba(0,0,0,0.2); }}
        .turno-box {{ border: 1px solid #d4af37; border-radius: 8px; margin-bottom: 30px; overflow: hidden; page-break-inside: avoid; }}
        .turno-title {{ background: #5c164e; color: #fff; padding: 10px 15px; margin: 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; text-align: center; }}
        .grid-varales {{ display: flex; width: 100%; }}
        .varal {{ flex: 1; padding: 10px; border-right: 1px solid #eee; }}
        .varal:last-child {{ border-right: none; }}
        .varal-title {{ text-align: center; color: #5c164e; border-bottom: 2px solid #d4af37; padding-bottom: 5px; margin-top: 0; font-size: 12px; font-weight: 800; text-transform: uppercase; }}
        .seccion-top {{ font-size: 10px; color: #5c164e; text-align: center; margin: 10px 0 5px 0; font-weight: bold; background: #eee; padding: 4px; border-radius: 3px; letter-spacing: 1px; }}
        .seccion-mid {{ font-size: 10px; color: #fff; text-align: center; margin: 8px 0; font-weight: bold; background: #5c164e; padding: 4px; border-radius: 3px; letter-spacing: 2px; }}
        .seccion-bot {{ font-size: 10px; color: #5c164e; text-align: center; margin: 5px 0 10px 0; font-weight: bold; background: #eee; padding: 4px; border-radius: 3px; letter-spacing: 1px; }}
        .lista-costaleros {{ list-style: none; padding: 0; margin: 0; font-size: 11px; }}
        .costalero-cell {{ padding: 5px 8px; margin-bottom: 3px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #ddd; background: #fff; }}
        .hueco-libre {{ padding: 5px 8px; margin-bottom: 3px; border-radius: 4px; display: flex; justify-content: center; align-items: center; border: 1px dashed #ccc; background: #fafafa; color: #aaa; font-style: italic; }}
        .bg-amarillo {{ background-color: #fff9c4 !important; border-color: #fbc02d !important; color: #000 !important; }}
        .bg-azul {{ background-color: #e1f5fe !important; border-color: #4fc3f7 !important; color: #000 !important; }}
        .bg-rojo {{ background-color: #ffebee !important; border-color: #ef9a9a !important; color: #000 !important; }}
        .c-info {{ display: flex; align-items: center; gap: 5px; }}
        .nombre {{ font-weight: 600; font-size: 11px; }}
        .meta {{ font-size: 9px; opacity: 0.7; font-weight: bold; }}
        .seccion-texto {{ background: #fafafa; padding: 20px; border-radius: 8px; border-left: 4px solid #5c164e; margin-bottom: 20px; page-break-inside: avoid; }}
        .seccion-texto h3 {{ color: #5c164e; margin-top: 0; border-bottom: 1px solid #ccc; padding-bottom: 5px; font-size: 16px; text-transform: uppercase; }}
        .lista-tramos {{ font-size: 12px; color: #444; line-height: 1.6; margin: 0; padding-left: 20px; }}
        @media print {{
            @page {{ margin: 0; }}
            body {{ background: #fff !important; padding: 1.5cm !important; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important; }}
            .no-print, .web-controls {{ display: none !important; }}
            .container {{ box-shadow: none !important; border-top: none !important; padding: 0 !important; max-width: 100% !important; }}
            .turno-box {{ border: 1px solid #000 !important; page-break-inside: avoid !important; margin-bottom: 20px !important; }}
            .turno-title {{ background: #eee !important; color: #000 !important; border-bottom: 1px solid #000 !important; }}
            .seccion-texto {{ background: transparent !important; border: 1px solid #ccc !important; border-left: 4px solid #5c164e !important; }}
            .page-break-avoid {{ page-break-inside: avoid !important; }}
            * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        }}
    </style>
</head>
<body>
    <div class="web-controls no-print">
        <button class="btn-pdf" onclick="window.print()">🖨️ IMPRIMIR / GUARDAR PDF</button>
        <p style="color:#d4af37; font-size:12px; margin-top:-5px;">*En la ventana de impresión, selecciona "Guardar como PDF"</p>
        
        <div class="buscador-box">
            <h3 style="margin-top:0; color:#d4af37;">🔍 BUSCADOR DE COSTALERO</h3>
            <input type="text" id="input-buscador" placeholder="Escribe un nombre..." onkeyup="actualizarBuscador()">
            <div id="resultado-itinerario" class="itinerario-result"></div>
        </div>
    </div>
    
    <div class="container" id="informe-content">
        <div class="sello-anio no-print">AÑO ${{anio}}</div>
        <div class="header">
            <img src="bandera_tercio_npj.png" alt="Escudo" class="logo-img" onerror="this.style.display='none'">
            <h1>OFS Muy Ilustre Mayordomía de Nuestro Padre Jesús Nazareno</h1>
            <h2>Orden Procesional - Personalizada</h2>
            <p>Fecha de emisión: ${{fecha_hoy}} | Cuadrante del Año: ${{anio}}</p>
        </div>
        
        <div class="leyenda">
            <div class="leyenda-item"><span class="caja bg-amarillo"></span> Sale en 2 Turnos</div>
            <div class="leyenda-item"><span class="caja bg-azul"></span> Lleva Trono y Cruz</div>
            <div class="leyenda-item"><span class="caja bg-rojo"></span> Alerta Carga (Dobles/Crítico)</div>
        </div>
        
        <div id="content-turnos"></div>
    </div>

    <script>
        const estadoGlobal = window.opener.exportDataForPDF.estadoGlobal;
        const datosExport = window.opener.exportDataForPDF.datos;
        const LLEVA_CRUZ = window.opener.exportDataForPDF.lleva_cruz;
        const MASTER_LIST = window.opener.exportDataForPDF.master;
        
        function normalizar(s) {{ return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase(); }}
        
        function actualizarBuscador() {{
            const val = normalizar(document.getElementById('input-buscador').value.trim());
            const resDiv = document.getElementById('resultado-itinerario');
            if (val.length < 2) {{ resDiv.style.display = 'none'; return; }}
            
            let foundId = null;
            for (let pid in estadoGlobal) {{
                if (normalizar(estadoGlobal[pid].nombre).includes(val)) {{
                    foundId = pid; break;
                }}
            }}
            
            if (!foundId) {{
                resDiv.innerHTML = '<p style="color:#ff4757; font-size:12px; margin:0;">No se encontró al costalero.</p>';
                resDiv.style.display = 'block';
                return;
            }}
            
            let e = estadoGlobal[foundId];
            let tramosInfo = [];
            for (let tr in datosExport.Mapping) {{
                let map = datosExport.Mapping[tr];
                let enTrono = e.tronoArr.includes(map.Trono);
                let enCruz  = LLEVA_CRUZ && e.cruzArr.includes(map.Cruz);
                if (enTrono || enCruz) {{
                    let roles = [];
                    if (enTrono) roles.push('⛪ Trono');
                    if (enCruz)  roles.push('✝ Cruz');
                    tramosInfo.push('<li><span class="tramo-label"><b>'+tr+'</b></span><span style="color:#d4af37; font-weight:bold;">'+roles.join(' + ')+'</span></li>');
                }} else {{
                    tramosInfo.push('<li><span class="tramo-label">'+tr+'</span><span style="color:#888;">🕯️ Cirio (Descanso)</span></li>');
                }}
            }}
            
            resDiv.innerHTML = '<div style="margin-bottom:10px; border-bottom:1px solid #d4af37; padding-bottom:5px;"><b>' + e.nombre + '</b></div><ul>' + tramosInfo.join('') + '</ul>';
            resDiv.style.display = 'block';
        }}
    <\/script>
</body>
</html>`;
        
        let contentHTML = "";
        
        let parseSlot = (p) => {{
            if (p.id === -1 || p.altura === 0) return '<li class="hueco-libre">Hueco Libre</li>';
            let e = estadoGlobal[p.id]; // <--- ¡Corregido aquí!
            let bg = '';
            if (e) {{
                if (e.estadoStr === 'critico' || e.estadoStr === 'doble') bg = 'bg-rojo';
                else if (e.estadoStr === 'cruzYTrono') bg = 'bg-azul';
                else if (e.estadoStr === 'dosTurnos') bg = 'bg-amarillo';
            }}
            return '<li class="costalero-cell '+bg+'"><div class="c-info"><span class="nombre">'+p.nombre+'</span></div><span class="meta">'+p.altura+'cm</span></li>';
        }};

        for (let turno in datos.Trono) {{ // <--- ¡Corregido aquí!
            contentHTML += '<div class="turno-box page-break-avoid"><h3 class="turno-title">⛪ TRONO - '+turno+'</h3><div class="grid-varales">';
            ['Izquierda', 'Centro', 'Derecha'].forEach(vara => {{
                contentHTML += '<div class="varal"><h4 class="varal-title">'+vara+'</h4><div class="seccion-top">DELANTE</div><ul class="lista-costaleros">';
                datos.Trono[turno].Delante[vara].forEach(p => {{ contentHTML += parseSlot(p); }});
                contentHTML += '</ul><div class="seccion-mid">CRISTO</div><ul class="lista-costaleros">';
                datos.Trono[turno].Detras[vara].forEach(p => {{ contentHTML += parseSlot(p); }});
                contentHTML += '</ul><div class="seccion-bot">DETRÁS</div></div>';
            }});
            contentHTML += '</div></div>';
        }}

        if (LLEVA_CRUZ && datos.Cruz) {{ // <--- ¡Corregido aquí!
            for (let turno in datos.Cruz) {{
                contentHTML += '<div class="turno-box page-break-avoid"><h3 class="turno-title">✝ CRUZ INSIGNIA - '+turno+'</h3><div class="grid-varales">';
                ['Izquierda', 'Derecha'].forEach(vara => {{
                    contentHTML += '<div class="varal"><h4 class="varal-title">'+vara+'</h4><div class="seccion-top">DELANTE</div><ul class="lista-costaleros">';
                    datos.Cruz[turno].Delante[vara].forEach(p => {{ contentHTML += parseSlot(p); }});
                    contentHTML += '</ul><div class="seccion-mid">CRUZ</div><ul class="lista-costaleros">';
                    datos.Cruz[turno].Detras[vara].forEach(p => {{ contentHTML += parseSlot(p); }});
                    contentHTML += '</ul><div class="seccion-bot">DETRÁS</div></div>';
                }});
                contentHTML += '</div></div>';
            }}
        }}

        contentHTML += '<div class="seccion-texto page-break-avoid"><h3>🗺️ Hoja de Ruta y Tramos</h3><ul class="lista-tramos">';
        for (let tr in datos.Mapping) {{ // <--- ¡Corregido aquí!
            let m = datos.Mapping[tr];
            let rStr = m.Ruta ? ` <i>(${{m.Ruta}})</i>` : '';
            let tStr = m.Trono ? 'Trono: ' + m.Trono : '';
            let cStr = (LLEVA_CRUZ && m.Cruz) ? ' | Cruz: ' + m.Cruz : ''; // <--- ¡Corregido aquí!
            contentHTML += '<li><b>'+tr+rStr+':</b> '+tStr+cStr+'</li>';
        }}
        contentHTML += '</ul></div>';

        html_pdf = html_pdf.replace('<div id="content-turnos"></div>', contentHTML);

        let pdfWin = window.open('', '_blank');
        pdfWin.document.write(html_pdf);
        pdfWin.document.close();
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
        if (target.bloqueado) {{
            alert("🔒 No puedes modificar un hueco que está bloqueado.");
            dragging = null; return;
        }}

        if (dragging.source === 'sidebar') {{
            if (target.id !== -1 && !confirm(`El hueco ya está ocupado por ${{target.nombre}}. ¿Reemplazar?`)) {{ dragging = null; return; }}
            datos[tipo][turno][sec][v][idx] = {{...dragging.persona, bloqueado: false}};
        }} else {{
            let orig = datos[dragging.tipo][dragging.turno][dragging.sec][dragging.v][dragging.idx];
            if (orig.bloqueado) {{
                alert("🔒 El costalero que intentas mover está bloqueado en su posición actual.");
                dragging = null; return;
            }}
            // Intercambio
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

    function normalizar(s) {{ return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase(); }}

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
                d.onclick = () => {{ 
                    datos[tipo][turno][sec][v][idx] = {{...m, bloqueado: false}}; 
                    render(); guardarMemoria(); if(sidebarAbierto) renderSidebar(); 
                }};
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