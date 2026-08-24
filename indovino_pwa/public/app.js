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
    if (signalsData) renderSignalsData(signalsData);
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

  // 3. Render Ultime Estrazioni Precedenti (ultime 10)
  const recentCont = document.getElementById('recent-draws-container');
  if (recentCont && data.draws) {
    recentCont.innerHTML = '';
    // Mostra le estrazioni dalla penultima indietro (fino a 10 estrazioni)
    const pastDraws = data.draws.slice(1, 11);
    if (pastDraws.length === 0) {
      recentCont.innerHTML = '<div style="color:var(--text-muted); font-size:0.8rem; text-align:center;">In attesa delle prossime estrazioni...</div>';
    } else {
      pastDraws.forEach(d => {
        const row = document.createElement('div');
        row.style.cssText = 'background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:10px;';
        
        const sumD = d.numeri.reduce((a, b) => a + b, 0);
        const ballsHtml = d.numeri.map(n => {
          let cls = 'ball';
          if (n === d.oro) cls += ' ball-oro';
          else if (n === d.doppio_oro) cls += ' ball-doppio-oro';
          return `<span class="${cls}" style="width:26px; height:26px; font-size:0.75rem; display:inline-flex; margin:1px;">${n.toString().padStart(2,'0')}</span>`;
        }).join('');

        row.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; font-size:0.82rem;">
            <div>
              <strong style="color:var(--gold);">Concorso #${d.concorso}</strong>
              <span style="color:var(--text-muted); margin-left:6px;">(${d.ora})</span>
            </div>
            <div style="font-size:0.75rem; color:var(--cyan);">
              Oro: <strong style="color:var(--gold);">${d.oro || '--'}</strong> | Somma: <strong>${sumD}</strong>
            </div>
          </div>
          <div style="display:flex; flex-wrap:wrap; gap:3px;">
            ${ballsHtml}
          </div>
        `;
        recentCont.appendChild(row);
      });
    }
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

  // 1. Popola la Card Principale del Pronostico 15 Minuti con il segnale più recente
  const activeSig = sigs.length > 0 ? sigs[0] : null;
  if (activeSig) {
    document.getElementById('pronostico-spy-num').textContent = activeSig.spia.toString().padStart(2, '0');
    document.getElementById('pronostico-score').textContent = activeSig.power_score || 93;
    
    // Terzina Display
    const terzinaCont = document.getElementById('pronostico-terzina');
    terzinaCont.innerHTML = '';
    activeSig.terzina.forEach(num => {
      const b = document.createElement('div');
      b.className = 'ball ball-large ball-oro';
      b.textContent = num.toString().padStart(2, '0');
      terzinaCont.appendChild(b);
    });

    const oroVal = activeSig.oro || activeSig.terzina[0];
    document.getElementById('pronostico-oro').textContent = oroVal.toString().padStart(2, '0');

    // Dettaglio testo terzina
    const textDesc = document.getElementById('pronostico-terzina-text');
    if (textDesc) {
      textDesc.textContent = `${activeSig.terzina.map(n => n.toString().padStart(2, '0')).join(' - ')} (Oro: ${oroVal.toString().padStart(2, '0')})`;
    }

    // Badge Colpi
    const badgeEl = document.getElementById('active-spy-colpi-badge');
    if (activeSig.stato === 'vinto_terno') {
      badgeEl.innerHTML = `<strong style="color:var(--green)">🏆 TERNO VINTO al Colpo ${activeSig.primo_terno_colpo || 1}!</strong>`;
    } else if (activeSig.stato === 'vinto_ambo' || activeSig.max_punti >= 2) {
      badgeEl.innerHTML = `<strong style="color:var(--green)">✅ AMBO VINTO al Colpo ${activeSig.primo_ambo_colpo || 1}!</strong>`;
    } else if (activeSig.colpi_trascorsi === 0) {
      badgeEl.innerHTML = `<strong style="color:var(--gold)">⚡ INIZIA AL PROSSIMO CONCORSO (#${activeSig.concorso_spia + 1})</strong>`;
    } else {
      badgeEl.innerHTML = `Colpo ${activeSig.colpi_trascorsi}/5 in corso`;
    }

    // Timeline 5 Colpi
    const timelineCont = document.getElementById('active-spy-timeline-container');
    timelineCont.innerHTML = '';
    for (let c = 1; c <= 5; c++) {
      const targetConc = activeSig.concorso_spia + c;
      const box = document.createElement('div');
      box.style.cssText = 'flex:1; background:rgba(0,0,0,0.4); padding:6px 2px; border-radius:8px; text-align:center; border:1px solid rgba(255,255,255,0.08);';
      
      const tItem = (activeSig.timeline || []).find(x => x.colpo === c);
      if (tItem) {
        let ptsColor = 'var(--text-muted)';
        let ptsText = `${tItem.punti} pt`;
        const presiArr = tItem.estratti_presi || tItem.presi || [];
        if (tItem.punti === 3) {
          ptsColor = 'var(--green)';
          ptsText = '🏆 TERNO!';
          box.style.borderColor = 'var(--green)';
          box.style.background = 'rgba(16,185,129,0.2)';
        } else if (tItem.punti === 2) {
          ptsColor = 'var(--cyan)';
          ptsText = '✅ AMBO!';
          box.style.borderColor = 'var(--cyan)';
          box.style.background = 'rgba(6,182,212,0.2)';
        } else if (tItem.punti === 1) {
          ptsColor = '#fff';
          ptsText = `1 pt [${presiArr.join(',')}]`;
        }

        box.innerHTML = `
          <div style="font-size:0.65rem; color:var(--text-muted);">Colpo ${c}</div>
          <div style="font-size:0.75rem; font-weight:800; color:${ptsColor}; margin-top:2px;">${ptsText}</div>
          <div style="font-size:0.62rem; color:var(--text-muted);">#${tItem.concorso}</div>
        `;
      } else {
        box.innerHTML = `
          <div style="font-size:0.65rem; color:var(--text-muted);">Colpo ${c}</div>
          <div style="font-size:0.75rem; font-weight:700; color:rgba(255,255,255,0.3); margin-top:2px;">⏳ Attesa</div>
          <div style="font-size:0.62rem; color:var(--text-muted);">#${targetConc}</div>
        `;
      }
      timelineCont.appendChild(box);
    }

    // Live Financials Active Spy
    const actSpesa = activeSig.spesa !== undefined ? activeSig.spesa : (activeSig.timeline ? activeSig.timeline.length * 1.0 : 0.0);
    const actRicavo = activeSig.ricavo !== undefined ? activeSig.ricavo : 0.0;
    const actNetto = activeSig.netto !== undefined ? activeSig.netto : (actRicavo - actSpesa);
    
    const actSEl = document.getElementById('active-spy-spesa');
    const actREl = document.getElementById('active-spy-ricavo');
    const actNEl = document.getElementById('active-spy-netto');
    if (actSEl) actSEl.textContent = `€ ${actSpesa.toFixed(2)}`;
    if (actREl) actREl.textContent = `€ ${actRicavo.toFixed(2)}`;
    if (actNEl) {
      actNEl.textContent = `${actNetto >= 0 ? '+' : ''}€ ${actNetto.toFixed(2)}`;
      actNEl.style.color = actNetto > 0 ? 'var(--green)' : (actNetto < 0 ? '#f87171' : 'var(--gold)');
    }
  }

  // 2. Popola la Scheda 2 (Registro Segnali 5 Colpi)
  const cont = document.getElementById('signals-list-container');

  if (!cont) return;

  // Aggiorna Riepilogo Finanziario Giornaliero
  if (data.stats) {
    const sEl = document.getElementById('stats-tot-spesa');
    const iEl = document.getElementById('stats-tot-incasso');
    const nEl = document.getElementById('stats-tot-netto');
    if (sEl) sEl.textContent = `€ ${(data.stats.totale_spesa || 0).toFixed(2)}`;
    if (iEl) iEl.textContent = `€ ${(data.stats.totale_incasso || 0).toFixed(2)}`;
    if (nEl) {
      const net = data.stats.saldo_netto || 0;
      nEl.textContent = `${net >= 0 ? '+' : ''}€ ${net.toFixed(2)}`;
      nEl.style.color = net >= 0 ? 'var(--green)' : '#f87171';
    }
  }

  cont.innerHTML = '';
  if (sigs.length === 0) {
    cont.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-muted);">Nessun segnale ancora registrato per oggi.</div>';
    return;
  }

  sigs.forEach(s => {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.marginBottom = '12px';

    let statoBadge = '<span style="color:var(--cyan); font-weight:bold;">⏳ In Corso (Colpi 0/5)</span>';
    if (s.stato === 'vinto_terno') statoBadge = `<span style="color:var(--green); font-weight:bold;">🏆 TERNO CENTRATO (Colpo ${s.primo_terno_colpo || 1})!</span>`;
    else if (s.stato === 'vinto_ambo') statoBadge = `<span style="color:var(--green); font-weight:bold;">✅ AMBO VINTO (Colpo ${s.primo_ambo_colpo || 1})!</span>`;
    else if (s.colpi_trascorsi >= 5) statoBadge = '<span style="color:var(--text-muted);">Chiuso 5/5</span>';
    else if (s.colpi_trascorsi > 0) statoBadge = `<span style="color:var(--cyan); font-weight:bold;">⏳ In Corso (Colpo ${s.colpi_trascorsi}/5)</span>`;

    const tBalls = s.terzina.map(n => `<span class="ball ball-oro" style="width:28px; height:28px; font-size:0.85rem; display:inline-flex;">${n.toString().padStart(2,'0')}</span>`).join(' ');
    const tText = s.terzina.map(n => n.toString().padStart(2, '0')).join(' - ');

    const spesaVal = s.spesa !== undefined ? s.spesa : (s.timeline ? s.timeline.length * 1.0 : 0.0);
    const ricavoVal = s.ricavo !== undefined ? s.ricavo : 0.0;
    const nettoVal = s.netto !== undefined ? s.netto : (ricavoVal - spesaVal);
    const nettoColor = nettoVal > 0 ? 'var(--green)' : (nettoVal < 0 ? '#f87171' : 'var(--text-muted)');

    let tlHtml = '';
    for (let c = 1; c <= 5; c++) {
      const targetConc = s.concorso_spia + c;
      const t = (s.timeline || []).find(x => x.colpo === c);
      if (t) {
        let tCol = 'var(--text-muted)';
        const presiArr = t.estratti_presi || t.presi || [];
        if (t.punti === 3) tCol = 'var(--green)';
        else if (t.punti === 2) tCol = 'var(--cyan)';
        else if (t.punti === 1) tCol = '#fff';

        tlHtml += `
          <div style="flex:1; background:rgba(0,0,0,0.35); padding:6px; border-radius:8px; font-size:0.75rem; text-align:center; border:1px solid rgba(255,255,255,0.08);">
            <div style="font-size:0.68rem; color:var(--text-muted);">Colpo ${c}</div>
            <div style="font-weight:800; color:${tCol}; margin-top:2px;">${t.punti} pt ${presiArr.length ? `[${presiArr.join(',')}]` : ''}</div>
            <div style="font-size:0.62rem; color:var(--text-muted);">#${t.concorso}</div>
          </div>
        `;
      } else {
        tlHtml += `
          <div style="flex:1; background:rgba(0,0,0,0.25); padding:6px; border-radius:8px; font-size:0.75rem; text-align:center; border:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:0.68rem; color:var(--text-muted);">Colpo ${c}</div>
            <div style="font-weight:700; color:rgba(255,255,255,0.3); margin-top:2px;">⏳ Attesa</div>
            <div style="font-size:0.62rem; color:var(--text-muted);">#${targetConc}</div>
          </div>
        `;
      }
    }

    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <div>
          <span style="font-size:0.85rem; font-weight:800; color:var(--gold);">🔴 Spia #${s.spia}</span>
          <span style="font-size:0.78rem; color:var(--text-muted); margin-left:6px;">(Conc. #${s.concorso_spia} ore ${s.ora})</span>
        </div>
        <div>${statoBadge}</div>
      </div>
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; background:rgba(0,0,0,0.25); padding:8px 10px; border-radius:8px;">
        <div style="display:flex; gap:8px; align-items:center;">
          <span style="font-size:0.8rem; color:var(--text-muted);">Terzina:</span>
          ${tBalls}
          <strong style="color:#fef08a; font-size:0.95rem; margin-left:4px;">${tText}</strong>
        </div>
        <div style="font-size:0.85rem;">Oro: <strong style="color:var(--gold)">${s.oro}</strong></div>
      </div>
      <div style="display:flex; gap:6px; overflow-x:auto; margin-bottom:8px;">
        ${tlHtml}
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(0,0,0,0.35); padding:6px 10px; border-radius:8px; font-size:0.8rem; border:1px solid rgba(255,255,255,0.05);">
        <div>💳 Spesa: <strong style="color:#f87171;">€ ${spesaVal.toFixed(2)}</strong></div>
        <div>💰 Ricavo: <strong style="color:var(--green);">€ ${ricavoVal.toFixed(2)}</strong></div>
        <div>⚖️ Netto: <strong style="color:${nettoColor};">${nettoVal >= 0 ? '+' : ''}€ ${nettoVal.toFixed(2)}</strong></div>
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

// Avvio applicazione con Auto-Refresh Continuo
document.addEventListener('DOMContentLoaded', () => {
  fetchLiveData(true);
  fetchSignalsData();

  // Aggiornamento continuo in background ogni 10 secondi
  setInterval(() => {
    fetchLiveData(true);
    fetchSignalsData();
  }, 10000);

  // Auto-sync immediato quando l'utente sblocca il telefono o torna sulla pagina
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      fetchLiveData(true);
      fetchSignalsData();
    }
  });

  window.addEventListener('focus', () => {
    fetchLiveData(true);
    fetchSignalsData();
  });
});


