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
CHANNEL_LINK = "https://t.me/rajaji2002"

bot = telebot.TeleBot(BOT_TOKEN)
client = MongoClient(MONGO_URI)
db = client['tg_bot_database']
users_col = db['users']

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def keep_alive(): app.run(host='0.0.0.0', port=8080)

# Start Command
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    uname = message.from_user.username or "No_Username"
    if not users_col.find_one({'uid': uid}):
        users_col.insert_one({'uid': uid, 'username': uname})
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ JOIN CHANNEL", url=CHANNEL_LINK))
    
    # Poster Image
    bot.send_photo(message.chat.id, "https://telegra.ph/file/8b38382d5563914945d8b.jpg", 
                   caption="🎉 *Welcome!*\n\n👇 Niche diye gaye button par click karke hamara channel join karein.", 
                   reply_markup=markup, parse_mode='Markdown')

# Admin Commands
@bot.message_handler(commands=['stats', 'list'])
def admin_cmds(message):
    if message.from_user.id == ADMIN_ID:
        if message.text == '/stats':
            count = users_col.count_documents({})
            bot.reply_to(message, f"📊 Total users: {count}")
        elif message.text == '/list':
            all_users = list(users_col.find())
            msg = "User List (Username | ID):\n" + "\n".join([f"@{u.get('username','N/A')} | {u['uid']}" for u in all_users])
            bot.reply_to(message, msg if len(msg) < 4000 else "List bahut badi hai.")

# Main Handler (Broadcast & Forwarding)
@bot.message_handler(content_types=['photo', 'video', 'document', 'audio', 'text'])
def handler(message):
    # 1. Admin Reply Logic (Reply to forward)
    if message.from_user.id == ADMIN_ID and message.reply_to_message:
        if message.reply_to_message.forward_from:
            bot.copy_message(message.reply_to_message.forward_from.id, message.chat.id, message.message_id)
            bot.reply_to(message, "✅ Sended!")
            return

    # 2. Broadcast Logic (Only if message is not a command)
    if message.from_user.id == ADMIN_ID and message.text not in ['/start', '/stats', '/list']:
        all_users = users_col.find()
        for u in all_users:
            try:
                # Markdown use kiya hai taaki *bold* kaam kare
                if message.content_type == 'photo': bot.send_photo(u['uid'], message.photo[-1].file_id, caption=message.caption, parse_mode='Markdown')
                elif message.content_type == 'video': bot.send_video(u['uid'], message.video.file_id, caption=message.caption, parse_mode='Markdown')
                elif message.content_type == 'audio': bot.send_audio(u['uid'], message.audio.file_id, caption=message.caption, parse_mode='Markdown')
                elif message.content_type == 'document': bot.send_document(u['uid'], message.document.file_id, caption=message.caption, parse_mode='Markdown')
                else: bot.send_message(u['uid'], message.text, parse_mode='Markdown')
            except: pass
        bot.reply_to(message, "✅ Broadcast Done!")
        return

    # 3. User Forwarding (If not Admin)
    if message.from_user.id != ADMIN_ID and message.text not in ['/start', '/stats', '/list']:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

if __name__ == '__main__':
    Thread(target=keep_alive).start()
    bot.infinity_polling()
