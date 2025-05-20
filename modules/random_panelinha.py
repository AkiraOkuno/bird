import requests
import re
from bs4 import BeautifulSoup
import random
import itertools
import os

from telegram_utils import send_image_message

def get_panelinha():
    
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "priority": "u=0, i",
        "referer": "https://panelinha.com.br/categoria/pratos-principais/pagina/49",
        "sec-ch-ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
    }


    dict_max_page = {"entradas":30,
                     "pratos-principais":50,
                     "verao":20,
                     "bebidas":5,
                     "cafe-da-manha":15,
                     "sopas":5,
                     "inverno":10,
                     "acompanhamentos":40,
                     "sobremesas":20,
                     "doces":25}
    
    categorias_pond = list(itertools.chain(*[[k]*v for k,v in dict_max_page.items()]))
    random_cat = random.choice(categorias_pond)
    get_max = dict_max_page.get(random_cat)
    random_page = random.randint(1,get_max)

    url = f"https://panelinha.com.br/categoria/{random_cat}/pagina/{random_page}"
    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.text, "html.parser")    
    lista_pratos = [x['href'] for x in soup.find_all('a', href=True) if "/receita/" in x['href']]
    random_prato = random.choice(lista_pratos)
    
    url_prato = "https://panelinha.com.br"+random_prato
    req_prato = requests.get(url_prato, headers=headers)
    req_prato.encoding = "utf-8"
    return req_prato.text

def generate():
  
    req_prato_text = get_panelinha()
    soup = BeautifulSoup(req_prato_text, "html.parser")
    nome = soup.find_all("h1", {'class': "tH2"})[0].text
    stats = list(itertools.chain(*[x.text.strip().split("   ") for x in soup.find_all("dl", {'class': "stats"})]))
    ingrs = list(itertools.chain(*[x.text.strip().split("   ") for x in soup.find_all("ul", {'class': "js_ga_ob"})]))
    steps = list(itertools.chain(*[x.text.strip().split("   ") for x in soup.find_all("ol", {'class': "olStd"})]))
    stats_print = "\n".join(stats)
    ingrs_print = "\n".join(["* " + x for x in ingrs])
    steps_print = "\n".join([str(n+1)+") "+x for n,x in enumerate(steps)])
    caption = f"🥩 Receita de hoje: {nome}\n\n{stats_print}\n\n🔪 Ingredientes:\n{ingrs_print}\n\n🍳 Modo de preparo:\n{steps_print}"
    
    links_imagens = soup.find_all("link", {'as': "image"})[0].get("imagesrcset")
    image_url = re.findall("[^,]+(?=640)",links_imagens)[0].strip()       

    chat_ids = os.environ["CHAT_IDS"].split(",")

    for chat_id in chat_ids:
        send_image_message(chat_id.strip(), image_url, caption)

    return None
