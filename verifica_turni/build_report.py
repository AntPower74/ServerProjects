import csv
import glob
import re
from collections import defaultdict

from parse_cartellini import parse_cartellini
from extract_crew_graph import extract_file_shifts

CARTELLINI_PDF = 'Turni settembre 2026/Cartellini turni da settembre 2026.pdf'
GRAPH_FILES = sorted(glob.glob('Turni settembre 2026/Crew_Graph__*.pdf'))
OUT_CSV = '/tmp/claude-1004/-home-antonio/7b054381-0b92-48d2-b0ae-aa7e478353d9/scratchpad/verifica_turni_settembre_2026.csv'


def dep_label(path):
    return path.split('Crew_Graph__')[1].replace('.pdf', '').title()


def nastro_grafico(inizio, fine):
    if not inizio or not fine:
        return ''
    ih, im = map(int, inizio.split(':'))
    fh, fm = map(int, fine.split(':'))
    start = ih * 60 + im
    end = fh * 60 + fm
    if end < start:
        end += 24 * 60
    diff = end - start
    return f"{diff // 60:02d}:{diff % 60:02d}"


def main():
    cartellini = parse_cartellini(CARTELLINI_PDF)
    cart_by_turno = defaultdict(list)
    for c in cartellini:
        cart_by_turno[c['turno']].append(c)

    graph_by_turno = defaultdict(list)
    for gf in GRAPH_FILES:
        label = dep_label(gf)
        for s in extract_file_shifts(gf):
            s['file_deposito'] = label
            graph_by_turno[s['turno']].append(s)

    def turno_key(turno):
        m = re.match(r'([A-Za-z]+)(\d*)', turno)
        prefix, digits = m.group(1), m.group(2)
        return (prefix.lower(), int(digits) if digits else 0)

    all_turni = sorted(set(cart_by_turno) | set(graph_by_turno), key=turno_key)

    rows = []
    n_ok = n_mismatch = n_no_graph = n_no_cart = n_no_cart_times = 0

    for turno in all_turni:
        c_list = cart_by_turno.get(turno, [])
        g_list = graph_by_turno.get(turno, [])
        n = max(len(c_list), len(g_list), 1)
        for i in range(n):
            c = c_list[i] if i < len(c_list) else (c_list[0] if c_list else None)
            g = g_list[i] if i < len(g_list) else (g_list[0] if g_list else None)

            if c is None:
                esito = 'MANCANTE NEL CARTELLINO'
                n_no_cart += 1
            elif g is None:
                esito = 'MANCANTE NEL GRAFICO'
                n_no_graph += 1
            elif not c['sign_on'] or not c['sign_off']:
                esito = 'DATI CARTELLINO INCOMPLETI'
                n_no_cart_times += 1
            elif c['sign_on'] == g['inizio_grafico'] and c['sign_off'] == g['fine_grafico']:
                esito = 'OK'
                n_ok += 1
            else:
                esito = 'DISCREPANZA'
                n_mismatch += 1

            rows.append({
                'Turno': turno,
                'Deposito (cartellino)': c['deposito'] if c else '',
                'Deposito (grafico)': g['file_deposito'] if g else '',
                'Giorni': c['giorni'] if c else '',
                'Data': c['data'] if c else '',
                'Tempo Pagato (cartellino)': c['tempo_pagato'] if c else '',
                'Tempo Pagato (grafico)': g['paid_graph'] if g else '',
                'Sign On (cartellino)': c['sign_on'] if c else '',
                'Sign Off (cartellino)': c['sign_off'] if c else '',
                'Inizio (grafico)': g['inizio_grafico'] if g else '',
                'Fine (grafico)': g['fine_grafico'] if g else '',
                'Nastro (grafico)': nastro_grafico(g['inizio_grafico'], g['fine_grafico']) if g else '',
                'Nastro (cartellino)': c['nastro'] if c else '',
                'Riprese (grafico)': g['n_riprese'] if g else '',
                'Esito': esito,
            })

    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Righe totali: {len(rows)}")
    print(f"OK: {n_ok}")
    print(f"Discrepanza: {n_mismatch}")
    print(f"Mancante nel grafico: {n_no_graph}")
    print(f"Mancante nel cartellino: {n_no_cart}")
    print(f"Cartellino con orari incompleti: {n_no_cart_times}")
    print(f"Salvato in: {OUT_CSV}")


if __name__ == '__main__':
    main()
