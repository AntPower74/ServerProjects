import re

with open('/root/extract_all.py', 'r') as f:
    content = f.read()
    
new_line = """    },
    {
        "file": "/root/000901.pdf",
        "linea": "901",
        "stops": [
            "BOBBIO PELLICE",
            "VILLAR PELLICE",
            "CHABRIOLS",
            "SEGG. VANDALINO",
            "S. MARGHERITA",
            "LOMBARIDINI/VOLTA",
            "TORRE PELLICE",
            "LUSERNA - piazza Partigiani",
            "LUSERNA - cimitero",
            "PONTE BIBIANA/FS",
            "BIBIANA",
            "BRICHERASIO",
            "CAPPELLA MORERI",
            "SAN SECONDO CANTINE",
            "SAN SECONDO BIVIO BIMA",
            "PINEROLO - piazza Cavour",
            "PINEROLO Movicentro",
            "PINEROLO - Centro Studi",
            "PINEROLO - staz. Olimpica",
            "PINEROLO - Ist. Immacolata",
            "AIRASCA - Stazione FS",
            "NONE - via Roma",
            "CANDIOLO - Stazione FS",
            "NICHELINO - Stazione FS",
            "SANGONE - Stazione FS",
            "TORINO - stazione Lingotto FS",
            "TO-c.so V.Eman. II-Porta Nuova",
            "TORINO - Autostazione c.so Bolzano",
            "TO - Autostazione c.so Bolzano",
            "PISCINA - v. Umberto I ang. V. Airasca",
            "PISCINA - v.Airasca ang. V. Umberto I"
        ]
    },"""

if '"file": "/root/000901.pdf"' not in content:
    content = content.replace('    {\n        "file": "/root/000267.pdf",', new_line + '\n    {\n        "file": "/root/000267.pdf",')
    with open('/root/extract_all.py', 'w') as f:
        f.write(content)
