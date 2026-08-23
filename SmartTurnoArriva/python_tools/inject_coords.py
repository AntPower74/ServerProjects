import json

with open('/root/stops_coords.json', 'r') as f:
    coords = json.load(f)

js_code = "\nwindow.stopsCoords = " + json.dumps(coords) + ";\n"

for filepath in ['/root/orari-app/data.js', '/root/shift-app/public/orari/data.js']:
    with open(filepath, 'a') as f:
        f.write(js_code)
