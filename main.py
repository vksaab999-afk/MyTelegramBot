import os
import telebot
from telebot import types
from pymongo import MongoClient
from flask import Flask
from threading import Thread

# Configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN')
MONGO_URI = os.environ.get('MONGO_URI')
ADMIN_ID = 5785924075 
CHANNEL_LINK = "https://t.me/+lFOBnj9z7yVmMGM1"
WELCOME_PHOTO = "https://raw.githubusercontent.com/vksaab999-afk/MyTelegramBot/main/poster.png"

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
client = MongoClient(MONGO_URI)
db = client['tg_bot_database']
users_col = db['users']

# Keep Alive Server
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def keep_alive(): app.run(host='0.0.0.0', port=8080)

# START COMMAND
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if not users_col.find_one({'uid': uid}):
        users_col.insert_one({'uid': uid, 'username': message.from_user.username or "None"})
    
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
        msg = "<b>User List:</b>\n"
        for u in all_users:
            uid = u['uid']
            uname = u.get('username')
            # HTML format: Sabhi clickable honge
            if uname and uname != "None" and uname != "N/A":
                clean_uname = uname.replace('_', '').replace('*', '')
                msg += f'<a href="tg://user?id={uid}">@{clean_uname}</a> | {uid}\n'
            else:
                msg += f'<a href="tg://user?id={uid}">Chat Link</a> | {uid}\n'
        
        bot.reply_to(message, msg[:4000], parse_mode='HTML')

# MESSAGE HANDLER
@bot.message_handler(content_types=['photo', 'video', 'document', 'text'])
def handle_all(message):
    # 1. ADMIN REPLY
    if message.from_user.id == ADMIN_ID and message.reply_to_message:
        target_id = None
        if message.reply_to_message.forward_from:
            target_id = message.reply_to_message.forward_from.id
        else:
            try:
                target_id = int(message.reply_to_message.text.split('|')[-1].strip())
            except: pass
        
        if target_id:
            bot.copy_message(target_id, message.chat.id, message.message_id)
            return 

    # 2. BROADCAST
    elif message.from_user.id == ADMIN_ID and not (message.text and message.text.startswith('/')):
        for u in users_col.find():
            try:
                if message.content_type == 'photo': bot.send_photo(u['uid'], message.photo[-1].file_id, caption=message.caption)
                elif message.content_type == 'video': bot.send_video(u['uid'], message.video.file_id, caption=message.caption)
                elif message.content_type == 'document': bot.send_document(u['uid'], message.document.file_id, caption=message.caption)
                else: bot.send_message(u['uid'], message.text)
            except: continue
        bot.reply_to(message, "✅ Broadcast Done!")
        return

    # 3. USER FORWARD
    elif message.from_user.id != ADMIN_ID:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

if __name__ == '__main__':
    Thread(target=keep_alive).start()
    bot.infinity_polling()
