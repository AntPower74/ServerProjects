import pdfplumber
import re
import csv

def parse_turni(pdf_path, output_csv):
    with pdfplumber.open(pdf_path) as pdf:
        turni = []
        
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue
            
            lines = text.split('\n')
            
            codice_turno = ""
            deposito = ""
            giorno = ""
            inizio = ""
            fine = ""
            
            for i, line in enumerate(lines):
                if "DEPOSITO:" in line:
                    parts = line.split("DEPOSITO:")
                    if i > 0:
                        codice_turno = lines[i-1].strip()
                    deposito = parts[1].strip()
                if "DAYS:" in line:
                    giorno = line.split("DAYS:")[1].strip()
                if "SIGN ON:" in line and "SIGN OFF:" in line:
                    m = re.search(r"SIGN ON:\s*([\d:]+),\s*SIGN OFF:\s*([\d:]+)", line)
                    if m:
                        inizio = m.group(1)
                        fine = m.group(2)
            
            corse = []
            current_corsa = None
            
            for line in lines:
                m_corsa = re.search(r"ID corsa:\s*([A-Za-z0-9_]+)\s*\|\s*Linea:\s*([A-Za-z0-9_]+)", line)
                if m_corsa:
                    current_corsa = {
                        "id": m_corsa.group(1),
                        "linea": m_corsa.group(2),
                        "stops": []
                    }
                    corse.append(current_corsa)
                    continue
                
                if current_corsa:
                    line_clean = re.sub(r'\.+$', '', line).strip()
                    m_stop = re.search(r'^(.*?)([\d\.\s:]+)$', line_clean)
                    if m_stop:
                        stop_name = m_stop.group(1).strip()
                        # Clean up weird OCR artifacts
                        stop_name = stop_name.replace('Bolzan0o', 'Bolzano')
                        stop_name = re.sub(r'[\d\.\s:]+$', '', stop_name).strip() # remove trailing digits from name
                        
                        time_raw = m_stop.group(2)
                        stop_time = re.sub(r'[^\d:]', '', time_raw)
                        
                        if len(stop_time) >= 4 and len(stop_name) > 3:
                            if len(stop_time) == 4 and ':' not in stop_time:
                                stop_time = stop_time[:2] + ':' + stop_time[2:]
                            elif len(stop_time) >= 5:
                                stop_time = stop_time[-5:] # get e.g. 08:19
                            
                            # Valid time check
                            if re.match(r'^\d{2}:\d{2}$', stop_time):
                                current_corsa["stops"].append({"name": stop_name, "time": stop_time})
                    else:
                        if "ID corsa:" in line or "PAUSA" in line or "EXTRA LAYOVER" in line:
                            current_corsa = None
            
            if not corse:
                turni.append([codice_turno, codice_turno, deposito, giorno, inizio, fine, "", "", "", "", ""])
            else:
                for c in corse:
                    if len(c["stops"]) >= 2:
                        da = c["stops"][0]["name"]
                        a = c["stops"][-1]["name"]
                        partenza = c["stops"][0]["time"]
                        arrivo = c["stops"][-1]["time"]
                    elif len(c["stops"]) == 1:
                        da = c["stops"][0]["name"]
                        a = da
                        partenza = c["stops"][0]["time"]
                        arrivo = partenza
                    else:
                        da = ""
                        a = ""
                        partenza = ""
                        arrivo = ""
                    turni.append([codice_turno, codice_turno, deposito, giorno, inizio, fine, c["linea"], da, a, partenza, arrivo])

        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Codice_Turno', 'Nome_Turno', 'Deposito', 'Giorno', 'Turno_Ora_Inizio', 'Turno_Ora_Fine', 'Corsa_Linea', 'Corsa_Da', 'Corsa_A', 'Corsa_Ora_Partenza', 'Corsa_Ora_Arrivo'])
            for t in turni:
                writer.writerow(t)
        print(f"Estratti {len(turni)} record e salvati in {output_csv}")

if __name__ == "__main__":
    parse_turni('Cartellini_turni.pdf', 'Cartellini_Turni.csv')
