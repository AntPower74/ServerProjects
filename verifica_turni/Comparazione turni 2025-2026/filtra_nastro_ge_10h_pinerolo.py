#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = [t for t in turni if t['codice_turno'].startswith('Pi')]

def parse_m(t):
    if not t: return 0
    t = str(t).replace(',', '.').replace(':', '.')
    p = t.split('.')
    if len(p) == 2:
        return int(p[0]) * 60 + int(p[1])
    return int(p[0]) * 60

def fmt_hm(m):
    return f"{m//60}h {m%60:02d}m"

ge_10h = []

for t in pinerolo:
    nas_str = t.get('nastro', '')
    nas_m = parse_m(nas_str)
    if nas_m >= 600: # >= 10h00
        ge_10h.append((nas_m, t))

ge_10h.sort(key=lambda x: x[0], reverse=True)

print(f"=== TURNI PINEROLO CON NASTRO >= 10h00 ({len(ge_10h)} TURNI SU 32) ===\n")
print(f"{'Codice':6s} | {'Nome Turno':22s} | {'Inizio':5s} | {'Fine':5s} | {'Nastro':7s} | {'OLG (Ore Lav)':13s} | {'Ore Guida':9s} | {'Sosta 100%':10s} | {'Sosta 12%':9s} | {'Riprese':7s}")
print("-" * 110)

for nas_m, t in ge_10h:
    code = t['codice_turno']
    name = t['nome_turno'][:22]
    in_s = t.get('inizio_servizio', '')
    out_s = t.get('fine_servizio', '')
    nas = t.get('nastro', '')
    olg = t.get('ore_lavoro', '')
    gui = t.get('ore_guida', '')
    s100 = t.get('sosta_100', '0,00')
    s12 = t.get('sosta_12', '0,00')
    rip = t.get('num_riprese', '1,00')
    print(f"{code:6s} | {name:22s} | {in_s:5s} | {out_s:5s} | {nas:7s} | {olg:13s} | {gui:9s} | {s100:10s} | {s12:9s} | {rip:7s}")
