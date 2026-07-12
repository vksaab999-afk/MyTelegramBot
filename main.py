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

# Flask Server for Keep Alive
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def keep_alive(): app.run(host='0.0.0.0', port=8080)

# Bot Commands
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if not users_col.find_one({'uid': uid}):
        users_col.insert_one({'uid': uid})
    bot.reply_to(message, "Welcome! Aap hamare database mein register ho gaye hain.")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id == ADMIN_ID:
        count = users_col.count_documents({})
        bot.reply_to(message, f"📊 Total users: {count}")

@bot.message_handler(commands=['list'])
def list_users(message):
    if message.from_user.id == ADMIN_ID:
        all_users = list(users_col.find())
        msg = "User List (ID):\n"
        for user in all_users:
            msg += f"{user['uid']}\n"
        bot.reply_to(message, msg if len(msg) < 4000 else "List bahut badi hai.")

# Broadcast Handler with Voice, Photo, Video, and HTML support
@bot.message_handler(content_types=['photo', 'video', 'document', 'text', 'voice', 'audio'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return

    if message.text in ['/start', '/stats', '/list']:
        return

    all_users = list(users_col.find())
    
    # HTML text ya Caption extract karna
    display_text = message.html_text if message.content_type == 'text' else message.caption
    if display_text is None: display_text = ""

    for user in all_users:
        try:
            if message.content_type == 'photo':
                bot.send_photo(user['uid'], message.photo[-1].file_id, caption=display_text, parse_mode='HTML')
            elif message.content_type == 'video':
                bot.send_video(user['uid'], message.video.file_id, caption=display_text, parse_mode='HTML')
            elif message.content_type == 'document':
                bot.send_document(user['uid'], message.document.file_id, caption=display_text, parse_mode='HTML')
            elif message.content_type == 'voice':
                bot.send_voice(user['uid'], message.voice.file_id, caption=display_text, parse_mode='HTML')
            elif message.content_type == 'audio':
                bot.send_audio(user['uid'], message.audio.file_id, caption=display_text, parse_mode='HTML')
            else:
                bot.send_message(user['uid'], display_text, parse_mode='HTML')
        except:
            pass

    bot.reply_to(message, "✅ Premium Broadcast complete!")

if __name__ == '__main__':
    Thread(target=keep_alive).start()
    bot.infinity_polling()
