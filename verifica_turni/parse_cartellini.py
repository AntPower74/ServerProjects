import re
import csv
from pdfminer.high_level import extract_text

def parse_cartellini(pdf_path):
    text = extract_text(pdf_path)

    # Find start positions of each turno block: "<NAME>\n\nDAYS:"
    starts = [(m.start(1), m.group(1)) for m in re.finditer(r'([A-Za-z0-9]+)\n\nDAYS:', text)]
    starts.append((len(text), None))  # sentinel for last block end

    turni = []
    for i in range(len(starts) - 1):
        pos, name = starts[i]
        end = starts[i + 1][0]
        block = text[pos:end]

        giorni = re.search(r'DAYS:\s*(.+)', block)
        data = re.search(r'COMMENCING:\s*([\d/]+)', block)
        tempo = re.search(r'TEMPO PAGATO:\s*([\d:]+)', block)
        deposito = re.search(r'DEPOSITO:\s*(.+)', block)
        signon = re.search(r'SIGN ON:\s*([\d:]+)', block)
        signoff = re.search(r'SIGN OFF:\s*([\d:]+)', block)
        nastro = re.search(r'NASTRO:\s*(.+)', block)

        riprese = []
        for pm in re.finditer(r'PAUSA\s+(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})', block):
            ph, pmn = map(int, pm.group(1).split(':'))
            qh, qmn = map(int, pm.group(2).split(':'))
            start = ph * 60 + pmn
            end = qh * 60 + qmn
            if end < start:
                end += 24 * 60
            dur = end - start
            if dur >= 31:
                riprese.append(f"{pm.group(1)}-{pm.group(2)} ({dur}min)")

        turni.append({
            'turno': name,
            'giorni': giorni.group(1).strip() if giorni else '',
            'data': data.group(1) if data else '',
            'tempo_pagato': tempo.group(1) if tempo else '',
            'deposito': deposito.group(1).strip() if deposito else '',
            'sign_on': signon.group(1) if signon else '',
            'sign_off': signoff.group(1) if signoff else '',
            'nastro': nastro.group(1).strip() if nastro else '',
            'riprese': '; '.join(riprese),
        })

    return turni


if __name__ == '__main__':
    turni = parse_cartellini('Turni settembre 2026/Cartellini turni da settembre 2026.pdf')
    print(f"Totale turni: {len(turni)}")
    with open('/tmp/claude-1004/-home-antonio/7b054381-0b92-48d2-b0ae-aa7e478353d9/scratchpad/cartellini_parsed.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(turni[0].keys()))
        writer.writeheader()
        writer.writerows(turni)
    print("Salvato in cartellini_parsed.csv")

    from collections import Counter
    deps = Counter(t['deposito'] for t in turni)
    for d, c in deps.items():
        print(d, c)
