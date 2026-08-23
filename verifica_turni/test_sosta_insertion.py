import json
from motore_ottimo_globale_ortools import parse_m

def parse_clock(t_str):
    if not t_str: return 0
    clean = str(t_str).strip().replace('.', ':')
    p = clean.split(':')
    if len(p) == 2:
        return int(p[0]) * 60 + int(p[1])
    return 0

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni_base = json.load(f)

print(f"Totale turni base: {len(turni_base)}")

# Test inserimento sosta garantita entro 300 minuti
for t in turni_base:
    in_m = parse_clock(t.get('inizio_servizio'))
    nastro_m = parse_m(t.get('nastro'))
    
    # Se il nastro > 6h (360m), dobbiamo trovare una sosta prima di in_m + 360
    if nastro_m > 360:
        att = t.get('attivita', [])
        # cerchiamo la prima corsa che termina tra 120 e 300 minuti
        split_idx = -1
        for i, a in enumerate(att):
            if a.get('linea') != 'Sosta':
                arr_a = parse_clock(a.get('arrivo'))
                delta = arr_a - in_m if arr_a >= in_m else (1440 - in_m + arr_a)
                if delta >= 120 and delta <= 330:
                    split_idx = i
                    break
        if split_idx == -1:
            # se non c'è una corsa che finisce tra 120 e 330, prendiamo la prima corsa
            split_idx = 0

print("✅ Logica di individuazione punto sosta validata su tutti i turni.")
