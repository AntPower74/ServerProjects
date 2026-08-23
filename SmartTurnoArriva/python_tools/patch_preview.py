import re

for filepath in ['/root/orari-app/index.html', '/root/shift-app/public/orari/index.html']:
    with open(filepath, 'r') as f:
        html = f.read()
        
    search_trips_old = """        if (!fromStop || !toStop) {
            container.innerHTML = `<p style="text-align:center; color:#9e9ea6;">Seleziona sia la partenza che l'arrivo.</p>`;
            return;
        }"""
        
    search_trips_new = """        if (!fromStop || !toStop) {
            const targetDate = new Date(dateVal);
            const selectedLinea = document.getElementById('lineaSelect').value;
            let lineTrips = tripsData.filter(t => t._linea === selectedLinea && isCorsaValida(t, targetDate));
            
            if (lineTrips.length === 0) {
                container.innerHTML = '<p style="text-align:center; color:#9e9ea6; line-height:1.5;">Nessuna corsa prevista per questa linea nella data selezionata.</p>';
                return;
            }
            
            let displayTrips = [];
            lineTrips.forEach(trip => {
                let validStops = [];
                Object.keys(trip).forEach(k => {
                    if (!k.startsWith('_')) {
                        let mins = parseTime(trip[k]);
                        if (mins > 0) validStops.push({stop: k, time: mins});
                    }
                });
                
                validStops.sort((a,b) => {
                    let ta = a.time, tb = b.time;
                    if (ta < 4*60 && tb > 20*60) ta += 24*60;
                    if (tb < 4*60 && ta > 20*60) tb += 24*60;
                    return ta - tb;
                });
                
                if (validStops.length >= 2) {
                    let first = validStops[0];
                    let last = validStops[validStops.length - 1];
                    let time1 = first.time;
                    let time2 = last.time;
                    if (time2 < time1 && time1 > 20*60 && time2 < 4*60) time2 += 24*60;
                    
                    displayTrips.push({
                        trip: trip,
                        time1: time1,
                        time2: time2,
                        fromName: first.stop,
                        toName: last.stop,
                        type: 'preview'
                    });
                }
            });
            
            displayTrips.sort((a, b) => a.time1 - b.time1);
            
            const uniqueTrips = [];
            const seen = new Set();
            displayTrips.forEach(t => {
                const key = t.time1 + '-' + t.time2 + '-' + t.fromName;
                if (!seen.has(key)) {
                    seen.add(key);
                    uniqueTrips.push(t);
                }
            });
            displayTrips = uniqueTrips;
            
            const now = new Date();
            const currentMins = now.getHours() * 60 + now.getMinutes();
            const todayStr = now.toISOString().split('T')[0];
            
            if (dateVal === todayStr) {
                let startIndex = displayTrips.findIndex(t => t.time1 > currentMins);
                if (startIndex === -1) startIndex = Math.max(0, displayTrips.length - 10);
                let endIndex = Math.min(displayTrips.length, startIndex + 10);
                if (endIndex - startIndex < 10) startIndex = Math.max(0, endIndex - 10);
                displayTrips = displayTrips.slice(startIndex, endIndex);
            } else {
                displayTrips = displayTrips.slice(0, 10);
            }
            
            container.innerHTML = '<div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 10px; border-radius: 8px; margin-bottom: 1rem; text-align: center; color: #93c5fd; font-size: 0.9rem;">Mostrando le prossime 10 corse dell\\'intera linea.<br><b>Seleziona partenza e arrivo per vedere tutte le corse.</b></div>';
            
            let tempContainer = document.createElement('div');
            renderResults(displayTrips, dateVal, tempContainer, false);
            container.innerHTML += tempContainer.innerHTML;
            return;
        }"""
        
    html = html.replace(search_trips_old, search_trips_new)
    
    # Update renderResults
    render_old = """            if (!isGlobal || r.type === 'direct') {
                let t = isGlobal ? r.trip : r.trip;
                const giorni = mapGiorni(t['_giorni']);
                const note = t['_note'] || t['_stagionalita'];
                const isExpress = t['_note'] && t['_note'].includes('EXPRESS');
                const tipoCorsa = isExpress ? 'Corsa Express' : 'Corsa Stradale';
                
                htmlStr += `
                <div class="trip-card ${isNext ? 'next-bus' : ''}">
                    ${leftCol}
                    <div class="trip-info-col">
                        <div class="trip-badges" style="margin-bottom: 8px;">
                            ${giorni ? `<span class="giorni-badge" style="background: rgba(168, 85, 247, 0.15); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.3); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">${giorni}</span>` : ''}
                            ${note && !isExpress ? `<span class="note-badge" style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; margin-left:5px;">${note}</span>` : ''}
                            ${isExpress ? `<span class="note-badge" style="background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; margin-left:5px;">EXPRESS</span>` : ''}
                        </div>
                        <div style="font-size: 0.95rem; color: #e4e4e7;">
                            <strong>${tipoCorsa}</strong><br>
                            <span style="color:#94a3b8; font-size:0.85rem;">Linea ${t['_linea']}</span>
                        </div>
                    </div>
                </div>`;"""
                
    render_new = """            if (!isGlobal || r.type === 'direct' || r.type === 'preview') {
                let t = r.trip;
                const giorni = mapGiorni(t['_giorni']);
                const note = t['_note'] || t['_stagionalita'];
                const isExpress = t['_note'] && t['_note'].includes('EXPRESS');
                const tipoCorsa = isExpress ? 'Corsa Express' : 'Corsa Stradale';
                
                let extraHtml = '';
                if (r.type === 'preview') {
                    extraHtml = `<div style="margin-top: 6px; font-size: 0.75rem; color: #cbd5e1; background: rgba(255,255,255,0.05); padding: 6px; border-radius: 6px;">
                        <span style="color:#a855f7;">Da:</span> <b>${r.fromName}</b><br>
                        <span style="color:#10b981;">A:</span> <b>${r.toName}</b>
                    </div>`;
                }
                
                htmlStr += `
                <div class="trip-card ${isNext ? 'next-bus' : ''}">
                    ${leftCol}
                    <div class="trip-info-col">
                        <div class="trip-badges" style="margin-bottom: 8px;">
                            ${giorni ? `<span class="giorni-badge" style="background: rgba(168, 85, 247, 0.15); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.3); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">${giorni}</span>` : ''}
                            ${note && !isExpress ? `<span class="note-badge" style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; margin-left:5px;">${note}</span>` : ''}
                            ${isExpress ? `<span class="note-badge" style="background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; margin-left:5px;">EXPRESS</span>` : ''}
                        </div>
                        <div style="font-size: 0.95rem; color: #e4e4e7;">
                            <strong>${tipoCorsa}</strong><br>
                            <span style="color:#94a3b8; font-size:0.85rem;">Linea ${t['_linea']}</span>
                            ${extraHtml}
                        </div>
                    </div>
                </div>`;"""
                
    html = html.replace(render_old, render_new)
    
    html = html.replace('data.js?v=10', 'data.js?v=11')
    
    with open(filepath, 'w') as f:
        f.write(html)
