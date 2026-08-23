for filepath in ['/root/orari-app/index.html', '/root/shift-app/public/orari/index.html']:
    with open(filepath, 'r') as f:
        html = f.read()
    
    html = html.replace("document.getElementById('results').innerHTML = '';", "if (searchMode === 'linea') searchTrips(); else document.getElementById('results').innerHTML = '';")
    
    html = html.replace('data.js?v=11', 'data.js?v=12')
    
    with open(filepath, 'w') as f:
        f.write(html)
