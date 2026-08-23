#!/usr/bin/env python3
import fitz
import json
import re

PDF_PATH = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini lun-ven 2026.pdf"
WEB_JSON_OUT = "/home/antonio/verifica_turni/web/turni_data.json"
JSON_OUT = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json"

doc = fitz.open(PDF_PATH)
turni_list = []

for page_idx, page in enumerate(doc):
    lines = [l.strip() for l in page.get_text().split('\n') if l.strip()]
    
    # 1. Trova Codice Turno e Nome
    codice = ""
    nome = ""
    for i, l in enumerate(lines):
        if "Cartellino di marcia del turno:" in l and i + 1 < len(lines):
            codice = lines[i+1].strip()
        if l.startswith("TURNO ") and not nome:
            nome = l.replace("Turno:", "").strip()

    if not codice:
        codice = f"Turno_{page_idx+1}"
    if not nome:
        nome = codice

    # Deposito
    dep = "Pinerolo"
    if codice.startswith("Pi"): dep = "Pinerolo"
    elif codice.startswith("Pe"): dep = "Perosa Argentina"
    elif codice.startswith("To"): dep = "Torino"
    elif codice.startswith("Ba"): dep = "Barge"
    elif codice.startswith("Po"): dep = "Pont"
    elif codice.startswith("Iv"): dep = "Ivrea"
    elif codice.startswith("Su"): dep = "Susa"
    elif codice.startswith("Mo"): dep = "Moncalieri"
    elif codice.startswith("Ca"): dep = "Carmagnola"
    elif codice.startswith("Bo"): dep = "Bobbio Pellice"
    elif codice.startswith("Co"): dep = "Condove"
    elif codice.startswith("Gi"): dep = "Giaveno"

    # 2. Parametri di Sintesi
    nastro, olg, guida, in_s, out_s, riprese = "", "", "", "", "", "1,00"
    for i, l in enumerate(lines):
        if "ORE LAVORO GIORNALIERO" in l and i + 1 < len(lines):
            olg = lines[i+1].replace(',', '.')
        if "Nastro del turno" in l and i + 1 < len(lines):
            nastro = lines[i+1].replace(',', '.')
        if "ORE DI GUIDA COMPLESSIVA" in l and i + 1 < len(lines):
            guida = lines[i+1].replace(',', '.')
        if "INIZIO SERVIZIO" in l and i + 1 < len(lines):
            in_s = lines[i+1].replace('.', ':')
        if "FINE SERVIZIO" in l and i + 1 < len(lines):
            out_s = lines[i+1].replace('.', ':')
        if "NUMERO RIPRESE" in l and i + 1 < len(lines):
            riprese = lines[i+1]

    # 3. Parsing Attività / Corse
    # Le righe della tabella sono comprese tra 'Trasf.' (o 'Controllo livelli') e 'Totali'
    start_idx = 0
    end_idx = len(lines)
    for i, l in enumerate(lines):
        if l in ["Trasf.", "Controllo livelli autobus"] and start_idx == 0:
            start_idx = i if l == "Controllo livelli autobus" else i + 1
        if l == "Totali":
            end_idx = i
            break

    table_lines = lines[start_idx:end_idx]
    attivita = []

    time_regex = re.compile(r'^\d{1,2}\.\d{2}$')
    i = 0
    while i < len(table_lines):
        item = table_lines[i]
        # Se è una descrizione di tratta o attività
        if not time_regex.match(item) and item not in ["Disp", "Trasf", "Totali"] and not re.match(r'^\d+,\d+$', item) and not re.match(r'^000\d{3}$', item):
            desc = item
            partenza = ""
            arrivo = ""
            km = "-"
            linea = "Tratta"
            
            # Cerca i prossimi elementi orari
            j = i + 1
            orari_trovati = []
            while j < len(table_lines) and j <= i + 8:
                next_item = table_lines[j]
                if time_regex.match(next_item):
                    orari_trovati.append(next_item)
                elif re.match(r'^\d+,\d+$', next_item):
                    km = next_item
                elif next_item in ["Disp", "Trasf"]:
                    linea = next_item
                elif re.match(r'^000(\d{3})$', next_item):
                    linea = re.match(r'^000(\d{3})$', next_item).group(1)
                elif not time_regex.match(next_item) and len(orari_trovati) >= 2:
                    # Inizio della prossima tratta
                    break
                j += 1

            if len(orari_trovati) >= 2:
                partenza = orari_trovati[0].replace('.', ':')
                arrivo = orari_trovati[1].replace('.', ':')
            elif len(orari_trovati) == 1:
                partenza = orari_trovati[0].replace('.', ':')

            if "Controllo" in desc or "Pulizia" in desc:
                linea = "Disp"
            elif "PARCHEGGIO" in desc or "Deposito" in desc or "Trasf" in linea:
                if linea == "Tratta": linea = "Trasf"

            da = desc
            a = ""
            if " - " in desc:
                parts = desc.split(" - ")
                da = parts[0].strip()
                a = parts[-1].strip()

            if partenza:
                attivita.append({
                    'linea': linea,
                    'descrizione': desc,
                    'da': da,
                    'a': a,
                    'partenza': partenza,
                    'arrivo': arrivo or partenza,
                    'km': km
                })
            i = j - 1
        i += 1

    if not in_s and attivita: in_s = attivita[0]['partenza']
    if not out_s and attivita: out_s = attivita[-1]['arrivo']

    turni_list.append({
        'codice_turno': codice,
        'nome_turno': nome,
        'deposito': dep,
        'inizio_servizio': in_s,
        'fine_servizio': out_s,
        'nastro': nastro or "0.00",
        'ore_lavoro': olg or "0.00",
        'ore_guida': guida or "0.00",
        'num_riprese': riprese,
        'attivita': attivita
    })

# Salva
with open(WEB_JSON_OUT, 'w', encoding='utf-8') as f:
    json.dump(turni_list, f, ensure_ascii=False, indent=2)

with open(JSON_OUT, 'w', encoding='utf-8') as f:
    json.dump(turni_list, f, ensure_ascii=False, indent=2)

print(f"✅ ESTRATTE TUTTE LE CORSE DI TUTTI I {len(turni_list)} TURNI!")
for t in turni_list[:5]:
    print(f"• {t['codice_turno']} ({t['nome_turno']}) -> {len(t['attivita'])} corse estratte")
