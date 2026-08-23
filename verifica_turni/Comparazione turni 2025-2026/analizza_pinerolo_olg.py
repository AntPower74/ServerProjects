#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = [t for t in turni if t['codice_turno'].startswith('Pi')]
print(f"Totale Turni Pinerolo: {len(pinerolo)}\n")

for t in pinerolo:
    code = t['codice_turno']
    name = t['nome_turno']
    in_s = t.get('inizio_servizio', '')
    out_s = t.get('fine_servizio', '')
    nastro = t.get('nastro', '')
    ore_lav = t.get('ore_lavoro', '')
    ore_guida = t.get('ore_guida', '')
    sosta_100 = t.get('sosta_100', '0,00')
    sosta_12 = t.get('sosta_12', '0,00')
    riprese = t.get('num_riprese', '1.00')
    att_cnt = len(t.get('attivita', []))
    print(f"{code:6s} | {name:25s} | Inizio: {in_s:5s} | Fine: {out_s:5s} | Nastro: {nastro:5s} | OLG (Ore Lav): {ore_lav:5s} | Guida: {ore_guida:5s} | S100: {sosta_100:4s} | S12: {sosta_12:4s} | Rip: {riprese:4s}")
