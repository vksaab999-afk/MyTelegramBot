import os
from flask import Flask
from threading import Thread

# Flask server banate hain taaki Render ko port mil jaye
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# Server ko background mein chalate hain
def keep_alive():
    t = Thread(target=run)
    t.start()

# Ye line aapke purane code ke pehle honi chahiye
keep_alive()

# Yahan se aapka asli bot ka code shuru hoga...
import telebot
from telebot import types
import json
import os

# --- DETAILS ---
BOT_TOKEN = "8772389822:AAGEoR5Uh17IYRJ29AsQoH6SSfOnC8aSbeI"
ADMIN_ID = 5785924075
CHANNEL_LINK = "https://t.me/+lFOBnj9z7yVmMGM1"
WELCOME_CAPTION = "Welcome Dear ☺️ 🎉\n\nNiche diye button pe click karke abhi hamare channel ko join kijiye ✅"
# -----------------

bot = telebot.TeleBot(BOT_TOKEN)
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE): return []
    with open(USERS_FILE, "r") as f:
        try: return json.load(f)
        except: return []

def save_users(users):
    with open(USERS_FILE, "w") as f: json.dump(users, f)

users = load_users()

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in users:
        users.append(uid)
        save_users(users)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL ✅", url=CHANNEL_LINK))
    
    # Aapki local image file jo GitHub repository mein hogi
    photo = open('poster.png', 'rb') 
    bot.send_photo(message.chat.id, photo=photo, caption=WELCOME_CAPTION, reply_markup=markup)

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
            except: msg += f"{uid} | Private\n"
        bot.reply_to(message, msg if len(msg) < 4000 else "List bahut badi hai.")

@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID, content_types=['photo', 'video', 'document', 'text', 'audio'])
def broadcast(message):
    for uid in users:
        try:
            if message.content_type == 'photo': bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption)
            elif message.content_type == 'video': bot.send_video(uid, message.video.file_id, caption=message.caption)
            elif message.content_type == 'document': bot.send_document(uid, message.document.file_id, caption=message.caption)
            else: bot.send_message(uid, message.text)
        except: pass
    bot.reply_to(message, "✅ Broadcast complete!")

bot.infinity_polling()
