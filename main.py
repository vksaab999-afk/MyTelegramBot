import os
import telebot
from telebot import types
from pymongo import MongoClient
from flask import Flask
from threading import Thread

# Config
BOT_TOKEN = os.environ.get('BOT_TOKEN')
MONGO_URI = os.environ.get('MONGO_URI')
ADMIN_ID = 5785924075 
CHANNEL_LINK = "https://t.me/your_channel_link" # Yahan apna link daalo

bot = telebot.TeleBot(BOT_TOKEN)
client = MongoClient(MONGO_URI)
db = client['tg_bot_database']
users_col = db['users']

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def keep_alive(): app.run(host='0.0.0.0', port=8080)

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    uname = message.from_user.username or "No_Username"
    if not users_col.find_one({'uid': uid}):
        users_col.insert_one({'uid': uid, 'username': uname})
    
    # Button logic
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Join Channel", url=CHANNEL_LINK))
    
    # Aapka original welcome message
    bot.reply_to(message, "Welcome! Aap hamare database mein register ho gaye hain.", reply_markup=markup)

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

@bot.message_handler(func=lambda message: True, content_types=['photo', 'video', 'document', 'text', 'audio'])
def handle_messages(message):
    # Admin Reply Logic
    if message.from_user.id == ADMIN_ID and message.reply_to_message:
        if message.reply_to_message.forward_from:
            target_id = message.reply_to_message.forward_from.id
            bot.copy_message(target_id, message.chat.id, message.message_id)
            bot.reply_to(message, "✅ Message user ko bhej diya gaya hai!")
            return

    # User to Admin Forwarding
    if message.from_user.id != ADMIN_ID and message.text not in ['/start', '/stats', '/list']:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        return

    # Broadcast Logic
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
