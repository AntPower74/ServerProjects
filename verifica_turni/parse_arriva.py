import fitz
import re

def parse_arriva_cartellino(pdf_path):
    doc = fitz.open(pdf_path)
    shifts = {}
    
    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text()
        
        # Find shift name
        m = re.search(r'Cartellino di marcia del turno:\s*(\S+)', text)
        if not m: continue
        shift_name = m.group(1).strip()
        
        # We need to extract the chronological blocks of times.
        # We can extract all HH.MM times and sort them. But it's better to read the 'Partenza' and 'Arrivo' columns.
        # Let's use get_text('words') and find the times in the 'Partenza' and 'Arrivo' columns
        # In Arriva, Partenza is around X=460-480, Arrivo is around X=500-520
        # Let's dump the columns for To0700 (page 35) to see X coords!
        words = page.get_text('words')
        
        # Find the header X coords
        partenza_x, arrivo_x = 0, 0
        for w in words:
            if w[4] == 'Partenza': partenza_x = w[0]
            if w[4] == 'Arrivo': arrivo_x = w[0]
            
        print(f"Shift: {shift_name} | Partenza X: {partenza_x} | Arrivo X: {arrivo_x}")
        if shift_name == 'To0700':
            for w in words:
                if re.match(r'^\d{1,2}\.\d{2}$', w[4]):
                    print(f"Time {w[4]} at X={w[0]:.1f}, Y={w[1]:.1f}")
        
parse_arriva_cartellino('Turni settembre 2025/cartellini_cas32.pdf')
