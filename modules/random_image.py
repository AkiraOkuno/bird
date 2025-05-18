import os
from telegram_utils import send_image_message

def generate():
    image_url = "https://picsum.photos/800/600"
    caption = "🖼️ Imagem aleatória do dia — via Picsum Photos"
    chat_ids = os.environ["CHAT_IDS"].split(",")

    for chat_id in chat_ids:
        send_image_message(chat_id.strip(), image_url, caption)

    return None
