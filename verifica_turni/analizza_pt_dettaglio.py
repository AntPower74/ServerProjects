#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

pt_turni = [t for t in turni if t['codice_turno'].startswith('Pt')]

print(f"🏢 ANALISI DETTAGLIATA PONT SAINT MARTIN ({len(pt_turni)} Turni):")
print("-" * 95)
print(f"{'Codice':8s} | {'Nome Turno':28s} | {'Orario':13s} | {'Nastro':8s} | {'OLG':8s} | {'Riprese':8s}")
print("-" * 95)

for t in sorted(pt_turni, key=lambda x: -float(str(x.get('nastro', '0')).replace(',', '.'))):
    print(f"{t['codice_turno']:8s} | {t['nome_turno'][:28]:28s} | {t['inizio_servizio']} - {t['fine_servizio']:5s} | {t['nastro']:8s} | {t['ore_lavoro']:8s} | {str(t.get('num_riprese','1,00')):8s}")
    att = t.get('attivita', [])
    for a in att:
        desc = (a.get('descrizione', '') + ' ' + a.get('da', '') + ' ' + a.get('a', '')).lower()
        if 'torino' in desc or 'porta susa' in desc or 'bolzano' in desc:
            print(f"   🚏 Line {a.get('linea')}: {a.get('partenza')} ➔ {a.get('arrivo')} | {a.get('descrizione')[:50]}")

print("-" * 95)
