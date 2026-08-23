import fitz
import re

doc = fitz.open('Turni settembre 2026/Crew_Graph__TORINO.pdf')
page = doc[0]
blocks = page.get_text('blocks')

blocks = sorted(blocks, key=lambda b: b[1])

shifts = []
current_shift = None

for b in blocks:
    x0, y0, x1, y1, text, block_no, block_type = b
    text = text.strip()
    
    if x0 < 20 and not text.startswith('(') and len(text) >= 2 and 'Crew Graph' not in text:
        if current_shift:
            shifts.append(current_shift)
        current_shift = {'name': text, 'hours': '', 'blocks': []}
        continue
        
    if current_shift:
        current_shift['blocks'].append(b)

if current_shift:
    shifts.append(current_shift)

for s in shifts[:10]:
    nome = s['name']
    
    hours = ""
    for b in s['blocks']:
        t = b[4].strip()
        if t.startswith('(') and t.endswith(')') and ':' in t:
            hours = t.replace('(', '').replace(')', '')
            break
            
    time_blocks = []
    for b in s['blocks']:
        t = b[4].strip()
        clean_t = re.sub(r'(.)\1{2}', r'\1', t)
        
        for line in clean_t.split('\n'):
            line = line.strip()
            if re.search(r'\d{2}:\d{2}', line):
                match = re.search(r'\d{2}:\d{2}', line)
                if match:
                    time_blocks.append((b[0], match.group()))
                    
    time_blocks.sort(key=lambda x: x[0])
    
    ordered_times = [t for _, t in time_blocks]
    unique_times = list(dict.fromkeys(ordered_times))
            
    print(f"Turno: {nome}, Ore Pagate: {hours}")
    print(f"Times: {unique_times}")
    print("-" * 30)
