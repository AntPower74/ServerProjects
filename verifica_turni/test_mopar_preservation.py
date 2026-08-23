import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni_reali = json.load(f)

# Troviamo tutti i turni con corse serali/notturne MOPAR / SKF / Operaie
mopar_shifts = []
for t in turni_reali:
    has_mopar = False
    for a in t.get('attivita', []):
        if 'MOPAR' in str(a.get('descrizione', '')).upper() or 'RIVALTA' in str(a.get('descrizione', '')).upper():
            has_mopar = True
    if has_mopar:
        mopar_shifts.append(t['codice_turno'])

print("Turni con corse MOPAR/Rivalta:", mopar_shifts)
