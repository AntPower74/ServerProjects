for filepath in ['/root/orari-app/index.html', '/root/shift-app/public/orari/index.html']:
    with open(filepath, 'r') as f:
        html = f.read()
    
    html = html.replace('<option value="283">Linea 283 (Cantalupa - Pinerolo)</option>', '<option value="283">Linea 283 (Cantalupa - Pinerolo)</option>\n                <option value="303">Linea 303 (Prali - Perosa - Pinerolo - Torino)</option>')
    
    html = html.replace('data.js?v=16', 'data.js?v=17')
    
    with open(filepath, 'w') as f:
        f.write(html)
