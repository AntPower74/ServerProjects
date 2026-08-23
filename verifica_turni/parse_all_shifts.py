import fitz
import re
import json

pdfs = [
    'Cartellini turni da settembre 2026.pdf',
    'cartellini scolastici torino attuali.pdf',
    'cartellini scolastici pinerolo attuali.pdf',
    'Turni dal 100925_giov.base scolastico.pdf'
]

shifts = {}

for pdf_path in pdfs:
    doc = fitz.open(pdf_path)
    for page in doc:
        words = page.get_text('words')
        
        shift_name = None
        for w in words:
            if re.match(r'^[A-Z][a-z]\d{3}$', w[4]) and w[1] < 100:
                shift_name = w[4]
                break
                
        if not shift_name:
            continue
            
        full_text = page.get_text().replace('\n', ' ')
        
        m = re.search(r'SIGN ON:\s*(\d{2}:\d{2})[\s,]*SIGN OFF:\s*(\d{2}:\d{2})', full_text)
        if not m:
            continue
            
        sign_on = m.group(1)
        sign_off = m.group(2)
        
        # Get breaks from PAUSA
        pauses = re.findall(r'PAUSA\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})', full_text)
        pauses.sort()
        
        def parse_t(t): return t.replace(':', '.')
        
        riprese = []
        curr = sign_on
        for ps, pe in pauses:
            riprese.append((parse_t(curr), parse_t(ps)))
            curr = pe
        riprese.append((parse_t(curr), parse_t(sign_off)))
        
        # Lu001 becomes Lu0010, Pe008 becomes Pe0080
        m_name = re.match(r'^([A-Z][a-z])(\d+)$', shift_name)
        if m_name:
            norm_name = f"{m_name.group(1)}{int(m_name.group(2)):03d}0"
            shifts[norm_name] = riprese

print(f"Parsed {len(shifts)} shifts.")
print("To0260:", shifts.get("To0260"))
print("Pt0040:", shifts.get("Pt0040"))
print("Lu0040:", shifts.get("Lu0040"))

with open('exact_cartellini_times.json', 'w') as f:
    json.dump(shifts, f)

