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

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if not users_col.find_one({'uid': uid}):
        users_col.insert_one({'uid': uid})
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ JOIN CHANNEL", url=CHANNEL_LINK))
    
    # Simple message for testing start
    bot.send_photo(message.chat.id, "https://telegra.ph/file/8b38382d5563914945d8b.jpg", 
                   caption="🎉 Welcome!\n\n👇 Niche diye gaye button par click karke hamara channel join karein.", 
                   reply_markup=markup)

@bot.message_handler(content_types=['photo', 'video', 'document', 'audio', 'text'])
def handle_messages(message):
    # Broadcast Logic (Admin)
    if message.from_user.id == ADMIN_ID:
        if message.text in ['/stats', '/list']:
            if message.text == '/stats':
                count = users_col.count_documents({})
                bot.reply_to(message, f"📊 Total users: {count}")
            elif message.text == '/list':
                all_users = list(users_col.find())
                bot.reply_to(message, f"Total Users: {len(all_users)}")
            return

        # Broadcast
        all_users = list(users_col.find())
        for user in all_users:
            try:
                if message.content_type == 'photo': bot.send_photo(user['uid'], message.photo[-1].file_id, caption=message.caption)
                elif message.content_type == 'video': bot.send_video(user['uid'], message.video.file_id, caption=message.caption)
                elif message.content_type == 'audio': bot.send_audio(user['uid'], message.audio.file_id, caption=message.caption)
                elif message.content_type == 'document': bot.send_document(user['uid'], message.document.file_id, caption=message.caption)
                else: bot.send_message(user['uid'], message.text)
            except: pass
        bot.reply_to(message, "✅ Broadcast complete!")
    
    # Forwarding (User)
    elif message.from_user.id != ADMIN_ID:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

if __name__ == '__main__':
    Thread(target=keep_alive).start()
    bot.infinity_polling()
