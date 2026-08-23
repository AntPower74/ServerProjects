import json

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

print(f"Totale turni: {len(turni)}")
min_n = min(t.get('nastro_m', 0) for t in turni)
max_n = max(t.get('nastro_m', 0) for t in turni)
avg_n = sum(t.get('nastro_m', 0) for t in turni) / len(turni)

print(f"Nastro Min: {min_n}m ({min_n//60}h {min_n%60}m)")
print(f"Nastro Max: {max_n}m ({max_n//60}h {max_n%60}m)")
print(f"Nastro Avg: {avg_n:.1f}m ({int(avg_n)//60}h {int(avg_n)%60}m)")

# Campione di 5 turni
for t in turni[:5]:
    print(f"  {t['codice_turno']}: nastro_str={t.get('nastro_str')}, nastro_m={t.get('nastro_m')}")
