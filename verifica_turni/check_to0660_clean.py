import json

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'To0660':
        print("To0660 Timeline:")
        for idx, a in enumerate(t.get('attivita', [])):
            print(f"  {idx+1}. [{a.get('partenza')} -> {a.get('arrivo')}] {a.get('linea')} : {a.get('descrizione', '')}")
