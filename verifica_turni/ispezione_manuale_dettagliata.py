#!/usr/bin/env python3
"""
ISPEZIONE MANUALE DETTAGLIATA TURNO PER TURNO SU TUTTI I 13 DEPOSITI
"""

import json
from collections import defaultdict

def parse_m(t_str):
    if not t_str: return 0
    t_clean = str(t_str).strip().replace('.', ':').replace(',', ':')
    p = t_clean.split(':')
    if len(p) == 1:
        try: return round(float(p[0]) * 60)
        except: return 0
    return int(p[0]) * 60 + int(p[1])

def fmt_time(m):
    h = (m // 60) % 24
    mins = m % 60
    return f"{h:02d}:{mins:02d}"

def fmt_durata(m):
    if not m or m < 0: return "0h 00m"
    h = m // 60
    mins = m % 60
    return f"{h}h {mins:02d}m"

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

by_dep = defaultdict(list)
for t in turni:
    pref = t['codice_turno'][:2]
    by_dep[pref].append(t)

print("================================================================================")
print("🔍 ISPEZIONE MANUALE APPROFONDITA SUI 13 DEPOSITI AZIENDALI")
print("================================================================================\n")

for pref, lista in sorted(by_dep.items()):
    dep_nome = lista[0].get('deposito', pref)
    print(f"\n🏢 DEPOSITO: {dep_nome.upper()} ({len(lista)} Turni)")
    print("-" * 80)
    
    for t in lista:
        code = t['codice_turno']
        nome = t['nome_turno']
        in_s = t['inizio_servizio']
        fin_s = t['fine_servizio']
        nastro = t['nastro_str']
        olg = t['olg_str']
        rip = t['num_riprese']
        att = t['attivita']
        
        # Check tratte e coerenza geografica
        num_corse_linea = sum(1 for a in att if a.get('linea') not in ['Disp', 'Sosta', 'Trasf'])
        num_soste = sum(1 for a in att if a.get('linea') == 'Sosta' or a.get('is_sosta_deposito'))
        
        # Luoghi di inizio e fine
        primo_luogo = att[0].get('da') if att else dep_nome
        ultimo_luogo = att[-1].get('a') if att else dep_nome
        
        # Tipo turno
        tipo = "Standard"
        if 'SCORTA' in nome.upper(): tipo = "Scorta/Riserva"
        elif 'FUORI' in nome.upper() or code.startswith('FT'): tipo = "Bis/Scolastico"
        elif code in ['Pi0070', 'To6030']: tipo = "Notturno Deposito"
        elif code == 'Bo3020': tipo = "Spezzato Sera-Mattina"
        elif num_corse_linea > 0: tipo = f"Linea ({num_corse_linea} corse)"
        
        print(f"• {code:7s} | {in_s} ➔ {fin_s} | Nastro: {nastro:8s} | OLG: {olg:8s} | Rip: {rip} | Soste: {num_soste} | Tipo: {tipo}")
        print(f"   ↳ Tratta: {primo_luogo} ➔ ... ➔ {ultimo_luogo}")

print("\n================================================================================")
print("ISPEZIONE COMPLETATA CON SUCCESSO")
print("================================================================================")
