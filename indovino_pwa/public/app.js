// Inizializzazione PWA & State
let appData = null;
let currentTab = 'tab-pronostico';
let spyMode = 'global'; // Di default 'global' (Spia Giornaliera)
let lastConcorsoNum = null;
let currentClientBuild = null;

// Registrazione Service Worker senza reload forzato
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW error:', err));
}


function setSpyMode(mode) {
  spyMode = mode;
  const recentBtn = document.getElementById('mode-recent-btn');
  const globalBtn = document.getElementById('mode-global-btn');
  
  if (recentBtn && globalBtn) {
    if (mode === 'recent') {
      recentBtn.className = 'btn';
      globalBtn.className = 'btn btn-outline';
    } else {
      recentBtn.className = 'btn btn-outline';
      globalBtn.className = 'btn';
    }
  }
  
  if (appData) {
    renderDashboard(appData);
  }
}

// Navigazione a Schede
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

  // Interroga il server puntualmente allo scoccare della nuova estrazione, non ogni secondo
  if (diffSec === 299 || diffSec === 290) {
    fetchLiveData(true);
  }
}
setInterval(updateCountdown, 1000);

let lastRenderedJson = '';
let lastSignalsJson = '';

// Caricamento Dati Principali con Diffing per non azzerare lo scroll
async function fetchLiveData(force = false) {
  try {
    const res = await fetch('/api/data?t=' + Date.now());
    const data = await res.json();
    if (data.status === 'ok') {
      currentClientBuild = data.build_version;

      const dataSignature = JSON.stringify({
        c: data.latest_draw ? data.latest_draw.concorso : null,
        mode: spyMode,
        best: data.best_spy ? data.best_spy.spy : null,
        recent: data.recent_spy ? data.recent_spy.spy : null
      });

      if (force || dataSignature !== lastRenderedJson) {
        lastRenderedJson = dataSignature;
        if (data.latest_draw && lastConcorsoNum !== data.latest_draw.concorso) {
          lastConcorsoNum = data.latest_draw.concorso;
          console.log(`📢 Nuova estrazione arrivata: #${lastConcorsoNum} ore ${data.latest_draw.ora}`);
        }
        appData = data;
        renderDashboard(data);
      }

      if (currentTab === 'tab-laboratorio') {
        fetchSignalsData();
      }
    }
  } catch (err) {
    console.error('Errore nel recupero dati:', err);
  }
}


// Render Dashboard & Pronostico
function renderDashboard(data) {
  // Concorso info
  const countEl = document.getElementById('total-draws-count');
  if (countEl) countEl.textContent = data.total_draws;

  const latest = data.latest_draw;
  if (latest) {
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

    // Alert Spia uscito
    const bestSpy = data.best_spy;
    if (bestSpy && latest.numeri.includes(bestSpy.spy)) {
      const alertBox = document.getElementById('spy-alert');
      const alertMsg = document.getElementById('spy-alert-msg');
      alertBox.classList.add('active');
      const t = bestSpy.top3;
      alertMsg.innerHTML = `<strong>ALLERTA SPIA ${bestSpy.spy}!</strong> È uscita la spia regina! Gioca subito al concorso #${latest.concorso+1} la terzina: <strong style="color:#fef08a">${t[0]}-${t[1]}-${t[2]}</strong> (Oro: ${bestSpy.top_oro})`;
    } else {
      document.getElementById('spy-alert').classList.remove('active');
    }
  }

  // Pronostico Sezione
  const activeSpy = (spyMode === 'recent' && data.recent_spy) ? data.recent_spy : data.best_spy;
  
  if (latest && activeSpy) {
    if (latest.numeri.includes(activeSpy.spy)) {
      const alertBox = document.getElementById('spy-alert');
      const alertMsg = document.getElementById('spy-alert-msg');
      alertBox.classList.add('active');
      const t = activeSpy.top3;
      alertMsg.innerHTML = `<strong>ALLERTA SPIA ${activeSpy.spy}!</strong> È uscita la spia attiva! Gioca subito al concorso #${latest.concorso+1} la terzina: <strong style="color:#fef08a">${t[0]}-${t[1]}-${t[2]}</strong> (Oro: ${activeSpy.top_oro})`;
    } else {
      document.getElementById('spy-alert').classList.remove('active');
    }
  }

  if (activeSpy) {
    const labelBox = document.querySelector('.spy-badge-box span');
    if (labelBox) {
      labelBox.textContent = (spyMode === 'recent') ? 'SPIA DEL MOMENTO (3 Ore):' : 'MIGLIOR SPIA GIORNALIERA:';
    }
    document.getElementById('pronostico-spy-num').textContent = activeSpy.spy.toString().padStart(2, '0');
    document.getElementById('pronostico-spy-pct').textContent = `${activeSpy.pct_presence}%`;
    
    const terzinaCont = document.getElementById('pronostico-terzina');
    terzinaCont.innerHTML = '';
    activeSpy.top3.forEach(num => {
      const b = document.createElement('div');
      b.className = 'ball ball-large ball-oro';
      b.textContent = num.toString().padStart(2, '0');
      terzinaCont.appendChild(b);
    });

    document.getElementById('pronostico-oro').textContent = (activeSpy.top_oro || activeSpy.top3[0]).toString().padStart(2, '0');
    document.getElementById('pronostico-score').textContent = activeSpy.score;
    document.getElementById('pronostico-ambi').textContent = activeSpy.ambi_post;
    document.getElementById('pronostico-terni').textContent = activeSpy.terni_post;

    // Popola anche l'input del simulatore
    const simInput = document.getElementById('sim-input');
    if (simInput) {
      simInput.value = activeSpy.top3.join(' ');
    }
  }

  // Radar Flusso Algoritmo Render
  if (data.radar) {
    const r = data.radar;
    // Eco balls
    const ecoCont = document.getElementById('radar-eco-balls');
    if (ecoCont && r.eco_candidati) {
      ecoCont.innerHTML = '';
      r.eco_candidati.forEach(num => {
        const b = document.createElement('span');
        b.className = 'ball';
        b.style.cssText = 'width:28px; height:28px; font-size:0.8rem; display:inline-flex; border-color:var(--cyan);';
        b.textContent = num.toString().padStart(2, '0');
        ecoCont.appendChild(b);
      });
    }

    // Lateral balls
    const latCont = document.getElementById('radar-lateral-balls');
    if (latCont && r.laterali_candidati) {
      latCont.innerHTML = '';
      r.laterali_candidati.forEach(num => {
        const b = document.createElement('span');
        b.className = 'ball';
        b.style.cssText = 'width:28px; height:28px; font-size:0.8rem; display:inline-flex; border-color:#fef08a;';
        b.textContent = num.toString().padStart(2, '0');
        latCont.appendChild(b);
      });
    }

    // Baricentro
    if (r.baricentro) {
      document.getElementById('baricentro-bassa').textContent = `${r.baricentro.bassa_1_30}%`;
      document.getElementById('baricentro-media').textContent = `${r.baricentro.media_31_60}%`;
      document.getElementById('baricentro-alta').textContent = `${r.baricentro.alta_61_90}%`;

      document.getElementById('bar-fill-bassa').style.width = `${r.baricentro.bassa_1_30}%`;
      document.getElementById('bar-fill-media').style.width = `${r.baricentro.media_31_60}%`;
      document.getElementById('bar-fill-alta').style.width = `${r.baricentro.alta_61_90}%`;
    }

    // Terzina flow
    if (r.terzina_flow) {
      document.getElementById('radar-fusion-terzina').textContent = r.terzina_flow.map(x => x.toString().padStart(2, '0')).join(' - ');
    }
  }

  // Profiler 100 Estrazioni Render
  if (data.profiler_100) {
    const p = data.profiler_100;
    const semBadge = document.getElementById('prof-badge-semaforo');
    const semMotivo = document.getElementById('prof-motivo-text');
    
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

// Simulatore
async function eseguiSimulazione() {
  const inputStr = document.getElementById('sim-input').value.trim();
  const option = document.getElementById('sim-option').value;
  const bet = parseFloat(document.getElementById('sim-bet').value) || 1.0;

  const nums = inputStr.split(/\s+/).map(x => parseInt(x, 10)).filter(x => !isNaN(x) && x >= 1 && x <= 90);
  if (nums.length !== 3) {
    alert('Inserisci esattamente 3 numeri validi compresi tra 1 e 90 (es: 59 74 84)');
    return;
  }

  try {
    const res = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ numbers: nums, option: option, bet: bet })
    });
    const result = await res.json();
    renderSimResult(result);
  } catch (err) {
    console.error('Errore simulazione:', err);
  }
}

function renderSimResult(res) {
  const cont = document.getElementById('sim-results-container');
  cont.style.display = 'block';

  document.getElementById('sim-res-spesa').textContent = `${res.spesa.toFixed(2)} €`;
  document.getElementById('sim-res-incasso').textContent = `${res.incasso.toFixed(2)} €`;
  
  const saldoEl = document.getElementById('sim-res-saldo');
  saldoEl.textContent = `${res.saldo >= 0 ? '+' : ''}${res.saldo.toFixed(2)} €`;
  saldoEl.style.color = res.saldo >= 0 ? 'var(--green)' : 'var(--red)';

  document.getElementById('sim-res-ambi').textContent = res.ambi;
  document.getElementById('sim-res-ambi-oro').textContent = res.ambi_oro;
  document.getElementById('sim-res-terni').textContent = res.terni;
  document.getElementById('sim-res-terni-oro').textContent = res.terni_oro;

  // Log vincite
  const logCont = document.getElementById('sim-log-tbody');
  logCont.innerHTML = '';
  if (res.log && res.log.length > 0) {
    res.log.slice(0, 10).forEach(item => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>#${item.concorso} (${item.ora})</td>
        <td><strong>${item.punti} Punti</strong> ${item.oro ? '<span style="color:var(--gold); font-weight:bold;">[ORO]</span>' : ''}</td>
        <td style="color:var(--green)">+${item.vinto.toFixed(2)} €</td>
        <td>${item.saldo_progressivo >= 0 ? '+' : ''}${item.saldo_progressivo.toFixed(2)} €</td>
      `;
      logCont.appendChild(tr);
    });
  } else {
    logCont.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">Nessuna vincita registrata oggi per questa combinazione.</td></tr>';
  }
}

// Matrice 90 Numeri Spia
function generaMatriceSpia() {
  const cont = document.getElementById('matrix-90-container');
  cont.innerHTML = '';
  for (let i = 1; i <= 90; i++) {
    const b = document.createElement('div');
    b.className = 'matrix-ball';
    b.textContent = i.toString().padStart(2, '0');
    b.onclick = () => selectSpyFromMatrix(i);
    b.id = `matrix-ball-${i}`;
    cont.appendChild(b);
  }
}

async function selectSpyFromMatrix(spyNum) {
  document.querySelectorAll('.matrix-ball').forEach(el => el.classList.remove('selected'));
  const target = document.getElementById(`matrix-ball-${spyNum}`);
  if (target) target.classList.add('selected');

  document.getElementById('spy-detail-loading').style.display = 'block';
  document.getElementById('spy-detail-card').style.display = 'none';

  try {
    const res = await fetch(`/api/spy?num=${spyNum}`);
    const spyData = await res.json();
    renderSpyDetail(spyData);
  } catch (e) {
    console.error(e);
  } finally {
    document.getElementById('spy-detail-loading').style.display = 'none';
  }
}

function renderSpyDetail(data) {
  if (!data || !data.spy) {
    alert('Nessun dato per questo numero oggi');
    return;
  }
  const card = document.getElementById('spy-detail-card');
  card.style.display = 'block';

  document.getElementById('spy-det-num').textContent = data.spy.toString().padStart(2, '0');
  document.getElementById('spy-det-freq').textContent = `${data.freq} volte (${data.pct_presence}%)`;
  document.getElementById('spy-det-terzina').textContent = data.top3.join(' - ');
  document.getElementById('spy-det-oro').textContent = data.top_oro || '--';
  document.getElementById('spy-det-ambi').textContent = data.ambi_post;
  document.getElementById('spy-det-terni').textContent = data.terni_post;

  const histCont = document.getElementById('spy-ranking-list');
  histCont.innerHTML = '';
  data.ranking_post.forEach(item => {
    const row = document.createElement('div');
    row.style.marginBottom = '8px';
    row.innerHTML = `
      <div style="display:flex; justify-content:space-between; font-size:0.85rem;">
        <span>Numero <strong style="color:var(--cyan)">${item.num.toString().padStart(2, '0')}</strong></span>
        <span>${item.count} uscite (<strong>${item.pct}%</strong>)</span>
      </div>
      <div class="progress-bar-container">
        <div class="progress-bar-fill" style="width: ${Math.min(100, item.pct * 2.5)}%;"></div>
      </div>
    `;
    histCont.appendChild(row);
  });
}

// Archivio Completo
async function caricaArchivioCompleto() {
  try {
    const res = await fetch('/api/all_draws');
    const allDraws = await res.json();
    const tbody = document.getElementById('archivio-tbody');
    tbody.innerHTML = '';

    allDraws.forEach(d => {
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
  } catch (e) {
    console.error(e);
  }
}

// Avvio applicazione
document.addEventListener('DOMContentLoaded', () => {
  generaMatriceSpia();
  fetchLiveData();
  setInterval(fetchLiveData, 15000); // refresh ogni 15s
  selectSpyFromMatrix(24); // default spia 24
});

// ================= LABORATORIO 24/48H SEGNALI =================

async function fetchSignalsData() {
  try {
    const res = await fetch('/api/signals');
    const data = await res.json();
    renderSignalsData(data);
  } catch (err) {
    console.error('Errore recupero segnali:', err);
  }
}

function renderSignalsData(data) {
  if (!data || !data.stats) return;
  const s = data.stats;

  document.getElementById('lab-tot-segnali').textContent = s.totale_segnali || 0;
  document.getElementById('lab-pct-ambo').textContent = `${s.pct_successo_ambo || 0}%`;
  document.getElementById('lab-pct-terno').textContent = `${s.pct_successo_terno || 0}%`;
  document.getElementById('lab-colpo-ambo').textContent = `${s.media_colpo_ambo || '--'}° colpo`;
  document.getElementById('lab-colpo-terno').textContent = `${s.media_colpo_terno || '--'}° colpo`;
  document.getElementById('lab-pct-oro').textContent = `${s.pct_con_oro || 0}%`;

  // Financial totals (Take profit mode)
  if (document.getElementById('lab-tot-spesa')) {
    document.getElementById('lab-tot-spesa').textContent = `${s.totale_spesa_tp || 0} €`;
    document.getElementById('lab-tot-incasso').textContent = `${s.totale_incasso_tp || 0} €`;
    const netEl = document.getElementById('lab-tot-netto');
    const netVal = s.saldo_netto_tp || 0;
    netEl.textContent = `${netVal >= 0 ? '+' : ''}${netVal.toFixed(2)} €`;
    netEl.style.color = netVal >= 0 ? 'var(--green)' : 'var(--red)';
  }

  const signalsSignature = JSON.stringify((data.signals || []).slice(0, 30).map(x => ({
    id: x.id,
    colpi: x.colpi_trascorsi,
    pts: x.max_punti,
    stato: x.stato
  })));

  if (signalsSignature === lastSignalsJson) {
    return;
  }
  lastSignalsJson = signalsSignature;

  const cont = document.getElementById('signals-list-container');
  cont.innerHTML = '';

  if (!data.signals || data.signals.length === 0) {
    cont.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-muted);">Nessun segnale ancora registrato.</div>';
    return;
  }


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
