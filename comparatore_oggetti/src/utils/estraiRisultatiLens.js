// Estrae annunci strutturati (titolo, prezzo, fonte, link, disponibilità) da un
// blocco di HTML incollato manualmente dall'utente (es. "Copy outerHTML" dei
// risultati di Google Lens/Shopping, vedi DevTools).
//
// Le classi CSS di Google sono generate/offuscate e cambiano ad ogni deploy:
// costruirci sopra dei selettori si romperebbe silenziosamente nel giro di
// settimane. Ci appoggiamo invece a segnali stabili: il testo visibile
// ("Disponibile" / "Non disponibile" è UI reale, non una classe), il simbolo
// €, e il dominio del link del prodotto. Meno preciso, ma non si rompe ad ogni
// aggiornamento di Google.

const DOMINI_ESCLUSI = [
  'facebook.com', 'instagram.com', 'twitter.com', 'x.com', 'tiktok.com',
  'youtube.com', 'youtu.be',
  'google.com', 'gstatic.com', 'googleusercontent.com', 'googleadservices.com'
]

function hostnamePulito(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return null
  }
}

function estraiPrezzoDaTesto(testo) {
  // Il simbolo € sta dopo il numero su Google ("90 €") ma spesso prima su
  // altri siti ("€90"/"€ 90,00" su Marketplace) — proviamo entrambi gli ordini.
  const corrispondenza = (testo || '').match(/(\d+(?:[.,]\d{1,2})?)\s*€|€\s*(\d+(?:[.,]\d{1,2})?)/)
  if (!corrispondenza) return null
  const grezzo = corrispondenza[1] ?? corrispondenza[2]
  const valore = parseFloat(grezzo.replace(',', '.'))
  return !isNaN(valore) && valore > 0 ? valore : null
}

// Come .textContent, ma ignora <script>/<style> (che .textContent include per
// intero: nella pagina di Google Lens sono enormi e falsano completamente la
// ricerca del prezzo) e i blocchi nascosti (aria-hidden, display:none) che
// Google dissemina ovunque come contenuto duplicato per gli screen reader.
// Include anche gli aria-label: nelle schede immagine di Lens il prezzo sta
// SOLO lì (es. "Titolo, 90 €*"), non nel testo visibile a schermo — è un
// elemento fratello del link, non un genitore, quindi va cercato dentro
// tutto il contenitore e non risalendo dal link.
function testoVisibile(nodo) {
  if (!nodo) return ''
  if (nodo.nodeType === 3) return nodo.textContent // nodo di testo
  if (nodo.nodeType !== 1) return '' // solo elementi ed testo ci interessano
  const tag = nodo.tagName
  if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'NOSCRIPT') return ''
  if (nodo.getAttribute('aria-hidden') === 'true') return ''
  if (/display:\s*none/i.test(nodo.getAttribute('style') || '')) return ''
  const label = nodo.getAttribute('aria-label')
  let testo = label ? ` ${label} ` : ''
  for (const figlio of nodo.childNodes) testo += testoVisibile(figlio) + ' '
  return testo
}

// Risale dal link del prodotto verso i genitori finché non trova un blocco che
// contiene un prezzo: è quasi sempre il contenitore della singola scheda
// prodotto (il badge prezzo in genere sta appena fuori dal tag <a>). Si ferma
// se il contenitore diventa troppo grande: oltre una certa soglia stiamo
// quasi certamente uscendo dalla scheda del singolo prodotto ed entrando in
// quella dei vicini.
function trovaContenitoreConPrezzo(ancora, maxLivelli = 8, maxCaratteri = 1000) {
  let nodo = ancora
  for (let i = 0; i < maxLivelli && nodo; i++) {
    const testo = testoVisibile(nodo)
    if (testo.length > maxCaratteri) break
    if (estraiPrezzoDaTesto(testo) !== null) return nodo
    nodo = nodo.parentElement
  }
  return null
}

// Etichette generiche di bottoni/UI che compaiono come aria-label sparsi
// dentro ai contenitori (menu, condivisione, microfono...): non sono mai il
// titolo del prodotto, vanno scartate a priori.
const ARIA_LABEL_GENERICHE = /^(informazioni su|condividi|chiudi|indietro|copia link|invia|riprova|microphone|aggiungi file)/i

function trovaTitolo(ancora, contenitore) {
  // 1) Un <h3> è quasi sempre il titolo (è così nei risultati organici da
  // sempre, tag semantico stabile, non una classe generata).
  const h3 = contenitore.querySelector?.('h3')
  const testoH3 = h3 ? testoVisibile(h3).trim() : ''
  if (testoH3) return testoH3

  // 2) Nelle schede immagine il titolo sta nell'aria-label di un elemento
  // FRATELLO del link (non un antenato), spesso nel formato "Titolo, 90 €*":
  // cerchiamo quindi in tutto il contenitore, non risalendo dal link.
  const candidati = Array.from(contenitore.querySelectorAll?.('[aria-label]') || [])
    .map((el) => (el.getAttribute('aria-label') || '').trim())
    .filter((testo) => testo.length > 8 && !/^\d/.test(testo) && !ARIA_LABEL_GENERICHE.test(testo))

  const conPrezzo = candidati.find((testo) => /€/.test(testo))
  const scelto = conPrezzo || candidati[0]
  if (scelto) return scelto.replace(/,?\s*\d+(?:[.,]\d{1,2})?\s*€\*?$/, '').trim()

  // 3) Ultima spiaggia: il testo del link stesso.
  const testoAncora = testoVisibile(ancora).trim()
  return testoAncora ? testoAncora.slice(0, 120) : null
}

function trovaDisponibilita(testo) {
  if (/non\s+disponibile/i.test(testo)) return false
  if (/disponibile/i.test(testo)) return true
  return null
}

// Su Lens la pagina è un aggregatore: i link che interessano puntano FUORI da
// google/social (da qui l'esclusione domini). Su Subito/Vinted/Marketplace,
// invece, la pagina È la fonte: i link che interessano puntano dentro allo
// stesso dominio, verso il singolo annuncio — li riconosciamo dal pattern
// stabile dell'URL (definito pubblicamente da ciascun sito), non da classi
// CSS generate che cambiano ad ogni deploy.
//
// Nota: questi tre pattern non sono stati verificati contro HTML reale (i
// siti bloccano lo scraping server-side, vedi memoria progetto) — sono
// costruiti sulla struttura nota degli URL. Come già successo con Lens,
// vanno probabilmente affinati dopo il primo uso reale.
const SITI = {
  lens: {
    accettaLink: (host) => !!host && !DOMINI_ESCLUSI.some((d) => host === d || host.endsWith(`.${d}`)),
    sorgente: (host) => host
  },
  subito: {
    accettaLink: (host, href) => !!host && host.endsWith('subito.it') && /-\d{6,}\.html?(?:[?#]|$)/i.test(href),
    sorgente: () => 'Subito'
  },
  vinted: {
    accettaLink: (host, href) => !!host && host.endsWith('vinted.it') && /\/items\/\d+/i.test(href),
    sorgente: () => 'Vinted'
  },
  marketplace: {
    accettaLink: (host, href) => !!host && (host === 'facebook.com' || host.endsWith('.facebook.com')) && /\/marketplace\/item\/\d+/i.test(href),
    sorgente: () => 'Marketplace'
  }
}

export function estraiRisultatiDaHtml(html, sito = 'lens') {
  if (!html || !html.includes('<')) return []

  const config = SITI[sito] || SITI.lens
  const doc = new DOMParser().parseFromString(html, 'text/html')
  const ancore = Array.from(doc.querySelectorAll('a[href^="http"]'))
  const trovati = new Map()

  for (const ancora of ancore) {
    const href = ancora.getAttribute('href')
    const host = hostnamePulito(href)
    if (!config.accettaLink(host, href)) continue
    if (trovati.has(href)) continue

    const contenitore = trovaContenitoreConPrezzo(ancora)
    if (!contenitore) continue
    const testoContenitore = testoVisibile(contenitore)
    const prezzo = estraiPrezzoDaTesto(testoContenitore)
    if (prezzo === null) continue

    trovati.set(href, {
      id: href,
      prezzo,
      stato: 'attivo',
      sorgente: config.sorgente(host),
      giorniFa: null,
      titolo: trovaTitolo(ancora, contenitore),
      url: href,
      disponibile: trovaDisponibilita(testoContenitore)
    })
  }

  return Array.from(trovati.values()).sort((a, b) => a.prezzo - b.prezzo)
}
