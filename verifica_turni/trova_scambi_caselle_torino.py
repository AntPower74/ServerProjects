#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

ca_turni = [t for t in turni if t['codice_turno'].startswith('Ca')]
to_turni = [t for t in turni if t['codice_turno'].startswith('To') or t['codice_turno'].startswith('Pt')]

print("🔍 ANALISI CORSE CASELLE VERSO TORINO:")
for t in ca_turni:
    print(f"\n• Turno {t['codice_turno']} (Nastro: {t['nastro']}h, OLG: {t['ore_lavoro']}h, Riprese: {t.get('num_riprese')})")
    for a in t.get('attivita', []):
        desc = (a.get('descrizione', '') + ' ' + a.get('da', '') + ' ' + a.get('a', '')).lower()
        if 'torino' in desc or 'carlo felice' in desc or 'porta susa' in desc:
            print(f"   Line {a.get('linea')}: {a.get('partenza')} ➔ {a.get('arrivo')} | {a.get('descrizione')}")

