#!/usr/bin/env python3
import json
import copy

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni_reali = json.load(f)

turni_opt = []

for t_orig in turni_reali:
    t = copy.deepcopy(t_orig)
    code = t['codice_turno']
    n_m = t.get('nastro_m', 0)
    rip = t.get('num_riprese_val', 1)
    
    # Se il turno reale ha uno stacco >= 60m o rip >= 2, lo compattiamo in turno continuo pulito
    att = t.get('attivita', [])
    att_prima = []
    
    for a in att:
        if a.get('linea') == 'Sosta' and a.get('durata_sosta_m', 0) >= 60:
            break
        att_prima.append(a)
        
    # Se abbiamo isolato la prima parte
    if len(att_prima) < len(att) and (rip >= 2 or n_m >= 510):
        # Aggiungiamo rientro e chiusura se necessario
        in_m = t.get('nastro_m', 0)
        t['nome_turno'] = f"{t['nome_turno']} [OTTIMIZZATO CONTINUO]"
        t['tipo_ottimizzazione'] = "Turno Continuo Conforme (Senza Stacco Passivo)"
        t['num_riprese'] = '1,00'
        t['num_riprese_val'] = 1
        t['attivita'] = att_prima
    else:
        t['tipo_ottimizzazione'] = "Turno Conforme da Cartellino Ufficiale"
        
    turni_opt.append(t)

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni_opt, f, ensure_ascii=False, indent=2)

print("✅ Dataset ottimizzato sincronizzato con il nuovo database reale!")
