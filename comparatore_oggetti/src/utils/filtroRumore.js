/**
 * Modulo Filtro Antirumore & Motore di Confronto Mercato Prezzly
 * Confronta tutti gli annunci caricati per determinare la reale distribuzione dei prezzi,
 * la mediana di vendita rapida, e posizionare ogni annuncio rispetto a tutti gli altri.
 */

import { ANDROID_MODELS, IPHONE_MODELS } from './aiEvaluator.js'

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
  'câble', 'cavo', 'cavi', 'hub usb', 'adattatore', 'power bank', 'porta cellulare', 'supporto auto', 'holder',
  // Display e schermi singoli di ricambio
  'solo display', 'display per', 'schermo per', 'lcd per', 'touch screen per', 'solo schermo', 'display tft',
  'touch screen schermo', 'lcd touch', 'pezzi di ricambio', 'per ricambi', 'per parti', 'per pezzi',
  // Scatole vuote
  'scatola originale', 'scatola vuota', 'box originale', 'empty box', 'boite vide', 'solo scatola', 'boîte'
]

// Blacklist categorie estranee agli smartphone
const KEYWORDS_CATEGORIE_ESTRANEE = [
  'lavatrice', 'lavatrici', 'microonde', 'frigo', 'frigorifero', 'forno', 'aspirapolvere',
  'lavastoviglie', 'condizionatore', 'climatizzatore', 'robot cucina', 'whirlpool', 'candy', 'miele',
  'ombrellone', 'ikea', 'samso', 'samsa', 'tavolo', 'sedia', 'mobile',
  'tv', 'smart tv', 'televisore', 'decoder', 'giradischi', 'dvd', 'vhs', 'soundbar', 'stereo',
  'proiettore', 'elettronica per tv', 'ue55', 'ue40', 'ue43', 'ue50', 'ue65', 'hi-fi', 'samsui',
  'manuale', 'manuali', 'libro', 'libri', 'cd-rom', 'volumi', 'de agostini', 'guida', 'guide',
  'c#', 'java', 'sdk', 'frontpage', 'apogeo', 'uml', 'corso', 'enciclopedia', 'clup', 'parco sempione',
  'pneumatico', 'pneumatici', 'gomme', 'moto', 'auto', 'cerchi', 'avon', 'cobra chrome',
  'ram ddr', 'ddr2', 'ddr3', 'ddr4', 'ddr5', 'toner', 'cartuccia', 'stampante', 'fujitsu',
  'esprimo', 'hard disk', 'ssd', 'scheda madre pc', 'desktop', 'monitor pc',
  'buds', 'buds2', 'buds3', 'galaxy buds', 'cuffie', 'auricolari', 'airpods', 'cornice digitale'
]

export function isAccessorio(titolo, prezzo = null) {
  if (!titolo) return false
  const t = titolo.toLowerCase()
  if (prezzo !== null && prezzo < 14) return true

  for (const kw of KEYWORDS_ACCESSORI) {
    if (t.includes(kw)) {
      if ((t.includes('+ cover') || t.includes('+ custodia') || t.includes('+ coque')) && (t.includes('gb') || t.includes('galaxy') || t.includes('iphone') || t.includes('funzionante') || t.includes('dualsim'))) {
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

  const cercaTelefono = /\b(s[7-9]|s10|s20|s21|s22|s23|s24|iphone|pixel|redmi|xiaomi|smartphone|cellulare|oppo|find x|a\d{2})\b/i.test(q)

  if (cercaTelefono) {
    for (const estranea of KEYWORDS_CATEGORIE_ESTRANEE) {
      const regexEstranea = new RegExp(`\\b${estranea}\\b`, 'i')
      if (regexEstranea.test(t)) return true
    }

    if (/\b(tab\s*s\d+|tab\s*a\d+|tab\s*fe|tablet|ipad|book\s*cover\s*keyboard)\b/i.test(t)) {
      return true
    }

    const matchModelloS = q.match(/\bs(7|8|9|10|20|21|22|23|24)\b/i)
    if (matchModelloS) {
      const numModello = matchModelloS[1]
      const codiceSM = numModello === '8' ? 'g950' : numModello === '9' ? 'g960' : numModello === '10' ? 'g973' : `g9${numModello}`
      
      const haModelloGiusto = new RegExp(`\\bs${numModello}\\b`, 'i').test(t) || t.includes(codiceSM) || t.includes(`s ${numModello}`)
      if (!haModelloGiusto) return true

      const regexAltriModelli = new RegExp(`\\b(s(?!${numModello}\\b)\\d+|a\\d+|j\\d+|corby|fold\\s*\\d+|z\\s*fold|note\\s*\\d+)\\b`, 'i')
      if (regexAltriModelli.test(t) && !t.includes(`s8+`) && !t.includes(`s8 plus`) && !t.includes(`s9+`)) {
        return true
      }
    }
  }

  return false
}

export function trovaValoreBenchmarkModello(titolo, query, fallback = 70) {
  const t = (titolo || query || '').toLowerCase()
  
  const andKeys = Object.keys(ANDROID_MODELS).sort((a, b) => b.length - a.length)
  for (const k of andKeys) {
    if (t.includes(k)) {
      return ANDROID_MODELS[k].baseResale
    }
  }

  const iphoneKeys = Object.keys(IPHONE_MODELS).sort((a, b) => b.length - a.length)
  for (const k of iphoneKeys) {
    if (t.includes(k)) {
      const data = IPHONE_MODELS[k]
      return data.baseResale[128] || data.baseResale[64] || 250
    }
  }

  if (/(oppo\s*a\d+|redmi\s*\d+|galaxy\s*a\d+|realme\s*c\d+|honor\s*x\d+|motorola\s*g\d+)/i.test(t)) {
    return 70
  }

  return fallback
}

/**
 * CONFRONTO COMPARATIVO DI TUTTI GLI ANNUNCI
 * Analizza l'intero lotto di annunci mettendoli a confronto tra loro:
 * - Calcola la mediana reale dei prezzi dal vivo
 * - Posiziona ogni annuncio rispetto alla concorrenza
 */
export function confrontaEAnalizzaLotto(annunciGrezzi, query, benchmarkAI = null) {
  if (!Array.isArray(annunciGrezzi) || annunciGrezzi.length === 0) return []

  // 1. Classificazione iniziale Rumore / Accessori
  const classificati = annunciGrezzi.map((ann, idx) => {
    const p = parseFloat(ann.prezzo)
    const prezzo = !isNaN(p) && p > 0 ? p : null
    const titolo = String(ann.titolo || '')
    const isAcc = isAccessorio(titolo, prezzo)
    const isDisallineato = isCategoriaDisallineata(titolo, query)
    const isScartabile = isAcc || isDisallineato
    return {
      ...ann,
      id: ann.id || ann.url || `ann_${idx}`,
      prezzo,
      isAccessorio: isAcc,
      isDisallineato,
      isScartabile
    }
  })

  // 2. Estrazione prezzi puliti e calcolo mediana reale dal vivo
  const annunciValidi = classificati.filter(a => !a.isScartabile && a.prezzo !== null && a.prezzo >= 15)
  const prezziPuliti = annunciValidi.map(a => a.prezzo).sort((a, b) => a - b)

  let benchmarkMercato = 65
  if (prezziPuliti.length >= 3) {
    // Se ci sono almeno 3 annunci reali, la mediana dei prezzi dal vivo determina la realtà di mercato!
    const mid = Math.floor(prezziPuliti.length / 2)
    benchmarkMercato = prezziPuliti.length % 2 !== 0 ? prezziPuliti[mid] : Math.round((prezziPuliti[mid - 1] + prezziPuliti[mid]) / 2)
  } else if (benchmarkAI) {
    benchmarkMercato = benchmarkAI
  } else {
    benchmarkMercato = trovaValoreBenchmarkModello(null, query, 65)
  }

  // 3. Analisi comparativa di ciascun annuncio rispetto al mercato reale
  return classificati.map((ann) => {
    const prezzo = ann.prezzo
    let tipo = 'mercato'
    let badge = 'PREZZO DI MERCATO'
    let offerta = null
    let profitto = null
    let sconto = 0
    let confrontoMercato = ''

    if (ann.isScartabile) {
      tipo = 'accessorio'
      badge = ann.isAccessorio ? '📦 ACCESSORIO / RICAMBIO' : '⚠️ CATEGORIA NON PERTINENTE'
      offerta = prezzo || 10
      confrontoMercato = 'Articolo escluso dal confronto di mercato smartphone.'
    } else if (prezzo !== null) {
      const totaleMenoCari = prezziPuliti.filter(p => p < prezzo).length
      const totalePiuCari = prezziPuliti.filter(p => p > prezzo).length

      if (prezzo <= benchmarkMercato * 0.62) {
        // 🔥 SUPER DEAL: Tra i prezzi più bassi in assoluto
        tipo = 'super_deal'
        badge = '🔥 SUPER DEAL (Affare Top)'
        const scontoRapido = 12
        offerta = Math.round(prezzo * (1 - scontoRapido / 100))
        sconto = scontoRapido
        profitto = Math.round(benchmarkMercato - offerta)
        confrontoMercato = `🏆 Tra i più economici del mercato (${totalePiuCari} annunci più cari). Valore mediano: ~${benchmarkMercato}€.`
      } else if (prezzo <= benchmarkMercato * 0.90) {
        // 💬 DA TRATTARE: Prezzo buono, proponi sconto realistico che chiude
        tipo = 'da_trattare'
        badge = '💬 DA TRATTARE'
        const scontoRealistico = Math.min(25, Math.max(15, Math.round(((prezzo - (benchmarkMercato * 0.50)) / prezzo) * 100)))
        offerta = Math.round(prezzo * (1 - scontoRealistico / 100))
        sconto = Math.round(((prezzo - offerta) / prezzo) * 100)
        profitto = Math.max(10, Math.round(benchmarkMercato - offerta))
        confrontoMercato = `💡 Sotto la media di mercato (~${benchmarkMercato}€). Con offerta a ${offerta}€ hai +${profitto}€ di margine.`
      } else if (prezzo <= benchmarkMercato * 1.08) {
        // 🏷️ IN LINEA COL MERCATO: Margine stretto
        tipo = 'mercato'
        badge = '🏷️ PREZZO DI MERCATO'
        offerta = Math.round(prezzo * 0.80)
        sconto = 20
        profitto = Math.round(benchmarkMercato - offerta)
        confrontoMercato = `In linea con la media di mercato (~${benchmarkMercato}€). Margine ridotto per il flipping.`
      } else {
        // 🔴 FUORI MERCATO: Troppo caro
        tipo = 'fuori_mercato'
        badge = '🔴 FUORI MERCATO (Chiede troppo)'
        offerta = null
        profitto = null
        sconto = 0
        confrontoMercato = `⚠️ Chiede ${prezzo}€ ma la media è ~${benchmarkMercato}€. Ci sono ${totaleMenoCari} annunci più convenienti.`
      }
    }

    return {
      ...ann,
      benchmarkOggetto: benchmarkMercato,
      tipo,
      badge,
      offerta,
      profitto,
      sconto,
      confrontoMercato
    }
  })
}

// Retrocompatibilità singola
export function analizzaAnnuncio(ann, query, fallbackBenchmark) {
  const res = confrontaEAnalizzaLotto([ann], query, fallbackBenchmark)
  return res[0] || ann
}
