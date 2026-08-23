import fitz
import re
import json

def parse_arriva_cartellini(pdf_path):
    doc = fitz.open(pdf_path)
    shifts = {}
    
    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text()
        
        m = re.search(r'Cartellino di marcia del turno:\s*(\S+)', text)
        if not m: continue
        shift_name = m.group(1).strip()
        
        words = page.get_text('words')
        
        partenza_x = 522
        arrivo_x = 560
        
        # We also need the location strings!
        # The location is typically the first part of the row.
        # Let's group words by Y coordinate
        lines = {}
        for w in words:
            y = round(w[1], 1)
            found = False
            for k in lines:
                if abs(k - y) < 4:
                    lines[k].append(w)
                    found = True
                    break
            if not found:
                lines[y] = [w]
                
        # Find the start of the table
        table_start_y = 0
        for y, lw in sorted(lines.items()):
            text_line = " ".join(w[4] for w in sorted(lw, key=lambda x: x[0]))
            if "Partenza Arrivo" in text_line or "I. Ripresa" in text_line:
                table_start_y = y
                break
                
        if table_start_y == 0: continue
        
        # Now extract rows
        rows = []
        for y, lw in sorted(lines.items()):
            if y <= table_start_y + 5: continue
            
            # check if it's a valid row with times
            partenza, arrivo = None, None
            loc_words = []
            
            lw.sort(key=lambda x: x[0])
            for w in lw:
                if w[0] < 450: # before the time columns
                    loc_words.append(w[4])
                elif 500 < w[0] < 540 and re.match(r'^\d{1,2}\.\d{2}$', w[4]):
                    partenza = w[4]
                elif 540 < w[0] < 580 and re.match(r'^\d{1,2}\.\d{2}$', w[4]):
                    arrivo = w[4]
                    
            if partenza and arrivo and loc_words:
                loc_text = " ".join(loc_words)
                # Parse times to minutes
                try:
                    hp, mp = map(int, partenza.split('.'))
                    ha, ma = map(int, arrivo.split('.'))
                    pmins = hp * 60 + mp
                    amins = ha * 60 + ma
                    # handle cross midnight
                    if amins < pmins: amins += 1440
                    rows.append({
                        'loc': loc_text,
                        'start': pmins,
                        'end': amins
                    })
                except:
                    pass
                    
        # Now form riprese using >30 min gap rule
        if not rows: continue
        
        # We need to sort rows by start time, but they are already chronological
        riprese = []
        sostas = []
        
        curr_start = rows[0]['start']
        curr_end = rows[0]['end']
        
        for r in rows[1:]:
            gap = r['start'] - curr_end
            if gap > 30:
                # new ripresa
                riprese.append([curr_start, curr_end])
                # the location of the Sosta is the location of the previous trip's end OR the next trip's start
                # Usually they are similar. Let's just use the end location of the previous trip, which is typically the second part of the loc string
                # e.g. "TORINO PN - CASELLE APT" -> CASELLE APT
                sostas.append(r['loc']) # Actually r['loc'] is the current trip's location. The Sosta is where they waited.
                curr_start = r['start']
                curr_end = r['end']
            else:
                curr_end = max(curr_end, r['end'])
                
        riprese.append([curr_start, curr_end])
        
        # Also need to extract the Sosta string properly.
        # "TORINO PN - CASELLE APT (Accellerato)" -> "CASELLE APT"
        
        if shift_name not in shifts:
            shifts[shift_name] = {'riprese': riprese, 'sostas': sostas, 'rows': rows}

    return shifts

data = parse_arriva_cartellini('Turni settembre 2025/cartellini_cas32.pdf')
print(f'Extracted {len(data)} shifts.')
for k in ['Ca0040', 'To0130', 'To0700']:
    if k in data:
        print(f'{k}:')
        print('  Riprese:', data[k]['riprese'])
        print('  Sostas:', data[k]['sostas'])
        print('  Rows:', len(data[k]['rows']))
