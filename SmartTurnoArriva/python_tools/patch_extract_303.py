import re

with open('/root/extract_all.py', 'r') as f:
    content = f.read()
    
new_line = """    },
    {
        "file": "/root/000303.pdf",
        "linea": "303",
        "stops": [
            "TORINO Autostazione",
            "PINEROLO",
            "PEROSA ARGENTINA arrivo",
            "PEROSA ARGENTINA part.",
            "POMARETTO OSPEDALE",
            "POMARETTO P.LAUSA",
            "POMARETTO P. LAUSA",
            "CHIOTTI",
            "TROSSIERI",
            "PERRERO",
            "PONTE RABBIOSO",
            "POMEYFRE",
            "CROSETTO MIN. GIANNA",
            "RODORETTO BIVIO",
            "VILLA DI PRALI",
            "PRALI GHIGO",
            "SEGGIOVIE"
        ]
    },"""

if '"file": "/root/000303.pdf"' not in content:
    content = content.replace('    {\n        "file": "/root/000267.pdf",', new_line + '\n    {\n        "file": "/root/000267.pdf",')
    with open('/root/extract_all.py', 'w') as f:
        f.write(content)
