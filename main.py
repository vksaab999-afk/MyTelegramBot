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
    caption = "🎉 <b>Welcome!</b>\n\n👇 Niche diye gaye button par click karke hamara channel join karein."
    try:
        bot.send_photo(message.chat.id, WELCOME_PHOTO, caption=caption, reply_markup=markup, parse_mode='HTML')
    except:
        bot.send_message(message.chat.id, caption, reply_markup=markup, parse_mode='HTML')

# ADMIN COMMANDS
@bot.message_handler(commands=['stats', 'list'])
def admin_commands(message):
    if message.from_user.id != ADMIN_ID: return
    
    if message.text == '/stats':
        count = users_col.count_documents({})
        bot.reply_to(message, f"📊 <b>Total Users:</b> {count}", parse_mode='HTML')
    
    elif message.text == '/list':
        all_users = list(users_col.find())
        msg = "<b>User List:</b>\n"
        for u in all_users:
            uid = u['uid']
            uname = u.get('username')
            clean_uname = str(uname).replace('_', '').replace('*', '')
            msg += f'<a href="tg://user?id={uid}">{clean_uname or "Chat"}</a> | <code>{uid}</code>\n'
        bot.reply_to(message, msg[:4000], parse_mode='HTML')

# BOLD FORMATTING FUNCTION (Isse aapka *text* bold ho jayega)
def format_text(text):
    # Regex ke bina simple logic: har * pair ko <b>...</b> se replace karega
    parts = text.split('*')
    for i in range(1, len(parts), 2):
        parts[i] = f"<b>{parts[i]}</b>"
    return "".join(parts)

# MESSAGE HANDLER
@bot.message_handler(content_types=['photo', 'video', 'document', 'text'])
def handle_all(message):
    # 1. ADMIN REPLY
    if message.from_user.id == ADMIN_ID and message.reply_to_message:
        try:
            target_id = int(message.reply_to_message.text.split('🆔')[1].strip())
            # Reply mein bhi formatting chalu rakhi hai
            formatted = format_text(message.text or message.caption or "")
            bot.copy_message(target_id, message.chat.id, message.message_id)
            bot.reply_to(message, "✅ <b>Reply sent!</b>", parse_mode='HTML')
        except:
            bot.reply_to(message, "❌ <b>Error:</b> ID nahi mili.", parse_mode='HTML')
        return

    # 2. BROADCAST
    elif message.from_user.id == ADMIN_ID and not (message.text and message.text.startswith('/')):
        raw_text = (message.text or message.caption or "")
        formatted_text = format_text(raw_text) # Yahan formatting apply hogi
        for u in users_col.find():
            try:
                if message.content_type == 'photo': bot.send_photo(u['uid'], message.photo[-1].file_id, caption=formatted_text, parse_mode='HTML')
                elif message.content_type == 'video': bot.send_video(u['uid'], message.video.file_id, caption=formatted_text, parse_mode='HTML')
                elif message.content_type == 'document': bot.send_document(u['uid'], message.document.file_id, caption=formatted_text, parse_mode='HTML')
                else: bot.send_message(u['uid'], formatted_text, parse_mode='HTML')
            except: continue
        bot.reply_to(message, "✅ <b>Broadcast Done!</b>", parse_mode='HTML')
        return

    # 3. USER MESSAGE
    elif message.from_user.id != ADMIN_ID:
        user_text = message.text or message.caption or ""
        full_msg = f"{user_text}\n\n👤 <b>User:</b> {message.from_user.first_name}\n🆔 <code>{message.from_user.id}</code>"
        bot.send_message(ADMIN_ID, full_msg, parse_mode='HTML')

if __name__ == '__main__':
    Thread(target=keep_alive).start()
    bot.infinity_polling()
