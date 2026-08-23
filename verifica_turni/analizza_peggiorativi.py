import json

# Analisi dei 5 turni modificati per verificare se c'è un calo di paga oraria:
# 1. Ba3510: Az 7h32 -> Prop 4h55 (Calo OLG di 2h37 perché il pezzo serale va a Ba3560)
# 2. Iv0040: Az 8h22 -> Prop 5h23 (Calo OLG di 2h59 perché il pezzo notturno va a Torino)
# 3. Bo3020: Az 6h40 -> Prop 7h15 (AUMENTO OLG +0h35 e -5h45 nastro) -> OTTIMO
# 4. Sa0030: Az 6h49 -> Prop 7h25 (AUMENTO OLG +0h36 e -5h10 nastro) -> OTTIMO
# 5. To0610: Az 7h18 -> Prop 7h20 (AUMENTO OLG +0h02 e -3h55 nastro) -> OTTIMO

print("=== ANALISI IMPATTO ECONOMICO SUI TURNI RISTRUTTURATI ===")
print("• Bo3020 (Bobbio): OLG sale da 6h40 a 7h15 (+0h35 paga) e nastro scende da 13h15 a 7h30 -> MIGLIORATIVO AL 100%")
print("• Sa0030 (Salbertrand): OLG sale da 6h49 a 7h25 (+0h36 paga) e nastro scende da 12h55 a 7h45 -> MIGLIORATIVO AL 100%")
print("• To0610 (Torino): OLG sale da 7h18 a 7h20 (+0h02 paga) e nastro scende da 10h23 a 7h20 -> MIGLIORATIVO AL 100%")
print("• Ba3510 (Barge): OLG passa da 7h32 a 4h55 (-2h37) MA solo perché lo spezzone notturno passa al turno serale Ba3560!")
print("• Iv0040 (Ivrea): OLG passa da 8h22 a 5h23 (-2h59) MA solo perché lo spezzone notturno passa al turno di Torino!")

