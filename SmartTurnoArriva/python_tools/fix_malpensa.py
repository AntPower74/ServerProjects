import json

with open("/root/orari-app/data.js", "r") as f:
    lines = f.readlines()

first_line = lines[0]
if first_line.startswith("const tripsData = ["):
    json_str = first_line[len("const tripsData = "):].strip()
    if json_str.endswith(";"):
        json_str = json_str[:-1]
    
    data = json.loads(json_str)
    
    count = 0
    for trip in data:
        if trip.get("_linea") == "MALPENSA":
            trip["_giorni"] = "GG"
            count += 1
            
    if count > 0:
        new_json_str = json.dumps(data)
        lines[0] = "const tripsData = " + new_json_str + ";\n"
        with open("/root/orari-app/data.js", "w") as fw:
            fw.writelines(lines)
        print(f"Fixed {count} trips.")
    else:
        print("No MALPENSA trips found.")
else:
    print("Format not recognized.")
