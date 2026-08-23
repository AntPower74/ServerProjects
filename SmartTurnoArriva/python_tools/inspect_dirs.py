import json
from collections import defaultdict

with open('/root/orari-app/data.js', 'r') as f:
    js_content = f.read()

start = js_content.find('[')
end = js_content.rfind(']') + 1
trips = json.loads(js_content[start:end])

line_267 = [t for t in trips if t.get('_linea') == '267']

dirs = defaultdict(int)
for t in line_267:
    stops = [k for k in t.keys() if not k.startswith('_')]
    first = stops[0]
    last = stops[-1]
    dirs[(first, last)] += 1

for k, v in dirs.items():
    print(f"From {k[0]} To {k[1]}: {v} trips")
