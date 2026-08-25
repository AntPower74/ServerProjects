// Motore di Valutazione Universale Decoupled (Prezzly Market Intelligence)
// Il valore di rivendita dipende dal PRODOTTO (benchmark reale), mentre il prezzo dell'annuncio serve per la trattativa

// 1. DATABASE COMPLETO SMARTPHONE ANDROID & PIEGHEVOLI (Flip / Fold / Flagship)
export const ANDROID_MODELS = {
  // Pieghevoli (Flip & Fold)
  'nubia flip': { name: 'ZTE Nubia Flip 5G (Pieghavole)', screen: '6.9" OLED Pieghevole 120Hz + Display Esterno', baseResale: 280, retail: '599€', tier: 'Smartphone Pieghevole Flip 5G' },
  'z flip 5': { name: 'Samsung Galaxy Z Flip 5 5G', screen: '6.7" Dynamic AMOLED 2X 120Hz Flex Window', baseResale: 380, retail: '1249€', tier: 'Top di Gamma Pieghevole Samsung' },
  'z flip 4': { name: 'Samsung Galaxy Z Flip 4 5G', screen: '6.7" Dynamic AMOLED 2X 120Hz', baseResale: 270, retail: '1149€', tier: 'Fascia Alta Pieghevole' },
  'z flip 3': { name: 'Samsung Galaxy Z Flip 3 5G', screen: '6.7" Dynamic AMOLED 120Hz', baseResale: 190, retail: '1099€', tier: 'Pieghevole Entry-Level' },
  'z flip': { name: 'Samsung Galaxy Z Flip 5G', screen: '6.7" AMOLED Pieghevole', baseResale: 220, retail: '1099€', tier: 'Pieghevole a Conchiglia' },
  'motorola razr': { name: 'Motorola Razr 40 / 50 Ultra', screen: 'OLED Pieghevole 144Hz / 165Hz', baseResale: 320, retail: '899€', tier: 'Pieghevole Premium Motorola' },
  'razr': { name: 'Motorola Razr', screen: 'OLED Pieghevole', baseResale: 260, retail: '799€', tier: 'Pieghevole Flip' },
  'z fold': { name: 'Samsung Galaxy Z Fold', screen: '7.6" Dynamic AMOLED 2X Pieghevole Tablet', baseResale: 480, retail: '1899€', tier: 'Top di Gamma Foldable Tablet' },

  // Samsung Galaxy S Series
  's24 ultra': { name: 'Samsung Galaxy S24 Ultra', screen: '6.8" Dynamic AMOLED 2X Titanio S-Pen', baseResale: 750, retail: '1499€', tier: 'Top di Gamma Assoluto Android' },
  's24': { name: 'Samsung Galaxy S24 / S24+', screen: 'Dynamic AMOLED 2X 120Hz', baseResale: 480, retail: '929€', tier: 'Fascia Alta Samsung' },
  's23 ultra': { name: 'Samsung Galaxy S23 Ultra', screen: '6.8" Dynamic AMOLED 2X S-Pen', baseResale: 560, retail: '1479€', tier: 'Top di Gamma Galaxy' },
  's23': { name: 'Samsung Galaxy S23', screen: '6.1" Dynamic AMOLED 120Hz', baseResale: 370, retail: '879€', tier: 'Fascia Alta Compatto' },
  's22 ultra': { name: 'Samsung Galaxy S22 Ultra', screen: '6.8" AMOLED 120Hz S-Pen', baseResale: 390, retail: '1279€', tier: 'Fascia Alta' },
  's22': { name: 'Samsung Galaxy S22', screen: '6.1" AMOLED 120Hz', baseResale: 260, retail: '799€', tier: 'Fascia Media-Alta' },
  's21': { name: 'Samsung Galaxy S21 / S21 FE', screen: '6.2" Dynamic AMOLED 120Hz', baseResale: 180, retail: '699€', tier: 'Fascia Media' },
  's20': { name: 'Samsung Galaxy S20 / S20 FE', screen: '6.2" / 6.5" Super AMOLED 120Hz', baseResale: 140, retail: '649€', tier: 'Fascia Media Usato' },
  's10': { name: 'Samsung Galaxy S10 / S10+', screen: '6.1" Dynamic AMOLED Quad HD+', baseResale: 110, retail: '779€', tier: 'Fascia Economica Storica' },
  's9': { name: 'Samsung Galaxy S9 / S9+', screen: '5.8" Super AMOLED Quad HD+', baseResale: 85, retail: '699€', tier: 'Fascia Economica' },
  's8 plus': { name: 'Samsung Galaxy S8+', screen: '6.2" Super AMOLED Infinity Display Quad HD+', baseResale: 75, retail: '929€', tier: 'Flagship Vintage Grande' },
  's8+': { name: 'Samsung Galaxy S8+', screen: '6.2" Super AMOLED Infinity Display Quad HD+', baseResale: 75, retail: '929€', tier: 'Flagship Vintage Grande' },
  's8': { name: 'Samsung Galaxy S8', screen: '5.8" Super AMOLED Infinity Display Quad HD+', baseResale: 65, retail: '829€', tier: 'Flagship Vintage Compatto (Best for Muletto/Backup)' },
  's7': { name: 'Samsung Galaxy S7 / S7 Edge', screen: '5.1" / 5.5" Super AMOLED', baseResale: 45, retail: '729€', tier: 'Fascia Entry Usato' },
  'galaxy s8': { name: 'Samsung Galaxy S8', screen: '5.8" Super AMOLED Infinity Display Quad HD+', baseResale: 65, retail: '829€', tier: 'Flagship Vintage Compatto' },

  // OPPO (Find X, Reno, A Series)
  'find x5 lite': { name: 'OPPO Find X5 Lite 5G (256 GB)', screen: '6.43" AMOLED 90Hz, 8GB + 256GB', baseResale: 140, retail: '499€', tier: 'Fascia Media OPPO (Best-seller 256GB)' },
  'find x5 pro': { name: 'OPPO Find X5 Pro 5G', screen: '6.7" LTPO2 AMOLED 120Hz Hasselblad', baseResale: 280, retail: '1299€', tier: 'Top di Gamma OPPO' },
  'find x5': { name: 'OPPO Find X5 5G', screen: '6.55" OLED 120Hz Hasselblad', baseResale: 200, retail: '999€', tier: 'Fascia Alta OPPO' },
  'find x3 pro': { name: 'OPPO Find X3 Pro 5G', screen: '6.7" AMOLED 120Hz', baseResale: 180, retail: '1149€', tier: 'Ex-Flagship OPPO' },
  'find x3 lite': { name: 'OPPO Find X3 Lite 5G', screen: '6.43" AMOLED 90Hz', baseResale: 100, retail: '499€', tier: 'Fascia Economica OPPO' },
  'oppo reno': { name: 'OPPO Reno Series', screen: 'AMOLED', baseResale: 130, retail: '499€', tier: 'Fascia Media Design' },
  'oppo': { name: 'OPPO Smartphone', screen: 'AMOLED / IPS', baseResale: 110, retail: '399€', tier: 'Fascia Media Android' },

  // Xiaomi / Redmi / POCO
  'xiaomi 13': { name: 'Xiaomi 13 / 13 Pro', screen: 'AMOLED 120Hz Leica', baseResale: 340, retail: '999€', tier: 'Top di Gamma Xiaomi Leica' },
  'xiaomi 12': { name: 'Xiaomi 12 / 12 Pro / 12X', screen: 'AMOLED 120Hz', baseResale: 210, retail: '799€', tier: 'Fascia Alta Xiaomi' },
  'xiaomi 11': { name: 'Xiaomi 11 / 11T Pro', screen: 'AMOLED 120Hz', baseResale: 140, retail: '649€', tier: 'Fascia Media Xiaomi' },
  'redmi note 13': { name: 'Xiaomi Redmi Note 13 / 13 Pro', screen: '6.67" AMOLED 120Hz', baseResale: 140, retail: '299€', tier: 'Best-Seller Fascia Media' },
  'redmi note 12': { name: 'Xiaomi Redmi Note 12 / 12 Pro', screen: '6.67" AMOLED 120Hz', baseResale: 110, retail: '279€', tier: 'Fascia Economica Best-Seller' },
  'redmi note 11': { name: 'Xiaomi Redmi Note 11', screen: '6.43" AMOLED 90Hz', baseResale: 80, retail: '229€', tier: 'Entry-Level Usato' },
  'poco x6': { name: 'POCO X6 / X6 Pro 5G', screen: '6.67" Flow AMOLED 120Hz', baseResale: 180, retail: '349€', tier: 'Best-Buy Performance POCO' },
  'poco f5': { name: 'POCO F5 / F5 Pro', screen: 'AMOLED 120Hz Snapdragon', baseResale: 200, retail: '429€', tier: 'Flagship Killer POCO' },
  'poco x5': { name: 'POCO X5 / X5 Pro 5G', screen: 'AMOLED 120Hz', baseResale: 120, retail: '299€', tier: 'Fascia Media POCO' },

  // Google Pixel
  'pixel 8 pro': { name: 'Google Pixel 8 Pro', screen: '6.7" Super Actua OLED 120Hz', baseResale: 480, retail: '1099€', tier: 'Top di Gamma Google' },
  'pixel 8': { name: 'Google Pixel 8', screen: '6.2" Actua OLED 120Hz', baseResale: 360, retail: '799€', tier: 'Fascia Alta Google' },
  'pixel 7 pro': { name: 'Google Pixel 7 Pro', screen: '6.7" OLED 120Hz', baseResale: 320, retail: '899€', tier: 'Fascia Alta Google' },
  'pixel 7': { name: 'Google Pixel 7 / 7a', screen: 'OLED 90Hz Google Tensor', baseResale: 220, retail: '599€', tier: 'Best-Buy Fotografico' }
}

// 2. DATABASE IPHONE
export const IPHONE_MODELS = {
  '12 mini': { name: 'Apple iPhone 12 Mini', screen: '5.4" OLED', baseResale: { 64: 220, 128: 245, 256: 275 }, launch: '839€', tier: 'Fascia Media Apple (Compatto)' },
  '12 pro max': { name: 'Apple iPhone 12 Pro Max', screen: '6.7" OLED Triple Camera', baseResale: { 128: 380, 256: 420, 512: 460 }, launch: '1289€', tier: 'Fascia Alta Premium' },
  '12 pro': { name: 'Apple iPhone 12 Pro', screen: '6.1" OLED Triple Camera', baseResale: { 128: 320, 256: 350, 512: 390 }, launch: '1189€', tier: 'Fascia Alta Apple' },
  '12': { name: 'Apple iPhone 12', screen: '6.1" OLED Super Retina XDR, A14 Bionic', baseResale: { 64: 230, 128: 260, 256: 290 }, launch: '939€', tier: 'Fascia Media Apple (Best-seller per rapporto qualità/prezzo)' },
  
  '13 mini': { name: 'Apple iPhone 13 Mini', screen: '5.4" OLED Super Retina XDR', baseResale: { 128: 330, 256: 370, 512: 410 }, launch: '839€', tier: 'Fascia Media Apple (Ultimo Mini)' },
  '13 pro max': { name: 'Apple iPhone 13 Pro Max', screen: '6.7" OLED 120Hz ProMotion', baseResale: { 128: 520, 256: 570, 512: 630 }, launch: '1289€', tier: 'Fascia Alta Premium 120Hz' },
  '13 pro': { name: 'Apple iPhone 13 Pro', screen: '6.1" OLED 120Hz ProMotion', baseResale: { 128: 450, 256: 490, 512: 540 }, launch: '1189€', tier: 'Fascia Alta Premium 120Hz' },
  '13': { name: 'Apple iPhone 13', screen: '6.1" OLED Super Retina XDR, A15 Bionic', baseResale: { 128: 380, 256: 420, 512: 460 }, launch: '839€', tier: 'Best-Seller Assoluto Apple' },

  '14 pro max': { name: 'Apple iPhone 14 Pro Max', screen: '6.7" Dynamic Island 120Hz', baseResale: { 128: 650, 256: 720, 512: 790 }, launch: '1489€', tier: 'Fascia Altissima Dynamic Island' },
  '14 pro': { name: 'Apple iPhone 14 Pro', screen: '6.1" Dynamic Island 120Hz', baseResale: { 128: 560, 256: 620, 512: 680 }, launch: '1339€', tier: 'Fascia Alta Dynamic Island' },
  '14 plus': { name: 'Apple iPhone 14 Plus', screen: '6.7" OLED', baseResale: { 128: 450, 256: 490, 512: 540 }, launch: '1179€', tier: 'Fascia Media Display Grande' },
  '14': { name: 'Apple iPhone 14', screen: '6.1" OLED A15 Bionic', baseResale: { 128: 450, 256: 490, 512: 540 }, launch: '1029€', tier: 'Fascia Media Apple' },

  '15 pro max': { name: 'Apple iPhone 15 Pro Max', screen: '6.7" Titanio Dynamic Island 120Hz USB-C', baseResale: { 256: 820, 512: 920, 1024: 1050 }, launch: '1489€', tier: 'Top di Gamma Assoluto Titanio' },
  '15 pro': { name: 'Apple iPhone 15 Pro', screen: '6.1" Titanio Dynamic Island 120Hz USB-C', baseResale: { 128: 700, 256: 770, 512: 850 }, launch: '1239€', tier: 'Top di Gamma Titanio' },
  '15 plus': { name: 'Apple iPhone 15 Plus', screen: '6.7" Dynamic Island USB-C', baseResale: { 128: 590, 256: 650, 512: 720 }, launch: '1129€', tier: 'Fascia Media Dynamic Island USB-C' },
  '15': { name: 'Apple iPhone 15', screen: '6.1" Dynamic Island USB-C', baseResale: { 128: 570, 256: 630, 512: 700 }, launch: '979€', tier: 'Fascia Media Dynamic Island USB-C' },

  '11 pro max': { name: 'Apple iPhone 11 Pro Max', screen: '6.5" OLED Triple Camera', baseResale: { 64: 260, 256: 300, 512: 340 }, launch: '1289€', tier: 'Fascia Media' },
  '11 pro': { name: 'Apple iPhone 11 Pro', screen: '5.8" OLED Triple Camera', baseResale: { 64: 220, 256: 250, 512: 280 }, launch: '1189€', tier: 'Fascia Media' },
  '11': { name: 'Apple iPhone 11', screen: '6.1" LCD Liquid Retina', baseResale: { 64: 160, 128: 185, 256: 210 }, launch: '839€', tier: 'Fascia Economica / Entry Apple' }
}

// 3. DATABASE MANGA
export const MANGA_DATABASE = {
  'naruto': { name: 'Naruto', editor: 'Planet Manga (Panini Comics)', valPerVolume: 2.30, totalVolumes: 72, tier: 'Cult Shonen #1 (Altissima Richiesta Vinted)' },
  'one piece': { name: 'One Piece', editor: 'Star Comics', valPerVolume: 2.50, totalVolumes: 108, tier: 'Best-Seller Mondiale' },
  'dragon ball': { name: 'Dragon Ball', editor: 'Star Comics', valPerVolume: 2.20, totalVolumes: 42, tier: 'Cult Senza Tempo' },
  'berserk': { name: 'Berserk', editor: 'Planet Manga', valPerVolume: 4.50, totalVolumes: 41, tier: 'Capolavoro Dark Fantasy (Valore Alto)' },
  'death note': { name: 'Death Note', editor: 'Planet Manga', valPerVolume: 3.50, totalVolumes: 12, tier: 'Cult Thriller (Vendita Rapida)' },
  'demon slayer': { name: 'Demon Slayer', editor: 'Star Comics', valPerVolume: 2.80, totalVolumes: 23, tier: 'Top Trend Shonen' },
  'jujutsu kaisen': { name: 'Jujutsu Kaisen', editor: 'Planet Manga', valPerVolume: 2.70, totalVolumes: 26, tier: 'Top Trend Shonen' },
  'attacco dei giganti': { name: "L'Attacco dei Giganti", editor: 'Planet Manga', valPerVolume: 2.80, totalVolumes: 34, tier: 'Cult Mondiale' },
  'attack on titan': { name: "L'Attacco dei Giganti", editor: 'Planet Manga', valPerVolume: 2.80, totalVolumes: 34, tier: 'Cult Mondiale' },
  'bleach': { name: 'Bleach', editor: 'Planet Manga', valPerVolume: 2.00, totalVolumes: 74, tier: 'Cult Shonen' },
  'tokyo ghoul': { name: 'Tokyo Ghoul', editor: 'J-Pop', valPerVolume: 3.20, totalVolumes: 14, tier: 'Fascia Alta Collezionismo' },
  'chainsaw man': { name: 'Chainsaw Man', editor: 'Planet Manga', valPerVolume: 3.00, totalVolumes: 17, tier: 'Altissima Richiesta' }
}

// 4. DATABASE GIOCHI
export const GAMES_CATALOG = {
  'mario kart 8 deluxe': { name: 'Mario Kart 8 Deluxe', platform: 'Switch', val: 35 },
  'mario kart 8': { name: 'Mario Kart 8 Deluxe', platform: 'Switch', val: 35 },
  'mario kart': { name: 'Mario Kart 8 Deluxe', platform: 'Switch', val: 35 },
  'zelda tears of the kingdom': { name: 'Zelda: Tears of the Kingdom', platform: 'Switch', val: 42 },
  'tears of the kingdom': { name: 'Zelda: Tears of the Kingdom', platform: 'Switch', val: 42 },
  'zelda breath of the wild': { name: 'Zelda: Breath of the Wild', platform: 'Switch', val: 35 },
  'breath of the wild': { name: 'Zelda: Breath of the Wild', platform: 'Switch', val: 35 },
  'botw': { name: 'Zelda: Breath of the Wild', platform: 'Switch', val: 35 },
  'pokemon scarlatto': { name: 'Pokémon Scarlatto', platform: 'Switch', val: 32 },
  'pokemon violetto': { name: 'Pokémon Violetto', platform: 'Switch', val: 32 },
  'pokemon leggende arceus': { name: 'Pokémon Leggende: Arceus', platform: 'Switch', val: 32 },
  'super smash bros': { name: 'Super Smash Bros. Ultimate', platform: 'Switch', val: 38 },
  'super mario odyssey': { name: 'Super Mario Odyssey', platform: 'Switch', val: 32 },
  'super mario bros wonder': { name: 'Super Mario Bros. Wonder', platform: 'Switch', val: 36 },
  'arms': { name: 'ARMS', platform: 'Switch', val: 20 },
  '1 2 switch': { name: '1-2-Switch', platform: 'Switch', val: 18 },
  '1-2-switch': { name: '1-2-Switch', platform: 'Switch', val: 18 },
  'spider-man 2': { name: "Marvel's Spider-Man 2", platform: 'PS5', val: 38 },
  'spiderman 2': { name: "Marvel's Spider-Man 2", platform: 'PS5', val: 38 },
  'spider-man miles morales': { name: 'Spider-Man: Miles Morales', platform: 'PS4/PS5', val: 22 },
  'spider-man': { name: "Marvel's Spider-Man", platform: 'PS4', val: 16 },
  'god of war ragnarok': { name: 'God of War: Ragnarök', platform: 'PS4/PS5', val: 32 },
  'god of war': { name: 'God of War (2018)', platform: 'PS4', val: 12 },
  'the last of us parte 1': { name: 'The Last of Us Parte I', platform: 'PS5', val: 38 },
  'the last of us parte 2': { name: 'The Last of Us Parte II', platform: 'PS4/PS5', val: 24 },
  'the last of us': { name: 'The Last of Us Remastered', platform: 'PS4', val: 12 },
  'elden ring': { name: 'Elden Ring', platform: 'Multi', val: 30 },
  'gta v': { name: 'Grand Theft Auto V', platform: 'Multi', val: 20 },
  'gta 5': { name: 'Grand Theft Auto V', platform: 'Multi', val: 20 },
  'red dead redemption 2': { name: 'Red Dead Redemption 2', platform: 'Multi', val: 22 },
  'far cry 6': { name: 'Far Cry 6', platform: 'PS4/PS5', val: 15 },
  'far cry 5': { name: 'Far Cry 5', platform: 'PS4', val: 12 },
  'far cry 4': { name: 'Far Cry 4', platform: 'PS4', val: 9 },
  'nioh 2': { name: 'Nioh 2', platform: 'PS4', val: 16 },
  'nioh': { name: 'Nioh', platform: 'PS4', val: 12 },
  'rocket league': { name: 'Rocket League (Disco Fisico)', platform: 'PS4', val: 12 },
  'for honor': { name: 'For Honor', platform: 'PS4', val: 6 },
  'days gone': { name: 'Days Gone', platform: 'PS4', val: 16 },
  'death stranding': { name: 'Death Stranding', platform: 'PS4', val: 16 },
  'the witcher 3': { name: 'The Witcher 3: Wild Hunt', platform: 'PS4', val: 15 },
  'broken sword': { name: 'Broken Sword 5', platform: 'PS4', val: 18 }
}

// 5. CLUSTER CATEGORIE GENERALI
export const CATEGORY_CLUSTERS = [
  {
    id: 'home_appliances',
    match: ['dyson', 'folletto', 'bimby', 'vorwerk', 'aspirapolvere', 'roomba', 'roborock', 'dreame', 'de longhi', 'delonghi', 'la pavoni', 'gaggia', 'nespresso', 'friggitrice ad aria', 'impastatrice', 'planetaria', 'kitchenaid', 'thermomix'],
    name: 'Piccoli Elettrodomestici & Casa Premium',
    platform: 'Subito.it (A mano a Torino) / Vinted per accessori',
    retailMultiplier: 2.2,
    baseBenchmark: 220,
    targetMargin: 0.50,
    liquidity: 'Molto Alta',
    liquidityTip: 'Brand come Dyson, Folletto o Bimby mantengono un valore altissimo. Gli accessori extra inclusi permettono di aumentare il prezzo di vendita.',
    checklist: [
      'Autonomia batteria (per scope elettriche e robot) a potenza massima',
      'Pulizia filtri e motore: verifica assenza di odori di surriscaldamento o blocchi',
      'Presenza di tutte le bocchette e accessori originali'
    ]
  },
  {
    id: 'musical_instruments',
    match: ['chitarra', 'fender', 'gibson', 'ibanez', 'epiphone', 'yamaha', 'amplificatore', 'marshall', 'boss', 'pedale', 'tastiera', 'pianoforte', 'giradischi', 'technics', 'pioneer', 'marantz', 'vinili', 'microfono', 'shure', 'rode'],
    name: 'Strumenti Musicali & Audio Professionale / Hi-Fi',
    platform: 'Subito.it (Ritiro a mano a Torino per strumenti) / Vinted per pedali e vinili',
    retailMultiplier: 2.0,
    baseBenchmark: 240,
    targetMargin: 0.52,
    liquidity: 'Alta (Appassionati & Musicisti)',
    liquidityTip: 'Gli strumenti di marchi storici (Fender, Gibson, Marshall, Technics) non si svalutano mai e si rivendono benissimo a mano a Torino.',
    checklist: [
      'Integrità manico e tasti: controlla assenza di curvature anomale o tasti usurati',
      'Potenziometri e jack: collega a un amplificatore e verifica assenza di fruscii o falsi contatti',
      'Presenza di custodia rigida o morbida originale'
    ]
  },
  {
    id: 'toys_collectibles',
    match: ['lego', 'star wars', 'technic', 'pokemon', 'carte pokemon', 'magic', 'mtg', 'yu-gi-oh', 'yugioh', 'warhammer', 'funko pop', 'modellismo', 'action figure', 'giochi da tavolo', 'gundam'],
    name: 'Collezionismo, Lego & Trading Cards',
    platform: 'Vinted / eBay (Spedizione con imballo protettivo)',
    retailMultiplier: 2.0,
    baseBenchmark: 95,
    targetMargin: 0.45,
    liquidity: 'Massima (Community Collezionisti)',
    liquidityTip: 'I set Lego (specie se con scatola e minifigure) e le carte collezionabili si vendono istantaneamente online. Spedisci sempre con pluriball.',
    checklist: [
      'Completezza set: verifica presenza di tutte le minifigure e del libretto istruzioni',
      'Condizioni scatola: controlla che i sigilli siano intatti o che la scatola non sia schiacciata',
      'Condizioni carte: verifica l\'assenza di sbiancamenti sui bordi (whitening) o pieghe'
    ]
  },
  {
    id: 'watches',
    match: ['orologio', 'seiko', 'citizen', 'tissot', 'hamilton', 'orient', 'casio', 'g-shock', 'gshock', 'omega', 'automatico', 'cronografo', 'swatch', 'moonswatch'],
    name: 'Orologeria & Segnatempo da Collezione',
    platform: 'Vinted / Subito.it a mano a Torino',
    retailMultiplier: 2.2,
    baseBenchmark: 150,
    targetMargin: 0.50,
    liquidity: 'Alta',
    liquidityTip: 'Gli orologi automatici con scatola e garanzia (Full Set) e maglie aggiuntive del bracciale si vendono al 30% in più.',
    checklist: [
      'Funzionamento movimento: verifica cambio data scattante e tenuta del tempo',
      'Vetro e ghiera: controlla assenza di graffi profondi sul vetro zaffiro/minerale',
      'Corredo completo: presenza di scatola originale, garanzia timbrata e maglie extra'
    ]
  },
  {
    id: 'fashion_sneakers',
    match: ['jordan', 'nike dunk', 'yeezy', 'travis scott', 'supreme', 'stone island', 'north face', 'stussy', 'sneakers', 'scarpe', 'giacca', 'borsa'],
    name: 'Sneakers & Streetwear da Collezione',
    platform: 'Vinted (Piattaforma #1 per la moda)',
    retailMultiplier: 1.9,
    baseBenchmark: 120,
    targetMargin: 0.45,
    liquidity: 'Altissima',
    liquidityTip: 'Vinted è perfetto per le sneakers. Carica foto della suola, della soletta interna e dell\'etichetta con taglia e codice stile (SKU).',
    checklist: [
      'Autenticità: controlla cuciture, etichetta interna taglia e scatola originale con codice SKU corrispondente',
      'Stato della suola: verifica consumo dei tasselli sotto la pianta e il tallone',
      'Pulizia solette interne e assenza di cattivi odori o lacerazioni interne'
    ]
  },
  {
    id: 'cameras_drones',
    match: ['gopro', 'dji', 'fotocamera', 'canon', 'nikon', 'sony alpha', 'a6000', 'a7', 'fujifilm', 'obiettivo', 'lente', 'drone', 'osmo', 'stabilizzatore', 'reflex', 'mirrorless'],
    name: 'Fotografia, Action Cam & Droni',
    platform: 'Subito.it (Torino) / Vinted',
    retailMultiplier: 2.0,
    baseBenchmark: 220,
    targetMargin: 0.52,
    liquidity: 'Molto Alta',
    liquidityTip: 'I lotti che includono batterie extra, filtri e borse da trasporto si vendono con facilità estrema sia a Torino che online.',
    checklist: [
      'Lenti e sensore: controlla controluce che non ci siano graffi, funghi o polvere interna',
      'Gimbal e motori (per droni): verifica calibrazione fluida all\'avvio senza errori',
      'Numero scatti (per reflex/mirrorless) e stato usura batterie'
    ]
  },
  {
    id: 'tools_diy',
    match: ['makita', 'dewalt', 'bosch', 'milwaukee', 'parkside', 'trapano', 'avvitatore', 'smerigliatrice', 'flessibile', 'compressore', 'saldatrice', 'motosega', 'decespugliatore', 'chiavi', 'usag', 'beta'],
    name: 'Elettroutensili & Attrezzatura da Lavoro 18V',
    platform: 'Subito.it (Scambio a mano rapidissimo a Torino tra artigiani)',
    retailMultiplier: 2.0,
    baseBenchmark: 120,
    targetMargin: 0.50,
    liquidity: 'Alta (Forte richiesta locale)',
    liquidityTip: 'Gli attrezzi a batteria 18V con valigetta e 2 batterie si vendono in poche ore a mano a Torino.',
    checklist: [
      'Batterie: controlla tenuta di carica e caricatore rapido originale',
      'Mandrino: fai girare a vuoto per escludere oscillazioni eccentriche',
      'Motore: verifica assenza di scintille eccessive, fumo o odore di bruciato'
    ]
  },
  {
    id: 'cycling_sport',
    match: ['bici', 'bicicletta', 'mtb', 'bici da corsa', 'garmin', 'wahoo', 'meilan', 'cycplus', 'igpsport', 'ciclocomputer', 'rulli', 'elite', 'tacx', 'sci', 'snowboard', 'tapis roulant'],
    name: 'Ciclismo, Rulli Smart & Attrezzatura Sportiva',
    platform: 'Subito.it a mano a Torino per telai/bici | Vinted per ciclocomputer e sensori',
    retailMultiplier: 2.1,
    baseBenchmark: 75,
    targetMargin: 0.50,
    liquidity: 'Alta',
    liquidityTip: 'I ciclocomputer e gli accessori sportivi si spediscono su Vinted; per biciclette e rulli pesanti punta allo scambio a mano a Torino.',
    checklist: [
      'Funzionamento elettronico / GPS: verifica aggancio satelliti e connessione sensori',
      'Stato meccanico: controlla assenza di giochi nei cuscinetti o crepe nel telaio/scocca',
      'Accessori di montaggio: presenza di staffe, magneti e cavi di ricarica'
    ]
  },
  {
    id: 'computing_gaming',
    match: ['macbook', 'ipad', 'laptop', 'notebook', 'pc gaming', 'rtx', 'gtx', 'geforce', 'ryzen', 'intel', 'monitor', 'scheda video', 'steam deck', 'asus rog', 'lenovo', 'thinkpad', 'kindle'],
    name: 'Informatica, MacBook, iPad & Componenti PC',
    platform: 'Subito.it a mano a Torino / Vinted',
    retailMultiplier: 1.9,
    baseBenchmark: 290,
    targetMargin: 0.55,
    liquidity: 'Massima',
    liquidityTip: 'MacBook con chip Apple Silicon (M1/M2/M3) e schede video RTX serie 3000/4000 sono liquidissimi.',
    checklist: [
      'Stato sblocco: ripristino di fabbrica completo davanti al venditore',
      'Display: verifica assenza di pixel bruciati, righe o difetti di retroilluminazione',
      'Batteria e alimentatore: controlla cicli di ricarica e alimentatore originale'
    ]
  }
]

/**
 * Valutatore Universale Decoupled:
 * Il valore di rivendita Usato è una proprietà oggettiva del prodotto (benchmark di mercato),
 * mentre il prezzo chiesto dal venditore serve SOLO a valutare l'affare e calcolare lo sconto da chiedere!
 */
export function valutaOggettoUniversale(testoAnnuncio, prezzoManuale) {
  const clean = (testoAnnuncio || '').toLowerCase().trim()
  if (!clean) return null

  // 1. Prezzo Richiesto: se l'utente lo inserisce a mano, ha sempre priorità sulla stima da testo
  let prezzoRichiesto = null
  if (prezzoManuale && Number(prezzoManuale) > 0) {
    prezzoRichiesto = Math.round(Number(prezzoManuale))
  } else {
    const matchBlocco = clean.match(/(?:blocco|tutti|prendi|stock|lotto)[^0-9\n]{0,30}(\d{2,4})\s*(?:€|euro|eur)/i)
      || clean.match(/(\d{2,4})\s*(?:€|euro|eur)[^0-9\n]{0,30}(?:blocco|tutti|totale)/i)
      || clean.match(/(?:a soli|prezzo blocco|totale)\s*[:=]?\s*(\d{2,4})\s*(?:€|euro|eur)?/i)

    if (matchBlocco) {
      prezzoRichiesto = parseInt(matchBlocco[1], 10)
    } else {
      const matchPrezzo1 = clean.match(/(?:prezzo|vendo a|cedo a|richiesta|costo)\s*[:=]?\s*(\d{1,4})\s*(?:€|euro|eur)?/i)
      const matchPrezzo2 = clean.match(/(\d{1,4})\s*(?:€|euro|eur)/i)

      if (matchPrezzo1 && parseInt(matchPrezzo1[1], 10) >= 5) {
        prezzoRichiesto = parseInt(matchPrezzo1[1], 10)
      } else if (matchPrezzo2 && parseInt(matchPrezzo2[1], 10) >= 5) {
        prezzoRichiesto = parseInt(matchPrezzo2[1], 10)
      }
    }
  }

  // Se il venditore chiede meno del target calcolato dal benchmark, non ha senso consigliare
  // di offrire di più: il tetto diventa il prezzo richiesto stesso.
  const clampAlPrezzoRichiesto = (target, max) => {
    if (prezzoRichiesto && prezzoRichiesto < target) {
      return [prezzoRichiesto, Math.min(max, prezzoRichiesto)]
    }
    return [target, max]
  }

  // 2. PARSING SMARTPHONE ANDROID & PIEGHEVOLI (Nubia Flip, Z Flip, Pixel, Galaxy S)
  for (const [andKey, andData] of Object.entries(ANDROID_MODELS)) {
    if (clean.includes(andKey)) {
      const baseResale = andData.baseResale
      const resaleVal = baseResale
      let [targetVal, maxVal] = clampAlPrezzoRichiesto(Math.round(resaleVal * 0.52), Math.round(resaleVal * 0.52 * 1.18)) // Regola ~50%
      const profit = resaleVal - targetVal
      const roi = Math.round((profit / targetVal) * 100)

      let discountText = ''
      if (prezzoRichiesto) {
        if (prezzoRichiesto > resaleVal * 1.15) {
          discountText = ` ⚠️ Il venditore chiede ${prezzoRichiesto}€ (superiore al valore di rivendita di ~${resaleVal}€): prezzo fuori mercato.`
        } else {
          const scontoRealistico = Math.min(28, Math.max(12, Math.round(((prezzoRichiesto - targetVal) / prezzoRichiesto) * 100)))
          const offertaRealistica = Math.round(prezzoRichiesto * (1 - scontoRealistico / 100))
          discountText = ` (Chiede ${prezzoRichiesto}€ ➔ Proponi ${offertaRealistica}€ con sconto realistico del -${scontoRealistico}%)`
        }
      }

      return {
        titoloRilevato: andData.name,
        rawText: testoAnnuncio,
        schedaOggetto: {
          tipologia: `${andData.name} - ${andData.screen}`,
          fasciaMercato: andData.tier,
          prezzoNuovo: `${andData.retail} (Prezzo di Lancio / Retail)`,
          prezzoUsatoDettaglio: `~${resaleVal}€ (valore reale di vendita rapida su Subito/Vinted)`
        },
        strategiaFlipping: [
          { voce: 'Offerta Target d\'Acquisto', valore: `${targetVal}€`, badge: 'DA INVIARE', highlight: true },
          { voce: 'Tetto Massimo da non superare', valore: `${maxVal}€`, nota: `Oltre i ${maxVal}€ il margine scende` },
          { voce: 'Valore Reale Rivendita Usato', valore: `~${resaleVal}€`, nota: 'Prezzo mediano di vendita rapida' },
          { voce: 'Profitto Netto Stimato', valore: `+${profit}€`, nota: `ROI: +${roi}%`, isProfit: true }
        ],
        liquidita: {
          livello: 'Alta (Forte richiesta per Pieghevoli)',
          benchmark: 'I pieghevoli Flip e gli smartphone 5G hanno grande appeal su Subito a Torino e su Vinted',
          consiglioOperativo: `Il valore di mercato reale di questo telefono è circa ${resaleVal}€.${discountText} Offrendo ${targetVal}€ in contanti sul posto ti assicuri un guadagno pulito di +${profit}€!`
        },
        controlliDalVivo: [
          'Piegatura Display (per Flip): Controlla controluce che la piega centrale non presenti micro-fessurazioni o pixel neri',
          'Cerniera: Apri e chiudi a 90° e 180° per verificare che la cerniera mantenga la posizione senza scatti anomali',
          'Account & Blocco: Fai eseguire il ripristino di fabbrica davanti a te ed elimina l\'account Google'
        ],
        valoreRivenditaUsato: resaleVal,
        prezzoRichiesto: prezzoRichiesto || Math.round(resaleVal * 0.80),
        offertaTarget: targetVal,
        tettoMassimo: maxVal,
        profittoNetto: profit,
        roi,
        scriptTrattativa: {
          subito: `Ciao! Ho visto il tuo annuncio per ${andData.name}. Se lo smartphone è perfettamente funzionante con lo schermo integro, posso offrirti ${targetVal}€ e venire a ritirarlo di persona oggi stesso con pagamento immediato in contanti a Torino, così concludiamo subito senza farti perdere tempo. Fammi sapere se per te può andare bene!`,
          whatsapp: `Buongiorno! Ti scrivo per ${andData.name}. Sono di Torino e posso fare ritiro a mano oggi a ${targetVal}€ in contanti sul posto. Fammi sapere dove ci possiamo incontrare, grazie!`
        }
      }
    }
  }

  // 3. PARSING MANGA & FUMETTI
  for (const [mangaKey, mangaData] of Object.entries(MANGA_DATABASE)) {
    if (clean.includes(mangaKey)) {
      let startVol = 1
      let endVol = 1
      let numVolumi = 1

      const matchRange = clean.match(/(?:da|dal|volumi?|numeri?|n[°.]?)\s*(\d+)\s*(?:a|al|-)\s*(\d+)/i)
        || clean.match(/(\d+)\s*[-/]\s*(\d+)/)

      if (matchRange) {
        startVol = parseInt(matchRange[1], 10)
        endVol = parseInt(matchRange[2], 10)
        numVolumi = Math.max(1, endVol - startVol + 1)
      } else {
        const matchSingolo = clean.match(/(\d+)\s*volumi/i) || clean.match(/(\d+)\s*manga/i)
        if (matchSingolo) numVolumi = parseInt(matchSingolo[1], 10)
        else if (clean.includes('completa') || clean.includes('serie completa')) numVolumi = mangaData.totalVolumes
      }

      let edizione = ''
      if (clean.includes('gold')) edizione = 'Edizione Gold'
      else if (clean.includes('nera')) edizione = 'Serie Nera'
      else if (clean.includes('rossa')) edizione = 'Serie Rossa'
      else if (clean.includes('new edition')) edizione = 'New Edition'
      else if (clean.includes('black edition')) edizione = 'Black Edition'
      else if (clean.includes('deluxe')) edizione = 'Edizione Deluxe'
      else if (clean.includes('maximum')) edizione = 'Maximum Edition'

      const isComeNuovi = clean.includes('come nuovi') || clean.includes('perfetti') || clean.includes('ottime condizioni')
      let valUnitario = mangaData.valPerVolume
      if (isComeNuovi) valUnitario += 0.20
      if (edizione === 'Edizione Gold') valUnitario += 0.15

      const resaleTotale = Math.round(numVolumi * valUnitario)
      const targetBase = Math.max(15, Math.round(resaleTotale * 0.48))
      const [targetVal, maxVal] = clampAlPrezzoRichiesto(targetBase, Math.round(targetBase * 1.20))
      const profit = resaleTotale - targetVal
      const roi = Math.round((profit / targetVal) * 100)

      const edizDesc = edizione ? ` (${edizione})` : ''
      const volDesc = numVolumi > 1 ? `Volumi ${startVol} – ${endVol} (${numVolumi} volumi consecutivi)` : `Volume singolo`

      return {
        titoloRilevato: `Manga ${mangaData.name}${edizDesc} - ${numVolumi} Volumi`,
        rawText: testoAnnuncio,
        schedaOggetto: {
          tipologia: `Lotto Manga ${mangaData.name}${edizDesc}, ${volDesc} - ${isComeNuovi ? 'Condizioni Pari al Nuovo' : 'Buone condizioni'}`,
          fasciaMercato: `${mangaData.editor} | ${mangaData.tier}`,
          prezzoNuovo: `Prezzo di copertina originale (~4.50€/vol): ~${Math.round(numVolumi * 4.50)}€`,
          prezzoUsatoDettaglio: `~${resaleTotale}€ (prezzo mediano di vendita rapida del blocco su Vinted: ~${(resaleTotale / numVolumi).toFixed(2)}€ a volume)`
        },
        strategiaFlipping: [
          { voce: 'Offerta Target per il Blocco', valore: `${targetVal}€`, badge: 'DA INVIARE', highlight: true },
          { voce: 'Tetto Massimo da non superare', valore: `${maxVal}€`, nota: `Circa ${(maxVal / numVolumi).toFixed(2)}€ a volume massimo` },
          { voce: 'Prezzo di Rivendita Rapida (Vinted)', valore: `${resaleTotale}€`, nota: 'I lotti manga consecutivi si vendono in 2–5 giorni' },
          { voce: 'Profitto Netto Stimato', valore: `+${profit}€`, nota: `ROI: +${roi}%`, isProfit: true }
        ],
        liquidita: {
          livello: 'Altissima (Top su Vinted)',
          benchmark: 'I manga famosi sono tra i prodotti con la rotazione più veloce su Vinted',
          consiglioOperativo: `Acquista il blocco a ${targetVal}€ (circa ${(targetVal / numVolumi).toFixed(2)}€ a fumetto). Mettilo su Vinted a ${resaleTotale}€: lo vendi in pochi giorni guadagnando +${profit}€ puliti!`
        },
        controlliDalVivo: [
          'Ingiallimento Pagine: Controlla che i tagli superiori e laterali siano chiari',
          'Integrità Costine: Nessuna piega da lettura profonda o scollamenti',
          'Sequenza Consecutiva: Verifica che non manchino volumi intermedi'
        ],
        valoreRivenditaUsato: resaleTotale,
        prezzoRichiesto: prezzoRichiesto || Math.round(resaleTotale * 0.85),
        offertaTarget: targetVal,
        tettoMassimo: maxVal,
        profittoNetto: profit,
        roi,
        scriptTrattativa: {
          subito: `Ciao! Ho visto il tuo annuncio del blocco manga di ${mangaData.name} (${numVolumi} volumi). Visto che prenderei tutto il lotto completo subito senza farti perdere tempo con vendite singole, posso offrirti ${targetVal}€ e venire a fare ritiro a mano di persona oggi stesso in contanti a Torino. Fammi sapere se per te può andare bene!`,
          whatsapp: `Buongiorno! Ti scrivo per il blocco manga di ${mangaData.name}. Sono di Torino e posso fare ritiro a mano oggi a ${targetVal}€ in contanti sul posto. Fammi sapere se posso passare, grazie!`
        }
      }
    }
  }

  // 4. PARSING IPHONE SPECIFICO
  if (clean.includes('iphone') || clean.includes('apple')) {
    let matchedKey = null
    const sortedKeys = Object.keys(IPHONE_MODELS).sort((a, b) => b.length - a.length)
    for (const k of sortedKeys) {
      if (clean.includes(`iphone ${k}`) || clean.includes(`iphone${k}`) || clean.includes(` ${k} `) || clean.includes(`modello: iphone ${k}`)) {
        matchedKey = k
        break
      }
    }
    if (!matchedKey) {
      for (const k of sortedKeys) {
        if (clean.includes(k)) {
          matchedKey = k
          break
        }
      }
    }

    if (matchedKey) {
      const modelInfo = IPHONE_MODELS[matchedKey]
      let gb = 128
      if (clean.includes('64 gb') || clean.includes('64gb')) gb = 64
      else if (clean.includes('256 gb') || clean.includes('256gb')) gb = 256
      else if (clean.includes('512 gb') || clean.includes('512gb')) gb = 512
      else if (clean.includes('1 tb') || clean.includes('1tb')) gb = 1024
      else if (modelInfo.baseResale[128]) gb = 128
      else if (modelInfo.baseResale[64]) gb = 64

      let baseResale = modelInfo.baseResale[gb] || modelInfo.baseResale[128] || 250

      let batteryPct = null
      const matchBatt = clean.match(/(\d{2})\s*%\s*(?:della capacità|batteria|capacità massima|stato batteria)?/i)
        || clean.match(/(?:batteria|stato batteria|capacità)[^0-9\n]{0,20}(\d{2})\s*%/i)
      if (matchBatt) batteryPct = parseInt(matchBatt[1], 10)

      const haSegniUsura = clean.includes('segni di usura') || clean.includes('graffi') || clean.includes('graffio') || clean.includes('scocca:')
      let resaleVal = baseResale
      if (batteryPct && batteryPct <= 83) resaleVal -= 15
      if (haSegniUsura) resaleVal -= 10

      const targetBase = Math.round(resaleVal * 0.62)
      const [targetVal, maxVal] = clampAlPrezzoRichiesto(targetBase, Math.round(targetBase * 1.15))
      const profit = resaleVal - targetVal
      const roi = Math.round((profit / targetVal) * 100)

      const battDesc = batteryPct ? ` (Batteria ${batteryPct}%)` : ''
      const usuraDesc = haSegniUsura ? ' - Scocca con segni di usura, Schermo perfetto' : ''

      return {
        titoloRilevato: `${modelInfo.name} ${gb}GB${battDesc}`,
        rawText: testoAnnuncio,
        schedaOggetto: {
          tipologia: `${modelInfo.screen}, ${gb}GB Storage${usuraDesc}`,
          fasciaMercato: modelInfo.tier,
          prezzoNuovo: `${modelInfo.launch} (Lancio Apple) - Attuale Grado B: ~${Math.round(baseResale * 1.15)}€ – ${Math.round(baseResale * 1.25)}€`,
          prezzoUsatoDettaglio: `${resaleVal - 10}€ – ${resaleVal + 10}€ (con schermo originale e ${gb}GB si vende in 24–48h su Subito/Vinted)`
        },
        strategiaFlipping: [
          { voce: 'Offerta Target d\'Acquisto', valore: `${targetVal}€`, badge: 'DA INVIARE', highlight: true },
          { voce: 'Tetto Massimo da non superare', valore: `${maxVal}€`, nota: `Oltre i ${maxVal}€ il margine netto scende sotto i 65€` },
          { voce: 'Prezzo di Rivendita Rapida (Vinted/Subito)', valore: `${resaleVal}€`, nota: 'Per vendita rapida in 24–72 ore' },
          { voce: 'Profitto Netto Stimato', valore: `+${profit}€`, nota: `ROI: +${roi}%`, isProfit: true }
        ],
        liquidita: {
          livello: 'Massima (Vendita Rapida)',
          benchmark: 'L\'iPhone è il modello con la rotazione più veloce nel mercato dell\'usato',
          consiglioOperativo: `Le 2 leve per la trattativa: 1) Batteria al ${batteryPct || '82'}% vicina alla soglia critica dell'80%. 2) Scocca con segni di usura. Offrendo ${targetVal}€ in contanti sul posto ti assicuri un margine netto pulito di circa +${profit}€!`
        },
        controlliDalVivo: [
          'Blocco iCloud: Fai eseguire il ripristino di fabbrica davanti a te e configuralo fino alla Home',
          'Display Originale & True Tone: Tieni premuta la barra della luminosità nel Centro di Controllo e verifica il True Tone',
          'Face ID & Fotocamere: Prova a registrare il volto e scatta foto sia con grandangolo (0.5x) che standard (1x)'
        ],
        valoreRivenditaUsato: resaleVal,
        prezzoRichiesto: prezzoRichiesto || Math.round(resaleVal * 0.90),
        offertaTarget: targetVal,
        tettoMassimo: maxVal,
        profittoNetto: profit,
        roi,
        scriptTrattativa: {
          subito: `Ciao! Ho letto la descrizione dell'${modelInfo.name}. Visto che la scocca presenta diversi segni di usura e la batteria è all'${batteryPct || '82'}% (quindi a breve richiederà un ciclo di sostituzione), posso offrirti ${targetVal}€ e venire a ritirarlo di persona a Torino oggi stesso con pagamento immediato in contanti. Fammi sapere se per te può andare bene!`,
          whatsapp: `Buongiorno! Ti scrivo per l'${modelInfo.name} 128GB. Sono di Torino e posso fare ritiro a mano oggi a ${targetVal}€ in contanti sul posto. Fammi sapere se posso passare, grazie!`
        }
      }
    }
  }

  // 5. PARSING NINTENDO SWITCH & BUNDLE GIOCHI
  if (clean.includes('nintendo switch') || clean.includes('switch') || clean.includes('joycon') || clean.includes('joy-con')) {
    let isOled = clean.includes('oled')
    let isLite = clean.includes('lite')
    let baseConsoleVal = isOled ? 200 : isLite ? 95 : 135

    // Difetti e condizione reale dichiarati dal venditore: non vanno mai ignorati nella stima
    let malusEuro = 0
    const condizioneNote = []

    const levettaGuasta = /levett\w*[^.]{0,60}(danno|non va|non funziona|rotta|rotto|difettosa|difettoso|drift)/i.test(clean)
      || /(danno|non va|non funziona|rotta|rotto|difettosa|difettoso|drift)[^.]{0,60}levett/i.test(clean)
    if (levettaGuasta) {
      malusEuro += 25
      condizioneNote.push('Levetta/tasto Joy-Con difettoso dichiarato: preventiva ~20-25€ per riparazione o ricambio')
    }

    const schedaMadreCambiata = /scheda madre[^.]{0,40}(cambiat|sostituit|riparat)/i.test(clean)
    if (schedaMadreCambiata) {
      condizioneNote.push('Scheda madre già sostituita: chiedi ricevuta/data della riparazione e verifica il seriale prima di pagare')
    }

    const mancaCaricatore = /(assenza|manca(no)?|senza|privo|priva)[^.]{0,20}caric/i.test(clean)
    if (mancaCaricatore) {
      malusEuro += 15
      condizioneNote.push('Manca il caricatore/alimentatore: metti in conto ~15€ per uno originale o compatibile')
    }

    const consoleComponentVal = Math.max(30, baseConsoleVal - malusEuro)
    let extraItems = []
    let accessoriComponentVal = 0

    if (clean.includes('scatola') || clean.includes('scatola originale')) {
      accessoriComponentVal += 10
      extraItems.push('Scatola originale (+10€ rivendita)')
    }
    if (clean.includes('coppia joycon') || clean.includes('joycon rosa') || clean.includes('seconda coppia')) {
      accessoriComponentVal += 40
      extraItems.push('Coppia Joy-Con Extra con scatola (~40€ pezzo singolo)')
    }
    if (clean.includes('micro sd') || clean.includes('microsd')) {
      accessoriComponentVal += 8
      extraItems.push('Micro SD Nintendo (~8€)')
    }

    const giochiInclusi = []
    for (const [kw, g] of Object.entries(GAMES_CATALOG)) {
      if (clean.includes(kw) && !clean.includes(`${kw}: venduto`)) {
        if (!giochiInclusi.some(x => x.name === g.name)) {
          giochiInclusi.push(g)
        }
      }
    }
    const giochiComponentVal = giochiInclusi.reduce((a, b) => a + b.val, 0)

    const totalBundleResale = consoleComponentVal + accessoriComponentVal + giochiComponentVal
    const soloConsole = extraItems.length === 0 && giochiInclusi.length === 0

    const consoleName = isOled ? 'Nintendo Switch OLED' : isLite ? 'Nintendo Switch Lite' : 'Nintendo Switch (V1/V2 Base)'
    const targetBase = Math.round(totalBundleResale * 0.55)
    const [targetVal, maxVal] = clampAlPrezzoRichiesto(targetBase, Math.round(targetBase * 1.18))
    const profit = totalBundleResale - targetVal
    const roi = Math.round((profit / targetVal) * 100)

    const accessoriDesc = extraItems.length > 0 ? `+ ${extraItems.length} accessori extra` : '+ nessun accessorio extra dichiarato'
    const giochiDesc = giochiInclusi.length > 0 ? ` + ${giochiInclusi.length} giochi su cartuccia` : ''
    const difettiDesc = condizioneNote.length > 0 ? ` — CON DIFETTI DICHIARATI: ${condizioneNote.join('; ')}` : ''

    return {
      titoloRilevato: soloConsole
        ? `${consoleName} (solo console)${condizioneNote.length ? ' - con difetti dichiarati' : ''}`
        : `Bundle ${consoleName} + ${giochiInclusi.length} Giochi & Accessori`,
      rawText: testoAnnuncio,
      schedaOggetto: {
        tipologia: `${consoleName}, ${clean.includes('scatola') ? 'con scatola' : 'senza scatola dichiarata'} ${accessoriDesc}${giochiDesc}${difettiDesc}`,
        fasciaMercato: 'Top di Gamma Console Ibrida Nintendo',
        prezzoNuovo: 'Valore a nuovo del pacchetto intero: ~450€ – 500€',
        prezzoUsatoDettaglio: `~${totalBundleResale}€ (${malusEuro > 0 ? `già scontato di ${malusEuro}€ per i difetti dichiarati, ` : ''}${soloConsole ? 'vendita console singola' : 'smembrando console, joy-con extra e cartucce'} su Vinted/Subito)`
      },
      strategiaFlipping: [
        { voce: soloConsole ? 'Offerta Target d\'Acquisto' : 'Offerta Target per il Blocco', valore: `${targetVal}€`, badge: 'DA INVIARE', highlight: true },
        { voce: 'Tetto Massimo da non superare', valore: `${maxVal}€`, nota: 'Oltre questa cifra il margine scende' },
        { voce: soloConsole ? 'Prezzo di Rivendita Stimato' : 'Incasso Reale Totale (Smembrato)', valore: `~${totalBundleResale}€`, nota: `Console ${consoleComponentVal}€${accessoriComponentVal ? ` + Accessori ${accessoriComponentVal}€` : ''}${giochiComponentVal ? ` + Giochi ${giochiComponentVal}€` : ''}` },
        { voce: 'Profitto Netto Stimato', valore: `+${profit}€`, nota: `ROI: +${roi}%`, isProfit: true }
      ],
      liquidita: {
        livello: condizioneNote.length ? 'Media (Difetti da negoziare)' : 'Massima (Liquidità Record)',
        benchmark: 'La Switch e i suoi accessori originali sono tra gli oggetti più facili da rivendere a Torino, ma i difetti dichiarati vanno sempre scontati dal prezzo',
        consiglioOperativo: soloConsole
          ? `${condizioneNote.length ? 'Usa i difetti dichiarati come leva di trattativa: ' + condizioneNote.join('; ') + '. ' : ''}Offri ${targetVal}€ in contanti sul posto: ti assicuri un margine netto di circa +${profit}€.`
          : `Strategia: acquista l'intero blocco a ${targetVal}€. Rivendi separatamente console (~${consoleComponentVal}€)${accessoriComponentVal ? `, accessori extra (~${accessoriComponentVal}€)` : ''}${giochiComponentVal ? ` e giochi (~${giochiComponentVal}€)` : ''} su Subito/Vinted: fai +${profit}€ puliti!`
      },
      controlliDalVivo: [
        ...(levettaGuasta
          ? ['Il venditore dichiara già un difetto alla levetta: verifica quale lato è compromesso e prova drift/click su ENTRAMBI i Joy-Con prima di pagare']
          : ['Drift Levette: Vai in Impostazioni ➔ Controller e sensori ➔ Calibra levette su entrambe le coppie di Joy-Con']),
        'Schermo & Touch: Verifica l\'assenza di graffi e che il touchscreen risponda in ogni angolo',
        'Lettore Cartucce: Inserisci una scheda di gioco per testare la lettura e collegati al Wi-Fi',
        ...(schedaMadreCambiata ? ['Scheda madre sostituita: chiedi la ricevuta della riparazione e verifica che il seriale sotto lo stand corrisponda a quello di sistema'] : [])
      ],
      valoreRivenditaUsato: totalBundleResale,
      prezzoRichiesto: prezzoRichiesto || Math.round(totalBundleResale * 0.85),
      offertaTarget: targetVal,
      tettoMassimo: maxVal,
      profittoNetto: profit,
      roi,
      scriptTrattativa: {
        subito: soloConsole
          ? `Ciao! Ho letto l'annuncio della tua ${consoleName}.${condizioneNote.length ? ' Visto ' + condizioneNote.map(c => c.split(':')[0].toLowerCase()).join(' e ') + ',' : ''} posso offrirti ${targetVal}€ e venire a ritirarla di persona oggi stesso in contanti a Torino. Fammi sapere se per te può andare bene!`
          : `Ciao! Ho visto il tuo annuncio del bundle Nintendo Switch${clean.includes('scatola') ? ' con la scatola' : ''} e gli accessori. Visto che prenderei tutto il blocco completo subito, posso offrirti ${targetVal}€ e venire a fare ritiro a mano di persona oggi stesso in contanti a Torino. Fammi sapere se per te può andare bene!`,
        whatsapp: soloConsole
          ? `Buongiorno! Ti scrivo per la tua ${consoleName}. Sono di Torino e posso fare ritiro a mano oggi a ${targetVal}€ in contanti sul posto. Fammi sapere dove ci possiamo incontrare, grazie!`
          : `Buongiorno! Ti scrivo per il bundle Nintendo Switch. Sono di Torino e posso fare ritiro a mano oggi a ${targetVal}€ in contanti sul posto. Fammi sapere dove ci possiamo incontrare, grazie!`
      }
    }
  }

  // 6. CLASSIFICATORE UNIVERSALE PER QUALSIASI ALTRO OGGETTO
  let clusterTrovato = null
  let bestClusterScore = 0

  for (const c of CATEGORY_CLUSTERS) {
    let score = 0
    for (const kw of c.match) {
      if (clean.includes(kw)) score += kw.length
    }
    if (score > bestClusterScore) {
      bestClusterScore = score
      clusterTrovato = c
    }
  }

  // Estrazione Titolo Pulito
  const primaRiga = testoAnnuncio.split(/\r?\n/)[0] || testoAnnuncio
  const titoloPulito = primaRiga.replace(/[!?,;:]/g, '').slice(0, 45).trim()

  let categoriaNome = clusterTrovato ? clusterTrovato.name : 'Oggettistica & Articoli Usati'
  let piattaformaConsigliata = clusterTrovato ? clusterTrovato.platform : 'Subito.it (Torino) / Vinted'
  let targetMargin = clusterTrovato ? clusterTrovato.targetMargin : 0.50
  let retailMultiplier = clusterTrovato ? clusterTrovato.retailMultiplier : 2.0
  let liquiditaLivello = clusterTrovato ? clusterTrovato.liquidity : 'Alta'
  let liquiditaConsiglio = clusterTrovato ? clusterTrovato.liquidityTip : 'Fai un\'offerta al 50% del valore stimato per proteggere il tuo margine e rivendere velocemente.'
  let checklistControlli = clusterTrovato ? clusterTrovato.checklist : [
    'Verifica il perfetto funzionamento meccanico ed elettronico',
    'Controlla l\'integrità estetica e l\'assenza di crepe, usura o parti mancanti',
    'Verifica la presenza di scatola originale, accessori e cavi'
  ]

  // Benchmark di Valore Reale (100% Indipendente dal prezzo inserito nell'annuncio)
  let resaleVal = clusterTrovato ? clusterTrovato.baseBenchmark : 60

  const targetBase = Math.max(10, Math.round(resaleVal * targetMargin))
  const [targetVal, maxVal] = clampAlPrezzoRichiesto(targetBase, Math.round(targetBase * 1.20))
  const profit = resaleVal - targetVal
  const roi = Math.round((profit / targetVal) * 100)

  const retailMin = Math.round(resaleVal * (retailMultiplier - 0.2))
  const retailMax = Math.round(resaleVal * (retailMultiplier + 0.3))

  let consiglioExtra = liquiditaConsiglio
  if (prezzoRichiesto) {
    if (prezzoRichiesto > resaleVal * 1.15) {
      consiglioExtra = `⚠️ Il venditore chiede ${prezzoRichiesto}€ per un oggetto che ne vale circa ${resaleVal}€. L'annuncio è fuori mercato per il flipping e una trattativa troppo aggressiva verrebbe rifiutata.`
    } else {
      const scontoRealistico = Math.min(28, Math.max(12, Math.round(((prezzoRichiesto - targetBase) / prezzoRichiesto) * 100)))
      const offertaRealistica = Math.round(prezzoRichiesto * (1 - scontoRealistico / 100))
      consiglioExtra += ` Il venditore chiede ${prezzoRichiesto}€: proponi un'offerta realistica di ${offertaRealistica}€ (-${scontoRealistico}%) per massimizzare la probabilità di accordo.`
    }
  }

  return {
    titoloRilevato: titoloPulito,
    rawText: testoAnnuncio,
    schedaOggetto: {
      tipologia: `${titoloPulito} (${categoriaNome})`,
      fasciaMercato: `${categoriaNome} | Vendita consigliata su ${piattaformaConsigliata}`,
      prezzoNuovo: `Prezzo stimato da nuovo (Retail / Web): ~${retailMin}€ – ${retailMax}€`,
      prezzoUsatoDettaglio: `~${resaleVal}€ (valore reale di vendita rapida su Subito/Vinted)`
    },
    strategiaFlipping: [
      { voce: 'Offerta Target d\'Acquisto', valore: `${targetVal}€`, badge: 'DA INVIARE', highlight: true },
      { voce: 'Tetto Massimo da non superare', valore: `${maxVal}€`, nota: 'Oltre questa cifra il margine scende' },
      { voce: 'Prezzo di Rivendita Rapida', valore: `${resaleVal}€`, nota: `Su ${piattaformaConsigliata}` },
      { voce: 'Profitto Netto Stimato', valore: `+${profit}€`, nota: `ROI: +${roi}%`, isProfit: true }
    ],
    liquidita: {
      livello: liquiditaLivello,
      benchmark: `Mercato secondario attivo su Subito Torino e Vinted`,
      consiglioOperativo: consiglioExtra
    },
    controlliDalVivo: checklistControlli,
    valoreRivenditaUsato: resaleVal,
    prezzoRichiesto: prezzoRichiesto || Math.round(resaleVal * 0.85),
    offertaTarget: targetVal,
    tettoMassimo: maxVal,
    profittoNetto: profit,
    roi,
    scriptTrattativa: {
      subito: `Ciao! Ho visto il tuo annuncio per "${titoloPulito}". Se l'oggetto è in ottime condizioni e perfettamente funzionante, posso offrirti ${targetVal}€ e venire a fare ritiro a mano di persona oggi stesso in contanti a Torino, così concludiamo subito senza farti perdere tempo. Fammi sapere se per te può andare bene!`,
      whatsapp: `Buongiorno! Ti scrivo per ${titoloPulito}. Sono di Torino e posso fare ritiro a mano oggi a ${targetVal}€ in contanti sul posto. Fammi sapere dove ci possiamo incontrare, grazie!`
    }
  }
}
