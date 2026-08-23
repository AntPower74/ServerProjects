import json

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'To0660':
        print(f"Turno To0660:")
        print(f"  Nastro: {t.get('nastro_str')} (m: {t.get('nastro_m')})")
        print(f"  OLG: {t.get('olg_str')} (m: {t.get('olg_m')})")
        print(f"  Inizio: {t.get('inizio_servizio')} - Fine: {t.get('fine_servizio')}")
        print("  Attività:")
        for a in t.get('attivita', []):
            print(f"    [{a.get('partenza')} -> {a.get('arrivo')}] {a.get('linea')} - {a.get('descrizione')}")
