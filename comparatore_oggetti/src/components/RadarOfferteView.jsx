import React, { useState, useMemo, useEffect, useCallback } from 'react'
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
  EyeOff,
  Loader2
} from 'lucide-react'
import { valutaOggettoUniversale } from '../utils/aiEvaluator.js'
import { estraiRisultatiDaHtml, pulisciPrezzoItaliano } from '../utils/estraiRisultatiLens.js'
import { confrontaEAnalizzaLotto, isAccessorio, isCategoriaDisallineata } from '../utils/filtroRumore.js'

function estraiPrezziDaTestoGrezzo(testo) {
  if (!testo) return []
  const linee = testo.split(/\r?\n/).map(l => l.trim()).filter(Boolean)
  const annunci = []
  
  // 1. Regex Vinted (es. "Telefono Oppo, Brand: OPPO, Modello: Find X5, Condizioni: Ottime, 100.00 €")
  const regexVinted = /(.*?),\s*(?:Brand:\s*([^,]+),)?\s*(?:Modello:\s*([^,]+),)?\s*(?:Condizioni:\s*([^,]+),)?\s*(\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)\s*€/i
  
  // 2. Regex Facebook Marketplace (es. "Smartphone Oppo A74, 55 €, San Giorgio di Piano, annuncio 1354061726834615")
  const regexMarketplace = /^(.*?),\s*(\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)\s*€(?:,\s*([^,]+))?(?:,\s*(?:annuncio|id)\s*([a-z0-9_-]+))?$/i

  // 3. Regex Subito / Generico a trattino (es. "Samsung Galaxy S8 64GB - 65 € - Torino")
  const regexTrattino = /^(.*?)\s*[-–—|]\s*(\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)\s*€(?:\s*[-–—|]\s*(.*))?$/i

  // 4. Prezzo isolato su una riga (es. "1.199 €" o "55 €")
  const regexPrezzoIsolato = /^(\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)\s*€$/i

  for (let i = 0; i < linee.length; i++) {
    const linea = linee[i]
    
    // Test 1: Vinted
    const matchVinted = linea.match(regexVinted)
    if (matchVinted && (matchVinted[2] || matchVinted[3] || matchVinted[4])) {
      const testoDesc = matchVinted[1]?.trim() || ''
      const brand = matchVinted[2]?.trim() || ''
      const modello = matchVinted[3]?.trim() || ''
      const condizione = matchVinted[4]?.trim() || ''
      const prezzo = pulisciPrezzoItaliano(matchVinted[5])
      
      if (prezzo !== null && prezzo > 0) {
        annunci.push({
          id: `vinted_${annunci.length}_${Date.now()}`,
          titolo: modello ? `${brand} ${modello}`.trim() : (testoDesc.length > 40 ? testoDesc.slice(0, 40) + '...' : testoDesc),
          descrizione: testoDesc,
          condizione,
          prezzo,
          fonte: 'Vinted'
        })
        continue
      }
    }

    // Test 2: Facebook Marketplace
    const matchMarketplace = linea.match(regexMarketplace)
    if (matchMarketplace) {
      const titolo = matchMarketplace[1]?.trim() || 'Articolo Marketplace'
      const prezzo = pulisciPrezzoItaliano(matchMarketplace[2])
      const luogo = matchMarketplace[3]?.trim() || ''
      const idAnnuncio = matchMarketplace[4]?.trim() || ''

      if (prezzo !== null && prezzo > 0) {
        annunci.push({
          id: idAnnuncio ? `fb_${idAnnuncio}` : `fb_${annunci.length}_${Date.now()}`,
          titolo,
          descrizione: [luogo, idAnnuncio ? `ID: ${idAnnuncio}` : ''].filter(Boolean).join(' • '),
          prezzo,
          fonte: 'Marketplace'
        })
        continue
      }
    }

    // Test 3: Subito / Generico
    const matchTrattino = linea.match(regexTrattino)
    if (matchTrattino) {
      const titolo = matchTrattino[1]?.trim() || 'Articolo'
      const prezzo = pulisciPrezzoItaliano(matchTrattino[2])
      const extra = matchTrattino[3]?.trim() || ''

      if (prezzo !== null && prezzo > 0) {
        annunci.push({
          id: `subito_${annunci.length}_${Date.now()}`,
          titolo,
          descrizione: extra,
          prezzo,
          fonte: 'Subito'
        })
        continue
      }
    }

    // Test 4: Prezzo su riga singola isolata (es. "1.199 €" dopo "Roma (RM)" e "Super fat bike")
    const matchPrezzo = linea.match(regexPrezzoIsolato)
    if (matchPrezzo && i >= 1) {
      const prezzo = pulisciPrezzoItaliano(matchPrezzo[1])
      const possibileLuogo = linee[i - 1]
      const possibileTitolo = i >= 2 ? linee[i - 2] : linee[i - 1]
      
      if (prezzo !== null && prezzo > 0 && !annunci.some(a => a.prezzo === prezzo && a.titolo === possibileTitolo)) {
        annunci.push({
          id: `subito_multi_${annunci.length}_${Date.now()}`,
          titolo: possibileTitolo,
          descrizione: possibileLuogo !== possibileTitolo ? possibileLuogo : '',
          prezzo,
          fonte: 'Subito'
        })
      }
    }
  }

  return annunci
}

export default function RadarOfferteView({ onCercaSitiEsterni, estensioneInstallata }) {
  const [query, setQuery] = useState('Samsung Galaxy S8')
  const [inputQuery, setInputQuery] = useState('Samsung Galaxy S8')
  const [caricandoAuto, setCaricandoAuto] = useState(false)
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

  // Ricerca automatica dal vivo multi-marketplace
  const cercaAnnunciAutomatico = useCallback(async (testoRicerca) => {
    const q = (testoRicerca || query).trim()
    if (!q || q.length < 2) return
    setCaricandoAuto(true)
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`)
      if (res.ok) {
        const data = await res.json()
        if (data && Array.isArray(data.annunci) && data.annunci.length > 0) {
          const formattati = data.annunci.map((item, idx) => ({
            id: item.id || `live_${idx}_${Date.now()}`,
            titolo: item.titolo || item.title || q,
            prezzo: parseFloat(item.prezzo || item.price) || 0,
            descrizione: item.descrizione || item.description || '',
            immagine: item.immagine || item.image || null,
            url: item.url || item.link || '',
            fonte: item.sorgente || 'eBay'
          }))
          setAnnunci(formattati)
        }
      }
    } catch (err) {
      console.warn('Errore ricerca automatica:', err)
    } finally {
      setCaricandoAuto(false)
    }
  }, [query])

  // Avvio automatico scansione al primo caricamento
  useEffect(() => {
    cercaAnnunciAutomatico('Samsung Galaxy S8')
  }, [])

  // Calcolo Benchmark AI
  const valutazioneAI = useMemo(() => {
    if (!query || query.trim().length < 3) return null
    return valutaOggettoUniversale(query)
  }, [query])

  // Calcolo Benchmark: PRIORITÀ ASSOLUTA agli annunci reali dal vivo se presenti
  const benchmarkVal = useMemo(() => {
    const annunciPuliti = (annunci || []).filter(a => !isAccessorio(a.titolo, a.prezzo) && !isCategoriaDisallineata(a.titolo, query))
    const prezzi = annunciPuliti.map(a => parseFloat(a.prezzo)).filter(p => !isNaN(p) && p >= 15).sort((a, b) => a - b)
    
    // Se ci sono annunci reali, la mediana del mercato dal vivo determina il benchmark
    if (prezzi.length >= 3) {
      const mid = Math.floor(prezzi.length / 2)
      return prezzi.length % 2 !== 0 ? prezzi[mid] : Math.round((prezzi[mid - 1] + prezzi[mid]) / 2)
    }

    // Altrimenti fallback su valutazione AI specifica del modello
    if (valutazioneAI?.schedaOggetto?.prezzoUsatoDettaglio) {
      const match = valutazioneAI.schedaOggetto.prezzoUsatoDettaglio.match(/~(\d+)/)
      if (match) return parseInt(match[1], 10)
    }

    if (prezzi.length > 0) {
      return prezzi[0]
    }

    return 65
  }, [valutazioneAI, annunci, query])

  const targetAcquisto = useMemo(() => Math.round(benchmarkVal * 0.52), [benchmarkVal])
  const tettoMassimo = useMemo(() => Math.round(benchmarkVal * 0.70), [benchmarkVal])

  // Analisi comparativa dinamica di tutti gli annunci
  const annunciAnalizzati = useMemo(() => {
    return confrontaEAnalizzaLotto(annunci || [], query, benchmarkVal)
  }, [annunci, query, benchmarkVal])

  const numeroScartati = useMemo(() => {
    return annunciAnalizzati.filter(a => a.isScartabile).length
  }, [annunciAnalizzati])

  // Filtro e Ordinamento
  const annunciFiltrati = useMemo(() => {
    let res = annunciAnalizzati

    if (filtraAccessori) {
      res = res.filter(a => !a.isScartabile)
    }

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

        {/* Barra di Ricerca Automatica & Azioni Rapide */}
        <form
          onSubmit={(e) => {
            e.preventDefault()
            const q = inputQuery.trim()
            if (q) {
              setQuery(q)
              cercaAnnunciAutomatico(q)
            }
          }}
          className="flex flex-col sm:flex-row gap-2 pt-2 border-t border-slate-800/80"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder="Cosa vuoi cercare? (es. Samsung Galaxy S8, Oppo A74, iPhone 12)..."
              className="w-full pl-9 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs sm:text-sm font-semibold text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all shadow-inner"
            />
          </div>

          <div className="flex items-center gap-1.5">
            <button
              type="submit"
              disabled={caricandoAuto}
              className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white text-xs sm:text-sm font-bold px-4 py-2.5 rounded-xl transition-all shadow-lg shadow-indigo-600/30 cursor-pointer disabled:opacity-50"
            >
              {caricandoAuto ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>Scansione...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  <span>Cerca Annunci</span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={handleIncollaDaAppunti}
              className="flex items-center justify-center gap-1.5 bg-slate-800 hover:bg-slate-700 active:scale-95 text-slate-200 text-xs font-bold px-3 py-2.5 rounded-xl transition-all border border-slate-700"
              title="Incolla annunci copiati da Vinted o Subito"
            >
              <ClipboardPaste className="w-4 h-4 text-indigo-400" /> Incolla
            </button>

            <button
              type="button"
              onClick={() => setMostraBoxIncolla(!mostraBoxIncolla)}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs border border-slate-700"
              title="Apri box di inserimento manuale"
            >
              <Tag className="w-4 h-4" />
            </button>
          </div>
        </form>

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
            👗 Vinted <ExternalLink className="w-3 h-3" />
          </a>
          <a
            href={`https://www.subito.it/annunci-italia/vendita/usato/?q=${encodeURIComponent(query)}&order=price_asc`}
            target="_blank"
            rel="noreferrer"
            className="text-[11px] font-bold px-2 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 hover:bg-amber-500/20 transition-colors inline-flex items-center gap-1"
          >
            🟧 Subito <ExternalLink className="w-3 h-3" />
          </a>
          <a
            href={`https://www.facebook.com/marketplace/search/?query=${encodeURIComponent(query)}`}
            target="_blank"
            rel="noreferrer"
            className="text-[11px] font-bold px-2 py-1 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-300 hover:bg-sky-500/20 transition-colors inline-flex items-center gap-1"
          >
            👥 Marketplace <ExternalLink className="w-3 h-3" />
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
              Filtro Antirumore: <b className="text-emerald-400">{numeroScartati}</b> cover, ricambi e accessori nascosti.
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

                      {ann.descrizione && (
                        <p className="text-[11px] text-slate-400 line-clamp-2 mt-1 italic bg-slate-950/60 px-2 py-1 rounded-lg border border-slate-800/80">
                          <span className="text-slate-500 font-medium not-italic">📝 Note:</span> {ann.descrizione}
                        </p>
                      )}

                      {ann.confrontoMercato && !ann.isScartabile && (
                        <p className="text-[11px] text-indigo-300 font-medium mt-1">
                          {ann.confrontoMercato}
                        </p>
                      )}
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
                      ) : ann.tipo === 'fuori_mercato' ? (
                        <span className="text-rose-400 font-medium flex items-center gap-1">
                          <span>🔴 Fuori Mercato:</span> Chiede troppo ({ann.prezzo}€ vs valore ~{benchmarkVal}€). Trattativa sconsigliata.
                        </span>
                      ) : ann.tipo === 'super_deal' ? (
                        <span className="text-emerald-400 font-bold flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Guadagno netto stimato: +{ann.profitto}€
                        </span>
                      ) : ann.tipo === 'da_trattare' ? (
                        <span className="text-amber-300 font-medium flex items-center gap-1">
                          <span>💡 Offerta realistica (-{ann.sconto}%):</span> <b className="text-amber-400 font-bold font-mono text-xs">{ann.offerta}€</b>
                          <span className="text-[10px] text-slate-400">(Margine target: +{ann.profitto}€)</span>
                        </span>
                      ) : (
                        <span className="text-slate-400">
                          Prezzo allineato al valore di mercato (~{benchmarkVal}€)
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-1.5 self-end sm:self-auto">
                      {!ann.isScartabile && ann.offerta != null && ann.tipo !== 'fuori_mercato' && (
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
