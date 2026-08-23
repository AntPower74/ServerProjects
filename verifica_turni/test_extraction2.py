import fitz
import re

pdfs = [
    'Cartellini turni da settembre 2026.pdf',
    'cartellini scolastici torino attuali.pdf',
    'cartellini scolastici pinerolo attuali.pdf',
    'Turni dal 100925_giov.base scolastico.pdf'
]

shifts_found = 0
for pdf_path in pdfs:
    doc = fitz.open(pdf_path)
    for page in doc:
        text = page.get_text()
        
        shift_name = None
        for line in text.split('\n'):
            line = line.strip()
            if re.match(r'^[A-Z][a-z]\d{3}$', line):
                shift_name = line
                break
                
        if not shift_name:
            continue
            
        m = re.search(r'SIGN ON:\s*(\d{2}:\d{2})[\s,]*SIGN OFF:\s*(\d{2}:\d{2})', text.replace('\n', ' '))
        if m:
            shifts_found += 1
        else:
            print(f"Missing sign on/off for {shift_name} in {pdf_path}")
            # print a snippet
            idx = text.find('SIGN ON')
            if idx != -1:
                print("Found SIGN ON but regex failed:", text[idx:idx+50])
            else:
                print("SIGN ON not found in text!")
                
print("Found", shifts_found, "shifts")
