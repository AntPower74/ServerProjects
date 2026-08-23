import requests
from bs4 import BeautifulSoup

url = "https://t.me/s/ArrivaTorino"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

messages = soup.find_all('div', class_='tgme_widget_message')
for msg in messages:
    text = msg.find('div', class_='tgme_widget_message_text')
    text_content = text.text if text else "No text"
    
    document = msg.find('a', class_='tgme_widget_message_document')
    if document:
        doc_link = document.get('href')
        doc_title_elem = document.find('div', class_='tgme_widget_message_document_title')
        doc_title = doc_title_elem.text if doc_title_elem else "Unknown.pdf"
        print(f"Found PDF: {doc_title}")
        print(f"Link: {doc_link}")
        print(f"Message: {text_content[:100]}...\n")
