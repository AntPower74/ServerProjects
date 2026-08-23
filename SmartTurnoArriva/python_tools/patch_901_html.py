for filepath in ['/root/orari-app/index.html', '/root/shift-app/public/orari/index.html']:
    with open(filepath, 'r') as f:
        html = f.read()
    
    html = html.replace('<option value="303">Linea 303 (Prali - Perosa - Pinerolo - Torino)</option>', '<option value="303">Linea 303 (Prali - Perosa - Pinerolo - Torino)</option>\n                <option value="901">Linea 901 (Bobbio - Torre Pellice - Pinerolo - Torino)</option>')
    
    html = html.replace('data.js?v=17', 'data.js?v=18')
    
    with open(filepath, 'w') as f:
        f.write(html)
