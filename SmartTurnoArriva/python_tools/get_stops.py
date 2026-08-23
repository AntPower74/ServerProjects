import pdfplumber

stops = []
with pdfplumber.open("/root/000265.pdf") as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        if table:
            for row in table:
                if row[0] and len(row[0]) > 2 and row[0] not in stops:
                    stops.append(row[0].replace("\n", " ").strip())

print(stops)
