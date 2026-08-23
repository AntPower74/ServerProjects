#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

torino = [t for t in turni if t['codice_turno'].startswith('To') or 'TORINO' in t.get('deposito','').upper() or 'To' in t['codice_turno']]
pinerolo = [t for t in turni if t['codice_turno'].startswith('Pi')]
perosa = [t for t in turni if t['codice_turno'].startswith('Pe')]

def parse_m(t_str):
    if not t_str: return 0
    p = str(t_str).strip().replace('.', ':').replace(',', ':').split(':')
    if len(p) == 1: return int(float(p[0])) * 60
    return int(p[0]) * 60 + int(p[1])

def fmt_hm(m):
    return f"{int(m)//60}h {int(m)%60:02d}m"

print(f"=== TOTALE TURNI TORINO: {len(torino)} ===")

# Trova turni di Torino che scendono a Pinerolo o Perosa
turni_to_interagenti = []
for t in torino:
    code = t['codice_turno']
    att = t.get('attivita', [])
    toccano = [a for a in att if 'PINEROLO' in a.get('da','').upper() or 'PINEROLO' in a.get('a','').upper() or 'PEROSA' in a.get('da','').upper() or 'PEROSA' in a.get('a','').upper() or a.get('linea') in ['275', '282', '277', '284']]
    if toccano:
        n = parse_m(t['nastro'])
        o = parse_m(t['ore_lavoro'])
        in_s = att[0]['partenza'] if att else ''
        out_s = att[-1]['arrivo'] if att else ''
        turni_to_interagenti.append((code, t['nome_turno'], in_s, out_s, n, o, len(att), t))

print(f"\n=== TURNI DI TORINO CHE SCENDONO A PINEROLO / PEROSA ({len(turni_to_interagenti)} Turni) ===")
for code, nome, in_s, out_s, n, o, n_att, t in sorted(turni_to_interagenti, key=lambda x: x[4], reverse=True):
    print(f"• {code:6s} ({nome[:25]:25s}) | {in_s} - {out_s} | Nastro: {fmt_hm(n):7s} | OLG: {fmt_hm(o):7s} | Attività: {n_att}")

