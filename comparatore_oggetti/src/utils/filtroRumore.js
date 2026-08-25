/**
 * Modulo Filtro Antirumore & Classificazione Intelligente Annunci Prezzly
 * Elimina accessori (cover, pulsanti, batterie, display, cavi) e categorie disallineate (es. tablet se si cerca smartphone).
 */

const KEYWORDS_ACCESSORI = [
  // Cover e custodie
  'cover', 'custodia', 'custodie', 'coque', 'funda', 'fundas', 'capa', 'capas',
  'case', 'cases', 'hoesje', 'housse', 'etui', 'étui', 'bumper', 'skin', 'wallet cover', 'book cover',
  // Pellicole e vetri protettivi
  'vetro', 'vetro temperato', 'screen protector', 'protection écran', 'protection ecran',
  'proteggi schermo', 'pellicola', 'pellicole', 'protector', 'tempered glass', 'folie', 'schutzfolie',
  // Parti di ricambio, tasti, flex, pulsanti
  'pulsante', 'pulsanti', 'interruttore', 'bouton', 'boutons', 'flex', 'tasto', 'tasti',
  'side keys', 'connettore', 'altoparlante', 'speaker', 'fotocamera ricambio', 'camera ricambio',
  'punte', 'pennini', 'molle', 'tasti fisici', 'hard buttons', 'volume rumoroso',
  // Batterie e caricatori
  'batteria', 'batterie', 'battery', 'accu', 'copribatteria', 'copri batteria', 'battery cover',
  'akkudeckel', 'retro cover', 'alimentatore', 'caricatore', 'caricabatterie', 'charger',
  'câble', 'cavo', 'hub usb', 'adattatore', 'power bank', 'porta cellulare', 'supporto auto', 'holder',
  // Display e schermi singoli di ricambio
  'solo display', 'display per', 'schermo per', 'lcd per', 'touch screen per', 'solo schermo',
  'pezzi di ricambio', 'per ricambi', 'per parti', 'per pezzi',
  // Scatole vuote
  'scatola originale', 'scatola vuota', 'box originale', 'empty box', 'boite vide', 'solo scatola', 'boîte'
]

export function isAccessorio(titolo, prezzo = null) {
  if (!titolo) return false
  const t = titolo.toLowerCase()

  // Se il prezzo è inferiore a 15€ ed è catalogato come smartphone/console, è quasi certamente un accessorio
  if (prezzo !== null && prezzo < 12) return true

  for (const kw of KEYWORDS_ACCESSORI) {
    if (t.includes(kw)) {
      // Eccezione: "Galaxy S9 + 2 covers" o "funzionante + cover" è un telefono con accessori inclusi
      if ((t.includes('+ cover') || t.includes('+ custodia') || t.includes('+ coque')) && (t.includes('gb') || t.includes('galaxy') || t.includes('iphone') || t.includes('funzionante') || t.includes('dualsim'))) {
        // Se non è esplicitamente solo la cover
        if (!t.startsWith('cover') && !t.startsWith('custodia') && !t.startsWith('coque') && !t.startsWith('funda')) {
          continue
        }
      }
      return true
    }
  }

  return false
}

export function isCategoriaDisallineata(titolo, query) {
  if (!titolo || !query) return false
  const t = titolo.toLowerCase()
  const q = query.toLowerCase()

  const cercaTablet = /\b(tab|tablet|ipad)\b/i.test(q)
  const cercaTelefono = /\b(s[7-9]|s10|s20|s21|s22|s23|s24|iphone|pixel|redmi|xiaomi|smartphone|cellulare)\b/i.test(q) && !cercaTablet

  // Se cerco uno smartphone (es. S8, S9, S10) e l'annuncio è un Tablet (es. Galaxy Tab S9, Tab S9 FE, Tab A8)
  if (cercaTelefono) {
    if (/\b(tab\s*s\d+|tab\s*a\d+|tab\s*fe|tablet|ipad|book\s*cover\s*keyboard)\b/i.test(t)) {
      return true
    }
  }

  // Controllo coerenza modello specifico se cerco Samsung Galaxy S...
  const matchModelloS = q.match(/\bs(7|8|9|10|20|21|22|23|24)\b/i)
  if (matchModelloS) {
    const numModello = matchModelloS[1]
    // Se cerco S9 ma il titolo è per A9, J9, S7, S8, S10, S20 senza menzionare S9
    const regexAltriS = new RegExp(`\\b(s(?!${numModello}\\b)\\d+|a\\d+|j\\d+|note\\s*\\d+)\\b`, 'i')
    if (regexAltriS.test(t) && !new RegExp(`\\bs${numModello}\\b`, 'i').test(t)) {
      return true
    }
  }

  return false
}

export function analizzaAnnuncio(ann, query, benchmarkVal) {
  const p = parseFloat(ann.prezzo)
  const prezzo = !isNaN(p) && p > 0 ? p : null
  const titolo = String(ann.titolo || '')
  
  const isAcc = isAccessorio(titolo, prezzo)
  const isDisallineato = isCategoriaDisallineata(titolo, query)
  const isScartabile = isAcc || isDisallineato

  const B = benchmarkVal || 75
  let tipo = 'mercato'
  let badge = 'PREZZO DI MERCATO'
  let offerta = null
  let profitto = null
  let sconto = 0

  if (isScartabile) {
    tipo = 'accessorio'
    badge = isAcc ? '📦 ACCESSORIO / RICAMBIO' : '⚠️ CATEGORIA / MODELLO DIVERSO'
    offerta = prezzo || 10
  } else if (prezzo !== null) {
    if (prezzo <= B * 0.55) {
      // 1. SUPER DEAL: Prezzo già eccellente (45%+ sotto mercato)
      // Se si fa un'offerta, proponiamo un ulteriore sconto rapido (-12%) per massimizzare il margine
      tipo = 'super_deal'
      badge = '🔥 SUPER DEAL (Affare Top)'
      const scontoRapido = 12
      offerta = Math.round(prezzo * (1 - scontoRapido / 100))
      sconto = scontoRapido
      profitto = Math.round(B - offerta)
    } else if (prezzo <= B * 0.95) {
      // 2. DA TRATTARE: Prezzo buono, proponi sconto realistico (15% - 25%) che il venditore accetta!
      tipo = 'da_trattare'
      badge = '💬 DA TRATTARE'
      
      // Calcola sconto realistico proporzionato (max 25% per non farsi mandare a quel paese)
      const scontoRealistico = Math.min(25, Math.max(15, Math.round(((prezzo - (B * 0.50)) / prezzo) * 100)))
      offerta = Math.round(prezzo * (1 - scontoRealistico / 100))
      sconto = Math.round(((prezzo - offerta) / prezzo) * 100)
      profitto = Math.max(12, Math.round(B - offerta))
    } else if (prezzo <= B * 1.15) {
      // 3. PREZZO DI MERCATO: Allineato alla media, margine flipping stretto
      tipo = 'mercato'
      badge = '🏷️ PREZZO DI MERCATO'
      offerta = Math.round(prezzo * 0.82) // Proposta -18%
      sconto = 18
      profitto = Math.round(B - offerta)
    } else {
      // 4. FUORI MERCATO: Chiede 100€ su un telefono da 75€ -> Non proporre 30€ (insulto), segnala sovrapprezzo!
      tipo = 'fuori_mercato'
      badge = '🔴 FUORI MERCATO (Chiede troppo)'
      offerta = null
      profitto = null
      sconto = 0
    }
  }

  return {
    ...ann,
    prezzo,
    isAccessorio: isAcc,
    isDisallineato,
    isScartabile,
    tipo,
    badge,
    offerta,
    profitto,
    sconto
  }
}
