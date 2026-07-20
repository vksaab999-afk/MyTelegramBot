import os
import telebot
import re
from telebot import types
from pymongo import MongoClient
from flask import Flask
from threading import Thread
import time

# Configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN')
MONGO_URI = os.environ.get('MONGO_URI')
ADMIN_ID = 5785924075 
CHANNEL_LINK = "https://t.me/+lFOBnj9z7yVmMGM1"
WELCOME_PHOTO = "https://raw.githubusercontent.com/vksaab999-afk/MyTelegramBot/main/poster.png"

# --- AUTOMATED SEQUENCE CONFIGURATION ---
AUTO_VIDEO_FILE_ID = "BAACAgUAAxkBAAIPcmpd1d_ydbdiiJLHlTMsz-_3JeGxAAKVJwACOWPwVnfD5_F52X1mPQQ" 

AUTO_VIDEO_CAPTION = """*Game ki traf se Frist deposit bonus to milege hi milega uska sath Jitna bada deposit utna bada profit or gift code meri traf se bhi milega ✨🫶🏻*

*1k Deposit ₹50 Bonus💸* 
*2.5k Deposit ₹150 Bonus💸* 
*5k Deposit ₹350 Bonus💸* 
*13k Deposit ₹800 Bonus💸* 
*30k Deposit ₹1500 Bonus💸* 

*Gift code lena ke liye deposit ke baad mujhe msg kro @teamrajajii_bot 👀*

*Channel me request tabhi accept hogi jab aapki I'd hamare official link se bani huyi hogi 🫶🏻💫*

*Prediction Timetable 💞*

*10:00AM ✅*
*12:00PM ✅*
*06:00PM ✅*
*09:00PM ✅*"""

REGISTRATION_LINK = "https://bdgking.vip//#/register?invitationCode=8235121574870"
FOLLOWUP_MESSAGE = "👋 Hello Dear! Kya aapko koi help chahiye ya koi doubt hai? Aap mujhe yhi message karke pooch sakte ho."
# ----------------------------------------

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
client = MongoClient(MONGO_URI)
db = client['tg_bot_database']
users_col = db['users']

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def keep_alive(): app.run(host='0.0.0.0', port=8080)

def apply_bold(text):
    return re.sub(r'\*(.*?)\*', r'<b>\1</b>', text or "")

# Bulletproof background sequence worker
def send_automated_sequence(chat_id):
    def worker():
        try:
            time.sleep(30.0)
            formatted_caption = apply_bold(AUTO_VIDEO_CAPTION)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔗 Registration Link", url=REGISTRATION_LINK))
            bot.send_video(chat_id, AUTO_VIDEO_FILE_ID, caption=formatted_caption, reply_markup=markup, parse_mode='HTML')
            
            time.sleep(30.0)
            bot.send_message(chat_id, apply_bold(FOLLOWUP_MESSAGE), parse_mode='HTML')
        except Exception as e:
            print(f"Sequence Error: {e}")

    Thread(target=worker, daemon=True).start()

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
        
    send_automated_sequence(message.chat.id)

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
            uname = str(u.get('username', 'Chat')).replace('<', '').replace('>', '')
            msg += f'<a href="tg://user?id={uid}">{uname}</a> | <code>{uid}</code>\n'
        bot.reply_to(message, msg[:4000], parse_mode='HTML')

@bot.message_handler(content_types=['photo', 'video', 'document', 'text', 'audio', 'voice'])
def handle_all(message):
    # 1. ADMIN REPLY (Media/Text Caption Bold Support)
    if message.from_user.id == ADMIN_ID and message.reply_to_message:
        try:
            reply_text = message.reply_to_message.text or message.reply_to_message.caption or ""
            target_id = int(re.findall(r'🆔\s*(\d+)', reply_text)[-1])
            
            if message.content_type == 'text':
                bot.send_message(target_id, apply_bold(message.text), parse_mode='HTML')
            else:
                formatted_caption = apply_bold(message.caption or "")
                bot.copy_message(target_id, message.chat.id, message.message_id, caption=formatted_caption, parse_mode='HTML')
            bot.reply_to(message, "✅ <b>Sent Successfully!</b>", parse_mode='HTML')
        except Exception as e:
            bot.reply_to(message, f"❌ <b>Error:</b> ID nahi mili. {e}", parse_mode='HTML')
        return

    # 2. BROADCAST (Media/Text Caption Bold Support)
    elif message.from_user.id == ADMIN_ID and not (message.text and message.text.startswith('/')):
        for u in users_col.find():
            try:
                if message.content_type == 'text':
                    bot.send_message(u['uid'], apply_bold(message.text), parse_mode='HTML')
                else:
                    formatted_caption = apply_bold(message.caption or "")
                    bot.copy_message(u['uid'], message.chat.id, message.message_id, caption=formatted_caption, parse_mode='HTML')
            except: continue
        bot.reply_to(message, "✅ <b>Broadcast Done!</b>", parse_mode='HTML')
        return

    # 3. USER MESSAGE (Text Bold + Info Attached)
    elif message.from_user.id != ADMIN_ID:
        user_name = message.from_user.first_name
        info_text = f"\n\n👤 <b>User:</b> <a href='tg://user?id={message.from_user.id}'>{user_name}</a>\n🆔 <code>{message.from_user.id}</code>"
        
        if message.content_type == 'text':
            bot.send_message(ADMIN_ID, apply_bold(message.text) + info_text, parse_mode='HTML')
        else:
            bot.copy_message(ADMIN_ID, message.chat.id, message.message_id, 
                             caption=f"{apply_bold(message.caption or '')}{info_text}", 
                             parse_mode='HTML')

if __name__ == '__main__':
    Thread(target=keep_alive).start()
    bot.infinity_polling()
