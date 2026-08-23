import csv
from collections import defaultdict

def parse_time(tStr):
    if not tStr: return 0
    tStr = tStr.strip()
    if tStr in ['-', '.', '', 'D', 'I', 'R']: return 0
    parts = tStr.replace('.', ':').split(':')
    if len(parts) < 2: return 0
    try:
        h = int(parts[0])
        m = int(parts[1])
        return h * 60 + m
    except:
        return 0

with open('/root/db.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    lines = list(reader)

# Extract trips
trips = []
current_trips = []
for row in lines:
    if not row or not row[0].strip():
        continue
    first = row[0].strip()
    
    if first == 'Linea':
        current_trips = []
        for c in range(1, len(row)):
            if row[c].strip():
                t = {'_linea': row[c].strip()}
                current_trips.append(t)
                trips.append(t)
            else:
                current_trips.append(None)
    elif first == 'ID_Corsa':
        for c in range(1, len(row)):
            if c-1 < len(current_trips) and current_trips[c-1] and row[c].strip():
                current_trips[c-1]['_id'] = row[c].strip()
    elif first == 'Giorni':
        for c in range(1, len(row)):
            if c-1 < len(current_trips) and current_trips[c-1] and row[c].strip():
                current_trips[c-1]['_giorni'] = row[c].strip()
    elif first == 'Stagionalita':
        for c in range(1, len(row)):
            if c-1 < len(current_trips) and current_trips[c-1] and row[c].strip():
                current_trips[c-1]['_stag'] = row[c].strip()
    elif first == 'Note':
        for c in range(1, len(row)):
            if c-1 < len(current_trips) and current_trips[c-1] and row[c].strip():
                current_trips[c-1]['_note'] = row[c].strip()
    else:
        # It's a stop
        stop_name = first
        for c in range(1, len(row)):
            if c-1 < len(current_trips) and current_trips[c-1] and row[c].strip():
                current_trips[c-1][stop_name] = row[c].strip()

trips_268 = [t for t in trips if t['_linea'] == '268']

outbound_stops_order = [
    "TORINO - Porta Nuova",
    "TORINO - Porta Susa",
    "TORINO - c.so Umbria/via Livorno",
    "TO \u2013 via Stradella",
    "TO - Via Stampini",
    "BORGARO T.SE - via Lanzo/via Martiri",
    "CASELLE T.SE - via Torino, 99",
    "CASELLE T.SE - str. Aeroporto, 44",
    "TORINO - Aeroporto (Caselle)"
]

inbound_stops_order = [
    "TORINO - Aeroporto (Caselle)",
    "CASELLE T.SE - str.Aerop. (fronte n\u00b0 36)",
    "CASELLE T.SE - via Torino (fronte n\u00b0 99)",
    "BORGARO T.SE - via Lanzo, 157",
    "TO - Str Aeroporto (Ferm.\"VERONESE\")",
    "TO \u2013 via Stradella",
    "TORINO - c.so Umbria/via Livorno",
    "TO - Via Stampini",
    "TORINO - Porta Susa",
    "TORINO - Porta Nuova"
]

outbound_trips = []
inbound_trips = []

for t in trips_268:
    # determine direction
    o_score = 0
    i_score = 0
    stops_in_t = [k for k in t.keys() if not k.startswith('_') and t[k]]
    
    def parseTime(ts):
        return parse_time(ts)

    # Sort by time
    stops_in_t.sort(key=lambda s: parseTime(t[s]) if parseTime(t[s]) > 4*60 else parseTime(t[s])+24*60)

    if len(stops_in_t) >= 2:
        f = stops_in_t[0]
        l = stops_in_t[-1]
        
        if f in outbound_stops_order and l in outbound_stops_order:
            if outbound_stops_order.index(f) <= outbound_stops_order.index(l):
                o_score += 10
        if f in inbound_stops_order and l in inbound_stops_order:
            if inbound_stops_order.index(f) <= inbound_stops_order.index(l):
                i_score += 10
                
    if o_score >= i_score:
        outbound_trips.append(t)
    else:
        inbound_trips.append(t)

# Sort trips by first stop time
def get_trip_time(t):
    stops = [k for k in t.keys() if not k.startswith('_') and t[k]]
    if not stops: return 0
    mins = parse_time(t[stops[0]])
    if mins < 4*60: mins += 24*60
    return mins

outbound_trips.sort(key=get_trip_time)
inbound_trips.sort(key=get_trip_time)

with open('/root/268_fixed.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    
    # OUTBOUND
    writer.writerow(['Linea'] + [t['_linea'] for t in outbound_trips])
    writer.writerow(['ID_Corsa'] + [t.get('_id', '') for t in outbound_trips])
    writer.writerow(['Giorni'] + [t.get('_giorni', '') for t in outbound_trips])
    writer.writerow(['Stagionalita'] + [t.get('_stag', '') for t in outbound_trips])
    writer.writerow(['Note'] + [t.get('_note', '') for t in outbound_trips])
    
    for stop in outbound_stops_order:
        writer.writerow([stop] + [t.get(stop, '') for t in outbound_trips])
        
    writer.writerow([])
    
    # INBOUND
    writer.writerow(['Linea'] + [t['_linea'] for t in inbound_trips])
    writer.writerow(['ID_Corsa'] + [t.get('_id', '') for t in inbound_trips])
    writer.writerow(['Giorni'] + [t.get('_giorni', '') for t in inbound_trips])
    writer.writerow(['Stagionalita'] + [t.get('_stag', '') for t in inbound_trips])
    writer.writerow(['Note'] + [t.get('_note', '') for t in inbound_trips])
    
    for stop in inbound_stops_order:
        writer.writerow([stop] + [t.get(stop, '') for t in inbound_trips])
        
print("Wrote /root/268_fixed.csv")
