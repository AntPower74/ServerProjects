import json
from test_exact_js_simulation import parse_clock

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni_base = json.load(f)

min_lavoro = 390 # 6h 30m
max_nastro = 630 # 10h 30m

print(f"Test con Min Lavoro = {min_lavoro//60}h {min_lavoro%60:02d}m e Max Nastro = {max_nastro//60}h {max_nastro%60:02d}m")
