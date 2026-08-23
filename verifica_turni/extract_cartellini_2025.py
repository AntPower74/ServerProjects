import re
import pdfplumber

TURNO_RE = re.compile(r'Cartellino di marcia del turno:\s*(\S+)')
LINE_RE = re.compile(r'^(.*\S)\s+(-?\d+[.,]\d+)(?:\s+[A-Z])?$')


def parse_summary_cell(cell_text):
    fields = {}
    if not cell_text:
        return fields
    for line in cell_text.split('\n'):
        line = line.strip()
        m = LINE_RE.match(line)
        if m:
            label = m.group(1).strip()
            value = m.group(2).replace(',', '.')
            fields[label] = value
    return fields


def parse_pdf(pdf_path):
    turni = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ''
            m = TURNO_RE.search(text)
            if not m:
                continue
            turno = m.group(1)

            tables = page.extract_tables()
            fields = {}
            if len(tables) >= 2:
                summary_table = tables[1]
                for row in summary_table:
                    for cell in row:
                        fields.update(parse_summary_cell(cell))

            turni.append({
                'turno': turno,
                'ore_lavoro_giornaliero': fields.get('ORE LAVORO GIORNALIERO', ''),
                'nastro_turno': fields.get('NASTRO DEL TURNO', ''),
                'numero_riprese': fields.get('NUMERO RIPRESE', ''),
                'ore_guida_complessiva': fields.get('ORE DI GUIDA COMPLESSIVA', ''),
            })
    return turni


if __name__ == '__main__':
    import sys
    turni = parse_pdf(sys.argv[1])
    for t in turni[:10]:
        print(t)
    print(len(turni))
