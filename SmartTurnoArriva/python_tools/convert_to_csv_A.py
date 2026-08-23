import json
import csv
import sys

with open('/root/orari-app/data.js', 'r') as f:
    js_content = f.read()

start = js_content.find('[')
end = js_content.rfind(']') + 1
if start == -1 or end == 0:
    print("Error parsing data.js")
    sys.exit(1)

trips = json.loads(js_content[start:end])

# Find max stops to create headers
max_stops = 0
for trip in trips:
    stops = [k for k in trip.keys() if not k.startswith('_')]
    if len(stops) > max_stops:
        max_stops = len(stops)

csv_file = '/root/orari-app/Database_Orari_OpzioneA.csv'

with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    
    headers = ['ID_Corsa', 'Linea', 'Giorni', 'Stagionalita', 'Note']
    for i in range(1, max_stops + 1):
        headers.extend([f'Fermata_{i}', f'Ora_{i}'])
        
    writer.writerow(headers)
    
    for i, trip in enumerate(trips):
        trip_id = f"C{i+1:04d}"
        linea = trip.get('_linea', '')
        giorni = trip.get('_giorni', '')
        stag = trip.get('_stagionalita', '')
        note = trip.get('_note', '')
        
        row = [trip_id, linea, giorni, stag, note]
        
        # Iterate over stops
        stops_added = 0
        for key, val in trip.items():
            if not key.startswith('_'):
                row.extend([key, val])
                stops_added += 1
                
        # Fill remaining columns with empty strings
        for _ in range(max_stops - stops_added):
            row.extend(['', ''])
            
        writer.writerow(row)

print(f"Generated {csv_file} successfully.")
