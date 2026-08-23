import fitz
import re

def find_location_for_time(pdf_path, target_shift, target_time):
    doc = fitz.open(pdf_path)
    for page in doc:
        text = page.get_text()
        if target_shift in text:
            words = page.get_text('words')
            # find the time
            time_words = [w for w in words if target_time in w[4]]
            if not time_words:
                continue
                
            print(f"Found {target_time} in {target_shift}:")
            for tw in time_words:
                y_time = tw[1]
                x_time = tw[0]
                
                # find words on the same line (y_time +/- 5), to the left of the time
                loc_words = [w for w in words if abs(w[1] - y_time) < 8 and w[0] < x_time]
                loc_words.sort(key=lambda w: w[0])
                
                # remove words that look like times or 'ID corsa'
                clean_loc = []
                for lw in loc_words:
                    if re.match(r'^\d{2}:\d{2}$', lw[4]): continue
                    if 'ID' in lw[4] or 'corsa' in lw[4] or 'Linea' in lw[4] or '|' in lw[4]: continue
                    if re.match(r'^\d+$', lw[4]): continue
                    clean_loc.append(lw[4])
                    
                loc_str = " ".join(clean_loc).strip()
                loc_str = re.sub(r'\.{3,}', '', loc_str).strip() # remove dots
                print(f"  Time {tw[4]} at Y={y_time:.1f} -> Location: {loc_str}")
            return True
    return False

find_location_for_time('Cartellini turni da settembre 2026.pdf', 'Lu001', '06:29')
find_location_for_time('Cartellini turni da settembre 2026.pdf', 'Lu001', '09:20')
find_location_for_time('Cartellini turni da settembre 2026.pdf', 'Lu001', '12:40')
