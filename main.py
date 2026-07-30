import os
import telebot

# Apna Bot Token yahan daal dena
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'TERA_BOT_TOKEN_YAHAN_DAAL')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def get_message_id(message):
    # Agar tu kisi message ko forward karega ya reply karega, ye uska ID bata dega
    msg_id = message.message_id
    bot.reply_to(message, f"📌 <b>Is message ka Message ID hai:</b> <code>{msg_id}</code>", parse_mode='HTML')

if __name__ == '__main__':
    print("ID Finder Bot Started...")
    bot.infinity_polling()
