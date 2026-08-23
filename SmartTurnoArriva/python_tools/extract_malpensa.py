import json

outbound_stops = [
    "TORINO - Piazza Cattaneo",
    "TORINO - Mombarcaro (Santa Rita)",
    "TORINO - Autostazione corso Bolzano",
    "TORINO - Corso Giulio Cesare 426",
    "CHIVASSO CENTRO - casello A4",
    "CARISIO - Casello A4",
    "MALPENSA OVEST (Terminal 1)",
    "MALPENSA NORD (Terminal 2)"
]

outbound_data = """
- - 04:50 06:20 07:20 08:20 09:20 - - - - - - - -
- - 05:00 06:30 07:30 08:30 09:30 - - - - - - - -
03:00 04:10 05:30 07:00 08:00 09:00 10:00 11:00 12:00 13:00 14:00 15:00 16:00 17:00 19:30
03:16 04:26 05:46 07:16 08:16 09:16 10:16 11:16 12:16 13:16 14:16 15:16 16:16 17:16 19:46
03:30 04:40 06:00 07:30 08:30 09:30 10:30 11:30 12:30 13:30 14:30 15:30 16:30 17:30 20:00
03:55 05:05 06:25 07:55 08:55 09:55 10:55 11:55 12:55 13:55 14:55 15:55 16:55 17:55 20:25
04:55 06:05 07:25 08:55 09:55 10:55 11:55 12:55 13:55 14:55 15:55 16:55 17:55 18:55 21:25
05:00 06:10 07:30 09:00 10:00 11:00 12:00 13:00 14:00 15:00 16:00 17:00 18:00 19:00 21:30
"""

return_stops = [
    "MALPENSA OVEST (Terminal 1)",
    "MALPENSA NORD (Terminal 2)",
    "CARISIO - Casello A4",
    "CHIVASSO CENTRO - casello A4",
    "TORINO - Corso Giulio Cesare 426",
    "TORINO - Autostazione corso Bolzano",
    "TORINO - Mombarcaro (Santa Rita)",
    "TORINO - Piazza Cattaneo"
]

return_data = """
07:50 09:00 10:00 11:00 12:00 13:00 14:00 15:15 16:30 17:30 18:30 19:30 20:40 21:40 23:40
07:55 09:05 10:05 11:05 12:05 13:05 14:05 15:20 16:35 17:35 18:35 19:35 20:45 21:45 23:45
08:50 10:00 11:00 12:00 13:00 14:00 15:00 16:15 17:30 18:30 19:30 20:30 21:40 22:40 00:40
09:15 10:25 11:25 12:25 13:25 14:25 15:25 16:40 17:55 18:55 19:55 20:55 22:05 23:05 01:05
09:34 10:44 11:44 12:44 13:44 14:44 15:44 16:59 18:14 19:14 20:14 21:14 22:24 23:24 01:24
09:50 11:00 12:00 13:00 14:00 15:00 16:00 17:15 18:30 19:30 20:30 21:30 22:40 23:40 01:40
- - - - - - - 17:30 - 19:45 20:45 21:45 22:55 - -
- - - - - - - 17:40 - 19:55 20:55 21:55 23:05 - -
"""

import re

def parse_matrix(data_str, stops):
    rows = [line.split() for line in data_str.strip().split('\n')]
    num_trips = len(rows[0])
    trips = []
    for col in range(num_trips):
        trip = {}
        for row_idx, stop in enumerate(stops):
            val = rows[row_idx][col]
            if val != '-':
                trip[stop] = val
        trip["_linea"] = "MALPENSA"
        trip["_giorni"] = "1234567"
        trips.append(trip)
    return trips

new_trips = parse_matrix(outbound_data, outbound_stops) + parse_matrix(return_data, return_stops)

with open("/root/orari-app/data.js", "r") as f:
    lines = f.readlines()

first_line = lines[0]
if first_line.startswith("const tripsData = ["):
    # extract the array
    json_str = first_line[len("const tripsData = "):].strip()
    if json_str.endswith(";"):
        json_str = json_str[:-1]
    
    try:
        data = json.loads(json_str)
        # Check if MALPENSA is already there to avoid duplicates
        if any(t.get("_linea") == "MALPENSA" for t in data):
            print("MALPENSA trips already exist in data.js!")
        else:
            data.extend(new_trips)
            new_json_str = json.dumps(data)
            lines[0] = "const tripsData = " + new_json_str + ";\n"
            
            with open("/root/orari-app/data.js", "w") as fw:
                fw.writelines(lines)
            print("Successfully added", len(new_trips), "trips.")
    except Exception as e:
        print("JSON parsing error:", e)
else:
    print("Format not recognized in line 1:", first_line[:50])
