import re

for filepath in ['/root/orari-app/index.html', '/root/shift-app/public/orari/index.html']:
    with open(filepath, 'r') as f:
        html = f.read()

    # 1. Store global results in renderResults
    if "window.currentRenderedResults = results;" not in html:
        html = html.replace('function renderResults(results, dateVal, container, isGlobal) {', 'function renderResults(results, dateVal, container, isGlobal) {\n        window.currentRenderedResults = results;')

    # 2. Add onclick to trip-card
    html = html.replace('<div class="trip-card ${isNext ? \'next-bus\' : \'\'}">', '<div class="trip-card ${isNext ? \'next-bus\' : \'\'}" onclick="showTripDetails(${i})" style="cursor:pointer;" title="Clicca per visualizzare tutte le fermate">')

    # 3. Add modal HTML and JS before </body>
    modal_code = """
<div id="tripModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:1000; padding:20px; box-sizing:border-box; flex-direction:column; justify-content:center; align-items:center;">
   <div style="background:var(--bg-card); border:1px solid var(--border-color); border-radius:12px; width:100%; max-width:500px; max-height:85vh; overflow-y:auto; padding:20px; box-shadow:0 10px 25px rgba(0,0,0,0.5); position:relative;">
      <button onclick="closeTripModal()" style="position:absolute; top:10px; right:15px; background:transparent; border:none; color:var(--text-muted); font-size:2rem; cursor:pointer; line-height:1;">&times;</button>
      <h3 style="margin-top:0; color:var(--text-main); margin-bottom:20px; padding-right:30px;">Dettaglio Fermate</h3>
      <div id="tripModalContent"></div>
   </div>
</div>

<script>
function showTripDetails(index) {
    if (!window.currentRenderedResults || !window.currentRenderedResults[index]) return;
    const r = window.currentRenderedResults[index];
    const content = document.getElementById('tripModalContent');
    let html = '';
    
    function renderStops(trip) {
        let stops = [];
        Object.keys(trip).forEach(k => {
            if (!k.startsWith('_')) {
                let mins = parseTime(trip[k]);
                if (mins > 0) stops.push({name: k, time: mins, originalTime: trip[k]});
            }
        });
        stops.sort((a,b) => {
            let ta = a.time, tb = b.time;
            if (ta < 4*60 && tb > 20*60) ta += 24*60;
            if (tb < 4*60 && ta > 20*60) tb += 24*60;
            return ta - tb;
        });
        
        let stopsHtml = '<div style="position:relative; padding-left:15px; margin-bottom:10px;">';
        stopsHtml += '<div style="position:absolute; left:4px; top:10px; bottom:10px; width:2px; background:rgba(255,255,255,0.1);"></div>';
        
        stops.forEach((s, idx) => {
            let color = '#94a3b8';
            let fw = 'normal';
            if (idx === 0) { color = '#4ade80'; fw = 'bold'; }
            if (idx === stops.length - 1) { color = '#f87171'; fw = 'bold'; }
            stopsHtml += `<div style="position:relative; padding-bottom:15px;">
                <div style="position:absolute; left:-15px; top:4px; width:10px; height:10px; border-radius:50%; background:${color}; border:2px solid var(--bg-card);"></div>
                <div style="display:flex; justify-content:space-between; font-size:0.9rem; color:var(--text-light); font-weight:${fw}; line-height:1.2;">
                    <span style="flex:1; padding-right:15px;">${s.name}</span>
                    <span style="color:${color}; white-space:nowrap;">${s.originalTime}</span>
                </div>
            </div>`;
        });
        stopsHtml += '</div>';
        return stopsHtml;
    }
    
    if (r.type === 'interchange') {
        html += `<h4 style="color:#3b82f6; margin-bottom:10px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:5px;">Linea ${r.trip1['_linea']}</h4>`;
        html += renderStops(r.trip1);
        
        let waitTimeHtml = '';
        if (r.t2Dep && r.t1Arrival) {
            let w = r.t2Dep - r.t1Arrival;
            let wh = Math.floor(w/60);
            let wm = w%60;
            waitTimeHtml = wh > 0 ? `${wh}h ${wm}m` : `${wm}m`;
        }
        
        html += `<div style="background:rgba(59,130,246,0.15); border-left:4px solid #3b82f6; padding:12px; margin:20px 0; border-radius:6px; font-size:0.9rem; color:#bfdbfe;">
            <b style="color:#60a5fa;">&#8644; Cambio a:</b> ${r.interchangeStop}<br>
            <span style="margin-top:5px; display:inline-block;">&#9202; Tempo di attesa: <b>${waitTimeHtml}</b></span>
        </div>`;
        html += `<h4 style="color:#3b82f6; margin-bottom:10px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:5px;">Linea ${r.trip2['_linea']}</h4>`;
        html += renderStops(r.trip2);
    } else {
        const lineaInfo = r.trip ? r.trip['_linea'] : 'Sconosciuta';
        html += `<h4 style="color:var(--accent-cyan); margin-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:5px;">Linea ${lineaInfo}</h4>`;
        html += renderStops(r.trip ? r.trip : r);
    }
    
    content.innerHTML = html;
    const modal = document.getElementById('tripModal');
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeTripModal() {
    document.getElementById('tripModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

document.getElementById('tripModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeTripModal();
    }
});
</script>
</body>"""
    if "tripModal" not in html:
        html = html.replace('</body>', modal_code)
        
    html = html.replace('data.js?v=12', 'data.js?v=13')
        
    with open(filepath, 'w') as f:
        f.write(html)
