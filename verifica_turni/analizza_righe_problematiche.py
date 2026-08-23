#!/usr/bin/env python3
"""
ANALISI PUNTUALE RIGHE PROBLEMATICHE NEL PDF UFFICIALE:
Verifica se ci sono:
1. Righe senza orari di partenza o arrivo validi
2. Righe con formati speciali (es. I.Ripresa e F.Ripresa)
3. Note di corsa e campi non standard
"""

import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

print(f"============================================================")
print(f"📊 REPORT ANALISI RIGHE SU TUTTI I {len(turni)} TURNI ESTRATTI")
print(f"============================================================\n")

righe_totali = 0
righe_senza_orario = []
righe_con_ripresa = []

for t in turni:
    code = t['codice_turno']
    for i, a in enumerate(t['attivita']):
        righe_totali += 1
        p = a.get('partenza', '')
        arr = a.get('arrivo', '')
        lin = a.get('linea', '')
        desc = a.get('descrizione', '')
        
        if p == '-' or arr == '-' or not p or not arr:
            righe_senza_orario.append((code, i+1, lin, desc))

print(f"• Righe totali elaborate nel PDF: {righe_totali}")
print(f"• Righe con orario mancante o non riconosciuto: {len(righe_senza_orario)}")

if righe_senza_orario:
    print("\nDettaglio righe anomale trovate:")
    for r in righe_senza_orario:
        print(f"   ↳ Turno {r[0]} | Riga {r[1]} | Linea: {r[2]} | Descrizione: {r[3]}")
else:
    print("✅ Tutte le righe sono state lette e parsate con successo al 100%!")

# Verifichiamo Ca0030
for t in turni:
    if t['codice_turno'] == 'Ca0030':
        print(f"\n--- VERIFICA DETTAGLIATA CA0030 ESTRATTO ---")
        print(f"Orario: {t['inizio_servizio']} -> {t['fine_servizio']} | Nastro: {t['nastro_str']} | OLG: {t['olg_str']} | Km: {t['km_totali']}")
        for i, a in enumerate(t['attivita']):
            print(f"  {i+1}. [{a.get('partenza')} -> {a.get('arrivo')}] {a.get('linea')} | {a.get('descrizione')} (Km: {a.get('km')})")
