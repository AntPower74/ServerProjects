import json

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for i in range(10):
    t = turni[i]
    print(f"Turno: {t.get('codice_turno')} | nastro: '{t.get('nastro')}' (type: {type(t.get('nastro'))}) | ore_lavoro: '{t.get('ore_lavoro')}' | nastro_str: '{t.get('nastro_str')}' | olg_str: '{t.get('olg_str')}'")
