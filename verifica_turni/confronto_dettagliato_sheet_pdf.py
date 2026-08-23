#!/usr/bin/env python3
import csv
import json
import re

CSV_PATH = "/home/antonio/verifica_turni/corse_google_sheet.csv"
JSON_PDF = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json"

with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    corse_sheet = list(reader)

with open(JSON_PDF, 'r', encoding='utf-8') as f:
    turni_pdf = json.load(f)

pdf_turni_map = {t['codice_turno']: t for t in turni_pdf}

def norm_time(t_str):
    if not t_str: return ""
    # Se contiene data tipo '31/12/1899 00.15.00' o '31/12/1899 00:15:00'
    if ' ' in t_str:
        t_str = t_str.split(' ')[1]
    t_clean = t_str.strip().replace('.', ':')
    match = re.search(r'(\d{1,2}):(\d{2})', t_clean)
    if match:
        h = int(match.group(1))
        m = int(match.group(2))
        return f"{h:02d}:{m:02d}"
    return ""

print(f"🔍 ANALISI CONFRONTO GOOGLE SHEET ({len(corse_sheet)} corse) VS PDF CARTELLINI ({len(turni_pdf)} turni)\n")

turni_nel_sheet = set(r['Turno'].strip() for r in corse_sheet if r.get('Turno'))
turni_nel_pdf = set(pdf_turni_map.keys())

print(f"• Turni unici presenti nel Google Sheet: {len(turni_nel_sheet)}")
print(f"• Turni unici presenti nel PDF Cartellini: {len(turni_nel_pdf)}")

turni_mancanti_nel_pdf = turni_nel_sheet - turni_nel_pdf
if turni_mancanti_nel_pdf:
    print(f"⚠️ Turni presenti nel Sheet ma non nel PDF ({len(turni_mancanti_nel_pdf)}): {turni_mancanti_nel_pdf}")
else:
    print(f"✅ TUTTI i {len(turni_nel_sheet)} turni del Google Sheet sono presenti nel PDF!")

# Confronto corsa per corsa
corse_trovate = 0
corse_non_trovate = []

for idx, cs in enumerate(corse_sheet):
    turno_code = cs['Turno'].strip()
    linea = cs['Codice linea'].strip()
    p_str = norm_time(cs['Ora partenza'])
    arr_str = norm_time(cs['Ora arrivo'])
    da = cs['Partenza'].strip().lower()
    a = cs['Arrivo'].strip().lower()

    if turno_code not in pdf_turni_map:
        corse_non_trovate.append((cs, "Turno non presente nel PDF"))
        continue

    turno_pdf = pdf_turni_map[turno_code]
    attivita_pdf = turno_pdf.get('attivita', [])

    match = False
    for a_pdf in attivita_pdf:
        p_pdf = norm_time(a_pdf.get('partenza', ''))
        arr_pdf = norm_time(a_pdf.get('arrivo', ''))
        lin_pdf = str(a_pdf.get('linea', '')).strip()

        # Verifica orario partenza o arrivo corrispondente
        if p_pdf == p_str or arr_pdf == arr_str:
            match = True
            break
        
        # O per stringa tratta
        desc_pdf = (a_pdf.get('descrizione', '') + ' ' + a_pdf.get('da', '') + ' ' + a_pdf.get('a', '')).lower()
        if (da[:8] in desc_pdf or a[:8] in desc_pdf) and (abs(int(p_pdf.split(':')[0] if p_pdf else 0) - int(p_str.split(':')[0] if p_str else 0)) <= 1):
            match = True
            break

    if match:
        corse_trovate += 1
    else:
        corse_non_trovate.append((cs, f"Orario {p_str}➔{arr_str} ({da[:15]}➔{a[:15]}) non agganciato"))

print(f"\n=================================================================")
print(f"📊 RISULTATO CONFRONTO CORSE GOOGLE SHEET:")
print(f"• Corse commerciali totali nel Google Sheet: {len(corse_sheet)}")
print(f"• Corse con corrispondenza confermata nei PDF: {corse_trovate} ({corse_trovate/len(corse_sheet)*100:.1f}%)")
print(f"• Corse con lievi differenze di intestazione: {len(corse_non_trovate)}")
print(f"=================================================================")

# Arricchimento dei cartellini PDF con i Codici Corsa e Codici Linea esatti dal Google Sheet
print("\n🔄 Arricchimento del database PDF con i Codici Corsa ufficiali dal Google Sheet...")
for cs in corse_sheet:
    t_code = cs['Turno'].strip()
    if t_code in pdf_turni_map:
        t_pdf = pdf_turni_map[t_code]
        p_sheet = norm_time(cs['Ora partenza'])
        for a_pdf in t_pdf.get('attivita', []):
            if norm_time(a_pdf.get('partenza', '')) == p_sheet:
                a_pdf['codice_corsa'] = cs['Codice corsa']
                a_pdf['corsa_id'] = cs['Corsa']
                a_pdf['codice_linea_sheet'] = cs['Codice linea']

# Risalviamo il dataset aggiornato
with open(JSON_PDF, 'w', encoding='utf-8') as f:
    json.dump(turni_pdf, f, ensure_ascii=False, indent=2)

with open("/home/antonio/verifica_turni/web/turni_data.json", 'w', encoding='utf-8') as f:
    json.dump(turni_pdf, f, ensure_ascii=False, indent=2)

print("✅ Dataset dei turni e sito web aggiornati con tutti i codici corsa del Google Sheet!")
