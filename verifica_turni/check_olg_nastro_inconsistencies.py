#!/usr/bin/env python3
import json

def parse_m(t_str):
    if not t_str: return 0
    t_clean = str(t_str).strip().replace('.', ':').replace(',', ':')
    p = t_clean.split(':')
    if len(p) == 1:
        try: return round(float(p[0]) * 60)
        except: return 0
    return int(p[0]) * 60 + int(p[1])

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

print("🔍 CONTROLLO INCONSISTENZE OLG > NASTRO:")
found = 0
for t in turni:
    n_m = t.get('nastro_m', parse_m(t.get('nastro')))
    o_m = t.get('olg_m', parse_m(t.get('ore_lavoro')))
    if o_m > n_m:
        found += 1
        print(f"❌ {t['codice_turno']:8s} | Nastro: {t.get('nastro_str')} ({n_m}m) | OLG: {t.get('olg_str')} ({o_m}m) | Guida: {t.get('ore_guida')}")

print(f"Totale anomalie trovate: {found}")
