import re
import pdfplumber

with pdfplumber.open('/PDF cartellino turni/Cartellini_Turni_DomenicaEstivo.pdf') as pdf:
    for line in pdf.pages[0].extract_text().split('\n'):
        if line.startswith('000279'):
            m = re.match(r'^(\d{6})\s+(.+)$', line)
            rest = m.group(2).strip()
            orari_reali = re.findall(r'\b(\d{1,2}[.:]\d{2})\b', rest)
            print(orari_reali)
            
            def parse_orario(o):
                o = o.replace('.', ':')
                if o.count(':') == 1:
                    parts = o.split(':')
                    if len(parts[0]) == 1:
                        return f"0{o}"
                return o
            
            partenza = parse_orario(orari_reali[0]) if len(orari_reali) > 0 else ""
            arrivo = parse_orario(orari_reali[1]) if len(orari_reali) > 1 else ""
            
            print(partenza, arrivo)
