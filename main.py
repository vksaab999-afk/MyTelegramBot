import os
import telebot
import re
from telebot import types
from pymongo import MongoClient
from flask import Flask
from threading import Thread
import time
import requests

# Configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN')
MONGO_URI = os.environ.get('MONGO_URI')
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://mytelegrambot-alwm.onrender.com')
ADMIN_ID = 5785924075 
CHANNEL_LINK = "https://t.me/+lFOBnj9z7yVmMGM1"
WELCOME_PHOTO = "https://raw.githubusercontent.com/vksaab999-afk/MyTelegramBot/main/poster.png"

# --- 3 MENU LINKS CONFIGURATION ---
AGENT_CHANNEL_LINK = "https://t.me/+aO4PoFUq5gU4YmNl"
ADD_BOT_SETUP_LINK = "https://t.me/+rQ8jUMlvyZozNmE1"

# --- AUTOMATED SEQUENCE CONFIGURATION ---
SOURCE_CHAT_ID = 5785924075  # Tera chat ID jahan se messages copy honge
TARGET_MESSAGE_ID = 4713     # Video + Animated Caption wali Message ID
VOICE_MESSAGE_ID = 5043      # Voice + Caption wali Message ID
APK_FILE_ID = "BQACAgUAAxkBAAIUiWpprNshwyvVGNZ6raSg8MWDoZ5QAALfHwACz_hQVxzmsJRNVjt-PQQ" # APK File ID

# 👇 Registration Link
REGISTRATION_LINK = "https://6club22.com/#/register?invitationCode=134575773989"
# ----------------------------------------

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
client = MongoClient(MONGO_URI)
db = client['tg_bot_database']
users_col = db['users']

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"

def keep_alive(): 
    app.run(host='0.0.0.0', port=8080)

def self_ping_worker():
    while True:
        try:
            if RENDER_EXTERNAL_URL:
                requests.get(RENDER_EXTERNAL_URL)
        except Exception as e:
            print(f"Ping Error: {e}")
        time.sleep(300)

def apply_bold(text):
    return re.sub(r'\*(.*?)\*', r'<b>\1</b>', text or "")

# Menu commands setup (Total 5 Commands)
def set_bot_commands():
    commands = [
        types.BotCommand("start", "Start the bot"),
        types.BotCommand("agent_channel", "Agent Channel"),
        types.BotCommand("add_bot_setup", "Add & Bot Set-up"),
        types.BotCommand("registration_link", "Registration Link"),
        types.BotCommand("download_vip_hack", "Download VIP Hack")
    ]
    bot.set_my_commands(commands)

# Sequence worker with 5s intervals and dual buttons for voice
def send_automated_sequence(chat_id):
    def worker():
        try:
            # 1. Start hone ke 5 second baad video message + download button + automatic pin
            time.sleep(5.0)
            
            markup_video = types.InlineKeyboardMarkup()
            markup_video.add(types.InlineKeyboardButton("📥 Download VIP Hack", callback_data="download_apk"))
            
            sent_msg = bot.copy_message(
                chat_id=chat_id,
                from_chat_id=SOURCE_CHAT_ID,
                message_id=TARGET_MESSAGE_ID,
                reply_markup=markup_video
            )
            
            try:
                bot.pin_chat_message(chat_id=chat_id, message_id=sent_msg.message_id)
            except Exception as pin_err:
                print(f"Pin Error: {pin_err}")
            
            # 2. Video ke 5 second baad voice message + 2 buttons (Registration Link & Join VIP Channel)
            time.sleep(5.0)
            
            markup_voice = types.InlineKeyboardMarkup()
            markup_voice.add(types.InlineKeyboardButton("📝 Registration Link", url=REGISTRATION_LINK))
            markup_voice.add(types.InlineKeyboardButton("✅ Join VIP Channel", url=CHANNEL_LINK))
            
            bot.copy_message(
                chat_id=chat_id,
                from_chat_id=SOURCE_CHAT_ID,
                message_id=VOICE_MESSAGE_ID,
                reply_markup=markup_voice
            )
            
        except Exception as e:
            print(f"Sequence Error: {e}")

    Thread(target=worker, daemon=True).start()

@bot.callback_query_handler(func=lambda call: call.data == "download_apk")
def handle_apk_download(call):
    try:
        bot.send_document(
            chat_id=call.message.chat.id,
            document=APK_FILE_ID,
            caption="📂 <b>Yeh lo aapka VIP Hack APK! Install karke use karein.</b> 🚀",
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id, "✅ APK Download Started!")
    except Exception as e:
        bot.answer_callback_query(call.id, "❌ Kuch error aa gaya, dobara try karein.")
        print(f"APK Send Error: {e}")

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

# --- MENU HANDLERS ---

@bot.message_handler(commands=['agent_channel'])
def agent_channel_handler(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Open Agent Channel", url=AGENT_CHANNEL_LINK))
    bot.reply_to(message, "💼 <b>Agent Channel ke liye niche diye gaye button par click karein:</b>", reply_markup=markup, parse_mode='HTML')

@bot.message_handler(commands=['add_bot_setup'])
def add_bot_setup_handler(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Open Add & Bot Set-up", url=ADD_BOT_SETUP_LINK))
    bot.reply_to(message, "⚙️ <b>Add & Bot Set-up ki jankari ke liye button par click karein:</b>", reply_markup=markup, parse_mode='HTML')

@bot.message_handler(commands=['registration_link'])
def registration_link_handler(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📝 Click to Register", url=REGISTRATION_LINK))
    bot.reply_to(message, "🔗 <b>Registration ke liye niche diye gaye button par click karein:</b>", reply_markup=markup, parse_mode='HTML')

@bot.message_handler(commands=['download_vip_hack'])
def download_vip_hack_handler(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📥 Download VIP Hack", callback_data="download_apk"))
    bot.reply_to(message, "🚀 <b>VIP Hack download karne ke liye niche button par click karein:</b>", reply_markup=markup, parse_mode='HTML')

# --------------------

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

@bot.message_handler(content_types=['photo', 'video', 'document', 'text', 'audio', 'voice', 'sticker', 'animation'])
def handle_all(message):
    # 1. ADMIN REPLY (Pure original copy_message logic)
    if message.from_user.id == ADMIN_ID and message.reply_to_message:
        try:
            reply_text = message.reply_to_message.text or message.reply_to_message.caption or ""
            target_id = int(re.findall(r'🆔\s*(\d+)', reply_text)[-1])
            
            bot.copy_message(target_id, message.chat.id, message.message_id)
            bot.reply_to(message, "✅ <b>Sent Successfully!</b>", parse_mode='HTML')
        except Exception as e:
            bot.reply_to(message, f"❌ <b>Error:</b> ID nahi mili. {e}", parse_mode='HTML')
        return

    # 2. BROADCAST (Pure original copy_message logic)
    elif message.from_user.id == ADMIN_ID and not (message.text and message.text.startswith('/')):
        for u in users_col.find():
            try:
                bot.copy_message(u['uid'], message.chat.id, message.message_id)
            except: continue
        bot.reply_to(message, "✅ <b>Broadcast Done!</b>", parse_mode='HTML')
        return

    # 3. USER MESSAGE
    elif message.from_user.id != ADMIN_ID:
        user_name = message.from_user.first_name
        info_text = f"\n\n👤 <b>User:</b> <a href='tg://user?id={message.from_user.id}'>{user_name}</a>\n🆔 <code>{message.from_user.id}</code>"
        
        if message.content_type == 'text':
            bot.send_message(ADMIN_ID, apply_bold(message.text) + info_text, parse_mode='HTML')
        elif message.content_type == 'sticker':
            bot.send_sticker(ADMIN_ID, message.sticker.file_id)
            bot.send_message(ADMIN_ID, info_text, parse_mode='HTML')
        elif message.content_type == 'animation':
            bot.send_animation(ADMIN_ID, message.animation.file_id, caption=f"{apply_bold(message.caption or '')}{info_text}", parse_mode='HTML')
        else:
            bot.copy_message(ADMIN_ID, message.chat.id, message.message_id, 
                             caption=f"{apply_bold(message.caption or '')}{info_text}", 
                             parse_mode='HTML')

if __name__ == '__main__':
    set_bot_commands()
    Thread(target=keep_alive).start()
    Thread(target=self_ping_worker, daemon=True).start()
    bot.infinity_polling()
