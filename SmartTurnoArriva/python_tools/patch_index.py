import re

with open('/root/orari-app/index.html', 'r') as f:
    html = f.read()

# 1. CSS
css_addition = """
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab { flex: 1; padding: 10px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #9e9ea6; border-radius: 8px; cursor: pointer; font-weight: 500; transition: all 0.2s; font-family: inherit; font-size: 0.9rem; }
        .tab.active { background: #4ade80; color: #18181b; border-color: #4ade80; }
        .interchange-badge { background: #3b82f6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; margin-left: 8px; font-weight:bold; }
        .interchange-details { font-size: 0.85rem; color: #a1a1aa; margin-top: 8px; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 8px; }
"""
html = html.replace('</style>', css_addition + '</style>')

# 2. HTML Tabs
html_tabs = """
    <div class="tabs">
        <button id="tab-linea" class="tab active" onclick="setMode('linea')">Ricerca per Linea</button>
        <button id="tab-globale" class="tab" onclick="setMode('globale')">Ricerca Globale (Cambi)</button>
    </div>
    <div class="form-group">
        <div id="lineaContainer">
"""
html = html.replace('<div class="form-group">\n        <div>\n            <label style="color:#9e9ea6; font-size:0.9rem; margin-bottom:0.5rem; display:block;">Linea:</label>', html_tabs + '            <label style="color:#9e9ea6; font-size:0.9rem; margin-bottom:0.5rem; display:block;">Linea:</label>')
html = html.replace('</select>\n        </div>\n        <div>', '</select>\n        </div></div>\n        <div>')

# 3. JS setMode & updateStops
js_setMode = """
    let searchMode = 'linea';
    function setMode(mode) {
        searchMode = mode;
        document.getElementById('tab-linea').className = mode === 'linea' ? 'tab active' : 'tab';
        document.getElementById('tab-globale').className = mode === 'globale' ? 'tab active' : 'tab';
        document.getElementById('lineaContainer').style.display = mode === 'linea' ? 'block' : 'none';
        updateStops();
    }

    function updateStops() {
"""
html = html.replace('    function updateStops() {', js_setMode)

html = html.replace('if (t._linea === linea) {', 'if (searchMode === \'globale\' || t._linea === linea) {')

# 4. Global Search logic
js_global = """
    function formatMinutes(mins) {
        const h = Math.floor(mins / 60);
        const m = mins % 60;
        return h > 0 ? `${h}h ${m}m` : `${m}m`;
    }

    function formatTime(mins) {
        let h = Math.floor(mins / 60);
        const m = mins % 60;
        if (h >= 24) h -= 24;
        return `${h}:${m.toString().padStart(2, '0')}`;
    }

    function searchTrips(isAutoUpdate = false) {
        if (searchMode === 'globale') {
            searchGlobalTrips(isAutoUpdate);
            return;
        }
"""
html = html.replace('    function searchTrips(isAutoUpdate = false) {\n', js_global)

global_logic = """
    function searchGlobalTrips(isAutoUpdate = false) {
        const fromStop = document.getElementById('fromSelect').value;
        const toStop = document.getElementById('toSelect').value;
        const dateVal = document.getElementById('dateSelect').value;
        const container = document.getElementById('results');
        
        if (!isAutoUpdate) container.innerHTML = '';
        
        if (!fromStop || !toStop) {
            container.innerHTML = `<p style="text-align:center; color:#9e9ea6;">Seleziona sia la partenza che l'arrivo.</p>`;
            return;
        }
        if (fromStop === toStop) {
            container.innerHTML = '<p style="text-align:center; color:#ef4444;">Partenza e arrivo non possono essere uguali.</p>';
            return;
        }

        const targetDate = new Date(dateVal);
        const validTrips = tripsData.filter(t => isCorsaValida(t, targetDate));
        
        const startTrips = validTrips.filter(t => t[fromStop] && parseTime(t[fromStop]) > 0);
        const endTrips = validTrips.filter(t => t[toStop] && parseTime(t[toStop]) > 0);
        
        let allResults = [];
        
        // 1. Direct trips
        startTrips.forEach(t1 => {
            if (t1[toStop] && parseTime(t1[toStop]) > 0) {
                let time1 = parseTime(t1[fromStop]);
                let time2 = parseTime(t1[toStop]);
                if (time2 < time1 && time1 > 20*60 && time2 < 4*60) time2 += 24*60;
                if (time1 < time2) {
                    allResults.push({
                        type: 'direct',
                        time1: time1,
                        time2: time2,
                        trip: t1
                    });
                }
            }
        });
        
        // 2. Interchanges
        startTrips.forEach(t1 => {
            let time1 = parseTime(t1[fromStop]);
            Object.keys(t1).forEach(stop => {
                if (stop.startsWith('_') || stop === fromStop || stop === toStop) return;
                let t1Arrival = parseTime(t1[stop]);
                if (t1Arrival > 0) {
                    if (t1Arrival < time1 && time1 > 20*60 && t1Arrival < 4*60) t1Arrival += 24*60;
                    if (t1Arrival > time1) {
                        endTrips.forEach(t2 => {
                            if (t1 === t2) return;
                            let t2Dep = parseTime(t2[stop]);
                            if (t2Dep > 0) {
                                if (t2Dep < t1Arrival && t1Arrival > 20*60 && t2Dep < 4*60) t2Dep += 24*60;
                                let waitTime = t2Dep - t1Arrival;
                                if (waitTime >= 0 && waitTime <= 120) { // allow 0-120 mins wait
                                    let time2 = parseTime(t2[toStop]);
                                    if (time2 > 0) {
                                        if (time2 < t2Dep && t2Dep > 20*60 && time2 < 4*60) time2 += 24*60;
                                        if (time2 > t2Dep) {
                                            allResults.push({
                                                type: 'interchange',
                                                time1: time1,
                                                time2: time2,
                                                t1Arrival: t1Arrival,
                                                t2Dep: t2Dep,
                                                trip1: t1,
                                                trip2: t2,
                                                interchangeStop: stop
                                            });
                                        }
                                    }
                                }
                            }
                        });
                    }
                }
            });
        });
        
        allResults.sort((a, b) => a.time1 - b.time1);
        
        // Deduplicate
        const uniqueResults = [];
        const seen = new Set();
        allResults.forEach(r => {
            const key = r.type === 'direct' ? `D-${r.time1}-${r.time2}` : `I-${r.time1}-${r.time2}-${r.interchangeStop}`;
            if (!seen.has(key)) {
                seen.add(key);
                uniqueResults.push(r);
            }
        });
        allResults = uniqueResults;
        
        if (allResults.length === 0) {
            container.innerHTML = '<p style="text-align:center; color:#9e9ea6; line-height:1.5;">Nessuna soluzione trovata (né diretta né con un cambio).<br/><small>Prova a cambiare data o fermate.</small></p>';
            return;
        }
        
        const now = new Date();
        const todayStr = now.toISOString().split('T')[0];
        const isToday = (dateVal === todayStr);
        const currentMins = now.getHours() * 60 + now.getMinutes();
        
        let nextBusFound = false;
        
        allResults.forEach(r => {
            let html = '';
            let isNext = false;
            
            if (isToday && !nextBusFound && r.time1 > currentMins) {
                isNext = true;
                nextBusFound = true;
                html += '<div class="next-bus-label">PROSSIMA CORSA O COMBINAZIONE</div>';
            }
            
            const totalMins = r.time2 - r.time1;
            
            if (r.type === 'direct') {
                const giorni = mapGiorni(r.trip['_giorni']);
                const note = r.trip['_note'] || r.trip['_stagionalita'];
                
                html += `
                <div class="trip-card ${isNext ? 'next-bus' : ''}">
                    <div class="trip-header">
                        <div class="trip-time">
                            <span style="font-size: 0.8rem; color:#9e9ea6; font-weight:normal;">Partenza</span><br>
                            ${formatTime(r.time1)}
                        </div>
                        <div class="trip-badges">
                            ${giorni ? `<span class="badge badge-giorni">${giorni}</span>` : ''}
                            ${note ? `<span class="badge badge-note">${note}</span>` : ''}
                        </div>
                    </div>
                    
                    <div class="trip-duration">
                        <span style="color:#9e9ea6;">&rarr;</span>
                        <span>${formatMinutes(totalMins)}</span>
                    </div>
                    
                    <div class="trip-time" style="text-align: right;">
                        <span style="font-size: 0.8rem; color:#9e9ea6; font-weight:normal;">Arrivo</span><br>
                        ${formatTime(r.time2)}
                    </div>
                </div>`;
            } else {
                html += `
                <div class="trip-card ${isNext ? 'next-bus' : ''}">
                    <div class="trip-header">
                        <div class="trip-time">
                            <span style="font-size: 0.8rem; color:#9e9ea6; font-weight:normal;">Partenza</span><br>
                            ${formatTime(r.time1)}
                        </div>
                        <div class="trip-badges">
                            <span class="interchange-badge">1 CAMBIO</span>
                        </div>
                    </div>
                    
                    <div class="trip-duration">
                        <span style="color:#9e9ea6;">&rarr;</span>
                        <span>${formatMinutes(totalMins)}</span>
                    </div>
                    
                    <div class="trip-time" style="text-align: right;">
                        <span style="font-size: 0.8rem; color:#9e9ea6; font-weight:normal;">Arrivo</span><br>
                        ${formatTime(r.time2)}
                    </div>
                    
                    <div class="interchange-details">
                        <b>1.</b> Prendi Linea ${r.trip1['_linea']} fino a <b>${r.interchangeStop}</b> (Arrivo ${formatTime(r.t1Arrival)})<br>
                        <i>Attesa: ${formatMinutes(r.t2Dep - r.t1Arrival)}</i><br>
                        <b>2.</b> Da <b>${r.interchangeStop}</b> prendi Linea ${r.trip2['_linea']} alle ${formatTime(r.t2Dep)}
                    </div>
                </div>`;
            }
            container.innerHTML += html;
        });
    }
"""

html = html.replace('// Next Bus check (only relevant if selected date is today)', global_logic + '\n        // Next Bus check (only relevant if selected date is today)')

with open('/root/orari-app/index.html', 'w') as f:
    f.write(html)
