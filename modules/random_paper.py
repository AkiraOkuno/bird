import requests
from bs4 import BeautifulSoup
import random
import os
from telegram_utils import send_telegram_message

def fetch_core():
    headers = {'User-Agent': 'Mozilla/5.0'}

    contagem = 1
    sucesso = 0
    while contagem <= 10:
        number = random.randint(1,150000000)
        if not sucesso:
            try:
                url = f"https://core.ac.uk/works/{number}"
                req = requests.get(url, headers=headers)
                soup = BeautifulSoup(req.text, "html.parser")

                title = soup.find('meta', attrs={'name': 'citation_title'})['content']
                authors = [meta['content'].replace('\u2009', ' ') for meta in soup.find_all('meta', attrs={'name': 'citation_author'})]
                abstract = soup.find('meta', attrs={'name': 'DCTERMS.abstract'})['content']
                print_authors = "\n".join(authors)
                sucesso = 1
                return f"🤓Paper de hoje:\n{title}\n\n{print_authors}\n\nAbstract:\n{abstract}\n\nLink: {url}"
            except:
                print(f"{number} não rodou... Tentando outro")
        contagem += 1
    if not sucesso:
        print("As 10 tentativas deram pau")
        return None

def generate():
    core = fetch_core()
    if core:
        return core
    else:
        return "⚠️ Não consegui encontrar o paper de hoje."
