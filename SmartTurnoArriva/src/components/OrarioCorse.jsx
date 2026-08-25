import React, { useState, useMemo, useRef } from 'react';
import { Clock, Search, X, Bus, ChevronDown, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import orarioCorseData from '../data/orario_corse_data.json';
import databaseOrari from '../data/database_orari.json';
import turniCorseData from '../data/turni_corse_db.json';

// Linee disponibili con descrizione e capolinea
const AVAILABLE_LINES = [
  { id: '268', code: '268', name: 'Linea 268', route: 'Torino ↔ Caselle Aeroporto', count: 144, outLabel: '➔ Aeroporto', inLabel: '➔ Torino' },
  { id: '275/282', code: '275/282', name: 'Linea 275/282', route: 'Torino ↔ Pinerolo ↔ Perosa ↔ Sestriere ↔ Oulx', count: 156, outLabel: '➔ Pinerolo / Sestriere', inLabel: '➔ Torino' },
  { id: '901', code: '901', name: 'Linea 901 (Val Pellice)', route: 'Bobbio ↔ Torre Pellice ↔ Luserna ↔ Pinerolo ↔ Torino', count: 115, outLabel: '➔ Bobbio Pellice', inLabel: '➔ Torino' },
  { id: '285', code: '285', name: 'Linea 285 (Alta Val Susa)', route: 'Oulx FS ↔ Sauze d\'Oulx ↔ Cesana ↔ Claviere ↔ Sestriere', count: 111, outLabel: '➔ Sestriere / Claviere', inLabel: '➔ Oulx FS' },
  { id: '267', code: '267', name: 'Linea 267', route: 'Torino ↔ Nichelino ↔ Vinovo ↔ Piobesi Torinese', count: 107, outLabel: '➔ Piobesi / Vinovo', inLabel: '➔ Torino' },
  { id: '265', code: '265', name: 'Linea 265 (Canavese)', route: 'Torino ↔ Chivasso ↔ Caluso ↔ Ivrea ↔ Pont-St-Martin', count: 75, outLabel: '➔ Ivrea / Pont', inLabel: '➔ Torino' },
  { id: '283', code: '283', name: 'Linea 283', route: 'Pinerolo ↔ Roletto ↔ Frossasco ↔ Cantalupa', count: 55, outLabel: '➔ Cantalupa', inLabel: '➔ Pinerolo' },
  { id: '303', code: '303', name: 'Linea 303 (Val Germanasca)', route: 'Torino / Pinerolo ↔ Perosa ↔ Perrero ↔ Prali', count: 55, outLabel: '➔ Perrero / Prali', inLabel: '➔ Perosa / Torino' },
  { id: '278', code: '278', name: 'Linea 278', route: 'Pinerolo ↔ Buriasco ↔ Cercenasco ↔ Vigone ↔ Pancalieri', count: 40, outLabel: '➔ Vigone / Pancalieri', inLabel: '➔ Pinerolo' },
  { id: '274', code: '274', name: 'Linea 274 (Val Susa)', route: 'Avigliana ↔ S.Ambrogio ↔ Sant\'Antonino ↔ Bruzolo ↔ Susa', count: 33, outLabel: '➔ Susa', inLabel: '➔ Avigliana' },
  { id: '20 (Malpensa Express)', code: '20', name: 'Linea 20 Malpensa', route: 'Torino ↔ Chivasso ↔ Carisio ↔ Milano Malpensa', count: 30, outLabel: '➔ Malpensa', inLabel: '➔ Torino' },
  { id: '101 (Torino - Aosta / SAVDA)', code: '101', name: 'Linea 101 SAVDA', route: 'Torino ↔ Chivasso ↔ Ivrea ↔ Pont ↔ Verrès ↔ Aosta', count: 14, outLabel: '➔ Aosta', inLabel: '➔ Torino' },
  { id: 'SAVDA (Aosta ↔ Malpensa)', code: 'SAVDA-MXP', name: 'SAVDA Aosta ↔ Malpensa', route: 'Aosta ↔ Châtillon ↔ Verrès ↔ Pont ↔ Malpensa', count: 10, outLabel: '➔ Malpensa', inLabel: '➔ Aosta' }
];

// Configurazioni fermate canoniche ordinate per corridoio geografico (Andata)
const CANONICAL_LINE_STOPS = {
  '268': [
    { key: 'to_pn', full: 'Torino Porta Nuova', short: 'TO - Porta Nuova', patterns: ['PORTA NUOVA'] },
    { key: 'to_ps', full: 'Torino Porta Susa', short: 'TO - Porta Susa', patterns: ['PORTA SUSA'] },
    { key: 'to_umb', full: 'Torino Umbria/Livorno', short: 'TO - Umbria/Liv.', patterns: ['UMBRIA', 'LIVORNO'] },
    { key: 'to_stra', full: 'Torino Stradella', short: 'TO - Stradella', patterns: ['STRADELLA'] },
    { key: 'to_ver', full: 'Torino Veronese', short: 'TO - Veronese', patterns: ['VERONESE', 'STAMPINI'] },
    { key: 'borgaro', full: 'Borgaro Torinese', short: 'Borgaro T.se', patterns: ['BORGARO'] },
    { key: 'caselle_vt', full: 'Caselle Via Torino', short: 'Caselle V. Torino', patterns: ['VIA TORINO', 'CASELLE V. TORINO'] },
    { key: 'caselle_sa', full: 'Caselle Strada Aeroporto', short: 'Caselle Str. Aeroporto', patterns: ['STRADA AEROPORTO', 'STR. AEROPORTO', 'STR.AEROP'] },
    { key: 'caselle_aero', full: 'Caselle Aeroporto', short: 'Caselle Aeroporto', patterns: ['AEROPORTO', 'CASELLE AEROPORTO'] }
  ],
  '275/282': [
    { key: 'to_ps', full: 'Torino Porta Susa', short: 'TO - Porta Susa', patterns: ['PORTA SUSA'] },
    { key: 'to_pn', full: 'Torino Porta Nuova', short: 'TO - Porta Nuova', patterns: ['PORTA NUOVA'] },
    { key: 'to_vinz', full: 'Torino C.so Vinzaglio', short: 'TO - Vinzaglio', patterns: ['VINZAGLIO'] },
    { key: 'to_maur', full: 'Torino Mauriziano', short: 'TO - Mauriziano', patterns: ['MAURIZIANO', 'TURATI'] },
    { key: 'to_seba', full: 'Torino Sebastopoli', short: 'TO - Sebastopoli', patterns: ['SEBASTOPOLI'] },
    { key: 'to_poveri', full: 'Torino Poveri Vecchi', short: 'TO - Poveri Vecchi', patterns: ['POVERI VECCHI'] },
    { key: 'to_cosenza', full: 'Torino C.so Cosenza', short: 'TO - Cosenza', patterns: ['COSENZA'] },
    { key: 'to_caio', full: 'Torino Caio Mario', short: 'TO - Caio Mario', patterns: ['CAIO MARIO'] },
    { key: 'to_drosso', full: 'Torino Strada Drosso', short: 'TO - Drosso', patterns: ['DROSSO'] },
    { key: 'stupinigi', full: 'Stupinigi (Palazzina/Ippodromo)', short: 'Stupinigi', patterns: ['STUPINIGI', 'IPPODROMO', 'PALAZZINA'] },
    { key: 'candiolo', full: 'Candiolo IRCCS / Bivio', short: 'Candiolo IRCCS', patterns: ['CANDIOLO', 'IRCCS', 'RICERCHE'] },
    { key: 'none', full: 'None (Bivio / Fornaci)', short: 'None Bivio', patterns: ['NONE -', 'NONE BIVIO', 'FORNACI'] },
    { key: 'volvera', full: 'Volvera Gerbole', short: 'Volvera Gerbole', patterns: ['VOLVERA', 'GERBOLE'] },
    { key: 'airasca', full: 'Airasca (Centro / SKF)', short: 'Airasca', patterns: ['AIRASCA', 'SKF'] },
    { key: 'piscina', full: 'Piscina (Baudi / Botteghe)', short: 'Piscina', patterns: ['PISCINA', 'BAUDI', 'BOTTEGHE', 'BSBORDANO', 'BAUDE'] },
    { key: 'riva', full: 'Riva di Pinerolo', short: 'Riva di Pin.', patterns: ['RIVA DI PINEROLO', 'RIVA -', 'RIVA '] },
    { key: 'pinerolo', full: 'Pinerolo - Movicentro', short: 'Pinerolo-Movicentro', patterns: ['PINEROLO -', 'PIN. -', 'PINEROLO CENTRO', 'PINEROLO CAVOUR', 'PINEROLO MOV', 'MACUMBA', 'MOVICENTRO', 'CENTRO STUDI'], excludes: ['RIVA DI PINEROLO', 'SAN SECONDO DI PINEROLO'] },
    { key: 'abbadia', full: 'Abbadia Alpina', short: 'Abbadia Alp.', patterns: ['ABBADIA', 'PONTE LEMINA', 'S. MARTINO'] },
    { key: 'porte', full: 'Porte', short: 'Porte', patterns: ['PORTE'] },
    { key: 's_germano', full: 'San Germano Chisone', short: 'S. Germano Ch.', patterns: ['S. GERMANO', 'SAN GERMANO'] },
    { key: 'villar', full: 'Villar Perosa / Dubbione', short: 'Villar Perosa', patterns: ['VILLAR PEROSA', 'V. PEROSA', 'DUBBIONE'] },
    { key: 'pinasca', full: 'Pinasca', short: 'Pinasca', patterns: ['PINASCA'] },
    { key: 'pomaretto', full: 'Pomaretto (Bivio Ospedale)', short: 'Pomaretto', patterns: ['POMARETTO'] },
    { key: 'perosa', full: 'Perosa Argentina (P.za 3° Alpini)', short: 'Perosa Arg.', patterns: ['PEROSA ARG', 'TERZO ALPINI', 'RG.-PZZA', 'PEROSA -', 'PEROSA ('], excludes: ['VILLAR PEROSA', 'V. PEROSA'] },
    { key: 'castel_bosco', full: 'Castel del Bosco', short: 'Castel d. Bosco', patterns: ['CASTEL DEL BOSCO'] },
    { key: 'roure', full: 'Roure / Roreto / Balma', short: 'Roure / Balma', patterns: ['ROURE', 'RORETO', 'BALMA'] },
    { key: 'mentoulles', full: 'Mentoulles / Villaretto', short: 'Mentoulles', patterns: ['MENTOULLES', 'VILLARETTO'] },
    { key: 'fenestrelle', full: 'Fenestrelle', short: 'Fenestrelle', patterns: ['FENESTRELLE'] },
    { key: 'usseaux', full: 'Usseaux / Pourrieres', short: 'Usseaux Bivio', patterns: ['USSEAUX', 'POURRIERES'] },
    { key: 'pragelato', full: 'Pragelato (Plan / Traverses)', short: 'Pragelato', patterns: ['PRAGELATO', 'PLAN', 'TRAVERSES'] },
    { key: 'sestriere', full: 'Sestriere / Borgata', short: 'Sestriere', patterns: ['SESTRIERE', 'BORGATA'] },
    { key: 'cesana', full: 'Cesana Torinese', short: 'Cesana T.se', patterns: ['CESANA'] },
    { key: 'oulx', full: 'Oulx (Stazione FS / Garambois)', short: 'Oulx FS', patterns: ['OULX'] }
  ],
  '901': [
    { key: 'bobbio', full: 'Bobbio Pellice', short: 'Bobbio Pellice', patterns: ['BOBBIO'] },
    { key: 'villar_p', full: 'Villar Pellice', short: 'Villar Pellice', patterns: ['VILLAR PELLICE', 'CHABRIOLS'] },
    { key: 's_margh', full: 'Santa Margherita', short: 'S. Margherita', patterns: ['MARGHERITA', 'VANDALINO'] },
    { key: 'torre_p', full: 'Torre Pellice', short: 'Torre Pellice', patterns: ['TORRE PELLICE'] },
    { key: 'luserna', full: 'Luserna p.zza Partigiani', short: 'Luserna', patterns: ['LUSERNA', 'PARTIGIANI'] },
    { key: 'bibiana', full: 'Ponte Bibiana / FS', short: 'Bibiana FS', patterns: ['BIBIANA'] },
    { key: 'bricherasio', full: 'Bricherasio', short: 'Bricherasio', patterns: ['BRICHERASIO'] },
    { key: 'moreri', full: 'Cappella Moreri', short: 'Cap. Moreri', patterns: ['MORERI'] },
    { key: 's_secondo', full: 'San Secondo (Cantine/Bima)', short: 'San Secondo', patterns: ['SAN SECONDO'] },
    { key: 'pin_cav', full: 'Pinerolo p.zza Cavour', short: 'PIN. - Cavour', patterns: ['CAVOUR'] },
    { key: 'pin_mov', full: 'Pinerolo - Movicentro', short: 'Pinerolo-Movicentro', patterns: ['MOVICENTRO', 'PINEROLO MOVICENTRO', 'PIN. - MOVICENTRO'], excludes: ['RIVA DI PINEROLO', 'SAN SECONDO'] },
    { key: 'pin_studi', full: 'Pinerolo Centro Studi', short: 'PIN. - Centro Studi', patterns: ['CENTRO STUDI', 'IMMACOLATA'] },
    { key: 'to_airasca', full: 'Airasca / None Bivio', short: 'Airasca/None', patterns: ['AIRASCA', 'NONE BIVIO', 'BOTTEGHE'] },
    { key: 'to_candiolo', full: 'Candiolo IRCCS', short: 'Candiolo IRCCS', patterns: ['CANDIOLO'] },
    { key: 'to_stup', full: 'Stupinigi', short: 'Stupinigi', patterns: ['STUPINIGI'] },
    { key: 'to_drosso', full: 'Torino Strada Drosso', short: 'TO - Drosso', patterns: ['DROSSO'] },
    { key: 'to_caio', full: 'Torino Caio Mario', short: 'TO - Caio Mario', patterns: ['CAIO MARIO', 'POVERI VECCHI'] },
    { key: 'to_pn', full: 'Torino Porta Nuova', short: 'TO - Porta Nuova', patterns: ['PORTA NUOVA', 'V.EMAN', 'BOLZANO'] },
    { key: 'to_ps', full: 'Torino Porta Susa', short: 'TO - Porta Susa', patterns: ['PORTA SUSA'] }
  ],
  '285': [
    { key: 'oulx_fs', full: 'Oulx Stazione FS', short: 'Oulx FS', patterns: ['OULX - STAZIONE FS', 'OULX FS', 'OULX -SCUOLE'] },
    { key: 'oulx_gar', full: 'Oulx p.zza Garambois', short: 'Oulx Garambois', patterns: ['GARAMBOIS'] },
    { key: 'sauze_oulx', full: "Sauze d'Oulx", short: "Sauze d'Oulx", patterns: ["SAUZE D'OULX", 'SAN MARCO'] },
    { key: 'fenils', full: 'Fenils / Amazas', short: 'Fenils / Amazas', patterns: ['FENILS', 'AMAZAS', 'SEGUIN'] },
    { key: 'cesana', full: 'Cesana Torinese', short: 'Cesana T.se', patterns: ['CESANA'] },
    { key: 'sauze_ces', full: 'Sauze di Cesana', short: 'Sauze di Ces.', patterns: ['SAUZE DI CESANA'] },
    { key: 'claviere', full: 'Claviere', short: 'Claviere', patterns: ['CLAVIERE'] },
    { key: 'sestriere', full: 'Sestriere', short: 'Sestriere', patterns: ['SESTRIERE'] }
  ],
  '267': [
    { key: 'to_bolz', full: 'Torino C.so Bolzano / De Cristoforis', short: 'TO - Bolzano', patterns: ['BOLZANO', 'CRISTOFORIS'] },
    { key: 'to_ling', full: 'Torino Lingotto / Nizza', short: 'TO - Lingotto', patterns: ['LINGOTTO', 'NIZZA', 'BENGASI'] },
    { key: 'to_caio', full: 'Torino Caio Mario / Drosso', short: 'TO - Caio Mario', patterns: ['CAIO MARIO', 'DROSSO', 'POVERIVECCHI'] },
    { key: 'nich_mun', full: 'Nichelino Municipio', short: 'Nichelino Mun.', patterns: ['NICHELINO - MUNICIPIO', 'DEBOUCH'] },
    { key: 'nich_fs', full: 'Nichelino Stazione FS', short: 'Nichelino FS', patterns: ['NICHELINO - STAZIONE FS'] },
    { key: 'garino', full: 'Garino', short: 'Garino', patterns: ['GARINO'] },
    { key: 'vinovo', full: 'Vinovo (Tetti Rosa / Torrette)', short: 'Vinovo', patterns: ['VINOVO', 'TETTI ROSA', 'TORRETTE'] },
    { key: 'carignano', full: 'Carignano (Donatori Avis)', short: 'Carignano', patterns: ['CARIGNANO'] },
    { key: 'candiolo', full: 'Candiolo', short: 'Candiolo', patterns: ['CANDIOLO'] },
    { key: 'piobesi', full: 'Piobesi Torinese (Municipio/Capolinea)', short: 'Piobesi T.se', patterns: ['PIOBESI'] }
  ],
  '265': [
    { key: 'to_bolz', full: 'Torino Autostazione c.so Bolzano', short: 'TO - Bolzano', patterns: ['BOLZANO', 'CATTANEO', 'SETTEMBRINI'] },
    { key: 'to_cesare', full: 'Torino C.so Giulio Cesare', short: 'TO - G. Cesare', patterns: ['GIULIO CESARE', 'G.CESARE', 'G. CESARE', 'IVECO', 'CONAD'] },
    { key: 'settimo', full: 'Settimo Torinese Casello A4', short: 'Settimo A4', patterns: ['SETTIMO'] },
    { key: 'chivasso', full: 'Chivasso (Bivio Mosche / Boschetto)', short: 'Chivasso Bivio', patterns: ['CHIVASSO', 'MOSCHE', 'BOSCHETTO'] },
    { key: 'montanaro', full: 'Montanaro Stazione FS', short: 'Montanaro FS', patterns: ['MONTANARO'] },
    { key: 'candia', full: 'Candia Canavese', short: 'Candia Can.', patterns: ['CANDIA'] },
    { key: 'mercenasco', full: 'Mercenasco Stazione FS', short: 'Mercenasco FS', patterns: ['MERCENASCO'] },
    { key: 'caluso', full: 'Caluso Stazione FS', short: 'Caluso FS', patterns: ['CALUSO'] },
    { key: 'ivrea_p_aosta', full: 'Ivrea Porta Aosta', short: 'Ivrea P. Aosta', patterns: ['PORTA AOSTA', 'DI VITTORIO'] },
    { key: 'ivrea_fs', full: 'Ivrea Stazione FS', short: 'Ivrea FS', patterns: ['IVREA - STAZIONE FS', 'IVREA - MOVICENTRO'] },
    { key: 'pont_sm', full: 'Pont Saint Martin Stazione FS', short: 'Pont-St-Martin', patterns: ['PONT'] }
  ],
  '283': [
    { key: 'pin_cav', full: 'Pinerolo p.zza Cavour', short: 'PIN. - Cavour', patterns: ['CAVOUR'] },
    { key: 'pin_mov', full: 'Pinerolo - Movicentro', short: 'Pinerolo-Movicentro', patterns: ['MOVICENTRO', 'PINEROLO MOVICENTRO', 'PIN. - MOVICENTRO'], excludes: ['RIVA DI PINEROLO'] },
    { key: 'pin_martiri', full: 'Pinerolo via Martiri XXI', short: 'PIN. - Martiri XXI', patterns: ['MARTIRI XXI'] },
    { key: 'pin_immac', full: 'Pinerolo Ist. Immacolata', short: 'PIN. - Immacolata', patterns: ['IMMACOLATA'] },
    { key: 'roncaglia', full: 'Frazione Roncaglia', short: 'Roncaglia', patterns: ['RONCAGLIA'] },
    { key: 'roletto', full: 'Roletto', short: 'Roletto', patterns: ['ROLETTO'] },
    { key: 'frossasco', full: 'Frossasco Bivio', short: 'Frossasco Biv.', patterns: ['FROSSASCO'] },
    { key: 'cantalupa', full: 'Cantalupa', short: 'Cantalupa', patterns: ['CANTALUPA'] }
  ],
  '303': [
    { key: 'to_auto', full: 'Torino Autostazione', short: 'TO - Autostaz.', patterns: ['TORINO AUTOSTAZIONE', 'TORINO'] },
    { key: 'pinerolo', full: 'Pinerolo', short: 'Pinerolo', patterns: ['PINEROLO'] },
    { key: 'perosa_arg', full: 'Perosa Argentina', short: 'Perosa Arg.', patterns: ['PEROSA ARGENTINA', 'PEROSA'] },
    { key: 'pomaretto', full: 'Pomaretto (Ospedale/P.Lausa)', short: 'Pomaretto', patterns: ['POMARETTO'] },
    { key: 'p_rabbioso', 'full': 'Ponte Rabbioso', short: 'P.te Rabbioso', patterns: ['RABBIOSO'] },
    { key: 'chiotti', full: 'Chiotti / Pomeyfre', short: 'Chiotti', patterns: ['CHIOTTI', 'POMEYFRE'] },
    { key: 'trossieri', full: 'Trossieri / Gianna', short: 'Trossieri', patterns: ['TROSSIERI', 'GIANNA'] },
    { key: 'perrero', full: 'Perrero', short: 'Perrero', patterns: ['PERRERO'] },
    { key: 'rodoretto', full: 'Rodoretto Bivio', short: 'Rodoretto Biv.', patterns: ['RODORETTO'] },
    { key: 'prali_v', full: 'Villa di Prali', short: 'Villa di Prali', patterns: ['VILLA DI PRALI'] },
    { key: 'prali_ghigo', full: 'Prali Ghigo', short: 'Prali Ghigo', patterns: ['PRALI GHIGO', 'PRALI'] },
    { key: 'prali_segg', full: 'Prali Seggiovie', short: 'Prali Seggiovie', patterns: ['SEGGIOVIE'] }
  ],
  '278': [
    { key: 'pin_cav', full: 'Pinerolo p.zza Cavour', short: 'PIN. - Cavour', patterns: ['CAVOUR'] },
    { key: 'pin_mov', full: 'Pinerolo - Movicentro', short: 'Pinerolo-Movicentro', patterns: ['MOVICENTRO', 'PINEROLO MOVICENTRO', 'PIN. - MOVICENTRO'], excludes: ['RIVA DI PINEROLO'] },
    { key: 'pin_fs', full: 'Pinerolo Stazione FS / Olimpica', short: 'PIN. - Staz. FS', patterns: ['STAZIONE FS', 'OLIMPICA'] },
    { key: 'pin_studi', full: 'Pinerolo Centro Studi / Bignone', short: 'PIN. - Centro Studi', patterns: ['CENTRO STUDI', 'BIGNONE', 'IMMACOLATA', 'SALUZZO', 'COTTOLENGO', 'S. CROCE'] },
    { key: 'riva', full: 'Riva di Pinerolo', short: 'Riva di Pin.', patterns: ['RIVA DI PINEROLO', 'MACUMBA'] },
    { key: 'baudenasca', full: 'Baudenasca', short: 'Baudenasca', patterns: ['BAUDENASCA'] },
    { key: 'buriasco', full: 'Buriasco / Stella', short: 'Buriasco', patterns: ['BURIASCO', 'STELLA'] },
    { key: 'macello', full: 'Macello', short: 'Macello', patterns: ['MACELLO'] },
    { key: 'cercenasco', full: 'Cercenasco', short: 'Cercenasco', patterns: ['CERCENASCO'] },
    { key: 'vigone', full: 'Vigone', short: 'Vigone', patterns: ['VIGONE', 'MURISENGHI'] },
    { key: 'virle', full: 'Virle Piemonte / Osasio', short: 'Virle Piem.', patterns: ['VIRLE', 'OSASIO', 'APPENDINI', 'SCALENGHE'] },
    { key: 'pancalieri', full: 'Pancalieri', short: 'Pancalieri', patterns: ['PANCALIERI'] }
  ],
  '274': [
    { key: 'avig_fs', full: 'Avigliana Stazione FS', short: 'Avigliana FS', patterns: ['AVIGLIANA'] },
    { key: 's_ambrogio', full: 'Sant\'Ambrogio', short: 'S. Ambrogio', patterns: ['AMBROGIO'] },
    { key: 'condove', full: 'Condove Bivio', short: 'Condove Biv.', patterns: ['CONDOVE'] },
    { key: 'vaie', full: 'Vaie Bivio', short: 'Vaie Bivio', patterns: ['VAIE'] },
    { key: 's_antonino', full: 'Sant\'Antonino Stazione FS', short: 'S. Antonino FS', patterns: ['ANTONINO'] },
    { key: 'bruzolo', full: 'Bruzolo', short: 'Bruzolo', patterns: ['BRUZOLO'] },
    { key: 'villar_foc', full: 'Villar Focchiardo Bivio', short: 'Villar Foc. Biv.', patterns: ['VILLAR FOCCHIARDO', 'TEKFOR', 'LUTHER KING'] },
    { key: 's_didero', full: 'San Didero Bivio', short: 'S. Didero Biv.', patterns: ['DIDERO'] },
    { key: 's_giorio', full: 'San Giorio Bivio', short: 'S. Giorio Biv.', patterns: ['GIORIO'] },
    { key: 'foresto', full: 'Foresto Bivio', short: 'Foresto Biv.', patterns: ['FORESTO', 'CASCINE VICA'] },
    { key: 'susa_fs', full: 'Susa Stazione FS', short: 'Susa FS', patterns: ['SUSA'] }
  ],
  '101 (Torino - Aosta / SAVDA)': [
    { key: 'to_bolz', full: 'Torino Autostazione corso Bolzano', short: 'TO - Bolzano', patterns: ['BOLZANO'] },
    { key: 'to_cesare', full: 'Torino Corso Giulio Cesare 426', short: 'TO - G. Cesare', patterns: ['GIULIO CESARE'] },
    { key: 'chivasso', full: 'Chivasso Centro Casello A4', short: 'Chivasso A4', patterns: ['CHIVASSO'] },
    { key: 'ivrea', full: 'Ivrea Movicentro / Stazione FS', short: 'Ivrea FS', patterns: ['IVREA'] },
    { key: 'pont', full: 'Pont-Saint-Martin (Piazza I Maggio)', short: 'Pont-St-Martin', patterns: ['PONT'] },
    { key: 'verres', full: 'Verrès Autostazione', short: 'Verrès', patterns: ['VERRES', 'VERRÈS'] },
    { key: 'chatillon', full: 'Châtillon Autostazione FS', short: 'Châtillon', patterns: ['CHATILLON', 'CHÂTILLON'] },
    { key: 'aosta', full: 'Aosta Autostazione (Piazza Manzetti)', short: 'Aosta', patterns: ['AOSTA'] }
  ],
  '20 (Malpensa Express)': [
    { key: 'to_catt', full: 'Torino Piazza Cattaneo', short: 'TO - Cattaneo', patterns: ['CATTANEO'] },
    { key: 'to_srita', full: 'Torino Mombarcaro (Santa Rita)', short: 'TO - Santa Rita', patterns: ['MOMBARCARO', 'SANTA RITA'] },
    { key: 'to_bolz', full: 'Torino Autostazione corso Bolzano', short: 'TO - Bolzano', patterns: ['BOLZANO'] },
    { key: 'to_cesare', full: 'Torino Corso Giulio Cesare 426', short: 'TO - G. Cesare', patterns: ['GIULIO CESARE'] },
    { key: 'chivasso', full: 'Chivasso Centro Casello A4', short: 'Chivasso A4', patterns: ['CHIVASSO'] },
    { key: 'carisio', full: 'Carisio Casello A4', short: 'Carisio A4', patterns: ['CARISIO'] },
    { key: 'mxp_t1', full: 'Milano Malpensa Terminal 1 (Ovest)', short: 'Malpensa T1', patterns: ['TERMINAL 1', 'T1', 'OVEST'] },
    { key: 'mxp_t2', full: 'Milano Malpensa Terminal 2 (Nord)', short: 'Malpensa T2', patterns: ['TERMINAL 2', 'T2', 'NORD'] }
  ],
  'SAVDA (Aosta ↔ Malpensa)': [
    { key: 'aosta', full: 'Aosta Autostazione (Piazza Manzetti)', short: 'Aosta', patterns: ['AOSTA'] },
    { key: 'chatillon', full: 'Châtillon Autostazione FS', short: 'Châtillon', patterns: ['CHATILLON', 'CHÂTILLON'] },
    { key: 'verres', full: 'Verrès Autostazione', short: 'Verrès', patterns: ['VERRES', 'VERRÈS'] },
    { key: 'pont', full: 'Pont-Saint-Martin (Piazza I Maggio)', short: 'Pont-St-Martin', patterns: ['PONT'] },
    { key: 'mxp_t1', full: 'Milano Malpensa Terminal 1 (Ovest)', short: 'Malpensa T1', patterns: ['TERMINAL 1', 'T1', 'OVEST'] },
    { key: 'mxp_t2', full: 'Milano Malpensa Terminal 2 (Nord)', short: 'Malpensa T2', patterns: ['TERMINAL 2', 'T2', 'NORD'] }
  ]
};

// Determina con precisione se una corsa è di Ritorno
const isTripReturn = (trip, lineId) => {
  const stops = trip.stops || [];
  if (stops.length === 0) return false;
  
  const realStops = stops.filter(s => s.time && !['A', 'F', 'S', '—', '-'].includes(s.time.trim()));
  const activeStops = realStops.length > 0 ? realStops : stops;
  
  const firstStop = (activeStops[0]?.name || '').toUpperCase();
  const lastStop = (activeStops[activeStops.length - 1]?.name || '').toUpperCase();
  
  if (lineId === '275/282') {
    if (lastStop.includes('TORINO') || lastStop.includes('TO -') || lastStop.includes('TO-') || lastStop.includes('PORTA NUOVA') || lastStop.includes('PORTA SUSA')) {
      return true;
    }
    if (firstStop.includes('TORINO') || firstStop.includes('TO -') || firstStop.includes('TO-') || firstStop.includes('PORTA NUOVA') || firstStop.includes('PORTA SUSA')) {
      return false;
    }
    if (firstStop.includes('SESTRIERE') || firstStop.includes('OULX') || firstStop.includes('CESANA') || firstStop.includes('FENESTRELLE') || firstStop.includes('PEROSA')) {
      return true;
    }
    return false;
  }
  
  if (lineId === '901') {
    if (lastStop.includes('TORINO') || lastStop.includes('PINEROLO') || lastStop.includes('PIN.')) return true;
    return false;
  }
  
  if (lineId === '267') {
    if (lastStop.includes('TORINO') || lastStop.includes('BOLZANO') || lastStop.includes('LINGOTTO')) return true;
    return false;
  }
  
  if (lineId === '265') {
    if (lastStop.includes('TORINO') || lastStop.includes('BOLZANO') || lastStop.includes('SETTEMBRINI')) return true;
    return false;
  }
  
  if (lineId === '278' || lineId === '283') {
    if (lastStop.includes('PINEROLO') || lastStop.includes('PIN.')) return true;
    return false;
  }
  
  if (lineId === '303') {
    if (lastStop.includes('TORINO') || lastStop.includes('PINEROLO') || lastStop.includes('PEROSA')) return true;
    return false;
  }
  
  if (lineId === '274') {
    if (lastStop.includes('AVIGLIANA')) return true;
    return false;
  }
  
  if (lineId === '285') {
    if (lastStop.includes('OULX')) return true;
    return false;
  }
  
  if (lineId.includes('Malpensa') || lineId === 'SAVDA (Aosta ↔ Malpensa)') {
    if (firstStop.includes('MALPENSA') || lastStop.includes('AOSTA') || lastStop.includes('TORINO')) return true;
    return false;
  }
  
  if (lineId === '101 (Torino - Aosta / SAVDA)') {
    if (lastStop.includes('TORINO') || lastStop.includes('BOLZANO')) return true;
    return false;
  }
  
  return false;
};

// Helper per ripulire e formattare orari HH:MM
const cleanTime = (t) => {
  if (!t || t === '—' || t === '-') return '';
  t = String(t).trim().replace('.', ':');
  const parts = t.split(':');
  if (parts.length === 2) {
    const h = parseInt(parts[0], 10);
    const m = parseInt(parts[1], 10);
    if (!isNaN(h) && !isNaN(m)) {
      return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
    }
  }
  return t;
};

// Helper per pulire orari da mostrare nelle celle (rimuove annotazioni come S, F, A)
const cleanDisplayTime = (val) => {
  if (!val || val === '—' || val === '-') return '—';
  const v = String(val).trim();
  if (/^[A-Za-z]$/.test(v)) return '—';
  return v;
};

// Trova codice turno autista per una corsa
// Trova codice turno autista per una corsa con verifica incrociata partenza/arrivo
const resolveTurnoForTrip = (trip) => {
  if (trip.turno && trip.turno !== '—') return trip.turno;
  if (!turniCorseData || turniCorseData.length === 0) return '—';
  
  const stops = trip.stops || [];
  const realStops = stops.filter(s => cleanTime(s.time));
  if (realStops.length === 0) return '—';
  
  const tripDep = cleanTime(realStops[0].time);
  const tripArr = cleanTime(realStops[realStops.length - 1].time);
  const tripLine = String(trip.line || '');

  let bestMatch = '—';
  let bestScore = 0;

  for (const t of turniCorseData) {
    const corse = t.corse || [];
    if (corse.length === 0) continue;

    const lastCorseArr = cleanTime(corse[corse.length - 1]?.arrivo);

    for (const c of corse) {
      const cLine = String(c.linea || '');
      const matchLine = !cLine || !tripLine || cLine.includes(tripLine) || tripLine.includes(cLine) || tripLine.split('/')[0] === cLine;
      if (!matchLine) continue;

      const cDep = cleanTime(c.partenza);
      const cArr = cleanTime(c.arrivo);

      // 1. Corrispondenza perfetta: partenza e arrivo completo della corsa coincidono
      if (tripDep && tripArr && cDep === tripDep && (cArr === tripArr || lastCorseArr === tripArr)) {
        return t.codice;
      }

      // 2. Corrispondenza su arrivo finale
      if (tripArr && (cArr === tripArr || lastCorseArr === tripArr)) {
        if (bestScore < 2) {
          bestMatch = t.codice;
          bestScore = 2;
        }
      }

      // 3. Corrispondenza su partenza (solo se l'arrivo non è in aperto conflitto)
      if (tripDep && cDep === tripDep && (!tripArr || !lastCorseArr || Math.abs(parseInt(tripArr.replace(':','')) - parseInt(lastCorseArr.replace(':',''))) <= 5)) {
        if (bestScore < 1.5) {
          bestMatch = t.codice;
          bestScore = 1.5;
        }
      }
    }
  }

  return bestScore >= 1.5 ? bestMatch : '—';
};

// Helper per determinare la direzione predefinita in base al deposito dell'utente
const getDefaultDirectionForDepot = (lineId) => {
  const userDepot = (localStorage.getItem('shiftlink_saved_depot') || '').toLowerCase();
  
  if (['pinerolo', 'perosa', 'bobbio', 'luserna', 'perrero'].some(d => userDepot.includes(d))) {
    if (['275/282', '901', '303', '267'].includes(lineId)) return 'inbound';
    if (['283', '278'].includes(lineId)) return 'outbound';
  }
  
  if (userDepot.includes('caselle')) {
    if (lineId === '268') return 'inbound';
  }
  
  if (['ivrea', 'pont'].some(d => userDepot.includes(d))) {
    if (['265', '101 (Torino - Aosta / SAVDA)'].includes(lineId)) return 'inbound';
  }
  
  if (['susa', 'oulx', 'cesana', 'sestriere'].some(d => userDepot.includes(d))) {
    if (['285', '274'].includes(lineId)) return 'inbound';
  }
  
  return 'outbound';
};

const OrarioCorse = () => {
  const [selectedLineId, setSelectedLineId] = useState('268');
  const [searchTerm, setSearchTerm] = useState('');
  const tableContainerRef = useRef(null);
  const sectionInboundRef = useRef(null);

  const handleLineChange = (lineId) => {
    setSelectedLineId(lineId);
    if (tableContainerRef.current) {
      tableContainerRef.current.scrollTo({ top: 0, left: 0, behavior: 'smooth' });
    }
  };

  const scrollTable = (offset) => {
    if (tableContainerRef.current) {
      tableContainerRef.current.scrollBy({ left: offset, behavior: 'smooth' });
    }
  };

  const scrollToPosition = (position) => {
    if (tableContainerRef.current) {
      tableContainerRef.current.scrollTo({ left: position === 'start' ? 0 : 99999, behavior: 'smooth' });
    }
  };

  const jumpToSection = (section) => {
    if (section === 'top' && tableContainerRef.current) {
      tableContainerRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (section === 'inbound' && sectionInboundRef.current && tableContainerRef.current) {
      const topPos = sectionInboundRef.current.offsetTop;
      tableContainerRef.current.scrollTo({ top: Math.max(0, topPos - 10), behavior: 'smooth' });
    }
  };

  const currentLineInfo = useMemo(() => {
    return AVAILABLE_LINES.find(l => l.id === selectedLineId) || {
      id: selectedLineId,
      name: `Linea ${selectedLineId}`,
      route: '',
      count: 0,
      outLabel: '➔ Andata',
      inLabel: '➔ Ritorno'
    };
  }, [selectedLineId]);

  // Dati calcolati per la linea selezionata (Sezione Andata + Sezione Ritorno per Tabella Unica)
  const { outboundData, inboundData, totalTripsCount } = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();

    // 1. Linea 268
    if (selectedLineId === '268') {
      const headersOut = [
        { full: 'TURNO', short: 'TURNO', isTurno: true },
        ...CANONICAL_LINE_STOPS['268']
      ];
      const headersIn = [
        { full: 'TURNO', short: 'TURNO', isTurno: true },
        ...[...CANONICAL_LINE_STOPS['268']].reverse()
      ];

      const rawOut = orarioCorseData.slice(0, 66).map((row, idx) => ({
        turno: (row[0] || '').trim(),
        isReturn: false,
        cells: row.slice(1, 10),
        rawSearch: row.join(' ')
      }));

      const rawIn = orarioCorseData.slice(66).map((row, idx) => ({
        turno: (row[0] || '').trim(),
        isReturn: true,
        cells: [...row.slice(1, 10)].reverse(), // Fermate e orari invertiti: Caselle a sinistra -> Torino a destra
        rawSearch: row.join(' ')
      }));

      const filteredOut = q ? rawOut.filter(r => r.rawSearch.toLowerCase().includes(q)) : rawOut;
      const filteredIn = q ? rawIn.filter(r => r.rawSearch.toLowerCase().includes(q)) : rawIn;

      return {
        outboundData: {
          title: `Partenze da ${CANONICAL_LINE_STOPS['268'][0].short} ➔ ${CANONICAL_LINE_STOPS['268'][CANONICAL_LINE_STOPS['268'].length - 1].short}`,
          headers: headersOut,
          rows: filteredOut,
          totalCount: rawOut.length
        },
        inboundData: {
          title: `Partenze da ${CANONICAL_LINE_STOPS['268'][CANONICAL_LINE_STOPS['268'].length - 1].short} ➔ ${CANONICAL_LINE_STOPS['268'][0].short}`,
          headers: headersIn,
          rows: filteredIn,
          totalCount: rawIn.length
        },
        totalTripsCount: rawOut.length + rawIn.length
      };
    }

    // 2. Tutte le altre linee dal database
    const allTrips = (databaseOrari.trips || []).filter(t => {
      if (selectedLineId === 'SAVDA (Aosta ↔ Malpensa)') {
        return String(t.line || '').includes('SAVDA') && String(t.line || '').includes('Malpensa');
      }
      return t.line === selectedLineId;
    });
    const lineConfig = CANONICAL_LINE_STOPS[selectedLineId] || [];

    const classifiedTrips = allTrips.map((trip, idx) => {
      const isReturn = isTripReturn(trip, selectedLineId);
      const turno = resolveTurnoForTrip(trip);
      return { trip, turno, isReturn, stops: trip.stops || [], originalIndex: idx };
    });

    const outTrips = classifiedTrips.filter(t => !t.isReturn);
    const inTrips = classifiedTrips.filter(t => t.isReturn);

    const colsOut = lineConfig;
    const colsIn = [...lineConfig].reverse();

    const headersOut = [{ full: 'TURNO', short: 'TURNO', isTurno: true }, ...colsOut];
    const headersIn = [{ full: 'TURNO', short: 'TURNO', isTurno: true }, ...colsIn];

    const mapTripToCells = (tripList, colList, isReturn) => {
      let list = tripList;
      if (q) {
        list = list.filter(t => {
          if (t.turno.toLowerCase().includes(q)) return true;
          return t.stops.some(s => s.name.toLowerCase().includes(q) || s.time.includes(q));
        });
      }

      return list.map(t => {
        const cells = colList.map(col => {
          let matchedTime = '—';
          const excludes = col.excludes || [];
          for (const stop of t.stops) {
            const stopUpper = stop.name.toUpperCase();
            if (excludes.some(ex => stopUpper.includes(ex))) continue;
            if (col.patterns.some(p => stopUpper.includes(p))) {
              matchedTime = stop.time;
              break;
            }
          }
          return matchedTime;
        });

        return {
          turno: t.turno,
          isReturn,
          cells,
          originalIndex: t.originalIndex
        };
      });
    };

    const firstStopName = lineConfig[0]?.short || 'Partenza';
    const lastStopName = lineConfig[lineConfig.length - 1]?.short || 'Arrivo';

    return {
      outboundData: {
        title: `Partenze da ${firstStopName} ➔ ${lastStopName}`,
        headers: headersOut,
        rows: mapTripToCells(outTrips, colsOut, false),
        totalCount: outTrips.length
      },
      inboundData: {
        title: `Partenze da ${lastStopName} ➔ ${firstStopName}`,
        headers: headersIn,
        rows: mapTripToCells(inTrips, colsIn, true),
        totalCount: inTrips.length
      },
      totalTripsCount: classifiedTrips.length
    };
  }, [selectedLineId, searchTerm, currentLineInfo]);

  // Verifica se un header corrisponde al termine di ricerca o è selezionato
  const isHeaderMatched = (header) => {
    if (!searchTerm.trim() || header.isTurno) return false;
    const q = searchTerm.trim().toLowerCase();
    const fullMatch = header.full && header.full.toLowerCase().includes(q);
    const shortMatch = header.short && header.short.toLowerCase().includes(q);
    const patternMatch = header.patterns && header.patterns.some(p => p.toLowerCase().includes(q));
    return fullMatch || shortMatch || patternMatch;
  };

  // Funzione di rendering per l'intestazione di tabella (allineata allo scorrimento orizzontale)
  const renderHeaderRow = (headerList, isStickyTop = true) => (
    <tr style={{
      background: '#131824',
      borderBottom: '2px solid rgba(245, 166, 35, 0.6)'
    }}>
      {headerList.map((h, i) => {
        const isTurno = i === 0;
        const isMatched = isHeaderMatched(h);

        return (
          <th
            key={i}
            style={{
              padding: isTurno ? '6px 4px' : '4px 2px',
              background: isTurno 
                ? '#131824' 
                : isMatched 
                  ? 'linear-gradient(180deg, rgba(245, 166, 35, 0.38) 0%, rgba(245, 166, 35, 0.18) 100%)' 
                  : '#131824',
              color: isTurno 
                ? 'var(--accent-orange)' 
                : isMatched 
                  ? '#fbbf24' 
                  : '#cbd5e1',
              textAlign: 'center',
              borderBottom: isMatched ? '3px solid #f5a623' : '2px solid rgba(245, 166, 35, 0.6)',
              borderRight: isTurno ? '2px solid rgba(245, 166, 35, 0.5)' : isMatched ? '2px solid #f5a623' : '1px solid rgba(255,255,255,0.15)',
              borderLeft: isMatched ? '2px solid #f5a623' : 'none',
              verticalAlign: 'bottom',
              width: isTurno ? '56px' : '44px',
              minWidth: isTurno ? '56px' : '44px',
              maxWidth: isTurno ? '56px' : '44px',
              position: isTurno ? 'sticky' : isStickyTop ? 'sticky' : 'static',
              top: isStickyTop ? 0 : 'auto',
              left: isTurno ? 0 : 'auto',
              zIndex: isTurno ? (isStickyTop ? 40 : 30) : isMatched ? 25 : (isStickyTop ? 20 : 5),
              height: isTurno ? 'auto' : '122px',
              boxShadow: isMatched ? 'inset 0 0 10px rgba(245, 166, 35, 0.3)' : 'none',
              boxSizing: 'border-box'
            }}
            title={h.full}
          >
            <div style={{
              writingMode: isTurno ? 'horizontal-tb' : 'vertical-rl',
              transform: isTurno ? 'none' : 'rotate(180deg)',
              whiteSpace: 'nowrap',
              fontSize: isTurno ? '0.75rem' : isMatched ? '0.74rem' : '0.68rem',
              fontWeight: (isTurno || isMatched) ? '900' : '600',
              letterSpacing: '0.01em',
              color: isTurno ? 'var(--accent-orange)' : isMatched ? '#fbbf24' : '#e2e8f0',
              paddingBottom: isTurno ? '4px' : '6px',
              paddingTop: isTurno ? '0' : '3px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: isTurno ? '100%' : '114px',
              margin: '0 auto',
              textShadow: isMatched ? '0 0 6px rgba(245, 166, 35, 0.5)' : 'none'
            }}>
              {isMatched && <span style={{ fontSize: '0.60rem', marginBottom: '2px' }}>📍</span>}
              <span>{h.short}</span>
            </div>
          </th>
        );
      })}
    </tr>
  );

  // Funzione di rendering per le righe delle corse
  const renderRowItem = (rowItem, rIdx, headerList) => {
    const turnoCode = (rowItem.turno || '').trim();
    const hasTurno = turnoCode !== '' && turnoCode !== '—' && turnoCode !== '-';
    const isEven = rIdx % 2 === 0;
    const rowBg = isEven ? 'rgba(30, 41, 59, 0.55)' : 'rgba(15, 23, 42, 0.95)';
    const stickyBg = isEven ? '#1e293b' : '#0f172a';

    return (
      <tr
        key={rIdx}
        style={{
          background: rowBg,
          borderBottom: '1px solid rgba(255,255,255,0.12)',
          height: '26px',
          transition: 'background 0.1s'
        }}
        onMouseEnter={e => {
          e.currentTarget.style.background = 'rgba(245, 166, 35, 0.2)';
          const stickyCell = e.currentTarget.querySelector('td:first-child');
          if (stickyCell) stickyCell.style.background = '#27272a';
        }}
        onMouseLeave={e => {
          e.currentTarget.style.background = rowBg;
          const stickyCell = e.currentTarget.querySelector('td:first-child');
          if (stickyCell) stickyCell.style.background = stickyBg;
        }}
      >
        {/* Colonna TURNO Sticky con Griglia */}
        <td style={{
          padding: '2px 4px',
          textAlign: 'center',
          position: 'sticky',
          left: 0,
          background: stickyBg,
          zIndex: 5,
          width: '56px',
          minWidth: '56px',
          maxWidth: '56px',
          borderRight: '2px solid rgba(245, 166, 35, 0.4)',
          borderBottom: '1px solid rgba(255,255,255,0.12)',
          fontWeight: '800',
          boxSizing: 'border-box',
          transition: 'background 0.1s'
        }}>
          {hasTurno ? (
            <span style={{
              background: rowItem.isReturn ? 'rgba(16, 185, 129, 0.22)' : 'rgba(245, 166, 35, 0.22)',
              border: rowItem.isReturn ? '1px solid rgba(16, 185, 129, 0.5)' : '1px solid rgba(245, 166, 35, 0.5)',
              color: rowItem.isReturn ? '#34d399' : 'var(--accent-orange)',
              padding: '1px 4px',
              borderRadius: '4px',
              fontSize: '0.68rem',
              fontWeight: '800',
              display: 'inline-block',
              letterSpacing: '-0.02em',
              whiteSpace: 'nowrap'
            }}>
              {turnoCode}
            </span>
          ) : (
            <span style={{ color: 'rgba(255,255,255,0.25)', fontSize: '0.65rem' }}>
              {turnoCode || '—'}
            </span>
          )}
        </td>

        {/* Colonne Fermate a Griglia con Spazio e Contrasto (44px fisse) */}
        {rowItem.cells.map((cellVal, j) => {
          const val = cleanDisplayTime(cellVal);
          const isStopValid = val !== '' && val !== '—' && val !== '-';
          const correspondingHeader = headerList[j + 1];
          const isColMatched = isHeaderMatched(correspondingHeader);

          return (
            <td
              key={j}
              style={{
                padding: '2px 4px',
                textAlign: 'center',
                width: '44px',
                minWidth: '44px',
                maxWidth: '44px',
                boxSizing: 'border-box',
                background: isColMatched 
                  ? (isStopValid ? 'rgba(245, 166, 35, 0.26)' : 'rgba(245, 166, 35, 0.12)')
                  : 'transparent',
                borderLeft: isColMatched ? '1.5px solid rgba(245, 166, 35, 0.6)' : 'none',
                borderRight: isColMatched ? '1.5px solid rgba(245, 166, 35, 0.6)' : '1px solid rgba(255,255,255,0.12)',
                borderBottom: '1px solid rgba(255,255,255,0.12)',
                color: isColMatched
                  ? (isStopValid ? '#fbbf24' : 'rgba(251, 191, 36, 0.4)')
                  : isStopValid 
                    ? (rowItem.isReturn ? '#34d399' : '#38bdf8') 
                    : 'rgba(255,255,255,0.18)',
                fontWeight: isColMatched && isStopValid ? '800' : isStopValid ? '700' : '400',
                fontSize: isColMatched && isStopValid ? '0.74rem' : isStopValid ? '0.72rem' : '0.64rem',
                fontVariantNumeric: 'tabular-nums',
                letterSpacing: '0.01em',
                whiteSpace: 'nowrap',
                boxShadow: isColMatched && isStopValid ? 'inset 0 0 4px rgba(245, 166, 35, 0.2)' : 'none'
              }}
            >
              {isStopValid ? val : '—'}
            </td>
          );
        })}
      </tr>
    );
  };

  return (
    <div style={{
      padding: '0.75rem 0.5rem',
      background: 'var(--bg-app)',
      minHeight: '100vh',
      paddingBottom: '90px',
      width: '100%',
      minWidth: 0,
      boxSizing: 'border-box',
      overflowX: 'hidden'
    }}>
      {/* Intestazione Titolo con Selettore Linea */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '0.4rem',
        marginBottom: '0.75rem',
        padding: '0 0.25rem'
      }}>
        <div>
          <h2 style={{
            fontSize: '1.1rem',
            fontWeight: 'bold',
            color: 'var(--text-main)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            margin: 0
          }}>
            <Clock size={18} style={{ color: 'var(--accent-orange)' }} />
            <span>Orario Corse ({currentLineInfo.name})</span>
          </h2>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '2px 0 0 0' }}>
            {currentLineInfo.route || 'Quadro orario completo con corse di andata e ritorno'}
          </p>
        </div>

        {/* Dropdown rapido scelta linea */}
        <div style={{ position: 'relative' }}>
          <select
            value={selectedLineId}
            onChange={(e) => handleLineChange(e.target.value)}
            style={{
              background: 'var(--bg-card)',
              color: 'var(--accent-cyan)',
              border: '1.5px solid var(--accent-cyan)',
              borderRadius: '8px',
              padding: '6px 28px 6px 10px',
              fontSize: '0.8rem',
              fontWeight: '700',
              cursor: 'pointer',
              outline: 'none',
              appearance: 'none'
            }}
          >
            {AVAILABLE_LINES.map(line => (
              <option key={line.id} value={line.id}>
                {line.name} ({line.route})
              </option>
            ))}
          </select>
          <ChevronDown size={14} style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--accent-cyan)' }} />
        </div>
      </div>

      {/* Selettore Linee a Pills Orizzontali */}
      <div style={{
        display: 'flex',
        gap: '6px',
        overflowX: 'auto',
        paddingBottom: '6px',
        marginBottom: '0.75rem',
        WebkitOverflowScrolling: 'touch'
      }}>
        {AVAILABLE_LINES.map(line => {
          const isSelected = selectedLineId === line.id;
          return (
            <button
              key={line.id}
              type="button"
              onClick={() => handleLineChange(line.id)}
              style={{
                padding: '5px 10px',
                borderRadius: '8px',
                border: isSelected ? '1.5px solid var(--accent-orange)' : '1px solid var(--border-color)',
                background: isSelected ? 'rgba(245, 166, 35, 0.2)' : 'var(--bg-card)',
                color: isSelected ? 'var(--accent-orange)' : 'var(--text-main)',
                fontWeight: isSelected ? '800' : '600',
                fontSize: '0.75rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                transition: 'all 0.15s'
              }}
            >
              <Bus size={12} />
              <span>{line.name}</span>
            </button>
          );
        })}
      </div>

      {/* Barra Azioni Rapide e Ricerca */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '10px',
        padding: '0.6rem 0.75rem',
        marginBottom: '0.75rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.5rem'
        }}>
          {/* Pulsanti di Salto Rapido tra le 2 Sezioni */}
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={() => jumpToSection('top')}
              style={{
                padding: '5px 11px',
                borderRadius: '8px',
                border: '1.5px solid #38bdf8',
                background: 'rgba(56, 189, 248, 0.18)',
                color: '#38bdf8',
                fontWeight: '800',
                fontSize: '0.75rem',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                transition: 'all 0.15s'
              }}
            >
              <span>⬆️ Inizio: {currentLineInfo.outLabel || 'Andata'}</span>
              <span style={{ background: '#38bdf8', color: '#0f172a', borderRadius: '10px', padding: '0 5px', fontSize: '0.65rem', fontWeight: '900' }}>
                {outboundData.rows.length}
              </span>
            </button>

            <button
              type="button"
              onClick={() => jumpToSection('inbound')}
              style={{
                padding: '5px 11px',
                borderRadius: '8px',
                border: '1.5px solid #10b981',
                background: 'rgba(16, 185, 129, 0.18)',
                color: '#10b981',
                fontWeight: '800',
                fontSize: '0.75rem',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                transition: 'all 0.15s'
              }}
            >
              <span>⬇️ Salta a: {currentLineInfo.inLabel || 'Ritorno'}</span>
              <span style={{ background: '#10b981', color: '#0f172a', borderRadius: '10px', padding: '0 5px', fontSize: '0.65rem', fontWeight: '900' }}>
                {inboundData.rows.length}
              </span>
            </button>
          </div>

          {/* Ricerca Rapida Turno / Fermata */}
          <div style={{ position: 'relative', minWidth: '170px', flex: '1 1 170px' }}>
            <Search size={13} style={{ position: 'absolute', left: '8px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Cerca fermata o turno..."
              style={{
                width: '100%',
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                padding: '5px 8px 5px 26px',
                color: 'var(--text-main)',
                fontSize: '0.75rem',
                outline: 'none'
              }}
            />
            {searchTerm && (
              <X
                size={12}
                onClick={() => setSearchTerm('')}
                style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', cursor: 'pointer' }}
              />
            )}
          </div>
        </div>

        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          Tabella unica con <strong>{outboundData.rows.length + inboundData.rows.length}</strong> corse totali su {currentLineInfo.name}
          {searchTerm.trim() && (
            <span style={{ marginLeft: '6px', color: 'var(--accent-orange)', fontWeight: '700' }}>
              • Evidenziazione colonna attiva
            </span>
          )}
        </div>
      </div>

      {/* Barra di Navigazione Rapida Orizzontale */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(245, 166, 35, 0.08)',
        border: '1px solid rgba(245, 166, 35, 0.25)',
        borderRadius: '8px',
        padding: '5px 8px',
        marginBottom: '0.6rem',
        gap: '6px',
        flexWrap: 'wrap'
      }}>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span>↔️ <strong style={{ color: 'var(--accent-orange)' }}>Scorri Fermate:</strong></span>
          <span style={{ fontSize: '0.66rem', color: 'rgba(255,255,255,0.5)' }}>(o trascina a destra/sinistra)</span>
        </div>

        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          <button
            type="button"
            onClick={() => scrollToPosition('start')}
            title="Vai a Inizio / Partenza"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '3px 7px',
              color: 'var(--accent-orange)',
              fontSize: '0.7rem',
              fontWeight: '700',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '2px'
            }}
          >
            <ChevronsLeft size={13} />
            <span>Inizio</span>
          </button>

          <button
            type="button"
            onClick={() => scrollTable(-350)}
            title="Scorri Sinistra"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '4px 10px',
              color: 'var(--text-main)',
              fontSize: '0.72rem',
              fontWeight: '700',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '2px'
            }}
          >
            <ChevronLeft size={14} />
            <span>SX</span>
          </button>

          <button
            type="button"
            onClick={() => scrollTable(350)}
            title="Scorri Destra"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '4px 10px',
              color: 'var(--text-main)',
              fontSize: '0.72rem',
              fontWeight: '700',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '2px'
            }}
          >
            <span>DX</span>
            <ChevronRight size={14} />
          </button>

          <button
            type="button"
            onClick={() => scrollToPosition('end')}
            title="Vai a Fine / Capolinea"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '4px 9px',
              color: 'var(--accent-cyan)',
              fontSize: '0.72rem',
              fontWeight: '700',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '2px'
            }}
          >
            <span>Capolinea</span>
            <ChevronsRight size={14} />
          </button>
        </div>
      </div>

      {/* Tabella Unica Continua con Intestazione Invertita a Centro Pagina */}
      <div style={{
        borderRadius: '8px',
        border: '1.5px solid rgba(255, 255, 255, 0.18)',
        overflow: 'hidden',
        background: 'var(--bg-card)',
        maxWidth: '100%',
        boxShadow: '0 4px 20px rgba(0,0,0,0.45)'
      }}>
        <div
          ref={tableContainerRef}
          style={{
            overflowX: 'auto',
            maxHeight: 'calc(100vh - 240px)',
            overflowY: 'auto',
            maxWidth: '100%',
            WebkitOverflowScrolling: 'touch',
            touchAction: 'pan-x pan-y',
            scrollbarWidth: 'thin',
            scrollbarColor: '#f5a623 rgba(255,255,255,0.05)'
          }}
        >
          <table style={{
            width: 'max-content',
            borderCollapse: 'collapse',
            fontSize: '0.74rem',
            tableLayout: 'fixed',
            touchAction: 'pan-x pan-y'
          }}>
            {/* SEZIONE 1: ANDATA (Partenze da Capolinea 1) */}
            <thead>
              {renderHeaderRow(outboundData.headers, true)}
            </thead>
            <tbody>
              {outboundData.rows.length === 0 ? (
                <tr>
                  <td colSpan={outboundData.headers.length} style={{ padding: '1.5rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    Nessuna corsa di andata trovata.
                  </td>
                </tr>
              ) : (
                outboundData.rows.map((rowItem, rIdx) => renderRowItem(rowItem, rIdx, outboundData.headers))
              )}

              {/* DIVISORE DI SEZIONE CENTRALE */}
              <tr ref={sectionInboundRef} style={{ background: 'transparent' }}>
                <td
                  colSpan={inboundData.headers.length}
                  style={{
                    padding: '12px 14px',
                    background: 'linear-gradient(90deg, rgba(16, 185, 129, 0.35) 0%, rgba(15, 23, 42, 0.95) 100%)',
                    borderTop: '3px solid #10b981',
                    borderBottom: '2px solid #10b981',
                    color: '#34d399',
                    fontWeight: '900',
                    fontSize: '0.82rem',
                    textAlign: 'left'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '1rem' }}>🔄</span>
                      <span>{inboundData.title} ({inboundData.rows.length} corse)</span>
                      <span style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.7)', fontWeight: 'normal' }}>
                        — Sequenza fermate invertita per lettura naturale da sinistra a destra
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={() => jumpToSection('top')}
                      style={{
                        background: 'rgba(255,255,255,0.1)',
                        border: '1px solid rgba(255,255,255,0.3)',
                        borderRadius: '6px',
                        padding: '3px 8px',
                        color: '#ffffff',
                        fontSize: '0.68rem',
                        fontWeight: '700',
                        cursor: 'pointer',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}
                    >
                      <span>⬆️ Torna a inizio tabella</span>
                    </button>
                  </div>
                </td>
              </tr>

              {/* SEZIONE 2: INTESTAZIONE FERMATE INVERTITE A CENTRO TABELLA */}
              {renderHeaderRow(inboundData.headers, false)}

              {/* RIGHE SEZIONE 2 (RITORNO) */}
              {inboundData.rows.length === 0 ? (
                <tr>
                  <td colSpan={inboundData.headers.length} style={{ padding: '1.5rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    Nessuna corsa di ritorno trovata.
                  </td>
                </tr>
              ) : (
                inboundData.rows.map((rowItem, rIdx) => renderRowItem(rowItem, rIdx, inboundData.headers))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default OrarioCorse;
