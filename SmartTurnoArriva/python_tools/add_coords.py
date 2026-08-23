import json

new_coords = {
    "TORINO - Piazza Cattaneo": {"lat": 45.033, "lng": 7.633},
    "TORINO - Mombarcaro (Santa Rita)": {"lat": 45.045, "lng": 7.641},
    "TORINO - Autostazione corso Bolzano": {"lat": 45.07166, "lng": 7.66635},
    "TORINO - Corso Giulio Cesare 426": {"lat": 45.111, "lng": 7.708},
    "CHIVASSO CENTRO - casello A4": {"lat": 45.183, "lng": 7.886},
    "CARISIO - Casello A4": {"lat": 45.424, "lng": 8.204},
    "CARISIO - Casello A4 - direzione Milano": {"lat": 45.424, "lng": 8.204},
    "CARISIO - Casello A4 - direzione Torino": {"lat": 45.424, "lng": 8.204},
    "MALPENSA OVEST (Terminal 1)": {"lat": 45.628, "lng": 8.708},
    "MALPENSA NORD (Terminal 2)": {"lat": 45.645, "lng": 8.723}
}

with open("/root/orari-app/data.js", "r") as f:
    content = f.read()

# Replace multiple instances of window.stopsCoords
for k, v in new_coords.items():
    json_insert = f', "{k}": {json.dumps(v)}}}'
    content = content.replace("};", json_insert)

with open("/root/orari-app/data.js", "w") as f:
    f.write(content)

print("Updated coordinates.")
