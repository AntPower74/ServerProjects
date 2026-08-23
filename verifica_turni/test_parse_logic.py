import re

def parse_m_exact(val):
    if val is None or val == '':
        return 0
    if isinstance(val, (int, float)):
        return round(val)
    val_str = str(val).strip()
    
    # 1. Formato "6h 30m" o "6h 30"
    m_h = re.match(r'^(\d+)\s*h\s*(\d+)?\s*m?$', val_str, re.IGNORECASE)
    if m_h:
        h = int(m_h.group(1))
        m = int(m_h.group(2)) if m_h.group(2) else 0
        return h * 60 + m

    # 2. Formato orario "06:34" o "6:34"
    if ':' in val_str:
        p = val_str.split(':')
        return int(p[0]) * 60 + int(p[1])

    # 3. Formato decimale "6.50" o "6,50" o intero "390"
    val_clean = val_str.replace(',', '.')
    try:
        f_val = float(val_clean)
        # Se > 24, è già in minuti (es. 390)
        if f_val > 24:
            return round(f_val)
        # Altrimenti è in ore decimali (es. 6.5 -> 390m)
        return round(f_val * 60)
    except:
        return 0

print("6.50 ->", parse_m_exact("6.50"), "minuti (aspettato: 390)")
print("6h 30m ->", parse_m_exact("6h 30m"), "minuti (aspettato: 390)")
print("06:34 ->", parse_m_exact("06:34"), "minuti (aspettato: 394)")
print("390 ->", parse_m_exact(390), "minuti (aspettato: 390)")
print("10h 25m ->", parse_m_exact("10h 25m"), "minuti (aspettato: 625)")
