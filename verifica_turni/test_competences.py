import fitz
import re

doc = fitz.open('Turni settembre 2026/Crew_Graph__LUSERNA.pdf')
page = doc[0]
blocks = page.get_text('blocks')
blocks = sorted(blocks, key=lambda b: b[1])

shifts = []
current_shift = None

for b in blocks:
    x0, y0, x1, y1, text, block_no, block_type = b
    text = text.strip()
    
    if x0 < 30 and not text.startswith('(') and len(text) >= 2 and 'Crew Graph' not in text and 'Service:' not in text:
        if current_shift:
            shifts.append(current_shift)
        current_shift = {'name': text, 'hours': '', 'blocks': []}
        continue
        
    if current_shift:
        current_shift['blocks'].append(b)

if current_shift:
    shifts.append(current_shift)

for s in shifts[:2]:
    nome = s['name']
    
    # We want to collect all text that is NOT the name, NOT the hours, and NOT the start/end times.
    # Actually, we can just collect ALL text in the band, clean it, and print it.
    all_text = []
    for b in s['blocks']:
        t = b[4].strip()
        clean_t = re.sub(r'(.)\1{2}', r'\1', t)
        
        # skip hours
        if clean_t.startswith('(') and clean_t.endswith(')'):
            continue
            
        # extract lines
        lines = clean_t.split('\n')
        # filter out lines that are just times
        non_time_lines = []
        for line in lines:
            line = line.strip()
            if not line: continue
            if re.match(r'^[-–]?\d{2}:\d{2}$', line):
                continue
            non_time_lines.append(line)
            
        if non_time_lines:
            all_text.extend(non_time_lines)
            
    # Deduplicate adjacent elements to prevent `11 11` if it's the same block
    # Actually, the user string was "11 11 11 104"
    print(f"Turno: {nome}")
    print("Competenze/Percorso:", " ".join(all_text))
    print("-" * 30)
