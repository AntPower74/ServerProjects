#!/usr/bin/env python3
"""
IMPOSTA IL CARTELLINO REALE ESATTO DI CA0030 DA DOCUMENTO ORIGINALE ARRIVA ITALIA
Inizio: 06:34 | Fine: 14:45 | Nastro: 8h 11m | Km: 123.91 km
"""

import json

attivita_ca0030 = [
    {
        'linea': 'Disp',
        'descrizione': 'Controllo livelli autobus – CASELLE Parcheggio P7',
        'da': 'CASELLE Parcheggio P7',
        'a': 'CASELLE Parcheggio P7',
        'partenza': '06:34',
        'arrivo': '06:44',
        'km': '-'
    },
    {
        'linea': 'Trasf',
        'descrizione': 'CASELLE - PARCHEGGIO P7 ➔ CASELLE Aeroporto',
        'da': 'CASELLE - PARCHEGGIO P7',
        'a': 'CASELLE Aeroporto',
        'partenza': '06:44',
        'arrivo': '06:45',
        'km': '0,40'
    },
    {
        'linea': '268',
        'codice_corsa': 'D6',
        'descrizione': 'CASELLE Aeroporto ➔ TO - piazza Carlo Felice',
        'da': 'CASELLE Aeroporto',
        'a': 'TO - piazza Carlo Felice',
        'partenza': '06:45',
        'arrivo': '07:30',
        'km': '17,49'
    },
    {
        'linea': 'Sosta',
        'descrizione': '☕ Sosta in Banchina (15 min) – piazza Carlo Felice',
        'da': 'piazza Carlo Felice',
        'a': 'piazza Carlo Felice',
        'partenza': '07:30',
        'arrivo': '07:45',
        'km': '-',
        'durata_sosta_m': 15,
        'is_sosta_deposito': True
    },
    {
        'linea': '268',
        'codice_corsa': 'A11',
        'descrizione': 'TO - piazza Carlo Felice ➔ CASELLE Aeroporto',
        'da': 'TO - piazza Carlo Felice',
        'a': 'CASELLE Aeroporto',
        'partenza': '07:45',
        'arrivo': '08:30',
        'km': '16,80'
    },
    {
        'linea': 'Sosta',
        'descrizione': '☕ Sosta in Banchina (15 min) – CASELLE Aeroporto',
        'da': 'CASELLE Aeroporto',
        'a': 'CASELLE Aeroporto',
        'partenza': '08:30',
        'arrivo': '08:45',
        'km': '-',
        'durata_sosta_m': 15,
        'is_sosta_deposito': True
    },
    {
        'linea': '268',
        'codice_corsa': 'D14',
        'descrizione': 'CASELLE Aeroporto ➔ TO - piazza Carlo Felice',
        'da': 'CASELLE Aeroporto',
        'a': 'TO - piazza Carlo Felice',
        'partenza': '08:45',
        'arrivo': '09:24',
        'km': '18,99'
    },
    {
        'linea': 'Trasf',
        'descrizione': 'TO - piazza Carlo Felice ➔ TORINO RIMESSA',
        'da': 'piazza Carlo Felice',
        'a': 'TORINO RIMESSA',
        'partenza': '09:24',
        'arrivo': '09:54',
        'km': '9,15'
    },
    {
        'linea': 'Sosta',
        'descrizione': '☕ Sosta Obbligatoria / Stacco al Deposito (1h 16m) – TORINO RIMESSA',
        'da': 'TORINO RIMESSA',
        'a': 'TORINO RIMESSA',
        'partenza': '09:54',
        'arrivo': '11:10',
        'km': '-',
        'durata_sosta_m': 76,
        'is_sosta_deposito': True
    },
    {
        'linea': 'Trasf',
        'descrizione': 'TORINO DEPOSITO ➔ TO - piazza Carlo Felice',
        'da': 'TORINO DEPOSITO',
        'a': 'piazza Carlo Felice',
        'partenza': '11:10',
        'arrivo': '11:40',
        'km': '8,49'
    },
    {
        'linea': '268',
        'codice_corsa': 'A27',
        'descrizione': 'TO - piazza Carlo Felice ➔ CASELLE Aeroporto',
        'da': 'piazza Carlo Felice',
        'a': 'CASELLE Aeroporto',
        'partenza': '11:45',
        'arrivo': '12:30',
        'km': '16,80'
    },
    {
        'linea': 'Sosta',
        'descrizione': '☕ Sosta in Banchina (15 min) – CASELLE Aeroporto',
        'da': 'CASELLE Aeroporto',
        'a': 'CASELLE Aeroporto',
        'partenza': '12:30',
        'arrivo': '12:45',
        'km': '-',
        'durata_sosta_m': 15,
        'is_sosta_deposito': True
    },
    {
        'linea': '268',
        'codice_corsa': 'D30',
        'descrizione': 'CASELLE Aeroporto ➔ TO - piazza Carlo Felice',
        'da': 'CASELLE Aeroporto',
        'a': 'TO - piazza Carlo Felice',
        'partenza': '12:45',
        'arrivo': '13:24',
        'km': '18,99'
    },
    {
        'linea': 'Sosta',
        'descrizione': '☕ Sosta in Banchina (21 min) – piazza Carlo Felice',
        'da': 'piazza Carlo Felice',
        'a': 'piazza Carlo Felice',
        'partenza': '13:24',
        'arrivo': '13:45',
        'km': '-',
        'durata_sosta_m': 21,
        'is_sosta_deposito': True
    },
    {
        'linea': '268',
        'codice_corsa': 'A35',
        'descrizione': 'TO - piazza Carlo Felice ➔ CASELLE Aeroporto',
        'da': 'piazza Carlo Felice',
        'a': 'CASELLE Aeroporto',
        'partenza': '13:45',
        'arrivo': '14:30',
        'km': '16,80'
    },
    {
        'linea': 'Trasf',
        'descrizione': 'CASELLE Aeroporto ➔ CASELLE - PARCHEGGIO P7',
        'da': 'CASELLE Aeroporto',
        'a': 'CASELLE - PARCHEGGIO P7',
        'partenza': '14:30',
        'arrivo': '14:35',
        'km': '0,40'
    },
    {
        'linea': 'Disp',
        'descrizione': 'Pulizia Interna Autobus – CASELLE Parcheggio P7',
        'da': 'CASELLE Parcheggio P7',
        'a': 'CASELLE Parcheggio P7',
        'partenza': '14:35',
        'arrivo': '14:45',
        'km': '-'
    }
]

# Aggiornamento in entrambi i file JSON
for path in ["/home/antonio/verifica_turni/web/turni_data.json", "/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json"]:
    with open(path) as f:
        turni = json.load(f)
    for t in turni:
        if t['codice_turno'] == 'Ca0030':
            t['inizio_servizio'] = "06:34"
            t['fine_servizio'] = "14:45"
            t['nastro'] = "8.18"
            t['nastro_str'] = "8h 11m"
            t['nastro_m'] = 491
            t['ore_lavoro'] = "6.92"
            t['olg_str'] = "6h 55m"
            t['olg_m'] = 415
            t['num_riprese'] = "1,00"
            t['num_riprese_val'] = 1
            t['km_totali'] = "123,91"
            t['attivita'] = attivita_ca0030
    with open(path, "w", encoding="utf-8") as f:
        json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Ca0030 allineato al 100% al documento originale Arriva Italia!")
