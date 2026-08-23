from playwright.sync_api import sync_playwright
import time
import os

def run():
    print("Avvio del robot in corso...")
    
    # Crea cartella dove scaricare i file
    download_dir = os.path.join(os.getcwd(), 'nuovi_turni')
    os.makedirs(download_dir, exist_ok=True)
    
    with sync_playwright() as p:
        # Avvia Chrome VERO in modo visibile e accetta i download
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(accept_downloads=True, no_viewport=True)
        page = context.new_page()

        print("\n" + "="*50)
        print("Il browser è aperto. Fai il login manualmente nella finestra.")
        print("Naviga fino alla pagina che contiene i turni o i pulsanti di download.")
        print("Quando sei pronto, premi INVIO qui nel terminale per farmi scaricare tutti i PDF.")
        print("="*50 + "\n")
        
        page.goto('https://in.arriva.it/Torino/')
        
        input("PREMI INVIO SOLO QUANDO SEI LOGGATO E VEDI I TURNI... ")
        
        print("\nInizio ricerca e download dei turni...")
        
        # Trova tutti i link che contengono .pdf o clicca su tutto ciò che sembra un turno
        # Poiché non conosciamo la struttura esatta, cerchiamo tutti i tag <a> che sembrano download
        links = page.locator('a').all()
        
        download_count = 0
        for link in links:
            href = link.get_attribute('href')
            text = link.inner_text().strip()
            
            # Condizioni per capire se è un turno (es. .pdf, o la parola 'Scarica', ecc.)
            if href and ('.pdf' in href.lower() or 'download' in href.lower()):
                try:
                    with page.expect_download(timeout=10000) as download_info:
                        link.click()
                    download = download_info.value
                    
                    # Salva il file
                    filename = download.suggested_filename
                    if not filename:
                        filename = f"turno_{download_count}.pdf"
                        
                    download.save_as(os.path.join(download_dir, filename))
                    print(f"✅ Scaricato: {filename}")
                    download_count += 1
                except Exception as e:
                    print(f"⚠️ Errore con il link {text[:20]}: {str(e)}")
                    
        print(f"\nFinito! Ho scaricato {download_count} file nella cartella 'nuovi_turni'")
        print("Puoi chiudere il browser.")
        browser.close()

if __name__ == '__main__':
    run()
