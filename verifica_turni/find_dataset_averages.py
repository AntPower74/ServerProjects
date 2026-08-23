import json
from motore_ottimo_globale_ortools import parse_m

for fname in ["turni_data.json", "turni_ottimizzati_completi.json", "turni_generati_da_zero.json"]:
    with open(f"/home/antonio/verifica_turni/web/{fname}") as f:
        t_list = json.load(f)
    tot_n = sum(parse_m(t.get('nastro')) for t in t_list)
    tot_o = sum(parse_m(t.get('ore_lavoro')) for t in t_list)
    print(f"File: {fname}")
    print(f"  Count: {len(t_list)}")
    print(f"  Nastro Medio: {tot_n // len(t_list) // 60}h {tot_n // len(t_list) % 60}m ({tot_n / len(t_list):.1f}m)")
    print(f"  OLG Medio: {tot_o // len(t_list) // 60}h {tot_o // len(t_list) % 60}m ({tot_o / len(t_list):.1f}m)")
