import re
import pdfplumber

stops = []
with pdfplumber.open("/root/000285.pdf") as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        if table:
            for row in table:
                if row[0] and len(row[0]) > 2:
                    name = row[0]
                    # strip times
                    name = re.split(r'\s+[\d\|]', name)[0].strip()
                    if name and name not in stops:
                        stops.append(name)

print("[\n" + ",\n".join(f'            "{s}"' for s in stops) + "\n]")
