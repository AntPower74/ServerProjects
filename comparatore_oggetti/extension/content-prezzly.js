// Gira sulla pagina di Prezzly (isolated world). Fa da ponte tra l'estensione
// e la pagina React, che non può parlare direttamente con chrome.runtime.

window.addEventListener('message', (evento) => {
  if (evento.source !== window) return
  const dati = evento.data
  if (!dati || typeof dati !== 'object') return

  // 1) Prezzly ci avvisa che sta per aprire Google Lens: armiamo l'estrazione
  //    automatica (solo per Lens) sulla scheda che si apre.
  if (dati.type === 'prezzly:arma-estensione') {
    chrome.storage.local.set({ prezzlyArmato_lens: true, prezzlyArmatoAlle_lens: Date.now() })
    return
  }

  // 2) Prezzly ci chiede se siamo installati (per decidere se mostrare i
  //    pulsanti manuali di fallback): rispondiamo subito.
  if (dati.type === 'prezzly:controlla-estensione') {
    window.postMessage({ type: 'prezzly:estensione-presente' }, window.location.origin)
    return
  }

  // 3) Prezzly ci chiede di cercare su Subito/Vinted/Marketplace: giriamo la
  //    richiesta al background, che apre le schede in background e le estrae.
  if (dati.type === 'prezzly:cerca-mercato') {
    chrome.runtime.sendMessage({ type: 'prezzly:cerca-mercato', query: dati.query, siti: dati.siti })
    return
  }
})

// Annuncio spontaneo al caricamento dello script: copre il caso in cui React
// sia già montato e in ascolto (es. dopo un refresh) prima ancora che arrivi
// un ping esplicito da 'prezzly:controlla-estensione'.
window.postMessage({ type: 'prezzly:estensione-presente' }, window.location.origin)

// 4) Il background ci passa l'HTML estratto da una scheda (Lens o uno dei
//    marketplace): lo iniettiamo nella pagina, dove App.jsx lo intercetta.
chrome.runtime.onMessage.addListener((messaggio) => {
  if (messaggio?.type !== 'prezzly:consegna') return
  window.postMessage({ type: 'prezzly:estensione-html', site: messaggio.site, html: messaggio.html }, window.location.origin)
})
