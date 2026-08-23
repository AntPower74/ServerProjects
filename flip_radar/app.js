/**
 * FlipRadar - Client Logic & Market Pricing Engine
 * Focus: Italian Used Electronics Market (Torino & National)
 */

// 1. Comprehensive Pricing Database (Prezzi medi di mercato aggiornati Italia/Torino)
const MARKET_DATABASE = [
  // iPhones
  { id: 'iphone-11-64', category: 'iphone', name: 'iPhone 11 (64 GB)', buyTarget: 110, resaleAvg: 180, keywords: ['iphone 11', '11 64'] },
  { id: 'iphone-11-128', category: 'iphone', name: 'iPhone 11 (128 GB)', buyTarget: 130, resaleAvg: 210, keywords: ['iphone 11 128', '11 128gb'] },
  { id: 'iphone-12-mini-64', category: 'iphone', name: 'iPhone 12 Mini (64 GB)', buyTarget: 140, resaleAvg: 220, keywords: ['12 mini 64', 'iphone 12 mini 64'] },
  { id: 'iphone-12-mini-128', category: 'iphone', name: 'iPhone 12 Mini (128 GB)', buyTarget: 160, resaleAvg: 260, keywords: ['12 mini', '12 mini 128', 'iphone 12 mini'] },
  { id: 'iphone-12-64', category: 'iphone', name: 'iPhone 12 (64 GB)', buyTarget: 160, resaleAvg: 250, keywords: ['iphone 12 64', '12 64gb'] },
  { id: 'iphone-12-128', category: 'iphone', name: 'iPhone 12 (128 GB)', buyTarget: 180, resaleAvg: 280, keywords: ['iphone 12', 'iphone 12 128', '12 128gb'] },
  { id: 'iphone-12-pro-128', category: 'iphone', name: 'iPhone 12 Pro (128 GB)', buyTarget: 220, resaleAvg: 340, keywords: ['iphone 12 pro', '12 pro'] },
  { id: 'iphone-13-mini-128', category: 'iphone', name: 'iPhone 13 Mini (128 GB)', buyTarget: 220, resaleAvg: 340, keywords: ['iphone 13 mini', '13 mini'] },
  { id: 'iphone-13-128', category: 'iphone', name: 'iPhone 13 (128 GB)', buyTarget: 260, resaleAvg: 380, keywords: ['iphone 13', 'iphone 13 128', '13 128gb'] },
  { id: 'iphone-13-pro-128', category: 'iphone', name: 'iPhone 13 Pro (128 GB)', buyTarget: 330, resaleAvg: 470, keywords: ['iphone 13 pro', '13 pro'] },
  { id: 'iphone-14-128', category: 'iphone', name: 'iPhone 14 (128 GB)', buyTarget: 340, resaleAvg: 480, keywords: ['iphone 14', 'iphone 14 128', '14 128gb'] },
  { id: 'iphone-14-pro-128', category: 'iphone', name: 'iPhone 14 Pro (128 GB)', buyTarget: 450, resaleAvg: 620, keywords: ['iphone 14 pro', '14 pro'] },
  { id: 'iphone-15-128', category: 'iphone', name: 'iPhone 15 (128 GB)', buyTarget: 440, resaleAvg: 590, keywords: ['iphone 15', 'iphone 15 128', '15 128gb'] },
  { id: 'iphone-15-pro-128', category: 'iphone', name: 'iPhone 15 Pro (128 GB)', buyTarget: 580, resaleAvg: 760, keywords: ['iphone 15 pro', '15 pro'] },

  // Apple Watch & AirPods & iPad
  { id: 'airpods-pro-1', category: 'apple', name: 'AirPods Pro (1ª Generazione)', buyTarget: 40, resaleAvg: 80, keywords: ['airpods pro 1', 'airpods pro'] },
  { id: 'airpods-pro-2', category: 'apple', name: 'AirPods Pro 2', buyTarget: 75, resaleAvg: 140, keywords: ['airpods pro 2', 'pro 2'] },
  { id: 'apple-watch-se', category: 'apple', name: 'Apple Watch SE (40/44mm)', buyTarget: 60, resaleAvg: 110, keywords: ['watch se', 'apple watch se'] },
  { id: 'apple-watch-7', category: 'apple', name: 'Apple Watch Series 7', buyTarget: 90, resaleAvg: 160, keywords: ['watch 7', 'series 7', 'apple watch 7'] },
  { id: 'apple-watch-8', category: 'apple', name: 'Apple Watch Series 8', buyTarget: 130, resaleAvg: 220, keywords: ['watch 8', 'series 8', 'apple watch 8'] },
  { id: 'ipad-9-64', category: 'apple', name: 'iPad 9ª Gen (64 GB)', buyTarget: 120, resaleAvg: 200, keywords: ['ipad 9', 'ipad 9a', 'ipad 9 gen'] },
  { id: 'ipad-air-4', category: 'apple', name: 'iPad Air 4 (64 GB)', buyTarget: 180, resaleAvg: 290, keywords: ['ipad air 4', 'air 4'] },

  // Gaming & Console
  { id: 'switch-v2', category: 'gaming', name: 'Nintendo Switch (V2 Confezione Rossa)', buyTarget: 85, resaleAvg: 145, keywords: ['switch', 'nintendo switch', 'switch v2'] },
  { id: 'switch-oled', category: 'gaming', name: 'Nintendo Switch OLED', buyTarget: 130, resaleAvg: 210, keywords: ['switch oled', 'nintendo switch oled', 'oled'] },
  { id: 'switch-lite', category: 'gaming', name: 'Nintendo Switch Lite', buyTarget: 55, resaleAvg: 95, keywords: ['switch lite', 'lite'] },
  { id: 'ps4-slim', category: 'gaming', name: 'PlayStation 4 Slim (500GB/1TB)', buyTarget: 65, resaleAvg: 115, keywords: ['ps4', 'ps4 slim', 'playstation 4'] },
  { id: 'ps4-pro', category: 'gaming', name: 'PlayStation 4 Pro (1TB)', buyTarget: 90, resaleAvg: 155, keywords: ['ps4 pro', 'playstation 4 pro'] },
  { id: 'ps5-digital', category: 'gaming', name: 'PlayStation 5 Digital', buyTarget: 230, resaleAvg: 340, keywords: ['ps5 digital', 'playstation 5 digital'] },
  { id: 'ps5-disk', category: 'gaming', name: 'PlayStation 5 Disco (Standard/Slim)', buyTarget: 260, resaleAvg: 390, keywords: ['ps5', 'ps5 disco', 'ps5 standard', 'playstation 5', 'ps5 slim'] },
  { id: 'xbox-series-s', category: 'gaming', name: 'Xbox Series S (512 GB)', buyTarget: 110, resaleAvg: 175, keywords: ['series s', 'xbox series s'] },
  { id: 'xbox-series-x', category: 'gaming', name: 'Xbox Series X (1 TB)', buyTarget: 240, resaleAvg: 360, keywords: ['series x', 'xbox series x'] },

  // Samsung Galaxy
  { id: 'samsung-s21-128', category: 'samsung', name: 'Samsung Galaxy S21 5G (128 GB)', buyTarget: 110, resaleAvg: 185, keywords: ['s21', 'galaxy s21', 'samsung s21'] },
  { id: 'samsung-s22-128', category: 'samsung', name: 'Samsung Galaxy S22 (128 GB)', buyTarget: 160, resaleAvg: 260, keywords: ['s22', 'galaxy s22', 'samsung s22'] },
  { id: 'samsung-s23-128', category: 'samsung', name: 'Samsung Galaxy S23 (128/256 GB)', buyTarget: 260, resaleAvg: 390, keywords: ['s23', 'galaxy s23', 'samsung s23'] },
  { id: 'samsung-zflip-4', category: 'samsung', name: 'Samsung Galaxy Z Flip 4', buyTarget: 150, resaleAvg: 250, keywords: ['z flip 4', 'flip 4'] }
];

// PWA Installation & Service Worker Handling
let deferredPrompt = null;
const btnInstallPwa = document.getElementById('btnInstallPwa');
const iosInstallBanner = document.getElementById('iosInstallBanner');
const btnCloseIosBanner = document.getElementById('btnCloseIosBanner');

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(reg => console.log('⚡ PWA Service Worker registrato con successo:', reg.scope))
      .catch(err => console.error('Errore registrazione Service Worker:', err));
  });
}

// Handle Android/Chrome PWA install prompt
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  if (btnInstallPwa) {
    btnInstallPwa.style.display = 'inline-flex';
  }
});

// Handle iOS Safari banner detection
function checkIosPwa() {
  const isIos = /iphone|ipad|ipod/.test(window.navigator.userAgent.toLowerCase());
  const isStandalone = window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches;
  if (isIos && !isStandalone && iosInstallBanner) {
    iosInstallBanner.style.display = 'flex';
  }
}

// App State
let currentAnalysis = null;
let currentScriptType = 'subito';
let savedDeals = JSON.parse(localStorage.getItem('flipradar_deals') || '[]');

// DOM Elements
const rawAdInput = document.getElementById('rawAdInput');
const btnClearInput = document.getElementById('btnClearInput');
const btnAnalyze = document.getElementById('btnAnalyze');
const resultContainer = document.getElementById('resultContainer');
const toastNotification = document.getElementById('toastNotification');
const toastMessage = document.getElementById('toastMessage');

// Verdict DOM Elements
const verdictBanner = document.getElementById('verdictBanner');
const verdictIcon = document.getElementById('verdictIcon');
const verdictBadge = document.getElementById('verdictBadge');
const scoreBadge = document.getElementById('scoreBadge');
const verdictTitle = document.getElementById('verdictTitle');
const verdictDescription = document.getElementById('verdictDescription');

// Metrics DOM Elements
const resAskingPrice = document.getElementById('resAskingPrice');
const resTargetOffer = document.getElementById('resTargetOffer');
const resDiscountPct = document.getElementById('resDiscountPct');
const resResaleValue = document.getElementById('resResaleValue');
const resEstimatedProfit = document.getElementById('resEstimatedProfit');
const resRoiPct = document.getElementById('resRoiPct');

// Strategy Bar
const strategyLowOffer = document.getElementById('strategyLowOffer');
const strategyTargetOffer = document.getElementById('strategyTargetOffer');
const strategyMaxOffer = document.getElementById('strategyMaxOffer');

// Scripts
const scriptContentText = document.getElementById('scriptContentText');
const btnCopyScript = document.getElementById('btnCopyScript');
const copyBtnText = document.getElementById('copyBtnText');

// Checklist & Save
const checklistItemsContainer = document.getElementById('checklistItemsContainer');
const btnSaveDeal = document.getElementById('btnSaveDeal');

// Tabs & DB
const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanels = document.querySelectorAll('.tab-panel');
const dbTableBody = document.getElementById('dbTableBody');
const dbSearchInput = document.getElementById('dbSearchInput');
const catChips = document.querySelectorAll('.cat-chip');

// Tracker Elements
const activeDealsCount = document.getElementById('activeDealsCount');
const statTotalProfit = document.getElementById('statTotalProfit');
const statDealsClosed = document.getElementById('statDealsClosed');
const statDealsPending = document.getElementById('statDealsPending');
const dealsListContainer = document.getElementById('dealsListContainer');
const emptyDealsState = document.getElementById('emptyDealsState');
const btnExportDeals = document.getElementById('btnExportDeals');

// Init App
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  renderPricingTable('all', '');
  updateTrackerUI();
  checkIosPwa();
});

function setupEventListeners() {
  // PWA Install Button Click
  if (btnInstallPwa) {
    btnInstallPwa.addEventListener('click', async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`User response to install prompt: ${outcome}`);
        deferredPrompt = null;
        btnInstallPwa.style.display = 'none';
      }
    });
  }

  // iOS Banner Close
  if (btnCloseIosBanner && iosInstallBanner) {
    btnCloseIosBanner.addEventListener('click', () => {
      iosInstallBanner.style.display = 'none';
    });
  }

  // Navigation
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab');
      switchTab(tabId);
    });
  });

  // Example chips
  document.querySelectorAll('.chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      rawAdInput.value = btn.getAttribute('data-example');
      analyzeInput();
    });
  });

  // Clear button
  btnClearInput.addEventListener('click', () => {
    rawAdInput.value = '';
    rawAdInput.focus();
  });

  // Analyze button
  btnAnalyze.addEventListener('click', analyzeInput);
  rawAdInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      analyzeInput();
    }
  });

  // Script Tabs
  document.querySelectorAll('.script-tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.script-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentScriptType = btn.getAttribute('data-script');
      updateScriptText();
    });
  });

  // Copy Script Button
  btnCopyScript.addEventListener('click', () => {
    const text = scriptContentText.innerText;
    navigator.clipboard.writeText(text).then(() => {
      showToast('Messaggio copiato negli appunti! Pronti ad incollare.');
      copyBtnText.innerText = 'Copiato! ✓';
      setTimeout(() => {
        copyBtnText.innerText = 'Copia Messaggio';
      }, 2000);
    });
  });

  // Save Deal Button
  btnSaveDeal.addEventListener('click', saveCurrentDeal);

  // DB Filters
  if (dbSearchInput) {
    dbSearchInput.addEventListener('input', (e) => {
      const activeCat = document.querySelector('.cat-chip.active')?.getAttribute('data-cat') || 'all';
      renderPricingTable(activeCat, e.target.value.toLowerCase());
    });
  }

  catChips.forEach(chip => {
    chip.addEventListener('click', () => {
      catChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const cat = chip.getAttribute('data-cat');
      const query = dbSearchInput ? dbSearchInput.value.toLowerCase() : '';
      renderPricingTable(cat, query);
    });
  });

  // Export
  if (btnExportDeals) {
    btnExportDeals.addEventListener('click', exportDealsJSON);
  }
}

function switchTab(tabId) {
  tabBtns.forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
  });
  tabPanels.forEach(panel => {
    panel.classList.toggle('active', panel.id === tabId);
  });
}

/**
 * Smart Natural Language Parser for ad listings
 */
function parseAdText(text) {
  const clean = text.toLowerCase();
  
  // Extract Price (e.g. 220euro, 220€, 220 euro, 220 €)
  let extractedPrice = null;
  const priceRegex = /(\d{2,4})\s*(?:€|euro|eur)/i;
  const priceMatch = clean.match(priceRegex);
  if (priceMatch) {
    extractedPrice = parseInt(priceMatch[1], 10);
  } else {
    // Look for standalone numbers like "220"
    const standaloneNumbers = clean.match(/\b\d{2,4}\b/g);
    if (standaloneNumbers) {
      // Pick the most likely price number
      for (const num of standaloneNumbers) {
        const val = parseInt(num, 10);
        if (val >= 30 && val <= 2500) {
          extractedPrice = val;
          break;
        }
      }
    }
  }

  // Identify Best Matching Item from Database
  let bestMatch = null;
  let bestScore = 0;

  for (const item of MARKET_DATABASE) {
    let score = 0;
    for (const kw of item.keywords) {
      if (clean.includes(kw)) {
        score += kw.length; // weight by keyword precision
      }
    }
    if (score > bestScore) {
      bestScore = score;
      bestMatch = item;
    }
  }

  // Fallback if no specific model matched
  if (!bestMatch) {
    if (clean.includes('iphone')) {
      bestMatch = MARKET_DATABASE.find(d => d.id === 'iphone-12-128');
    } else if (clean.includes('switch')) {
      bestMatch = MARKET_DATABASE.find(d => d.id === 'switch-oled');
    } else if (clean.includes('ps5')) {
      bestMatch = MARKET_DATABASE.find(d => d.id === 'ps5-disk');
    } else {
      bestMatch = {
        id: 'generic-device',
        category: 'elettronica',
        name: 'Dispositivo Rilevato',
        buyTarget: extractedPrice ? Math.round(extractedPrice * 0.7) : 100,
        resaleAvg: extractedPrice ? Math.round(extractedPrice * 1.25) : 150
      };
    }
  }

  // Extract battery info if any
  let batteryHealth = null;
  const batteryMatch = clean.match(/batteria\s*(\d{2,3})%?/i) || clean.match(/(\d{2,3})%\s*(?:batteria|stato)/i);
  if (batteryMatch) {
    batteryHealth = parseInt(batteryMatch[1], 10);
  }

  return {
    rawText: text,
    matchedItem: bestMatch,
    askingPrice: extractedPrice || (bestMatch.resaleAvg * 0.9),
    batteryHealth: batteryHealth
  };
}

/**
 * Main Analysis Handler
 */
function analyzeInput() {
  const input = rawAdInput.value.trim();
  if (!input) {
    showToast('Inserisci il testo di un annuncio o il nome del modello!');
    rawAdInput.focus();
    return;
  }

  const parsed = parseAdText(input);
  const item = parsed.matchedItem;
  const asking = parsed.askingPrice;
  const resale = item.resaleAvg;

  // Calculation Logic
  const lowOffer = Math.round(item.buyTarget * 0.9);
  const targetOffer = item.buyTarget;
  const maxOffer = Math.round(item.buyTarget * 1.12);

  const estimatedProfit = resale - targetOffer;
  const roiPct = Math.round((estimatedProfit / targetOffer) * 100);
  const discountPct = Math.round(((asking - targetOffer) / asking) * 100);

  // Deal Scoring
  let score = 5;
  let verdictType = 'warning'; // 'great', 'warning', 'danger'
  let verdictTitleText = '';
  let verdictDescText = '';
  let verdictBadgeText = '';

  if (asking <= targetOffer) {
    // Instant gold deal
    score = 9.5;
    verdictType = 'great';
    verdictBadgeText = '🔥 AFFARE D\'ORO';
    verdictTitleText = 'Prezzo Già Basso: Compra Subito!';
    verdictDescText = `Il venditore chiede già ${asking}€ (sotto o pari al target di ${targetOffer}€). Fai una piccola offerta di ${lowOffer}€ o prendilo subito prima che lo veda qualcun altro!`;
  } else if (asking <= maxOffer) {
    score = 8.0;
    verdictType = 'great';
    verdictBadgeText = '✅ OTTIMO AFFARE (DA TRATTARE)';
    verdictTitleText = 'Margine Alto: Invia l\'Offerta Target';
    verdictDescText = `Chiede ${asking}€, ma offrendo ${targetOffer}€ ottieni un profitto netto di circa +${estimatedProfit}€ (+${roiPct}% ROI) rivendendo a ${resale}€.`;
  } else if (asking <= resale * 0.95) {
    score = 6.5;
    verdictType = 'warning';
    verdictBadgeText = '⚠️ MARGINE MEDIO / TRATTATIVA DURA';
    verdictTitleText = 'Serve uno Sconto Deciso (-30%)';
    verdictDescText = `A ${asking}€ il margine è troppo rischioso. Devi proporre ${targetOffer}€ (sconto di ${discountPct}%) puntando sul ritiro a mano immediato in contanti.`;
  } else {
    score = 3.5;
    verdictType = 'danger';
    verdictBadgeText = '❌ PREZZO FUORI MERCATO';
    verdictTitleText = 'Sovrapprezzato: Tentare Lowball o Passare';
    verdictDescText = `Chiede ${asking}€ per un oggetto che vale ${resale}€ sul mercato dell'usato a Torino. Fai comunque un'offerta a ${lowOffer}€, ma non spendere più di ${maxOffer}€.`;
  }

  currentAnalysis = {
    parsed,
    item,
    asking,
    resale,
    lowOffer,
    targetOffer,
    maxOffer,
    estimatedProfit,
    roiPct,
    discountPct,
    score,
    verdictType,
    verdictTitleText,
    verdictDescText,
    verdictBadgeText
  };

  renderAnalysisResult();
}

/**
 * Render Analysis Result to UI
 */
function renderAnalysisResult() {
  const d = currentAnalysis;
  if (!d) return;

  // Show container
  resultContainer.style.display = 'block';

  // Verdict Banner
  verdictBanner.className = `verdict-banner ${d.verdictType}`;
  verdictIcon.innerText = d.verdictType === 'great' ? '🔥' : (d.verdictType === 'warning' ? '⚡' : '🛑');
  verdictBadge.innerText = d.verdictBadgeText;
  scoreBadge.innerText = `Affare: ${d.score}/10`;
  verdictTitle.innerText = d.verdictTitleText;
  verdictDescription.innerText = d.verdictDescText;

  // Numbers Grid
  resAskingPrice.innerText = `${d.asking} €`;
  resTargetOffer.innerText = `${d.targetOffer} €`;
  resDiscountPct.innerText = d.discountPct > 0 ? `-${d.discountPct}%` : `0%`;
  resResaleValue.innerText = `${d.resale} €`;
  resEstimatedProfit.innerText = `+${d.estimatedProfit} €`;
  resRoiPct.innerText = `+${d.roiPct}%`;

  // Strategy Bar
  strategyLowOffer.innerText = `${d.lowOffer} €`;
  strategyTargetOffer.innerText = `${d.targetOffer} € - ${Math.round((d.targetOffer + d.maxOffer) / 2)} €`;
  strategyMaxOffer.innerText = `${d.maxOffer} €`;

  // Scripts
  updateScriptText();

  // Checklist
  renderChecklist(d.item.category);

  // Smooth scroll to result
  resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Generates tailored negotiation scripts
 */
function updateScriptText() {
  if (!currentAnalysis) return;
  const d = currentAnalysis;
  const itemName = d.item.name;
  const targetPrice = d.targetOffer;
  const lowPrice = d.lowOffer;

  let script = '';

  if (currentScriptType === 'subito') {
    script = `Ciao! Sono di Torino e sono molto interessato al tuo ${itemName}. 
Se il dispositivo è in buone condizioni e perfettamente funzionante, posso offrirti ${targetPrice}€ e venire a ritirarlo di persona oggi stesso con pagamento immediato in contanti. 
Se per te va bene concludiamo subito, fammi sapere dove ci possiamo incontrare!`;
  } else if (currentScriptType === 'whatsapp') {
    script = `Buongiorno! Ti scrivo per l'annuncio del ${itemName}. Sono di Torino e posso fare ritiro a mano oggi stesso a ${targetPrice}€ in contanti. Fammi sapere se posso passare, grazie!`;
  } else if (currentScriptType === 'counter') {
    script = `Capisco perfettamente la tua richiesta! Il massimo a cui posso arrivare per concludere subito oggi senza farti perdere tempo è ${Math.round((targetPrice + d.maxOffer) / 2)}€ in contanti sul posto. Se cambi idea o non dovessi concludere con altri, la mia offerta rimane valida! Buona giornata.`;
  } else if (currentScriptType === 'questions') {
    script = `Ciao! Prima di definire l'acquisto volevo farti un paio di verifiche rapide:
1. Lo stato della batteria a che percentuale è?
2. Schermo o altri componenti sono mai stati sostituiti?
3. È presente la scatola originale con gli accessori?
Grazie mille!`;
  }

  scriptContentText.innerText = script;
}

/**
 * Render Device Checklist based on category
 */
function renderChecklist(category) {
  let checks = [];

  if (category === 'iphone') {
    checks = [
      { title: 'Blocco iCloud / Reset Fabbrica', desc: 'Verifica che il telefono sia ripristinato e disattivato da "Dov\'è". MAI comprare se bloccato.' },
      { title: 'True Tone e Display Originale', desc: 'Scorri il Centro di Controllo -> tieni premuto Luminosità -> controlla se True Tone è presente. Se manca, schermo sostituito.' },
      { title: 'Face ID / Touch ID Funzionante', desc: 'Configura il volto o l\'impronta per verificare i sensori biometrici.' },
      { title: 'Stato Batteria', desc: 'Impostazioni -> Batteria -> Stato. Ideale >80-85%. Nessun messaggio di "Batteria sconosciuta".' },
      { title: 'Fotocamere (0.5x, 1x, Zoom) e Microfoni', desc: 'Fai una registrazione vocale e un breve video per testare microfono superiore e inferiore.' }
    ];
  } else if (category === 'gaming') {
    checks = [
      { title: 'Connessione a Internet & Nessun Ban', desc: 'Verifica che la console acceda a PSN / Nintendo Online senza errori di ban della console.' },
      { title: 'Porta HDMI e Lettore Dischi', desc: 'Controlla che i pin HDMI siano dritti e che il lettore carichi ed espella i dischi senza rumori anomali.' },
      { title: 'Drift Joystick & Pulsanti', desc: 'Muovi le levette analogiche per escludere problemi di deriva.' },
      { title: 'Rumore Ventola / Surriscaldamento', desc: 'Accertati che non emetta forti sibili da polvere intasata.' }
    ];
  } else if (category === 'apple') {
    checks = [
      { title: 'Autenticità & Seriale Apple', desc: 'Inserisci il numero di serie su checkcoverage.apple.com.' },
      { title: 'Cancellazione Attiva del Rumore (ANC)', desc: 'Nelle AirPods Pro verifica che l\'isolamento acustico e l\'audio spaziale funzionino realmente.' },
      { title: 'Disaccoppiamento Apple ID', desc: 'Assicurati che il precedente proprietario abbia rimosso il dispositivo dal suo account.' }
    ];
  } else {
    checks = [
      { title: 'Reset Account Google / FRP', desc: 'Assicurati che tutti gli account siano stati rimossi prima del ripristino.' },
      { title: 'Touchscreen completo & Schermo OLED', desc: 'Digita il codice test (*#0*# su Samsung) per verificare pixel bruciati o ghosting.' },
      { title: 'Porta di Ricarica USB-C & Connettività', desc: 'Inserisci un cavo per controllare che carichi stabilmente.' }
    ];
  }

  checklistItemsContainer.innerHTML = checks.map((c, idx) => `
    <label class="check-item" for="chk_${idx}">
      <input type="checkbox" id="chk_${idx}">
      <div class="check-item-text">
        <div class="check-item-title">${c.title}</div>
        <div class="check-item-desc">${c.desc}</div>
      </div>
    </label>
  `).join('');
}

/**
 * Save Current Deal to Tracker
 */
function saveCurrentDeal() {
  if (!currentAnalysis) return;
  const d = currentAnalysis;

  const newDeal = {
    id: 'deal_' + Date.now(),
    name: d.item.name,
    category: d.item.category,
    askingPrice: d.asking,
    targetPrice: d.targetOffer,
    resaleEst: d.resale,
    expectedProfit: d.estimatedProfit,
    status: 'negotiating', // 'negotiating', 'purchased', 'sold'
    date: new Date().toLocaleDateString('it-IT'),
    actualBuyPrice: null,
    actualSellPrice: null
  };

  savedDeals.unshift(newDeal);
  localStorage.setItem('flipradar_deals', JSON.stringify(savedDeals));
  updateTrackerUI();
  showToast('Affare salvato nei tuoi tracker!');
  switchTab('tracker-tab');
}

/**
 * Pricing Table (Tab 2)
 */
function renderPricingTable(category = 'all', query = '') {
  if (!dbTableBody) return;

  const filtered = MARKET_DATABASE.filter(item => {
    const matchCat = category === 'all' || item.category === category;
    const matchQuery = !query || item.name.toLowerCase().includes(query) || item.keywords.some(k => k.includes(query));
    return matchCat && matchQuery;
  });

  if (filtered.length === 0) {
    dbTableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 24px;">Nessun dispositivo trovato.</td></tr>`;
    return;
  }

  dbTableBody.innerHTML = filtered.map(item => {
    const profit = item.resaleAvg - item.buyTarget;
    return `
      <tr>
        <td class="device-name">${item.name}</td>
        <td class="target-buy">${item.buyTarget} €</td>
        <td class="resale-val">${item.resaleAvg} €</td>
        <td class="net-profit">+${profit} €</td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="quickAnalyzeFromDb('${item.id}')">Analizza</button>
        </td>
      </tr>
    `;
  }).join('');
}

// Global scope for onclick
window.quickAnalyzeFromDb = function(itemId) {
  const item = MARKET_DATABASE.find(i => i.id === itemId);
  if (!item) return;

  rawAdInput.value = `${item.name} a ${Math.round(item.resaleAvg * 0.85)} euro Torino`;
  switchTab('analyzer-tab');
  analyzeInput();
};

/**
 * Update Tracker UI & Summary Stats (Tab 3)
 */
function updateTrackerUI() {
  if (activeDealsCount) activeDealsCount.innerText = savedDeals.length;

  let totalProfitRealized = 0;
  let closedCount = 0;
  let pendingCount = 0;

  savedDeals.forEach(deal => {
    if (deal.status === 'sold') {
      closedCount++;
      const realized = (deal.actualSellPrice || deal.resaleEst) - (deal.actualBuyPrice || deal.targetPrice);
      totalProfitRealized += realized;
    } else {
      pendingCount++;
    }
  });

  if (statTotalProfit) statTotalProfit.innerText = `+${totalProfitRealized} €`;
  if (statDealsClosed) statDealsClosed.innerText = closedCount;
  if (statDealsPending) statDealsPending.innerText = pendingCount;

  if (savedDeals.length === 0) {
    if (emptyDealsState) emptyDealsState.style.display = 'block';
    if (dealsListContainer) dealsListContainer.innerHTML = '';
    return;
  }

  if (emptyDealsState) emptyDealsState.style.display = 'none';

  dealsListContainer.innerHTML = savedDeals.map(deal => {
    let statusClass = 'status-negotiating';
    let statusText = 'In Trattativa';
    if (deal.status === 'purchased') {
      statusClass = 'status-purchased';
      statusText = 'Acquistato (Da Rivendere)';
    } else if (deal.status === 'sold') {
      statusClass = 'status-sold';
      statusText = 'Rivenduto (Chiuso)';
    }

    return `
      <div class="deal-item">
        <div class="deal-main">
          <div class="deal-title">${deal.name}</div>
          <div class="deal-meta">
            Target d'acquisto: <b>${deal.targetPrice}€</b> | Rivendita stimata: <b>${deal.resaleEst}€</b> (${deal.date})
          </div>
          <div style="margin-top: 6px;">
            <span class="deal-status-badge ${statusClass}">${statusText}</span>
          </div>
        </div>

        <div class="deal-actions">
          ${deal.status === 'negotiating' ? `
            <button class="btn btn-secondary btn-sm" onclick="setDealStatus('${deal.id}', 'purchased')">Ho Comprato</button>
          ` : ''}
          ${deal.status === 'purchased' ? `
            <button class="btn btn-primary btn-sm" onclick="setDealStatus('${deal.id}', 'sold')">Ho Rivenduto</button>
          ` : ''}
          <button class="btn btn-secondary btn-sm" title="Elimina" onclick="deleteDeal('${deal.id}')">🗑️</button>
        </div>
      </div>
    `;
  }).join('');
}

window.setDealStatus = function(dealId, newStatus) {
  const deal = savedDeals.find(d => d.id === dealId);
  if (!deal) return;

  if (newStatus === 'purchased') {
    const buyPrice = prompt('A quanto l\'hai acquistato (€)?', deal.targetPrice);
    if (buyPrice !== null) {
      deal.actualBuyPrice = parseInt(buyPrice, 10) || deal.targetPrice;
      deal.status = 'purchased';
    }
  } else if (newStatus === 'sold') {
    const sellPrice = prompt('A quanto l\'hai rivenduto (€)?', deal.resaleEst);
    if (sellPrice !== null) {
      deal.actualSellPrice = parseInt(sellPrice, 10) || deal.resaleEst;
      deal.status = 'sold';
    }
  }

  localStorage.setItem('flipradar_deals', JSON.stringify(savedDeals));
  updateTrackerUI();
};

window.deleteDeal = function(dealId) {
  if (confirm('Vuoi rimuovere questo affare dal registro?')) {
    savedDeals = savedDeals.filter(d => d.id !== dealId);
    localStorage.setItem('flipradar_deals', JSON.stringify(savedDeals));
    updateTrackerUI();
  }
};

function exportDealsJSON() {
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(savedDeals, null, 2));
  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute("href", dataStr);
  downloadAnchor.setAttribute("download", `flipradar_affari_${Date.now()}.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
}

/**
 * Toast Notification Helper
 */
function showToast(msg) {
  if (!toastNotification || !toastMessage) return;
  toastMessage.innerText = msg;
  toastNotification.classList.add('show');
  setTimeout(() => {
    toastNotification.classList.remove('show');
  }, 2500);
}
