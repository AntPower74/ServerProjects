import fitz
import re

# Modifichiamo lo script del PDF per garantire che il turno Ba3510 mostri tutte le corse e il rientro a Barge fino alle 09:30

with open("/home/antonio/verifica_turni/aggiorna_dossier_stacca_box_cambi.py", "r") as f:
    code = f.read()

# Inseriamo la gestione personalizzata completa di Ba3510 per mostrare la sequenza esatta del mattino e del rientro a Barge
blocco_ba3510 = """    if code == "Ba3510":
        corse_prop_puntuali = [
            ["20:45", "20:55", "Disp", "Presa servizio & Controllo a BARGE"],
            ["04:35", "04:40", "Trasf (BUS)", "BAG PARCHEGGIO -> Viale Mazzini"],
            ["04:45", "05:15", "000280", "BARGE V. Mazzini -> OSASCO Ponte Chisone"],
            ["05:15", "05:27", "000275", "OSASCO -> Villar Perosa SKF (Operai)"],
            ["06:05", "06:34", "000275", "Villar Perosa SKF -> Pinerolo SAPAV"],
            ["06:40", "07:10", "000281", "PINEROLO Stazione FS -> Candiolo / CAS"],
            ["07:23", "08:05", "000278", "PANCALIERI -> PINEROLO Piazza Cavour"],
            ["08:05", "08:15", "Trasf (BUS)", "PINEROLO P. Cavour -> Pinerolo Deposito"],
            ["08:45", "09:15", "000280", "PINEROLO FS -> BARGE V. Mazzini (Corsa Rientro)"],
            ["09:15", "09:20", "Trasf (BUS)", "BARGE Viale Mazzini -> BAG PARCHEGGIO"],
            ["09:20", "09:30", "Disp", "Pulizia interna & Fine Spezzone a BARGE"]
        ]
        p_fine = "09:30 / 23:22"
        p_nastro = "12h 45m"
        p_olg = "7h 32m"
        p_rip = "2"
        p_pasto = pasto_att
        stato_header = "🟢 SPEZZONE BARGE CON RIENTRO IN LINEA 000280"
        box_diff_text = f"• <b>&Delta; Nastro:</b> 12h 45m | • <b>&Delta; OLG (Paga):</b> 7h 32m | • <b>&Delta; Riprese:</b> 2 riprese<br/>" \
                        f"• <b>CORSA DI RIENTRO:</b> Alle <b>08:45</b> rientra da Pinerolo Stazione FS a Barge con la <b>corsa di linea passeggeri 000280 (Arr. 09:15)</b> e chiusura a Barge alle 09:30."
    elif code == "To0280":"""

code = code.replace('    if code == "To0280":', blocco_ba3510)

with open("/home/antonio/verifica_turni/aggiorna_dossier_stacca_box_cambi.py", "w") as f:
    f.write(code)

print("Aggiornamento script eseguito. Ricompilazione PDF...")
