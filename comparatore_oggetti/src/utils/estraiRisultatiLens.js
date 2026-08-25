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
  // 1) Attributi diretti sul link: title o aria-label
  const titleAttr = ancora.getAttribute('title')?.trim()
  if (titleAttr && titleAttr.length > 3 && !ARIA_LABEL_GENERICHE.test(titleAttr)) return titleAttr

  const ariaAttr = ancora.getAttribute('aria-label')?.trim()
  if (ariaAttr && ariaAttr.length > 3 && !ARIA_LABEL_GENERICHE.test(ariaAttr)) return ariaAttr

  // 2) Immagine con alt dentro il link (comunissimo nelle card Vinted/Subito)
  const imgAlt = ancora.querySelector('img')?.getAttribute('alt')?.trim()
  if (imgAlt && imgAlt.length > 3 && !ARIA_LABEL_GENERICHE.test(imgAlt)) return imgAlt

  // 3) Elementi specifici di Vinted / Subito / Lens (data-testid o classi note)
  const testIdTitle = contenitore.querySelector?.('[data-testid*="title"], [data-testid*="name"], [data-testid="grid-item-subtitle"], .item-title, h3, h4')
  const testoTestId = testIdTitle ? testoVisibile(testIdTitle).trim() : ''
  if (testoTestId && testoTestId.length > 3 && !ARIA_LABEL_GENERICHE.test(testoTestId)) return testoTestId

  // 4) h3 classico
  const h3 = contenitore.querySelector?.('h3')
  const testoH3 = h3 ? testoVisibile(h3).trim() : ''
  if (testoH3) return testoH3

  // 5) Nelle schede immagine il titolo sta nell'aria-label di un elemento
  // FRATELLO del link (non un antenato), spesso nel formato "Titolo, 90 €*":
  // cerchiamo quindi in tutto il contenitore, non risalendo dal link.
  const candidati = Array.from(contenitore.querySelectorAll?.('[aria-label]') || [])
    .map((el) => (el.getAttribute('aria-label') || '').trim())
    .filter((testo) => testo.length > 5 && !/^\d/.test(testo) && !ARIA_LABEL_GENERICHE.test(testo))

  const conPrezzo = candidati.find((testo) => /€/.test(testo))
  const scelto = conPrezzo || candidati[0]
  if (scelto) return scelto.replace(/,?\s*\d+(?:[.,]\d{1,2})?\s*€\*?$/, '').trim()

  // 6) Testo del link stesso
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
const SITI = {
  lens: {
    baseUrl: '',
    accettaLink: (host, href) => !!host && !DOMINI_ESCLUSI.some((d) => host === d || host.endsWith(`.${d}`)),
    sorgente: (host) => host
  },
  subito: {
    baseUrl: 'https://www.subito.it',
    accettaLink: (host, href) => (!host || host.endsWith('subito.it')) && (/-\d{6,}\.html?(?:[?#]|$)/i.test(href) || /\/annunci\//i.test(href)),
    sorgente: () => 'Subito'
  },
  vinted: {
    baseUrl: 'https://www.vinted.it',
    accettaLink: (host, href) => (!host || /(^|\.)vinted\.[a-z.]+$/i.test(host)) && /\/items\/\d+/i.test(href),
    sorgente: () => 'Vinted'
  },
  marketplace: {
    baseUrl: 'https://www.facebook.com',
    accettaLink: (host, href) => (!host || host === 'facebook.com' || host.endsWith('.facebook.com')) && /\/marketplace\/item\/\d+/i.test(href),
    sorgente: () => 'Marketplace'
  }
}

export function estraiRisultatiDaHtml(html, sito = 'lens') {
  if (!html || !html.includes('<')) return []

  const config = SITI[sito] || SITI.lens
  const doc = new DOMParser().parseFromString(html, 'text/html')
  // Seleziona tutti i tag <a> con href (sia link assoluti che relativi /items/...)
  const ancore = Array.from(doc.querySelectorAll('a[href]'))
  const trovati = new Map()

  for (const ancora of ancore) {
    let href = ancora.getAttribute('href') || ''
    if (!href || href.startsWith('#') || href.startsWith('javascript:')) continue

    // Risolvi i link relativi se il sito ha un dominio base definito
    if (href.startsWith('/') && config.baseUrl) {
      href = config.baseUrl + href
    }

    const host = hostnamePulito(href)
    if (!config.accettaLink(host, href)) continue
    if (trovati.has(href)) continue

    const contenitore = trovaContenitoreConPrezzo(ancora)
    if (!contenitore) continue
    const testoContenitore = testoVisibile(contenitore)
    const prezzo = estraiPrezzoDaTesto(testoContenitore)
    if (prezzo === null) continue

    const titolo = trovaTitolo(ancora, contenitore)

    trovati.set(href, {
      id: href,
      prezzo,
      stato: 'attivo',
      sorgente: config.sorgente(host || 'vinted.it'),
      giorniFa: null,
      titolo: titolo || 'Articolo ' + (host || 'Vinted'),
      url: href,
      disponibile: trovaDisponibilita(testoContenitore)
    })
  }

  return Array.from(trovati.values()).sort((a, b) => a.prezzo - b.prezzo)
}
