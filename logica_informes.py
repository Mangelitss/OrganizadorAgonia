import json
import datetime

def crear_html_informe(tipo, archivo_json):
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except Exception as e:
        return False, str(e)

    fecha = datetime.datetime.now().strftime("%d/%m/%Y")
    
    # 1. RASTREO DE IDS (Para pintar el fondo de amarillo en los que repiten Trono)
    ids_en_turno_c = set()
    if "Trono" in datos and "Turno C" in datos["Trono"]:
        for varal in datos["Trono"]["Turno C"].values():
            for sec in varal.values():
                for p in sec:
                    if p.get("id", -1) != -1:
                        ids_en_turno_c.add(p["id"])

    # 2. DEFINICIÓN DINÁMICA DE TEXTOS Y LÓGICA SEGÚN PROCESIÓN
    if "Viernes" in tipo:
        # ==========================================
        # TEXTOS: VIERNES SANTO
        # ==========================================
        bloque_itinerario = """
        <div class="seccion-texto">
            <h3>📍 Orden e Itinerario Oficial (Viernes Santo)</h3>
            <ul class="lista-tramos">
                <li><b>Tramo 1 (Turno A):</b> Monserrate ➔ Plaza del Carmen (Ayuntamiento)</li>
                <li><b>Tramo 2 (Turno B):</b> Plaza del Carmen ➔ As de Oros (Plaza Nueva)</li>
                <li><b>Tramo 3 (Turno A):</b> As de Oros ➔ Glorieta</li>
                <li><b>Tramo 4 (Turno C):</b> Glorieta ➔ Oficina de Turismo</li>
                <li><b>Regreso (Turno A):</b> Oficina de Turismo ➔ Santiago</li>
                <li><b>Regreso (Turno B+C):</b> Santiago ➔ Gasolinera</li>
                <li><b>Regreso (Turno A):</b> Gasolinera ➔ San Francisco</li>
            </ul>
        </div>
        """
        
        # 🟢 AQUÍ PUEDES MODIFICAR LAS INDICACIONES DEL VIERNES:
        bloque_indicaciones = """
        <div class="seccion-texto">
            <h3>⚠️ Indicaciones Específicas para los Tramos</h3>
            <p><b>Tramo 1:</b> Atención especial a la salida de Monserrate. Movimientos muy suaves y coordinados para salvar la puerta.</p>
            <p><b>Tramo 2:</b> Cuidado con el giro de entrada a la Plaza Nueva y evitar los tirones en las arrancadas.</p>
            <p><b>Tramo 3:</b> Mantener el paso firme, especial precaución con el cruce de cables en la Glorieta.</p>
            <p><b>Tramo 4:</b> Respetar los tiempos de relevo marcados por el capataz, la calle se estrecha en los últimos metros.</p>
        </div>
        """
        
        js_tramos_obj = """
            const TRAMOS = {
                "Trono": { "Turno A": [1, 3, 5, 7], "Turno B": [2, 6], "Turno C": [4, 6] },
                "Cruz": { "Turno 1": [1], "Turno 2": [2], "Turno 3": [3], "Turno 4": [4] }
            };
        """
        js_estado_doble = """
            for (let i = 0; i < allTramos.length - 1; i++) {
                if (allTramos[i+1] - allTramos[i] === 1) tieneDoble = true;
            }
            if (allTramos.filter(t => t <= 4).length > 2) tieneDoble = true;
        """
        js_html_rutas = """
            let html = `<h4 style="color:#d4af37; margin-top:0; margin-bottom:15px; font-size:18px; border-bottom:1px solid #3d0c2e; padding-bottom:10px;">📋 Hoja de Ruta: ${st.nombre}</h4>`;
            html += `<div style="background:#160311; padding:15px; border-radius:5px; border-left:5px solid #d4af37; margin-bottom:10px;">
                        <h5 style="margin: 0 0 8px 0; color: #e8d08c; font-size: 14px; border-bottom: 1px solid #3d0c2e; padding-bottom: 5px;">🌟 PROCESIÓN (Trono y Cruz)</h5>
                        <ul style="list-style:none; padding:0; margin:0;">`;
            [
                { num: 1, txt: "1. Monserrate ➔ Ayto" },
                { num: 2, txt: "2. Ayto ➔ As de Oros" },
                { num: 3, txt: "3. As Oros ➔ Glorieta" },
                { num: 4, txt: "4. Glorieta ➔ Turismo" }
            ].forEach(tr => { html += generarFilaTramo(tr, st, tOcupados); });
            html += `</ul></div>`;

            html += `<div style="background:#160311; padding:15px; border-radius:5px; border-left:5px solid #d4af37;">
                        <h5 style="margin: 0 0 8px 0; color: #e8d08c; font-size: 14px; border-bottom: 1px solid #3d0c2e; padding-bottom: 5px;">🏠 REGRESO (Solo Trono)</h5>
                        <ul style="list-style:none; padding:0; margin:0;">`;
            [
                { num: 5, txt: "5. Turismo ➔ Santiago" },
                { num: 6, txt: "6. Santiago ➔ Gasolinera" },
                { num: 7, txt: "7. Gasolinera ➔ San Fco" }
            ].forEach(tr => { html += generarFilaTramo(tr, st, tOcupados); });
            html += `</ul></div>`;
            return html;
        """
        js_fila_tramo = """
            if (enCristo.length > 0 && enCruz.length > 0) {
                label = `💥 <strong style='color:#ff0000'>¡IMPOSIBLE! (${enCristo.join('+')} y ${enCruz.join('+')})</strong>`;
            } else if (enCristo.length > 0) {
                label = `💪 <strong style='color:#e8d08c'>🕍 Trono (${enCristo.join(" + ")})</strong>`;
            } else if (enCruz.length > 0) {
                let sinDescanso = tOcupados.includes(tr.num - 1) || tOcupados.includes(tr.num + 1);
                let sobrecarga = tOcupados.filter(t => t <= 4).length > 2;
                if (sinDescanso || sobrecarga) {
                    label = `⚠️ <strong style='color:#ff4757'>✝️ Cruz (${enCruz.join('+')}) [SOBREESFUERZO]</strong>`;
                } else {
                    label = `💪 <strong style='color:#00d2ff'>✝️ Cruz (${enCruz.join('+')})</strong>`;
                }
            }
        """
    else:
        # ==========================================
        # TEXTOS Y LÓGICA: MIÉRCOLES SANTO
        # ==========================================
        anio = datetime.datetime.now().year
        es_par = (anio % 2 == 0)
        txt_trono_1 = "Turno B" if es_par else "Turno A"
        txt_trono_2 = "Turno A" if es_par else "Turno B"
        t_a = "[2]" if es_par else "[1]"
        t_b = "[1]" if es_par else "[2]"

        bloque_itinerario = f"""
        <div class="seccion-texto">
            <h3>📍 Orden e Itinerario Oficial (Miércoles Santo)</h3>
            <ul class="lista-tramos">
                <li><b>Tramo 1 (S. Francisco ➔ Gasolinera):</b> Carga el Trono el <b>{txt_trono_1}</b>, y la Cruz el <b>Turno 1</b>.</li>
                <li><b>Tramo 2 (Gasolinera ➔ Monserrate):</b> Carga el Trono el <b>{txt_trono_2}</b>, y la Cruz el <b>Turno 2</b>.</li>
            </ul>
        </div>
        """
        
        # 🟢 AQUÍ PUEDES MODIFICAR LAS INDICACIONES DEL MIÉRCOLES:
        bloque_indicaciones = """
        <div class="seccion-texto">
            <h3>⚠️ Indicaciones Específicas para los Tramos</h3>
            <p><b>Tramo 1 (San Francisco a Gasolinera):</b> Cuidado extremo en la salida por la puerta de San Francisco. Movimientos suaves al girar a la calle principal y mantener siempre la cadencia del tambor.</p>
            <p><b>Tramo 2 (Gasolinera a Monserrate):</b> Tramo de esfuerzo y subida hacia el Santuario de Monserrate. Administrar las fuerzas y hacer caso estricto a las indicaciones del Capataz en la rampa de llegada.</p>
        </div>
        """

        js_tramos_obj = f"""
            const TRAMOS = {{
                "Trono": {{ "Turno A": {t_a}, "Turno B": {t_b} }},
                "Cruz": {{ "Turno 1": [1], "Turno 2": [2] }}
            }};
        """
        js_estado_doble = """
            if (allTramos.length > 1) tieneDoble = true;
        """
        js_html_rutas = """
            let html = `<h4 style="color:#d4af37; margin-top:0; margin-bottom:15px; font-size:18px; border-bottom:1px solid #3d0c2e; padding-bottom:10px;">📋 Hoja de Ruta: ${st.nombre}</h4>`;
            html += `<div style="background:#160311; padding:15px; border-radius:5px; border-left:5px solid #d4af37; margin-bottom:10px;">
                        <h5 style="margin: 0 0 8px 0; color: #e8d08c; font-size: 14px; border-bottom: 1px solid #3d0c2e; padding-bottom: 5px;">🌟 PROCESIÓN (Ida)</h5>
                        <ul style="list-style:none; padding:0; margin:0;">`;
            [
                { num: 1, txt: "1. S.Francisco ➔ Gasolinera" },
                { num: 2, txt: "2. Gasolinera ➔ Monserrate" }
            ].forEach(tr => { html += generarFilaTramo(tr, st, tOcupados); });
            html += `</ul></div>`;
            return html;
        """
        js_fila_tramo = """
            if (enCristo.length > 0 && enCruz.length > 0) {
                label = `💥 <strong style='color:#ff0000'>¡IMPOSIBLE! (${enCristo.join('+')} y ${enCruz.join('+')})</strong>`;
            } else if (enCristo.length > 0) {
                label = `💪 <strong style='color:#e8d08c'>🕍 Trono (${enCristo.join(" + ")})</strong>`;
            } else if (enCruz.length > 0) {
                label = `💪 <strong style='color:#00d2ff'>✝️ Cruz (${enCruz.join('+')})</strong>`;
            }
            if(tOcupados.length === 2 && (enCristo.length > 0 || enCruz.length > 0)) {
                label = label.replace("💪", "⚠️").replace("#e8d08c", "#ff4757").replace("#00d2ff", "#ff4757") + " [SOBREESFUERZO]";
            }
        """

    def generar_li_costalero(p):
        nombre_original = p.get('nombre', 'HUECO LIBRE')
        if nombre_original == "HUECO LIBRE" or p.get('id', -1) == -1:
            return "<li class='hueco-libre'>-- Hueco Libre --</li>"
        
        clase_bg = ""
        nombre_limpio = nombre_original
        
        if "(C-Doble)" in nombre_original:
            clase_bg = "bg-rojo"
            nombre_limpio = nombre_original.replace(" (C-Doble)", "")
        elif "(C)" in nombre_original:
            clase_bg = "bg-azul"
            nombre_limpio = nombre_original.replace(" (C)", "")
        elif "(R)" in nombre_original or p.get("id") in ids_en_turno_c:
            clase_bg = "bg-amarillo"
            nombre_limpio = nombre_original.replace(" (R)", "")
            
        altura = f"{p.get('altura', '')}cm"
        pid = p.get('id', -1)
        
        return f"""
        <li class='costalero-cell {clase_bg}'>
            <div class="c-info">
                <button class="btn-info no-print" onclick="abrirInfoModal({pid})" title="Ver itinerario">ℹ️</button>
                <span class='nombre'>{nombre_limpio.strip()}</span>
            </div>
            <span class='meta'>{altura}</span>
        </li>
        """

    # ==========================================
    # 3. HTML COMPLETO MAQUETADO
    # ==========================================
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Informe Oficial - {tipo}</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=Open+Sans:wght@400;600;800&display=swap');
            
            body {{ font-family: 'Open Sans', Arial, sans-serif; background: #f4f6f8; color: #333; margin: 0; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #fff; padding: 40px; box-shadow: 0 0 15px rgba(0,0,0,0.1); border-top: 8px solid #5c164e; }}
            
            /* WEB CONTROLS (NO PRINT) */
            .web-controls {{ display: flex; flex-direction: column; align-items: center; gap: 15px; margin-bottom: 30px; background: #1a0514; padding: 20px; border-radius: 8px; border: 1px solid #d4af37; }}
            .buscador-box {{ width: 100%; max-width: 600px; text-align: center; }}
            .buscador-box input {{ width: 100%; padding: 12px; font-size: 16px; background: #0c0209; color: #d4af37; border: 1px solid #3d0c2e; border-radius: 5px; outline: none; }}
            .itinerario-result {{ margin-top: 15px; padding: 15px; background: #23061b; border-radius: 5px; border-left: 5px solid #d4af37; display: none; color: #f8f0f5; text-align: left; }}
            .itinerario-result ul {{ list-style: none; padding: 0; margin: 0; }}
            .itinerario-result li {{ padding: 8px 0; border-bottom: 1px dashed #3d0c2e; font-size: 13px; display: flex; }}
            .tramo-label {{ width: 220px; color: #a37c95; flex-shrink: 0; }}
            .btn-pdf {{ background: #5c164e; color: #fff; text-align: center; padding: 12px 25px; border-radius: 5px; font-weight: bold; cursor: pointer; border: none; font-size: 14px; text-transform: uppercase; box-shadow: 0 4px 6px rgba(92, 22, 78, 0.3); transition: 0.3s; width: 100%; max-width: 350px; }}
            .btn-pdf:hover {{ background: #7a1b67; transform: translateY(-2px); }}

            /* HEADER DOCUMENTO OFICIAL */
            .header {{ text-align: center; border-bottom: 2px solid #e0e0e0; padding-bottom: 20px; margin-bottom: 20px; }}
            .logo-img {{ width: 100px; height: auto; margin-bottom: 10px; }}
            .header h1 {{ color: #4a148c; margin: 0; font-size: 20px; text-transform: uppercase; letter-spacing: 1px; font-family: 'Cinzel', serif; font-weight: 600; }}
            .header h2 {{ color: #b5952f; margin: 5px 0; font-size: 16px; text-transform: uppercase; letter-spacing: 2px; }}
            .header p {{ color: #666; font-size: 12px; margin: 5px 0 0 0; font-weight: bold; }}
            
            /* LEYENDA */
            .leyenda {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; font-size: 11px; font-weight: bold; background: #fafafa; padding: 10px; border-radius: 5px; border: 1px solid #eee; flex-wrap: wrap; }}
            .leyenda-item {{ display: flex; align-items: center; gap: 5px; }}
            .caja {{ width: 12px; height: 12px; border-radius: 3px; display: inline-block; border: 1px solid rgba(0,0,0,0.2); }}
            
            /* TRONOS Y VARALES */
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
            
            .bg-amarillo {{ background-color: #fff9c4 !important; border-color: #fbc02d !important; color: #000; }}
            .bg-azul {{ background-color: #e1f5fe !important; border-color: #4fc3f7 !important; color: #000; }}
            .bg-rojo {{ background-color: #ffebee !important; border-color: #ef9a9a !important; color: #000; }}
            
            .c-info {{ display: flex; align-items: center; gap: 5px; }}
            .nombre {{ font-weight: 600; font-size: 11px; }}
            .meta {{ font-size: 9px; opacity: 0.7; font-weight: bold; }}
            .btn-info {{ background: none; border: none; color: #007bff; cursor: pointer; padding: 0; font-size: 14px; line-height: 1; margin-top:-2px; }}
            .btn-info:hover {{ transform: scale(1.1); }}

            /* TEXTOS INFERIORES */
            .seccion-texto {{ background: #fafafa; padding: 20px; border-radius: 8px; border-left: 4px solid #5c164e; margin-bottom: 20px; page-break-inside: avoid; }}
            .seccion-texto h3 {{ color: #5c164e; margin-top: 0; border-bottom: 1px solid #ccc; padding-bottom: 5px; font-size: 16px; text-transform: uppercase; }}
            .seccion-texto p {{ font-size: 12px; line-height: 1.5; color: #444; margin-bottom: 8px; }}
            .lista-tramos {{ font-size: 12px; color: #444; line-height: 1.6; margin: 0; padding-left: 20px; }}

            /* MODAL (POP-UP) */
            .modal-overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 1000; justify-content: center; align-items: center; backdrop-filter: blur(3px); }}
            .modal-content {{ background: #1a0514; border: 2px solid #d4af37; padding: 25px; border-radius: 12px; width: 90%; max-width: 550px; box-shadow: 0 0 25px rgba(212, 175, 55, 0.2); position: relative; animation: slideIn 0.3s ease-out; color: #fff; }}
            .modal-close {{ position: absolute; top: 15px; right: 15px; background: none; border: none; color: #ff4757; font-size: 24px; cursor: pointer; transition: 0.2s; }}
            .modal-close:hover {{ transform: scale(1.2); }}
            @keyframes slideIn {{ from {{ transform: translateY(-30px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}

            /* REGLAS DE IMPRESIÓN (PDF) */
            @media print {{
                body {{ background: #fff; padding: 0; font-family: 'Open Sans', Helvetica, sans-serif; }}
                .no-print, .web-controls {{ display: none !important; }}
                .container {{ box-shadow: none; border-top: none; padding: 0; }}
                .turno-box {{ border: 1px solid #000; }}
                .turno-title {{ background: #eee !important; color: #000 !important; border-bottom: 1px solid #000; -webkit-print-color-adjust: exact; }}
                .bg-amarillo, .bg-azul, .bg-rojo, .seccion-mid, .caja {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
            }}
        </style>
    </head>
    <body>
        <div class="web-controls no-print">
            <button class="btn-pdf" onclick="generarPDF()">📥 DESCARGAR PDF PARA WHATSAPP</button>
            <div class="buscador-box">
                <h3 style="margin-top:0; color:#d4af37;">🔍 BUSCADOR DE COSTALERO</h3>
                <input type="text" id="input-buscador" placeholder="Escribe un nombre..." onkeyup="actualizarBuscador()">
                <div id="resultado-itinerario" class="itinerario-result"></div>
            </div>
        </div>

        <div id="modal-info" class="modal-overlay no-print" onclick="cerrarModal(event)">
            <div class="modal-content" onclick="event.stopPropagation()">
                <button class="modal-close" onclick="cerrarModal()">✖</button>
                <div id="modal-body"></div>
            </div>
        </div>
        
        <div class="container" id="informe-content">
            <div class="header">
                <img src="bandera_tercio_npj.jpg" alt="Escudo Mayordomía" class="logo-img" onerror="this.style.display='none'">
                <h1>OFS Muy Ilustre Mayordomía de Nuestro Padre Jesús Nazareno</h1>
                <h2>Orden Procesional - {tipo}</h2>
                <p>Emitido: {fecha}</p>
            </div>
            
            <div class="leyenda">
                <div class="leyenda-item"><span class="caja bg-amarillo"></span> Dobla Trono (Turnos seguidos)</div>
                <div class="leyenda-item"><span class="caja bg-azul"></span> Carga Alterna (Trono y Cruz)</div>
                <div class="leyenda-item"><span class="caja bg-rojo"></span> Sobreesfuerzo Crítico (Carga doble seguida)</div>
            </div>
    """

    for categoria, turnos in datos.items():
        if not turnos: continue
        
        html += f"<h2 style='color:#5c164e; border-bottom: 2px solid #5c164e; padding-bottom:5px; margin-top:30px; font-size:18px;'>ESTRUCTURA: {categoria.upper()}</h2>"
        
        for nombre_turno, varales in turnos.items():
            html += f"""
            <div class="turno-box">
                <h3 class="turno-title">{nombre_turno}</h3>
                <div class="grid-varales">
            """
            for nombre_varal, secciones in varales.items():
                html += f"""
                    <div class="varal">
                        <h4 class="varal-title">VARA {nombre_varal}</h4>
                """
                if "Delante" in secciones:
                    html += "<div class='seccion-top'>▲ DELANTE ▲</div>"
                    html += "<ul class='lista-costaleros'>"
                    for p in secciones["Delante"]:
                        html += generar_li_costalero(p)
                    html += "</ul>"
                
                html += "<div class='seccion-mid'> TRONO </div>"
                
                if "Detras" in secciones:
                    html += "<ul class='lista-costaleros'>"
                    for p in secciones["Detras"]:
                        html += generar_li_costalero(p)
                    html += "</ul>"
                    html += "<div class='seccion-bot'>▼ DETRÁS ▼</div>"
                
                html += "</div>"
            html += "</div></div>"

    # INSERTAMOS LOS TEXTOS ESPECÍFICOS DE LA PROCESIÓN (Itinerario + Indicaciones)
    html += bloque_itinerario
    html += bloque_indicaciones
    
    html += """
        <div class="seccion-texto">
            <h3>📜 Normativa de la Cuadrilla</h3>
            <p><i>(Reservado para las normas oficiales de la Mayordomía que se adjuntarán próximamente).</i></p>
        </div>
    """

    turnos_json_str = json.dumps(datos)
    html += f"""
            <div style="text-align: center; margin-top: 40px; font-size: 10px; color: #999; border-top: 1px solid #eee; padding-top: 10px;">
                Generado por el Sistema Gestor Cofrade de la Agonía.
            </div>
        </div>
        
        <script>
            let datos = {turnos_json_str};
            let estadoGlobal = {{}};
            
            {js_tramos_obj}

            function analizarEstado() {{
                let stats = {{}};
                for (let tipo of ["Trono", "Cruz"]) {{
                    if(!datos[tipo]) continue;
                    for (let t of Object.keys(datos[tipo])) {{
                        for (let v of Object.keys(datos[tipo][t])) {{
                            for (let sec of ["Delante", "Detras"]) {{
                                datos[tipo][t][v][sec].forEach(p => {{
                                    if (p.id && p.id !== -1) {{
                                        if (!stats[p.id]) stats[p.id] = {{ nombre: p.nombre.replace(" (R)","").replace(" (C)","").replace(" (C-Doble)",""), cristo: [], cruz: [] }};
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
                    let cristoArr = [];
                    s.cristo.forEach(t => cristoArr.push(...(TRAMOS.Trono[t] || [])));
                    let cruzArr = [];
                    s.cruz.forEach(t => cruzArr.push(...(TRAMOS.Cruz[t] || [])));
                    
                    let allTramos = [...new Set([...cristoArr, ...cruzArr])].sort((a,b) => a - b);
                    s.tramos = allTramos;
                }}
                estadoGlobal = stats;
            }}

            function generarFilaTramo(tr, st, tOcupados) {{
                let label = "🕯️ <strong style='color:#884d72'>Cirio (Descanso)</strong>";
                let enCristo = [];
                st.cristo.forEach(t => {{ if((TRAMOS.Trono[t]||[]).includes(tr.num)) enCristo.push(t); }});
                let enCruz = [];
                st.cruz.forEach(t => {{ if((TRAMOS.Cruz[t]||[]).includes(tr.num)) enCruz.push(t); }});

                {js_fila_tramo}
                
                return `<li style="color:#f8f0f5;"><span class="tramo-label" style="color:#a37c95;">${{tr.txt}}</span> ${{label}}</li>`;
            }}

            function construirHTMLItinerario(st) {{
                let tOcupados = st.tramos;
                {js_html_rutas}
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
                    resDiv.style.display = 'block';
                    resDiv.innerHTML = construirHTMLItinerario(estadoGlobal[idFound]);
                }} else {{
                    resDiv.style.display = 'none';
                }}
            }}

            function abrirInfoModal(id) {{
                let st = estadoGlobal[id];
                if (!st) return;
                document.getElementById('modal-body').innerHTML = construirHTMLItinerario(st);
                document.getElementById('modal-info').style.display = 'flex';
            }}

            function cerrarModal(ev) {{
                if (!ev || ev.target.id === 'modal-info' || ev.target.className === 'modal-close') {{
                    document.getElementById('modal-info').style.display = 'none';
                }}
            }}

            window.onload = () => {{ analizarEstado(); }};

            function generarPDF() {{
                const element = document.getElementById('informe-content');
                const btn = document.querySelector('.btn-pdf');
                btn.innerText = "⏳ GENERANDO PDF...";
                
                const opt = {{
                    margin:       [10, 10, 10, 10], 
                    filename:     'Orden_Procesional_Agonia_{tipo.replace(" ", "_")}.pdf',
                    image:        {{ type: 'jpeg', quality: 0.98 }},
                    html2canvas:  {{ scale: 2, useCORS: true }},
                    jsPDF:        {{ unit: 'mm', format: 'a4', orientation: 'portrait' }}
                }};
                
                html2pdf().set(opt).from(element).save().then(() => {{
                    btn.innerText = "📥 DESCARGAR PDF PARA WHATSAPP";
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    output_file = "informe_generado.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
        
    return True, output_file