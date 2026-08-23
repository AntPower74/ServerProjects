#!/usr/bin/env python3
import json
from collections import defaultdict

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = [t for t in turni if t['codice_turno'].startswith('Pi')]

def parse_m(t):
    if not t: return 0
    p = t.split(':')
    return int(p[0]) * 60 + int(p[1])

def fmt_hm(m):
    return f"{m//60}h {m%60:02d}m"

print(f"=== ANALISI OPPORTUNITÀ DI SCAMBIO CORSE (DEPOSITO PINEROLO) ===\n")

# Mappa turni corti (OLG < 6h00) e turni lunghi (Nastro > 11h30)
turni_corti = []
turni_lunghi = []

for t in pinerolo:
    code = t['codice_turno']
    name = t['nome_turno']
    att = t.get('attivita', [])
    if not att: continue
    
    in_p = att[0]['partenza']
    out_a = att[-1]['arrivo']
    in_m = parse_m(in_p)
    out_m = parse_m(out_a)
    if out_m < in_m: out_m += 24*60
    nastro_m = out_m - in_m
    
    # Guida effettiva
    guida_m = 0
    for a in att:
        if a.get('linea') not in ['Disp', 'Sosta', 'Pausa']:
            p = parse_m(a.get('partenza'))
            arr = parse_m(a.get('arrivo'))
            if arr < p: arr += 24*60
            guida_m += (arr - p)
            
    # Classificazione
    if guida_m < 330: # < 5h30 guida
        turni_corti.append((code, name, in_p, out_a, nastro_m, guida_m, att))
    if nastro_m >= 690: # >= 11h30 nastro
        turni_lunghi.append((code, name, in_p, out_a, nastro_m, guida_m, att))

print("🔴 TURNI CON BASSO OLG / GUIDA (DA INCREMENTARE):")
for c, n, inp, outa, nas, gui, att in turni_corti:
    print(f"• {c:6s} ({n:20s}) | Servizio: {inp} - {outa} | Nastro: {fmt_hm(nas)} | Guida Eff.: {fmt_hm(gui)} | Attività: {len(att)}")

print("\n🔵 TURNI CON NASTRO LUNGO >= 11h30 (DA CUI CEDERE CORSE POMERIDIANE):")
for c, n, inp, outa, nas, gui, att in turni_lunghi:
    print(f"• {c:6s} ({n:20s}) | Servizio: {inp} - {outa} | Nastro: {fmt_hm(nas)} | Guida Eff.: {fmt_hm(gui)} | Attività: {len(att)}")

print("\n" + "="*80)
print("🎯 PROPOSTE SPECIFICHE DI SCAMBIO / INNESTO CORSE:")
print("="*80)

# Esempio 1: Pi0370 (Mattinale che finisce alle 11:45)
print("\n1️⃣ CASO Pi0370 (Attuale: 06:30 - 11:45, Guida: 4h06, Nastro: 5h15)")
print("   • Situazione: Il turno finisce a Pinerolo Deposito alle 11:45 dopo le navette Linea 703.")
print("   • Scambio proposto: Può prendere un blocco pomeridiano (dopo 1h30 di pausa):")
print("     - Opzione A: Riceve da Pi0080 il blocco 12:50 - 14:55 (Linea 901 Pinerolo-Torre Pellice A/R).")
print("       --> Risultato Pi0370: OLG passa da 5h15 a 7h20! Nastro: 8h25 (06:30 - 14:55).")
print("       --> Risultato Pi0080: Nastro scende da 12h30 a 7h00 (inizia alle 12:40 anziché 07:00).")

# Esempio 2: Pi0470 (Attuale: 05:00 - 11:20, Guida: 4h18, Nastro: 6h20)
print("\n2️⃣ CASO Pi0470 (Attuale: 05:00 - 11:20, Guida: 4h18, Nastro: 6h20)")
print("   • Situazione: Finisce a Pinerolo Deposito alle 11:20 dopo il servizio sulla Linea 701.")
print("   • Scambio proposto:")
print("     - Riceve da Pi0210 o Pi0580 la corsa delle 13:10 (Linea 275 Villar Perosa SKF) o 13:30 (Linea 278).")
print("       --> Risultato Pi0470: OLG sale a 6h45 (+1h20).")
print("       --> Risultato Pi0210/Pi0580: Riduzione del nastro di oltre 2 ore.")

# Esempio 3: Pi0280 (Attuale: 06:15 - 16:17, Guida: 4h29, Nastro: 10h02, ha un buco dalle 08:15 alle 13:10)
print("\n3️⃣ CASO Pi0280 (Attuale: 06:15 - 16:17, Guida: 4h29, Nastro: 10h02)")
print("   • Situazione: Ha solo 4h29 di guida perché fa 06:15-08:15, poi sosta fino alle 13:10, e finisce alle 16:17 (Linea 703).")
print("   • Scambio proposto:")
print("     - Inserire tra le 11:00 e le 12:40 le corse di Linea 283 (Cantalupa) attualmente in Pi0030.")
print("       --> Risultato Pi0280: OLG sale da 5h07 a 6h37!")
print("       --> Risultato Pi0030: Elimina una ripresa (passa da 4 riprese a 2 riprese con nastro compatto).")

# Esempio 4: Pi0950 (Attuale: 05:49 - 14:53, Guida: 4h26, Nastro: 9h04, buco 08:20 - 12:05)
print("\n4️⃣ CASO Pi0950 (Attuale: 05:49 - 14:53, Guida: 4h26, Nastro: 9h04)")
print("   • Situazione: Finisce alle 14:53 a Pinerolo Deposito.")
print("   • Scambio proposto:")
print("     - Può coprire la corsa di Linea 281 delle 15:00 - 16:15 (Gerbole di Volvera) di Pi0060.")
print("       --> Risultato Pi0950: OLG sale a 6h40.")
print("       --> Risultato Pi0060: Nastro scende da 11h25 a 9h15.")
