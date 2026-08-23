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

csv_file = '/root/.gemini/antigravity-cli/brain/4cdfeb15-664f-4107-a0ca-620778a57ac3/Database_Orari.csv'

with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ID_Corsa', 'Linea', 'Giorni', 'Stagionalita', 'Note', 'Ordine_Fermata', 'Nome_Fermata', 'Ora'])
    
    for i, trip in enumerate(trips):
        trip_id = f"C{i+1:04d}"
        linea = trip.get('_linea', '')
        giorni = trip.get('_giorni', '')
        stag = trip.get('_stagionalita', '')
        note = trip.get('_note', '')
        
        order = 1
        for key, val in trip.items():
            if not key.startswith('_'):
                writer.writerow([trip_id, linea, giorni, stag, note, order, key, val])
                order += 1

print(f"Generated {csv_file} successfully.")
