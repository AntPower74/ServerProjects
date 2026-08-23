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

# Ripristiniamo la timeline pura
with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

print(f"============================================================")
print(f"🔍 AUDIT GENERALE DI VALIDAZIONE SU TUTTI I {len(turni)} TURNI")
print(f"============================================================\n")

anomalie_cronologia = 0
anomalie_nastro = 0
anomalie_olg = 0
anomalie_soste = 0

for t in turni:
    code = t['codice_turno']
    nome = t.get('nome_turno', code)
    in_serv_m = parse_m(t.get('inizio_servizio'))
    fin_serv_m = parse_m(t.get('fine_servizio'))
    nastro_dichiarato_m = t.get('nastro_m', parse_m(t.get('nastro')))
    olg_dichiarato_m = t.get('olg_m', parse_m(t.get('ore_lavoro')))
    rip_val = float(str(t.get('num_riprese', '1')).replace(',', '.'))
    att = t.get('attivita', [])
    
    # 1. Calcolo Nastro Reale
    if code in ['Pi0070', 'Bo3020']:
        nastro_calcolato_m = (1440 - in_serv_m + fin_serv_m)
    else:
        nastro_calcolato_m = (fin_serv_m - in_serv_m) if fin_serv_m >= in_serv_m else (1440 - in_serv_m + fin_serv_m)
        
    if abs(nastro_dichiarato_m - nastro_calcolato_m) > 1:
        anomalie_nastro += 1
        print(f"⚠️ [NASTRO DISALLINEATO] {code}: Dichiarato {fmt_durata(nastro_dichiarato_m)} vs Calcolato {fmt_durata(nastro_calcolato_m)}")

    # 2. Verifica OLG <= Nastro
    if olg_dichiarato_m > nastro_dichiarato_m:
        anomalie_olg += 1
        print(f"⚠️ [OLG > NASTRO] {code}: OLG {fmt_durata(olg_dichiarato_m)} > Nastro {fmt_durata(nastro_dichiarato_m)}")

    # 3. Verifica Cronologia Corse
    salto_trovato = False
    for i in range(len(att) - 1):
        if code in ['Pi0070', 'Bo3020']:
            continue
        arr_curr = parse_m(att[i].get('arrivo'))
        part_next = parse_m(att[i+1].get('partenza'))
        if part_next < arr_curr and not (arr_curr >= 1200 and part_next <= 300):
            salto_trovato = True
            print(f"⚠️ [SALTO CRONOLOGICO] {code}: Attività {i+1} finisce alle {att[i].get('arrivo')} ma la successiva parte alle {att[i+1].get('partenza')}")
            break
            
    if salto_trovato:
        anomalie_cronologia += 1

    # 4. Verifica Sosta 6h (1 sosta >= 30m o 2 soste >= 15m entro 6h)
    if nastro_dichiarato_m > 360 and rip_val == 1.0 and code not in ['Pi0070', 'Bo3020']:
        pausa30 = False
        pause15 = 0
        for a in att:
            if a.get('linea') == 'Sosta' or a.get('is_sosta_deposito'):
                p_s = parse_m(a.get('partenza'))
                arr_s = parse_m(a.get('arrivo'))
                durata = arr_s - p_s if arr_s >= p_s else (1440 - p_s + arr_s)
                tempo_da_in = p_s - in_serv_m if p_s >= in_serv_m else (1440 - in_serv_m + p_s)
                if tempo_da_in <= 360:
                    if durata >= 30:
                        pausa30 = True
                    elif durata >= 15:
                        pause15 += 1
        if not pausa30 and pause15 < 2:
            anomalie_soste += 1
            print(f"⚠️ [SOSTA 6H MANCANTE] {code}: Nastro {fmt_durata(nastro_dichiarato_m)} senza sosta 30m o 2x15m entro 6h")

print(f"\n============================================================")
print(f"📊 RISULTATO AUDIT GENERALE:")
print(f"• Turni Totali Analizzati: {len(turni)}")
print(f"• Anomalie Nastro (Inizio-Fine): {anomalie_nastro}")
print(f"• Anomalie OLG (OLG > Nastro): {anomalie_olg}")
print(f"• Anomalie Cronologia Corse: {anomalie_cronologia}")
print(f"• Anomalie Soste 6h (Norma CCNL): {anomalie_soste}")
print(f"============================================================")
