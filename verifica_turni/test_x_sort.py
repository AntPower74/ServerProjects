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

for s in shifts[:5]:
    nome = s['name']
    
    hours = ""
    for b in s['blocks']:
        t = b[4].strip()
        if t.startswith('(') and t.endswith(')') and ':' in t:
            hours = t.replace('(', '').replace(')', '')
            break
            
    # Find time blocks
    time_blocks = []
    for b in s['blocks']:
        t = b[4].strip()
        clean_t = re.sub(r'(.)\1{2}', r'\1', t)
        
        # Split by newlines as sometimes they are multiline
        for line in clean_t.split('\n'):
            line = line.strip()
            # If it's a time (maybe with a dash)
            if re.search(r'\d{2}:\d{2}', line):
                # Extract just the HH:MM
                match = re.search(r'\d{2}:\d{2}', line)
                if match:
                    # We store the X coordinate to sort them left-to-right
                    time_blocks.append((b[0], match.group()))
                    
    # Sort by X coordinate (left to right)
    time_blocks.sort(key=lambda x: x[0])
    
    # Extract times and deduplicate adjacent identical times
    ordered_times = []
    for _, t in time_blocks:
        if not ordered_times or ordered_times[-1] != t:
            ordered_times.append(t)
            
    print(f"Turno: {nome}, Ore Pagate: {hours}")
    print(f"Times: {ordered_times}")
    print("-" * 30)

