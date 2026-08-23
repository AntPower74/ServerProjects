import pdfplumber
import re

with pdfplumber.open('Turni dal 100925_giov.base scolastico.pdf') as pdf:
    text = pdf.pages[0].extract_text(layout=True)
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if line.startswith("  01 "):
            tokens = line.split()
            if len(tokens) >= 2:
                turno = tokens[1]
                nastro = tokens[-1]
                
                line_above = lines[i-1].strip()
                if line_above:
                    above_tokens = line_above.split()
                    if len(above_tokens) >= 2:
                        rip = above_tokens[-1]
                        olg_token = above_tokens[-2]
                        olg = re.sub(r'[^\d,]', '', olg_token)
                        print(f"Turno: {turno}, OLG: {olg}, Nastro: {nastro}, Rip: {rip}")
