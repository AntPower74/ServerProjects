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
    nome = t['nome_turno']
    
    # Pulizia orari scorte
    if 'SCORTA' in nome.upper() or code in ['To5010', 'To5030', 'To6010', 'To6020', 'To6030', 'To6040', 'Ca6010', 'Ca6020', 'Pe5010']:
        dep = t.get('deposito', 'Deposito')
        if code == 'To6040':
            in_t, fin_t = "09:00", "15:00" # 6h esatte
        elif code == 'To5010':
            in_t, fin_t = "03:30", "10:00" # 6h30
        elif code == 'To5030':
            in_t, fin_t = "11:30", "18:00" # 6h30
        elif code == 'To6010':
            in_t, fin_t = "06:00", "14:00" # 8h00
        elif code == 'To6020':
            in_t, fin_t = "14:00", "22:00" # 8h00
        elif code == 'To6030':
            in_t, fin_t = "22:00", "06:00" # 8h00
        elif code == 'Ca6010':
            in_t, fin_t = "11:00", "18:00" # 7h00
        elif code == 'Ca6020':
            in_t, fin_t = "08:00", "15:00" # 7h00
        elif code == 'Pe5010':
            in_t, fin_t = "04:00", "10:00" # 6h00
        else:
            in_t, fin_t = t['inizio_servizio'], t['fine_servizio']
            
        in_m = parse_m(in_t)
        fin_m = parse_m(fin_t)
        nastro_m = fin_m - in_m if fin_m >= in_m else (1440 - in_m + fin_m)
        s_mid_m = (in_m + (nastro_m // 2) - 15) % 1440
        s_mid_end_m = (s_mid_m + 30) % 1440
        
        t['inizio_servizio'] = in_t
        t['fine_servizio'] = fin_t
        t['nastro'] = f"{nastro_m/60:.2f}"
        t['nastro_str'] = fmt_durata(nastro_m)
        t['nastro_m'] = nastro_m
        t['ore_lavoro'] = f"{nastro_m/60:.2f}"
        t['olg_str'] = fmt_durata(nastro_m)
        t['olg_m'] = nastro_m
        t['num_riprese'] = '1,00'
        t['num_riprese_val'] = 1
        
        t['attivita'] = [
            {
                'linea': 'Disp',
                'descrizione': f"Presa servizio e disponibilità scorta / riserva – {dep} Deposito",
                'da': f"{dep} Deposito",
                'a': f"{dep} Deposito",
                'partenza': in_t,
                'arrivo': fmt_time(s_mid_m),
                'km': '-'
            },
            {
                'linea': 'Sosta',
                'descrizione': f"☕ Sosta Obbligatoria / Pausa Mensa CCNL (30 min) – {dep} Deposito",
                'da': f"{dep} Deposito",
                'a': f"{dep} Deposito",
                'partenza': fmt_time(s_mid_m),
                'arrivo': fmt_time(s_mid_end_m),
                'km': '-',
                'durata_sosta_m': 30,
                'is_sosta_deposito': True
            },
            {
                'linea': 'Disp',
                'descrizione': f"Disponibilità scorta e chiusura turno – {dep} Deposito",
                'da': f"{dep} Deposito",
                'a': f"{dep} Deposito",
                'partenza': fmt_time(s_mid_end_m),
                'arrivo': fin_t,
                'km': '-'
            }
        ]

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Turni di scorta e chiusure rifiniti!")
