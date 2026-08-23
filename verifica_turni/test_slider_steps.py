import json

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for max_n in [360, 420, 480, 540, 600, 630]:
    conformi = sum(1 for t in turni if t.get('nastro_m', 0) <= max_n)
    print(f"Max Nastro = {max_n//60}h {max_n%60:02d}m ({max_n}m) -> Conformi: {conformi}/{len(turni)} ({conformi/len(turni)*100:.1f}%)")
