import re

with open('/root/orari-app/index.html', 'r') as f:
    html = f.read()

# Fix CSS for trip-card completely
css_target = re.compile(r'\.trip-card \{.*?\n        \.trip-card\.next-bus', re.DOTALL)
new_css = """        .trip-card {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 1.2rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: row;
            align-items: stretch;
            gap: 1.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .trip-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
            background: rgba(30, 41, 59, 0.8);
        }
        .trip-times-col {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            min-width: 65px;
            border-right: 1px dashed rgba(255,255,255,0.1);
            padding-right: 1.5rem;
        }
        .time-block { text-align: center; }
        .time-val { display: block; font-size: 1.4rem; font-weight: 800; color: #f0f0f2; }
        .next-bus .time-val { color: #10b981; }
        .time-label { display: block; font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
        .time-duration { font-size: 0.85rem; color: #a855f7; font-weight: 600; display: flex; flex-direction: column; align-items: center; margin: 0.75rem 0; }
        .trip-info-col { flex: 1; display: flex; flex-direction: column; justify-content: center; }
        .trip-card.next-bus"""

html = css_target.sub(new_css, html)

# Now completely replace the JS block
js_start = html.find('<script>\n    // Set default date to today')
if js_start == -1:
    print("Could not find JS start")
    exit(1)

js_end = html.find('</body>', js_start)

new_js = """<script>
    // Set default date to today
    document.getElementById('dateSelect').valueAsDate = new Date();

    let searchMode = 'linea';
    function setMode(mode) {
        searchMode = mode;
        document.getElementById('tab-linea').className = mode === 'linea' ? 'tab active' : 'tab';
        document.getElementById('tab-globale').className = mode === 'globale' ? 'tab active' : 'tab';
        document.getElementById('lineaContainer').style.display = mode === 'linea' ? 'block' : 'none';
        updateStops();
    }

    function updateStops() {
        const linea = document.getElementById('lineaSelect').value;
        const allStops = new Set();
        
        tripsData.forEach(t => {
            if (searchMode === 'globale' || t._linea === linea) {
                Object.keys(t).forEach(k => {
                    if(!k.startsWith('_')) allStops.add(k);
                });
            }
        });
        
        const sortedStops = Array.from(allStops).sort();
        
        const fromSelect = document.getElementById('fromSelect');
        const toSelect = document.getElementById('toSelect');
        
        fromSelect.innerHTML = '<option value="">-- Seleziona Partenza --</option>';
        toSelect.innerHTML = '<option value="">-- Seleziona Arrivo --</option>';
        
        sortedStops.forEach(stop => {
            fromSelect.innerHTML += `<option value="${stop}">${stop}</option>`;
            toSelect.innerHTML += `<option value="${stop}">${stop}</option>`;
        });
        
        document.getElementById('results').innerHTML = '';
    }

    window.onload = function() {
        updateStops();
        updateClock();
        setInterval(updateClock, 1000);
        setInterval(() => searchTrips(true), 60000);
    };

    function updateClock() {
        const now = new Date();
        document.getElementById('clock-time').textContent = now.toLocaleTimeString('it-IT', { hour12: false });
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        let dateStr = now.toLocaleDateString('it-IT', options);
        document.getElementById('clock-date').textContent = dateStr.charAt(0).toUpperCase() + dateStr.slice(1);
    }

    function parseTime(tStr) {
        if (!tStr || tStr === 'D' || tStr === 'I' || tStr === 'R') return 0;
        let parts = tStr.split(/[:.]/);
        if (parts.length < 2) return 0;
        let h = parseInt(parts[0], 10);
        let m = parseInt(parts[1], 10);
        if (isNaN(h) || isNaN(m)) return 0;
        return h * 60 + m;
    }

    function getEasterDate(year) {
        const f = Math.floor, G = year % 19, C = f(year / 100),
              H = (C - f(C / 4) - f((8 * C + 13) / 25) + 19 * G + 15) % 30,
              I = H - f(H / 28) * (1 - f(29 / (H + 1)) * f((21 - G) / 11)),
              J = (year + f(year / 4) + I + 2 - C + f(C / 4)) % 7,
              L = I - J, month = 3 + f((L + 40) / 44), day = L + 28 - 31 * f(month / 4);
        return new Date(year, month - 1, day);
    }

    function getItalianHolidays(year) {
        const easter = getEasterDate(year);
        const easterMonday = new Date(year, easter.getMonth(), easter.getDate() + 1);
        
        return [
            `01-01-${year}`, `06-01-${year}`, `25-04-${year}`, `01-05-${year}`, `02-06-${year}`,
            `15-08-${year}`, `01-11-${year}`, `08-12-${year}`, `25-12-${year}`, `26-12-${year}`,
            `${('0' + easter.getDate()).slice(-2)}-${('0' + (easter.getMonth()+1)).slice(-2)}-${year}`,
            `${('0' + easterMonday.getDate()).slice(-2)}-${('0' + (easterMonday.getMonth()+1)).slice(-2)}-${year}`
        ];
    }

    function mapGiorni(giorniStr) {
        if (!giorniStr) return "";
        if (giorniStr === 'GG') return "Giornaliero";
        if (giorniStr === '12345') return "Lun-Ven";
        if (giorniStr === '123456') return "Lun-Sab";
        if (giorniStr === '6') return "Sabato";
        if (giorniStr === '78' || giorniStr === '8') return "Dom / Festivi";
        return giorniStr;
    }

    function isCorsaValida(trip, targetDate) {
        const dayOfWeek = targetDate.getDay(); 
        const year = targetDate.getFullYear();
        const holidays = getItalianHolidays(year);
        const dateStr = `${('0' + targetDate.getDate()).slice(-2)}-${('0' + (targetDate.getMonth()+1)).slice(-2)}-${year}`;
        const isHoliday = holidays.includes(dateStr) || dayOfWeek === 0;
        
        const note = trip['_note'] || '';
        const stagionalita = trip['_stagionalita'] || '';
        const giorni = trip['_giorni'] || '';
        
        const isAugustBreak = (targetDate.getMonth() === 7 && targetDate.getDate() >= 4 && targetDate.getDate() <= 31);
        if (note.includes('04/08') && !isAugustBreak) return false;
        
        if (note.includes('Scol') && isAugustBreak) return false; 
        if (note.includes('A') && isAugustBreak) return false; 
        if (note.includes('F') && !isAugustBreak) return false;
        if (note.includes('J') && dateStr.startsWith('25-12')) return false;

        if (stagionalita === 'FEST' && !isHoliday) return false;
        if (stagionalita === 'FER' && isHoliday) return false;
        
        if (giorni) {
            if (giorni === 'GG') {
            } else if (giorni.match(/^[1-8]+$/)) {
                const weekStr = dayOfWeek === 0 ? '7' : dayOfWeek.toString();
                let isValidDay = false;
                
                if (giorni.includes(weekStr)) {
                    isValidDay = true;
                    if (isHoliday && !giorni.includes('8') && stagionalita !== 'FEST') {
                        isValidDay = false;
                    }
                }
                
                if (isHoliday && giorni.includes('8')) {
                    isValidDay = true;
                }
                
                if (!isValidDay) return false;
            }
        }
        
        return true;
    }

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
        const selectedLinea = document.getElementById('lineaSelect').value;
        
        let validTrips = [];
        tripsData.forEach(trip => {
            if (trip._linea === selectedLinea && trip[fromStop] && trip[toStop]) {
                if (!isCorsaValida(trip, targetDate)) return;

                let time1 = parseTime(trip[fromStop]);
                let time2 = parseTime(trip[toStop]);
                
                if (time1 > 0 && time2 > 0) {
                    if (time2 < time1 && time1 > 20*60 && time2 < 4*60) time2 += 24*60; 
                    if (time1 < time2) {
                        validTrips.push({
                            trip: trip,
                            time1: time1,
                            time2: time2
                        });
                    }
                }
            }
        });
        
        validTrips.sort((a, b) => a.time1 - b.time1);
        
        const uniqueTrips = [];
        const seen = new Set();
        validTrips.forEach(t => {
            const key = t.time1 + '-' + t.time2;
            if (!seen.has(key)) {
                seen.add(key);
                uniqueTrips.push(t);
            }
        });
        validTrips = uniqueTrips;
        
        if (validTrips.length === 0) {
            container.innerHTML = '<p style="text-align:center; color:#9e9ea6; line-height:1.5;">Nessuna corsa trovata per questa tratta <b>nella data selezionata</b>.<br/><small>Controlla se si tratta di un giorno festivo, di un mese con servizio ridotto, o se le fermate sono nella direzione sbagliata.</small></p>';
            return;
        }
        
        renderResults(validTrips, dateVal, container, false);
    }

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
        
        startTrips.forEach(t1 => {
            if (t1[toStop] && parseTime(t1[toStop]) > 0) {
                let time1 = parseTime(t1[fromStop]);
                let time2 = parseTime(t1[toStop]);
                if (time2 < time1 && time1 > 20*60 && time2 < 4*60) time2 += 24*60;
                if (time1 < time2) {
                    allResults.push({ type: 'direct', time1, time2, trip: t1 });
                }
            }
        });
        
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
                            if (!t2[stop]) return;
                            let t2Dep = parseTime(t2[stop]);
                            if (t2Dep > 0) {
                                if (t2Dep < t1Arrival && t1Arrival > 20*60 && t2Dep < 4*60) t2Dep += 24*60;
                                let waitTime = t2Dep - t1Arrival;
                                if (waitTime >= 0 && waitTime <= 120) {
                                    let time2 = parseTime(t2[toStop]);
                                    if (time2 > 0) {
                                        if (time2 < t2Dep && t2Dep > 20*60 && time2 < 4*60) time2 += 24*60;
                                        if (time2 > t2Dep) {
                                            allResults.push({
                                                type: 'interchange', time1, time2,
                                                t1Arrival, t2Dep, trip1: t1, trip2: t2, interchangeStop: stop
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
            container.innerHTML = '<p style="text-align:center; color:#9e9ea6; line-height:1.5;">Nessuna soluzione trovata.<br/><small>Prova a cambiare data o fermate.</small></p>';
            return;
        }
        
        renderResults(allResults, dateVal, container, true);
    }

    function renderResults(results, dateVal, container, isGlobal) {
        const now = new Date();
        const todayStr = now.toISOString().split('T')[0];
        const isToday = (dateVal === todayStr);
        const currentMins = now.getHours() * 60 + now.getMinutes();
        let nextBusFound = false;
        
        let htmlStr = '';
        results.forEach(r => {
            let isNext = false;
            if (isToday && !nextBusFound && r.time1 > currentMins) {
                isNext = true;
                nextBusFound = true;
                htmlStr += '<div class="next-bus-label" style="text-align:center; color:#10b981; font-weight:bold; margin:10px 0;">PROSSIMA CORSA O COMBINAZIONE &darr;</div>';
            }
            
            const totalMins = r.time2 - r.time1;
            
            // Layout common left column
            let leftCol = `
                <div class="trip-times-col">
                    <div class="time-block">
                        <span class="time-label">Part.</span>
                        <span class="time-val">${formatTime(r.time1)}</span>
                    </div>
                    <div class="time-duration">
                        <span>&darr;</span>
                        <span>${formatMinutes(totalMins)}</span>
                    </div>
                    <div class="time-block">
                        <span class="time-val">${formatTime(r.time2)}</span>
                        <span class="time-label">Arr.</span>
                    </div>
                </div>`;
                
            if (!isGlobal || r.type === 'direct') {
                let t = isGlobal ? r.trip : r.trip;
                const giorni = mapGiorni(t['_giorni']);
                const note = t['_note'] || t['_stagionalita'];
                
                htmlStr += `
                <div class="trip-card ${isNext ? 'next-bus' : ''}">
                    ${leftCol}
                    <div class="trip-info-col">
                        <div class="trip-badges" style="margin-bottom: 8px;">
                            ${giorni ? `<span class="giorni-badge" style="background: rgba(168, 85, 247, 0.15); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.3); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">${giorni}</span>` : ''}
                            ${note ? `<span class="note-badge" style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; margin-left:5px;">${note}</span>` : ''}
                        </div>
                        <div style="font-size: 0.95rem; color: #e4e4e7;">
                            <strong>Corsa Diretta</strong><br>
                            <span style="color:#94a3b8; font-size:0.85rem;">Linea ${t['_linea']}</span>
                        </div>
                    </div>
                </div>`;
            } else {
                htmlStr += `
                <div class="trip-card ${isNext ? 'next-bus' : ''}">
                    ${leftCol}
                    <div class="trip-info-col">
                        <div class="trip-badges" style="margin-bottom: 8px;">
                            <span class="interchange-badge" style="background: #3b82f6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight:bold;">1 CAMBIO</span>
                        </div>
                        <div class="timeline" style="position:relative; padding-left:10px; margin-top:5px;">
                            <div style="position:absolute; left:14px; top:10px; bottom:10px; width:2px; background:rgba(255,255,255,0.1);"></div>
                            <div class="timeline-step" style="position:relative; padding-left:20px; margin-bottom:12px;">
                                <div class="timeline-dot dot-start" style="position:absolute; left:0; top:4px; width:10px; height:10px; border-radius:50%; background:#4ade80; border:2px solid #18181b;"></div>
                                <div class="timeline-content" style="font-size:0.85rem; color:#e4e4e7;">
                                    <strong>Partenza:</strong> <span class="badge-linea" style="background:rgba(255,255,255,0.1); padding:2px 5px; border-radius:4px; font-size:0.75rem; margin-left:4px;">L. ${r.trip1['_linea']}</span>
                                </div>
                            </div>
                            <div class="timeline-step" style="position:relative; padding-left:20px; margin-bottom:12px;">
                                <div class="timeline-dot dot-change" style="position:absolute; left:0; top:4px; width:10px; height:10px; border-radius:50%; background:#3b82f6; border:2px solid #18181b; box-shadow:0 0 0 2px rgba(59,130,246,0.3);"></div>
                                <div class="timeline-content" style="font-size:0.85rem; color:#e4e4e7;">
                                    <strong>Cambio:</strong> ${r.interchangeStop}<br>
                                    <span style="color:#9e9ea6; font-size:0.75rem; display:block; margin-top:3px; background:rgba(0,0,0,0.2); padding:6px; border-radius:4px;">
                                        Arr: <b style="color:#f0f0f2;">${formatTime(r.t1Arrival)}</b> | Rip: <b style="color:#f0f0f2;">${formatTime(r.t2Dep)}</b><br>
                                        <span style="color:#3b82f6; margin-top:2px; display:inline-block;">&#9202; Attesa: ${formatMinutes(r.t2Dep - r.t1Arrival)}</span>
                                    </span>
                                </div>
                            </div>
                            <div class="timeline-step" style="position:relative; padding-left:20px;">
                                <div class="timeline-dot dot-end" style="position:absolute; left:0; top:4px; width:10px; height:10px; border-radius:50%; background:#f87171; border:2px solid #18181b;"></div>
                                <div class="timeline-content" style="font-size:0.85rem; color:#e4e4e7;">
                                    <strong>Arrivo:</strong> <span class="badge-linea" style="background:rgba(255,255,255,0.1); padding:2px 5px; border-radius:4px; font-size:0.75rem; margin-left:4px;">L. ${r.trip2['_linea']}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`;
            }
        });
        
        container.innerHTML = htmlStr;
    }
</script>\n"""

html = html[:js_start] + new_js + html[js_end:]

# increment v=4 to v=5
html = html.replace('data.js?v=4', 'data.js?v=5')

with open('/root/orari-app/index.html', 'w') as f:
    f.write(html)
