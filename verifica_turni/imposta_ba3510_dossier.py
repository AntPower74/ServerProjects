import re

with open("/home/antonio/verifica_turni/genera_dossier_con_codici_corsa.py", "r") as f:
    code = f.read()

# Aggiorniamo la gestione di Ba3510 per chiarire i due spezzoni e la violazione del nastro aziendale
blocco_ba3510 = """    if code == "Ba3510":
        p_fine = "09:30 / 23:22"
        p_nastro = "12h 45m (Azienda) -> 7h 45m"
        p_olg = "7h 32m"
        p_rip = "2 (Azienda) -> 1"
        stato_header = "🟢 SANATORIA SUPERO NASTRO ILLEGALE (12h45 -> 7h45)"
        box_diff_text = f"• <b>VIOLAZIONE CCNL AZIENDA:</b> Nastro illegale di <b>12h 45m</b> con voce esplicita <i>'SUPERO NASTRO ORE: 0,45'</i>.<br/>" \\
                        f"• <b>&Delta; Nastro:</b> <font color='#006600'><b>Ricondotto a 7h 45m</b></font> (Spezzone mattino 04:35-09:30 con rientro in linea passeggeri 000280 a Barge)."
    elif code == "To0280":"""

code = code.replace('    if code == "To0280":', blocco_ba3510)

with open("/home/antonio/verifica_turni/genera_dossier_con_codici_corsa.py", "w") as f:
    f.write(code)

print("Aggiornato file generatore per Ba3510!")
