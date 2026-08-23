for filepath in ['/root/orari-app/index.html', '/root/shift-app/public/orari/index.html']:
    with open(filepath, 'r') as f:
        html = f.read()
    
    html = html.replace("results.forEach(r => {", "results.forEach((r, i) => {")
    html = html.replace('data.js?v=13', 'data.js?v=14')
    
    with open(filepath, 'w') as f:
        f.write(html)
