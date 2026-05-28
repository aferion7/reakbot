import os
import random
from fastapi import FastAPI, Request
from telebot import TeleBot
from telebot.types import Update
from dotenv import load_dotenv
app = FastAPI()
# .env faylini yuklash (Lokal ishlash uchun)
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
# Emojilarni vergul bilan ajratilgan matndan ro'yxatga aylantiramiz
EMOJI_LIST = [e.strip() for e in os.getenv("EMOJI_LIST", "👍,❤️,🔥,👏").split(",") if e.strip()]

bot = TeleBot(TOKEN)
app = FastAPI()

# Render to'xtab qolmasligi uchun "Health Check" (Sog'lomlik testi) havolasi
@app.get("/")
def read_root():
    return {"status": "alive", "info": f"@{BOT_USERNAME} is running successfully!"}

# Telegram xabarlarini qabul qiluvchi Webhook manzili
@app.post(f"/{TOKEN}")
async def process_webhook(request: Request):
    json_string = await request.json()
    update = Update.de_json(json_string)
    bot.process_new_updates([update])
    return {"status": "ok"}

# Kanaldagi yangi postlarga reaksiya bildirish
@app.channel_post_handler(func=lambda message: True)
def handle_channel_post(message):
    try:
        chosen_emoji = random.choice(EMOJI_LIST)
        # Telegram API orqali postga reaksiya qoldirish
        bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[{"type": "emoji", "emoji": chosen_emoji}],
            is_big=False
        )
    except Exception as e:
        print(f"Xatolik (Kanal): {e}")

# Guruhdagi yangi xabarlarga reaksiya bildirish
@app.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document'])
def handle_group_message(message):
    # Faqat guruhlarda ishlashi uchun shart (shaxsiy chatlarni tashlab ketadi)
    if message.chat.type in ["group", "supergroup"]:
        try:
            chosen_emoji = random.choice(EMOJI_LIST)
            bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[{"type": "emoji", "emoji": chosen_emoji}],
                is_big=False
            )
        except Exception as e:
            print(f"Xatolik (Guruh): {e}")
