import fitz
import re

def parse_time(time_str):
    # converts "04:40" to "04.40" for the Google Sheet format
    return time_str.replace(':', '.')

def extract_shift_from_cartellino(pdf_paths):
    shifts = {}
    for pdf_path in pdf_paths:
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text = page.get_text('words')
                # sort by y, then x
                text.sort(key=lambda w: (w[1], w[0]))
                
                # identify shift name (top left)
                shift_name = None
                for w in text[:20]:
                    if re.match(r'^[A-Z][a-z]\d{3}$', w[4]):
                        shift_name = w[4]
                        break
                        
                if not shift_name:
                    continue
                    
                # get full text string for regex
                full_text = page.get_text()
                
                # find SIGN ON / SIGN OFF
                m_sign = re.search(r'SIGN ON:\s*(\d{2}:\d{2}),\s*SIGN OFF:\s*(\d{2}:\d{2})', full_text)
                if not m_sign:
                    continue
                    
                sign_on = m_sign.group(1)
                sign_off = m_sign.group(2)
                
                # find PAUSA
                pauses = re.findall(r'PAUSA\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})', full_text)
                # Ensure they are sorted by time
                pauses.sort()
                
                # construct riprese
                riprese = []
                current_start = sign_on
                for p_start, p_end in pauses:
                    riprese.append((parse_time(current_start), parse_time(p_start)))
                    current_start = p_end
                riprese.append((parse_time(current_start), parse_time(sign_off)))
                
                shifts[shift_name] = riprese
        except Exception as e:
            print(f"Error on {pdf_path}: {e}")
            
    return shifts

pdfs = [
    'Cartellini turni da settembre 2026.pdf',
    'cartellini scolastici torino attuali.pdf',
    'cartellini scolastici pinerolo attuali.pdf',
    'Turni dal 100925_giov.base scolastico.pdf'
]

shifts = extract_shift_from_cartellino(pdfs)
print("Extracted", len(shifts), "shifts")
print("Lu001:", shifts.get('Lu001'))
print("Lu002:", shifts.get('Lu002'))
print("Pe008:", shifts.get('Pe008'))
print("Pi004:", shifts.get('Pi004'))
print("To026:", shifts.get('To026'))

