import re

with open("/home/antonio/verifica_turni/genera_dossier_con_codici_corsa.py", "r") as f:
    code = f.read()

# Sostituiamo la logica di Ba3510 per renderla limpida, corretta e matematicamente inattaccabile
vecchio = """    if code == "Ba3510":
        p_fine = "09:30 / 23:22"
        p_nastro = "12h 45m (Azienda) -> 7h 45m"
        p_olg = "7h 32m"
        p_rip = "2 (Azienda) -> 1"
        stato_header = "🟢 SANATORIA SUPERO NASTRO ILLEGALE (12h45 -> 7h45)"
        box_diff_text = f"• <b>VIOLAZIONE CCNL AZIENDA:</b> Nastro illegale di <b>12h 45m</b> con voce esplicita <i>'SUPERO NASTRO ORE: 0,45'</i>.<br/>" \\
                        f"• <b>&Delta; Nastro:</b> <font color='#006600'><b>Ricondotto a 7h 45m</b></font> (Spezzone mattino 04:35-09:30 con rientro in linea passeggeri 000280 a Barge).\""""

nuovo = """    if code == "Ba3510":
        p_fine = "09:30"
        p_nastro = "12h 45m"
        p_olg = "7h 32m"
        p_rip = "2"
        p_pasto = "1 (€ 1.00)"
        stato_header = "🔴 TURNO FUORILEGGE AZIENDA (SUPERO NASTRO 12h45 & RIPOSO 5h13)"
        box_diff_text = f"• <b>CRITICITÀ GRAVE CCNL:</b> Nastro illegale di <b>12h 45m</b> (supero di 0h45) e stacco notturno di sole <b>5h 13m</b> tra le 23:22 e le 04:35.<br/>" \\
                        f"• <b>PROPOSTA SINDACALE:</b> Separare lo spezzone serale (20:45-23:22) da quello mattutino (04:35-09:30) per garantire riposo legale e sicurezza alla guida.\"
        nota_cambio_turno = "■ <b>PROPOSTA SINDACALE:</b> Separare il servizio serale SKF Airasca (2h37) dal servizio mattutino (4h55). Rientro a Barge alle 09:30 con linea 000280."
    """

code = code.replace(vecchio, nuovo)

with open("/home/antonio/verifica_turni/genera_dossier_con_codici_corsa.py", "w") as f:
    f.write(code)

print("Aggiornamento Ba3510 eseguito!")
