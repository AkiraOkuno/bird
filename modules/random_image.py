import random
import os
from telegram_utils import send_image_message

def generate():
    
    # Pick random width and height between 500 and 1000
    width = random.randint(500, 1000)
    height = random.randint(500, 1000)

    # Generate the image URL with cache-busting
    image_url = f"https://picsum.photos/{width}/{height}?random"
    caption = f"🖼️ Imagem aleatória do dia ({width}x{height})"
    chat_ids = os.environ["CHAT_IDS"].split(",")

    for chat_id in chat_ids:
        send_image_message(chat_id.strip(), image_url, caption)

    return None
