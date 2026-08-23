#!/usr/bin/env python3
"""
================================================================================
🔮 INDOVINO 10eLOTTO 5 MINUTI - ANALIZZATORE STATISTICO & NUMERI SPIA
================================================================================
Programma per l'analisi quantitativa della giornata del 10eLotto ogni 5 minuti:
- Rilevamento automatico del Numero Spia dominante del giorno
- Calcolo della Terzina d'Oro (3 numeri) con la massima sinergia
- Identificazione del Numero Oro più probabile
- Simulatore di vincite e bilancio economico in tempo reale
- Live Monitor con avviso di estrazione ogni 5 minuti
- Ricerca avanzata per qualsiasi numero spia personalizzato
================================================================================
"""

import urllib.request
import re
import json
import time
import sys
import os
from collections import Counter
from datetime import datetime

# URL di acquisizione estrazioni
SOURCE_URL = "https://www.10elotto5.com/"

# Codici colore ANSI per terminale
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_CYAN = "\033[96m"
C_MAGENTA = "\033[95m"
C_BLUE = "\033[94m"


def scarica_estrazioni_oggi():
    """Scarica e parsa tutte le estrazioni del 10eLotto della giornata corrente."""
    try:
        req = urllib.request.Request(
            SOURCE_URL,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,"
                    " like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"{C_RED}[!] Errore nel download delle estrazioni: {e}{C_RESET}")
        return []

    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL)
    draws = []
    for r in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL)
        if len(cells) >= 5:
            num = re.sub(r"<[^>]+>", "", cells[0]).strip()
            draw_time = re.sub(r"<[^>]+>", "", cells[1]).strip()
            nums_raw = cells[2]

            extra_match = re.search(
                r"Extra:(.*)", nums_raw, re.DOTALL | re.IGNORECASE
            )
            if extra_match:
                main_raw = nums_raw[: extra_match.start()]
                extra_raw = extra_match.group(1)
            else:
                main_raw = nums_raw
                extra_raw = ""

            main_nums = [
                int(x)
                for x in re.findall(
                    r"\b\d{1,2}\b", re.sub(r"<[^>]+>", " ", main_raw)
                )
            ]
            extra_nums = [
                int(x)
                for x in re.findall(
                    r"\b\d{1,2}\b", re.sub(r"<[^>]+>", " ", extra_raw)
                )
            ]
            oro = re.sub(r"<[^>]+>", "", cells[3]).strip()
            d_oro = re.sub(r"<[^>]+>", "", cells[4]).strip()

            if num.isdigit() and len(main_nums) == 20:
                draws.append({
                    "concorso": int(num),
                    "ora": draw_time,
                    "numeri": main_nums,
                    "extra": extra_nums,
                    "oro": int(oro) if oro.isdigit() else None,
                    "doppio_oro": int(d_oro) if d_oro.isdigit() else None,
                })

    draws.sort(key=lambda x: x["concorso"])
    return draws


def analizza_spia(draws, spy_num, min_concorso=1, max_concorso=None):
    """Calcola le statistiche e la risposta al colpo +1 di un determinato numero spia."""
    if max_concorso is None:
        max_concorso = draws[-1]["concorso"] if draws else 288

    sub_draws = [
        d
        for d in draws
        if min_concorso <= d["concorso"] <= max_concorso
    ]
    if not sub_draws:
        return None

    indices = [
        i
        for i in range(len(sub_draws) - 1)
        if spy_num in sub_draws[i]["numeri"]
    ]
    freq = len(indices)
    if freq == 0:
        return None

    post_nums = []
    post_oros = []
    for i in indices:
        post_nums.extend(sub_draws[i + 1]["numeri"])
        if sub_draws[i + 1]["oro"] is not None:
            post_oros.append(sub_draws[i + 1]["oro"])

    counter_post = Counter(post_nums)
    counter_oro = Counter(post_oros)

    top3 = [n for n, c in counter_post.most_common(3)]
    top3_set = set(top3)

    ambi_post = 0
    terni_post = 0
    oro_hit_post = 0

    for i in indices:
        d_next = sub_draws[i + 1]
        hits = len(top3_set.intersection(set(d_next["numeri"])))
        if hits >= 2:
            ambi_post += 1
        if hits == 3:
            terni_post += 1
        if d_next["oro"] in top3_set:
            oro_hit_post += 1

    score = (
        (ambi_post * 3.0)
        + (terni_post * 15.0)
        + (oro_hit_post * 2.0)
        + (freq * 0.5)
    )

    top_oro = counter_oro.most_common(1)[0][0] if counter_oro else (top3[0] if top3 else None)

    return {
        "spy": spy_num,
        "freq": freq,
        "total_obs": len(sub_draws),
        "pct_presence": (freq / len(sub_draws)) * 100,
        "top3": top3,
        "top3_counts": [counter_post[n] for n in top3],
        "top_oro": top_oro,
        "ambi_post": ambi_post,
        "terni_post": terni_post,
        "oro_hit_post": oro_hit_post,
        "score": score,
        "ranking_post": counter_post.most_common(10),
    }


def trova_migliori_spie(draws, min_presence_pct=15.0):
    """Esamina tutti i 90 numeri e stila la classifica delle migliori spie della giornata."""
    risultati = []
    tot = len(draws)
    if tot < 10:
        return []

    for spy in range(1, 91):
        res = analizza_spia(draws, spy)
        if res and res["pct_presence"] >= min_presence_pct:
            risultati.append(res)

    risultati.sort(key=lambda x: x["score"], reverse=True)
    return risultati


def simula_giocata(draws, terzina, con_oro=True, puntata_base=1.0):
    """Simula il rendimento economico della terzina su tutte le estrazioni caricate."""
    terzina_set = set(terzina)
    costo_per_estrazione = (puntata_base * 2.0) if con_oro else puntata_base

    saldo = 0.0
    tot_spesa = 0.0
    tot_incasso = 0.0
    ambi = 0
    ambi_oro = 0
    terni = 0
    terni_oro = 0
    dettagli = []

    for d in draws:
        tot_spesa += costo_per_estrazione
        hits = len(terzina_set.intersection(set(d["numeri"])))
        has_oro = (d["oro"] in terzina_set)

        win = 0.0
        if hits == 2:
            ambi += 1
            if con_oro and has_oro:
                ambi_oro += 1
                win = 25.0 * puntata_base
            else:
                win = 2.0 * puntata_base
        elif hits == 3:
            terni += 1
            if con_oro and has_oro:
                terni_oro += 1
                win = 130.0 * puntata_base
            else:
                win = 45.0 * puntata_base

        tot_incasso += win
        saldo = tot_incasso - tot_spesa

        if win > 0:
            dettagli.append({
                "concorso": d["concorso"],
                "ora": d["ora"],
                "punti": hits,
                "oro": has_oro,
                "vinto": win,
                "saldo_progressivo": saldo,
            })

    return {
        "concorsi_giocati": len(draws),
        "spesa": tot_spesa,
        "incasso": tot_incasso,
        "saldo": saldo,
        "ambi": ambi,
        "ambi_oro": ambi_oro,
        "terni": terni,
        "terni_oro": terni_oro,
        "dettagli_vincite": dettagli,
    }


def stampa_banner():
    os.system("clear" if os.name == "posix" else "cls")
    print(f"{C_YELLOW}{C_BOLD}" + "=" * 70)
    print("  🔮 INDOVINO 10eLOTTO 5 MINUTI - ANALISI STATISTICA GIORNALIERA 🔮  ")
    print("=" * 70 + f"{C_RESET}")


def menu_pronostico_giornata(draws):
    stampa_banner()
    print(f"\n{C_CYAN}📊 ANALISI IN TEMPO REALE DI OGGI{C_RESET}")
    print(f"Estrazioni acquisite: {C_BOLD}{len(draws)}{C_RESET} su 288 (dalle {draws[0]['ora']} alle {draws[-1]['ora']})")

    if len(draws) < 20:
        print(f"\n{C_YELLOW}[!] Attenzione: Meno di 20 estrazioni disponibili. La statistica potrebbe essere instabile.{C_RESET}")

    spie = trova_migliori_spie(draws)
    if not spie:
        print(f"{C_RED}[!] Dati insufficienti per calcolare la spia.{C_RESET}")
        input("\nPremi INVIO per tornare al menu...")
        return

    migliore = spie[0]
    print("\n" + f"{C_GREEN}{C_BOLD}🏆 MIGLIOR NUMERO SPIA DELLA GIORNATA: {migliore['spy']:02d}{C_RESET}")
    print(f"├─ Presenze oggi: {migliore['freq']}/{migliore['total_obs']} concorsi ({migliore['pct_presence']:.1f}%)")
    print(f"├─ Ambi post-spia generati: {migliore['ambi_post']}")
    print(f"├─ Terni post-spia generati: {migliore['terni_post']}")
    print(f"└─ Power Score: {migliore['score']:.1f}")

    print("\n" + "=" * 70)
    print(f"{C_YELLOW}{C_BOLD}🎯 IL PRONOSTICO UFFICIALE DELL'INDOVINO:{C_RESET}")
    t = migliore["top3"]
    print(f"👉 TERZINA CONSIGLIATA: {C_BOLD}{C_GREEN} {t[0]:02d} - {t[1]:02d} - {t[2]:02d} {C_RESET}")
    print(f"👉 NUMERO ORO:          {C_BOLD}{C_YELLOW} {migliore['top_oro']:02d} {C_RESET}")
    print(f"👉 STRATEGIA D'INGRESSO: Giocare a colpo (+1) SUBITO dopo l'uscita del numero {C_BOLD}{migliore['spy']:02d}{C_RESET}")
    print(f"👉 REGOLA TAKE PROFIT:  Fermarsi al primo Terno o a +30€/+50€ di utile netto.")
    print("=" * 70)

    # Top 5 Spie alternative
    print(f"\n{C_CYAN}📋 TOP 5 SPIE ALTERNATIVE DI OGGI:{C_RESET}")
    print(f"{'Pos.':<5} | {'Spia':<6} | {'Presenze':<10} | {'Terzina Chiamata':<18} | {'Ambi/Terni':<12} | {'Score':<6}")
    print("-" * 68)
    for idx, s in enumerate(spie[:5], 1):
        terz_str = f"{s['top3'][0]:02d}-{s['top3'][1]:02d}-{s['top3'][2]:02d}"
        hits_str = f"{s['ambi_post']}A / {s['terni_post']}T"
        print(f"{idx:<5} | {s['spy']:02d}     | {s['freq']:02d} ({s['pct_presence']:.0f}%)  | {terz_str:<18} | {hits_str:<12} | {s['score']:<6.1f}")

    input(f"\n{C_CYAN}Premi INVIO per tornare al menu...{C_RESET}")


def menu_simula_terzina(draws):
    stampa_banner()
    print(f"\n{C_CYAN}💰 SIMULATORE DI VINCITA IN TEMPO REALE{C_RESET}")
    spie = trova_migliori_spie(draws)
    default_terzina = spie[0]["top3"] if spie else [59, 74, 84]

    print(f"Terzina predefinita (Miglior Spia): {default_terzina}")
    inp = input(f"Inserisci 3 numeri separati da spazio (premi INVIO per usare {default_terzina}): ").strip()

    if inp:
        try:
            terzina = [int(x) for x in inp.split() if 1 <= int(x) <= 90]
            if len(terzina) != 3:
                print(f"{C_RED}[!] Devi inserire esattamente 3 numeri validi.{C_RESET}")
                time.sleep(2)
                return
        except Exception:
            print(f"{C_RED}[!] Input non valido.{C_RESET}")
            time.sleep(2)
            return
    else:
        terzina = default_terzina

    # Esegui simulazione
    res_base = simula_giocata(draws, terzina, con_oro=False)
    res_oro = simula_giocata(draws, terzina, con_oro=True)

    print("\n" + "=" * 70)
    print(f"📊 RISULTATI SIMULAZIONE PER LA TERZINA: {terzina}")
    print(f"Concorsi simulati oggi: {res_base['concorsi_giocati']}")
    print("-" * 70)
    print(f"🏆 Punteggi centrati:")
    print(f"  ├─ Ambi (2 su 3):  {res_oro['ambi']} volte (di cui {res_oro['ambi_oro']} con Numero Oro)")
    print(f"  └─ Terni (3 su 3): {res_oro['terni']} volte (di cui {res_oro['terni_oro']} con Numero Oro)")
    print("-" * 70)
    print(f"💵 BILANCIO BASE (1,00 € a estrazione):")
    print(f"  Spesa: {res_base['spesa']:.2f} € | Incasso: {res_base['incasso']:.2f} € | Netto: {res_base['saldo']:+.2f} €")
    print("-" * 70)
    print(f"🥇 BILANCIO CON NUMERO ORO (2,00 € a estrazione):")
    col = C_GREEN if res_oro["saldo"] > 0 else C_RED
    print(f"  Spesa: {res_oro['spesa']:.2f} € | Incasso: {res_oro['incasso']:.2f} € | Netto: {col}{res_oro['saldo']:+.2f} €{C_RESET}")
    print("=" * 70)

    if res_oro["dettagli_vincite"]:
        print(f"\n{C_CYAN}📜 Dettaglio ultime vincite:{C_RESET}")
        for v in res_oro["dettagli_vincite"][-8:]:
            oro_tag = f"{C_YELLOW}[ORO]{C_RESET}" if v["oro"] else ""
            print(f"  Concorso #{v['concorso']:03d} ({v['ora']}) ➔ {v['punti']} punti {oro_tag} -> Vinto {v['vinto']:.2f} € (Saldo prog: {v['saldo_progressivo']:+.2f} €)")

    input(f"\n{C_CYAN}Premi INVIO per tornare al menu...{C_RESET}")


def menu_ricerca_spia_personalizzata(draws):
    stampa_banner()
    print(f"\n{C_CYAN}🔎 ANALISI DI UN NUMERO SPIA PERSONALIZZATO{C_RESET}")
    inp = input("Inserisci il numero spia da analizzare (1-90): ").strip()
    if not inp.isdigit() or not (1 <= int(inp) <= 90):
        print(f"{C_RED}[!] Numero non valido.{C_RESET}")
        time.sleep(2)
        return

    spy = int(inp)
    res = analizza_spia(draws, spy)
    if not res:
        print(f"{C_RED}[!] Il numero {spy} non è mai stato estratto oggi.{C_RESET}")
        input("\nPremi INVIO per tornare al menu...")
        return

    print("\n" + "=" * 70)
    print(f"📊 REPORT PER IL NUMERO SPIA: {C_BOLD}{spy:02d}{C_RESET}")
    print(f"├─ Estratto oggi: {res['freq']} volte su {res['total_obs']} concorsi ({res['pct_presence']:.1f}%)")
    print(f"├─ Terzina più attirata (+1): {C_GREEN}{res['top3']}{C_RESET}")
    print(f"├─ Numero Oro più frequente post-spia: {C_YELLOW}{res['top_oro']}{C_RESET}")
    print(f"├─ Ambi generati subito dopo: {res['ambi_post']}")
    print(f"└─ Terni generati subito dopo: {res['terni_post']}")
    print("-" * 70)
    print("Top 10 numeri chiamati dopo l'uscita del " + str(spy) + ":")
    for n, c in res["ranking_post"]:
        pct = (c / res["freq"]) * 100
        bar = "█" * int(pct / 5)
        print(f"  Numero {n:02d}: uscito {c:2d}/{res['freq']} volte ({pct:5.1f}%) {C_BLUE}{bar}{C_RESET}")
    print("=" * 70)

    input(f"\n{C_CYAN}Premi INVIO per tornare al menu...{C_RESET}")


def menu_live_monitor():
    stampa_banner()
    print(f"\n{C_GREEN}📡 MODALITÀ LIVE MONITOR (AGGIORNAMENTO AUTOMATICO){C_RESET}")
    print("Il programma controllerà ogni 30 secondi le nuove estrazioni.")
    print("Premi Ctrl+C in qualsiasi momento per uscire e tornare al menu.\n")

    last_concorso = None
    try:
        while True:
            draws = scarica_estrazioni_oggi()
            if draws:
                latest = draws[-1]
                if last_concorso != latest["concorso"]:
                    last_concorso = latest["concorso"]
                    spie = trova_migliori_spie(draws)
                    top_spy = spie[0] if spie else None

                    now_str = datetime.now().strftime("%H:%M:%S")
                    print(f"\n{C_YELLOW}[{now_str}] 📢 NUOVA ESTRAZIONE CONCORSO #{latest['concorso']} ({latest['ora']}){C_RESET}")
                    nums_fmt = " ".join(f"{n:02d}" for n in latest["numeri"])
                    print(f"  Estratti:  {nums_fmt}")
                    print(f"  🥇 Oro:    {latest['oro']} | 🥈 Doppio Oro: {latest['doppio_oro']}")

                    if top_spy:
                        if top_spy["spy"] in latest["numeri"]:
                            print(f"\n  {C_RED}{C_BOLD}🚨 ATTENZIONE! È USCITA LA SPIA REGINA ({top_spy['spy']:02d})! 🚨{C_RESET}")
                            t = top_spy["top3"]
                            print(f"  👉 GIOCA AL PROSSIMO CONCORSO #{latest['concorso']+1}: {C_GREEN}{t[0]:02d} - {t[1]:02d} - {t[2]:02d}{C_RESET} (Oro: {top_spy['top_oro']:02d})")
                        else:
                            t = top_spy["top3"]
                            print(f"  ℹ️ Spia attiva: {top_spy['spy']:02d} (Terzina da giocare all'uscita: {t})")

            time.sleep(30)
    except KeyboardInterrupt:
        print(f"\n{C_YELLOW}Monitoraggio interrotto dall'utente.{C_RESET}")
        time.sleep(1)


def main():
    while True:
        draws = scarica_estrazioni_oggi()
        stampa_banner()
        n_estraz = len(draws) if draws else 0
        latest_ora = draws[-1]["ora"] if draws else "--:--"
        latest_conc = draws[-1]["concorso"] if draws else 0

        print(f"🗓️  Stato odierno: {C_BOLD}{n_estraz}{C_RESET}/288 estrazioni caricate | Ultimo concorso: #{latest_conc} ({latest_ora})")
        print("-" * 70)
        print("  1. 🎯 Visualizza il Pronostico dell'Indovino (Spia + Terzina + Oro)")
        print("  2. 💰 Simula Vincite e Bilancio di una Terzina su Oggi")
        print("  3. 🔎 Analizza un Numero Spia Personalizzato (1-90)")
        print("  4. 📡 Avvia Live Monitor (Allerte estrazioni e notifiche Spia)")
        print("  5. 🔄 Aggiorna i dati da internet")
        print("  0. 🚪 Esci")
        print("-" * 70)

        scelta = input(f"{C_BOLD}Seleziona un'opzione (0-5): {C_RESET}").strip()

        if scelta == "1":
            menu_pronostico_giornata(draws)
        elif scelta == "2":
            menu_simula_terzina(draws)
        elif scelta == "3":
            menu_ricerca_spia_personalizzata(draws)
        elif scelta == "4":
            menu_live_monitor()
        elif scelta == "5":
            print(f"{C_GREEN}[*] Aggiornamento dati in corso...{C_RESET}")
            time.sleep(1)
        elif scelta == "0":
            print(f"\n{C_YELLOW}Arrivederci e buona fortuna! 🔮✨{C_RESET}\n")
            sys.exit(0)
        else:
            print(f"{C_RED}[!] Scelta non valida.{C_RESET}")
            time.sleep(1)


if __name__ == "__main__":
    main()
