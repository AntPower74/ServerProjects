#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

perosa = [t for t in turni if t['codice_turno'].startswith('Pe')]

def parse_m(t_str):
    if not t_str: return 0
    p = str(t_str).strip().replace('.', ':').replace(',', ':').split(':')
    if len(p) == 1: return int(float(p[0])) * 60
    return int(p[0]) * 60 + int(p[1])

def fmt_hm(m):
    return f"{int(m)//60}h {int(m)%60:02d}m"

print(f"=== TUTTI I {len(perosa)} TURNI DEL DEPOSITO DI PEROSA ARGENTINA ===")
for t in perosa:
    code = t['codice_turno']
    n = parse_m(t['nastro'])
    o = parse_m(t['ore_lavoro'])
    in_s = t['attivita'][0]['partenza'] if t.get('attivita') else ''
    out_s = t['attivita'][-1]['arrivo'] if t.get('attivita') else ''
    print(f"\n🔹 {code:6s} ({t['nome_turno']}) | {in_s} - {out_s} | Nastro: {fmt_hm(n)} | OLG: {fmt_hm(o)} | Riprese: {t.get('num_riprese')}")
    for a in t.get('attivita', []):
        print(f"   {a['partenza']} - {a['arrivo']} | {a['linea']:5s} | {a['da']} -> {a.get('a','')}")
