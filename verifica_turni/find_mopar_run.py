import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni_reali = json.load(f)

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni_opt = json.load(f)

print("--- RICERCA IN TURNI REALI (turni_data.json) ---")
for t in turni_reali:
    for a in t.get('attivita', []):
        if '22:15' in str(a.get('partenza')) or '22.15' in str(a.get('partenza')):
            if 'MOPAR' in str(a.get('descrizione', '')).upper() or 'RIVALTA' in str(a.get('descrizione', '')).upper():
                print(f"Trovata in Turno Reale: {t['codice_turno']} ({t.get('nome_turno')}) - Deposito: {t.get('deposito')}")
                print(f"  Attività: {json.dumps(a, indent=4)}")

print("\n--- RICERCA IN TURNI OTTIMIZZATI (turni_ottimizzati_completi.json) ---")
for t in turni_opt:
    for a in t.get('attivita', []):
        if '22:15' in str(a.get('partenza')) or '22.15' in str(a.get('partenza')):
            if 'MOPAR' in str(a.get('descrizione', '')).upper() or 'RIVALTA' in str(a.get('descrizione', '')).upper():
                print(f"Trovata in Turno Ottimizzato: {t['codice_turno']} ({t.get('nome_turno')}) - Deposito: {t.get('deposito')}")
                print(f"  Attività: {json.dumps(a, indent=4)}")

print("\n--- TUTTE LE CORSE DI To0660 (Reale vs Ottimizzato) ---")
for t in turni_reali:
    if t['codice_turno'] == 'To0660':
        print(f"To0660 REALE (Inizio {t.get('inizio_servizio')} - Fine {t.get('fine_servizio')}, Nastro {t.get('nastro')}):")
        for a in t.get('attivita', []):
            print(f"  [{a.get('partenza')} -> {a.get('arrivo')}] {a.get('linea')} - {a.get('descrizione')}")

for t in turni_opt:
    if t['codice_turno'] == 'To0660':
        print(f"\nTo0660 OTTIMIZZATO (Inizio {t.get('inizio_servizio')} - Fine {t.get('fine_servizio')}, Nastro {t.get('nastro_str')}):")
        for a in t.get('attivita', []):
            print(f"  [{a.get('partenza')} -> {a.get('arrivo')}] {a.get('linea')} - {a.get('descrizione')}")
