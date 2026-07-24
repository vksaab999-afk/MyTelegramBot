import os
import telebot
import re
from telebot import types
from pymongo import MongoClient
from flask import Flask
from threading import Thread

BOT_TOKEN = os.environ.get('BOT_TOKEN')
MONGO_URI = os.environ.get('MONGO_URI')
ADMIN_ID = 5785924075 

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

# YEH CODE TERE BOT KO APNI KHUD KI FILE_ID NIKAL KAR DEGA
@bot.message_handler(content_types=['video'])
def get_my_file_id(message):
    if message.from_user.id == ADMIN_ID:
        my_real_file_id = message.video.file_id
        bot.reply_to(message, f"👇 <b>Yeh hai tere bot ki ASLI file_id:</b>\n\n<code>{my_real_file_id}</code>", parse_mode='HTML')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Bhai bot chal raha hai! Abhi apni video mujhe bhej kar apni asli file_id nikal le.")

if __name__ == '__main__':
    Thread(target=keep_alive).start()
    bot.infinity_polling()
