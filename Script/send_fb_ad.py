import requests

TOKEN = "8924812869:AAHOuXz5EY4Xtt_02X_lVP33J6jFQuN0ZGQ"
CHAT_ID = "@risparmiospesato"

message = """Ecco una bozza per l'annuncio sui gruppi Facebook (CUP Piemonte):

Titolo: Prenotare al CUP è un incubo? 🏥

Testo:
Ciao a tutti! 👋
So bene quanto sia stressante e difficile trovare un posto libero in tempi ragionevoli sul portale del CUP Piemonte. Spesso bisogna ricaricare la pagina 100 volte per trovare una disponibilità.

Proprio per questo motivo, ho creato un piccolo strumento che ti fa risparmiare un sacco di tempo:
✅ Basta caricare la foto della ricetta dematerializzata.
✅ Il sistema estrae in automatico i codici.
✅ E calcola le distanze con i principali ospedali (Molinette, Mauriziano, Novara, Cuneo, ecc.)!

Lo trovate qui: https://cup.calq.it 
Spero davvero che possa essere d'aiuto a chi, come me, ha perso giornate intere sul sito del CUP.

Se avete feedback o suggerimenti, scrivetemi nei commenti! 👇"""

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {
    "chat_id": CHAT_ID,
    "text": message,
    "parse_mode": "HTML"
}
response = requests.post(url, data=data)
print(response.json())
