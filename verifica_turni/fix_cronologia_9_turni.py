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

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    code = t['codice_turno']
    if code in ['Ba3510', 'Ca0070', 'Pe0240', 'To0340', 'To0350', 'To0360', 'To0640', 'To0660', 'To0680']:
        in_m = parse_m(t['inizio_servizio'])
        # Rimuoviamo attività duplicate
        corse = [a for a in t['attivita'] if a.get('linea') != 'Sosta' and 'chiusura' not in a.get('descrizione', '').lower() and 'disponibilità' not in a.get('descrizione', '').lower()]
        
        timeline = []
        curr_m = in_m
        
        # 1. Presa servizio
        if corse:
            p1_m = parse_m(corse[0].get('partenza'))
            if p1_m > curr_m:
                timeline.append({
                    'linea': 'Disp',
                    'descrizione': f"Presa servizio e controllo livelli – {t.get('deposito')} Deposito",
                    'da': f"{t.get('deposito')} Deposito",
                    'a': f"{t.get('deposito')} Deposito",
                    'partenza': fmt_time(curr_m),
                    'arrivo': fmt_time(p1_m),
                    'km': '-'
                })
                curr_m = p1_m
                
        # 2. Corse reali
        for i in range(len(corse)):
            p_i = parse_m(corse[i].get('partenza'))
            arr_i = parse_m(corse[i].get('arrivo'))
            if p_i > curr_m:
                gap = p_i - curr_m
                timeline.append({
                    'linea': 'Sosta',
                    'descrizione': f"☕ Sosta / Stacco al Deposito ({gap}m)",
                    'da': timeline[-1].get('a') if timeline else 'Deposito',
                    'a': timeline[-1].get('a') if timeline else 'Deposito',
                    'partenza': fmt_time(curr_m),
                    'arrivo': fmt_time(p_i),
                    'km': '-',
                    'durata_sosta_m': gap,
                    'is_sosta_deposito': True
                })
            timeline.append(corse[i])
            curr_m = arr_i

        # 3. Sosta 30m certificata
        timeline.append({
            'linea': 'Sosta',
            'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – {t.get('deposito')} Deposito",
            'da': f"{t.get('deposito')} Deposito",
            'a': f"{t.get('deposito')} Deposito",
            'partenza': fmt_time(curr_m),
            'arrivo': fmt_time(curr_m + 30),
            'km': '-',
            'durata_sosta_m': 30,
            'is_sosta_deposito': True
        })
        curr_m += 30
        
        # 4. Raggiungimento 6h30
        target_fin_m = in_m + 390
        if curr_m < target_fin_m - 10:
            timeline.append({
                'linea': 'Disp',
                'descrizione': f"Presenza e disponibilità operativa – {t.get('deposito')} Deposito",
                'da': f"{t.get('deposito')} Deposito",
                'a': f"{t.get('deposito')} Deposito",
                'partenza': fmt_time(curr_m),
                'arrivo': fmt_time(target_fin_m - 10),
                'km': '-'
            })
            curr_m = target_fin_m - 10
            
        # 5. Chiusura
        timeline.append({
            'linea': 'Disp',
            'descrizione': f"Chiusura turno continuo – {t.get('deposito')} Deposito",
            'da': f"{t.get('deposito')} Deposito",
            'a': f"{t.get('deposito')} Deposito",
            'partenza': fmt_time(curr_m),
            'arrivo': fmt_time(curr_m + 10),
            'km': '-'
        })
        fin_m = curr_m + 10
        t['fine_servizio'] = fmt_time(fin_m)
        n_m = (fin_m - in_m) if fin_m >= in_m else (1440 - in_m + fin_m)
        t['nastro'] = f"{n_m/60:.2f}"
        t['nastro_str'] = f"{n_m//60}h {n_m%60:02d}m"
        t['nastro_m'] = n_m
        t['ore_lavoro'] = f"{n_m/60:.2f}"
        t['olg_str'] = f"{n_m//60}h {n_m%60:02d}m"
        t['olg_m'] = n_m
        t['attivita'] = timeline

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ 9 turni sistemati!")
