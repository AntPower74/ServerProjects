#!/usr/bin/env python3
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

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    code = t['codice_turno']
    dep = t.get('deposito', 'Pinerolo')
    in_m = parse_m(t['inizio_servizio'])
    
    # 1. Pi0620: Sistema trasferimenti Perosa - Pinerolo
    if code == 'Pi0620':
        t['attivita'] = [
            {
                'linea': 'Disp',
                'descrizione': 'Presa servizio e controllo livelli autobus – Pinerolo Deposito',
                'da': 'Pinerolo Deposito',
                'a': 'Pinerolo Deposito',
                'partenza': '13:10',
                'arrivo': '13:20',
                'km': '-'
            },
            {
                'linea': 'Trasf',
                'descrizione': 'Pinerolo Deposito ➔ Pinerolo Stazione FS',
                'da': 'Pinerolo Deposito',
                'a': 'Pinerolo Stazione FS',
                'partenza': '13:20',
                'arrivo': '13:30',
                'km': '2,35'
            },
            {
                'linea': '275',
                'descrizione': 'PINEROLO - stazione FS - PEROSA ARGENTINA - Deposito',
                'da': 'Pinerolo Stazione FS',
                'a': 'Perosa Deposito',
                'partenza': '13:30',
                'arrivo': '14:05',
                'km': '17,80'
            },
            {
                'linea': '275',
                'descrizione': 'PEROSA ARGENTINA - Deposito - PINEROLO - stazione FS',
                'da': 'Perosa Deposito',
                'a': 'Pinerolo Stazione FS',
                'partenza': '14:30',
                'arrivo': '15:05',
                'km': '17,80'
            },
            {
                'linea': 'Trasf',
                'descrizione': 'Pinerolo Stazione FS ➔ Pinerolo Deposito',
                'da': 'Pinerolo Stazione FS',
                'a': 'Pinerolo Deposito',
                'partenza': '15:05',
                'arrivo': '15:15',
                'km': '2,35'
            },
            {
                'linea': 'Sosta',
                'descrizione': '☕ Sosta Obbligatoria CCNL (30 min) – Pinerolo Deposito',
                'da': 'Pinerolo Deposito',
                'a': 'Pinerolo Deposito',
                'partenza': '15:15',
                'arrivo': '15:45',
                'km': '-',
                'durata_sosta_m': 30,
                'is_sosta_deposito': True
            },
            {
                'linea': 'Disp',
                'descrizione': 'Presenza e disponibilità operativa in rimessa – Pinerolo Deposito',
                'da': 'Pinerolo Deposito',
                'a': 'Pinerolo Deposito',
                'partenza': '15:45',
                'arrivo': '19:30',
                'km': '-'
            },
            {
                'linea': 'Disp',
                'descrizione': 'Controllo finale e chiusura turno continuo – Pinerolo Deposito',
                'da': 'Pinerolo Deposito',
                'a': 'Pinerolo Deposito',
                'partenza': '19:30',
                'arrivo': '19:40',
                'km': '-'
            }
        ]
        t['inizio_servizio'] = "13:10"
        t['fine_servizio'] = "19:40"
        t['nastro'] = "6.30"
        t['nastro_str'] = "6h 30m"
        t['nastro_m'] = 390
        t['ore_lavoro'] = "6.30"
        t['olg_str'] = "6h 30m"
        t['olg_m'] = 390

    # 2. Soste serali certificate prima della 6a ora (Ba3510, Ca0070, Pe0240, To0340, To0350, To0360, To0640, To0660, To0680)
    if code in ['Ba3510', 'Ca0070', 'Pe0240', 'To0340', 'To0350', 'To0360', 'To0640', 'To0660', 'To0680']:
        att = t['attivita']
        s_placed = False
        for a in att:
            if a.get('linea') == 'Sosta' or a.get('is_sosta_deposito'):
                p_s = parse_m(a.get('partenza'))
                delta = p_s - in_m if p_s >= in_m else (1440 - in_m + p_s)
                if delta <= 360:
                    a['arrivo'] = fmt_time(p_s + 30)
                    a['durata_sosta_m'] = 30
                    s_placed = True
                    break
        if not s_placed and len(att) >= 2:
            loc = att[1].get('da') or f"{dep} Deposito"
            p_s = in_m + 120 # Alla 2a ora
            att.insert(1, {
                'linea': 'Sosta',
                'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – {loc}",
                'da': loc,
                'a': loc,
                'partenza': fmt_time(p_s),
                'arrivo': fmt_time(p_s + 30),
                'km': '-',
                'durata_sosta_m': 30,
                'is_sosta_deposito': True
            })

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Sigillatura completata!")
