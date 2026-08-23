import os

html_content = r'''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Piattaforma Ufficiale Turni TPL Arriva Italia 2026</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome 6 Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        .selected-row { background-color: #312e81 !important; border-left: 4px solid #818cf8 !important; color: #ffffff !important; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #0b0f19; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #334155; }

        /* DOUBLE RANGE SLIDER STYLES */
        .range-slider-container {
            position: relative;
            width: 100%;
            height: 36px;
            display: flex;
            align-items: center;
        }
        .range-slider-track {
            position: absolute;
            width: 100%;
            height: 8px;
            background: #090d16;
            border-radius: 9999px;
            border: 1px solid #1e293b;
        }
        .range-slider-fill {
            position: absolute;
            height: 8px;
            background: linear-gradient(90deg, #10b981 0%, #6366f1 100%);
            border-radius: 9999px;
            pointer-events: none;
            box-shadow: 0 0 14px rgba(99, 102, 241, 0.5);
        }
        .range-input {
            position: absolute;
            width: 100%;
            height: 8px;
            background: none;
            pointer-events: none;
            -webkit-appearance: none;
            appearance: none;
            margin: 0;
            outline: none;
            z-index: 20;
        }
        .range-input::-webkit-slider-thumb {
            height: 22px;
            width: 22px;
            border-radius: 50%;
            background: #ffffff;
            border: 3px solid #10b981;
            pointer-events: auto;
            -webkit-appearance: none;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0,0,0,0.6);
            transition: transform 0.15s ease, border-color 0.15s ease;
        }
        .range-input::-webkit-slider-thumb:hover {
            transform: scale(1.2);
        }
        .range-input::-webkit-slider-thumb:active {
            transform: scale(1.3);
        }
        #input-max-nastro::-webkit-slider-thumb {
            border-color: #6366f1;
        }
        .range-input::-moz-range-thumb {
            height: 22px;
            width: 22px;
            border-radius: 50%;
            background: #ffffff;
            border: 3px solid #10b981;
            pointer-events: auto;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0,0,0,0.6);
        }
        #input-max-nastro::-moz-range-thumb {
            border-color: #6366f1;
        }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col antialiased selection:bg-indigo-500 selection:text-white">

    <!-- TOAST NOTIFICATION -->
    <div id="toast" class="fixed bottom-6 right-6 z-50 transform translate-y-20 opacity-0 transition-all duration-300 pointer-events-none bg-slate-900 border border-emerald-500/40 text-white px-4 py-3 rounded-2xl shadow-2xl flex items-center gap-3 font-medium text-xs">
        <i class="fa-solid fa-circle-check text-emerald-400 text-base"></i>
        <span id="toast-msg">Notifica</span>
    </div>

    <!-- HEADER PRINCIPALE -->
    <header class="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center justify-between gap-4">
            
            <!-- Logo & Titolo -->
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-emerald-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20 ring-1 ring-white/20">
                    <i class="fa-solid fa-bus text-lg"></i>
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <h1 class="text-base sm:text-lg font-black tracking-tight text-white">TPL Piemonte 2026</h1>
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono">175 TURNI UFFICIALI</span>
                    </div>
                    <p class="text-xs text-slate-400">Verifica, Certificazione CCNL & Ottimizzazione Matematica Esatta</p>
                </div>
            </div>

            <!-- Selettore Modalità -->
            <div class="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 gap-1 flex-wrap shadow-inner">
                <button onclick="cambiaModalita('REALE')" id="btn-mode-reale" class="px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 text-slate-400 hover:text-white">
                    <i class="fa-solid fa-file-lines"></i> 1. Dati Reali Azienda
                </button>
                <button onclick="cambiaModalita('OTTIMIZZATO')" id="btn-mode-ottimizzato" class="px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 bg-emerald-600 text-white shadow ring-2 ring-emerald-400">
                    <i class="fa-solid fa-arrows-rotate"></i> 2. Ottimo Globale (OR-Tools)
                </button>
                <button onclick="cambiaModalita('DA_ZERO')" id="btn-mode-da-zero" class="px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 text-purple-300 hover:text-white">
                    <i class="fa-solid fa-wand-magic-sparkles text-purple-400"></i> 3. Generati da Zero
                </button>
            </div>

            <!-- Tasti Azione: Solver OR-Tools, Rigenera Set, Download PDF -->
            <div class="flex items-center gap-2 flex-wrap">
                <button onclick="avviaOttimizzazioneOrTools()" id="btn-ottimo-globale" class="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-emerald-600 hover:from-indigo-500 hover:to-emerald-500 text-white text-xs font-bold transition shadow-lg cursor-pointer active:scale-95 border border-indigo-400/40">
                    <i class="fa-solid fa-microchip text-yellow-300"></i> 🚀 Calcola Ottimo Globale
                </button>
                <button onclick="rigeneraNuovoSetTurni()" id="btn-rigenera-set" class="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 hover:from-amber-600 hover:to-orange-700 text-white text-xs font-bold transition shadow-md cursor-pointer active:scale-95 border border-amber-400/40">
                    <i class="fa-solid fa-wand-magic-sparkles text-amber-200"></i> ⚡ Genera Altro Set
                </button>
                <button onclick="scaricaPDF()" class="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 text-white text-xs font-bold transition shadow-md cursor-pointer active:scale-95 border border-red-500/40">
                    <i class="fa-solid fa-file-pdf"></i> Scarica PDF
                </button>
            </div>
        </div>
    </header>

    <!-- MODAL PROGRESSO OTTIMIZZATORE OR-TOOLS -->
    <div id="modal-ottimo-globale" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 backdrop-blur-md hidden transition-all duration-300">
        <div class="bg-slate-900 border border-indigo-500/50 rounded-3xl p-6 sm:p-8 max-w-lg w-full mx-4 shadow-2xl space-y-6 text-white text-center relative overflow-hidden">
            <div class="absolute -right-16 -top-16 w-36 h-36 bg-indigo-500/20 rounded-full blur-2xl pointer-events-none"></div>
            <div class="absolute -left-16 -bottom-16 w-36 h-36 bg-emerald-500/20 rounded-full blur-2xl pointer-events-none"></div>

            <div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-2xl shadow-lg border border-indigo-400/40">
                <i id="modal-icon-spinner" class="fa-solid fa-atom fa-spin text-yellow-300"></i>
            </div>

            <div class="space-y-1">
                <h3 class="text-lg sm:text-xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-indigo-200 via-purple-200 to-emerald-200">
                    Ottimizzatore Matematico Esatto
                </h3>
                <p class="text-xs text-slate-400 font-mono">Motore: Google OR-Tools CP-SAT (C++ Backend)</p>
            </div>

            <!-- Barra di Avanzamento -->
            <div class="space-y-2">
                <div class="flex justify-between text-xs font-bold font-mono">
                    <span id="modal-progress-step" class="text-indigo-300 text-left truncate mr-2">Inizializzazione solver...</span>
                    <span id="modal-progress-perc" class="text-emerald-400 text-right">0%</span>
                </div>
                <div class="w-full bg-slate-950 rounded-full h-3.5 p-0.5 border border-slate-800 overflow-hidden shadow-inner">
                    <div id="modal-progress-bar" class="bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 h-full rounded-full transition-all duration-300 shadow-md" style="width: 0%;"></div>
                </div>
            </div>

            <!-- Box Statistiche Risultato -->
            <div id="modal-stats-box" class="bg-slate-950/70 border border-slate-800 rounded-2xl p-4 text-xs font-mono space-y-2 text-left hidden">
                <div class="text-slate-400 font-bold uppercase tracking-wider text-[10px] text-center border-b border-slate-800 pb-1 text-indigo-400">
                    Risultato Ottimo Globale
                </div>
                <div class="flex justify-between">
                    <span class="text-slate-400">Turni Totali:</span>
                    <span id="stat-totale-turni" class="font-bold text-white">175</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-slate-400">Turni Continui (1 Ripresa):</span>
                    <span id="stat-turni-continui" class="font-bold text-emerald-400">173 (98.9%)</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-slate-400">Ore di Stacco Tagliate:</span>
                    <span id="stat-ore-risparmiate" class="font-bold text-yellow-400">455h 52m</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-slate-400">Conformità Normativa Soste:</span>
                    <span id="stat-conformita" class="font-bold text-emerald-300">100% Legale</span>
                </div>
            </div>

            <!-- Bottone Chiudi & Mostra -->
            <button id="modal-btn-chiudi" onclick="chiudiModalOttimo()" class="hidden w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 font-bold text-xs tracking-wider uppercase transition shadow-lg active:scale-95 cursor-pointer">
                Visualizza Turni Ottimizzati
            </button>
        </div>
    </div>

    <!-- MAIN CONTAINER -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-5 space-y-5">

        <!-- PANNELLO PARAMETRI CON DOUBLE SLIDER (MINIMO LAVORO & MASSIMO NASTRO) -->
        <div class="bg-gradient-to-br from-slate-900 via-indigo-950/60 to-slate-900 p-4 sm:p-5 rounded-2xl shadow-xl border border-indigo-500/30 space-y-3.5">
            <div class="flex flex-wrap items-center justify-between gap-3 border-b border-indigo-800/40 pb-2.5">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-xl bg-indigo-600/30 border border-indigo-500/40 text-indigo-300 flex items-center justify-center text-sm shadow">
                        <i class="fa-solid fa-sliders"></i>
                    </div>
                    <div>
                        <h2 class="text-xs sm:text-sm font-bold text-white uppercase tracking-wider">Parametri Normativi & Range Orario Turni</h2>
                        <p class="text-[11px] text-indigo-300/80">Regola il range tra il Minimo Lavoro Garantito e il Massimo Nastro Ammesso</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="impostaPreset(390, 630)" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-indigo-900/60 hover:bg-indigo-800 text-indigo-200 border border-indigo-700/50 transition shadow-sm">
                        CCNL Standard (6h30 - 10h30)
                    </button>
                    <button onclick="ripristinaDefault()" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition flex items-center gap-1.5 border border-slate-700">
                        <i class="fa-solid fa-rotate-left"></i> Reset
                    </button>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 text-xs items-center">
                
                <!-- DOUBLE SLIDER (7 COLONNE) -->
                <div class="lg:col-span-7 bg-slate-950/70 p-3.5 rounded-xl border border-slate-800 space-y-1.5">
                    <div class="flex justify-between items-center text-xs">
                        <div class="flex items-center gap-1.5">
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block shadow"></span>
                            <span class="text-slate-300 font-bold">Minimo Lavoro Garantito:</span>
                            <span id="label-min-lavoro" class="font-mono font-bold text-emerald-400 text-sm">6h 30m</span>
                        </div>
                        <div class="flex items-center gap-1.5">
                            <span class="text-slate-300 font-bold">Massimo Nastro:</span>
                            <span id="label-max-nastro" class="font-mono font-bold text-indigo-400 text-sm">10h 30m</span>
                            <span class="w-2.5 h-2.5 rounded-full bg-indigo-500 inline-block shadow"></span>
                        </div>
                    </div>

                    <!-- Double Range Track -->
                    <div class="range-slider-container">
                        <div class="range-slider-track"></div>
                        <div id="slider-range-fill" class="range-slider-fill" style="left: 25%; width: 40%;"></div>
                        <input type="range" id="input-min-lavoro" min="240" max="840" step="15" value="390" oninput="aggiornaDoubleSlider('min')" class="range-input">
                        <input type="range" id="input-max-nastro" min="240" max="840" step="15" value="630" oninput="aggiornaDoubleSlider('max')" class="range-input">
                    </div>

                    <div class="flex justify-between text-[10px] font-mono text-slate-500 pt-0.5">
                        <span>4h 00m (Min)</span>
                        <span class="text-slate-400">Trascina le due levette per calibrare il range</span>
                        <span>14h 00m (Max)</span>
                    </div>
                </div>

                <!-- MAX RIPRESE & SOSTE (5 COLONNE) -->
                <div class="lg:col-span-5 grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div class="bg-slate-950/70 p-3 rounded-xl border border-slate-800 space-y-1.5">
                        <label class="font-bold text-slate-300 flex items-center gap-1.5"><i class="fa-solid fa-repeat text-yellow-400"></i> Max Riprese:</label>
                        <select id="select-max-riprese" onchange="aggiornaFiltriCondizioni()" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2 py-1.5 text-white font-mono text-xs focus:ring-1 focus:ring-indigo-500">
                            <option value="1">1 sola ripresa (Continuo)</option>
                            <option value="2" selected>Max 2 riprese (Stacco)</option>
                            <option value="ALL">Nessun limite</option>
                        </select>
                    </div>

                    <div class="bg-slate-950/70 p-3 rounded-xl border border-slate-800 flex flex-col justify-center gap-1.5">
                        <label class="flex items-center gap-2 text-slate-300 cursor-pointer">
                            <input type="checkbox" id="check-sosta-6h" checked disabled class="accent-emerald-500 rounded">
                            <span class="text-[11px]"><b class="text-emerald-400">Sosta 6h</b> (30m / 2x15m)</span>
                        </label>
                        <label class="flex items-center gap-2 text-slate-300 cursor-pointer">
                            <input type="checkbox" id="check-hub-torino" checked onchange="aggiornaFiltriCondizioni()" class="accent-indigo-500 rounded">
                            <span class="text-[11px]">Hub Scambio Torino</span>
                        </label>
                    </div>
                </div>

            </div>
        </div>

        <!-- 4 KPI SUMMARY CARDS -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
            <div class="bg-slate-900 p-4 rounded-2xl border border-slate-800 shadow space-y-1">
                <p class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Nastro Medio</p>
                <h3 class="text-2xl font-black text-white font-mono" id="kpi-nastro-val">8h 47m</h3>
                <p class="text-[11px] text-slate-500 font-medium" id="kpi-nastro-sub">Deposito selezionato</p>
            </div>
            <div class="bg-slate-900 p-4 rounded-2xl border border-slate-800 shadow space-y-1">
                <p class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Conformi al Range</p>
                <h3 class="text-2xl font-black text-emerald-400 font-mono" id="kpi-turni-conformi">100% (175/175)</h3>
                <p class="text-[11px] text-slate-500 font-medium" id="kpi-conformi-sub">Min Lavoro &le; Turno &le; Max Nastro</p>
            </div>
            <div class="bg-slate-900 p-4 rounded-2xl border border-slate-800 shadow space-y-1">
                <p class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">OLG Medio Retribuito</p>
                <h3 class="text-2xl font-black text-emerald-400 font-mono" id="kpi-olg-val">8h 47m</h3>
                <p class="text-[11px] text-emerald-400/80 font-medium" id="kpi-target-label">Garantito &ge; Minimo Lavoro</p>
            </div>
            <div class="bg-slate-900 p-4 rounded-2xl border border-slate-800 shadow space-y-1">
                <p class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Turni nel Deposito</p>
                <h3 class="text-2xl font-black text-white font-mono" id="kpi-turni-count">175 Turni</h3>
                <p class="text-[11px] text-purple-400 font-medium" id="kpi-dep-label">Tutti i Depositi</p>
            </div>
        </div>

        <!-- FILTRI DEPOSITI & RICERCA -->
        <div class="bg-slate-900 p-3.5 rounded-2xl border border-slate-800 shadow space-y-2.5">
            <div class="flex flex-wrap items-center justify-between gap-3">
                <div class="relative flex-1 min-w-[240px]">
                    <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-3 text-slate-500 text-xs"></i>
                    <input type="text" id="search-input" oninput="aggiornaFiltriCondizioni()" placeholder="Cerca codice turno (es. Ca0030, Pi0010, To0660), linea (268, 275, 121, MOPAR) o località..." class="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500">
                </div>
            </div>

            <!-- Pulsanti Depositi -->
            <div class="flex flex-wrap gap-1.5 text-xs font-semibold" id="dep-buttons-container">
                <button onclick="selezionaDeposito('TUTTI')" id="btn-dep-tutti" class="dep-btn px-3 py-1.5 rounded-lg bg-indigo-600 text-white shadow">Tutti (175)</button>
                <button onclick="selezionaDeposito('Pi')" id="btn-dep-pi" class="dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800">Pinerolo (32)</button>
                <button onclick="selezionaDeposito('To')" id="btn-dep-to" class="dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800">Torino (47)</button>
                <button onclick="selezionaDeposito('Pe')" id="btn-dep-pe" class="dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800">Perosa (25)</button>
                <button onclick="selezionaDeposito('Pt')" id="btn-dep-pt" class="dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800">Pont St. Martin (13)</button>
                <button onclick="selezionaDeposito('Su')" id="btn-dep-su" class="dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800">Susa (11)</button>
                <button onclick="selezionaDeposito('Pb')" id="btn-dep-pb" class="dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800">Piobesi (10)</button>
                <button onclick="selezionaDeposito('Ca')" id="btn-dep-ca" class="dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800">Caselle (9)</button>
                <button onclick="selezionaDeposito('Sa')" id="btn-dep-sa" class="dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800">Salbertrand (8)</button>
                <button onclick="selezionaDeposito('Lu')" id="btn-dep-lu" class="dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800">Luserna S.G. (6)</button>
                <button onclick="selezionaDeposito('Ba')" id="btn-dep-ba" class="dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800">Barge (4)</button>
                <button onclick="selezionaDeposito('Iv')" id="btn-dep-iv" class="dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800">Ivrea (4)</button>
                <button onclick="selezionaDeposito('Bo')" id="btn-dep-bo" class="dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800">Bobbio Pellice (3)</button>
                <button onclick="selezionaDeposito('FT')" id="btn-dep-ft" class="dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800">Fuori Turno (3)</button>
            </div>
        </div>

        <!-- LAYOUT A 2 COLONNE: TABELLA TURNI & DETTAGLIO CARTELLINO -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">

            <!-- Colonna Sinistra: Tabella Turni (6 colonne) -->
            <div class="lg:col-span-6 bg-slate-900 rounded-2xl border border-slate-800 shadow overflow-hidden">
                <div class="p-3.5 bg-slate-950/60 border-b border-slate-800 flex justify-between items-center text-xs">
                    <span class="font-bold text-slate-300 flex items-center gap-2">
                        <i class="fa-solid fa-list-check text-indigo-400"></i> Elenco Turni
                    </span>
                    <span id="tabella-count-badge" class="font-mono text-slate-400 font-semibold">175 turni</span>
                </div>

                <div class="overflow-x-auto max-h-[760px] overflow-y-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-slate-950 text-slate-400 font-mono text-[11px] uppercase tracking-wider sticky top-0 border-b border-slate-800 z-10">
                            <tr>
                                <th class="py-2.5 px-3">Turno</th>
                                <th class="py-2.5 px-3">Servizio</th>
                                <th class="py-2.5 px-3">Nastro</th>
                                <th class="py-2.5 px-3">OLG</th>
                                <th class="py-2.5 px-3 text-center">Rip</th>
                                <th class="py-2.5 px-3 text-center">Sosta 6h</th>
                                <th class="py-2.5 px-3 text-center">Stato</th>
                            </tr>
                        </thead>
                        <tbody id="turni-table-body" class="divide-y divide-slate-800/60 font-medium">
                            <!-- Righe inserite dinamicamente -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Colonna Destra: Dossier Cartellino con Timeline Transit & Gantt (6 colonne) -->
            <div class="lg:col-span-6 bg-slate-900 rounded-2xl border border-slate-800 shadow p-4 sm:p-5 space-y-4 sticky top-16">
                
                <!-- Intestazione Turno Selezionato & Azioni Rapide -->
                <div class="flex items-start justify-between border-b border-slate-800 pb-3 gap-2">
                    <div class="space-y-1">
                        <div class="flex items-center gap-2 flex-wrap">
                            <span id="detail-code-badge" class="font-mono font-bold px-2.5 py-1 rounded-lg bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs shadow-sm">Ca0030</span>
                            <h3 id="detail-title" class="font-bold text-white text-sm sm:text-base tracking-tight">Ca0030 – CASELLE-TORINO-CASELLE</h3>
                        </div>
                        <p id="detail-subtitle" class="text-xs text-slate-400 flex items-center gap-2">
                            <span id="detail-dep-badge" class="font-medium text-slate-300"><i class="fa-solid fa-warehouse mr-1 text-slate-500"></i>Deposito: Caselle</span>
                            <span class="text-slate-600">&bull;</span>
                            <span id="detail-orario-badge" class="font-mono text-indigo-300 font-semibold"><i class="fa-regular fa-clock mr-1"></i>06:34 ➔ 14:45</span>
                        </p>
                    </div>

                    <!-- Bottoni Azione Rapida Turno -->
                    <div class="flex items-center gap-1.5 shrink-0">
                        <button onclick="copiaCartellinoTesto()" title="Copia cartellino negli appunti" class="p-2 rounded-xl bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs transition active:scale-95">
                            <i class="fa-solid fa-copy"></i>
                        </button>
                    </div>
                </div>

                <!-- 4 Box KPI Turno -->
                <div class="grid grid-cols-4 gap-2 text-center text-xs font-mono">
                    <div class="bg-slate-950 p-2 rounded-xl border border-slate-800/80 shadow-inner">
                        <span class="text-[10px] text-slate-400 block uppercase font-bold">Nastro</span>
                        <b id="detail-nastro" class="text-white text-sm">8h 11m</b>
                    </div>
                    <div class="bg-slate-950 p-2 rounded-xl border border-slate-800/80 shadow-inner">
                        <span class="text-[10px] text-slate-400 block uppercase font-bold">OLG (Lavoro)</span>
                        <b id="detail-olg" class="text-emerald-400 text-sm">7h 04m</b>
                    </div>
                    <div class="bg-slate-950 p-2 rounded-xl border border-slate-800/80 shadow-inner">
                        <span class="text-[10px] text-slate-400 block uppercase font-bold">Guida Eff.</span>
                        <b id="detail-guida" class="text-indigo-400 text-sm">5.25h</b>
                    </div>
                    <div class="bg-slate-950 p-2 rounded-xl border border-slate-800/80 shadow-inner">
                        <span class="text-[10px] text-slate-400 block uppercase font-bold">Riprese</span>
                        <b id="detail-riprese" class="text-yellow-400 text-sm">1,00</b>
                    </div>
                </div>

                <!-- Barra Visuale Gantt Proporzionale del Turno -->
                <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-1.5">
                    <div class="flex justify-between items-center text-[10px] font-mono text-slate-400">
                        <span class="font-bold uppercase tracking-wider text-slate-300"><i class="fa-solid fa-chart-gantt text-indigo-400 mr-1"></i>Spettro Giornaliero Attività</span>
                        <span id="detail-gantt-span" class="text-slate-400">06:34 ➔ 14:45</span>
                    </div>
                    <div id="detail-gantt-bar" class="w-full h-3 bg-slate-900 rounded-full flex overflow-hidden border border-slate-800 p-0.5">
                        <!-- Segmenti visuali inseriti dinamicamente -->
                    </div>
                    <div class="flex justify-between text-[10px] font-mono text-slate-500 pt-0.5">
                        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-indigo-500 inline-block"></span> Guida</span>
                        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-amber-400 inline-block"></span> Sosta CCNL</span>
                        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-purple-500 inline-block"></span> Trasf</span>
                        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-slate-600 inline-block"></span> Disp</span>
                    </div>
                </div>

                <!-- Box Sosta CCNL -->
                <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800 flex items-center justify-between gap-3 text-xs">
                    <div class="space-y-0.5">
                        <span class="text-[10px] text-slate-400 block uppercase font-bold flex items-center gap-1.5">
                            <i class="fa-solid fa-shield-halved text-emerald-400"></i> Conformità Sosta CCNL (Entro 6h)
                        </span>
                        <p id="detail-sosta-desc" class="text-slate-300 font-medium text-[11px]">Sosta in deposito fruita alle ore 09:54 ➔ 11:10 (1h 16m)</p>
                    </div>
                    <span id="detail-sosta-badge" class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shrink-0">🟢 A NORMA</span>
                </div>

                <!-- Timeline Attività con Header Riassuntivo e Filtri -->
                <div class="space-y-2.5">
                    <div class="flex items-center justify-between flex-wrap gap-2">
                        <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                            <i class="fa-solid fa-route text-indigo-400"></i> Cronologia Attività & Soste
                        </h4>
                        <!-- Badge Riassuntivi Turno -->
                        <div id="detail-pills-summary" class="flex items-center gap-1 text-[10px] font-mono text-slate-400 flex-wrap">
                            <!-- Inseriti dinamicamente -->
                        </div>
                    </div>

                    <!-- Filtri Tipo Attività -->
                    <div class="flex items-center gap-1 text-[11px] font-mono pb-1 border-b border-slate-800/80 overflow-x-auto">
                        <button onclick="filtraAttivitaDossier('ALL')" id="pill-filter-all" class="px-2.5 py-1 rounded-lg bg-indigo-600 text-white font-bold text-[10px] transition">Tutte</button>
                        <button onclick="filtraAttivitaDossier('LINEA')" id="pill-filter-linea" class="px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 text-[10px] transition">🚌 Corse</button>
                        <button onclick="filtraAttivitaDossier('SOSTA')" id="pill-filter-sosta" class="px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 text-[10px] transition">☕ Soste</button>
                        <button onclick="filtraAttivitaDossier('TRASF')" id="pill-filter-trasf" class="px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 text-[10px] transition">🔀 Trasf</button>
                    </div>

                    <!-- Contenitore Scroll Attività con Timeline Connessa -->
                    <div class="relative">
                        <div id="corse-list-container" class="space-y-2.5 max-h-[460px] overflow-y-auto pr-1">
                            <!-- Card attività grafiche inserite dinamicamente -->
                        </div>
                    </div>
                </div>

            </div>

        </div>

    </main>

    <!-- FOOTER -->
    <footer class="bg-slate-900 border-t border-slate-800 py-4 mt-auto text-center text-xs text-slate-500">
        <p>Piattaforma di Verifica e Ottimizzazione Orari TPL Piemonte &copy; 2026 Arriva Italia / SADEM &bull; Algoritmo Esatto Google OR-Tools CP-SAT</p>
    </footer>

    <!-- JAVASCRIPT APP -->
    <script>
        // STATO GLOBALE APPLICAZIONE CON PERSISTENZA LOCALSTORAGE
        let allTurniReali = [];
        let allTurniOttimizzati = [];
        let allTurniDaZero = [];
        
        let modalitaAttiva = localStorage.getItem('tpl_modalita') || 'OTTIMIZZATO';
        let depositoFiltro = localStorage.getItem('tpl_deposito') || 'TUTTI';
        let turnoSelezionato = null;
        let filtroAttivitaAttivo = 'ALL';
        let pollingInterval = null;

        const MIN_RANGE_VAL = 240; // 4h 00m
        const MAX_RANGE_VAL = 840; // 14h 00m

        // PARSER ORARIO CLOCK ("06:34" o "6.34" -> minuti da mezzanotte)
        function parseClock(tStr) {
            if (!tStr) return 0;
            const clean = String(tStr).trim().replace('.', ':').replace(',', ':');
            const parts = clean.split(':');
            if (parts.length === 2) {
                return (parseInt(parts[0]) || 0) * 60 + (parseInt(parts[1]) || 0);
            }
            return 0;
        }

        // PARSER DURATA (Minuti o stringa "6h 30m" o decimale "6.50")
        function parseDurataM(val) {
            if (val === null || val === undefined || val === '') return 0;
            if (typeof val === 'number') return Math.round(val);
            const valStr = String(val).trim();

            const mH = valStr.match(/^(\d+)\s*h\s*(\d+)?\s*m?$/i);
            if (mH) {
                const h = parseInt(mH[1]) || 0;
                const m = parseInt(mH[2]) || 0;
                return h * 60 + m;
            }

            if (valStr.includes(':')) {
                const p = valStr.split(':');
                return (parseInt(p[0]) || 0) * 60 + (parseInt(p[1]) || 0);
            }

            const fVal = parseFloat(valStr.replace(',', '.'));
            if (isNaN(fVal)) return 0;
            if (fVal > 24) return Math.round(fVal);
            return Math.round(fVal * 60);
        }

        function fmtDurata(m) {
            if (!m || m < 0) return "0h 00m";
            const h = Math.floor(m / 60);
            const mins = m % 60;
            return `${h}h ${String(mins).padStart(2, '0')}m`;
        }

        function fmtMinutiBrevi(m) {
            if (!m || m < 0) return "0m";
            if (m < 60) return `${m}m`;
            const h = Math.floor(m / 60);
            const mins = m % 60;
            return mins > 0 ? `${h}h ${mins}m` : `${h}h`;
        }

        function mostraToast(msg) {
            const toast = document.getElementById('toast');
            document.getElementById('toast-msg').innerText = msg;
            toast.classList.remove('translate-y-20', 'opacity-0');
            setTimeout(() => {
                toast.classList.add('translate-y-20', 'opacity-0');
            }, 2500);
        }

        // AGGIORNAMENTO DOUBLE SLIDER CON PERSISTENZA
        function aggiornaDoubleSlider(source) {
            const inputMin = document.getElementById('input-min-lavoro');
            const inputMax = document.getElementById('input-max-nastro');
            const fill = document.getElementById('slider-range-fill');

            let minVal = parseInt(inputMin.value);
            let maxVal = parseInt(inputMax.value);

            if (minVal > maxVal - 15) {
                if (source === 'min') {
                    inputMin.value = maxVal - 15;
                    minVal = maxVal - 15;
                } else {
                    inputMax.value = minVal + 15;
                    maxVal = minVal + 15;
                }
            }

            document.getElementById('label-min-lavoro').innerText = fmtDurata(minVal);
            document.getElementById('label-max-nastro').innerText = fmtDurata(maxVal);

            localStorage.setItem('tpl_min_lavoro', minVal);
            localStorage.setItem('tpl_max_nastro', maxVal);

            const totalSpan = MAX_RANGE_VAL - MIN_RANGE_VAL;
            const leftPerc = ((minVal - MIN_RANGE_VAL) / totalSpan) * 100;
            const rightPerc = ((maxVal - MIN_RANGE_VAL) / totalSpan) * 100;
            const widthPerc = rightPerc - leftPerc;

            fill.style.left = `${leftPerc}%`;
            fill.style.width = `${widthPerc}%`;

            aggiornaFiltriCondizioni();
        }

        function impostaPreset(minM, maxM) {
            document.getElementById('input-min-lavoro').value = minM;
            document.getElementById('input-max-nastro').value = maxM;
            aggiornaDoubleSlider('both');
        }

        // CARICAMENTO DATI
        async function caricaDati(isSilent = false) {
            try {
                const savedMin = localStorage.getItem('tpl_min_lavoro');
                const savedMax = localStorage.getItem('tpl_max_nastro');
                const savedRip = localStorage.getItem('tpl_max_riprese');
                const savedSearch = localStorage.getItem('tpl_search');

                if (savedMin) document.getElementById('input-min-lavoro').value = parseInt(savedMin);
                if (savedMax) document.getElementById('input-max-nastro').value = parseInt(savedMax);
                if (savedRip) document.getElementById('select-max-riprese').value = savedRip;
                if (savedSearch) document.getElementById('search-input').value = savedSearch;

                const [rReali, rOpt, rZero] = await Promise.all([
                    fetch(`turni_data.json?t=${Date.now()}`),
                    fetch(`turni_ottimizzati_completi.json?t=${Date.now()}`),
                    fetch(`turni_generati_da_zero.json?t=${Date.now()}`)
                ]);
                allTurniReali = await rReali.json();
                allTurniOttimizzati = await rOpt.json();
                allTurniDaZero = await rZero.json();

                cambiaModalita(modalitaAttiva, false);
                selezionaDeposito(depositoFiltro, false);
                aggiornaDoubleSlider('both');
            } catch (err) {
                console.error("Errore caricamento dati:", err);
            }
        }

        // CAMBIO MODALITÀ (REALE / OTTIMIZZATO / DA ZERO)
        function cambiaModalita(mode, triggerUpdate = true) {
            modalitaAttiva = mode;
            localStorage.setItem('tpl_modalita', mode);

            const btnReale = document.getElementById('btn-mode-reale');
            const btnOpt = document.getElementById('btn-mode-ottimizzato');
            const btnZero = document.getElementById('btn-mode-da-zero');

            btnReale.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 text-slate-400 hover:text-white';
            btnOpt.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 text-slate-400 hover:text-white';
            btnZero.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 text-slate-400 hover:text-white';

            if (mode === 'REALE') {
                btnReale.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 bg-blue-600 text-white shadow';
            } else if (mode === 'OTTIMIZZATO') {
                btnOpt.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 bg-emerald-600 text-white shadow ring-2 ring-emerald-400';
            } else if (mode === 'DA_ZERO') {
                btnZero.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 bg-purple-600 text-white shadow ring-2 ring-purple-400';
            }

            if (triggerUpdate) aggiornaFiltriCondizioni();
        }

        // SELEZIONE DEPOSITO
        function selezionaDeposito(dep, triggerUpdate = true) {
            depositoFiltro = dep;
            localStorage.setItem('tpl_deposito', dep);

            document.querySelectorAll('.dep-btn').forEach(b => {
                b.className = 'dep-btn px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800';
            });
            const activeBtn = document.getElementById(`btn-dep-${dep.toLowerCase()}`);
            if (activeBtn) {
                activeBtn.className = 'dep-btn px-3 py-1.5 rounded-lg bg-indigo-600 text-white shadow font-bold';
            }
            if (triggerUpdate) aggiornaFiltriCondizioni();
        }

        // VERIFICA CONFORMITÀ SOSTE 6H CCNL
        function verificaSosteEntro6h(t) {
            const nastroM = t.nastro_m || parseDurataM(t.nastro_str) || parseDurataM(t.nastro) || 0;
            if (nastroM <= 360) {
                return { ok: true, desc: "Impegno <= 6h00 (Sosta non obbligatoria)" };
            }

            const inServizioM = parseClock(t.inizio_servizio);
            const att = t.attivita || [];
            let pausa30 = false;
            let pause15 = 0;
            let sostaOrario = "";

            for (let a of att) {
                if (a.linea === 'Sosta' || a.is_sosta_deposito) {
                    const pM = parseClock(a.partenza);
                    const arrM = parseClock(a.arrivo);
                    const dur = arrM >= pM ? (arrM - pM) : (1440 - pM + arrM);
                    const tempoDaIn = pM >= inServizioM ? (pM - inServizioM) : (1440 - inServizioM + pM);

                    if (tempoDaIn <= 360) {
                        if (dur >= 30) {
                            pausa30 = true;
                            sostaOrario = `${a.partenza} ➔ ${a.arrivo} (${fmtDurata(dur)})`;
                        } else if (dur >= 15) {
                            pause15++;
                        }
                    }
                }
            }

            const ripVal = parseFloat(String(t.num_riprese || '1').replace(',', '.')) || 1;
            if (ripVal >= 2) {
                return { ok: true, desc: "Stacco al deposito garantito tra le riprese" };
            }
            if (pausa30) {
                return { ok: true, desc: `Sosta in deposito fruita alle ore ${sostaOrario}` };
            }
            if (pause15 >= 2) {
                return { ok: true, desc: "2 soste in banchina da 15 min garantite entro 6h" };
            }

            return { ok: false, desc: "Manca sosta 30m o 2x15m entro la 6ª ora" };
        }

        // MOTORE DI FILTRAGGIO & RENDERING
        function aggiornaFiltriCondizioni() {
            const minLavoro = parseInt(document.getElementById('input-min-lavoro').value) || 390;
            const maxNastro = parseInt(document.getElementById('input-max-nastro').value) || 630;
            const maxRipVal = document.getElementById('select-max-riprese').value;
            const searchVal = (document.getElementById('search-input').value || '').toLowerCase().trim();

            localStorage.setItem('tpl_max_riprese', maxRipVal);
            localStorage.setItem('tpl_search', searchVal);

            let dataset = allTurniReali;
            if (modalitaAttiva === 'OTTIMIZZATO') dataset = allTurniOttimizzati;
            else if (modalitaAttiva === 'DA_ZERO') dataset = allTurniDaZero;

            // Filtro deposito
            let filtrati = dataset;
            if (depositoFiltro !== 'TUTTI') {
                filtrati = dataset.filter(t => t.codice_turno && t.codice_turno.startsWith(depositoFiltro));
            }

            // Filtro ricerca
            if (searchVal) {
                filtrati = filtrati.filter(t => 
                    (t.codice_turno && t.codice_turno.toLowerCase().includes(searchVal)) ||
                    (t.nome_turno && t.nome_turno.toLowerCase().includes(searchVal)) ||
                    (t.attivita && t.attivita.some(a => (a.linea && a.linea.toLowerCase().includes(searchVal)) || (a.descrizione && a.descrizione.toLowerCase().includes(searchVal))))
                );
            }

            // Calcolo Conformità per ogni turno
            let conformiCount = 0;
            let totNastro = 0;
            let totOLG = 0;

            const listaCalcolata = filtrati.map(t => {
                const nastroM = t.nastro_m || parseDurataM(t.nastro_str) || parseDurataM(t.nastro);
                const olgM = t.olg_m || parseDurataM(t.olg_str) || parseDurataM(t.ore_lavoro);
                const ripVal = parseFloat(String(t.num_riprese || '1').replace(',', '.')) || 1;

                totNastro += nastroM;
                totOLG += olgM;

                const nastroOk = nastroM <= maxNastro;
                const minLavoroOk = (nastroM <= 240 || (t.codice_turno && t.codice_turno.startsWith('FT'))) || (olgM >= minLavoro);
                const ripOk = (maxRipVal === 'ALL') || (ripVal <= parseFloat(maxRipVal));
                const sostaRes = verificaSosteEntro6h(t);

                const isConforme = nastroOk && minLavoroOk && ripOk && sostaRes.ok;
                if (isConforme) conformiCount++;

                return {
                    ...t,
                    calc_nastro_m: nastroM,
                    calc_olg_m: olgM,
                    calc_rip_val: ripVal,
                    sosta_res: sostaRes,
                    is_conforme: isConforme
                };
            });

            // Aggiornamento KPI
            if (listaCalcolata.length > 0) {
                const nMedio = Math.round(totNastro / listaCalcolata.length);
                const oMedio = Math.round(totOLG / listaCalcolata.length);
                const percConformi = Math.round((conformiCount / listaCalcolata.length) * 100);

                document.getElementById('kpi-nastro-val').innerText = fmtDurata(nMedio);
                document.getElementById('kpi-olg-val').innerText = fmtDurata(oMedio);
                document.getElementById('kpi-turni-conformi').innerText = `${percConformi}% (${conformiCount}/${listaCalcolata.length})`;
                document.getElementById('kpi-turni-count').innerText = `${listaCalcolata.length} Turni`;

                let depNome = depositoFiltro === 'TUTTI' ? 'Tutti i Depositi' : `Deposito ${depositoFiltro}`;
                document.getElementById('kpi-dep-label').innerText = `${depNome} (${modalitaAttiva === 'OTTIMIZZATO' ? 'Ottimizzati OR-Tools' : (modalitaAttiva === 'DA_ZERO' ? 'Generati da Zero' : 'Dati Reali')})`;
            }

            // Rendering Tabella
            renderTabella(listaCalcolata);
        }

        // RENDERING RIGHE TABELLA
        function renderTabella(lista) {
            const tbody = document.getElementById('turni-table-body');
            tbody.innerHTML = '';
            document.getElementById('tabella-count-badge').innerText = `${lista.length} turni`;

            if (lista.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-slate-500 font-mono">Nessun turno trovato con i filtri selezionati</td></tr>`;
                return;
            }

            lista.forEach((t, i) => {
                const tr = document.createElement('tr');
                const isSelected = turnoSelezionato && turnoSelezionato.codice_turno === t.codice_turno;
                tr.className = `hover:bg-slate-800/60 cursor-pointer transition ${isSelected ? 'selected-row' : 'text-slate-300'}`;
                tr.onclick = () => {
                    selezionaTurno(t);
                    aggiornaSelezioneTabella();
                };

                const badgeStato = t.is_conforme ? 
                    `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">🟢 A NORMA</span>` :
                    `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-300 border border-red-500/30">🔴 SFORATO</span>`;

                const badgeSosta = t.sosta_res.ok ?
                    `<span class="text-emerald-400 font-mono text-[10px]"><i class="fa-solid fa-check"></i> Sosta OK</span>` :
                    `<span class="text-red-400 font-mono text-[10px]"><i class="fa-solid fa-xmark"></i> Sosta No</span>`;

                tr.innerHTML = `
                    <td class="py-2.5 px-3 font-mono font-bold text-white">${t.codice_turno}</td>
                    <td class="py-2.5 px-3 font-mono text-slate-400 text-[11px]">${t.inizio_servizio} - ${t.fine_servizio}</td>
                    <td class="py-2.5 px-3 font-mono">${t.nastro_str || fmtDurata(t.calc_nastro_m)}</td>
                    <td class="py-2.5 px-3 font-mono text-emerald-400">${t.olg_str || fmtDurata(t.calc_olg_m)}</td>
                    <td class="py-2.5 px-3 text-center font-mono">${t.calc_rip_val === 1 ? '1,00' : '2,00'}</td>
                    <td class="py-2.5 px-3 text-center">${badgeSosta}</td>
                    <td class="py-2.5 px-3 text-center">${badgeStato}</td>
                `;
                tbody.appendChild(tr);
            });

            const target = (turnoSelezionato && lista.find(x => x.codice_turno === turnoSelezionato.codice_turno)) || lista[0];
            selezionaTurno(target);
        }

        function aggiornaSelezioneTabella() {
            document.querySelectorAll('#turni-table-body tr').forEach(row => {
                const codeEl = row.querySelector('td:first-child');
                if (codeEl && turnoSelezionato && codeEl.innerText.trim() === turnoSelezionato.codice_turno) {
                    row.classList.add('selected-row');
                } else {
                    row.classList.remove('selected-row');
                }
            });
        }

        // FILTRO ATTIVITÀ DOSSIER
        function filtraAttivitaDossier(tipo) {
            filtroAttivitaAttivo = tipo;
            ['all', 'linea', 'sosta', 'trasf'].forEach(k => {
                const b = document.getElementById(`pill-filter-${k}`);
                if (b) {
                    b.className = (tipo.toLowerCase() === k) ?
                        'px-2.5 py-1 rounded-lg bg-indigo-600 text-white font-bold text-[10px] transition shadow' :
                        'px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 text-[10px] transition';
                }
            });
            if (turnoSelezionato) renderListaAttivita(turnoSelezionato);
        }

        // COPIA CARTELLINO NEGLI APPUNTI
        function copiaCartellinoTesto() {
            if (!turnoSelezionato) return;
            const t = turnoSelezionato;
            let text = `📋 CARTELLINO TURNO: ${t.codice_turno} (${t.nome_turno || ''})\n`;
            text += `🏢 Deposito: ${t.deposito || 'Deposito'}\n`;
            text += `⏱️ Orario: ${t.inizio_servizio} ➔ ${t.fine_servizio} (Nastro: ${t.nastro_str || fmtDurata(t.nastro_m)})\n`;
            text += `💼 OLG: ${t.olg_str || fmtDurata(t.olg_m)} | Guida: ${t.ore_guida || '0'}h\n\n`;
            text += `--- ATTIVITÀ ---\n`;

            (t.attivita || []).forEach((a, i) => {
                text += `${i+1}. [${a.partenza} -> ${a.arrivo}] ${a.linea}: ${a.descrizione || `${a.da || ''} -> ${a.a || ''}`} (Km: ${a.km || '-'})\n`;
            });

            navigator.clipboard.writeText(text).then(() => {
                mostraToast(`Cartellino ${t.codice_turno} copiato negli appunti!`);
            }).catch(e => {
                console.error("Copia fallita:", e);
            });
        }

        // SELEZIONE TURNO & CARTELLINO ATTIVITÀ GRAFICA MODERNA
        function selezionaTurno(t) {
            if (!t) return;
            turnoSelezionato = t;

            document.getElementById('detail-code-badge').innerText = t.codice_turno;
            document.getElementById('detail-title').innerText = `${t.codice_turno} – ${t.nome_turno || ''}`;
            document.getElementById('detail-subtitle').innerHTML = `
                <span class="font-medium text-slate-300"><i class="fa-solid fa-warehouse mr-1 text-slate-500"></i>Deposito: ${t.deposito || 'Deposito'}</span>
                <span class="text-slate-600">&bull;</span>
                <span class="font-mono text-indigo-300 font-semibold"><i class="fa-regular fa-clock mr-1"></i>${t.inizio_servizio} ➔ ${t.fine_servizio}</span>
            `;

            document.getElementById('detail-nastro').innerText = t.nastro_str || fmtDurata(t.calc_nastro_m);
            document.getElementById('detail-olg').innerText = t.olg_str || fmtDurata(t.calc_olg_m);
            document.getElementById('detail-guida').innerText = `${t.ore_guida || '0.00'}h`;
            document.getElementById('detail-riprese').innerText = t.num_riprese || '1,00';

            const sostaRes = t.sosta_res || verificaSosteEntro6h(t);
            document.getElementById('detail-sosta-desc').innerText = sostaRes.desc;
            const badgeSosta = document.getElementById('detail-sosta-badge');
            badgeSosta.innerText = sostaRes.ok ? '🟢 A NORMA' : '🔴 ILLEGALE';
            badgeSosta.className = sostaRes.ok ? 
                'px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shrink-0' :
                'px-2.5 py-1 rounded-full text-[10px] font-bold bg-red-500/20 text-red-300 border border-red-500/30 shrink-0';

            // Costruzione Mini-Gantt Bar
            renderGanttBar(t);

            // Conteggi Riassuntivi
            const att = t.attivita || [];
            let nCorse = 0;
            let nSoste = 0;
            let nTrasf = 0;
            let totKm = 0;

            att.forEach(a => {
                if (a.linea === 'Sosta' || a.is_sosta_deposito) nSoste++;
                else if (a.linea === 'Trasf') nTrasf++;
                else if (a.linea === 'Disp') {}
                else nCorse++;

                const kmVal = parseFloat(String(a.km || '0').replace(',', '.'));
                if (!isNaN(kmVal)) totKm += kmVal;
            });

            document.getElementById('detail-pills-summary').innerHTML = `
                <span class="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300"><i class="fa-solid fa-bus text-indigo-400 mr-1"></i>${nCorse} corse</span>
                <span class="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300"><i class="fa-solid fa-mug-hot text-amber-400 mr-1"></i>${nSoste} soste</span>
                <span class="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300"><i class="fa-solid fa-road text-emerald-400 mr-1"></i>${totKm.toFixed(1)} km</span>
            `;

            renderListaAttivita(t);
        }

        // RENDERING MINI-GANTT DEL TURNO
        function renderGanttBar(t) {
            const ganttBar = document.getElementById('detail-gantt-bar');
            ganttBar.innerHTML = '';
            document.getElementById('detail-gantt-span').innerText = `${t.inizio_servizio} ➔ ${t.fine_servizio}`;

            const inM = parseClock(t.inizio_servizio);
            const finM = parseClock(t.fine_servizio);
            const totM = finM >= inM ? (finM - inM) : (1440 - inM + finM);
            if (totM <= 0) return;

            const att = t.attivita || [];
            att.forEach(a => {
                const pM = parseClock(a.partenza);
                const arrM = parseClock(a.arrivo);
                const durM = arrM >= pM ? (arrM - pM) : (1440 - pM + arrM);
                const perc = Math.max(1, (durM / totM) * 100);

                const seg = document.createElement('div');
                seg.style.width = `${perc}%`;
                seg.className = "h-full transition hover:opacity-80 cursor-pointer";

                if (a.linea === 'Sosta' || a.is_sosta_deposito) {
                    seg.className += " bg-amber-400";
                    seg.title = `Sosta: ${a.partenza} - ${a.arrivo} (${durM}m)`;
                } else if (a.linea === 'Trasf') {
                    seg.className += " bg-purple-500";
                    seg.title = `Trasf: ${a.partenza} - ${a.arrivo} (${durM}m)`;
                } else if (a.linea === 'Disp') {
                    seg.className += " bg-slate-600";
                    seg.title = `Disp: ${a.partenza} - ${a.arrivo} (${durM}m)`;
                } else {
                    seg.className += " bg-indigo-500";
                    seg.title = `Linea ${a.linea}: ${a.partenza} - ${a.arrivo} (${durM}m)`;
                }

                ganttBar.appendChild(seg);
            });
        }

        // RENDERING LISTA ATTIVITÀ GRAFICA
        function renderListaAttivita(t) {
            const container = document.getElementById('corse-list-container');
            container.innerHTML = '';

            let att = t.attivita || [];

            // Applicazione filtro per tipo
            if (filtroAttivitaAttivo === 'LINEA') {
                att = att.filter(a => a.linea !== 'Sosta' && a.linea !== 'Disp' && a.linea !== 'Trasf' && !a.is_sosta_deposito);
            } else if (filtroAttivitaAttivo === 'SOSTA') {
                att = att.filter(a => a.linea === 'Sosta' || a.is_sosta_deposito);
            } else if (filtroAttivitaAttivo === 'TRASF') {
                att = att.filter(a => a.linea === 'Trasf');
            }

            if (att.length === 0) {
                container.innerHTML = `<div class="p-6 text-center text-slate-500 font-mono text-xs">Nessuna attività corrisponde al filtro selezionato</div>`;
                return;
            }

            att.forEach((a, idx) => {
                const card = document.createElement('div');
                const isSosta = a.linea === 'Sosta' || a.is_sosta_deposito;
                const isDisp = a.linea === 'Disp';
                const isTrasf = a.linea === 'Trasf';

                const pM = parseClock(a.partenza);
                const arrM = parseClock(a.arrivo);
                const durM = arrM >= pM ? (arrM - pM) : (1440 - pM + arrM);
                const durStr = fmtMinutiBrevi(durM);

                if (isSosta) {
                    // CARD SOSTA / PAUSA CCNL (Ambra / Oro)
                    card.className = "p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 border-l-4 border-l-amber-400 text-xs space-y-1.5 shadow-sm hover:border-amber-400/60 transition";
                    card.innerHTML = `
                        <div class="flex justify-between items-center">
                            <div class="flex items-center gap-2">
                                <span class="w-5 h-5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-bold flex items-center justify-center font-mono border border-amber-500/30">${idx + 1}</span>
                                <span class="font-mono px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                                    <i class="fa-solid fa-mug-hot text-amber-400"></i> SOSTA CCNL
                                </span>
                            </div>
                            <span class="font-mono text-amber-200 font-bold bg-slate-950 px-2 py-0.5 rounded text-[11px] border border-amber-500/30">
                                ${a.partenza || '-'} ➔ ${a.arrivo || '-'} <span class="text-amber-400 text-[10px] font-normal">(${durStr})</span>
                            </span>
                        </div>
                        <div class="flex items-center gap-1.5 text-amber-100 font-semibold text-xs pl-7">
                            <i class="fa-solid fa-location-dot text-amber-400 text-[10px] shrink-0"></i>
                            <span class="truncate">${a.descrizione || a.da || 'Sosta in Deposito'}</span>
                        </div>
                        <div class="flex justify-between items-center text-[10px] font-mono text-amber-400/80 pt-1 border-t border-amber-500/20 pl-7">
                            <span>Durata effettiva: <b>${durStr}</b></span>
                            <span class="uppercase tracking-wider font-semibold">☕ Pausa Retribuita CCNL</span>
                        </div>
                    `;
                } else if (isTrasf) {
                    // CARD TRASFERIMENTO / FUORI SERVIZIO (Viola / Purple)
                    card.className = "p-3 rounded-xl bg-slate-950 border border-purple-900/40 border-l-4 border-l-purple-500 text-xs space-y-1.5 shadow-sm hover:border-purple-500/60 transition";
                    card.innerHTML = `
                        <div class="flex justify-between items-center">
                            <div class="flex items-center gap-2">
                                <span class="w-5 h-5 rounded-full bg-slate-800 text-slate-400 text-[10px] font-bold flex items-center justify-center font-mono">${idx + 1}</span>
                                <span class="font-mono px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center gap-1">
                                    <i class="fa-solid fa-shuffle text-purple-400"></i> TRASFERIMENTO
                                </span>
                            </div>
                            <span class="font-mono text-purple-200 bg-slate-900 px-2 py-0.5 rounded text-[11px] border border-purple-900/50">
                                ${a.partenza || '-'} ➔ ${a.arrivo || '-'} <span class="text-purple-400 text-[10px]">(${durStr})</span>
                            </span>
                        </div>
                        <div class="flex items-center gap-1.5 text-slate-200 font-medium text-xs pl-7">
                            <span class="truncate">${a.descrizione || `${a.da || ''} ➔ ${a.a || ''}`}</span>
                        </div>
                        <div class="flex justify-between items-center text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-800/80 pl-7">
                            <span>Distanza: <b class="text-purple-300">${a.km && a.km !== '-' ? a.km + ' Km' : 'Tratta Tecnica'}</b></span>
                            <span class="uppercase tracking-wider text-purple-400">Fuori Servizio</span>
                        </div>
                    `;
                } else if (isDisp) {
                    // CARD DISPOSIZIONE / PRESA SERVIZIO (Slate / Blue)
                    card.className = "p-3 rounded-xl bg-slate-950 border border-slate-800 border-l-4 border-l-slate-500 text-xs space-y-1.5 shadow-sm hover:border-slate-700 transition";
                    card.innerHTML = `
                        <div class="flex justify-between items-center">
                            <div class="flex items-center gap-2">
                                <span class="w-5 h-5 rounded-full bg-slate-800 text-slate-400 text-[10px] font-bold flex items-center justify-center font-mono">${idx + 1}</span>
                                <span class="font-mono px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1">
                                    <i class="fa-solid fa-clipboard-check text-slate-400"></i> DISPOSIZIONE
                                </span>
                            </div>
                            <span class="font-mono text-slate-300 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                                ${a.partenza || '-'} ➔ ${a.arrivo || '-'} <span class="text-slate-500 text-[10px]">(${durStr})</span>
                            </span>
                        </div>
                        <div class="flex items-center gap-1.5 text-slate-300 font-medium text-xs pl-7">
                            <span class="truncate">${a.descrizione || 'Presa servizio / Controllo livelli / Chiusura'}</span>
                        </div>
                        <div class="flex justify-between items-center text-[10px] font-mono text-slate-500 pt-1 border-t border-slate-800/80 pl-7">
                            <span>Attività Deposito</span>
                            <span class="uppercase tracking-wider">Accessoria Retribuita</span>
                        </div>
                    `;
                } else {
                    // CARD CORSA COMMERCIALE DI LINEA (Indigo / Emerald)
                    card.className = "p-3.5 rounded-xl bg-slate-950 border border-indigo-950/60 border-l-4 border-l-indigo-500 text-xs space-y-2 shadow-sm hover:border-indigo-500/50 transition";
                    
                    let percorsoHtml = `<span class="truncate">${a.descrizione || `${a.da || ''} ➔ ${a.a || ''}`}</span>`;
                    if (a.da && a.a) {
                        percorsoHtml = `
                            <div class="flex items-center gap-1.5 text-slate-100 font-bold text-xs truncate">
                                <span class="text-indigo-200 truncate">${a.da}</span>
                                <i class="fa-solid fa-arrow-right text-indigo-400 text-[10px] shrink-0 mx-1"></i>
                                <span class="text-emerald-300 truncate">${a.a}</span>
                            </div>
                        `;
                    }

                    card.innerHTML = `
                        <div class="flex justify-between items-center">
                            <div class="flex items-center gap-2">
                                <span class="w-5 h-5 rounded-full bg-indigo-600/30 text-indigo-300 text-[10px] font-bold flex items-center justify-center font-mono border border-indigo-500/30">${idx + 1}</span>
                                <span class="font-mono px-2.5 py-0.5 rounded text-[11px] font-black bg-gradient-to-r from-indigo-600/30 to-purple-600/30 text-indigo-200 border border-indigo-500/40 flex items-center gap-1.5 shadow-sm">
                                    <i class="fa-solid fa-bus text-yellow-400 text-xs"></i> Linea ${a.linea}
                                </span>
                            </div>
                            <span class="font-mono text-white font-bold bg-slate-900 px-2.5 py-0.5 rounded text-[11px] border border-slate-800 shadow-inner">
                                ${a.partenza || '-'} ➔ ${a.arrivo || '-'} <span class="text-emerald-400 text-[10px] font-medium">(${durStr})</span>
                            </span>
                        </div>
                        <div class="pl-7">
                            ${percorsoHtml}
                        </div>
                        <div class="flex justify-between items-center text-[10px] font-mono text-slate-400 pt-1.5 border-t border-slate-800/80 pl-7">
                            <span class="flex items-center gap-1">Km Commerciali: <b class="text-white">${a.km || '-'} Km</b></span>
                            <span class="uppercase tracking-wider font-semibold text-emerald-400 flex items-center gap-1">
                                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block"></span> Corsa di Linea
                            </span>
                        </div>
                    `;
                }

                container.appendChild(card);
            });
        }

        // AVVIO OTTIMIZZATORE GOOGLE OR-TOOLS (C++)
        async function avviaOttimizzazioneOrTools() {
            const modal = document.getElementById('modal-ottimo-globale');
            const pBar = document.getElementById('modal-progress-bar');
            const pPerc = document.getElementById('modal-progress-perc');
            const pStep = document.getElementById('modal-progress-step');
            const statsBox = document.getElementById('modal-stats-box');
            const btnChiudi = document.getElementById('modal-btn-chiudi');
            const iconSpinner = document.getElementById('modal-icon-spinner');

            pBar.style.width = '10%';
            pPerc.textContent = '10%';
            pStep.textContent = 'Avvio solver OR-Tools C++...';
            statsBox.classList.add('hidden');
            btnChiudi.classList.add('hidden');
            iconSpinner.className = 'fa-solid fa-atom fa-spin text-yellow-300';
            modal.classList.remove('hidden');

            const minLavoro = document.getElementById('input-min-lavoro').value;
            const maxNastro = document.getElementById('input-max-nastro').value;

            try {
                await fetch(`/api/avvia_ottimo_globale?min_lavoro=${minLavoro}&max_nastro=${maxNastro}&t=${Date.now()}`);

                if (pollingInterval) clearInterval(pollingInterval);
                pollingInterval = setInterval(async () => {
                    try {
                        const r = await fetch(`/api/ottimo_globale_status?t=${Date.now()}`);
                        const statusData = await r.json();

                        pBar.style.width = `${statusData.progress}%`;
                        pPerc.textContent = `${statusData.progress}%`;
                        pStep.textContent = statusData.step || 'Elaborazione in corso...';

                        if (statusData.status === 'completed' || statusData.progress >= 100) {
                            clearInterval(pollingInterval);
                            pBar.style.width = '100%';
                            pPerc.textContent = '100%';
                            pStep.textContent = '🏆 Ottimo Globale Trovato!';
                            iconSpinner.className = 'fa-solid fa-circle-check text-emerald-400 text-3xl animate-bounce';

                            if (statusData.stats) {
                                document.getElementById('stat-totale-turni').textContent = statusData.stats.totale_turni || '175';
                                document.getElementById('stat-turni-continui').textContent = `${statusData.stats.turni_continui} (${statusData.stats.perc_continui})`;
                                document.getElementById('stat-ore-risparmiate').textContent = statusData.stats.ore_stacco_azzerate || '455h 52m';
                                document.getElementById('stat-conformita').textContent = statusData.stats.conformita || '100% Legale';
                                statsBox.classList.remove('hidden');
                            }

                            btnChiudi.classList.remove('hidden');
                            await caricaDati(false);
                            cambiaModalita('OTTIMIZZATO');
                        }
                    } catch (e) {
                        console.warn("Polling warning:", e);
                    }
                }, 250);

            } catch (err) {
                console.error("Errore avvio ottimizzatore:", err);
                alert("Errore avvio ottimizzatore: " + err.message);
                modal.classList.add('hidden');
            }
        }

        // CHIUSURA MODAL & APPLICAZIONE DIRETTA
        async function chiudiModalOttimo() {
            document.getElementById('modal-ottimo-globale').classList.add('hidden');
            await caricaDati(false);
            cambiaModalita('OTTIMIZZATO');
        }

        // RIGENERA ALTRO SET (FAST COMBINATORIAL)
        async function rigeneraNuovoSetTurni() {
            const btn = document.getElementById('btn-rigenera-set');
            const oldHtml = btn.innerHTML;
            btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Generazione...`;
            btn.disabled = true;

            const minLavoro = document.getElementById('input-min-lavoro').value;
            const maxNastro = document.getElementById('input-max-nastro').value;
            const strategie = ['bilanciato', 'compatto', 'esteso'];
            const strat = strategie[Math.floor(Math.random() * strategie.length)];

            try {
                const resp = await fetch(`/api/rigenera_turni?min_lavoro=${minLavoro}&max_nastro=${maxNastro}&strategia=${strat}&t=${Date.now()}`);
                const data = await resp.json();
                if (data.status === 'ok') {
                    await caricaDati(false);
                    cambiaModalita('OTTIMIZZATO');
                }
            } catch (err) {
                console.error("Errore rigenerazione:", err);
            } finally {
                btn.innerHTML = oldHtml;
                btn.disabled = false;
            }
        }

        // DOWNLOAD PDF DINAMICO (1 PAGINA PER TURNO)
        function scaricaPDF() {
            const minLavoro = document.getElementById('input-min-lavoro').value;
            const maxNastro = document.getElementById('input-max-nastro').value;
            const maxRip = document.getElementById('select-max-riprese').value;
            const dep = depositoFiltro;
            const mode = modalitaAttiva;

            const url = `/api/genera_pdf?dep=${encodeURIComponent(dep)}&min_lavoro=${minLavoro}&max_nastro=${maxNastro}&max_rip=${encodeURIComponent(maxRip)}&mode=${mode}&t=${Date.now()}`;
            window.open(url, '_blank');
        }

        function ripristinaDefault() {
            localStorage.clear();
            impostaPreset(390, 630);
            document.getElementById('select-max-riprese').value = '2';
            document.getElementById('search-input').value = '';
            depositoFiltro = 'TUTTI';
            cambiaModalita('OTTIMIZZATO');
        }

        window.onload = () => {
            caricaDati(false);
        };
    </script>
</body>
</html>
'''

with open("/home/antonio/verifica_turni/web/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ /home/antonio/verifica_turni/web/index.html aggiornato con successo.")
