import json
import csv

with open('/root/orari-app/turni_corse.json', 'r', encoding='utf-8') as f:
    turni = json.load(f)

csv_file = '/root/orari-app/Cartellini_Turni.csv'

with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Codice_Turno', 'Nome_Turno', 'Deposito', 'Giorno', 
        'Turno_Ora_Inizio', 'Turno_Ora_Fine', 
        'Corsa_Linea', 'Corsa_Da', 'Corsa_A', 'Corsa_Ora_Partenza', 'Corsa_Ora_Arrivo'
    ])
    
    for t in turni:
        codice = t.get('codice', '')
        nome = t.get('nome', '')
        dep = t.get('deposito', '')
        giorno = t.get('giorno', '')
        inizio = t.get('ora_inizio', '')
        fine = t.get('ora_fine', '')
        
        corse = t.get('corse', [])
        if not corse:
            # Write a row with empty corsa details
            writer.writerow([codice, nome, dep, giorno, inizio, fine, '', '', '', '', ''])
        else:
            for c in corse:
                writer.writerow([
                    codice, nome, dep, giorno, inizio, fine,
                    c.get('linea', ''),
                    c.get('da', ''),
                    c.get('a', ''),
                    c.get('partenza', ''),
                    c.get('arrivo', '')
                ])

print(f"Generated {csv_file}")
