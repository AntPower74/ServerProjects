import fitz
import re

# Modifichiamo lo script per To0280:
# Il turno To0280 fa 3 giri A/R di Caselle.
# L'ultimo arrivo a Carlo Felice è alle 11:45.
# Dalle 11:45 alle 12:30 c'è la sosta tecnica/pausa a Carlo Felice.
# Dalle 12:30 alle 13:00 c'è il trasferimento di rientro TO Carlo Felice -> TORINO DEPOSITO (Grugliasco).
# Dalle 13:00 alle 13:10 Disp: Pulizia interna autobus & Smonto a 8h00 piene (40h/sett).

print("Correzione To0280 con dicitura chiara e senza raccordi fittizi...")
