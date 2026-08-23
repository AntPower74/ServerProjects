import re

with open('/root/orari-app/index.html', 'r') as f:
    html = f.read()

# 1. CSS
css_addition = """
        .timeline { margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); position: relative; padding-left: 10px; }
        .timeline::before { content: ''; position: absolute; left: 14px; top: 25px; bottom: 25px; width: 2px; background: rgba(255,255,255,0.1); }
        .timeline-step { position: relative; padding-left: 20px; margin-bottom: 12px; }
        .timeline-step:last-child { margin-bottom: 0; }
        .timeline-dot { position: absolute; left: 0; top: 4px; width: 10px; height: 10px; border-radius: 50%; z-index: 1; border: 2px solid #18181b; }
        .dot-start { background: #4ade80; }
        .dot-change { background: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.3); }
        .dot-end { background: #f87171; }
        .timeline-content { font-size: 0.85rem; color: #e4e4e7; line-height: 1.4; }
        .badge-linea { background: rgba(255,255,255,0.1); color: white; padding: 2px 5px; border-radius: 4px; font-size: 0.75rem; margin-left: 4px; border: 1px solid rgba(255,255,255,0.2); }
"""
html = html.replace('</style>', css_addition + '</style>')

# 2. JS HTML replacement for interchange
old_interchange = """                    <div class="interchange-details">
                        <b>1.</b> Prendi Linea ${r.trip1['_linea']} fino a <b>${r.interchangeStop}</b> (Arrivo ${formatTime(r.t1Arrival)})<br>
                        <i>Attesa: ${formatMinutes(r.t2Dep - r.t1Arrival)}</i><br>
                        <b>2.</b> Da <b>${r.interchangeStop}</b> prendi Linea ${r.trip2['_linea']} alle ${formatTime(r.t2Dep)}
                    </div>"""

new_interchange = """                    <div class="timeline">
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
                    </div>"""

html = html.replace(old_interchange, new_interchange)

# Ensure cache bypass is incremented
html = html.replace('data.js?v=2', 'data.js?v=3')

with open('/root/orari-app/index.html', 'w') as f:
    f.write(html)
