import json

with open("/root/orari-app/data.js", "r") as f:
    lines = f.readlines()

first_line = lines[0]
if first_line.startswith("const tripsData = ["):
    json_str = first_line[len("const tripsData = "):].strip()
    if json_str.endswith(";"):
        json_str = json_str[:-1]
    
    data = json.loads(json_str)
    
    keys = set()
    for trip in data:
        for k in trip.keys():
            if not k.startswith('_'):
                keys.add(k)
                
    for k in sorted(keys):
        k_lower = k.lower()
        if "pinerolo" in k_lower or "movicentro" in k_lower or "chivasso" in k_lower:
            print(k)
