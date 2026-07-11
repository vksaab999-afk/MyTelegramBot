import os
import telebot
import json
from flask import Flask
from threading import Thread
from telebot import types

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get("BOT_TOKEN") 
ADMIN_ID = 5785924075
CHANNEL_LINK = "https://t.me/+lFOBnj9z7yVmMGM1"
WELCOME_CAPTION = "Welcome Dear ☺️ 🎉\n\nNiche diye button pe click karke abhi hamare channel ko join kijiye ✅"
USERS_FILE = "users.json"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- USER DATA ---
def load_users():
    if not os.path.exists(USERS_FILE): return []
    try:
        with open(USERS_FILE, "r") as f: return json.load(f)
    except: return []

def save_users(users):
    with open(USERS_FILE, "w") as f: json.dump(users, f)

users = load_users()

# --- BOT COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in users:
        users.append(uid)
        save_users(users)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL ✅", url=CHANNEL_LINK))
    
    try:
        with open('poster.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo=photo, caption=WELCOME_CAPTION, reply_markup=markup)
    except:
        bot.send_message(message.chat.id, WELCOME_CAPTION, reply_markup=markup)

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, f"📊 Total users: {len(users)}")

@bot.message_handler(commands=['list'])
def list_users(message):
    if message.from_user.id == ADMIN_ID:
        msg = "User List (ID | Username):\n"
        for uid in users:
            try:
                chat = bot.get_chat(uid)
                username = f"@{chat.username}" if chat.username else "No Username"
                msg += f"{uid} | {username}\n"
            except:
                msg += f"{uid} | Private\n"
        bot.reply_to(message, msg if len(msg) < 4000 else "List bahut badi hai.")

@bot.message_handler(content_types=['photo', 'video', 'document', 'text'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID and message.text not in ['/start', '/stats', '/list']:
        for uid in users:
            try:
                if message.content_type == 'photo': bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption)
                elif message.content_type == 'video': bot.send_video(uid, message.video.file_id, caption=message.caption)
                elif message.content_type == 'document': bot.send_document(uid, message.document.file_id, caption=message.caption)
                else: bot.send_message(uid, message.text)
            except: pass
        bot.reply_to(message, "✅ Broadcast complete!")

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling(none_stop=True)
