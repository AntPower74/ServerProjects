import pdfplumber
import json
import re

pdf_path = "/root/000275.pdf"
output_path = "/root/orari_275.json"

all_stops = []
all_times = []

# List of stops we care about based on the PDF
known_stops = [
    "OULX - Stazione FS", "OULX - Liceo", "OULX - p.zza Garambois", "CESANA TORINESE",
    "SESTRIERE", "PRAGELATO", "FENESTRELLE - via Nazionale", "PEROSA ARG.-pzza Terzo Alpini (Arrivo)",
    "PEROSA ARG.-pzza Terzo Alpini (Partenza)", "PINASCA", "DUBBIONE - via Nazionale",
    "VILLAR PEROSA - via Nazionale", "S. GERMANO CHISONE", "PORTE", "S. MARTINO", "ABBADIA ALPINA",
    "PONTE LEMINA", "PINEROLO - piazza Cavour", "PINEROLO - movicentro (Arrivo)", 
    "PINEROLO - movicentro (Partenza)", "PINEROLO - c.so Torino-MACUMBA", "PINEROLO Centro Studi",
    "RIVA di Pinerolo", "Bivio BOTTEGHE", "AIRASCA", "NONE Bivio", "CANDIOLO IRCCS-Centro Ricerche",
    "STUPINIGI - Palazzina di Caccia", "TORINO - p.zza Carducci", 
    "TORINO -c.so V.Eman. II (Porta Nuova FS)", "TORINO - Autostazione c.so Bolzano"
]

results = {}
for s in known_stops:
    results[s] = []

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text(x_tolerance=2, y_tolerance=2)
        if not text: continue
        
        lines = text.split('\n')
        for line in lines:
            for stop in known_stops:
                if line.startswith(stop):
                    # extract everything after the stop name
                    times_part = line[len(stop):].strip()
                    # times are usually like 6.40, 7.15, or sometimes D, R, etc.
                    # let's split by spaces
                    tokens = [t for t in times_part.split() if re.match(r'^(\d{1,2}[:.]\d{2}|[A-Z])$', t)]
                    results[stop].extend(tokens)
                    break

# Clean up empty
cleaned_results = {k: v for k, v in results.items() if len(v) > 0}

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(cleaned_results, f, indent=2, ensure_ascii=False)

print("Estratto completato! Salvato in", output_path)
