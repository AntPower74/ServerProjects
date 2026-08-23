for filepath in ['/root/orari-app/index.html', '/root/shift-app/public/orari/index.html']:
    with open(filepath, 'r') as f:
        html = f.read()
    
    html = html.replace('<option value="268">Linea 268 (Torino - Aeroporto)</option>', '<option value="268">Linea 268 (Torino - Aeroporto)</option>\n                <option value="283">Linea 283 (Cantalupa - Pinerolo)</option>')
    
    html = html.replace('data.js?v=15', 'data.js?v=16')
    
    with open(filepath, 'w') as f:
        f.write(html)
