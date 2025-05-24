import requests
from bs4 import BeautifulSoup
import random
import os
import re
import time
from telegram_utils import send_image_message, send_telegram_message, send_telegram_audio
from wiki_utils import get_image_from_wikidata
from utils.retry import try_with_retries

def save_mp3_xeno(codigo):
    url = f"https://xeno-canto.org/{codigo}/download"
    req = requests.get(url)
    with open(f"../xeno/{codigo}.mp3", 'wb') as f:
        f.write(req.content)

def get_xeno():
    headers = {'User-Agent': 'Mozilla/5.0',
               'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}


    req = requests.get("https://xeno-canto.org/explore/random", headers=headers)
    recordings = list(set(re.findall("(?<=XC)[0-9]+",req.text)))
    random_record = random.choice(recordings)
    print(random_record)
    save_mp3_xeno(random_record)

    url = f"https://xeno-canto.org/{random_record}"
    req = requests.get(url, headers=headers)
    
    link_especie = re.findall("https\:\/\/xeno-canto\.org\/species\/[A-Za-z0-9-]+",req.text)[0]
    req2 = requests.get(link_especie, headers=headers)
    return req.text, req2.text, random_record

def generate():
    req_text, req2_text, random_record = try_with_retries(get_xeno, attempts=5, delay=3)
    if req_text is None:
        return "⚠️ Não foi possível achar um pássaro hoje."

    soup = BeautifulSoup(req_text, "html.parser")
    features = [x.text for x in soup.find("table", {'class': "key-value"}).find_all('tr')]

    gravador = re.sub("^Gravador","Gravador: ",features[0]).replace("\n","").strip()
    data = re.sub("^Data","Data: ",features[1]).replace("\n","").strip()
    hora = re.sub("^Hora","Hora: ",features[2]).replace("\n","").strip()
    lat = re.sub("^Latitude","Latitude: ",features[3]).replace("\n","").strip()
    long = re.sub("^Longitude","Longitude: ",features[4]).replace("\n","").strip()
    local = re.sub("^Localidade","Localidade: ",features[5]).replace("\n","").strip()
    pais = re.sub("^País","País: ",features[6]).replace("\n","").strip()
    altitude = re.sub("^Altitude","Altitude: ",features[7]).replace("\n","").strip()

    rating = "Qualidade da gravação: " + soup.find_all("li", {'class': "selected"})[0].text
    print_features = [gravador,data,hora,lat,long,local,pais,altitude,rating]
    print_features = "\n".join(["- " + x for x in print_features])
    
    soup2 = BeautifulSoup(req2_text, "html.parser")
    name = soup2.find('title').text.split(':')[0].strip()
    nome_origem = soup2.find_all("span", {'class': "authority"})[0].text.strip()
    
    wikidata_id = 0
    try:
        wikidata_id = [x.get('href').split('/')[-1] for x in soup2.find_all("a") if 'wikidata' in x.get('href')]
        if wikidata_id:
            wikidata_id = wikidata_id[0].strip()
            image_url = get_image_from_wikidata(wikidata_id)
            print(image_url)
    except Exception as e:
        print(f"[XENO] Error extracting image: {e}")
        image_url = None

    full_text = (
        f"🦜 Pássaro do dia: *{name}*, descrita por {nome_origem}.\n\n"
        "Para ouvir seu belo canto, só ouvir o áudio abaixo!\n\n"
        "Características da gravação:\n"
        f"{print_features}"
    )

    chat_ids = os.environ["CHAT_IDS"].split(",")

    if image_url:
        for chat_id in chat_ids:
            chat_id = chat_id.strip()
            send_image_message(chat_id, image_url, full_text)
    else:
        send_telegram_message(full_text)
    
    time.sleep(1.5)  # ✅ Ensure image arrives first
    link_audio = str(random_record)+".mp3"
    send_telegram_audio(link_audio, "xeno")

    return None
