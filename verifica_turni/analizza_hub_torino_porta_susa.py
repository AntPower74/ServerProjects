#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

print("🔍 ANALISI HUB TORINO (PORTA SUSA AUTOSTAZIONE & PIAZZA CARLO FELICE)\n")

turni_hub_torino = []

for t in turni:
    code = t['codice_turno']
    dep = t.get('deposito', '')
    att = t.get('attivita', [])
    
    passaggi_ps = []
    passaggi_cf = []
    
    for idx, a in enumerate(att):
        desc = (a.get('descrizione', '') + ' ' + a.get('da', '') + ' ' + a.get('a', '')).lower()
        arr = a.get('arrivo', '')
        part = a.get('partenza', '')
        
        if 'autostazione' in desc or 'porta susa' in desc or 'bolzano' in desc:
            passaggi_ps.append((idx, a.get('linea'), part, arr, a.get('descrizione')))
        if 'carlo felice' in desc or 'porta nuova' in desc:
            passaggi_cf.append((idx, a.get('linea'), part, arr, a.get('descrizione')))

    if passaggi_ps or passaggi_cf:
        nastro_val = float(str(t.get('nastro', '0')).replace(',', '.'))
        turni_hub_torino.append({
            'codice': code,
            'deposito': dep,
            'nome': t.get('nome_turno'),
            'nastro': nastro_val,
            'nastro_str': f"{int(nastro_val)}h {int((nastro_val%1)*60):02d}m",
            'passaggi_ps': passaggi_ps,
            'passaggi_cf': passaggi_cf,
            'tot_passaggi': len(passaggi_ps) + len(passaggi_cf)
        })

print(f"📊 Totale turni che toccano Porta Susa o Carlo Felice: {len(turni_hub_torino)} su 175\n")

# Mostriamo i turni suddivisi per deposito con nastro lungo
turni_hub_lunghi = sorted([t for t in turni_hub_torino if t['nastro'] >= 9.0], key=lambda x: -x['nastro'])

print(f"🔴 TURNI CON NASTRO LUNGO (>= 9h00) CHE TOCCANO TORINO HUB ({len(turni_hub_lunghi)} turni):")
print("-" * 110)
print(f"{'Codice':8s} | {'Deposito':18s} | {'Nastro':10s} | {'Passaggi Porta Susa':25s} | {'Passaggi Carlo Felice'}")
print("-" * 110)

for t in turni_hub_lunghi:
    ps_info = f"{len(t['passaggi_ps'])} passaggi" if t['passaggi_ps'] else "-"
    cf_info = f"{len(t['passaggi_cf'])} passaggi" if t['passaggi_cf'] else "-"
    
    ps_detail = ", ".join([f"{p[1]} ({p[2]}-{p[3]})" for p in t['passaggi_ps'][:2]]) if t['passaggi_ps'] else ""
    cf_detail = ", ".join([f"{p[1]} ({p[2]}-{p[3]})" for p in t['passaggi_cf'][:2]]) if t['passaggi_cf'] else ""
    
    print(f"{t['codice']:8s} | {t['deposito'][:18]:18s} | {t['nastro_str']:10s} | {ps_detail[:35]:35s} | {cf_detail[:35]}")

print("-" * 110)

