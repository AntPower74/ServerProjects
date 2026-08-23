#!/usr/bin/env python3
import csv
from collections import Counter, defaultdict

with open("/home/antonio/verifica_turni/corse_google_sheet.csv") as f:
    reader = csv.DictReader(f)
    corse = list(reader)

print(f"Total rows in sheet: {len(corse)}")

dep_counts = Counter()
turni_by_dep = defaultdict(set)

for c in corse:
    t = c.get('Turno', '').strip()
    pref = t[:2]
    dep_counts[pref] += 1
    turni_by_dep[pref].add(t)

for pref, cnt in dep_counts.most_common():
    print(f"Deposito '{pref}': {cnt} corse commerciali | {len(turni_by_dep[pref])} turni ufficiali")
