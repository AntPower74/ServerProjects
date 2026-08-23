#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

pi_turni = [t for t in turni if t['codice_turno'].startswith('Pi')]
print(f"📊 VERIFICA PINEROLO ({len(pi_turni)} Turni):")
for t in pi_turni[:10]:
    print(f"{t['codice_turno']:8s} | Nastro: {t['nastro_str']:8s} | OLG: {t['olg_str']:8s} | Riprese: {t['num_riprese']} | Orario: {t['inizio_servizio']} -> {t['fine_servizio']}")

n_med = sum(t['nastro_m'] for t in pi_turni) // len(pi_turni)
print(f"Nastro Medio Pinerolo: {n_med//60}h {n_med%60:02d}m")
