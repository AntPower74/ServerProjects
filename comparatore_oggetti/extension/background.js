const URL_PREZZLY = 'https://prezzly.cupto.it'
const TIMEOUT_ESTRAZIONE_MS = 15000

const URL_SITI = {
  subito: (q) => `https://www.subito.it/annunci-italia/vendita/usato/?q=${encodeURIComponent(q)}`,
  vinted: (q) => `https://www.vinted.it/catalog?search_text=${encodeURIComponent(q)}`,
  marketplace: (q) => `https://www.facebook.com/marketplace/search/?query=${encodeURIComponent(q)}`
}

// tabId della scheda di ricerca aperta in background -> tabId della scheda
// Prezzly che l'ha richiesta. Usata per consegnare i risultati silenziosamente
// (senza rubare il focus, a differenza del flusso Lens qui sotto) e per
// chiudere la scheda di ricerca una volta estratti i dati.
const schedeInCorso = new Map()

async function trovaOApriTabPrezzly() {
  const tabs = await chrome.tabs.query({ url: `${URL_PREZZLY}/*` })
  if (tabs.length > 0) {
    const tab = tabs[0]
    await chrome.tabs.update(tab.id, { active: true })
    await chrome.windows.update(tab.windowId, { focused: true })
    return tab
  }

  const nuovaTab = await chrome.tabs.create({ url: `${URL_PREZZLY}/?lens=1` })
  return new Promise((resolve) => {
    function alAggiornamento(tabId, info) {
      if (tabId === nuovaTab.id && info.status === 'complete') {
        chrome.tabs.onUpdated.removeListener(alAggiornamento)
        resolve(nuovaTab)
      }
    }
    chrome.tabs.onUpdated.addListener(alAggiornamento)
  })
}

// Apre in background (schede non attive, l'utente non le vede mai) una
// ricerca per ciascun sito richiesto, armando prima l'estrazione per quel
// sito specifico. Ogni scheda si autoestrae e si chiude da sola quando
// content-estrattore.js manda i risultati (vedi handler 'prezzly:estratto').
async function avviaRicercaMercato(query, siti, prezzlyTabId) {
  if (prezzlyTabId == null) return

  for (const sito of siti || []) {
    const costruisciUrl = URL_SITI[sito]
    if (!costruisciUrl) continue

    await chrome.storage.local.set({
      [`prezzlyArmato_${sito}`]: true,
      [`prezzlyArmatoAlle_${sito}`]: Date.now()
    })

    const tab = await chrome.tabs.create({ url: costruisciUrl(query), active: false })
    schedeInCorso.set(tab.id, { prezzlyTabId, sito })

    setTimeout(() => {
      if (schedeInCorso.has(tab.id)) {
        schedeInCorso.delete(tab.id)
        chrome.tabs.remove(tab.id).catch(() => {})
      }
    }, TIMEOUT_ESTRAZIONE_MS)
  }
}

chrome.runtime.onMessage.addListener((messaggio, mittente, rispondi) => {
  if (messaggio?.type === 'prezzly:estratto') {
    const tabId = mittente.tab?.id
    const infoScheda = tabId != null ? schedeInCorso.get(tabId) : null

    // Estrazione arrivata da una scheda aperta in background da noi: consegna
    // silenziosa alla scheda Prezzly che l'ha richiesta, senza attivarla né
    // rubare il focus (l'utente non ha mai lasciato quella scheda).
    if (infoScheda) {
      schedeInCorso.delete(tabId)
      chrome.tabs.sendMessage(infoScheda.prezzlyTabId, { type: 'prezzly:consegna', site: messaggio.site, html: messaggio.html })
        .then(() => rispondi({ ok: true }))
        .catch((errore) => {
          console.error('Estrai per Prezzly:', errore)
          rispondi({ ok: false })
        })
      chrome.tabs.remove(tabId).catch(() => {})
      return true
    }

    // Flusso classico Lens: l'utente ha aperto la scheda lui stesso (foto ->
    // "Apri Google Lens"), quindi riattivare/riportare in primo piano la
    // scheda Prezzly è il comportamento atteso.
    trovaOApriTabPrezzly()
      .then((tab) => chrome.tabs.sendMessage(tab.id, { type: 'prezzly:consegna', site: messaggio.site, html: messaggio.html }))
      .then(() => rispondi({ ok: true }))
      .catch((errore) => {
        console.error('Estrai per Prezzly:', errore)
        rispondi({ ok: false })
      })
    return true
  }

  if (messaggio?.type === 'prezzly:cerca-mercato') {
    avviaRicercaMercato(messaggio.query, messaggio.siti, mittente.tab?.id)
      .then(() => rispondi({ ok: true }))
      .catch((errore) => {
        console.error('Estrai per Prezzly:', errore)
        rispondi({ ok: false })
      })
    return true
  }
})
