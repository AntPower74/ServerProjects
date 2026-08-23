import fitz
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
        current_shift = {'name': text, 'y0': y0}
        continue
if current_shift:
    shifts.append(current_shift)
for s in shifts:
    print(s)
