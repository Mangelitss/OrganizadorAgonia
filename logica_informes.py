import json
import datetime
import base64
import os

def crear_html_informe(tipo, archivo_json, anio):
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos_raw = json.load(f)
    except Exception as e:
        return False, f"Error al abrir el archivo: {str(e)}"

    fecha_hoy = datetime.datetime.now().strftime("%d/%m/%Y")
    es_par = (anio % 2 == 0)
    
    # Sistema Antidespistes de Informes
    tipo_json = datos_raw.get("tipo_procesion", "")
    if tipo_json == "miercoles_santo":
        tipo = "Miércoles Santo"
    elif tipo_json == "viernes_santo":
        tipo = "Viernes Santo"
    
    indicaciones = datos_raw.get("indicaciones", {})
    datos_tronos = {k: v for k, v in datos_raw.items() if k in ["Trono", "Cruz"]}

    # Convertimos la imagen a código puro (Base64) para que el PDF jamás falle en local
    img_b64 = ""
    if os.path.exists("bandera_tercio_npj.jpg"):
        try:
            with open("bandera_tercio_npj.jpg", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                img_b64 = f"data:image/jpeg;base64,{encoded_string}"
        except: pass

    i_norm = indicaciones.get("normativa", "").strip() or "(Sin normativa específica dictada por el Capataz)"

    # ==========================================
    # MOTOR MATEMÁTICO DE COLORES Y TRAMOS
    # ==========================================
    tramos_dict = {}
    for cat, turnos in datos_tronos.items():
        for t_nom, varales in turnos.items():
            for v_nom, secciones in varales.items():         
                for sec_nom, personas in secciones.items():  
                    for p in personas:                       
                        pid = p.get('id', -1)
                        if pid != -1:
                            if pid not in tramos_dict:
                                tramos_dict[pid] = {'cristo': [], 'cruz': []}
                            if cat == "Trono":
                                tramos_dict[pid]['cristo'].append(t_nom)
                            else:
                                tramos_dict[pid]['cruz'].append(t_nom)

    if "Viernes" in tipo:
        if es_par:
            map_tr = {"Turno A": [1,3,5,7], "Turno B": [2,6], "Turno C": [4,6]}
        else:
            map_tr = {"Turno A": [2,4,6], "Turno B": [3,5,7], "Turno C": [1,5,7]}
        map_cr = {"Turno 1": [1], "Turno 2": [2], "Turno 3": [3], "Turno 4": [4]}
    else:
        if es_par:
            map_tr = {"Turno A": [2], "Turno B": [1]}
        else:
            map_tr = {"Turno A": [1], "Turno B": [2]}
        map_cr = {"Turno 1": [1], "Turno 2": [2]}

    # Cálculo implacable de Sobreesfuerzos y Repeticiones
    for pid, d in tramos_dict.items():
        all_tr = []
        for t in d['cristo']: all_tr.extend(map_tr.get(t, []))
        for t in d['cruz']: all_tr.extend(map_cr.get(t, []))
        
        all_tr = sorted(list(set(all_tr)))
        tiene_doble = False
        
        for i in range(len(all_tr)-1):
            if all_tr[i+1] - all_tr[i] == 1:
                tiene_doble = True
                
        if "Viernes" in tipo:
            cargas_procesion = len([x for x in all_tr if x <= 4])
            if cargas_procesion > 2:
                tiene_doble = True
                
        d['all_tr'] = all_tr
        d['tiene_doble'] = tiene_doble

    # ==========================================
    # LÓGICA DE TEXTOS (VIERNES VS MIÉRCOLES)
    # ==========================================
    if "Viernes" in tipo:
        i_t1 = indicaciones.get("tramo1", "").strip() or "(Sin indicaciones especiales)"
        i_t2 = indicaciones.get("tramo2", "").strip() or "(Sin indicaciones especiales)"
        i_t3 = indicaciones.get("tramo3", "").strip() or "(Sin indicaciones especiales)"
        i_t4 = indicaciones.get("tramo4", "").strip() or "(Sin indicaciones especiales)"

        if es_par:
            txt_t1, txt_t2, txt_t3, txt_t4 = "Turno A", "Turno B", "Turno A", "Turno C"
            txt_r1, txt_r2, txt_r3 = "Turno A", "Turnos B y C", "Turno A"
            js_tramos_obj = """
            const TRAMOS = {
                "Trono": { "Turno A": [1, 3, 5, 7], "Turno B": [2, 6], "Turno C": [4, 6] },
                "Cruz": { "Turno 1": [1], "Turno 2": [2], "Turno 3": [3], "Turno 4": [4] }
            };
            """
        else:
            txt_t1, txt_t2, txt_t3, txt_t4 = "Turno C", "Turno A", "Turno B", "Turno A"
            txt_r1, txt_r2, txt_r3 = "Turnos B y C", "Turno A", "Turnos B y C"
            js_tramos_obj = """
            const TRAMOS = {
                "Trono": { "Turno A": [2, 4, 6], "Turno B": [3, 5, 7], "Turno C": [1, 5, 7] },
                "Cruz": { "Turno 1": [1], "Turno 2": [2], "Turno 3": [3], "Turno 4": [4] }
            };
            """

        bloque_itinerario = f"""
        <div class="seccion-texto">
            <h3>📍 Orden e Itinerario Oficial (Viernes Santo - Año {anio})</h3>
            <ul class="lista-tramos">
                <li><b>Tramo 1:</b> Monserrate ➔ Ayuntamiento || <b>{txt_t1}</b></li>
                <li><b>Tramo 2:</b> Ayuntamiento ➔ As de Oros || <b>{txt_t2}</b></li>
                <li><b>Tramo 3:</b> As de Oros ➔ Glorieta || <b>{txt_t3}</b></li>
                <li><b>Tramo 4:</b> Glorieta ➔ Oficina Turismo || <b>{txt_t4}</b></li>
                <li style="margin-top:5px; border-top:1px dashed #ccc; padding-top:5px;"><b>Regreso 1:</b> Oficina Turismo ➔ Santiago || <b>{txt_r1}</b></li>
                <li><b>Regreso 2:</b> Santiago ➔ Gasolinera || <b>{txt_r2}</b></li>
                <li><b>Regreso 3:</b> Gasolinera ➔ San Francisco || <b>{txt_r3}</b></li>
            </ul>
        </div>
        """
        
        bloque_indicaciones = f"""
        <div class="seccion-texto indicaciones-dinamicas">
            <h3>⚠️ Indicaciones Específicas del Capataz</h3>
            <p><b>Tramo 1 (Monserrate ➔ Ayto):</b><br>{i_t1}</p>
            <p><b>Tramo 2 (Ayto ➔ As de Oros):</b><br>{i_t2}</p>
            <p><b>Tramo 3 (As Oros ➔ Glorieta):</b><br>{i_t3}</p>
            <p><b>Tramo 4 y Regreso:</b><br>{i_t4}</p>
        </div>
        <div class="seccion-texto indicaciones-dinamicas">
            <h3>📜 Normativa de la Cuadrilla</h3>
            <p>{i_norm}</p>
        </div>
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

        # Variable recuperada para el Viernes
        js_fila_tramo = """
            if (enCristo.length > 0 && enCruz.length > 0) {
                label = `💥 <strong style='color:#ff0000'>¡IMPOSIBLE! (${enCristo.join('+')} y ${enCruz.join('+')})</strong>`;
            } else if (enCristo.length > 0) {
                label = `💪 <strong style='color:#e8d08c'>Trono (${enCristo.join(" + ")})</strong>`;
            } else if (enCruz.length > 0) {
                let sinDescanso = false;
                for(let i=0; i<tOcupados.length-1; i++){
                    if(tOcupados[i+1] - tOcupados[i] === 1) sinDescanso = true;
                }
                let sobrecarga = tOcupados.filter(t => t <= 4).length > 2;
                if (sinDescanso || sobrecarga) {
                    label = `⚠️ <strong style='color:#ff4757'>Cruz (${enCruz.join('+')}) [SOBREESFUERZO]</strong>`;
                } else {
                    label = `💪 <strong style='color:#00d2ff'>Cruz (${enCruz.join('+')})</strong>`;
                }
            }
        """

    else: 
        # ==================== MIÉRCOLES SANTO ====================
        i_t1 = indicaciones.get("tramo1", "").strip() or "(Sin indicaciones especiales)"
        i_t2 = indicaciones.get("tramo2", "").strip() or "(Sin indicaciones especiales)"

        if es_par:
            txt_trono_1, txt_trono_2 = "Turno B", "Turno A"
            js_tramos_obj = """
            const TRAMOS = {
                "Trono": { "Turno A": [2], "Turno B": [1] },
                "Cruz": { "Turno 1": [1], "Turno 2": [2] }
            };
            """
        else:
            txt_trono_1, txt_trono_2 = "Turno A", "Turno B"
            js_tramos_obj = """
            const TRAMOS = {
                "Trono": { "Turno A": [1], "Turno B": [2] },
                "Cruz": { "Turno 1": [1], "Turno 2": [2] }
            };
            """

        bloque_itinerario = f"""
        <div class="seccion-texto">
            <h3>📍 Orden e Itinerario Oficial (Miércoles Santo - Año {anio})</h3>
            <ul class="lista-tramos">
                <li><b>Tramo 1 (S. Francisco ➔ Gasolinera):</b> Carga el Trono el <b>{txt_trono_1}</b>, y la Cruz el <b>Turno 1</b>.</li>
                <li><b>Tramo 2 (Gasolinera ➔ Monserrate):</b> Carga el Trono el <b>{txt_trono_2}</b>, y la Cruz el <b>Turno 2</b>.</li>
            </ul>
        </div>
        """
        
        bloque_indicaciones = f"""
        <div class="seccion-texto indicaciones-dinamicas">
            <h3>⚠️ Indicaciones Específicas del Capataz</h3>
            <p><b>Tramo 1 (San Francisco a Gasolinera):</b><br>{i_t1}</p>
            <p><b>Tramo 2 (Gasolinera a Monserrate):</b><br>{i_t2}</p>
        </div>
        <div class="seccion-texto indicaciones-dinamicas">
            <h3>📜 Normativa de la Cuadrilla</h3>
            <p>{i_norm}</p>
        </div>
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

        # Variable recuperada para el Miércoles
        js_fila_tramo = """
            if (enCristo.length > 0 && enCruz.length > 0) {
                label = `💥 <strong style='color:#ff0000'>¡IMPOSIBLE! (${enCristo.join('+')} y ${enCruz.join('+')})</strong>`;
            } else if (enCristo.length > 0) {
                label = `💪 <strong style='color:#e8d08c'>Trono (${enCristo.join(" + ")})</strong>`;
            } else if (enCruz.length > 0) {
                label = `💪 <strong style='color:#00d2ff'>Cruz (${enCruz.join('+')})</strong>`;
            }
            if(tOcupados.length === 2 && (enCristo.length > 0 || enCruz.length > 0)) {
                label = label.replace("💪", "⚠️").replace("#e8d08c", "#ff4757").replace("#00d2ff", "#ff4757") + " [SOBREESFUERZO]";
            }
        """

    # GENERADOR DE CELDAS (APLICANDO COLOR MATEMÁTICO REAL)
    def generar_li_costalero(p):
        nombre_original = p.get('nombre', 'HUECO LIBRE')
        if nombre_original == "HUECO LIBRE" or p.get('id', -1) == -1:
            return "<li class='hueco-libre'>-- Hueco Libre --</li>"
        
        pid = p.get('id', -1)
        clase_bg = ""
        nombre_limpio = nombre_original.replace(" (R)", "").replace(" (C)", "").replace(" (C-Doble)", "").strip()
        
        # APLICACIÓN INFALIBLE DE COLORES POR MATRIZ DE TRAMOS
        if pid in tramos_dict:
            d = tramos_dict[pid]
            if d['tiene_doble']:
                clase_bg = "bg-rojo"
            elif len(set(d['cruz'])) > 0 and len(set(d['cristo'])) > 0:
                clase_bg = "bg-azul"
            elif len(set(d['cristo'])) >= 2:
                clase_bg = "bg-amarillo"
            
        altura = f"{p.get('altura', '')}cm"
        
        return f"""
        <li class='costalero-cell {clase_bg}'>
            <div class="c-info">
                <button class="btn-info no-print" onclick="abrirInfoModal({pid})" title="Ver itinerario">ℹ️</button>
                <span class='nombre'>{nombre_limpio}</span>
            </div>
            <span class='meta'>{altura}</span>
        </li>
        """

    # ==========================================
    # HTML ESTRUCTURA
    # ==========================================
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Informe Oficial - {tipo} {anio}</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=Open+Sans:wght@400;600;800&display=swap');
            
            body {{ font-family: 'Open Sans', Arial, sans-serif; background: #f4f6f8; color: #333; margin: 0; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #fff; padding: 40px; box-shadow: 0 0 15px rgba(0,0,0,0.1); border-top: 8px solid #5c164e; position: relative; }}
            
            .web-controls {{ display: flex; flex-direction: column; align-items: center; gap: 15px; margin-bottom: 30px; background: #1a0514; padding: 20px; border-radius: 8px; border: 1px solid #d4af37; }}
            .buscador-box {{ width: 100%; max-width: 600px; text-align: center; }}
            .buscador-box input {{ width: 100%; padding: 12px; font-size: 16px; background: #0c0209; color: #d4af37; border: 1px solid #3d0c2e; border-radius: 5px; outline: none; }}
            .itinerario-result {{ margin-top: 15px; padding: 15px; background: #23061b; border-radius: 5px; border-left: 5px solid #d4af37; display: none; color: #f8f0f5; text-align: left; }}
            .itinerario-result ul {{ list-style: none; padding: 0; margin: 0; }}
            .itinerario-result li {{ padding: 8px 0; border-bottom: 1px dashed #3d0c2e; font-size: 13px; display: flex; }}
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
            
            .bg-amarillo {{ background-color: #fff9c4 !important; border-color: #fbc02d !important; color: #000; }}
            .bg-azul {{ background-color: #e1f5fe !important; border-color: #4fc3f7 !important; color: #000; }}
            .bg-rojo {{ background-color: #ffebee !important; border-color: #ef9a9a !important; color: #000; }}
            
            .c-info {{ display: flex; align-items: center; gap: 5px; }}
            .nombre {{ font-weight: 600; font-size: 11px; }}
            .meta {{ font-size: 9px; opacity: 0.7; font-weight: bold; }}
            .btn-info {{ background: none; border: none; color: #007bff; cursor: pointer; padding: 0; font-size: 14px; line-height: 1; margin-top:-2px; }}
            .btn-info:hover {{ transform: scale(1.1); }}

            .seccion-texto {{ background: #fafafa; padding: 20px; border-radius: 8px; border-left: 4px solid #5c164e; margin-bottom: 20px; page-break-inside: avoid; }}
            .seccion-texto h3 {{ color: #5c164e; margin-top: 0; border-bottom: 1px solid #ccc; padding-bottom: 5px; font-size: 16px; text-transform: uppercase; }}
            .seccion-texto p {{ font-size: 12px; line-height: 1.5; color: #444; margin-bottom: 8px; }}
            .lista-tramos {{ font-size: 12px; color: #444; line-height: 1.6; margin: 0; padding-left: 20px; }}
            .indicaciones-dinamicas p {{ white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word; word-break: break-word; margin-bottom: 12px; }}

            .modal-overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 1000; justify-content: center; align-items: center; backdrop-filter: blur(3px); }}
            .modal-content {{ background: #1a0514; border: 2px solid #d4af37; padding: 25px; border-radius: 12px; width: 90%; max-width: 550px; box-shadow: 0 0 25px rgba(212, 175, 55, 0.2); position: relative; animation: slideIn 0.3s ease-out; color: #fff; }}
            .modal-close {{ position: absolute; top: 15px; right: 15px; background: none; border: none; color: #ff4757; font-size: 24px; cursor: pointer; transition: 0.2s; }}
            .modal-close:hover {{ transform: scale(1.2); }}
            @keyframes slideIn {{ from {{ transform: translateY(-30px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}

            @media print {{
                body {{ background: #fff; padding: 0; font-family: 'Open Sans', Helvetica, sans-serif; }}
                .no-print, .web-controls {{ display: none !important; }}
                .container {{ box-shadow: none; border-top: none; padding: 0; }}
                .turno-box {{ border: 1px solid #000; page-break-inside: avoid; }}
                .turno-title {{ background: #eee !important; color: #000 !important; border-bottom: 1px solid #000; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
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
            <div class="sello-anio no-print">AÑO {anio}</div>
            <div class="header">
                <img src="{img_b64}" alt="Escudo Mayordomia" class="logo-img" style="{'display:none' if not img_b64 else ''}">
                <h1>OFS Muy Ilustre Mayordomía de Nuestro Padre Jesús Nazareno</h1>
                <h2>Orden Procesional - {tipo}</h2>
                <p>Fecha de emisión: {fecha_hoy} | Cuadrante del Año: {anio}</p>
            </div>
            
            <div class="leyenda">
                <div class="leyenda-item"><span class="caja bg-amarillo"></span> Repite Trono (Turnos seguidos)</div>
                <div class="leyenda-item"><span class="caja bg-azul"></span> Carga Alterna (Trono y Cruz)</div>
                <div class="leyenda-item"><span class="caja bg-rojo"></span> Sobreesfuerzo Crítico (Consecutivos)</div>
            </div>
    """

    for categoria, turnos in datos_tronos.items():
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
                
                html += "<div class='seccion-mid'>▼ TRONO ▼</div>"
                
                if "Detras" in secciones:
                    html += "<ul class='lista-costaleros'>"
                    for p in secciones["Detras"]:
                        html += generar_li_costalero(p)
                    html += "</ul>"
                    html += "<div class='seccion-bot'>▼ DETRÁS ▼</div>"
                
                html += "</div>"
            html += "</div></div>"

    html += bloque_itinerario
    html += bloque_indicaciones

    turnos_json_str = json.dumps(datos_raw)
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
                    filename:     `Orden_Procesional_Agonia_{tipo.replace(" ", "_")}.pdf`,
                    image:        {{ type: 'jpeg', quality: 0.98 }},
                    html2canvas:  {{ scale: 2, useCORS: true }},
                    jsPDF:        {{ unit: 'mm', format: 'a4', orientation: 'portrait' }}
                }};
                
                setTimeout(() => {{
                    html2pdf().set(opt).from(element).save().then(() => {{
                        btn.innerText = "📥 DESCARGAR PDF PARA WHATSAPP";
                    }}).catch(err => {{
                        alert("Error al generar PDF. Asegúrate de tener conexión a Internet.");
                        btn.innerText = "📥 DESCARGAR PDF PARA WHATSAPP";
                    }});
                }}, 150);
            }}
        </script>
    </body>
    </html>
    """
    
    output_file = "informe_generado.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
        
    return True, output_file