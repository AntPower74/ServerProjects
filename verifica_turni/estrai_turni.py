import re
import csv
from pdfminer.high_level import extract_text

def parse_pdf(pdf_path, output_csv):
    text = extract_text(pdf_path)
    
    # regex to match:
    # <Turno>
    # DAYS: <Days>
    # COMMENCING: <Date>
    # TEMPO PAGATO: <Tempo>
    # DEPOSITO: <Deposito>
    # SIGN ON: <SignOn>, SIGN OFF: <SignOff>
    # NASTRO: <Nastro>
    
    # We can split text by "DAYS:" to process chunks
    chunks = text.split("DAYS:")
    
    turni = []
    
    for i in range(1, len(chunks)):
        chunk = chunks[i]
        
        # Turno name is usually at the end of the previous chunk
        prev_chunk = chunks[i-1]
        turno_match = re.search(r'([A-Za-z0-9_]+)\s*$', prev_chunk)
        turno = turno_match.group(1) if turno_match else ""
        
        giorni_match = re.search(r'^\s*(.*?)\n', chunk)
        giorni = giorni_match.group(1).strip() if giorni_match else ""
        
        data_match = re.search(r'COMMENCING:\s*([\d/]+)', chunk)
        data = data_match.group(1) if data_match else ""
        
        tempo_match = re.search(r'TEMPO PAGATO:\s*([\d:]+)', chunk)
        tempo = tempo_match.group(1) if tempo_match else ""
        
        deposito_match = re.search(r'DEPOSITO:\s*(.*?)\n', chunk)
        deposito = deposito_match.group(1).strip() if deposito_match else ""
        
        sign_on_match = re.search(r'SIGN ON:\s*([\d:]+)', chunk)
        sign_on = sign_on_match.group(1) if sign_on_match else ""
        
        sign_off_match = re.search(r'SIGN OFF:\s*([\d:]+)', chunk)
        sign_off = sign_off_match.group(1) if sign_off_match else ""
        
        nastro_match = re.search(r'NASTRO:\s*(.*?)\n', chunk)
        nastro = nastro_match.group(1).strip() if nastro_match else ""
        
        turni.append([turno, deposito, giorni, data, sign_on, sign_off, tempo, nastro])

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Turno', 'Deposito', 'Giorni', 'Data', 'Sign On', 'Sign Off', 'Tempo Pagato', 'Nastro'])
        for turno in turni:
            writer.writerow(turno)

    print(f"Estratti {len(turni)} turni e salvati in {output_csv}")

if __name__ == "__main__":
    parse_pdf('Cartellini_turni.pdf', 'turni_estratti.csv')
