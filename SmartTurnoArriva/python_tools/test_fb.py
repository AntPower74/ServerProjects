import asyncio
from bot import invia_post_facebook

async def main():
    messaggio = "👋 Ciao! Questo è un messaggio di prova automatico per confermare che il collegamento tra il bot e la Pagina Facebook funziona perfettamente. 🤖"
    # Passiamo None come immagine per fare solo un post di testo
    await invia_post_facebook(messaggio, None)
    print("Messaggio di prova inviato con successo!")

if __name__ == "__main__":
    asyncio.run(main())
