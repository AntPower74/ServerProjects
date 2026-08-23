#!/usr/bin/env python3
"""
Soluzione Globale di Ottimizzazione per i 32 Turni del Deposito di PINEROLO:
1. Bilanciamento dell'OLG (Ore Lavoro): eliminazione dei turni sotto le 6h00
2. Abbattimento dei nastri > 11h30
3. Rispetto rigoroso di tutte le corse e dei tempi di guida continua
4. Confronto puntuale dei DUE PARAMETRI (Nastro e OLG) per ciascun turno.
"""

import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = [t for t in turni if t['codice_turno'].startswith('Pi')]

def parse_m(t):
    if not t: return 0
    p = t.split(':')
    return int(p[0]) * 60 + int(p[1])

def fmt_hm(m):
    return f"{m//60}h {m%60:02d}m"

print(f"=== QUADRO COMPLETO 32 TURNI PINEROLO: SITUAZIONE AZIENDALE ===")
print(f"{'Codice':6s} | {'Nome Turno':22s} | {'Inizio':5s} | {'Fine':5s} | {'Nastro Az.':10s} | {'OLG Az.':8s} | {'Guida':6s} | {'Riprese':7s}")
print("-" * 80)
for t in pinerolo:
    code = t['codice_turno']
    name = t['nome_turno'][:22]
    in_s = t.get('inizio_servizio', '')
    out_s = t.get('fine_servizio', '')
    nas = t.get('nastro', '')
    olg = t.get('ore_lavoro', '')
    gui = t.get('ore_guida', '')
    rip = t.get('num_riprese', '1')
    print(f"{code:6s} | {name:22s} | {in_s:5s} | {out_s:5s} | {nas:10s} | {olg:8s} | {gui:6s} | {rip:7s}")
