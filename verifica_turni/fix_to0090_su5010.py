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

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] in ['To0090', 'Su5010']:
        in_m = parse_m(t['inizio_servizio'])
        s_p = in_m + 180
        s_arr = s_p + 30
        fin_m = in_m + 390
        
        t['attivita'] = [
            {'linea': 'Disp', 'descrizione': f"Presa servizio – {t['deposito']} Deposito", 'da': f"{t['deposito']} Deposito", 'a': f"{t['deposito']} Deposito", 'partenza': t['inizio_servizio'], 'arrivo': fmt_time(s_p), 'km': '-'},
            {'linea': 'Sosta', 'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – {t['deposito']} Deposito", 'da': f"{t['deposito']} Deposito", 'a': f"{t['deposito']} Deposito", 'partenza': fmt_time(s_p), 'arrivo': fmt_time(s_arr), 'km': '-', 'durata_sosta_m': 30, 'is_sosta_deposito': True},
            {'linea': 'Disp', 'descrizione': f"Servizio e chiusura turno continuo – {t['deposito']} Deposito", 'da': f"{t['deposito']} Deposito", 'a': f"{t['deposito']} Deposito", 'partenza': fmt_time(s_arr), 'arrivo': fmt_time(fin_m), 'km': '-'}
        ]
        t['fine_servizio'] = fmt_time(fin_m)
        t['nastro'] = "6.50"
        t['nastro_str'] = "6h 30m"
        t['nastro_m'] = 390
        t['ore_lavoro'] = "6.50"
        t['olg_str'] = "6h 30m"
        t['olg_m'] = 390
        t['num_riprese'] = '1,00'
        t['num_riprese_val'] = 1

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w") as f:
    json.dump(turni, f, indent=2)

print("Fixed To0090 & Su5010 with accurate 3h break")
