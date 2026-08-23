#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

perosa = [t for t in turni if t['codice_turno'].startswith('Pe') or 'PEROSA' in t.get('deposito','').upper() or 'Pe' in t['codice_turno']]
pinerolo = [t for t in turni if t['codice_turno'].startswith('Pi')]

def parse_m(t_str):
    if not t_str: return 0
    p = str(t_str).strip().replace('.', ':').replace(',', ':').split(':')
    if len(p) == 1: return int(float(p[0])) * 60
    return int(p[0]) * 60 + int(p[1])

def fmt_hm(m):
    return f"{int(m)//60}h {int(m)%60:02d}m"

print("=== TURNI DEL DEPOSITO DI PEROSA ARGENTINA ===")
for t in turni:
    code = t['codice_turno']
    if code.startswith('Pe'):
        n = parse_m(t['nastro'])
        o = parse_m(t['ore_lavoro'])
        in_s = t['attivita'][0]['partenza'] if t.get('attivita') else ''
        out_s = t['attivita'][-1]['arrivo'] if t.get('attivita') else ''
        print(f"• {code:6s} ({t['nome_turno'][:22]:22s}) | {in_s} - {out_s} | Nastro: {fmt_hm(n):7s} | OLG: {fmt_hm(o):7s} | Riprese: {t.get('num_riprese')}")

print("\n=== CORSE SU PEROSA ARGENTINA EFFETTUATE DA PINEROLO ===")
for t in pinerolo:
    code = t['codice_turno']
    att_perosa = [a for a in t.get('attivita',[]) if 'PEROSA' in a.get('da','').upper() or 'PEROSA' in a.get('a','').upper()]
    if att_perosa:
        print(f"\n--- {code} ({t['nome_turno']}) | Nastro: {t['nastro']} | OLG: {t['ore_lavoro']} ---")
        for a in t.get('attivita', []):
            print(f"   {a['partenza']} - {a['arrivo']} | {a['linea']:5s} | {a['da']} -> {a.get('a','')}")
