import csv
import json

tripsData = []

with open('/root/foglio.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader) # skip header
    for row in reader:
        if len(row) < 6: continue
        turno = row[0].strip()
        nome = row[1].strip()
        linea = row[2].strip()
        partenza_time = row[3].strip()
        arrivo_time = row[4].strip()
        da_a = row[5].strip()
        
        if not linea or not linea.strip(): continue
        if not partenza_time or not arrivo_time: continue
        
        # We try to split da_a intelligently if possible, 
        # but to keep the table clean, we just use "Partenza" and "Arrivo"
        # and store the route info in _note
        
        trip = {
            "_linea": linea,
            "Partenza": partenza_time,
            "Arrivo": arrivo_time,
            "_note": f"{turno}: {da_a}",
            "_stagionalita": "",
            "_giorni": "1234567" # default to all days since we don't have days in CSV
        }
        tripsData.append(trip)

js_code = "const tripsData = " + json.dumps(tripsData, ensure_ascii=False) + ";\nwindow.db = tripsData;\nwindow.stopsCoords = {};\n"

with open('/root/orari-app/data.js', 'w', encoding='utf-8') as f:
    f.write(js_code)
    
with open('/root/shift-app/public/orari/data.js', 'w', encoding='utf-8') as f:
    f.write(js_code)

print(f"Generated data.js with {len(tripsData)} trips from foglio.csv!")
