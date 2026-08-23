for filepath in ['/root/orari-app/index.html', '/root/shift-app/public/orari/index.html']:
    with open(filepath, 'r') as f:
        html = f.read()
    
    html = html.replace('<option value="274">Linea 274 (Susa - Avigliana - Torino)</option>', '<option value="274">Linea 274 (Susa - Avigliana - Torino)</option>\n                <option value="285">Linea 285 (Oulx - Sestriere - Pinerolo)</option>')
    
    html = html.replace('data.js?v=19', 'data.js?v=20')
    
    with open(filepath, 'w') as f:
        f.write(html)
