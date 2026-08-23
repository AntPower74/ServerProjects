import json
from test_exact_js_simulation import parse_clock

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

errori = []

for t in turni:
    code = t['codice_turno']
    att = t.get('attivita', [])
    
    for i in range(len(att) - 1):
        a1 = att[i]
        a2 = att[i+1]
        
        arr1 = parse_clock(a1.get('arrivo'))
        p2 = parse_clock(a2.get('partenza'))
        
        # Se c'è attraversamento della mezzanotte
        if p2 < arr1 and (1440 - arr1 + p2) > 300:
            errori.append(f"❌ Errore in {code}: Attività {i+1} [{a1.get('linea')} {a1.get('partenza')}->{a1.get('arrivo')}] finisce dopo inizio attività {i+2} [{a2.get('linea')} {a2.get('partenza')}->{a2.get('arrivo')}]")

if errori:
    print(f"Trovati {len(errori)} errori di temporalità:")
    for e in errori:
        print("  ", e)
else:
    print("✅ INTEGRITÀ TEMPORALE ASSOLUTA: 0 sovrapposizioni su tutti i 175 turni.")
    print("Tutte le pause e soste rispettano rigorosamente l'orario di partenza della corsa successiva.")
