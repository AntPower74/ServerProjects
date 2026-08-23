import fitz
import re

doc = fitz.open('Turni settembre 2026/Crew_Graph__TORINO.pdf')
page = doc[0]
blocks = page.get_text('blocks')

# Sort by Y0 coordinate
blocks = sorted(blocks, key=lambda b: b[1])

# A shift block usually starts with a block at X < 30 that doesn't start with '('
# Let's group by finding the Shift Names and taking all blocks until the next Shift Name.

shifts = []
current_shift = None

for b in blocks:
    x0, y0, x1, y1, text, block_no, block_type = b
    text = text.strip()
    
    # Is it a shift name?
    # Usually X is very small (like < 20) and it doesn't start with '('
    if x0 < 20 and not text.startswith('(') and len(text) >= 2:
        if current_shift:
            shifts.append(current_shift)
        current_shift = {'name': text, 'hours': '', 'blocks': []}
        continue
        
    if current_shift:
        current_shift['blocks'].append(text)

if current_shift:
    shifts.append(current_shift)

# Now parse the blocks for each shift
for s in shifts[:5]:
    nome = s['name']
    
    # Find paid hours
    hours = ""
    for t in s['blocks']:
        if t.startswith('(') and t.endswith(')') and ':' in t:
            hours = t.replace('(', '').replace(')', '')
            break
            
    # Find times
    starts = []
    ends = []
    for t in s['blocks']:
        # We need to deduplicate characters first because of the bold effect
        clean_t = re.sub(r'(.)\1{2}', r'\1', t)
        for line in clean_t.split('\n'):
            if re.search(r'(?<![-–])\b\d{2}:\d{2}\b', line):
                starts.extend(re.findall(r'(?<![-–])\b\d{2}:\d{2}\b', line))
            if re.search(r'[-–]\d{2}:\d{2}\b', line):
                ends.extend(re.findall(r'[-–](\d{2}:\d{2})\b', line))
                
    # Deduplicate start/end times while preserving order (since they are repeated)
    unique_starts = []
    for st in starts:
        if not unique_starts or unique_starts[-1] != st:
            unique_starts.append(st)
            
    unique_ends = []
    for en in ends:
        if not unique_ends or unique_ends[-1] != en:
            unique_ends.append(en)
            
    print(f"Turno: {nome}, Ore Pagate: {hours}")
    print(f"Starts: {unique_starts}")
    print(f"Ends: {unique_ends}")
    print("-" * 30)

