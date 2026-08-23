#!/usr/bin/env python3
"""
Parser completo di tutti i 175 cartellini dal PDF ufficiale 'Cartellini lun-ven 2026.pdf'
"""

import fitz # PyMuPDF
import json
import re
import os

PDF_PATH = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini lun-ven 2026.pdf"
JSON_OUT = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json"
WEB_JSON_OUT = "/home/antonio/verifica_turni/web/turni_data.json"

print(f"🔄 Inizio parsing da: {PDF_PATH}")
doc = fitz.open(PDF_PATH)

turni_totali = []

for page_idx in range(len(doc)):
    page = doc[page_idx]
    text = page.get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # 1. Estrazione Intestazione Turno
    codice_turno = ""
    nome_turno = ""
    for i, line in enumerate(lines):
        if "Cartellino di marcia del turno:" in line and i + 1 < len(lines):
            codice_turno = lines[i+1].strip()
        if line.startswith("TURNO ") and not nome_turno:
            nome_turno = line.replace("Turno:", "").strip()

    if not codice_turno and lines:
        for l in lines[:10]:
            if re.match(r'^[A-Za-z]{2}\d{3,4}$', l):
                codice_turno = l
                break

    # Determina deposito dal prefisso
    deposito = "Pinerolo"
    if codice_turno.startswith("Pi"):
        deposito = "Pinerolo"
    elif codice_turno.startswith("Pe"):
        deposito = "Perosa Argentina"
    elif codice_turno.startswith("To"):
        deposito = "Torino"
    elif codice_turno.startswith("Ba"):
        deposito = "Barge"
    elif codice_turno.startswith("Po"):
        deposito = "Pont"
    elif codice_turno.startswith("Iv"):
        deposito = "Ivrea"
    elif codice_turno.startswith("Su"):
        deposito = "Susa"
    elif codice_turno.startswith("Mo"):
        deposito = "Moncalieri"
    elif codice_turno.startswith("Ca"):
        deposito = "Carmagnola"
    elif codice_turno.startswith("Ch"):
        deposito = "Chivasso"

    # 2. Estrazione Parametri di Riepilogo (Nastro, OLG, Guida, Riprese)
    nastro = ""
    ore_lavoro = ""
    ore_guida = ""
    inizio_servizio = ""
    fine_servizio = ""
    num_riprese = "1,00"

    for i, line in enumerate(lines):
        if "ORE LAVORO GIORNALIERO" in line and i + 1 < len(lines):
            ore_lavoro = lines[i+1].replace(',', '.')
        if "Nastro del turno" in line and i + 1 < len(lines):
            nastro = lines[i+1].replace(',', '.')
        if "ORE DI GUIDA COMPLESSIVA" in line and i + 1 < len(lines):
            ore_guida = lines[i+1].replace(',', '.')
        if "INIZIO SERVIZIO" in line and i + 1 < len(lines):
            inizio_servizio = lines[i+1].replace('.', ':')
        if "FINE SERVIZIO" in line and i + 1 < len(lines):
            fine_servizio = lines[i+1].replace('.', ':')
        if "NUMERO RIPRESE" in line and i + 1 < len(lines):
            num_riprese = lines[i+1]

    # 3. Estrazione Attività / Righe del Cartellino
    # Usiamo page.get_tables() o l'analisi dei blocchi testo per precisione
    blocchi = page.get_text("blocks")
    # Ordiniamo i blocchi per coordinata y
    blocchi_ordinati = sorted(blocchi, key=lambda b: (round(b[1] / 10) * 10, b[0]))

    attivita = []
    
    # Cerchiamo le righe con orari 'HH.MM' o 'HH:MM'
    riga_orario_pattern = re.compile(r'(\d{1,2}[\.:]\d{2})\s+(\d{1,2}[\.:]\d{2})')
    
    for l in lines:
        match_orario = riga_orario_pattern.search(l)
        if match_orario and (" - " in l or "Disp" in l or "Trasf" in l or "Controllo" in l or "Pulizia" in l or any(c.isdigit() for c in l)):
            p_str = match_orario.group(1).replace('.', ':')
            arr_str = match_orario.group(2).replace('.', ':')
            
            # Linea
            lin = "Tratta"
            if "Disp" in l or "Controllo" in l or "Pulizia" in l:
                lin = "Disp"
            elif "Trasf" in l:
                lin = "Trasf"
            else:
                match_lin = re.search(r'000(\d{3})|Linea\s*(\d{3})|(\d{3})', l)
                if match_lin:
                    lin = match_lin.group(1) or match_lin.group(2) or match_lin.group(3)

            # Da / A
            da = l
            a = ""
            if " - " in l:
                parts = l.split(" - ")
                da = parts[0].strip()
                a = parts[1].strip()

            attivita.append({
                'linea': lin,
                'descrizione': l,
                'da': da,
                'a': a,
                'partenza': p_str,
                'arrivo': arr_str,
                'km': '-'
            })

    # Pulizia orari se mancanti
    if attivita:
        if not inizio_servizio:
            inizio_servizio = attivita[0]['partenza']
        if not fine_servizio:
            fine_servizio = attivita[-1]['arrivo']

    turno_dict = {
        'codice_turno': codice_turno or f"Turno_{page_idx+1}",
        'nome_turno': nome_turno or codice_turno,
        'deposito': deposito,
        'inizio_servizio': inizio_servizio,
        'fine_servizio': fine_servizio,
        'nastro': nastro or "0.00",
        'ore_lavoro': ore_lavoro or "0.00",
        'ore_guida': ore_guida or "0.00",
        'num_riprese': num_riprese,
        'attivita': attivita
    }
    turni_totali.append(turno_dict)

# Salvataggio JSON
with open(JSON_OUT, 'w', encoding='utf-8') as f:
    json.dump(turni_totali, f, ensure_ascii=False, indent=2)

with open(WEB_JSON_OUT, 'w', encoding='utf-8') as f:
    json.dump(turni_totali, f, ensure_ascii=False, indent=2)

print(f"✅ PARSING COMPLETATO CON SUCCESSO!")
print(f"📄 Totale Turni Estratti Direttamente dal PDF: {len(turni_totali)}")
print(f"💾 Salvato in: {JSON_OUT}")
print(f"🌐 Aggiornato dataset per il sito web in: {WEB_JSON_OUT}")

