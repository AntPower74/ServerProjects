#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = [t for t in turni if t['codice_turno'].startswith('Pi')]
t130 = [x for x in pinerolo if x['codice_turno'] == 'Pi0130'][0]
t190 = [x for x in pinerolo if x['codice_turno'] == 'Pi0190'][0]

print("=== OPZIONE SCAMBIO: Pi0130 <---> Pi0190 ===")
print(f"🔴 Pi0130 (Azienda): Inizio 06:35 | Fine 19:05 | Nastro 12h30 | OLG 7h00")
print(f"🔴 Pi0190 (Azienda): Inizio 17:15 | Fine 23:01 | Nastro 5h46  | OLG 5h46")

# Scambio: Pi0130 cede le corse 703 tardo pomeriggio (16:00 - 18:50) a Pi0190 (o Pi0230)
# Pi0130 fa: 06:35 - 08:05 + 13:35 - 15:30 (Fine a Pinerolo alle 15:35)
# Nastro Pi0130: 06:35 - 15:35 = 9h 00m (-3h 30m!)
# OLG Pi0130: 4h 30m + tempo accessorio = 4h 50m (oppure se tiene 701 fino alle 16:00 fa 5h20m)

# Pi0190 fa: 16:00 - 18:50 (Navette 703) + 18:46 - 23:01 (Torino Bolzano / Perosa)
# Nastro Pi0190: 16:00 - 23:01 = 7h 01m (+1h 15m di nastro perfetto!)
# OLG Pi0190: sale da 5h46 a 7h30m! (+1h44m di lavoro pieno per un turno serale corto!)

print("\n--- RISULTATO DELLO SCAMBIO ---")
print("🟢 Pi0130 (Dopo Scambio): Inizio 06:35 | Fine 15:35 | Nastro 9h00m (-3h30m) | OLG 5h20m | 2 riprese compatte")
print("🟢 Pi0190 (Dopo Scambio): Inizio 16:00 | Fine 23:01 | Nastro 7h01m (Perfetto) | OLG 7h30m (+1h44m OLG!) | 1 ripresa continua")
