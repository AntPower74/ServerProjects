import fitz
import re

# Ispezioniamo i turni per capire come inserire nel PDF comparativo
# la sequenza ESATTA delle corse di linea montanti e discendenti con la loro tratta reale
# invece del testo generico

print("Verifica aggiornamento cartellini con tratte e linee reali...")
