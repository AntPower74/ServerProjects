import re

with open("/home/antonio/verifica_turni/aggiorna_dossier_zero_olg_fittizio.py", "r") as f:
    code = f.read()

# Sostituiamo la logica di To0660 per trattarlo come TURNO CONFERMATO (Blu)
vecchio_blocco = """    elif code == "To0660":
        # To0660: Manteniamo OLG reale a 7h38m e abbattiamo il nastro eliminando lo spezzamento
        p_nastro = "8h 05m"
        p_rip = "1"
        stato_header = "🟢 PROPOSTA OTTIMIZZATA (NASTRO COMPATTO & 1 RIPRESA)"
        box_diff_text = f"• <b>&Delta; Nastro:</b> <font color='#006600'><b>Da {n_att} a {p_nastro} (Compattato)</b></font> | " \\
                        f"• <b>&Delta; Ore Pagate (OLG):</b> Confermato {p_olg} (Effettivo) | " \\
                        f"• <b>&Delta; Riprese:</b> Da 2 a 1 (Continuo)<br/>" \\
                        f"• <b>MIGLIORAMENTO:</b> Eliminato lo spezzamento passivo a Pinerolo (20:34-21:30). Turno continuo a 1 sola ripresa.\""""

nuovo_blocco = """    elif code == "To0660":
        p_fine = "24:18"
        p_nastro = "8h 27m"
        p_olg = "7h 38m"
        p_rip = "2"
        stato_header = "🔵 TURNO CONFERMATO (ORARIO AZIENDALE REGOLARE)"
        box_diff_text = f"• <b>&Delta; Nastro:</b> 0h 00m (Confermato 8h 27m) | " \\
                        f"• <b>&Delta; Ore Pagate (OLG):</b> Confermato 7h 38m | " \\
                        f"• <b>&Delta; Riprese:</b> Confermato 2 (Sosta tecnica a Pinerolo)<br/>" \\
                        f"• <b>STATO DEL TURNO:</b> <b>TURNO GIÀ CONFORME E SOSTENIBILE.</b> Copre la sequenza completa pomeridiana/serale Pinerolo + MOPAR Rivalta con rientro a Grugliasco.\""""

code = code.replace(vecchio_blocco, nuovo_blocco)

with open("/home/antonio/verifica_turni/aggiorna_dossier_zero_olg_fittizio.py", "w") as f:
    f.write(code)

print("Aggiornamento To0660 completato!")
