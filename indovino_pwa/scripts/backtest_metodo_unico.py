#!/usr/bin/env python3
import json
import os
from collections import Counter

ARCHIVE_FILE = '/home/antonio/indovino_pwa/archive/full_archive.json'

def run_backtest():
    with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
        draws = json.load(f)
        
    print(f"==================================================")
    print(f"🧪 BACKTEST SCIENTIFICO: METODO UNICO (3 COLPI)")
    print(f"📊 Totale Estrazioni in Analisi: {len(draws)}")
    print(f"==================================================\n")
    
    # Raggruppa per giorno
    days = {}
    for d in draws:
        days.setdefault(d['data'], []).append(d)
        
    total_signals = 0
    win_colpo_1 = 0
    win_colpo_2 = 0
    win_colpo_3 = 0
    losses = 0
    
    tot_spesa = 0.0
    tot_incasso = 0.0
    
    ambo_base = 0
    ambo_oro = 0
    terni_base = 0
    terni_oro = 0
    
    log_trades = []
    
    for date_str, day_draws in sorted(days.items()):
        print(f"📅 Analisi Giorno: {date_str} ({len(day_draws)} estrazioni)")
        
        # Simulazione rolling: per ogni concorso dopo i primi 30 di calibrazione
        # Cerchiamo la Super-Spia calcolata sui 30-50 concorsi precedenti
        active_trade = None
        
        for i in range(30, len(day_draws) - 3):
            curr_draw = day_draws[i]
            
            # Se c'è un trade attivo, non apriamo nuovi trade finché non chiude
            if active_trade is not None:
                continue
                
            # Calibra le spie sulle estrazioni precedenti del giorno
            window = day_draws[max(0, i-50):i]
            if len(window) < 20:
                continue
                
            # Trova la migliore spia
            spies = []
            for s in range(1, 91):
                indices = [k for k in range(len(window)-1) if s in window[k]['numeri']]
                freq = len(indices)
                if freq < 4:
                    continue
                post_nums = []
                post_oros = []
                for k in indices:
                    post_nums.extend(window[k+1]['numeri'])
                    if window[k+1]['oro'] is not None:
                        post_oros.append(window[k+1]['oro'])
                c_post = Counter(post_nums)
                c_oro = Counter(post_oros)
                top3 = [n for n, c in c_post.most_common(3)]
                top3_set = set(top3)
                ambi_post = 0
                terni_post = 0
                oro_hit = 0
                for k in indices:
                    d_nxt = window[k+1]
                    hits = len(top3_set.intersection(set(d_nxt['numeri'])))
                    if hits >= 2: ambi_post += 1
                    if hits == 3: terni_post += 1
                    if d_nxt['oro'] in top3_set: oro_hit += 1
                score = (ambi_post * 3.0) + (terni_post * 15.0) + (oro_hit * 2.0) + (freq * 0.5)
                top_oro = c_oro.most_common(1)[0][0] if c_oro else top3[0]
                spies.append({'spy': s, 'score': score, 'top3': top3, 'top_oro': top_oro, 'freq': freq})
                
            spies.sort(key=lambda x: x['score'], reverse=True)
            if not spies or spies[0]['score'] < 30.0:
                continue
                
            best_spy = spies[0]
            
            # Controlla se la Spia è uscita nell'estrazione corrente
            if best_spy['spy'] in curr_draw['numeri']:
                # TRIGGER! Giochiamo per max 3 colpi successivi
                total_signals += 1
                terzina_set = set(best_spy['top3'])
                oro_target = best_spy['top_oro']
                
                trade_won = False
                spesa_trade = 0.0
                incasso_trade = 0.0
                esito_str = ""
                colpo_vinto = None
                
                for step in range(1, 4):
                    nxt_idx = i + step
                    if nxt_idx >= len(day_draws):
                        break
                    nxt_draw = day_draws[nxt_idx]
                    spesa_trade += 2.0  # 1€ base + 1€ oro
                    
                    hits = len(terzina_set.intersection(set(nxt_draw['numeri'])))
                    has_oro = (nxt_draw['oro'] in terzina_set)
                    
                    if hits == 3:
                        trade_won = True
                        colpo_vinto = step
                        if has_oro:
                            incasso_trade = 130.0
                            terni_oro += 1
                            esito_str = f"💥 TERNO CON ORO ({130.0}€)"
                        else:
                            incasso_trade = 45.0
                            terni_base += 1
                            esito_str = f"🥇 TERNO BASE ({45.0}€)"
                        break
                    elif hits == 2:
                        trade_won = True
                        colpo_vinto = step
                        if has_oro:
                            incasso_trade = 25.0
                            ambo_oro += 1
                            esito_str = f"🥈 AMBO CON ORO ({25.0}€)"
                        else:
                            incasso_trade = 2.0
                            ambo_base += 1
                            esito_str = f"🥉 AMBO BASE ({2.0}€)"
                        break
                        
                if trade_won:
                    if colpo_vinto == 1: win_colpo_1 += 1
                    elif colpo_vinto == 2: win_colpo_2 += 1
                    elif colpo_vinto == 3: win_colpo_3 += 1
                else:
                    losses += 1
                    esito_str = "🛑 STOP LOSS (0 pt)"
                    
                netto = incasso_trade - spesa_trade
                tot_spesa += spesa_trade
                tot_incasso += incasso_trade
                
                log_trades.append({
                    'data': date_str,
                    'concorso': curr_draw['concorso'],
                    'ora': curr_draw['ora'],
                    'spia': best_spy['spy'],
                    'terzina': best_spy['top3'],
                    'oro': oro_target,
                    'esito': esito_str,
                    'colpo': colpo_vinto if trade_won else 'Perso',
                    'spesa': spesa_trade,
                    'incasso': incasso_trade,
                    'netto': netto
                })
                
    wins_total = win_colpo_1 + win_colpo_2 + win_colpo_3
    win_rate = (wins_total / max(1, total_signals)) * 100
    
    print("\n" + "="*50)
    print("📈 RISULTATI TOTALI BACKTEST METODO UNICO (3 COLPI)")
    print("="*50)
    print(f"🎯 Totale Segnali Giocati: {total_signals}")
    print(f"🟢 Segnali Vincenti entro 3 colpi: {wins_total} ({win_rate:.1f}%)")
    print(f"   ├─ 🥇 Vinti al 1° Colpo: {win_colpo_1} ({win_colpo_1/max(1,total_signals)*100:.1f}%)")
    print(f"   ├─ 🥈 Vinti al 2° Colpo: {win_colpo_2} ({win_colpo_2/max(1,total_signals)*100:.1f}%)")
    print(f"   └─ 🥉 Vinti al 3° Colpo: {win_colpo_3} ({win_colpo_3/max(1,total_signals)*100:.1f}%)")
    print(f"🔴 Segnali Chiusi in Stop Loss (3 colpi a vuoto): {losses} ({losses/max(1,total_signals)*100:.1f}%)")
    print(f"\n🏆 Dettaglio Tipologie di Vincita:")
    print(f"   ├─ 💥 Terni con Numero Oro (130€): {terni_oro}")
    print(f"   ├─ 🥇 Terni Base (45€): {terni_base}")
    print(f"   ├─ 🥈 Ambi con Numero Oro (25€): {ambo_oro}")
    print(f"   └─ 🥉 Ambi Base (2€): {ambo_base}")
    print(f"\n💰 BILANCIO ECONOMICO COMPLESSIVO:")
    print(f"   ├─ Spesa Totale: {tot_spesa:.2f} €")
    print(f"   ├─ Incasso Totale: {tot_incasso:.2f} €")
    saldo_totale = tot_incasso - tot_spesa
    sign = "+" if saldo_totale >= 0 else ""
    print(f"   └─ 🟢 SALDO NETTO FINALE: {sign}{saldo_totale:.2f} €")
    print("="*50)

if __name__ == '__main__':
    run_backtest()
