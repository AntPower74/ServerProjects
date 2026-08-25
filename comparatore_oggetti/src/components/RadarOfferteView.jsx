import React, { useState, useMemo } from 'react'
import {
  Target,
  Flame,
  MessageSquareText,
  Copy,
  Check,
  PlusCircle,
  ExternalLink,
  Search,
  Sparkles,
  ClipboardPaste,
  RotateCcw,
  ArrowUpDown,
  Filter,
  CheckCircle2,
  DollarSign,
  TrendingUp,
  Tag,
  ShoppingBag,
  Shield,
  SlidersHorizontal,
  Eye,
  EyeOff
} from 'lucide-react'
import { valutaOggettoUniversale } from '../utils/aiEvaluator.js'
import { estraiRisultatiDaHtml } from '../utils/estraiRisultatiLens.js'

const KEYWORDS_ACCESSORI = [
  'cover', 'custodia', 'custodie', 'coque', 'funda', 'fundas', 'capa', 'capas',
  'case', 'cases', 'hoesje', 'housse', 'etui', 'étui', 'bumper', 'skin',
  'vetro', 'vetro temperato', 'screen protector', 'protection écran', 'protection ecran',
  'proteggi schermo', 'pellicola', 'pellicole', 'protector', 'tempered glass', 'folie', 'schutzfolie',
  'copri batteria', 'copribatteria', 'battery cover', 'akkudeckel', 'retro cover',
  'scatola originale', 'scatola vuota', 'box originale', 'empty box', 'boite vide', 'solo scatola', 'boîte',
  'cavo', 'caricatore', 'caricabatterie', 'charger', 'câble', 'adattatore', 'power bank',
  'supporto auto', 'holder', 'coque silicone', 'funda movil', 'reinder',
  'solo display', 'display per', 'solo schermo', 'pezzi di ricambio', 'per ricambi'
]

function isAccessorio(titolo, prezzo) {
  if (!titolo) return false
  const t = titolo.toLowerCase()
  
  // Prezzo inferiore a 12€ per smartphone/console è quasi sempre un accessorio
  if (prezzo !== null && prezzo < 12) return true
  
  return KEYWORDS_ACCESSORI.some(kw => {
    return t.includes(kw)
  })
}

function isModelloIncoerente(titolo, query) {
  if (!titolo || !query) return false
  const t = titolo.toLowerCase()
  const q = query.toLowerCase()

  // Se cerco S8 specifico, scarta tablet, A8, J8, S7, S9, Note 8, Note 9
  if (/\bs8\b/i.test(q)) {
    if (/\b(tab\s*s8|tablet)\b/i.test(t)) return true
    if (/\b(galaxy\s*a8|galaxy\s*j8|galaxy\s*s7|galaxy\s*s9|galaxy\s*note\s*8|galaxy\s*note\s*9|galaxy\s*a6)\b/i.test(t)) return true
    if (/\b(a8|j8|s7|s9|s10|s20|note\s*8|note\s*9|a6)\b/i.test(t) && !/\bs8\b/i.test(t)) return true
  }

  // Se cerco iPhone 12, scarta altri numeri
  if (/\biphone\s*12\b/i.test(q)) {
    if (/\biphone\s*(11|13|14|15|x|xr|xs|7|8)\b/i.test(t) && !/\biphone\s*12\b/i.test(t)) return true
  }

  return false
}

function estraiPrezziDaTestoGrezzo(testo) {
  if (!testo) return []
  const linee = testo.split(/\r?\n/).map(l => l.trim()).filter(Boolean)
  const annunci = []
  
  const regexRigaCompleta = /(.*?),\s*(?:Brand:\s*([^,]+),)?\s*(?:Modello:\s*([^,]+),)?\s*(?:Condizioni:\s*([^,]+),)?\s*(\d+(?:[.,]\d{1,2})?)\s*€/i
  const regexPrezzoIsolato = /^(\d+(?:[.,]\d{1,2})?)\s*€$/

  for (let i = 0; i < linee.length; i++) {
    const linea = linee[i]
    
    const matchRiga = linea.match(regexRigaCompleta)
    if (matchRiga) {
      const titolo = matchRiga[1]?.trim() || 'Articolo Vinted'
      const brand = matchRiga[2]?.trim() || ''
      const modello = matchRiga[3]?.trim() || ''
      const condizione = matchRiga[4]?.trim() || ''
      const prezzo = parseFloat(matchRiga[5].replace(',', '.'))
      
      if (!isNaN(prezzo) && prezzo > 0) {
        annunci.push({
          id: `vinted_txt_${annunci.length}_${Date.now()}`,
          titolo: modello ? `${brand} ${modello} - ${titolo}` : titolo,
          condizione,
          prezzo,
          fonte: 'Vinted'
        })
        continue
      }
    }

    const matchPrezzo = linea.match(regexPrezzoIsolato)
    if (matchPrezzo && i >= 1) {
      const prezzo = parseFloat(matchPrezzo[1].replace(',', '.'))
      const possibileCondizione = linee[i - 1]
      const possibileTitolo = i >= 2 ? linee[i - 2] : linee[i - 1]
      
      if (!annunci.some(a => a.prezzo === prezzo && a.titolo === possibileTitolo)) {
        annunci.push({
          id: `vinted_multi_${annunci.length}_${Date.now()}`,
          titolo: possibileTitolo,
          condizione: possibileCondizione !== possibileTitolo ? possibileCondizione : 'Usato',
          prezzo,
          fonte: 'Vinted'
        })
      }
    }
  }

  return annunci
}

export default function RadarOfferteView({ onCercaSitiEsterni, estensioneInstallata }) {
  const [query, setQuery] = useState('Samsung Galaxy S8')
  const [testoIncollato, setTestoIncollato] = useState('')
  const [mostraBoxIncolla, setMostraBoxIncolla] = useState(false)
  const [annunci, setAnnunci] = useState([])
  const [filtro, setFiltro] = useState('tutti') // 'tutti' | 'affari' | 'trattabili'
  const [filtraAccessori, setFiltraAccessori] = useState(true) // TOGGLE ANTIRUMORE
  const [ordinamento, setOrdinamento] = useState('prezzo-asc') // 'prezzo-asc' | 'margine-desc' | 'prezzo-desc'
  const [copiatoId, setCopiatoId] = useState(null)
  const [affariSalvati, setAffariSalvati] = useState(() => {
    try { return JSON.parse(localStorage.getItem('prezzly_flip_deals') || '[]') } catch { return [] }
  })

  // Calcolo Benchmark AI
  const valutazioneAI = useMemo(() => {
    if (!query || query.trim().length < 3) return null
    return valutaOggettoUniversale(query)
  }, [query])

  // Identificazione e marcatura accessori / rumore
  const annunciClassificati = useMemo(() => {
    return annunci.map(ann => {
      const isAcc = isAccessorio(ann.titolo, ann.prezzo)
      const isIncoerente = isModelloIncoerente(ann.titolo, query)
      const isScartabile = isAcc || isIncoerente
      return {
        ...ann,
        isAccessorio: isAcc,
        isIncoerente,
        isScartabile
      }
    })
  }, [annunci, query])

  const numeroScartati = useMemo(() => {
    return annunciClassificati.filter(a => a.isScartabile).length
  }, [annunciClassificati])

  // Calcolo Benchmark su annunci puliti (non inquinati da cover a 2€)
  const benchmarkVal = useMemo(() => {
    if (valutazioneAI?.schedaOggetto?.prezzoUsatoDettaglio) {
      const match = valutazioneAI.schedaOggetto.prezzoUsatoDettaglio.match(/~(\d+)/)
      if (match) return parseInt(match[1], 10)
    }
    const annunciPuliti = annunciClassificati.filter(a => !a.isScartabile)
    const prezzi = annunciPuliti.map(a => a.prezzo).filter(p => !isNaN(p) && p >= 15).sort((a, b) => a - b)
    if (prezzi.length > 0) {
      const mid = Math.floor(prezzi.length / 2)
      return prezzi.length % 2 !== 0 ? prezzi[mid] : Math.round((prezzi[mid - 1] + prezzi[mid]) / 2)
    }
    return 65
  }, [valutazioneAI, annunciClassificati])

  const targetAcquisto = useMemo(() => Math.round(benchmarkVal * 0.52), [benchmarkVal])
  const tettoMassimo = useMemo(() => Math.round(benchmarkVal * 0.70), [benchmarkVal])

  // Analisi completa di ciascun annuncio
  const annunciAnalizzati = useMemo(() => {
    return annunciClassificati.map((ann, idx) => {
      const p = parseFloat(ann.prezzo)
      const prezzo = !isNaN(p) && p > 0 ? p : null
      const id = ann.id || ann.url || `ann_${idx}`
      
      let tipo = 'mercato'
      let badge = 'PREZZO DI MERCATO'
      let offerta = targetAcquisto
      let profitto = null
      let sconto = 0

      if (prezzo !== null) {
        if (ann.isScartabile) {
          tipo = 'accessorio'
          badge = ann.isAccessorio ? '📦 ACCESSORIO / COVER' : '⚠️ MODELLO DIVERSO'
          offerta = prezzo
        } else if (prezzo <= targetAcquisto) {
          tipo = 'super_deal'
          badge = '🔥 SUPER DEAL (Compra Ora)'
          profitto = Math.max(10, Math.round(benchmarkVal - prezzo))
          offerta = prezzo
        } else if (prezzo <= tettoMassimo || prezzo <= benchmarkVal * 0.85) {
          tipo = 'da_trattare'
          badge = '💬 DA TRATTARE'
          sconto = Math.max(5, Math.round(((prezzo - targetAcquisto) / prezzo) * 100))
          profitto = Math.round(benchmarkVal - targetAcquisto)
          offerta = targetAcquisto
        }
      }

      return {
        ...ann,
        id,
        prezzo,
        tipo,
        badge,
        offerta,
        profitto,
        sconto
      }
    })
  }, [annunciClassificati, benchmarkVal, targetAcquisto, tettoMassimo])

  // Filtro e Ordinamento
  const annunciFiltrati = useMemo(() => {
    let res = annunciAnalizzati

    // Applica filtro antirumore (esclude cover/scatole/altri modelli)
    if (filtraAccessori) {
      res = res.filter(a => !a.isScartabile)
    }

    // Applica filtro categoria deal
    if (filtro === 'affari') res = res.filter(a => a.tipo === 'super_deal')
    if (filtro === 'trattabili') res = res.filter(a => a.tipo === 'super_deal' || a.tipo === 'da_trattare')

    return res.sort((a, b) => {
      if (ordinamento === 'margine-desc') return (b.profitto || 0) - (a.profitto || 0)
      if (ordinamento === 'prezzo-desc') return (b.prezzo || 0) - (a.prezzo || 0)
      return (a.prezzo || 0) - (b.prezzo || 0)
    })
  }, [annunciAnalizzati, filtraAccessori, filtro, ordinamento])

  const superDealsCount = useMemo(() => annunciAnalizzati.filter(a => a.tipo === 'super_deal' && !a.isScartabile).length, [annunciAnalizzati])
  const daTrattareCount = useMemo(() => annunciAnalizzati.filter(a => a.tipo === 'da_trattare' && !a.isScartabile).length, [annunciAnalizzati])

  // Incolla e Parsa da Appunti
  const handleIncollaDaAppunti = async () => {
    try {
      if (navigator.clipboard && navigator.clipboard.readText) {
        const text = await navigator.clipboard.readText()
        if (text && text.trim().length > 0) {
          elaboraTesto(text)
          return
        }
      }
    } catch (e) {
      console.warn(e)
    }
    setMostraBoxIncolla(true)
  }

  const elaboraTesto = (raw) => {
    if (!raw || !raw.trim()) return
    let estratti = []

    if (raw.includes('<') && raw.includes('>')) {
      estratti = estraiRisultatiDaHtml(raw, 'vinted')
      if (estratti.length === 0) estratti = estraiRisultatiDaHtml(raw, 'subito')
      if (estratti.length === 0) estratti = estraiRisultatiDaHtml(raw, 'lens')
    } else {
      estratti = estraiPrezziDaTestoGrezzo(raw)
    }

    if (estratti.length > 0) {
      setAnnunci(prev => {
        const mappa = new Map(prev.map(a => [a.url || a.titolo + a.prezzo, a]))
        for (const e of estratti) mappa.set(e.url || e.titolo + e.prezzo, e)
        return Array.from(mappa.values())
      })
      setTestoIncollato('')
      setMostraBoxIncolla(false)
    } else {
      alert('Non ho trovato annunci con prezzi validi nel testo incollato.')
    }
  }

  const copiaMessaggioOfferta = (ann) => {
    const titolo = ann.titolo || query || 'l\'articolo'
    const offerta = ann.offerta || targetAcquisto
    const testo = `Ciao! Sono interessato al tuo annuncio per "${titolo}". Se per te va bene, posso concludere subito e pagare a ${offerta}€. Fammi sapere se possiamo accordarci, grazie!`
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(testo).then(() => {
        setCopiatoId(ann.id)
        setTimeout(() => setCopiatoId(null), 3000)
      }).catch(() => {
        prompt('Copia il messaggio di offerta:', testo)
      })
    } else {
      prompt('Copia il messaggio di offerta:', testo)
    }
  }

  const salvaNeiMieiAffari = (ann) => {
    const nuovo = {
      id: 'deal_' + Date.now(),
      nome: ann.titolo || query,
      prezzoRichiesto: ann.prezzo ? `${ann.prezzo}€` : 'N/D',
      targetAcquisto: `${ann.offerta || targetAcquisto}€`,
      rivenditaStimata: `${benchmarkVal}€`,
      profittoStimato: ann.profitto ? `+${ann.profitto}€` : 'N/D',
      stato: 'in_trattativa',
      data: new Date().toLocaleDateString('it-IT'),
      url: ann.url || null,
      fonte: ann.fonte || 'Vinted'
    }
    const aggiornati = [nuovo, ...affariSalvati]
    setAffariSalvati(aggiornati)
    localStorage.setItem('prezzly_flip_deals', JSON.stringify(aggiornati))
    setCopiatoId(`salvato_${ann.id}`)
    setTimeout(() => setCopiatoId(null), 2500)
  }

  return (
    <div className="space-y-5 animate-in fade-in duration-300">
      
      {/* Hero Header */}
      <div className="rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950/40 p-4 sm:p-5 space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <span className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
              <Target className="w-3.5 h-3.5" /> Radar Annunci & Offerte
            </span>
            <h2 className="text-xl font-bold text-slate-100 mt-1">Offerte dal Vivo su Vinted & Subito</h2>
            <p className="text-xs text-slate-400">Analisi automatica con esclusione accessori e calcolo delle offerte con margine reale.</p>
          </div>

          <div className="text-right shrink-0">
            <span className="text-[10px] text-slate-500 block uppercase tracking-wider font-semibold">Valore Reale Telefono</span>
            <b className="text-lg sm:text-xl font-mono font-extrabold text-emerald-400">~{benchmarkVal}€</b>
          </div>
        </div>

        {/* Barra di Ricerca & Pulsanti Azione */}
        <div className="flex flex-col sm:flex-row gap-2 pt-2 border-t border-slate-800/80">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Cerca un modello (es. Samsung Galaxy S8, iPhone 12, Nintendo Switch...)"
              className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-medium"
            />
          </div>

          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={handleIncollaDaAppunti}
              className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white text-xs font-bold px-3 py-2 rounded-xl transition-all shadow"
            >
              <ClipboardPaste className="w-4 h-4" /> Incolla da Vinted/Subito
            </button>
            <button
              type="button"
              onClick={() => setMostraBoxIncolla(!mostraBoxIncolla)}
              className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs border border-slate-700"
              title="Apri box di inserimento manuale"
            >
              <Tag className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Box Incolla Manuale Espandibile */}
        {mostraBoxIncolla && (
          <div className="pt-3 border-t border-slate-800/80 space-y-2 animate-in fade-in">
            <label className="text-xs font-semibold text-slate-300 block">
              Incolla il testo o l'HTML copiato dalla pagina di Vinted/Subito:
            </label>
            <textarea
              rows="4"
              value={testoIncollato}
              onChange={(e) => setTestoIncollato(e.target.value)}
              placeholder="Incolla qui tutto il testo o l'HTML degli annunci (Ctrl+A e Ctrl+C su Vinted)..."
              className="w-full p-2.5 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-200 placeholder-slate-500 font-mono"
            />
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setMostraBoxIncolla(false)}
                className="text-xs text-slate-400 px-3 py-1.5 rounded-lg hover:text-slate-200"
              >
                Annulla
              </button>
              <button
                type="button"
                onClick={() => elaboraTesto(testoIncollato)}
                className="text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 px-3.5 py-1.5 rounded-lg"
              >
                Estrai Annunci Ora
              </button>
            </div>
          </div>
        )}

        {/* Scorciatoie di Ricerca Diretta Portali */}
        <div className="flex items-center gap-1.5 flex-wrap pt-1">
          <span className="text-[10px] text-slate-500 font-semibold">Cerca su:</span>
          <a
            href={`https://www.vinted.it/catalog?search_text=${encodeURIComponent(query)}&order=price_low_to_high`}
            target="_blank"
            rel="noreferrer"
            className="text-[11px] font-bold px-2 py-1 rounded-lg bg-teal-500/10 border border-teal-500/20 text-teal-300 hover:bg-teal-500/20 transition-colors inline-flex items-center gap-1"
          >
            👗 Vinted (dal + economico) <ExternalLink className="w-3 h-3" />
          </a>
          <a
            href={`https://www.subito.it/annunci-italia/vendita/usato/?q=${encodeURIComponent(query)}&order=price_asc`}
            target="_blank"
            rel="noreferrer"
            className="text-[11px] font-bold px-2 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 hover:bg-amber-500/20 transition-colors inline-flex items-center gap-1"
          >
            🟧 Subito (dal + economico) <ExternalLink className="w-3 h-3" />
          </a>
          <a
            href={`https://www.ebay.it/sch/i.html?_nkw=${encodeURIComponent(query)}&_sop=15`}
            target="_blank"
            rel="noreferrer"
            className="text-[11px] font-bold px-2 py-1 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-300 hover:bg-blue-500/20 transition-colors inline-flex items-center gap-1"
          >
            🔵 eBay <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>

      {/* Pannello KPI / Target Flipping */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">Target Offerta</span>
          <b className="text-base font-mono font-extrabold text-indigo-400">~{targetAcquisto}€</b>
        </div>
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">Tetto Massimo</span>
          <b className="text-base font-mono font-extrabold text-amber-400">~{tettoMassimo}€</b>
        </div>
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">Super Affari</span>
          <b className="text-base font-mono font-extrabold text-emerald-400">{superDealsCount} telefoni</b>
        </div>
      </div>

      {/* Banner Filtro Antirumore / Accessori */}
      {annunci.length > 0 && numeroScartati > 0 && (
        <div className="flex items-center justify-between gap-2 p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-indigo-400 shrink-0" />
            <span className="text-slate-300">
              Filtro Antirumore: <b className="text-emerald-400">{numeroScartati}</b> cover, accessori e modelli non coerenti nascosti.
            </span>
          </div>
          <button
            type="button"
            onClick={() => setFiltraAccessori(!filtraAccessori)}
            className="text-[11px] font-bold text-slate-400 hover:text-slate-200 inline-flex items-center gap-1 underline"
          >
            {filtraAccessori ? <><Eye className="w-3 h-3" /> Mostra tutti</> : <><EyeOff className="w-3 h-3" /> Nascondi accessori</>}
          </button>
        </div>
      )}

      {/* Lista Annunci con Filtri e Azioni Offerta */}
      {annunci.length > 0 ? (
        <div className="space-y-3">
          
          {/* Barra Filtri e Ordinamento */}
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
              <button
                type="button"
                onClick={() => setFiltro('tutti')}
                className={`text-[11px] font-bold px-3 py-1.5 rounded-lg border transition-all ${
                  filtro === 'tutti'
                    ? 'bg-indigo-600 text-white border-indigo-500'
                    : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                Telefoni ({annunciFiltrati.length})
              </button>
              <button
                type="button"
                onClick={() => setFiltro('affari')}
                className={`text-[11px] font-bold px-3 py-1.5 rounded-lg border transition-all flex items-center gap-1 ${
                  filtro === 'affari'
                    ? 'bg-emerald-600 text-white border-emerald-500'
                    : 'bg-slate-900 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/10'
                }`}
              >
                🔥 Super Affari ({superDealsCount})
              </button>
              <button
                type="button"
                onClick={() => setFiltro('trattabili')}
                className={`text-[11px] font-bold px-3 py-1.5 rounded-lg border transition-all flex items-center gap-1 ${
                  filtro === 'trattabili'
                    ? 'bg-amber-600 text-white border-amber-500'
                    : 'bg-slate-900 text-amber-400 border-amber-500/30 hover:bg-amber-500/10'
                }`}
              >
                💬 Da Trattare ({daTrattareCount})
              </button>
            </div>

            <div className="flex items-center gap-1.5">
              <span className="text-[10px] text-slate-400">Ordina:</span>
              <select
                value={ordinamento}
                onChange={(e) => setOrdinamento(e.target.value)}
                className="bg-slate-900 text-slate-200 text-xs border border-slate-800 rounded-lg px-2 py-1 outline-none font-medium"
              >
                <option value="prezzo-asc">Prezzo: crescente</option>
                <option value="margine-desc">Margine più alto</option>
                <option value="prezzo-desc">Prezzo: decrescente</option>
              </select>
            </div>
          </div>

          {/* Schede Annunci */}
          <div className="space-y-2.5">
            {annunciFiltrati.map((ann, i) => {
              const isCopiato = copiatoId === ann.id
              const isSalvato = copiatoId === `salvato_${ann.id}`
              const fonte = String(ann.fonte || 'Vinted')

              let iconaFonte = '👗'
              let badgeFonte = 'text-teal-300 bg-teal-500/10 border-teal-500/20'
              if (fonte.includes('Subito')) { iconaFonte = '🟧'; badgeFonte = 'text-amber-300 bg-amber-500/10 border-amber-500/20' }
              else if (fonte.includes('eBay')) { iconaFonte = '🔵'; badgeFonte = 'text-blue-300 bg-blue-500/10 border-blue-500/20' }
              else if (fonte.includes('Marketplace')) { iconaFonte = '👥'; badgeFonte = 'text-sky-300 bg-sky-500/10 border-sky-500/20' }

              return (
                <div
                  key={ann.id || i}
                  className={`p-3.5 rounded-2xl border transition-all ${
                    ann.isScartabile
                      ? 'bg-slate-950/40 border-slate-800/60 opacity-60'
                      : ann.tipo === 'super_deal'
                      ? 'bg-emerald-950/25 border-emerald-500/50 hover:border-emerald-500 shadow-md'
                      : ann.tipo === 'da_trattare'
                      ? 'bg-slate-900/80 border-amber-500/30 hover:border-amber-500/60'
                      : 'bg-slate-900/60 border-slate-800'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    {ann.immagine ? (
                      <div className="relative shrink-0">
                        <img
                          src={ann.immagine}
                          alt={ann.titolo}
                          className="w-16 h-16 sm:w-20 sm:h-20 rounded-xl object-cover bg-slate-950 border border-slate-800/80 shadow-sm"
                          onError={(e) => { e.target.parentElement.style.display = 'none' }}
                        />
                      </div>
                    ) : (
                      <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-xl bg-slate-950 border border-slate-800/80 flex items-center justify-center text-xl sm:text-2xl shrink-0 select-none">
                        📱
                      </div>
                    )}

                    <div className="space-y-1 flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded border inline-flex items-center gap-1 ${badgeFonte}`}>
                          <span>{iconaFonte}</span> {fonte}
                        </span>

                        {ann.condizione && (
                          <span className="text-[10px] text-slate-300 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                            {ann.condizione}
                          </span>
                        )}

                        {ann.tipo === 'super_deal' && (
                          <span className="text-[10px] font-extrabold text-emerald-400 bg-emerald-500/20 border border-emerald-500/40 px-2 py-0.5 rounded-full inline-flex items-center gap-1">
                            <Flame className="w-3 h-3 text-emerald-400" /> SUPER DEAL (Compra Subito)
                          </span>
                        )}

                        {ann.tipo === 'da_trattare' && (
                          <span className="text-[10px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 rounded-full inline-flex items-center gap-1">
                            <MessageSquareText className="w-3 h-3 text-amber-400" /> DA TRATTARE (-{ann.sconto}%)
                          </span>
                        )}

                        {ann.isScartabile && (
                          <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                            {ann.badge}
                          </span>
                        )}
                      </div>

                      <h4 className="text-xs sm:text-sm font-semibold text-slate-100 line-clamp-2 mt-1">
                        {String(ann.titolo || 'Articolo')}
                      </h4>
                    </div>

                    <div className="text-right shrink-0">
                      <span className="text-[10px] text-slate-400 block">Prezzo Richiesto:</span>
                      <b className="text-base sm:text-lg font-extrabold text-slate-100 font-mono">
                        {ann.prezzo != null ? `${ann.prezzo}€` : 'N/D'}
                      </b>
                    </div>
                  </div>

                  {/* Banner Proposta & Azioni */}
                  <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                    <div className="text-[11px]">
                      {ann.isScartabile ? (
                        <span className="text-slate-500 italic">
                          Articolo accessorio o modello secondario escluso dal calcolo di rivendita.
                        </span>
                      ) : ann.tipo === 'super_deal' ? (
                        <span className="text-emerald-400 font-bold flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Guadagno netto stimato: +{ann.profitto}€
                        </span>
                      ) : ann.tipo === 'da_trattare' ? (
                        <span className="text-amber-300 font-medium flex items-center gap-1">
                          <span>💡 Offerta consigliata:</span> <b className="text-amber-400 font-bold font-mono text-xs">{ann.offerta}€</b>
                          <span className="text-[10px] text-slate-400">(Margine target: +{ann.profitto}€)</span>
                        </span>
                      ) : (
                        <span className="text-slate-400">
                          Prezzo allineato alla mediana di mercato (~{benchmarkVal}€)
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-1.5 self-end sm:self-auto">
                      {!ann.isScartabile && (
                        <button
                          type="button"
                          onClick={() => copiaMessaggioOfferta(ann)}
                          className={`text-xs font-bold px-3 py-1.5 rounded-xl border transition-all flex items-center gap-1.5 ${
                            isCopiato
                              ? 'bg-emerald-600 text-white border-emerald-500'
                              : 'bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border-indigo-500/30 active:scale-95'
                          }`}
                        >
                          {isCopiato ? (
                            <>
                              <Check className="w-3.5 h-3.5" /> Offerta Copiata!
                            </>
                          ) : (
                            <>
                              <Copy className="w-3.5 h-3.5" /> Copia Offerta ({ann.offerta}€)
                            </>
                          )}
                        </button>
                      )}

                      <button
                        type="button"
                        onClick={() => salvaNeiMieiAffari(ann)}
                        className={`text-xs font-bold p-1.5 rounded-xl border transition-all ${
                          isSalvato
                            ? 'bg-emerald-600 text-white border-emerald-500'
                            : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'
                        }`}
                        title="Salva nei miei affari"
                      >
                        {isSalvato ? <Check className="w-4 h-4" /> : <PlusCircle className="w-4 h-4" />}
                      </button>

                      {ann.url && (
                        <a
                          href={ann.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-xs font-bold p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors inline-flex items-center"
                          title="Apri annuncio sul portale"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="text-center pt-2">
            <button
              type="button"
              onClick={() => { setAnnunci([]); setTestoIncollato(''); }}
              className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Svuota e fai una nuova ricerca
            </button>
          </div>
        </div>
      ) : (
        <div className="p-8 text-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/30 text-slate-400 space-y-3">
          <ShoppingBag className="w-10 h-10 mx-auto text-slate-600" />
          <div>
            <h4 className="text-sm font-bold text-slate-200">Nessun annuncio caricato</h4>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              Vai su Vinted o Subito, seleziona gli annunci (Ctrl+A e Ctrl+C) e clicca sul pulsante <b>"Incolla da Vinted/Subito"</b> in alto per analizzarli tutti istantaneamente!
            </p>
          </div>
          <button
            type="button"
            onClick={handleIncollaDaAppunti}
            className="inline-flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-4 py-2 rounded-xl shadow transition-all"
          >
            <ClipboardPaste className="w-4 h-4" /> Incolla dagli Appunti
          </button>
        </div>
      )}

    </div>
  )
}
