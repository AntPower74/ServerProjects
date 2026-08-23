for filepath in ['/root/orari-app/index.html', '/root/shift-app/public/orari/index.html']:
    with open(filepath, 'r') as f:
        html = f.read()
    
    html = html.replace('<option value="267">Linea 267 (Torino - Vinovo - Carignano)</option>', '<option value="265">Linea 265 (Torino - Chivasso - Ivrea - Pont)</option>\n                <option value="267">Linea 267 (Torino - Vinovo - Carignano)</option>')
    
    html = html.replace('data.js?v=14', 'data.js?v=15')
    
    with open(filepath, 'w') as f:
        f.write(html)
