#!/usr/bin/env python3
import csv
import json

CSV_PATH = "/home/antonio/verifica_turni/corse_google_sheet.csv"
JSON_PDF = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json"

with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows_sheet = list(reader)

print(f"📊 Totale righe nel Google Sheet: {len(rows_sheet)}")
if rows_sheet:
    print("📋 Intestazione Google Sheet:", rows_sheet[0])
    for r in rows_sheet[1:6]:
        print("  •", r)

with open(JSON_PDF, 'r', encoding='utf-8') as f:
    turni_pdf = json.load(f)

tot_corse_pdf = sum(len(t.get('attivita', [])) for t in turni_pdf)
print(f"\n📊 Totale turni estratti da PDF: {len(turni_pdf)}")
print(f"📊 Totale corse/attività estratte da PDF: {tot_corse_pdf}")

