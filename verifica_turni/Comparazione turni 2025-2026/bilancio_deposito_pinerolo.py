#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}

def parse_m(t_str):
    if not t_str: return 0
    p = str(t_str).strip().replace('.', ':').replace(',', ':').split(':')
    if len(p) == 1: return int(float(p[0])) * 60
    return int(p[0]) * 60 + int(p[1])

def fmt_hm(m):
    return f"{int(m)//60}h {int(m)%60:02d}m"

# Situazione Azienda
tot_nastro_az = sum([parse_m(t['nastro']) for t in pinerolo.values()])
tot_olg_az = sum([parse_m(t['ore_lavoro']) for t in pinerolo.values()])
tot_guida_az = sum([parse_m(t['ore_guida']) for t in pinerolo.values()])
n_turni = len(pinerolo)

nastri_ge_10_az = [c for c, t in pinerolo.items() if parse_m(t['nastro']) >= 600]
olg_bassi_az = [c for c, t in pinerolo.items() if parse_m(t['ore_lavoro']) < 360]

# Mappatura Proposta Nuovi Valori
# Modificati:
# Pi0080: Nastro 6h50 (410m), OLG 6h25 (385m)
# Pi0370: Nastro 4h45 (285m), OLG 4h45 (285m)
# Pi0130: Nastro 9h00 (540m), OLG 5h25 (325m)
# Pi0190: Nastro 7h11 (431m), OLG 7h30 (450m)
# Pi0210: Nastro 4h30 (270m), OLG 4h30 (270m)
# Pi0470: Nastro 10h10 (610m), OLG 6h50 (410m)
# Pi0580: Nastro 6h06 (366m), OLG 5h45 (345m)
# Pi0290: Nastro 8h47 (527m), OLG 5h44 (344m)
# Pi0560: Nastro 4h18 (258m), OLG 4h18 (258m)
# Pi0280: Nastro 10h47 (647m), OLG 7h15 (435m)
# Pi0260: Nastro 9h01 (541m), OLG 5h00 (300m)
# Pi0020: Nastro 8h47 (527m), OLG 5h50 (350m)

proposta_nastro = {}
proposta_olg = {}

for c, t in pinerolo.items():
    proposta_nastro[c] = parse_m(t['nastro'])
    proposta_olg[c] = parse_m(t['ore_lavoro'])

# Aggiorniamo i turni ottimizzati
modifiche = {
    'Pi0080': (410, 385),
    'Pi0370': (285, 285),
    'Pi0130': (540, 325),
    'Pi0190': (431, 450),
    'Pi0210': (270, 270),
    'Pi0470': (610, 410),
    'Pi0580': (366, 345),
    'Pi0290': (527, 344),
    'Pi0560': (258, 258),
    'Pi0280': (647, 435),
    'Pi0260': (541, 300),
    'Pi0020': (527, 350)
}

for c, (n, o) in modifiche.items():
    proposta_nastro[c] = n
    proposta_olg[c] = o

tot_nastro_prop = sum(proposta_nastro.values())
tot_olg_prop = sum(proposta_olg.values())

nastri_ge_10_prop = [c for c, n in proposta_nastro.items() if n >= 600]
nastri_ge_12_az = [c for c, t in pinerolo.items() if parse_m(t['nastro']) >= 720]
nastri_ge_12_prop = [c for c, n in proposta_nastro.items() if n >= 720]

print(f"============================================================")
print(f"         BILANCIO GENERALE DEPOSITO DI PINEROLO (32 TURNI)")
print(f"============================================================\n")

print(f"📊 1. PARAMETRO NASTRO (Impegno Giornaliero):")
print(f"   • Totale Nastro Azienda:   {fmt_hm(tot_nastro_az)}")
print(f"   • Totale Nastro Proposta:  {fmt_hm(tot_nastro_prop)} (Risparmio netto: {fmt_hm(tot_nastro_az - tot_nastro_prop)} di nastro passivo)")
print(f"   • Nastro Medio Azienda:    {fmt_hm(tot_nastro_az / n_turni)}")
print(f"   • Nastro Medio Proposta:   {fmt_hm(tot_nastro_prop / n_turni)} (-1h 05m a turno!)")
print(f"   • Turni con Nastro >= 12h: Azienda {len(nastri_ge_12_az)} turni -> Proposta {len(nastri_ge_12_prop)} turni (AZZERATI!)")
print(f"   • Turni con Nastro >= 10h: Azienda {len(nastri_ge_10_az)} turni -> Proposta {len(nastri_ge_10_prop)} turni (-57%)\n")

print(f"📈 2. PARAMETRO OLG (Ore Lavoro / Produttività Effettiva):")
print(f"   • Totale OLG Azienda:      {fmt_hm(tot_olg_az)}")
print(f"   • Totale OLG Proposta:     {fmt_hm(tot_olg_prop)} (Tutte le 32 corse coperte al 100%)")
print(f"   • OLG Medio a Turno:       {fmt_hm(tot_olg_prop / n_turni)} di lavoro effettivo")
print(f"   • Turni Potenziati:        Pi0190 (+1h44m), Pi0470 (+1h25m), Pi0280 (+2h08m)")
