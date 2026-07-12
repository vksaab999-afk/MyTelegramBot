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

# Keep Alive
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
    bot.reply_to(message, "*Welcome!* Aap register ho gaye hain.", parse_mode='Markdown')

# Broadcast (Photo/Video/Text)
@bot.message_handler(content_types=['photo', 'video', 'document', 'text', 'audio'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID and message.text not in ['/start', '/stats', '/list']:
        all_users = list(users_col.find())
        # Caption agar hai toh wahi, nahi toh khali
        caption = message.caption or ""
        
        for user in all_users:
            try:
                if message.content_type == 'photo': 
                    bot.send_photo(user['uid'], message.photo[-1].file_id, caption=caption, parse_mode='Markdown')
                elif message.content_type == 'video': 
                    bot.send_video(user['uid'], message.video.file_id, caption=caption, parse_mode='Markdown')
                elif message.content_type == 'document': 
                    bot.send_document(user['uid'], message.document.file_id, caption=caption, parse_mode='Markdown')
                elif message.content_type == 'audio':
                    bot.send_audio(user['uid'], message.audio.file_id, caption=caption, parse_mode='Markdown')
                else: 
                    bot.send_message(user['uid'], message.text, parse_mode='Markdown')
            except: pass
        bot.reply_to(message, "✅ *Broadcast complete!*", parse_mode='Markdown')

if __name__ == '__main__':
    Thread(target=keep_alive).start()
    bot.infinity_polling()
