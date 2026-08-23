import re
texts = [
    "TORINO - Autostazione c.so Bolzano - IVREA - loc Banchette 225",
    "CASELLE Aeroporto - TO - piazza Carlo Felice",
    "PINEROLO - movicentro - PER - V. Nazionale 6 (Deposito Ex Sapav)",
    "BARGE-Viale Mazzini/Cavallotta - AIRASCA - stabilimento SKF",
    "OULX - Stazione FS - SESTRIERE - parcheggio"
]
for t in texts:
    parts = re.split(r'\s+-\s+(?=[A-Z]{2,})', t, maxsplit=1)
    if len(parts) == 1:
        # fallback
        parts = re.split(r'\s+-\s+', t, maxsplit=1)
    print(t)
    print("  DA:", parts[0].strip())
    print("  A :", parts[1].strip() if len(parts)>1 else "")
