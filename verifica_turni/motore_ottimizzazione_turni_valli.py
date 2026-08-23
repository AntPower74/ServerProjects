import json
from collections import defaultdict

with open("/home/antonio/verifica_turni/DATABASE_CORSE_DA_SHEETS.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Funzione per calcolare minuti da orario "HH:MM:SS"
def to_min(t_str):
    p = t_str.split(':')
    return int(p[0]) * 60 + int(p[1])

def fmt_min(m):
    return f"{m//60:02d}:{m%60:02d}"

print("=== MOTORE DI OTTIMIZZAZIONE E RISTRUTTURAZIONE REALE DEI TURNI ===")
print("Regole di Ottimizzazione:")
print("1. Accoppiamento continuo delle corse con soste < 30 min (Turno Unico).")
print("2. Nastro compatto target: 7h15 - 8h30 (Abbattimento stacchi passivi diurni).")
print("3. Rientro garantito al deposito di residenza a fine servizio.")
print("4. Copertura al 100% di tutte le corse commerciali aziendali.")

