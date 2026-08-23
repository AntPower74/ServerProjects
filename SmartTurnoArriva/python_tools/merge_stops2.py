import json

merge_groups = [
    {
        "target": "PINEROLO - Movicentro (Stazione FS)",
        "sources": ["PINEROLO - Movicentro", "PINEROLO Movicentro", "PINEROLO - Stazione FS", "PINEROLO Stazione FS"]
    },
    {
        "target": "PINEROLO - Centro Studi",
        "sources": ["PINEROLO - Centro Studi", "PINEROLO Centro Studi"]
    },
    {
        "target": "PINEROLO - Ist. Immacolata",
        "sources": ["PINEROLO - Ist. Immacolata", "PINEROLO Ist. Immacolata"]
    },
    {
        "target": "CHIVASSO - Movicentro (Stazione FS)",
        "sources": ["CHIVASSO - Staz. FS Movicentro", "CHIVASSO - Movicentro", "CHIVASSO Movicentro", "CHIVASSO FS", "CHIVASSO Stazione FS"]
    }
]

with open("/root/orari-app/data.js", "r") as f:
    lines = f.readlines()

first_line = lines[0]
if first_line.startswith("const tripsData = ["):
    json_str = first_line[len("const tripsData = "):].strip()
    if json_str.endswith(";"):
        json_str = json_str[:-1]
    
    data = json.loads(json_str)
    
    changes = 0
    for trip in data:
        for group in merge_groups:
            merged_times = []
            for source in group["sources"]:
                if source in trip:
                    merged_times.append(trip[source])
                    del trip[source]
                    changes += 1
            if merged_times:
                trip[group["target"]] = merged_times[0]

    if changes > 0:
        new_json_str = json.dumps(data)
        lines[0] = "const tripsData = " + new_json_str + ";\n"
        with open("/root/orari-app/data.js", "w") as fw:
            fw.writelines(lines)
        print(f"Merged {changes} stops based on groups.")
    else:
        print("No stops found to merge.")
else:
    print("Format not recognized.")
