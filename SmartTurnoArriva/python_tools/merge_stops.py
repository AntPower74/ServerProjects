import json

stops_to_merge = [
    "TO - Autostazione c.so Bolzano",
    "TORINO - Autostazione corso Bolzano",
    "TORINO - Porta Susa",
    "TORINO Autostazione"
]
merged_stop_name = "TORINO - Porta Susa (Autostazione)"

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
        merged_times = []
        
        # Collect all times from the merged stops in this trip
        for stop in stops_to_merge:
            if stop in trip:
                # We could have multiple of these in the same trip!
                # Actually we shouldn't, but let's take the first non-empty time
                merged_times.append(trip[stop])
                del trip[stop]
                changes += 1
                
        if merged_times:
            # We pick the first valid time or just the first one if all are invalid
            # Since they are practically the same stop, they should have the same time
            trip[merged_stop_name] = merged_times[0]

    if changes > 0:
        new_json_str = json.dumps(data)
        lines[0] = "const tripsData = " + new_json_str + ";\n"
        with open("/root/orari-app/data.js", "w") as fw:
            fw.writelines(lines)
        print(f"Merged {changes} stops into '{merged_stop_name}'.")
    else:
        print("No stops found to merge.")
else:
    print("Format not recognized.")
