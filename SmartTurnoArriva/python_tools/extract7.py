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
        lines = []
        for w in words:
            matched_line = None
            for l in lines:
                if abs(l[0]['top'] - w['top']) < 4:
                    matched_line = l
                    break
            if matched_line:
                matched_line.append(w)
            else:
                lines.append([w])
            
        lines.sort(key=lambda l: l[0]['top'])
        
        block_trips = []
        all_page_trips = []
        
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
        
        def assign_metadata(line_words, prefix, key_name, current_trips):
            prefix_len = len(prefix)
            curr_len = 0
            val_words = []
            for w in line_words:
                if curr_len >= prefix_len:
                    val_words.append(w)
                else:
                    curr_len += len(w['text'])
            
            for w in val_words:
                t = w['text'].strip()
                if not t: continue
                x = w['x0']
                trip_found = False
                for trip in current_trips:
                    if abs(trip['x'] - x) < 15:
                        trip[key_name] = t
                        trip_found = True
                        break
                if not trip_found:
                    current_trips.append({
                        'x': x,
                        'stops': {},
                        key_name: t
                    })

        for line_words in lines:
            line_words = sorted(line_words, key=lambda w: w['x0'])
            line_text = " ".join([w['text'] for w in line_words])
            
            if line_text.startswith("Stagionalità corsa"):
                if block_trips:
                    all_page_trips.extend(block_trips)
                block_trips = []
                assign_metadata(line_words, "Stagionalità corsa", "stagionalita", block_trips)
                continue
                
            if line_text.startswith("Giorni di effettuazione"):
                assign_metadata(line_words, "Giorni di effettuazione", "giorni", block_trips)
                continue
                
            if line_text.startswith("NOTE:"):
                assign_metadata(line_words, "NOTE:", "note", block_trips)
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
                    if re.match(r'^(\d{1,2}[:.]\d{2}|[A-Z#])$', t):
                        x = w['x0']
                        trip_found = False
                        for trip in block_trips:
                            if abs(trip['x'] - x) < 15:
                                trip['stops'][matched_stop] = t
                                trip_found = True
                                break
                        if not trip_found:
                            block_trips.append({
                                'x': x,
                                'stops': {matched_stop: t},
                            })
                            
        if block_trips:
            all_page_trips.extend(block_trips)
                            
        for trip in all_page_trips:
            if len(trip['stops']) > 1:
                trip_data = dict(trip['stops'])
                trip_data['_giorni'] = trip.get('giorni', '')
                trip_data['_stagionalita'] = trip.get('stagionalita', '')
                trip_data['_note'] = trip.get('note', '')
                trips.append(trip_data)

js_content = f"const tripsData = {json.dumps(trips)};"
with open("/root/orari-app/data.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"Saved {len(trips)} trips to data.js!")
