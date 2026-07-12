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
    # HTML formatting (<b>bold</b>)
    bot.reply_to(message, "<b>Welcome!</b> Aap hamare database mein register ho gaye hain.", parse_mode='HTML')

# Stats & List
@bot.message_handler(commands=['stats', 'list'])
def admin_commands(message):
    if message.from_user.id == ADMIN_ID:
        if message.text == '/stats':
            count = users_col.count_documents({})
            bot.reply_to(message, f"📊 <b>Total users:</b> {count}", parse_mode='HTML')
        elif message.text == '/list':
            all_users = list(users_col.find())
            msg = "<b>User List (Username | ID):</b>\n\n"
            for user in all_users:
                msg += f"@{user.get('username', 'N/A')} | {user['uid']}\n"
            bot.reply_to(message, msg if len(msg) < 4000 else "List bahut badi hai.", parse_mode='HTML')

# Final Broadcast (HTML Mode)
@bot.message_handler(content_types=['photo', 'video', 'document', 'text', 'audio'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID and message.text not in ['/start', '/stats', '/list']:
        all_users = list(users_col.find())
        caption = message.caption or ""
        
        for user in all_users:
            try:
                if message.content_type == 'photo': 
                    bot.send_photo(user['uid'], message.photo[-1].file_id, caption=caption, parse_mode='HTML')
                elif message.content_type == 'video': 
                    bot.send_video(user['uid'], message.video.file_id, caption=caption, parse_mode='HTML')
                elif message.content_type == 'audio': 
                    bot.send_audio(user['uid'], message.audio.file_id, caption=caption, parse_mode='HTML')
                elif message.content_type == 'document': 
                    bot.send_document(user['uid'], message.document.file_id, caption=caption, parse_mode='HTML')
                else: 
                    bot.send_message(user['uid'], message.text, parse_mode='HTML')
            except: pass
        bot.reply_to(message, "✅ <b>Broadcast complete!</b>", parse_mode='HTML')

if __name__ == '__main__':
    Thread(target=keep_alive).start()
    bot.infinity_polling()
