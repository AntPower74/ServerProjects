import json
import pdfplumber
import re
import os

pdf_path = "/root/000275.pdf"

trips = []

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        words = page.extract_words(x_tolerance=2, y_tolerance=2)
        lines = {}
        for w in words:
            y = round(w['top'] / 3.0) * 3
            if y not in lines:
                lines[y] = []
            lines[y].append(w)
            
        sorted_y = sorted(lines.keys())
        page_trips = []
        
        stop_names = [
            "OULX - Stazione FS", "OULX - Liceo", "OULX - p.zza Garambois", "CESANA TORINESE",
            "SESTRIERE", "PRAGELATO", "FENESTRELLE - via Nazionale", "PEROSA ARG.-pzza Terzo Alpini (Arrivo)",
            "PEROSA ARG.-pzza Terzo Alpini (Partenza)", "PINASCA", "DUBBIONE - via Nazionale",
            "VILLAR PEROSA - via Nazionale", "S. GERMANO CHISONE", "PORTE", "S. MARTINO", "ABBADIA ALPINA",
            "PONTE LEMINA", "PINEROLO - piazza Cavour", "PINEROLO - movicentro (Arrivo)", 
            "PINEROLO - movicentro (Partenza)", "PINEROLO - c.so Torino-MACUMBA", "PINEROLO Centro Studi",
            "RIVA di Pinerolo", "Bivio BOTTEGHE", "AIRASCA", "NONE Bivio", "CANDIOLO IRCCS-Centro Ricerche",
            "STUPINIGI - Palazzina di Caccia", "TORINO - p.zza Carducci", 
            "TORINO -c.so V.Eman. II (Porta Nuova FS)", "TORINO - Autostazione c.so Bolzano"
        ]
        
        for y in sorted_y:
            line_words = sorted(lines[y], key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            
            if line_text.startswith("Giorni di effettuazione"):
                prefix_len = 23
                curr_len = 0
                giorni_words = []
                for w in line_words:
                    if curr_len >= prefix_len:
                        giorni_words.append(w)
                    else:
                        curr_len += len(w['text'])
                
                for w in giorni_words:
                    t = w['text'].strip()
                    x = w['x0']
                    trip_found = False
                    for trip in page_trips:
                        if abs(trip['x'] - x) < 15:
                            trip['giorni'] = t
                            trip_found = True
                            break
                    if not trip_found:
                        page_trips.append({
                            'x': x,
                            'stops': {},
                            'giorni': t
                        })
                continue

            matched_stop = None
            for s in stop_names:
                if line_text.startswith(s):
                    matched_stop = s
                    break
                    
            if matched_stop:
                stop_name_len = len(matched_stop.replace(" ", ""))
                curr_len = 0
                time_words = []
                for w in line_words:
                    if curr_len >= stop_name_len:
                        time_words.append(w)
                    else:
                        curr_len += len(w['text'])
                
                for w in time_words:
                    t = w['text']
                    if re.match(r'^(\d{1,2}[:.]\d{2}|[A-Z])$', t):
                        x = w['x0']
                        trip_found = False
                        for trip in page_trips:
                            if abs(trip['x'] - x) < 15:
                                trip['stops'][matched_stop] = t
                                trip_found = True
                                break
                        if not trip_found:
                            page_trips.append({
                                'x': x,
                                'stops': {matched_stop: t},
                                'giorni': 'Tutti'
                            })
                            
        for trip in page_trips:
            if len(trip['stops']) > 1:
                trip_data = dict(trip['stops'])
                trip_data['_giorni'] = trip.get('giorni', 'Tutti')
                trips.append(trip_data)

os.makedirs("/root/shift-app/src/data", exist_ok=True)
output_path = "/root/shift-app/src/data/trips.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(trips, f, ensure_ascii=False, indent=2)

print("Saved JSON trips!")
