import Hls from 'hls.js';
import mpegts from 'mpegts.js';

const m3uUrlInput = document.getElementById('m3u-url');
const loadM3uBtn = document.getElementById('load-m3u');
const m3uFileInput = document.getElementById('m3u-file');
const loadFileBtn = document.getElementById('load-file-btn');
const mainListEl = document.getElementById('main-list');
const searchInput = document.getElementById('search-input');
const video = document.getElementById('video-player');
const channelTitleEl = document.getElementById('channel-title');
const channelGroupEl = document.getElementById('channel-group');
const nowPlayingInfo = document.getElementById('now-playing-info');
const tabBtns = document.querySelectorAll('.tab-btn');

let channels = [];
let groups = {};
let hls = null;
let tsPlayer = null;
let currentTab = 'all'; 
let currentGroupFilter = null;

// Gestione Preferiti tramite localStorage
let favorites = JSON.parse(localStorage.getItem('streampro_favs') || '[]');

function saveFavorites() {
  localStorage.setItem('streampro_favs', JSON.stringify(favorites));
}

function toggleFavorite(channel, btn) {
  const index = favorites.findIndex(f => f.url === channel.url);
  if (index > -1) {
    favorites.splice(index, 1);
    btn.classList.remove('is-fav');
    btn.textContent = '☆';
  } else {
    favorites.push(channel);
    btn.classList.add('is-fav');
    btn.textContent = '★';
  }
  saveFavorites();
  
  if (currentTab === 'favs') {
    renderChannels(favorites);
  }
}

// Inizializza Web Worker per parsing in background
const parserWorker = new Worker(new URL('./worker.js', import.meta.url));

let workerCallback = null;
parserWorker.onmessage = function(e) {
  const data = e.data;
  if (data.type === 'progress' && workerCallback) {
    workerCallback.onProgress(data.percent);
  } else if (data.type === 'done' && workerCallback) {
    workerCallback.onDone(data.channels, data.groups);
  }
};

function parseM3UWorker(content, onProgress, onDone) {
  workerCallback = { onProgress, onDone };
  parserWorker.postMessage(content);
}


let currentRenderLimit = 50;
let currentFilteredData = [];
let observer = null;

function renderChannels(channelData, append = false) {
  if (!append) {
    mainListEl.innerHTML = '';
    currentFilteredData = channelData;
    currentRenderLimit = 50;
  }
  
  if (currentFilteredData.length === 0) {
    mainListEl.innerHTML = '<li class="placeholder">Nessun elemento trovato</li>';
    return;
  }

  const start = append ? currentRenderLimit - 50 : 0;
  const end = currentRenderLimit;
  const toRender = currentFilteredData.slice(start, end);

  toRender.forEach(channel => {
    const li = document.createElement('li');
    li.className = 'channel-item';
    
    const isFav = favorites.some(f => f.url === channel.url);
    
    li.innerHTML = `
      <img class="channel-logo" src="${channel.logo || 'https://via.placeholder.com/50x50/334155/94a3b8?text=TV'}" alt="logo" onerror="this.onerror=null; this.src='https://via.placeholder.com/50x50/334155/94a3b8?text=TV'" />
      <div class="channel-info">
        <span class="channel-name">${channel.name}</span>
        <span class="channel-group">${channel.group}</span>
      </div>
      <button class="fav-btn ${isFav ? 'is-fav' : ''}">${isFav ? '★' : '☆'}</button>
    `;
    
    const favBtn = li.querySelector('.fav-btn');
    favBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleFavorite(channel, favBtn);
    });
    
    li.addEventListener('click', () => {
      document.querySelectorAll('.channel-item').forEach(el => el.classList.remove('active'));
      li.classList.add('active');
      playChannel(channel);
      
      // Scorri verso l'alto per far vedere il player all'utente su mobile!
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    // Doppio click per andare a schermo intero
    li.addEventListener('dblclick', () => {
      if (video.requestFullscreen) {
        video.requestFullscreen();
      } else if (video.webkitRequestFullscreen) { /* Safari */
        video.webkitRequestFullscreen();
      }
    });
    
    mainListEl.appendChild(li);
  });

  // Setup infinite scroll observer
  if (observer) {
    observer.disconnect();
  }
  
  if (currentRenderLimit < currentFilteredData.length) {
    const sentinel = document.createElement('li');
    sentinel.className = 'placeholder';
    sentinel.textContent = 'Caricamento altri...';
    mainListEl.appendChild(sentinel);

    observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        observer.unobserve(sentinel);
        sentinel.remove();
        currentRenderLimit += 50;
        renderChannels([], true);
      }
    }, { root: mainListEl, rootMargin: '100px' });
    
    observer.observe(sentinel);
  }
}

function renderGroups() {
  mainListEl.innerHTML = '';
  const groupNames = Object.keys(groups).sort();
  
  if (groupNames.length === 0) {
    mainListEl.innerHTML = '<li class="placeholder">Nessuna categoria trovata</li>';
    return;
  }

  // Optimize groups render too
  const maxRenderGroups = 200;
  const toRender = groupNames.slice(0, maxRenderGroups);

  toRender.forEach(g => {
    const li = document.createElement('li');
    li.className = 'group-item';
    li.innerHTML = `
      <div class="channel-info">
        <span class="group-name">${g}</span>
        <span class="group-count">${groups[g]} canali</span>
      </div>
    `;
    
    li.addEventListener('click', () => {
      currentGroupFilter = g;
      currentTab = 'all';
      updateTabButtons();
      const filtered = channels.filter(c => c.group === g);
      renderChannels(filtered);
    });
    
    mainListEl.appendChild(li);
  });

  if (groupNames.length > maxRenderGroups) {
    const li = document.createElement('li');
    li.className = 'placeholder';
    li.textContent = 'Cerca le altre categorie usando la barra di ricerca...';
    mainListEl.appendChild(li);
  }
}

function playChannel(channel) {
  channelTitleEl.textContent = channel.name;
  channelGroupEl.textContent = channel.group;
  nowPlayingInfo.classList.add('visible');
  
  setTimeout(() => {
    nowPlayingInfo.classList.remove('visible');
  }, 5000);

  // Distruggi i player precedenti
  if (hls) {
    hls.destroy();
    hls = null;
  }
  if (tsPlayer) {
    tsPlayer.destroy();
    tsPlayer = null;
  }

  const isTs = channel.url.toLowerCase().split('?')[0].endsWith('.ts');

  if (isTs && mpegts.getFeatureList().mseLivePlayback) {
    try {
      tsPlayer = mpegts.createPlayer({
        type: 'mpegts',
        isLive: true,
        url: channel.url
      });
      tsPlayer.attachMediaElement(video);
      tsPlayer.load();
      tsPlayer.play().catch(e => console.log(e));

      tsPlayer.on(mpegts.Events.ERROR, (errorType, errorDetail, errorInfo) => {
        channelTitleEl.textContent = "❌ " + channel.name;
        channelGroupEl.textContent = "Blocco Sicurezza Server (CORS/User-Agent)";
        nowPlayingInfo.classList.add('visible');
      });
    } catch (e) {
      console.error('MpegTS error:', e);
    }
  } else if (Hls.isSupported()) {
    hls = new Hls();
    hls.loadSource(channel.url);
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED, () => {
      video.play().catch(e => console.log(e));
    });
    hls.on(Hls.Events.ERROR, function (event, data) {
      if (data.fatal) {
        channelTitleEl.textContent = "❌ " + channel.name;
        channelGroupEl.textContent = "Blocco Sicurezza Server o Canale Offline";
        nowPlayingInfo.classList.add('visible');
        if (data.type === Hls.ErrorTypes.NETWORK_ERROR) {
          hls.destroy();
        }
      }
    });
  } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = channel.url;
    video.addEventListener('loadedmetadata', () => {
      video.play().catch(e => console.log(e));
    });
    video.addEventListener('error', () => {
      channelTitleEl.textContent = "❌ " + channel.name;
      channelGroupEl.textContent = "Canale Offline";
      nowPlayingInfo.classList.add('visible');
    });
  } else {
    video.src = channel.url;
    video.play().catch(e => console.log(e));
  }
}

// Doppio clic sul video stesso per lo schermo intero
video.addEventListener('dblclick', () => {
  if (!document.fullscreenElement) {
    if (video.requestFullscreen) video.requestFullscreen();
    else if (video.webkitRequestFullscreen) video.webkitRequestFullscreen();
  } else {
    if (document.exitFullscreen) document.exitFullscreen();
    else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
  }
});

// Carica M3U URL
loadM3uBtn.addEventListener('click', async () => {
  const url = m3uUrlInput.value.trim();
  if (!url) return;
  
  try {
    loadM3uBtn.textContent = 'Scaricamento...';
    const proxyUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(url)}`;
    const response = await fetch(proxyUrl);
    const data = await response.json();
    
    if (data.contents) {
      loadM3uBtn.textContent = 'Parsing in background...';
      parseM3UWorker(data.contents, 
        (percent) => {
          loadM3uBtn.textContent = `Analisi... ${percent}%`;
        },
        (resChannels, resGroups) => {
          channels = resChannels;
          groups = resGroups;
          currentGroupFilter = null;
          document.querySelector('[data-tab="all"]').click();
          loadM3uBtn.textContent = 'Carica da URL';
        }
      );
    } else {
      alert("Errore nel caricamento della playlist");
      loadM3uBtn.textContent = 'Carica da URL';
    }
  } catch (err) {
    console.error(err);
    alert("Errore di rete o URL non valido");
    loadM3uBtn.textContent = 'Carica da URL';
  }
});

// Carica file M3U locale
if (loadFileBtn && m3uFileInput) {
  loadFileBtn.addEventListener('click', () => {
    m3uFileInput.click();
  });

  m3uFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const originalText = loadFileBtn.textContent;
    const reader = new FileReader();
    
    reader.onprogress = (event) => {
      if (event.lengthComputable) {
        const percentLoaded = Math.round((event.loaded / event.total) * 100);
        loadFileBtn.textContent = `Lettura file... ${percentLoaded}%`;
      }
    };

    reader.onload = (event) => {
      loadFileBtn.textContent = 'Avvio analisi in background...';
      const content = event.target.result;
      
      parseM3UWorker(content, 
        (percent) => {
          loadFileBtn.textContent = `Analisi canali: ${percent}%`;
        }, 
        (resChannels, resGroups) => {
          channels = resChannels;
          groups = resGroups;
          currentGroupFilter = null;
          document.querySelector('[data-tab="all"]').click();
          loadFileBtn.textContent = originalText;
        }
      );
    };
    reader.readAsText(file);
    e.target.value = '';
  });
}

// Gestione Tabs
function updateTabButtons() {
  tabBtns.forEach(b => {
    b.classList.remove('active');
    if (b.dataset.tab === currentTab) b.classList.add('active');
  });
}

tabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    currentTab = btn.dataset.tab;
    currentGroupFilter = null;
    updateTabButtons();
    searchInput.value = '';
    
    if (currentTab === 'all') {
      renderChannels(channels);
    } else if (currentTab === 'groups') {
      renderGroups();
    } else if (currentTab === 'favs') {
      renderChannels(favorites);
    }
  });
});

// Ricerca
searchInput.addEventListener('input', (e) => {
  const term = e.target.value.toLowerCase();
  
  if (currentTab === 'groups') {
    mainListEl.innerHTML = '';
    const filteredGroups = Object.keys(groups).filter(g => g.toLowerCase().includes(term));
    const toRender = filteredGroups.slice(0, 200);
    toRender.forEach(g => {
      const li = document.createElement('li');
      li.className = 'group-item';
      li.innerHTML = `<div class="channel-info"><span class="group-name">${g}</span></div>`;
      li.addEventListener('click', () => {
        currentGroupFilter = g;
        currentTab = 'all';
        updateTabButtons();
        renderChannels(channels.filter(c => c.group === g));
      });
      mainListEl.appendChild(li);
    });
  } else {
    const sourceList = currentTab === 'favs' ? favorites : channels;
    let filtered = sourceList.filter(c => 
      c.name.toLowerCase().includes(term) || 
      c.group.toLowerCase().includes(term)
    );
    if (currentGroupFilter) {
      filtered = filtered.filter(c => c.group === currentGroupFilter);
    }
    renderChannels(filtered);
  }
});

// Inizializzazione
if (favorites.length > 0) {
  document.querySelector('[data-tab="favs"]').click();
} else {
  renderChannels(channels);
}
