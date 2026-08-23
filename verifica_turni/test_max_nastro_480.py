import json
from test_exact_js_simulation import parse_clock

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

max_nastro = 480 # 8h 00m
conformi = 0

for t in turni:
    nM = t.get('nastro_m') or 0
    nOk = nM <= max_nastro
    if nOk:
        conformi += 1
    else:
        print(f"Sforato con max_nastro 8h: {t['codice_turno']} (Nastro: {t.get('nastro_str')} = {nM}m)")

print(f"\nConformi a 8h: {conformi} / {len(turni)} ({conformi/len(turni)*100:.1f}%)")
