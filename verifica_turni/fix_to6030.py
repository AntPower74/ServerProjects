#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'To6030':
        t['attivita'] = [
            {
                'linea': 'Disp',
                'descrizione': 'Presa servizio notturno e scorta rimessa – Torino Deposito',
                'da': 'Torino Deposito',
                'a': 'Torino Deposito',
                'partenza': '22:00',
                'arrivo': '01:30',
                'km': '-'
            },
            {
                'linea': 'Sosta',
                'descrizione': '☕ Sosta Obbligatoria Notturna CCNL (30 min) – Torino Deposito',
                'da': 'Torino Deposito',
                'a': 'Torino Deposito',
                'partenza': '01:30',
                'arrivo': '02:00',
                'km': '-',
                'durata_sosta_m': 30,
                'is_sosta_deposito': True
            },
            {
                'linea': 'Disp',
                'descrizione': 'Disponibilità scorta e chiusura turno notturno – Torino Deposito',
                'da': 'Torino Deposito',
                'a': 'Torino Deposito',
                'partenza': '02:00',
                'arrivo': '06:00',
                'km': '-'
            }
        ]

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ To6030 sanato al 100%!")
