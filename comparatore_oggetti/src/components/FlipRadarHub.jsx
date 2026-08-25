import React, { useState, useEffect, useRef, useImperativeHandle, forwardRef } from 'react'
import {
  Zap,
  TrendingUp,
  DollarSign,
  Copy,
  CheckCircle2,
  AlertTriangle,
  Flame,
  ShieldCheck,
  Trash2,
  PlusCircle,
  Search,
  MessageSquareText,
  Sparkles,
  ShoppingBag,
  Camera,
  Images,
  Loader2,
  X,
  FileText,
  ListPlus,
  Check,
  Info,
  ClipboardPaste,
  Gamepad2,
  Smartphone,
  Ban,
  RotateCcw,
  Gauge,
  Tag,
  Layers,
  HelpCircle,
  Target,
  ExternalLink,
  Send,
  BookmarkPlus,
  Percent,
  Shield,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import Tesseract from 'tesseract.js'
import { preElaboraImmagineCanvas, pulisciTestoOcr } from '../utils/ocrOptimizer.js'
import { valutaOggettoUniversale } from '../utils/aiEvaluator.js'
import { confrontaEAnalizzaLotto, isAccessorio, isCategoriaDisallineata } from '../utils/filtroRumore.js'

function ricalcolaMediana(annunci, query = '') {
  const prezziValidi = (annunci || [])
    .filter(a => !isAccessorio(a.titolo, a.prezzo) && !isCategoriaDisallineata(a.titolo, query))
    .map((a) => parseFloat(a.prezzo))
    .filter((p) => typeof p === 'number' && !isNaN(p) && p >= 15)
    .sort((a, b) => a - b)
  if (prezziValidi.length === 0) return null
  const meta = Math.floor(prezziValidi.length / 2)
  if (prezziValidi.length % 2 !== 0) return Math.round(prezziValidi[meta])
  return Math.round((prezziValidi[meta - 1] + prezziValidi[meta]) / 2)
}

const FlipRadarHub = forwardRef(function FlipRadarHub({ onSearchMarketplace, estensioneInstallata, onCercaSitiEsterni }, ref) {
  const [sezione, setSezione] = useState('analizzatore')
  // Il round-trip del bookmarklet (Subito/Vinted/Marketplace -> torna su Prezzly)
  // ricarica la pagina da zero, non è una navigazione interna alla app: senza
  // salvare qui l'analisi in corso andrebbe persa proprio mentre il risultato
  // sta per arrivare. sessionStorage sopravvive al reload ma non ad altre schede.
  const bozzaSalvata = (() => {
    try {
      return JSON.parse(sessionStorage.getItem('prezzly_flip_bozza') || 'null')
    } catch {
      return null
    }
  })()
  const [testoAnnuncio, setTestoAnnuncio] = useState(bozzaSalvata?.testoAnnuncio || '')
  const [prezzoVenditore, setPrezzoVenditore] = useState(bozzaSalvata?.prezzoVenditore || '')
  const [analisiDettagliata, setAnalisiDettagliata] = useState(null)
  const [scriptSelezionato, setScriptSelezionato] = useState('subito')
  const [copiato, setCopiato] = useState(false)
  const [inCalcolo, setInCalcolo] = useState(false)
  const [affariSalvati, setAffariSalvati] = useState(() => {
    return JSON.parse(localStorage.getItem('prezzly_flip_deals') || '[]')
  })

  const [anteprimaFoto, setAnteprimaFoto] = useState(null)
  const [scansioneOcr, setScansioneOcr] = useState(false)
  const [progressOcr, setProgressOcr] = useState(0)
  
  // Live Marketplace States
  const [annunciRealiLive, setAnnunciRealiLive] = useState([])
  const [caricandoAnnunciLive, setCaricandoAnnunciLive] = useState(false)
  const [medianaRealeLive, setMedianaRealeLive] = useState(null)
  const [filtroOpportunita, setFiltroOpportunita] = useState('tutti')
  const [filtraAccessori, setFiltraAccessori] = useState(true)
  const [copiatoOffertaId, setCopiatoOffertaId] = useState(null)
  
  // Accordion Dropdowns
  const [mostraLiquidita, setMostraLiquidita] = useState(false)
  const [mostraControlli, setMostraControlli] = useState(false)
  const [mostraScript, setMostraScript] = useState(false)

  function copiaMessaggioOffertaRapida(ann, offertaConsigliata, id) {
    const titolo = ann?.titolo || analisiDettagliata?.titoloRilevato || 'questo articolo'
    const prezzo = offertaConsigliata || ann?.prezzo || 30
    const testo = `Ciao! Sono interessato al tuo annuncio per "${titolo}". Se per te va bene, posso concludere subito e pagare a ${prezzo}€. Fammi sapere se possiamo accordarci, grazie!`
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(testo).then(() => {
        setCopiatoOffertaId(id)
        setTimeout(() => setCopiatoOffertaId(null), 3000)
      }).catch(() => {
        prompt('Copia il messaggio di offerta:', testo)
      })
    } else {
      prompt('Copia il messaggio di offerta:', testo)
    }
  }

  function salvaAffareDaAnnuncio(ann, offertaConsigliata, benchmark, profitto) {
    const nuovo = {
      id: 'deal_' + Date.now(),
      nome: ann?.titolo || analisiDettagliata?.titoloRilevato || 'Annuncio',
      prezzoRichiesto: ann?.prezzo != null ? `${ann.prezzo}€` : 'N/D',
      targetAcquisto: `${offertaConsigliata}€`,
      rivenditaStimata: `${benchmark}€`,
      profittoStimato: profitto ? `+${profitto}€` : 'N/D',
      stato: 'in_trattativa',
      data: new Date().toLocaleDateString('it-IT'),
      url: ann?.url || null,
      fonte: ann?.fonte || 'Mercato'
    }
    setAffariSalvati([nuovo, ...affariSalvati])
    setCopiatoOffertaId(`salvato_${ann?.url || ann?.id}`)
    setTimeout(() => setCopiatoOffertaId(null), 2500)
  }
  
  const primoMontRef = useRef(true)
  const textareaRef = useRef(null)
  const resultsRef = useRef(null)
  const inputCameraRef = useRef(null)
  const inputGalleriaRef = useRef(null)

  useEffect(() => {
    localStorage.setItem('prezzly_flip_deals', JSON.stringify(affariSalvati))
  }, [affariSalvati])

  useEffect(() => {
    if (testoAnnuncio) {
      sessionStorage.setItem('prezzly_flip_bozza', JSON.stringify({ testoAnnuncio, prezzoVenditore }))
    } else {
      sessionStorage.removeItem('prezzly_flip_bozza')
    }
  }, [testoAnnuncio, prezzoVenditore])

  // Riceve dall'estensione (via App.jsx) i risultati di Subito/Vinted/Marketplace
  // cercati in background, senza alcun click manuale, e li unisce a quelli eBay.
  useImperativeHandle(ref, () => ({
    aggiungiAnnunciMercato(nuovi) {
      if (!Array.isArray(nuovi) || nuovi.length === 0) return
      setAnnunciRealiLive(prev => {
        const normalizzati = nuovi.map(a => ({ ...a, fonte: a.fonte || a.sorgente || 'Mercato' }))
        const mappa = new Map(prev.map(a => [a.url || `${a.fonte}-${a.titolo}-${a.prezzo}`, a]))
        for (const a of normalizzati) {
          mappa.set(a.url || `${a.fonte}-${a.titolo}-${a.prezzo}`, a)
        }
        const uniti = Array.from(mappa.values())
        setMedianaRealeLive(ricalcolaMediana(uniti))
        return uniti
      })
    }
  }))

  // AUTO-ANALISI IN TEMPO REALE AL CAMBIO DEL TESTO (Debounced 300ms)
  useEffect(() => {
    if (!testoAnnuncio || testoAnnuncio.trim().length < 4) {
      setAnalisiDettagliata(null)
      return
    }
    // Al primo mount con una bozza ripristinata (dopo un reload da bookmarklet)
    // non è un nuovo testo digitato dall'utente: non azzeriamo i risultati live,
    // che potrebbero già essere arrivati (o arrivare a momenti) dal bookmarklet.
    const eraPrimoMontConBozza = primoMontRef.current && !!bozzaSalvata?.testoAnnuncio
    primoMontRef.current = false
    const timer = setTimeout(() => {
      eseguiValutazione(testoAnnuncio, false, eraPrimoMontConBozza)
    }, eraPrimoMontConBozza ? 0 : 300)
    return () => clearTimeout(timer)
  }, [testoAnnuncio, prezzoVenditore])

  // Incolla sicuro dagli appunti
  async function incollaDagliAppunti() {
    try {
      if (navigator.clipboard && navigator.clipboard.readText) {
        const text = await navigator.clipboard.readText()
        if (text && text.trim().length > 0) {
          setTestoAnnuncio(text)
          eseguiValutazione(text, true)
          return
        }
      }
    } catch (e) {
      console.warn('Clipboard readText fallback', e)
    }
    if (textareaRef.current) {
      textareaRef.current.focus()
      alert('Tieni premuto nel riquadro e seleziona "Incolla"')
    }
  }

  function handleFotoSelezionata(file) {
    if (!file) return
    const url = URL.createObjectURL(file)
    setAnteprimaFoto(url)
    eseguiOcr(file)
  }

  async function eseguiOcr(file) {
    setScansioneOcr(true)
    setProgressOcr(0)
    try {
      const blobOttimizzato = await preElaboraImmagineCanvas(file)
      const risultato = await Tesseract.recognize(
        blobOttimizzato,
        'ita+eng',
        {
          logger: m => {
            if (m.status === 'recognizing text') {
              setProgressOcr(Math.round(m.progress * 100))
            }
          }
        }
      )
      
      const testoGrezzo = risultato.data.text || ''
      const testoPulito = pulisciTestoOcr(testoGrezzo)

      if (testoPulito && testoPulito.trim().length > 3) {
        setTestoAnnuncio(testoPulito)
        eseguiValutazione(testoPulito, true)
      } else {
        alert('Nessun testo nitido trovato nello screenshot. Incolla il testo dell\'annuncio manualmente.')
      }
    } catch (err) {
      console.error(err)
      alert('Errore lettura immagine. Riprova con uno screenshot nitido.')
    } finally {
      setScansioneOcr(false)
    }
  }

  function rimuoviFoto() {
    setAnteprimaFoto(null)
    if (inputCameraRef.current) inputCameraRef.current.value = ''
    if (inputGalleriaRef.current) inputGalleriaRef.current.value = ''
  }

  /**
   * ESEGUI VALUTAZIONE ISTANTANEA (0 Millisecondi) + RICERCA LIVE IN BACKGROUND
   */
  function eseguiValutazione(testo, shouldScroll = true, skipReset = false) {
    const raw = testo !== undefined ? testo : testoAnnuncio
    if (!raw || !raw.trim()) {
      return
    }

    let queryRicerca = raw.split(/\r?\n/)[0].replace(/(?:\d{1,3}(?:\.\d{3})+|\d+)(?:[.,]\d{1,2})?\s*(?:€|euro|eur)/gi, '').trim()

    // 1. RENDER ISTANTANEO A 0 MILLISECONDI
    try {
      const valutazioneLocale = valutaOggettoUniversale(raw, prezzoVenditore ? parseFloat(prezzoVenditore) : null)
      if (valutazioneLocale) {
        setAnalisiDettagliata(valutazioneLocale)
        queryRicerca = valutazioneLocale.titoloRilevato || queryRicerca
        if (shouldScroll) {
          setTimeout(() => {
            try {
              if (resultsRef.current) {
                resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
              }
            } catch (err) {
              // Ignore scrolling error on older browsers
            }
          }, 50)
        }
      }
    } catch (e) {
      console.warn('Errore valutazione locale:', e)
    }

    setInCalcolo(false)

    // 2. Ricerca Live in Background (Non-Bloccante): eBay via API server-side,
    // Subito/Vinted/Marketplace via l'estensione (se installata) in schede invisibili.
    setCaricandoAnnunciLive(true)
    if (!skipReset) {
      setAnnunciRealiLive([])
      setMedianaRealeLive(null)
    }

    onCercaSitiEsterni?.(queryRicerca)

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 2500)

      fetch(`/api/search?q=${encodeURIComponent(queryRicerca)}`, { signal: controller.signal })
        .then(res => (res && res.ok ? res.json() : null))
        .then(dataSearch => {
          clearTimeout(timeoutId)
          if (dataSearch && dataSearch.annunci && Array.isArray(dataSearch.annunci) && dataSearch.annunci.length > 0) {
            setAnnunciRealiLive(prev => {
              const mappa = new Map(prev.map(a => [a.url || `${a.fonte}-${a.titolo}-${a.prezzo}`, a]))
              for (const a of dataSearch.annunci) {
                mappa.set(a.url || `${a.fonte}-${a.titolo}-${a.prezzo}`, a)
              }
              const uniti = Array.from(mappa.values())
              const nuovaMediana = ricalcolaMediana(uniti, queryRicerca)
              if (nuovaMediana) {
                setMedianaRealeLive(nuovaMediana)
                setAnalisiDettagliata(prev => {
                  if (!prev) return prev
                  const targetVal = Math.round(nuovaMediana * 0.52)
                  const maxVal = Math.round(nuovaMediana * 0.70)
                  const profit = nuovaMediana - targetVal
                  const roi = Math.round((profit / targetVal) * 100)
                  return {
                    ...prev,
                    valoreRivenditaUsato: nuovaMediana,
                    strategiaFlipping: [
                      { voce: 'Offerta Target d\'Acquisto', valore: `${targetVal}€`, badge: 'DA INVIARE', highlight: true },
                      { voce: 'Tetto Massimo da non superare', valore: `${maxVal}€`, nota: `Oltre i ${maxVal}€ il margine scende` },
                      { voce: 'Valore Reale Rivendita Usato', valore: `~${nuovaMediana}€`, nota: 'Prezzo mediano basato su annunci reali dal vivo' },
                      { voce: 'Profitto Netto Stimato', valore: `+${profit}€`, nota: `ROI: +${roi}%`, isProfit: true }
                    ]
                  }
                })
              }
              return uniti
            })
          }
        })
        .catch(() => {})
        .finally(() => {
          setCaricandoAnnunciLive(false)
        })
    } catch (err) {
      setCaricandoAnnunciLive(false)
    }
  }

  function generaScript() {
    if (!analisiDettagliata) return ''
    const d = analisiDettagliata
    if (scriptSelezionato === 'subito') {
      return d.scriptTrattativa?.subito || `Ciao! Se è perfettamente funzionante, posso offrirti ${d.offertaTarget}€ e fare ritiro a mano oggi stesso in contanti a Torino. Fammi sapere!`
    } else if (scriptSelezionato === 'whatsapp') {
      return d.scriptTrattativa?.whatsapp || `Buongiorno! Sono di Torino e posso fare ritiro a mano oggi a ${d.offertaTarget}€ in contanti sul posto. Fammi sapere se posso passare!`
    } else if (scriptSelezionato === 'counter') {
      return `Capisco la tua richiesta! Il massimo a cui posso arrivare per chiudere subito oggi in contanti sul posto è ${d.tettoMassimo}€. Se cambi idea o non concludi con altri, la mia offerta rimane valida! Buona giornata.`
    }
    return ''
  }

  function copiaScript() {
    const text = generaScript()
    if (!text) return
    navigator.clipboard.writeText(text).then(() => {
      setCopiato(true)
      setTimeout(() => setCopiato(false), 2000)
    })
  }

  function salvaNelTracker() {
    if (!analisiDettagliata) return
    const d = analisiDettagliata
    const nuovo = {
      id: 'deal_' + Date.now(),
      nome: d.titoloRilevato,
      prezzoRichiesto: d.prezzoRichiesto,
      targetAcquisto: d.offertaTarget,
      rivenditaStimata: d.valoreRivenditaUsato,
      profittoStimato: d.profittoNetto,
      stato: 'in_trattativa',
      data: new Date().toLocaleDateString('it-IT')
    }
    setAffariSalvati([nuovo, ...affariSalvati])
    setSezione('tracker')
  }

  return (
    <div className="space-y-5 animate-in fade-in duration-300">
      
      {/* Sotto-Navigazione Hub */}
      <div className="flex bg-slate-900/80 p-1 rounded-xl border border-slate-800">
        <button
          type="button"
          onClick={() => setSezione('analizzatore')}
          className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
            sezione === 'analizzatore' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Zap className="w-3.5 h-3.5" /> Analizzatore & OCR
        </button>
        <button
          type="button"
          onClick={() => setSezione('tracker')}
          className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
            sezione === 'tracker' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <DollarSign className="w-3.5 h-3.5" /> Miei Affari ({affariSalvati.length})
        </button>
      </div>

      {sezione === 'analizzatore' && (
        <div className="space-y-4">
          
          {/* Scanner Foto / Screenshot OCR */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                <Sparkles className="w-3 h-3" /> SCANNER FOTO & SCREENSHOT
              </span>
              <span className="text-[10px] text-slate-400">Lettura automatica OCR</span>
            </div>

            {anteprimaFoto ? (
              <div className="relative overflow-hidden rounded-xl border border-slate-700 bg-slate-950">
                <img src={anteprimaFoto} alt="Anteprima" className="h-40 w-full object-contain bg-slate-950" />
                <button
                  type="button"
                  onClick={rimuoviFoto}
                  className="absolute right-2 top-2 rounded-full bg-slate-900/90 p-1.5 text-slate-300 hover:text-white"
                  title="Rimuovi"
                >
                  <X className="h-4 w-4" />
                </button>
                {scansioneOcr && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-slate-950/85 text-slate-200 p-4">
                    <Loader2 className="h-6 w-6 animate-spin text-emerald-400" />
                    <span className="font-bold text-xs">Lettura e analisi in corso ({progressOcr}%)...</span>
                    <div className="w-48 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div className="bg-emerald-500 h-full transition-all duration-200" style={{ width: `${progressOcr}%` }}></div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-2.5">
                <label className="flex cursor-pointer flex-col items-center gap-2 rounded-xl border border-slate-700/80 bg-slate-800/60 p-3 text-center transition-all hover:border-emerald-500 hover:bg-slate-800">
                  <Camera className="h-5 w-5 text-emerald-400" />
                  <div>
                    <span className="text-xs font-bold text-slate-200 block">Fotocamera</span>
                    <small className="text-[10px] text-slate-400">Foto a oggetti o scatole</small>
                  </div>
                  <input ref={inputCameraRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={(e) => handleFotoSelezionata(e.target.files?.[0])} />
                </label>
                <label className="flex cursor-pointer flex-col items-center gap-2 rounded-xl border border-slate-700/80 bg-slate-800/60 p-3 text-center transition-all hover:border-indigo-500 hover:bg-slate-800">
                  <Images className="h-5 w-5 text-indigo-400" />
                  <div>
                    <span className="text-xs font-bold text-slate-200 block">Screenshot</span>
                    <small className="text-[10px] text-slate-400">Da Subito/Marketplace</small>
                  </div>
                  <input ref={inputGalleriaRef} type="file" accept="image/*" className="hidden" onChange={(e) => handleFotoSelezionata(e.target.files?.[0])} />
                </label>
              </div>
            )}
          </div>

          {/* Box Inserimento Testo */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-indigo-400" /> Incolla Qualsiasi Titolo o Annuncio
              </span>
              <div className="flex gap-1.5">
                {testoAnnuncio && (
                  <button
                    type="button"
                    onClick={() => { setTestoAnnuncio(''); setPrezzoVenditore(''); setAnalisiDettagliata(null); }}
                    className="inline-flex items-center gap-1 text-[10px] text-slate-400 hover:text-slate-200 bg-slate-800 px-2 py-1 rounded"
                    title="Pulisci testo"
                  >
                    <RotateCcw className="w-3 h-3" /> Pulisci
                  </button>
                )}
                <button
                  type="button"
                  onClick={incollaDagliAppunti}
                  className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-300 bg-indigo-500/20 hover:bg-indigo-500/30 border border-indigo-500/30 px-2.5 py-1 rounded-lg transition-colors active:scale-95"
                >
                  <ClipboardPaste className="w-3.5 h-3.5" /> Incolla da Appunti
                </button>
              </div>
            </div>

            <textarea
              ref={textareaRef}
              value={testoAnnuncio}
              onChange={(e) => setTestoAnnuncio(e.target.value)}
              placeholder="Incolla l'annuncio qui (es: Nintendo Switch 1 con Joycon extra e giochi, iPhone 12, GPS Meilan...)"
              rows="3"
              className="w-full resize-none rounded-xl border border-slate-700 bg-slate-800/80 px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-500 font-sans text-xs leading-relaxed"
            />

            {/* Prezzo Richiesto dal Venditore */}
            <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/80 px-3.5 py-2.5">
              <Tag className="w-3.5 h-3.5 text-amber-400 shrink-0" />
              <span className="text-xs font-semibold text-slate-300 whitespace-nowrap">Prezzo richiesto dal venditore:</span>
              <input
                type="number"
                inputMode="decimal"
                min="0"
                value={prezzoVenditore}
                onChange={(e) => setPrezzoVenditore(e.target.value)}
                placeholder="es. 150"
                className="flex-1 min-w-0 bg-transparent text-sm text-slate-100 placeholder-slate-500 outline-none font-mono"
              />
              <span className="text-xs text-slate-400 shrink-0">€</span>
            </div>

            {/* Quick Presets */}
            <div className="flex flex-wrap gap-1.5">
              <span className="text-[10px] text-slate-500 self-center">Esempi:</span>
              <button
                type="button"
                onClick={() => {
                  const t = 'Nintendo Switch 1 già formattata con tutti gli accessori originali e la scatola + micro SD Nintendo + coppia Joycon rosa e verde con scatola originale + gioco "Arms" su cartuccia + gioco "1 2 Switch" su cartuccia'
                  setTestoAnnuncio(t)
                  eseguiValutazione(t, true)
                }}
                className="text-[10px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-0.5 rounded-full border border-slate-700"
              >
                🕹️ Bundle Switch + Joycon + Giochi
              </button>
              <button
                type="button"
                onClick={() => {
                  const t = 'iPhone 12 128GB Nero batteria 82% schermo perfetto con segni di usura sulla scocca'
                  setTestoAnnuncio(t)
                  eseguiValutazione(t, true)
                }}
                className="text-[10px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-0.5 rounded-full border border-slate-700"
              >
                📱 iPhone 12 128GB
              </button>
              <button
                type="button"
                onClick={() => {
                  const t = 'Navihood GPS Meilan Mini preto Bike Computer'
                  setTestoAnnuncio(t)
                  eseguiValutazione(t, true)
                }}
                className="text-[10px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-0.5 rounded-full border border-slate-700"
              >
                🚲 GPS Bici Meilan
              </button>
            </div>

            <button
              type="button"
              onClick={() => eseguiValutazione(undefined, true)}
              disabled={inCalcolo}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-emerald-600 py-3 text-sm font-bold text-white shadow-lg active:scale-98 transition-transform disabled:opacity-50"
            >
              {inCalcolo ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
              <span>⚡ Calcola Valore & Margine di Guadagno</span>
            </button>
          </div>

          {/* Risultato dell'Analisi Dettagliata (Executive Layout) */}
          {analisiDettagliata && (
            <div ref={resultsRef} className="space-y-4 animate-in slide-in-from-bottom-2 duration-300">
              
              {/* 1. SEZIONE SCHEDA OGGETTO & PREZZI DI MERCATO */}
              <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/90 space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-base">📋</span>
                  <h3 className="text-sm font-bold text-slate-100">{analisiDettagliata.titoloRilevato}</h3>
                </div>

                <div className="space-y-2 text-xs divide-y divide-slate-800/80">
                  <div className="pt-1 flex flex-col gap-0.5">
                    <span className="text-slate-400 font-medium">Modello Rilevato:</span>
                    <span className="text-slate-200 font-semibold">{analisiDettagliata.schedaOggetto?.tipologia || analisiDettagliata.titoloRilevato}</span>
                  </div>

                  <div className="pt-2 flex flex-col gap-0.5">
                    <span className="text-slate-400 font-medium">Fascia di Mercato:</span>
                    <span className="text-slate-200 font-semibold">{analisiDettagliata.schedaOggetto?.fasciaMercato || 'Smartphone Usato'}</span>
                  </div>

                  <div className="pt-2 flex justify-between items-center">
                    <span className="text-slate-400 font-medium">Media Annunci Usato dal Vivo:</span>
                    <b className="font-mono text-indigo-300">
                      ~{medianaRealeLive || (analisiDettagliata?.valoreRivenditaUsato || 65)}€
                    </b>
                  </div>

                  <div className="pt-2 flex justify-between items-center">
                    <span className="text-slate-400 font-medium">Prezzo Consigliato Rivendita Rapida:</span>
                    <b className="font-mono text-emerald-400">
                      ~{medianaRealeLive || (analisiDettagliata?.valoreRivenditaUsato || 65)}€
                    </b>
                  </div>
                </div>
              </div>



              {/* 3. TENDINA: GIUDIZIO LIQUIDITÀ & CONSIGLIO OPERATIVO */}
              <div className="rounded-2xl border border-slate-800 bg-slate-900/90 overflow-hidden transition-all">
                <button
                  type="button"
                  onClick={() => setMostraLiquidita(!mostraLiquidita)}
                  className="w-full p-3.5 flex items-center justify-between gap-2 text-left hover:bg-slate-800/50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-base">⚠️</span>
                    <h3 className="text-xs sm:text-sm font-bold text-slate-200">Giudizio Liquidità & Consiglio Operativo</h3>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-extrabold bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded">
                      {analisiDettagliata?.liquidita?.livello || 'Media'}
                    </span>
                    {mostraLiquidita ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                  </div>
                </button>

                {mostraLiquidita && (
                  <div className="p-4 pt-1 border-t border-slate-800/80 space-y-2 text-xs animate-in fade-in">
                    <p className="text-slate-300 leading-relaxed bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                      💡 <b>Consiglio Operativo:</b> {analisiDettagliata?.liquidita?.consiglioOperativo || 'Effettua una valutazione accurata sul posto.'}
                    </p>
                    
                    {analisiDettagliata?.liquidita?.benchmark && (
                      <div className="text-[11px] text-slate-400 pt-0.5">
                        📊 <b>Benchmark di mercato:</b> {analisiDettagliata.liquidita.benchmark}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* 4. TENDINA: CONTROLLI ANTI-FREGATURA DAL VIVO */}
              {Array.isArray(analisiDettagliata?.controlliDalVivo) && analisiDettagliata.controlliDalVivo.length > 0 && (
                <div className="rounded-2xl border border-slate-800 bg-slate-900/90 overflow-hidden transition-all">
                  <button
                    type="button"
                    onClick={() => setMostraControlli(!mostraControlli)}
                    className="w-full p-3.5 flex items-center justify-between gap-2 text-left hover:bg-slate-800/50 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-base">🛡️</span>
                      <h3 className="text-xs sm:text-sm font-bold text-slate-200">Controlli Anti-Fregatura dal Vivo</h3>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-slate-400">
                        {analisiDettagliata.controlliDalVivo.length} Verifiche
                      </span>
                      {mostraControlli ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                    </div>
                  </button>

                  {mostraControlli && (
                    <div className="p-4 pt-1 border-t border-slate-800/80 space-y-2 text-xs text-slate-300 animate-in fade-in">
                      {analisiDettagliata.controlliDalVivo.map((tip, idx) => (
                        <div key={idx} className="flex items-start gap-2 bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80">
                          <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                          <span>{tip}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* 5. TENDINA: SCRIPT DI TRATTATIVA VELOCE */}
              <div className="rounded-2xl border border-slate-800 bg-slate-900/90 overflow-hidden transition-all">
                <button
                  type="button"
                  onClick={() => setMostraScript(!mostraScript)}
                  className="w-full p-3.5 flex items-center justify-between gap-2 text-left hover:bg-slate-800/50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-base">💬</span>
                    <h3 className="text-xs sm:text-sm font-bold text-slate-200">Script di Trattativa per il Venditore</h3>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-indigo-400 font-bold bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                      1-Click Copy
                    </span>
                    {mostraScript ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                  </div>
                </button>

                {mostraScript && (
                  <div className="p-4 pt-1 border-t border-slate-800/80 space-y-3 animate-in fade-in">
                    <div className="flex gap-1.5 overflow-x-auto pb-1">
                      <button
                        type="button"
                        onClick={() => setScriptSelezionato('subito')}
                        className={`text-[11px] font-semibold px-2.5 py-1 rounded-lg transition-colors whitespace-nowrap ${
                          scriptSelezionato === 'subito' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        Subito / Ritiro a Mano
                      </button>
                      <button
                        type="button"
                        onClick={() => setScriptSelezionato('whatsapp')}
                        className={`text-[11px] font-semibold px-2.5 py-1 rounded-lg transition-colors whitespace-nowrap ${
                          scriptSelezionato === 'whatsapp' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        WhatsApp Diretto
                      </button>
                      <button
                        type="button"
                        onClick={() => setScriptSelezionato('counter')}
                        className={`text-[11px] font-semibold px-2.5 py-1 rounded-lg transition-colors whitespace-nowrap ${
                          scriptSelezionato === 'counter' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        Controproposta
                      </button>
                    </div>

                    <div className="p-3.5 rounded-xl bg-slate-950/90 border border-slate-800 text-xs text-slate-200 leading-relaxed select-all whitespace-pre-wrap font-sans">
                      {generaScript()}
                    </div>

                    <button
                      type="button"
                      onClick={copiaScript}
                      className={`w-full flex items-center justify-center gap-2 rounded-xl py-2.5 text-xs font-bold transition-all ${
                        copiato ? 'bg-emerald-600 text-white' : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow'
                      }`}
                    >
                      {copiato ? (
                        <>
                          <CheckCircle2 className="w-4 h-4" /> Messaggio Copiato negli Appunti!
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" /> Copia Messaggio per il Venditore
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>

              {/* 6. RADAR OPPORTUNITÀ & ANNUNCI SU CUI FARE OFFERTA */}
              {(() => {
                const queryCorrente = analisiDettagliata?.titoloRilevato || oggettoManual?.nome || ''
                const benchmarkVal = medianaRealeLive || (() => {
                  if (analisiDettagliata?.valoreRivenditaUsato) return analisiDettagliata.valoreRivenditaUsato
                  if (analisiDettagliata?.schedaOggetto?.prezzoUsatoDettaglio) {
                    const m = analisiDettagliata.schedaOggetto.prezzoUsatoDettaglio.match(/~(\d+)/) || analisiDettagliata.schedaOggetto.prezzoUsatoDettaglio.match(/(\d+)/)
                    if (m) return parseInt(m[1], 10)
                  }
                  return 65
                })()

                const annunciElaborati = confrontaEAnalizzaLotto(annunciRealiLive || [], queryCorrente, benchmarkVal)

                const numeroScartati = annunciElaborati.filter(a => a.isScartabile).length
                const annunciFiltratiRumore = filtraAccessori ? annunciElaborati.filter(a => !a.isScartabile) : annunciElaborati

                const superDeals = annunciFiltratiRumore.filter(a => a.tipo === 'super_deal')
                const trattabili = annunciFiltratiRumore.filter(a => a.tipo === 'da_trattare')
                const listaMostrata = annunciFiltratiRumore.filter(a => {
                  if (filtroOpportunita === 'affari') return a.tipo === 'super_deal'
                  if (filtroOpportunita === 'trattabili') return a.tipo === 'super_deal' || a.tipo === 'da_trattare'
                  return true
                })

                return (
                  <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/90 space-y-3.5">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                      <div className="flex items-center gap-2">
                        <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                          <Target className="w-5 h-5" />
                        </div>
                        <div>
                          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                            Annunci su cui fare Offerta
                            {superDeals.length > 0 && (
                              <span className="text-[10px] font-extrabold bg-emerald-500 text-slate-950 px-2 py-0.5 rounded-full animate-pulse">
                                {superDeals.length} SUPER AFFARI
                              </span>
                            )}
                          </h3>
                          <p className="text-[11px] text-slate-400">Radar annunci dal vivo con proposta di trattativa immediata</p>
                        </div>
                      </div>

                      {benchmarkVal && (
                        <div className="flex items-center gap-1.5 self-start sm:self-auto">
                          <span className="text-[10px] text-slate-400 font-medium">Valore Riferimento Telefono:</span>
                          <span className="text-xs font-mono font-extrabold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                            ~{benchmarkVal}€
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Banner Antirumore Accessori */}
                    {numeroScartati > 0 && (
                      <div className="flex items-center justify-between gap-2 p-2 rounded-xl bg-slate-950/80 border border-slate-800 text-[11px]">
                        <div className="flex items-center gap-1.5">
                          <Shield className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                          <span className="text-slate-300">
                            Filtro Antirumore: <b className="text-emerald-400">{numeroScartati}</b> cover, ricambi e accessori nascosti.
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => setFiltraAccessori(!filtraAccessori)}
                          className="text-[10px] font-bold text-slate-400 hover:text-slate-200 inline-flex items-center gap-1 underline"
                        >
                          {filtraAccessori ? <><Eye className="w-3 h-3" /> Mostra tutti</> : <><EyeOff className="w-3 h-3" /> Nascondi accessori</>}
                        </button>
                      </div>
                    )}

                    {caricandoAnnunciLive ? (
                      <div className="flex items-center justify-center gap-2 py-6 text-xs text-slate-400">
                        <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                        <span>Scansione e calcolo offerte in tempo reale da Vinted, Subito ed eBay...</span>
                      </div>
                    ) : annunciFiltratiRumore.length > 0 ? (
                      <div className="space-y-3">
                        {/* Filtri Rapidi */}
                        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
                          <button
                            type="button"
                            onClick={() => setFiltroOpportunita('tutti')}
                            className={`text-[11px] font-bold px-3 py-1.5 rounded-lg border transition-all whitespace-nowrap ${
                              filtroOpportunita === 'tutti'
                                ? 'bg-indigo-600 text-white border-indigo-500 shadow-sm'
                                : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                            }`}
                          >
                            Dispositivi ({annunciFiltratiRumore.length})
                          </button>
                          <button
                            type="button"
                            onClick={() => setFiltroOpportunita('affari')}
                            className={`text-[11px] font-bold px-3 py-1.5 rounded-lg border transition-all whitespace-nowrap flex items-center gap-1 ${
                              filtroOpportunita === 'affari'
                                ? 'bg-emerald-600 text-white border-emerald-500 shadow-sm'
                                : 'bg-slate-950 text-emerald-400/90 border-emerald-500/30 hover:bg-emerald-500/10'
                            }`}
                          >
                            🔥 Super Affari ({superDeals.length})
                          </button>
                          <button
                            type="button"
                            onClick={() => setFiltroOpportunita('trattabili')}
                            className={`text-[11px] font-bold px-3 py-1.5 rounded-lg border transition-all whitespace-nowrap flex items-center gap-1 ${
                              filtroOpportunita === 'trattabili'
                                ? 'bg-amber-600 text-white border-amber-500 shadow-sm'
                                : 'bg-slate-950 text-amber-400/90 border-amber-500/30 hover:bg-amber-500/10'
                            }`}
                          >
                            💬 Da Trattare ({trattabili.length})
                          </button>
                        </div>

                        {/* Griglia / Lista Annunci */}
                        <div className="space-y-2.5">
                          {listaMostrata.map((ann, i) => {
                            const isCopiato = copiatoOffertaId === ann.idUnico
                            const isSalvato = copiatoOffertaId === `salvato_${ann.idUnico}`
                            const fonte = String(ann?.fonte || 'Mercato')

                            let iconaFonte = '🌐'
                            let badgeColoreFonte = 'text-slate-300 bg-slate-800'
                            if (fonte.includes('Vinted')) { iconaFonte = '👗'; badgeColoreFonte = 'text-teal-300 bg-teal-500/10 border-teal-500/20' }
                            else if (fonte.includes('Subito')) { iconaFonte = '🟧'; badgeColoreFonte = 'text-amber-300 bg-amber-500/10 border-amber-500/20' }
                            else if (fonte.includes('eBay')) { iconaFonte = '🔵'; badgeColoreFonte = 'text-blue-300 bg-blue-500/10 border-blue-500/20' }
                            else if (fonte.includes('Marketplace')) { iconaFonte = '👥'; badgeColoreFonte = 'text-sky-300 bg-sky-500/10 border-sky-500/20' }

                            return (
                              <div
                                key={ann.idUnico || i}
                                className={`p-3 rounded-xl border transition-all ${
                                  ann.isScartabile
                                    ? 'bg-slate-950/40 border-slate-800/60 opacity-60'
                                    : ann.tipo === 'super_deal'
                                    ? 'bg-emerald-950/20 border-emerald-500/40 hover:border-emerald-500/70 shadow-sm'
                                    : ann.tipo === 'da_trattare'
                                    ? 'bg-slate-950/80 border-amber-500/30 hover:border-amber-500/60'
                                    : 'bg-slate-950/60 border-slate-800/80'
                                }`}
                              >
                                <div className="flex items-start justify-between gap-3">
                                  {ann.immagine ? (
                                    <div className="relative shrink-0">
                                      <img
                                        src={ann.immagine}
                                        alt={ann.titolo}
                                        className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl object-cover bg-slate-950 border border-slate-800/80 shadow-sm"
                                        onError={(e) => { e.target.parentElement.style.display = 'none' }}
                                      />
                                    </div>
                                  ) : (
                                    <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-slate-950 border border-slate-800/80 flex items-center justify-center text-xl shrink-0 select-none">
                                      📱
                                    </div>
                                  )}

                                  <div className="space-y-1 flex-1 min-w-0">
                                    <div className="flex items-center gap-1.5 flex-wrap">
                                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border inline-flex items-center gap-1 ${badgeColoreFonte}`}>
                                        <span>{iconaFonte}</span> {fonte}
                                      </span>

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

                                    <h4 className="text-xs font-semibold text-slate-200 line-clamp-2 mt-1">
                                      {String(ann?.titolo || 'Articolo')}
                                    </h4>

                                    {ann.descrizione && (
                                      <p className="text-[10px] text-slate-400 line-clamp-2 mt-1 italic bg-slate-950/60 px-2 py-0.5 rounded border border-slate-800/80">
                                        <span className="text-slate-500 font-medium not-italic">📝 Note:</span> {ann.descrizione}
                                      </p>
                                    )}

                                    {ann.confrontoMercato && !ann.isScartabile && (
                                      <p className="text-[10px] text-indigo-300 font-medium mt-1">
                                        {ann.confrontoMercato}
                                      </p>
                                    )}
                                  </div>

                                  <div className="text-right shrink-0">
                                    <span className="text-[10px] text-slate-400 block">Prezzo Richiesto:</span>
                                    <b className="text-base font-extrabold text-slate-100 font-mono">
                                      {ann.prezzo != null ? `${ann.prezzo}€` : 'N/D'}
                                    </b>
                                  </div>
                                </div>

                                {/* Banner Proposta Offerta e Margine */}
                                <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
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
                                        <CheckCircle2 className="w-3.5 h-3.5" /> Margine netto stimato: +{ann.profitto}€
                                      </span>
                                    ) : ann.tipo === 'da_trattare' ? (
                                      <span className="text-amber-300 font-medium flex items-center gap-1">
                                        <span>💡 Offerta realistica (-{ann.sconto}%):</span> <b className="text-amber-400 font-bold font-mono text-xs">{ann.offerta}€</b>
                                        <span className="text-[10px] text-slate-400">(Margine target: +{ann.profitto}€)</span>
                                      </span>
                                    ) : (
                                      <span className="text-slate-400">
                                        In linea con il valore di mercato (~{benchmarkVal}€)
                                      </span>
                                    )}
                                  </div>

                                  {/* Bottoni Azione Rapida */}
                                  <div className="flex items-center gap-1.5 self-end sm:self-auto">
                                    {!ann.isScartabile && ann.offerta != null && ann.tipo !== 'fuori_mercato' && (
                                      <button
                                        type="button"
                                        onClick={() => copiaMessaggioOffertaRapida(ann, ann.offerta, ann.idUnico)}
                                        className={`text-[11px] font-bold px-2.5 py-1 rounded-lg border transition-all flex items-center gap-1 ${
                                          isCopiato
                                            ? 'bg-emerald-600 text-white border-emerald-500'
                                            : 'bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border-indigo-500/30 active:scale-95'
                                        }`}
                                        title="Copia messaggio di offerta e trattativa"
                                      >
                                        {isCopiato ? (
                                          <>
                                            <Check className="w-3 h-3" /> Offerta Copiata!
                                          </>
                                        ) : (
                                          <>
                                            <Copy className="w-3 h-3" /> Copia Offerta ({ann.offerta}€)
                                          </>
                                        )}
                                      </button>
                                    )}

                                    <button
                                      type="button"
                                      onClick={() => salvaAffareDaAnnuncio(ann, ann.offerta, benchmarkVal, ann.profitto)}
                                      className={`text-[11px] font-bold p-1 rounded-lg border transition-all ${
                                        isSalvato
                                          ? 'bg-emerald-600 text-white border-emerald-500'
                                          : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'
                                      }`}
                                      title="Salva nei miei affari"
                                    >
                                      {isSalvato ? <Check className="w-3.5 h-3.5" /> : <PlusCircle className="w-3.5 h-3.5" />}
                                    </button>

                                    {ann.url && (
                                      <a
                                        href={ann.url}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-[11px] font-bold p-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors inline-flex items-center"
                                        title="Apri annuncio sul portale"
                                      >
                                        <ExternalLink className="w-3.5 h-3.5" />
                                      </a>
                                    )}
                                  </div>
                                </div>
                              </div>
                            )
                          })}
                        </div>

                        <p className="text-[10px] text-slate-400 text-center pt-1">
                          Trovati <b className="text-slate-200">{annunciFiltratiRumore.length}</b> dispositivi reali. Clicca <b>"Copia Offerta"</b> per incollare subito la proposta al venditore.
                        </p>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-400 text-center py-4 bg-slate-950/60 rounded-xl border border-slate-800">
                        Nessun annuncio attivo trovato al momento su eBay per questa dicitura esatta. Usa i link diretti sotto per cercare su Subito e Vinted!
                      </p>
                    )}
                  </div>
                )
              })()}

              {/* 7. RICERCA LIVE SUI PORTALI */}
              <div className="p-3.5 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-2.5">
                <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                  <Search className="w-3.5 h-3.5 text-indigo-400" /> Cerca Annunci Simili Attivi Live
                </span>

                {estensioneInstallata ? (
                  <p className="text-[11px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-lg px-2.5 py-2">
                    ✓ Estensione attiva: Subito, Vinted e Marketplace vengono cercati automaticamente e uniti ai "Risultati Reali dal Vivo" qui sopra, nessun click necessario.
                  </p>
                ) : (
                  <>
                    <p className="text-[10px] text-slate-500">
                      Apri un sito qui sotto, poi sui risultati tocca il <a href="/bookmarklet.html" className="text-indigo-400 hover:text-indigo-300">bookmarklet</a> salvato: il risultato torna da solo qui, senza copia-incolla. (Da PC con Chrome/Edge, l'<a href="/estensione.html" className="text-indigo-400 hover:text-indigo-300">estensione</a> lo fa tutto da sola, zero tap.)
                    </p>
                    <div className="grid grid-cols-2 gap-2">
                      {/* Niente 'noopener/noreferrer' qui: il bookmarklet sui risultati di
                          questi siti deve poter ritrovare/riusare QUESTA scheda (window.name
                          'prezzlyTab') per consegnare il risultato senza aprirne una nuova vuota. */}
                      <button
                        type="button"
                        onClick={() => window.open(`https://www.subito.it/annunci-piemonte/vendita/usato/torino/?q=${encodeURIComponent(analisiDettagliata.titoloRilevato)}`, '_blank')}
                        className="flex items-center justify-center gap-1.5 p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700 transition-colors"
                      >
                        <span className="text-amber-400">🟧</span> Subito (Torino)
                      </button>
                      <button
                        type="button"
                        onClick={() => window.open(`https://www.vinted.it/catalog?search_text=${encodeURIComponent(analisiDettagliata.titoloRilevato)}`, '_blank')}
                        className="flex items-center justify-center gap-1.5 p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700 transition-colors"
                      >
                        <span className="text-cyan-400">👗</span> Vinted Italia
                      </button>
                      <button
                        type="button"
                        onClick={() => window.open(`https://www.facebook.com/marketplace/torino/search?query=${encodeURIComponent(analisiDettagliata.titoloRilevato)}`, '_blank')}
                        className="flex items-center justify-center gap-1.5 p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700 transition-colors"
                      >
                        <span className="text-blue-400">👥</span> Marketplace (Torino)
                      </button>
                      <a
                        href={`https://www.ebay.it/sch/i.html?_nkw=${encodeURIComponent(analisiDettagliata.titoloRilevato)}&LH_Complete=1&LH_Sold=1`}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center justify-center gap-1.5 p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700 transition-colors"
                      >
                        <span className="text-emerald-400">🔵</span> eBay Venduti
                      </a>
                    </div>
                  </>
                )}
              </div>

              {/* Salva Affare */}
              <button
                type="button"
                onClick={salvaNelTracker}
                className="w-full flex items-center justify-center gap-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 py-3 text-xs font-bold text-slate-200"
              >
                <PlusCircle className="w-4 h-4 text-indigo-400" /> Salva nei Miei Affari in Trattativa
              </button>

            </div>
          )}

        </div>
      )}

      {/* SEZIONE TRACKER */}
      {sezione === 'tracker' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
            <span className="text-xs text-slate-400 block font-semibold">Affari Salvati</span>
            <b className="text-xl font-mono text-indigo-400 font-extrabold">{affariSalvati.length}</b>
          </div>

          {affariSalvati.length === 0 ? (
            <div className="p-8 text-center rounded-2xl border border-dashed border-slate-800 text-slate-500 text-xs">
              <ShoppingBag className="w-8 h-8 mx-auto mb-2 text-slate-600" />
              Nessun affare salvato finora.
            </div>
          ) : (
            <div className="space-y-2">
              {affariSalvati.map(deal => (
                <div key={deal.id} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                  <div>
                    <h4 className="text-xs font-bold text-slate-100">{deal.nome}</h4>
                    <p className="text-[11px] text-slate-400">Target: <b>{deal.targetAcquisto}€</b> | Rivendita: <b>{deal.rivenditaStimata}€</b></p>
                  </div>
                  <button type="button" onClick={() => setAffariSalvati(affariSalvati.filter(d => d.id !== deal.id))} className="text-slate-500 hover:text-rose-400 p-1">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

    </div>
  )
})

export default FlipRadarHub
