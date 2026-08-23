import fitz
import re

# Modifichiamo lo script del PDF per rendere la nota univoca:
# "CAMBIO CON: Alle 11:45 a piazza Carlo Felice CEDE IL BUS a To0710" (eliminando To0320)

with open("/home/antonio/verifica_turni/aggiorna_dossier_pulizia_riga_intestazione.py", "r") as f:
    code = f.read()

# Sostituzione nota ambigua
code = code.replace("To0710 / To0320", "To0710")
code = code.replace("CEDE A To0710 / To0320", "CEDE A To0710")
code = code.replace("CAMBIO TURNO A CARLO FELICE -> CEDE A To0710", "CAMBIO A CARLO FELICE -> CEDE IL BUS A To0710")

with open("/home/antonio/verifica_turni/aggiorna_dossier_pulizia_riga_intestazione.py", "w") as f:
    f.write(code)

print("File aggiornato. Rigenerazione PDF...")
