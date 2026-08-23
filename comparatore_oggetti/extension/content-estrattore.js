// Gira su lens.google.com, subito.it, vinted.it e facebook.com/marketplace.
// Estrae l'HTML dei risultati SOLO se Prezzly ci ha "armati" di recente per
// QUESTO sito specifico (flag separato per sito: evita che l'apertura in
// background di un sito armi per errore l'estrazione su un altro, e soprattutto
// evita che il content script estragga dati durante la normale navigazione
// dell'utente su questi siti, che non ha nulla a che fare con Prezzly).
const SELETTORE_PRONTO = {
  lens: '#search'
}

;(async function () {
  const TIMEOUT_ARMATO_MS = 3 * 60 * 1000

  const sito = rilevaSito(location.hostname)
  if (!sito) return

  const chiaveArmato = `prezzlyArmato_${sito}`
  const chiaveTimestamp = `prezzlyArmatoAlle_${sito}`

  const dati = await chrome.storage.local.get([chiaveArmato, chiaveTimestamp])
  if (!dati[chiaveArmato]) return
  if (!dati[chiaveTimestamp] || Date.now() - dati[chiaveTimestamp] > TIMEOUT_ARMATO_MS) return

  // Disarma subito: non vogliamo ri-estrarre su altre pagine dello stesso sito visitate dopo.
  await chrome.storage.local.set({ [chiaveArmato]: false })

  const selettorePronto = SELETTORE_PRONTO[sito]
  const elemento = selettorePronto ? await aspettaElemento(selettorePronto, 10000) : await attesaGenerica(2000)
  const html = (elemento || document.body).outerHTML

  chrome.runtime.sendMessage({ type: 'prezzly:estratto', site: sito, html })

  function rilevaSito(hostname) {
    const host = hostname.replace(/^www\./, '')
    if (host === 'lens.google.com') return 'lens'
    if (host.endsWith('subito.it')) return 'subito'
    if (host.endsWith('vinted.it')) return 'vinted'
    if (host === 'facebook.com' || host.endsWith('.facebook.com')) return 'marketplace'
    return null
  }

  function aspettaElemento(selettore, timeoutMs) {
    return new Promise((resolve) => {
      const giaPresente = document.querySelector(selettore)
      if (giaPresente) return resolve(giaPresente)

      const osservatore = new MutationObserver(() => {
        const trovato = document.querySelector(selettore)
        if (trovato) {
          osservatore.disconnect()
          resolve(trovato)
        }
      })
      osservatore.observe(document.documentElement, { childList: true, subtree: true })

      setTimeout(() => {
        osservatore.disconnect()
        resolve(document.querySelector(selettore))
      }, timeoutMs)
    })
  }

  // Per Subito/Vinted/Marketplace non abbiamo un selettore dei risultati
  // verificato (i siti bloccano lo scraping server-side, non possiamo
  // ispezionare l'HTML reale in anticipo, vedi memoria progetto): aspettiamo
  // solo che la pagina finisca di caricare e diamo un margine per il
  // rendering asincrono, poi prendiamo tutto il body.
  function attesaGenerica(ritardoMs) {
    return new Promise((resolve) => {
      function fine() {
        setTimeout(() => resolve(null), ritardoMs)
      }
      if (document.readyState === 'complete') fine()
      else window.addEventListener('load', fine, { once: true })
    })
  }
})()
