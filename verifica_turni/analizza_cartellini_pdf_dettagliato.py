import pdfplumber
import json
import re

PDF_PATH = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini lun-ven 2026.pdf"

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

print("Analisi approfondita del PDF originale Arriva...")

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

# 1. Turni con lavoro continuo > 6h SENZA sosta 30m o 2x15m (Violazione CCNL / D.Lgs 234/2007)
violazioni_sosta = []
nastro_eccessivo = []
stacchi_anomali = []
sovrapposizioni = []
discrepanze_ore = []

for t in turni:
    code = t['codice_turno']
    nome = t.get('nome_turno', '')
    dep = t.get('deposito', '')
    in_m = parse_m(t.get('inizio_servizio'))
    fin_m = parse_m(t.get('fine_servizio'))
    nastro_m = t.get('nastro_m', 0)
    olg_m = t.get('olg_m', 0)
    att = t.get('attivita', [])
    rip = float(str(t.get('num_riprese', '1')).replace(',', '.'))
    
    # Nastro > 12h (Art. 8 CCNL Autoferrotranvieri)
    if nastro_m > 720: # 12h
        nastro_eccessivo.append({
            'codice': code,
            'deposito': dep,
            'nastro': f"{nastro_m//60}h {nastro_m%60}m",
            'servizio': f"{t.get('inizio_servizio')} -> {t.get('fine_servizio')}",
            'riprese': rip,
            'motivo': f"Nastro di {nastro_m//60}h {nastro_m%60}m eccede il limite massimo di 12h previsto dal CCNL (Art. 8)"
        })
        
    # Verifica sosta 30m entro 6h
    if nastro_m > 360 and rip == 1:
        has_sosta_valida = False
        soste_trovate = []
        for a in att:
            if a.get('linea') == 'Sosta' or a.get('is_sosta_deposito'):
                p_s = parse_m(a.get('partenza'))
                arr_s = parse_m(a.get('arrivo'))
                dur_s = arr_s - p_s if arr_s >= p_s else (1440 - p_s + arr_s)
                tempo_da_in = p_s - in_m if p_s >= in_m else (1440 - in_m + p_s)
                soste_trovate.append(f"{a.get('partenza')}->{a.get('arrivo')} ({dur_s}m, al minuto {tempo_da_in})")
                if tempo_da_in <= 360 and dur_s >= 30:
                    has_sosta_valida = True
        
        if not has_sosta_valida:
            violazioni_sosta.append({
                'codice': code,
                'deposito': dep,
                'nastro': f"{nastro_m//60}h {nastro_m%60}m",
                'inizio': t.get('inizio_servizio'),
                'fine': t.get('fine_servizio'),
                'soste_nel_turno': soste_trovate if soste_trovate else "Nessuna sosta registrata",
                'motivo': "Turno continuo con Nastro > 6h privo di sosta di almeno 30 minuti entro le prime 6 ore di servizio"
            })

    # Stacchi passivi inferiori a 60 min non retribuiti
    for a in att:
        if a.get('linea') == 'Sosta' and a.get('is_sosta_deposito'):
            p_s = parse_m(a.get('partenza'))
            arr_s = parse_m(a.get('arrivo'))
            dur_s = arr_s - p_s if arr_s >= p_s else (1440 - p_s + arr_s)
            if 0 < dur_s < 30 and rip > 1:
                stacchi_anomali.append({
                    'codice': code,
                    'orario': f"{a.get('partenza')} -> {a.get('arrivo')}",
                    'durata': f"{dur_s} min",
                    'motivo': "Stacco tra riprese inferiore a 30 minuti non retribuito"
                })

print(f"\n1. Turni con Nastro > 12h (Eccesso limite CCNL): {len(nastro_eccessivo)}")
for n in nastro_eccessivo[:5]:
    print("  ", n)

print(f"\n2. Turni Continui con violazione sosta obbligatoria 6h: {len(violazioni_sosta)}")
for v in violazioni_sosta[:5]:
    print("  ", v)

print(f"\n3. Stacchi anomali: {len(stacchi_anomali)}")

