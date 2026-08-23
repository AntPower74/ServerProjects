import re

with open('/root/orari-app/index.html', 'r') as f:
    html = f.read()

# 1. Update .trip-card CSS and add new column CSS
css_old_trip_card = """        .trip-card {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }"""

css_new_trip_card = """        .trip-card {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 1.2rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: row;
            align-items: stretch;
            gap: 1rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .trip-times-col {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            min-width: 60px;
            border-right: 1px solid rgba(255,255,255,0.1);
            padding-right: 1rem;
        }
        .time-block { text-align: center; }
        .time-val { display: block; font-size: 1.3rem; font-weight: 800; color: #f0f0f2; }
        .next-bus .time-val { color: #10b981; }
        .time-label { display: block; font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom:2px; }
        .time-duration { font-size: 0.8rem; color: #a855f7; font-weight: 600; display: flex; flex-direction: column; align-items: center; margin: 0.5rem 0; }
        .trip-info-col { flex: 1; display: flex; flex-direction: column; justify-content: center; }"""

html = html.replace(css_old_trip_card, css_new_trip_card)

# 2. Update the JS rendering logic in BOTH standard search and global search.
# Wait, let's find the standard search logic first.
# Standard search is in `searchTrips()`
standard_old = """                <div class="trip-card ${isNext ? 'next-bus' : ''}">
                    <div class="trip-header">
                        <div class="trip-time">
                            <span style="font-size: 0.8rem; color:#9e9ea6; font-weight:normal;">Partenza</span><br>
                            ${trip.fromTime}
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
                        ${trip.toTime}
                    </div>
                </div>"""

standard_new = """                <div class="trip-card ${isNext ? 'next-bus' : ''}">
                    <div class="trip-times-col">
                        <div class="time-block">
                            <span class="time-label">Part.</span>
                            <span class="time-val">${trip.fromTime}</span>
                        </div>
                        <div class="time-duration">
                            <span>&darr;</span>
                            <span>${formatMinutes(totalMins)}</span>
                        </div>
                        <div class="time-block">
                            <span class="time-val">${trip.toTime}</span>
                            <span class="time-label">Arr.</span>
                        </div>
                    </div>
                    <div class="trip-info-col">
                        <div class="trip-badges" style="margin-bottom: 8px;">
                            ${giorni ? `<span class="giorni-badge">${giorni}</span>` : ''}
                            ${note ? `<span class="note-badge">${note}</span>` : ''}
                        </div>
                        <div style="font-size: 0.9rem; color: #e4e4e7;">
                            <strong>Corsa Diretta</strong><br>
                            <span style="color:#94a3b8; font-size:0.8rem;">Linea ${trip._linea || document.getElementById('lineaSelect').value}</span>
                        </div>
                    </div>
                </div>"""

html = html.replace(standard_old, standard_new)


# 3. Update the global search logic (Direct)
global_direct_old = """                <div class="trip-card ${isNext ? 'next-bus' : ''}">
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
                </div>"""

global_direct_new = """                <div class="trip-card ${isNext ? 'next-bus' : ''}">
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
                    </div>
                    <div class="trip-info-col">
                        <div class="trip-badges" style="margin-bottom: 8px;">
                            ${giorni ? `<span class="giorni-badge">${giorni}</span>` : ''}
                            ${note ? `<span class="note-badge">${note}</span>` : ''}
                        </div>
                        <div style="font-size: 0.9rem; color: #e4e4e7;">
                            <strong>Corsa Diretta</strong><br>
                            <span style="color:#94a3b8; font-size:0.8rem;">Linea ${r.trip['_linea']}</span>
                        </div>
                    </div>
                </div>"""
html = html.replace(global_direct_old, global_direct_new)


# 4. Update the global search logic (Interchange)
global_interchange_old = """                <div class="trip-card ${isNext ? 'next-bus' : ''}">
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
                    
                    <div class="timeline">
                        <div class="timeline-step">
                            <div class="timeline-dot dot-start"></div>
                            <div class="timeline-content">
                                <strong>Partenza con:</strong> <span class="badge-linea">Linea ${r.trip1['_linea']}</span>
                            </div>
                        </div>
                        <div class="timeline-step">
                            <div class="timeline-dot dot-change"></div>
                            <div class="timeline-content">
                                <strong>Cambio a:</strong> ${r.interchangeStop}<br>
                                <span style="color:#9e9ea6; font-size:0.8rem; display:block; margin-top:3px; background:rgba(0,0,0,0.2); padding:4px 6px; border-radius:4px;">
                                    Arrivo: <b>${formatTime(r.t1Arrival)}</b> &bull; Ripartenza: <b>${formatTime(r.t2Dep)}</b><br>
                                    <span style="color:#3b82f6;">&#9202; Attesa: ${formatMinutes(r.t2Dep - r.t1Arrival)}</span>
                                </span>
                            </div>
                        </div>
                        <div class="timeline-step">
                            <div class="timeline-dot dot-end"></div>
                            <div class="timeline-content">
                                <strong>Prosegui con:</strong> <span class="badge-linea">Linea ${r.trip2['_linea']}</span>
                            </div>
                        </div>
                    </div>
                </div>"""

global_interchange_new = """                <div class="trip-card ${isNext ? 'next-bus' : ''}">
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
                    </div>
                    <div class="trip-info-col">
                        <div class="trip-badges" style="margin-bottom: 8px;">
                            <span class="interchange-badge" style="margin-left:0;">1 CAMBIO</span>
                        </div>
                        <div class="timeline" style="margin-top:0; padding-top:5px; border-top:none;">
                            <div class="timeline-step">
                                <div class="timeline-dot dot-start"></div>
                                <div class="timeline-content">
                                    <strong>Partenza:</strong> <span class="badge-linea">L. ${r.trip1['_linea']}</span>
                                </div>
                            </div>
                            <div class="timeline-step">
                                <div class="timeline-dot dot-change"></div>
                                <div class="timeline-content">
                                    <strong>Cambio:</strong> ${r.interchangeStop}<br>
                                    <span style="color:#9e9ea6; font-size:0.75rem; display:block; margin-top:3px; background:rgba(0,0,0,0.2); padding:4px 6px; border-radius:4px;">
                                        Arr: <b>${formatTime(r.t1Arrival)}</b> | Rip: <b>${formatTime(r.t2Dep)}</b><br>
                                        <span style="color:#3b82f6;">&#9202; Attesa: ${formatMinutes(r.t2Dep - r.t1Arrival)}</span>
                                    </span>
                                </div>
                            </div>
                            <div class="timeline-step">
                                <div class="timeline-dot dot-end"></div>
                                <div class="timeline-content">
                                    <strong>Arrivo:</strong> <span class="badge-linea">L. ${r.trip2['_linea']}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>"""
html = html.replace(global_interchange_old, global_interchange_new)


with open('/root/orari-app/index.html', 'w') as f:
    f.write(html)
