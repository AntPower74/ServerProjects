#!/usr/bin/env python3
"""
INSERIMENTO SOSTA FORMALE CCNL NEI TURNI DI SCORTA E RESIDUI
I turni di scorta (Ca6010, Ca6020, To5010, To5030, To6010, To6020, To6030) in deposito
prevedono la pausa/sosta formale di 30 min alla 4ª ora.
"""

import json

def parse_m(t_str):
    if not t_str: return 0
    t_clean = str(t_str).strip().replace('.', ':').replace(',', ':')
    p = t_clean.split(':')
    if len(p) == 1:
        try: return round(float(p[0]) * 60)
        except: return 0
    return int(p[0]) * 60 + int(p[1])

def fmt_time(m):
    h = (m // 60) % 24
    mins = m % 60
    return f"{h:02d}:{mins:02d}"

def fmt_durata(m):
    if not m or m < 0: return "0h 00m"
    h = m // 60
    mins = m % 60
    return f"{h}h {mins:02d}m"

def sistema_scorte_e_turni(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        turni = json.load(f)

    for t in turni:
        code = t['codice_turno']
        n_m = t.get('nastro_m', parse_m(t.get('nastro')))
        in_m = parse_m(t.get('inizio_servizio'))
        
        # Se è un turno di scorta o supera le 6h senza soste
        if 'SCORTA' in t.get('nome_turno', '').upper() or code in ['To0090', 'Ca6010', 'Ca6020', 'To5010', 'To5030', 'To6010', 'To6020', 'To6030', 'To6040']:
            dep = t.get('deposito', 'Deposito')
            # Sosta a metà turno (es. dopo 3h30m)
            sosta_start_m = (in_m + 210) % 1440
            sosta_end_m = (sosta_start_m + 30) % 1440
            
            t['attivita'] = [
                {
                    'linea': 'Disp',
                    'descrizione': f"Presenza e disponibilità scorta / riserva – {dep}",
                    'da': dep,
                    'a': dep,
                    'partenza': fmt_time(in_m),
                    'arrivo': fmt_time(sosta_start_m),
                    'km': '-'
                },
                {
                    'linea': 'Sosta',
                    'descrizione': f"☕ Sosta Obbligatoria / Pausa Mensa CCNL (30 min) – {dep}",
                    'da': dep,
                    'a': dep,
                    'partenza': fmt_time(sosta_start_m),
                    'arrivo': fmt_time(sosta_end_m),
                    'km': '-',
                    'durata_sosta_m': 30,
                    'is_sosta_deposito': True
                },
                {
                    'linea': 'Disp',
                    'descrizione': f"Disponibilità scorta e chiusura turno – {dep}",
                    'da': dep,
                    'a': dep,
                    'partenza': fmt_time(sosta_end_m),
                    'arrivo': t.get('fine_servizio'),
                    'km': '-'
                }
            ]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(turni, f, ensure_ascii=False, indent=2)

sistema_scorte_e_turni("/home/antonio/verifica_turni/web/turni_data.json")
sistema_scorte_e_turni("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json")
sistema_scorte_e_turni("/home/antonio/verifica_turni/web/turni_generati_da_zero.json")

print("✅ Soste formali nei turni di scorta inserite con successo!")
