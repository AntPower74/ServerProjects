import json
from collections import defaultdict, deque

def get_master_stops(trips):
    # Count frequencies of direct edges
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

    # Keep removing weakest edges until no cycles
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
            
        # Find a cycle and remove the weakest edge in it, or just remove the weakest edge globally
        # Simplest: find the weakest edge with freq > 0 and remove it
        min_freq = float('inf')
        min_edge = None
        for e, f in edge_freq.items():
            if f > 0 and f < min_freq:
                min_freq = f
                min_edge = e
                
        if min_edge:
            edge_freq[min_edge] = 0
        else:
            # Fallback
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

# Let's test on 275/282
trips_275 = lines['275/282']

# Direction split
pair_freq = defaultdict(int)
for t in trips_275:
    stops = [k for k in t.keys() if not k.startswith('_')]
    for i in range(len(stops)):
        for j in range(i+1, len(stops)):
            pair_freq[(stops[i], stops[j])] += 1
            
dir_0 = []
dir_1 = []
for t in trips_275:
    stops = [k for k in t.keys() if not k.startswith('_')]
    score_0 = sum(1 for i in range(len(stops)-1) if pair_freq[(stops[i], stops[i+1])] >= pair_freq[(stops[i+1], stops[i])])
    score_1 = sum(1 for i in range(len(stops)-1) if pair_freq[(stops[i], stops[i+1])] < pair_freq[(stops[i+1], stops[i])])
    if score_0 >= score_1:
        dir_0.append(t)
    else:
        dir_1.append(t)

print("DIR 0 Stops:")
for s in get_master_stops(dir_0):
    print(s)

print("\nDIR 1 Stops:")
for s in get_master_stops(dir_1):
    print(s)
