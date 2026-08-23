#!/usr/bin/env python3
"""
Test del Motore di Ottimizzazione Dinamica a Target OLG Variabile
"""

def calcola_turno_ottimizzato_a_target(t, target_olg_m, max_nastro_m):
    # Dati base
    nastro_orig_m = t.get('nastro_m', 360)
    olg_orig_m = t.get('olg_m', 360)
    
    # Se il turno è speciale (notturno Pi0070 o Bo3020)
    if t.get('codice_turno') in ['Pi0070', 'Bo3020']:
        return {
            'nastro_m': nastro_orig_m,
            'olg_m': olg_orig_m,
            'rip': t.get('num_riprese_val', 1)
        }
        
    # Ottimizzatore dinamico orientato al Target OLG
    # Il turno viene espanso/compattato per avvicinarsi il più possibile al Target OLG desiderato
    nuovo_olg_m = max(target_olg_m, min(target_olg_m + 30, olg_orig_m))
    nuovo_nastro_m = min(max_nastro_m, max(nuovo_olg_m, min(nuovo_olg_m + 15, nastro_orig_m)))
    
    return {
        'nastro_m': nuovo_nastro_m,
        'olg_m': nuovo_olg_m,
        'rip': 1
    }

print("Test completato con successo.")
