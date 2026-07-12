import os
import telebot
from telebot import types
from pymongo import MongoClient
from flask import Flask
from threading import Thread
import time

# Config
BOT_TOKEN = os.environ.get('BOT_TOKEN')
MONGO_URI = os.environ.get('MONGO_URI')
ADMIN_ID = 5785924075 
CHANNEL_LINK = "https://t.me/+lFOBnj9z7yVmMGM1"
WELCOME_PHOTO = "https://i.ibb.co/L5kL2k9/welcome.jpg"

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
client = MongoClient(MONGO_URI)
db = client['tg_bot_database']
users_col = db['users']

# Conflict Fix: Forcefully clear all connections before starting
try:
    bot.remove_webhook()
    time.sleep(1)
except: pass

# Keep Alive
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def keep_alive(): app.run(host='0.0.0.0', port=8080)

# START COMMAND
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if not users_col.find_one({'uid': uid}):
        users_col.insert_one({'uid': uid, 'username': message.from_user.username or "N/A"})
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ JOIN CHANNEL", url=CHANNEL_LINK))
    
    caption = "🎉 *Welcome!*\n\n👇 Niche diye gaye button par click karke hamara channel join karein."
    
    try:
        bot.send_photo(message.chat.id, WELCOME_PHOTO, caption=caption, reply_markup=markup, parse_mode='Markdown')
    except:
        bot.send_message(message.chat.id, caption, reply_markup=markup, parse_mode='Markdown')

# ADMIN COMMANDS
@bot.message_handler(commands=['stats', 'list'])
def admin_commands(message):
    if message.from_user.id != ADMIN_ID: return
    if message.text == '/stats':
        count = users_col.count_documents({})
        bot.reply_to(message, f"📊 Total Users: {count}")
    elif message.text == '/list':
        all_users = list(users_col.find())
        msg = "User List:\n" + "\n".join([f"@{u.get('username','N/A')} | {u['uid']}" for u in all_users])
        bot.reply_to(message, msg if len(msg) < 4000 else "List badi hai.")

# BROADCAST & FORWARDING
@bot.message_handler(content_types=['photo', 'video', 'document', 'text'])
def handle_all(message):
    if message.text and message.text.startswith('/'): return
    if message.from_user.id == ADMIN_ID and message.reply_to_message:
        bot.copy_message(message.reply_to_message.forward_from.id, message.chat.id, message.message_id)
        return

    if message.from_user.id == ADMIN_ID:
        for u in users_col.find():
            try:
                caption = message.caption or ""
                if message.content_type == 'photo': bot.send_photo(u['uid'], message.photo[-1].file_id, caption=caption, parse_mode='Markdown')
                elif message.content_type == 'video': bot.send_video(u['uid'], message.video.file_id, caption=caption, parse_mode='Markdown')
                elif message.content_type == 'document': bot.send_document(u['uid'], message.document.file_id, caption=caption, parse_mode='Markdown')
                else: bot.send_message(u['uid'], message.text, parse_mode='Markdown')
            except: continue
        bot.reply_to(message, "✅ Broadcast Done!")
        return

    if message.from_user.id != ADMIN_ID:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

if __name__ == '__main__':
    Thread(target=keep_alive).start()
    # Final fix for conflict
    bot.infinity_polling(none_stop=True, skip_pending=True)
