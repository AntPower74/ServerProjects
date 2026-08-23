import json
import pdfplumber
import re
import os

pdfs = [
    {
        "file": "/root/000275.pdf",
        "linea": "275/282",
        "stops": [
            "OULX - Stazione FS", "OULX - Liceo", "OULX - p.zza Garambois", "CESANA TORINESE",
            "SESTRIERE", "PRAGELATO", "FENESTRELLE - via Nazionale", "PEROSA ARG.-pzza Terzo Alpini (Arrivo)",
            "PEROSA ARG.-pzza Terzo Alpini (Partenza)", "PINASCA", "DUBBIONE - via Nazionale",
            "VILLAR PEROSA - via Nazionale", "S. GERMANO CHISONE", "PORTE", "S. MARTINO", "ABBADIA ALPINA",
            "PONTE LEMINA", "PINEROLO - piazza Cavour", "PINEROLO - movicentro (Arrivo)", 
            "PINEROLO - movicentro (Partenza)", "PINEROLO - c.so Torino-MACUMBA", "PINEROLO Centro Studi",
            "RIVA DI PINEROLO", "RIVA di Pinerolo", "Bivio BOTTEGHE", "AIRASCA", "NONE Bivio", "CANDIOLO IRCCS-Centro Ricerche",
            "STUPINIGI - Palazzina di Caccia", "TORINO - p.zza Carducci", 
            "TORINO -c.so V.Eman. II (Porta Nuova FS)", "TORINO - Autostazione c.so Bolzano"
        ]
    },
    {
        "file": "/root/000278.pdf",
        "linea": "278",
        "stops": [
            "PINEROLO - Osp. Cottolengo", "PINEROLO - p.za S. Croce", "PINEROLO - Ist. Immacolata", 
            "PINEROLO - via Saluzzo (ENEL)", "PINEROLO - piazza Cavour", "PINEROLO - Stazione FS", 
            "PINEROLO - movicentro", "PINEROLO - Stazione Olimpica", "PINEROLO Centro Studi", 
            "PINEROLO Centro Studi (Corso Torino)", "PINEROLO Poste - via Bignone", "PINEROLO - c.so Torino-MACUMBA", 
            "BAUDENASCA", "RIVA DI PINEROLO", "MACELLO", "BURIASCO", "Bivio MURISENGHI", "STELLA", 
            "Bivio STELLA", "VIGONE", "CERCENASCO", "APPENDINI", "SCALENGHE via Cavour", 
            "PANCALIERI - via Re Umberto 106", "PANCALIERI - via P. Amedeo 62", "VIRLE PIEMONTE - via Carignano", 
            "OSASIO - piazza Castello"
        ]
    },
    {
        "file": "/root/000265.pdf",
        "linea": "265",
        "stops": [
            "TO-p.za Cattaneo-Mirafiori FCA",
            "TO - Autostazione c.so Bolzano",
            "TORINO - c.so G. Cesare",
            "TORINO - c.so G.Cesare (SPAZIO CONAD)",
            "BRANDIZZO - casello A4",
            "CHIVASSO - p.le Alfa-Lancia",
            "VALLO - Chiesa",
            "CHIVASSO - Bivio Mosche",
            "CHIVASSO - Bivio Boschetto (TEMP. SOPPRESSA)",
            "CALUSO - Bivio Carolina (TEMP. SOPPRESSA)",
            "VALLO - Bivio (TEMP. SOPPRESSA)",
            "ARÉ- via Duca degli Abruzzi",
            "CALUSO - Stazione FS",
            "CALUSO - Liceo",
            "CALUSO - via De Brissac",
            "CANDIA - p.zza VII Martiri",
            "MERCENASCO - Stazione FS",
            "MERCENASCO - via Nazionale",
            "STRAMBINO - c.so Torino",
            "STRAMBINO - Stazione FS",
            "CERONE - Bivio",
            "SAN BERNARDO - via Torino",
            "IVREA - loc Banchette",
            "IVREA - Stazione FS",
            "IVREA - Porta Vercelli",
            "IVREA - Porta Aosta",
            "MONTALTO DORA",
            "BORGOFRANCO - Stazione FS",
            "MONTESTRUTTO",
            "SETTIMO VITTONE",
            "TAVAGNASCO - Stazione FS",
            "QUINCINETTO - largo Europa",
            "CAREMA - via Torino",
            "PONT S. MARTIN - Stazione FS",
            "PONT S.MARTIN-pzza IV Novembre",
            "SETTIMO T.SE - casello A4",
            "CHIVASSO - Staz. FS Movicentro",
            "MONTANARO-v.Caviglietti-StazFS",
            "RODALLO - Stazione FS",
            "IVREA - via Di Vittorio",
            "MERCENASCO FS - Navoletto",
            "TORINO-Parcheggio STURA (fermata a richiesta)",
            "TORINO - c.so G.Cesare (IVECO)",
            "TORINO - c.so Giulio Cesare",
            "GRUGLIASCO - via Libertà",
            "TO-Settembrini-Mirafiori FCA"
        ]
    },
    {
        "file": "/root/000283.pdf",
        "linea": "283",
        "stops": [
            "CANTALUPA",
            "FROSSASCO Bivio",
            "ROLETTO",
            "FRAZIONE RONCAGLIA",
            "PINEROLO - via Martiri XXI",
            "PINEROLO Ist. Immacolata",
            "PINEROLO - movicentro",
            "PINEROLO - piazza Cavour"
        ]
    },
    {
        "file": "/root/000303.pdf",
        "linea": "303",
        "stops": [
            "TORINO Autostazione",
            "PINEROLO",
            "PEROSA ARGENTINA arrivo",
            "PEROSA ARGENTINA part.",
            "POMARETTO OSPEDALE",
            "POMARETTO P.LAUSA",
            "POMARETTO P. LAUSA",
            "CHIOTTI",
            "TROSSIERI",
            "PERRERO",
            "PONTE RABBIOSO",
            "POMEYFRE",
            "CROSETTO MIN. GIANNA",
            "RODORETTO BIVIO",
            "VILLA DI PRALI",
            "PRALI GHIGO",
            "SEGGIOVIE"
        ]
    },
    {
        "file": "/root/000901.pdf",
        "linea": "901",
        "stops": [
            "BOBBIO PELLICE",
            "VILLAR PELLICE",
            "CHABRIOLS",
            "SEGG. VANDALINO",
            "S. MARGHERITA",
            "LOMBARIDINI/VOLTA",
            "TORRE PELLICE",
            "LUSERNA - piazza Partigiani",
            "LUSERNA - cimitero",
            "PONTE BIBIANA/FS",
            "BIBIANA",
            "BRICHERASIO",
            "CAPPELLA MORERI",
            "SAN SECONDO CANTINE",
            "SAN SECONDO BIVIO BIMA",
            "PINEROLO - piazza Cavour",
            "PINEROLO Movicentro",
            "PINEROLO - Centro Studi",
            "PINEROLO - staz. Olimpica",
            "PINEROLO - Ist. Immacolata",
            "AIRASCA - Stazione FS",
            "NONE - via Roma",
            "CANDIOLO - Stazione FS",
            "NICHELINO - Stazione FS",
            "SANGONE - Stazione FS",
            "TORINO - stazione Lingotto FS",
            "TO-c.so V.Eman. II-Porta Nuova",
            "TORINO - Autostazione c.so Bolzano",
            "TO - Autostazione c.so Bolzano",
            "PISCINA - v. Umberto I ang. V. Airasca",
            "PISCINA - v.Airasca ang. V. Umberto I"
        ]
    },
    {
        "file": "/root/000285.pdf",
        "linea": "285",
        "stops": [
            "OULX - Stazione FS",
            "AMAZAS",
            "FENILS",
            "CESANA",
            "CLAVIERE",
            "Bivio SEGUIN",
            "SESTRIERE",
            "PINEROLO - Stazione FS",
            "TO - Autostazione c.so Bolzano",
            "PINEROLO - piazza Cavour",
            "SAUZE DI CESANA",
            "SAUZE D'OULX",
            "SAN MARCO",
            "OULX -Scuole",
            "OULX - piazza Garambois",
            "BUSSOLENO",
            "SUSA",
            "GRAVERE",
            "CHIOMONTE",
            "EXILLES",
            "OULX FS"
        ]
    },
    {
        "file": "/root/000267.pdf",
        "linea": "267",
        "stops": [
            "TORINO - Via De Cristoforis (Capolinea)", "TORINO - p.za Carducci", "TORINO - via Nizza -Lingotto Fiere",
            "TORINO - p.za Bengasi", "TORINO - c.soUnione Soviet.-PoveriVecchi", "TORINO - c.so Unione Sov. 409 (p.zza Caio Mario)",
            "TORINO - strada del Drosso", "Bivio MONCALIERI", "NICHELINO - Municipio", "NICHELINO - Stazione FS",
            "NICHELINO-v.XXV Aprile -Scuole", "NICHELINO- strada Debouchè 1-5", "CANDIOLO - via Pinerolo 61/B",
            "GARINO", "VINOVO - Ippodromo -Mondo Juve", "VINOVO - Bivio Torrette", "VINOVO - Tetti Rosa",
            "VINOVO - v. S. Desiderio", "PIOBESI T.SE - Municipio", "PIOBESI T.SE-v.Torino/Costituz",
            "PIOBESI T.SE-v.Torino 41-Capol", "PIOBESI T.SE - c.so Italia 50d", "CARIGNANO-P.zza Donatori Avis"
        ]
    },
    {
        "file": "/root/000268.pdf",
        "linea": "268",
        "stops": [
            "TORINO P.zza Carlo Felice", "TO c.so Bolzano - stallo 13 (Porta Susa)", "TORINO - c.so Umbria/via Livorno",
            "TO \u2013 via Stradella", "TO - Via Stampini", "BORGARO T.SE - via Lanzo/via Martiri",
            "CASELLE T.SE - via Torino, 99", "CASELLE T.SE - str. Aeroporto, 44", "TORINO AEROPORTO (livello Partenze)",
            "TORINO AEROPORTO (livello Arrivi)", "CASELLE T.SE - str.Aerop. (fronte n\u00b0 36)", 
            "CASELLE T.SE - via Torino (fronte n\u00b0 99)", "BORGARO T.SE - via Lanzo, 157", 
            "TO - Str Aeroporto (Ferm.\"VERONESE\")", "TO c.so Bolzano - stallo 5 (Porta Susa)"
        ]
    },
    {
        "file": "/root/000274.pdf",
        "linea": "274",
        "stops": [
            "FERMATE S.S.",
            "SUSA - Stazione FS",
            "Bivio FORESTO",
            "FORESTO",
            "Bivio S.GIORIO",
            "BRUZOLO",
            "Bivio S.DIDERO",
            "Bivio VILLAR FOCCHIARDO",
            "SANT'ANTONINO - Stazione FS",
            "Bivio VAIE",
            "S.AMBROGIO",
            "AVIGLIANA - Stazione FS",
            "LUTHER KING - TEKFOR",
            "CASCINE VICA",
            "LEUMANN - c.so Francia fr",
            "COLLEGNO - c.so Pastrengo",
            "TO-c.so Regina Margherita",
            "LEUMANN - c.so Francia",
            "Bivio CONDOVE"
        ]
    }
]

trips = []

for pdf_info in pdfs:
    pdf_path = pdf_info["file"]
    linea_name = pdf_info["linea"]
    stop_names = pdf_info["stops"]
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(x_tolerance=2, y_tolerance=2)
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
            
            def assign_metadata(line_words, prefix, key_name, current_trips):
                prefix_len = len(prefix.replace(" ", ""))
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

            pending_stop = None
            for line_words in lines:
                line_words = sorted(line_words, key=lambda w: w['x0'])
                line_text = " ".join([w['text'] for w in line_words])
                
                if line_text.startswith("Stagionalità corsa"):
                    if block_trips:
                        all_page_trips.extend(block_trips)
                    block_trips = []
                    assign_metadata(line_words, "Stagionalità corsa", "stagionalita", block_trips)
                    pending_stop = None
                    continue
                    
                if line_text.startswith("Giorni di effettuazione"):
                    assign_metadata(line_words, "Giorni di effettuazione", "giorni", block_trips)
                    pending_stop = None
                    continue
                    
                if line_text.startswith("NOTE:"):
                    assign_metadata(line_words, "NOTE:", "note", block_trips)
                    pending_stop = None
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
                    
                    times_extracted = 0
                    for w in time_words:
                        t = w['text']
                        if re.match(r'^(\d{1,2}[:.]\d{2}|[A-Z#$|\-])$', t):
                            x = w['x0']
                            trip_found = False
                            for trip in block_trips:
                                if abs(trip['x'] - x) < 15:
                                    trip['stops'][matched_stop] = t
                                    trip_found = True
                                    times_extracted += 1
                                    break
                            if not trip_found:
                                block_trips.append({
                                    'x': x,
                                    'stops': {matched_stop: t},
                                })
                                times_extracted += 1
                    
                    if times_extracted == 0:
                        pending_stop = matched_stop
                    else:
                        pending_stop = None
                        
                elif pending_stop:
                    times_extracted = 0
                    for w in line_words:
                        t = w['text']
                        if re.match(r'^(\d{1,2}[:.]\d{2}|[A-Z#$|\-])$', t):
                            x = w['x0']
                            for trip in block_trips:
                                if abs(trip['x'] - x) < 15:
                                    trip['stops'][pending_stop] = t
                                    times_extracted += 1
                                    break
                    if times_extracted > 0:
                        pending_stop = None
                                
            if block_trips:
                all_page_trips.extend(block_trips)
                                
            for trip in all_page_trips:
                if len(trip['stops']) > 1:
                    trip_data = dict(trip['stops'])
                    trip_data['_giorni'] = trip.get('giorni', '')
                    trip_data['_stagionalita'] = trip.get('stagionalita', '')
                    trip_data['_note'] = trip.get('note', '')
                    trip_data['_linea'] = linea_name
                    trips.append(trip_data)

    STOP_ALIASES = {
        "TO c.so Bolzano - stallo 13 (Porta Susa)": "TORINO - Porta Susa",
        "TO c.so Bolzano - stallo 5 (Porta Susa)": "TORINO - Porta Susa",
        "TORINO - Autostazione c.so Bolzano": "TORINO - Porta Susa",

        "TORINO P.zza Carlo Felice": "TORINO - Porta Nuova",
        "TORINO -c.so V.Eman. II (Porta Nuova FS)": "TORINO - Porta Nuova",
        "TORINO - p.za Carducci": "TORINO - Piazza Carducci",
        "TORINO - p.zza Carducci": "TORINO - Piazza Carducci",
        "TORINO AEROPORTO (livello Arrivi)": "TORINO - Aeroporto (Caselle)",
        "TORINO AEROPORTO (livello Partenze)": "TORINO - Aeroporto (Caselle)",
        "PINEROLO - movicentro": "PINEROLO - Movicentro",
        "PINEROLO - movicentro (Arrivo)": "PINEROLO - Movicentro",
        "PINEROLO - movicentro (Partenza)": "PINEROLO - Movicentro",
        "RIVA DI PINEROLO": "RIVA di Pinerolo",
    }
    
    normalized_trips = []
    for trip in trips:
        new_trip = {}
        for k, v in trip.items():
            if k in STOP_ALIASES:
                new_trip[STOP_ALIASES[k]] = v
            else:
                new_trip[k] = v
        normalized_trips.append(new_trip)

    with open('/root/orari-app/data.js', 'w', encoding='utf-8') as f:
        f.write('const tripsData = ')
        json.dump(normalized_trips, f, ensure_ascii=False)
        f.write(';')
        
    with open('/root/shift-app/public/orari/data.js', 'w', encoding='utf-8') as f:
        f.write('const tripsData = ')
        json.dump(normalized_trips, f, ensure_ascii=False)
        f.write(';')
    
    print(f"Saved {len(normalized_trips)} trips to data.js in both directories!")
