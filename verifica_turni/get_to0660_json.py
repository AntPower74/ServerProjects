import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for idx, t in enumerate(turni):
    if t['codice_turno'] == 'To0660':
        print(f"Indice turno #{idx + 1}")
        print(json.dumps(t, indent=2))
        break
