import csv
import json
import re

with open('/root/orari-app/data.js', 'r') as f:
    content = f.read()
    start_idx = content.find('[')
    end_idx = content.find('];') + 1
    db = json.loads(content[start_idx:end_idx])

# Create a quick lookup for trips
# Linea -> list of trips
db_by_linea = {}
for trip in db:
    l = trip.get('_linea', '')
    if l not in db_by_linea:
        db_by_linea[l] = []
    db_by_linea[l].append(trip)

# Read foglio.csv
errors = []

with open('/root/foglio.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader) # skip header
    for row in reader:
        if len(row) < 6: continue
        turno = row[0].strip()
        linea = row[2].strip()
        partenza_time = row[3].strip()
        arrivo_time = row[4].strip()
        da_a = row[5].strip()
        
        if not linea: continue
        
        # Check if line exists
        if linea not in db_by_linea:
            errors.append(f"Turno {turno}: Linea {linea} not found in DB.")
            continue
            
        trips_for_line = db_by_linea[linea]
        
        # Find a trip that departs at partenza_time and arrives at arrivo_time
        # Since stops can be anything, we just check if any stop has the departure time
        # and a subsequent stop has the arrival time
        
        found_exact = False
        found_start = False
        
        for trip in trips_for_line:
            # get all time keys
            times = []
            for k, v in trip.items():
                if k.startswith('_'): continue
                if ':' in v or '.' in v:
                    t = v.replace('.', ':')
                    times.append((k, t))
            
            # Sort by order of appearance is hard, but we can just check if partenza and arrivo exist
            # in the same trip
            times_only = [x[1] for x in times]
            if partenza_time in times_only:
                found_start = True
                if arrivo_time in times_only:
                    found_exact = True
                    break
        
        if not found_exact:
            if found_start:
                errors.append(f"Turno {turno} Corsa {partenza_time}: Arrivo previsto {arrivo_time} non trovato nel DB per questa corsa!")
            else:
                errors.append(f"Turno {turno} Corsa {partenza_time}: Partenza non trovata nel DB per la linea {linea}!")

print(f"Verifica completata. Errori trovati: {len(errors)}")
for e in errors[:50]:
    print(e)
