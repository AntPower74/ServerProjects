import json
import csv
from collections import defaultdict, deque
import sys

def get_master_stops(trips):
    edge_freq = defaultdict(int)
    stops = set()
    
    for trip in trips:
        trip_stops = [k for k in trip.keys() if not k.startswith('_')]
        for s in trip_stops:
            stops.add(s)
        for i in range(len(trip_stops) - 1):
            u = trip_stops[i]
            v = trip_stops[i+1]
            edge_freq[(u, v)] += 1

    while True:
        graph = defaultdict(set)
        in_degree = {s: 0 for s in stops}
        
        for (u, v), freq in edge_freq.items():
            if freq > 0:
                graph[u].add(v)
                in_degree[v] += 1
                
        queue = deque([s for s in stops if in_degree[s] == 0])
        master_stops = []
        
        while queue:
            u = queue.popleft()
            master_stops.append(u)
            for v in list(graph[u]):
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
                    
        if len(master_stops) == len(stops):
            return master_stops
            
        min_freq = float('inf')
        min_edge = None
        for e, f in edge_freq.items():
            if f > 0 and f < min_freq:
                min_freq = f
                min_edge = e
                
        if min_edge:
            edge_freq[min_edge] = 0
        else:
            remaining = stops - set(master_stops)
            master_stops.extend(list(remaining))
            return master_stops

with open('/root/orari-app/data.js', 'r') as f:
    js_content = f.read()

start = js_content.find('[')
end = js_content.rfind(']') + 1
all_trips = json.loads(js_content[start:end])

lines = defaultdict(list)
for t in all_trips:
    lines[t.get('_linea', 'Unknown')].append(t)

csv_file = '/root/orari-app/Database_Orari_PDF.csv'
trip_counter = 1

with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    
    for linea, trips in lines.items():
        # Count global pair frequencies for this line
        pair_freq = defaultdict(int)
        for t in trips:
            stops = [k for k in t.keys() if not k.startswith('_')]
            for i in range(len(stops)):
                for j in range(i+1, len(stops)):
                    pair_freq[(stops[i], stops[j])] += 1
                    
        # Divide into two directions
        dir_0 = []
        dir_1 = []
        for t in trips:
            stops = [k for k in t.keys() if not k.startswith('_')]
            score_0 = 0
            score_1 = 0
            for i in range(len(stops)-1):
                u = stops[i]
                v = stops[i+1]
                if pair_freq[(u, v)] >= pair_freq[(v, u)]:
                    score_0 += 1
                else:
                    score_1 += 1
            if score_0 >= score_1:
                dir_0.append(t)
            else:
                dir_1.append(t)
                
        # Process each direction block
        for block_trips in [dir_0, dir_1]:
            if not block_trips:
                continue
                
            master_stops = get_master_stops(block_trips)
            
            # Write headers
            row_linea = ['Linea'] + [t.get('_linea', '') for t in block_trips]
            row_id = ['ID_Corsa']
            for _ in block_trips:
                row_id.append(f"C{trip_counter:04d}")
                trip_counter += 1
            row_giorni = ['Giorni'] + [t.get('_giorni', '') for t in block_trips]
            row_stag = ['Stagionalita'] + [t.get('_stagionalita', '') for t in block_trips]
            row_note = ['Note'] + [t.get('_note', '') for t in block_trips]
            
            writer.writerow(row_linea)
            writer.writerow(row_id)
            writer.writerow(row_giorni)
            writer.writerow(row_stag)
            writer.writerow(row_note)
            
            # Write stops
            for stop in master_stops:
                row_stop = [stop] + [t.get(stop, '') for t in block_trips]
                writer.writerow(row_stop)
                
            writer.writerow([]) # Blank line separator

print(f"Generated {csv_file}")
