import json

def actualizar():
    try:
        with open('datos.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)

        for p in datos:
            p['viernes_santo'] = True
            # Aprovechamos por si alguno no tenía el del miércoles
            if 'miercoles_santo' not in p:
                p['miercoles_santo'] = True

        with open('datos.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

        print("✅ ¡Éxito! El archivo datos.json ha sido actualizado con 'viernes_santo'.")
    except Exception as e:
        print(f"❌ Error actualizando el archivo: {e}")

if __name__ == "__main__":
    actualizar()