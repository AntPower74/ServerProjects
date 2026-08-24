// Inizializzazione PWA & State
let appData = null;
let signalsData = null;
let currentTab = 'tab-pronostico';
let lastConcorsoNum = null;
let currentClientBuild = null;
let lastRenderedJson = '';
let lastSignalsJson = '';

// Registrazione Service Worker senza reload forzato
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW error:', err));
}

// Navigazione a Schede (3 Schede Essenziali)
function switchTab(tabId) {
  currentTab = tabId;
  document.querySelectorAll('.tab-screen').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  
  const target = document.getElementById(tabId);
  if (target) target.classList.add('active');
  
  const navBtn = document.querySelector(`[data-tab="${tabId}"]`);
  if (navBtn) navBtn.classList.add('active');

  if (tabId === 'tab-archivio') {
    caricaArchivioCompleto();
  } else if (tabId === 'tab-laboratorio') {
    fetchSignalsData();
  }
}

// Countdown Timer alla prossima estrazione (ogni 5 minuti)
function updateCountdown() {
  const now = new Date();
  const minutes = now.getMinutes();
  const seconds = now.getSeconds();
  
  const next5Min = (Math.floor(minutes / 5) + 1) * 5;
  let diffSec = (next5Min * 60) - (minutes * 60 + seconds);
  if (diffSec <= 0) diffSec = 300;
  
  const m = Math.floor(diffSec / 60);
  const s = diffSec % 60;
  
  const timerEl = document.getElementById('next-draw-timer');
  if (timerEl) {
    timerEl.textContent = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }

  // Interroga il server allo scoccare esatto dell'estrazione
  if (diffSec === 299 || diffSec === 290) {
    fetchLiveData(true);
    fetchSignalsData();
  }
}
setInterval(updateCountdown, 1000);

// Caricamento Dati Principali con Diffing
async function fetchLiveData(force = false) {
  try {
    const res = await fetch('/api/data?t=' + Date.now());
    const data = await res.json();
    if (data.status === 'ok') {
      currentClientBuild = data.build_version;

      const dataSignature = JSON.stringify({
        c: data.latest_draw ? data.latest_draw.concorso : null,
        best: data.best_spy ? data.best_spy.spy : null
      });

      if (force || dataSignature !== lastRenderedJson) {
        lastRenderedJson = dataSignature;
        if (data.latest_draw && lastConcorsoNum !== data.latest_draw.concorso) {
          lastConcorsoNum = data.latest_draw.concorso;
        }
        appData = data;
        renderDashboard(data);
      }

      fetchSignalsData();
    }
  } catch (err) {
    console.error('Errore nel recupero dati:', err);
  }
}

// Render Dashboard & Pronostico 15 Minuti
function renderDashboard(data) {
  const latest = data.latest_draw;
  if (!latest) return;

  // 1. Estrazione Live
  document.getElementById('latest-concorso-num').textContent = `#${latest.concorso}`;
  document.getElementById('latest-concorso-time').textContent = latest.ora;
  
  // Palline estratti
  const ballsCont = document.getElementById('latest-draw-balls');
  ballsCont.innerHTML = '';
  latest.numeri.forEach(num => {
    const b = document.createElement('div');
    b.className = 'ball';
    if (num === latest.oro) b.classList.add('ball-oro');
    else if (num === latest.doppio_oro) b.classList.add('ball-doppio-oro');
    b.textContent = num.toString().padStart(2, '0');
    ballsCont.appendChild(b);
  });

  document.getElementById('latest-oro-val').textContent = latest.oro || '--';
  document.getElementById('latest-doro-val').textContent = latest.doppio_oro || '--';

  // Somma dei 20 numeri
  const sumTot = latest.numeri.reduce((a, b) => a + b, 0);
  const sumEl = document.getElementById('latest-sum-val');
  if (sumEl) {
    sumEl.textContent = `${sumTot} (${sumTot < 850 ? 'Bassa ➔ Spinta 20-40' : (sumTot > 970 ? 'Alta' : 'Bilanciata')})`;
  }

  // 2. Radar Parametri Statistici
  const hour = parseInt(latest.ora.split(':')[0], 10);
  const isOroHour = (hour === 13 || hour === 17 || hour === 23);
  const fasciaEl = document.getElementById('radar-fascia-oraria');
  if (fasciaEl) {
    fasciaEl.innerHTML = isOroHour 
      ? `🔥 Ore ${hour}:00 <span style="color:var(--gold); font-size:0.8rem;">(ORA D'ORO 38.4%)</span>` 
      : `⏱ Ore ${latest.ora} (Fascia Normale)`;
  }

  const cadenza = latest.concorso % 10;
  const cadenzaEl = document.getElementById('radar-cadenza-concorso');
  if (cadenzaEl) {
    let cadNote = 'Normale';
    if (cadenza === 7) cadNote = '🏆 PICCO MASSIMO (37.7%)';
    else if (cadenza === 4 || cadenza === 5) cadNote = '🟢 Alta (36.0%)';
    else if (cadenza === 1 || cadenza === 6) cadNote = '⚪ Bassa (30.7%)';
    cadenzaEl.innerHTML = `Cadenza #${cadenza} ➔ <span style="font-size:0.8rem;">${cadNote}</span>`;
  }

  // Decine Calamita (20-29 e 70-79)
  const d20 = latest.numeri.filter(n => n >= 20 && n <= 29).length;
  const d70 = latest.numeri.filter(n => n >= 70 && n <= 79).length;
  const decineEl = document.getElementById('radar-decine-calamita');
  if (decineEl) {
    decineEl.innerHTML = `Decina 20: <strong>${d20}</strong> | Decina 70: <strong>${d70}</strong>`;
  }

  // Catalizzatori 1 e 90
  const has1 = latest.numeri.includes(1);
  const has90 = latest.numeri.includes(90);
  const catEl = document.getElementById('radar-catalizzatori');
  if (catEl) {
    if (has1 && has90) catEl.innerHTML = '🌟 <strong>1 e 90 Presenti Insieme!</strong> (+49.6%)';
    else if (has1) catEl.innerHTML = '🟢 <strong>Numero 1 Presente</strong> (Innesco)';
    else if (has90) catEl.innerHTML = '🔵 <strong>Numero 90 Presente</strong> (Reset 20-40)';
    else catEl.innerHTML = '⚪ Assenti';
  }
}

    if (semBadge && p.semaforo) {
      if (p.semaforo === 'VERDE') {
        semBadge.textContent = '🟢 VERDE (ALTA REGOLARITÀ)';
        semBadge.style.cssText = 'background:rgba(16,185,129,0.2); color:var(--green); border:1px solid var(--green);';
      } else if (p.semaforo === 'GIALLO') {
        semBadge.textContent = '🟡 GIALLO (MEDIO)';
        semBadge.style.cssText = 'background:rgba(245,158,11,0.2); color:var(--gold); border:1px solid var(--gold);';
      } else {
        semBadge.textContent = '⚪ IN ATTESA';
        semBadge.style.cssText = 'background:rgba(255,255,255,0.1); color:var(--text-muted); border:1px solid var(--text-muted);';
      }
    }
    if (semMotivo && p.motivo_semaforo) {
      semMotivo.textContent = p.motivo_semaforo;
    }

    // Top 5 balls
    const t5Cont = document.getElementById('prof-top5-balls');
    if (t5Cont && p.top5_guida) {
      t5Cont.innerHTML = '';
      p.top5_guida.forEach(item => {
        const b = document.createElement('div');
        b.className = 'ball ball-oro';
        b.style.cssText = 'width:32px; height:32px; font-size:0.85rem;';
        b.textContent = item.num.toString().padStart(2, '0');
        b.title = `Uscito ${item.freq} volte (${item.pct}%)`;
        t5Cont.appendChild(b);
      });
    }

    // Decine & Cadenze
    if (p.decine_canale && document.getElementById('prof-decine-text')) {
      document.getElementById('prof-decine-text').textContent = p.decine_canale.map(d => `${d.decina} (${d.pct}%)`).join(' • ');
    }
    if (p.cadenze_canale && document.getElementById('prof-cadenze-text')) {
      document.getElementById('prof-cadenze-text').textContent = p.cadenze_canale.map(c => `${c.cadenza} (${c.pct}%)`).join(' • ');
    }

    // Super Spy
    if (p.super_spy_certificata && document.getElementById('prof-spy-id')) {
      document.getElementById('prof-spy-id').textContent = p.super_spy_certificata.spy.toString().padStart(2, '0');
      document.getElementById('prof-spy-terzina').textContent = p.super_spy_certificata.top3.join(' - ');
    }
  }

  // Top 5 Spie Alternative
  const spiesTbody = document.getElementById('top-spies-tbody');
  if (spiesTbody && data.top_spies) {
    spiesTbody.innerHTML = '';
    data.top_spies.slice(0, 6).forEach((s, idx) => {
      const tr = document.createElement('tr');
      tr.style.cursor = 'pointer';
      tr.onclick = () => { selectSpyFromMatrix(s.spy); switchTab('tab-spia'); };
      tr.innerHTML = `
        <td><strong style="color:var(--cyan)">#${idx+1}</strong></td>
        <td><span class="ball" style="width:28px; height:28px; font-size:0.8rem; display:inline-flex;">${s.spy.toString().padStart(2,'0')}</span></td>
        <td>${s.pct_presence}% (${s.freq})</td>
        <td><strong style="color:#fef08a">${s.top3.join('-')}</strong></td>
        <td>${s.ambi_post}A / ${s.terni_post}T</td>
        <td><strong style="color:var(--gold)">${s.score}</strong></td>
      `;
      spiesTbody.appendChild(tr);
    });
  }
}

function copiaTerzinaRadar() {
  if (appData && appData.radar && appData.radar.terzina_flow) {
    const tStr = appData.radar.terzina_flow.join(' ');
    document.getElementById('sim-input').value = tStr;
    switchTab('tab-simulatore');
    eseguiSimulazione();
  }
}

// Caricamento e Render dei Segnali 15 Minuti
async function fetchSignalsData() {
  try {
    const res = await fetch('/api/signals?t=' + Date.now());
    const data = await res.json();
    signalsData = data;
    renderSignalsData(data);
  } catch (err) {
    console.error('Errore recupero segnali:', err);
  }
}

function renderSignalsData(data) {
  if (!data) return;
  const sigs = data.signals || [];

  // 1. Popola la Card Principale del Pronostico 15 Minuti con il segnale attivo più recente
  const activeSig = sigs.length > 0 ? sigs[0] : null;
  if (activeSig) {
    document.getElementById('pronostico-spy-num').textContent = activeSig.spia.toString().padStart(2, '0');
    document.getElementById('pronostico-score').textContent = activeSig.power_score || 93;
    
    // Terzina
    const terzinaCont = document.getElementById('pronostico-terzina');
    terzinaCont.innerHTML = '';
    activeSig.terzina.forEach(num => {
      const b = document.createElement('div');
      b.className = 'ball ball-large ball-oro';
      b.textContent = num.toString().padStart(2, '0');
      terzinaCont.appendChild(b);
    });

    document.getElementById('pronostico-oro').textContent = (activeSig.oro || activeSig.terzina[0]).toString().padStart(2, '0');

    // Badge Colpi
    const badgeEl = document.getElementById('active-spy-colpi-badge');
    if (activeSig.stato === 'vinto_terno') {
      badgeEl.innerHTML = `<strong style="color:var(--green)">🏆 TERNO VINTO al Colpo ${activeSig.primo_terno_colpo || 1}!</strong>`;
    } else if (activeSig.stato === 'vinto_ambo' || activeSig.max_punti >= 2) {
      badgeEl.innerHTML = `<strong style="color:var(--green)">✅ AMBO VINTO al Colpo ${activeSig.primo_ambo_colpo || 1}!</strong>`;
    } else {
      badgeEl.innerHTML = `Colpo ${activeSig.colpi_trascorsi}/5 in corso`;
    }

    // Timeline 5 Colpi
    const timelineCont = document.getElementById('active-spy-timeline-container');
    timelineCont.innerHTML = '';
    for (let c = 1; c <= 5; c++) {
      const box = document.createElement('div');
      box.style.cssText = 'flex:1; background:rgba(0,0,0,0.4); padding:6px; border-radius:8px; text-align:center; border:1px solid rgba(255,255,255,0.08);';
      
      const tItem = (activeSig.timeline || []).find(x => x.colpo === c);
      if (tItem) {
        let ptsColor = 'var(--text-muted)';
        let ptsText = `${tItem.punti} pt`;
        if (tItem.punti === 3) {
          ptsColor = 'var(--green)';
          ptsText = '🏆 TERNO!';
          box.style.borderColor = 'var(--green)';
          box.style.background = 'rgba(16,185,129,0.15)';
        } else if (tItem.punti === 2) {
          ptsColor = 'var(--cyan)';
          ptsText = '✅ AMBO!';
          box.style.borderColor = 'var(--cyan)';
          box.style.background = 'rgba(6,182,212,0.15)';
        } else if (tItem.punti === 1) {
          ptsColor = '#fff';
          ptsText = `1 pt [${tItem.presi.join(',')}]`;
        }

        box.innerHTML = `
          <div style="font-size:0.68rem; color:var(--text-muted);">Colpo ${c}</div>
          <div style="font-size:0.75rem; font-weight:800; color:${ptsColor}; margin-top:2px;">${ptsText}</div>
          <div style="font-size:0.65rem; color:var(--text-muted);">#${tItem.concorso}</div>
        `;
      } else {
        box.innerHTML = `
          <div style="font-size:0.68rem; color:var(--text-muted);">Colpo ${c}</div>
          <div style="font-size:0.75rem; font-weight:700; color:rgba(255,255,255,0.3); margin-top:2px;">⏳ Attesa</div>
        `;
      }
      timelineCont.appendChild(box);
    }
  }

  // 2. Popola la Scheda 2 (Registro Segnali 5 Colpi)
  const cont = document.getElementById('signals-list-container');
  if (!cont) return;

  const signalsSignature = JSON.stringify(sigs.map(x => ({ id: x.id, colpi: x.colpi_trascorsi, pts: x.max_punti, stato: x.stato })));
  if (signalsSignature === lastSignalsJson) return;
  lastSignalsJson = signalsSignature;

  cont.innerHTML = '';
  if (sigs.length === 0) {
    cont.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-muted);">Nessun segnale ancora registrato per oggi.</div>';
    return;
  }

  sigs.forEach(s => {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.marginBottom = '12px';

    let statoBadge = '<span style="color:var(--cyan); font-weight:bold;">⏳ In Corso</span>';
    if (s.stato === 'vinto_terno') statoBadge = '<span style="color:var(--green); font-weight:bold;">🏆 TERNO CENTRATO!</span>';
    else if (s.stato === 'vinto_ambo') statoBadge = '<span style="color:var(--green); font-weight:bold;">✅ AMBO VINTO!</span>';
    else if (s.colpi_trascorsi >= 5) statoBadge = '<span style="color:var(--text-muted);">Chiuso 5/5</span>';

    const tBalls = s.terzina.map(n => `<span class="ball ball-oro" style="width:28px; height:28px; font-size:0.85rem; display:inline-flex;">${n.toString().padStart(2,'0')}</span>`).join(' ');

    let tlHtml = '';
    (s.timeline || []).forEach(t => {
      let tCol = 'var(--text-muted)';
      if (t.punti === 3) tCol = 'var(--green)';
      else if (t.punti === 2) tCol = 'var(--cyan)';
      else if (t.punti === 1) tCol = '#fff';

      tlHtml += `
        <div style="background:rgba(0,0,0,0.3); padding:4px 8px; border-radius:6px; font-size:0.75rem; text-align:center;">
          <div>Colpo ${t.colpo} (#${t.concorso})</div>
          <div style="font-weight:bold; color:${tCol};">${t.punti} pt ${t.presi.length ? `[${t.presi.join(',')}]` : ''}</div>
        </div>
      `;
    });

    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <div>
          <span style="font-size:0.8rem; color:var(--text-muted);">Spia <strong>#${s.spia}</strong> (Concorso #${s.concorso_spia} ore ${s.ora})</span>
        </div>
        <div>${statoBadge}</div>
      </div>
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
        <div style="display:flex; gap:6px; align-items:center;">
          <span>Terzina:</span>
          ${tBalls}
        </div>
        <div style="font-size:0.85rem;">Oro: <strong style="color:var(--gold)">${s.oro}</strong></div>
      </div>
      <div style="display:flex; gap:6px; overflow-x:auto;">
        ${tlHtml || '<span style="color:var(--text-muted); font-size:0.75rem;">In attesa dei colpi successivi...</span>'}
      </div>
    `;
    cont.appendChild(card);
  });
}

// Archivio Storico
let archivioDraws = [];
async function caricaArchivioCompleto() {
  try {
    const res = await fetch('/api/all_draws');
    archivioDraws = await res.json();
    document.getElementById('archivio-count-badge').textContent = `${archivioDraws.length} estrazioni`;
    filtraArchivio();
  } catch (e) {
    console.error(e);
  }
}

function filtraArchivio() {
  const query = (document.getElementById('archivio-search-input').value || '').trim().toLowerCase();
  const tbody = document.getElementById('archivio-tbody');
  tbody.innerHTML = '';

  const filtered = archivioDraws.filter(d => {
    if (!query) return true;
    if (d.concorso.toString().includes(query)) return true;
    if (d.numeri.some(n => n.toString() === query)) return true;
    return false;
  }).slice(0, 100);

  filtered.forEach(d => {
    const tr = document.createElement('tr');
    const ballsHtml = d.numeri.map(n => {
      let cls = 'ball';
      if (n === d.oro) cls += ' ball-oro';
      else if (n === d.doppio_oro) cls += ' ball-doppio-oro';
      return `<span class="${cls}" style="width:24px; height:24px; font-size:0.75rem; display:inline-flex; margin:1px;">${n.toString().padStart(2,'0')}</span>`;
    }).join(' ');

    tr.innerHTML = `
      <td><strong>#${d.concorso}</strong></td>
      <td>${d.ora}</td>
      <td><div style="display:flex; flex-wrap:wrap; max-width:480px;">${ballsHtml}</div></td>
      <td><strong style="color:var(--gold)">${d.oro || '--'}</strong></td>
    `;
    tbody.appendChild(tr);
  });
}

// Avvio applicazione
document.addEventListener('DOMContentLoaded', () => {
  fetchLiveData();
  fetchSignalsData();
  setInterval(fetchLiveData, 15000);
});



  data.signals.slice(0, 30).forEach(sig => {
    const card = document.createElement('div');
    card.className = `signal-card ${sig.stato.replace('_', '-')}`;

    let badgeClass = 'badge-in-corso';
    let badgeText = `IN CORSO (${sig.colpi_trascorsi}/20)`;
    let stopBanner = '';
    if (sig.stato === 'vinto_terno') {
      badgeClass = 'badge-terno';
      badgeText = `🛑 STOP: TERNO AL ${sig.primo_terno_colpo}° COLPO!`;
      stopBanner = `<div style="background:rgba(34,197,94,0.15); border:1px solid var(--green); border-radius:6px; padding:6px 10px; font-size:0.8rem; color:#86efac; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
        <span>🛑</span> <strong>GIOCATA INTERROTTA:</strong> Obiettivo Terno centrato al ${sig.primo_terno_colpo}° colpo. Incasso consolidato!
      </div>`;
    } else if (sig.stato === 'vinto_ambo') {
      badgeClass = 'badge-ambo';
      badgeText = `🛑 STOP: AMBO AL ${sig.primo_ambo_colpo}° COLPO`;
      stopBanner = `<div style="background:rgba(34,197,94,0.15); border:1px solid var(--green); border-radius:6px; padding:6px 10px; font-size:0.8rem; color:#86efac; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
        <span>🛑</span> <strong>GIOCATA INTERROTTA:</strong> Ambo centrato al ${sig.primo_ambo_colpo}° colpo (${sig.oro_centrato ? 'con Numero ORO' : 'senza Oro'}). Incasso consolidato!
      </div>`;
    } else if (sig.stato === 'concluso_vuoto') {
      badgeClass = 'badge-vuoto';
      badgeText = 'CONCLUSO (0)';
    }

    // Timeline dots
    let dotsHtml = '';
    for (let step = 1; step <= sig.max_colpi; step++) {
      const match = sig.timeline.find(t => t.colpo === step);
      if (match) {
        let dotCls = 'dot-step';
        if (match.punti === 3) dotCls += ' dot-terno';
        else if (match.punti === 2) dotCls += ' dot-ambo';
        if (match.ha_oro) dotCls += ' dot-oro';
        dotsHtml += `<div class="${dotCls}" title="Colpo #${step} (Conc #${match.concorso}): ${match.punti} punti ${match.ha_oro ? '+ORO' : ''}">${match.punti}</div>`;
      } else {
        dotsHtml += `<div class="dot-step" style="opacity:0.3;">${step}</div>`;
      }
    }

    // Financial detail per card
    const netColor = sig.netto_take_profit >= 0 ? 'var(--green)' : 'var(--red)';
    const netPrefix = sig.netto_take_profit >= 0 ? '+' : '';

    card.innerHTML = `
      <div class="signal-header">
        <div>
          <span style="font-size:0.78rem; color:var(--text-muted);">${sig.data} ore ${sig.ora}</span>
          <div style="font-size:1.05rem; font-weight:800; color:#fff;">
            Concorso #${sig.concorso_spia} ➔ Spia <span style="color:var(--cyan)">${sig.spia.toString().padStart(2, '0')}</span>
          </div>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="badge-status ${badgeClass}">${badgeText}</span>
          <button class="btn-delete-signal" onclick="eliminaSegnaleConConferma('${sig.id}')" title="Elimina segnale dal registro">❌</button>
        </div>
      </div>

      <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(0,0,0,0.25); padding:8px 12px; border-radius:8px; font-size:0.85rem; margin-bottom:8px;">
        <div>Terzina: <strong style="color:#fef08a">${sig.terzina.join(' - ')}</strong></div>
        <div>Oro: <strong style="color:var(--gold)">${sig.oro}</strong></div>
        <div>Max Punti: <strong style="color:var(--green)">${sig.max_punti}</strong></div>
      </div>

      ${stopBanner}

      <!-- Financial Box Card -->
      <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); padding:8px 12px; border-radius:8px; font-size:0.8rem; margin-bottom:6px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
          <span>Take Profit (${sig.tipo_tp || 'Uscita'} al ${sig.colpo_take_profit || sig.colpi_trascorsi}° colpo):</span>
          <strong style="color:${netColor}; font-size:0.95rem;">${netPrefix}${(sig.netto_take_profit !== undefined ? sig.netto_take_profit : sig.netto_totale).toFixed(2)} €</strong>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-muted);">
          <span>Spesa: <strong>${sig.spesa_take_profit || sig.spesa_totale} €</strong> | Incasso: <strong style="color:var(--cyan)">${sig.incasso_take_profit || sig.incasso_totale} €</strong></span>
          <span>(Ciclo 20 colpi: <strong>${sig.netto_totale >= 0 ? '+' : ''}${sig.netto_totale.toFixed(2)} €</strong>)</span>
        </div>
      </div>

      <div class="timeline-dots">
        ${dotsHtml}
      </div>
    `;
    cont.appendChild(card);
  });
}

async function aggiungiSegnaleManuale() {
  const spyVal = parseInt(document.getElementById('lab-in-spy').value, 10);
  const terzStr = document.getElementById('lab-in-terzina').value.trim();
  const oroVal = parseInt(document.getElementById('lab-in-oro').value, 10);

  const nums = terzStr.split(/\s+/).map(x => parseInt(x, 10)).filter(x => !isNaN(x) && x >= 1 && x <= 90);
  if (isNaN(spyVal) || nums.length !== 3) {
    alert('Compila tutti i campi: Spia e 3 numeri di terzina.');
    return;
  }

  try {
    const res = await fetch('/api/add_custom_signal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        spy: spyVal,
        terzina: nums,
        oro: isNaN(oroVal) ? nums[0] : oroVal
      })
    });
    const result = await res.json();
    if (result.status === 'ok') {
      alert('✅ Segnale registrato con successo! Verrà monitorato per i prossimi 20 concorsi.');
      fetchSignalsData();
    }
  } catch (e) {
    console.error(e);
  }
}

// Hook al cambio tab
const originalSwitchTab = switchTab;
switchTab = function(tabId) {
  originalSwitchTab(tabId);
  if (tabId === 'tab-laboratorio') {
    fetchSignalsData();
  }
};
setInterval(() => {
  if (currentTab === 'tab-laboratorio') {
    fetchSignalsData();
  }
}, 15000);

// ================= FUNZIONI 1-CLICK REGISTRAZIONE SPIA =================

async function registraSpiaAttiva1Click() {
  const activeSpy = (spyMode === 'recent' && appData && appData.recent_spy) ? appData.recent_spy : (appData ? appData.best_spy : null);
  if (!activeSpy) {
    alert('Nessuna spia attiva al momento.');
    return;
  }
  await eseguiRegistrazioneSpia(activeSpy.spy, activeSpy.top3, activeSpy.top_oro || activeSpy.top3[0]);
}

async function registraSpiaRapida() {
  const inputEl = document.getElementById('quick-spy-input');
  const num = parseInt(inputEl.value, 10);
  if (isNaN(num) || num < 1 || num > 90) {
    alert('Inserisci un numero valido da 1 a 90.');
    return;
  }

  try {
    const res = await fetch(`/api/spy?num=${num}`);
    const data = await res.json();
    if (data && data.top3) {
      const top3 = data.top3;
      const oro = data.top_oro || top3[0];
      await eseguiRegistrazioneSpia(num, top3, oro);
      inputEl.value = '';
    }
  } catch (e) {
    alert('Errore nel recupero dati per la spia: ' + e);
  }
}

async function eseguiRegistrazioneSpia(spyNum, terzina, oro) {
  try {
    const res = await fetch('/api/add_custom_signal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        spy: parseInt(spyNum, 10),
        terzina: terzina,
        oro: parseInt(oro, 10),
        power_score: 150.0
      })
    });
    const result = await res.json();
    if (result.status === 'ok') {
      alert(`🎯 SPIA ${spyNum} REGISTRATA CON SUCCESSO!\n\n🔮 Terzina Prevista: ${terzina.join(' - ')}\n👑 Numero Oro: ${oro}\n\n✅ Verranno monitorate le prossime 20 estrazioni nel Laboratorio!`);
      switchTab('tab-laboratorio');
    }
  } catch (e) {
    alert('Errore nella registrazione: ' + e);
  }
}

async function eliminaSegnaleConConferma(signalId) {
  if (!confirm('⚠️ Vuoi davvero eliminare questa scheda di spia dal registro?')) {
    return;
  }
  try {
    const res = await fetch('/api/delete_signal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: signalId })
    });
    const result = await res.json();
    if (result.status === 'ok') {
      fetchSignalsData();
    } else {
      alert('Errore: ' + result.message);
    }
  } catch (e) {
    alert('Errore durante l\'eliminazione: ' + e);
  }
}
