import re

with open('/root/extract_all.py', 'r') as f:
    content = f.read()
    
new_line = """    },
    {
        "file": "/root/000285.pdf",
        "linea": "285",
        "stops": [
            "OULX - Stazione FS",
            "AMAZAS",
            "FENILS",
            "CESANA",
            "CLAVIERE",
            "Bivio SEGUIN",
            "SESTRIERE",
            "PINEROLO - Stazione FS",
            "TO - Autostazione c.so Bolzano",
            "PINEROLO - piazza Cavour",
            "SAUZE DI CESANA",
            "SAUZE D'OULX",
            "SAN MARCO",
            "OULX -Scuole",
            "OULX - piazza Garambois",
            "BUSSOLENO",
            "SUSA",
            "GRAVERE",
            "CHIOMONTE",
            "EXILLES",
            "OULX FS"
        ]
    },"""

if '"file": "/root/000285.pdf"' not in content:
    content = content.replace('    {\n        "file": "/root/000267.pdf",', new_line + '\n    {\n        "file": "/root/000267.pdf",')
    with open('/root/extract_all.py', 'w') as f:
        f.write(content)
