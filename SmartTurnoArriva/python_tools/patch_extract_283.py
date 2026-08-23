import re

with open('/root/extract_all.py', 'r') as f:
    content = f.read()
    
new_line = """    },
    {
        "file": "/root/000283.pdf",
        "linea": "283",
        "stops": [
            "CANTALUPA",
            "FROSSASCO Bivio",
            "ROLETTO",
            "FRAZIONE RONCAGLIA",
            "PINEROLO - via Martiri XXI",
            "PINEROLO Ist. Immacolata",
            "PINEROLO - movicentro",
            "PINEROLO - piazza Cavour"
        ]
    },"""

if '"file": "/root/000283.pdf"' not in content:
    content = content.replace('    {\n        "file": "/root/000267.pdf",', new_line + '\n    {\n        "file": "/root/000267.pdf",')
    with open('/root/extract_all.py', 'w') as f:
        f.write(content)
