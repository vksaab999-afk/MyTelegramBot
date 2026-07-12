import os
import telebot
from pymongo import MongoClient
from flask import Flask
from threading import Thread

# Config
BOT_TOKEN = os.environ.get('BOT_TOKEN')
MONGO_URI = os.environ.get('MONGO_URI')
ADMIN_ID = 5785924075 

bot = telebot.TeleBot(BOT_TOKEN)
client = MongoClient(MONGO_URI)
db = client['tg_bot_database']
users_col = db['users']

# Flask Server
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def keep_alive(): app.run(host='0.0.0.0', port=8080)

# Start Command (Yahan apna message aur link daal do)
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    uname = message.from_user.username or "No_Username"
    if not users_col.find_one({'uid': uid}):
        users_col.insert_one({'uid': uid, 'username': uname})
    # Apna Welcome Message aur Link yahan edit kar lo
    bot.reply_to(message, "Welcome! Aap hamare database mein register ho gaye hain.\n\n[Channel Link Yahan Daalo]")

# Admin Commands
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id == ADMIN_ID:
        count = users_col.count_documents({})
        bot.reply_to(message, f"📊 Total users: {count}")

@bot.message_handler(commands=['list'])
def list_users(message):
    if message.from_user.id == ADMIN_ID:
        all_users = list(users_col.find())
        msg = "User List (Username | ID):\n"
        for user in all_users:
            msg += f"@{user.get('username', 'N/A')} | {user['uid']}\n"
        bot.reply_to(message, msg if len(msg) < 4000 else "List bahut badi hai.")

# Broadcast, Forwarding & Reply Logic
@bot.message_handler(func=lambda message: True, content_types=['photo', 'video', 'document', 'text', 'audio'])
def handle_messages(message):
    # 1. Admin Reply Logic
    if message.from_user.id == ADMIN_ID and message.reply_to_message:
        if message.reply_to_message.forward_from:
            target_id = message.reply_to_message.forward_from.id
            bot.copy_message(target_id, message.chat.id, message.message_id)
            bot.reply_to(message, "✅ Message user ko bhej diya gaya hai!")
            return

    # 2. User to Admin Forwarding
    if message.from_user.id != ADMIN_ID and message.text not in ['/start', '/stats', '/list']:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        return

    # 3. Broadcast Logic
    if message.from_user.id == ADMIN_ID and message.text not in ['/start', '/stats', '/list']:
        all_users = list(users_col.find())
        caption = message.caption or ""
        for user in all_users:
            try:
                if message.content_type == 'photo': bot.send_photo(user['uid'], message.photo[-1].file_id, caption=caption, parse_mode='Markdown')
                elif message.content_type == 'video': bot.send_video(user['uid'], message.video.file_id, caption=caption, parse_mode='Markdown')
                elif message.content_type == 'audio': bot.send_audio(user['uid'], message.audio.file_id, caption=caption, parse_mode='Markdown')
                elif message.content_type == 'document': bot.send_document(user['uid'], message.document.file_id, caption=caption, parse_mode='Markdown')
                else: bot.send_message(user['uid'], message.text, parse_mode='Markdown')
            except: pass
        bot.reply_to(message, "✅ Broadcast complete!")

if __name__ == '__main__':
    Thread(target=keep_alive).start()
    bot.infinity_polling()
