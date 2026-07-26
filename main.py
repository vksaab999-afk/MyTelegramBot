import os
import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['photo', 'video', 'document', 'text', 'audio', 'voice', 'sticker', 'animation'])
def get_message_id(message):
    chat_id = message.chat.id
    msg_id = message.message_id
    
    response_text = (
        f"✅ <b>Message Mil Gaya!</b>\n\n"
        f"🆔 <b>Message ID:</b> <code>{msg_id}</code>\n"
        f"💬 <b>Chat ID:</b> <code>{chat_id}</code>\n\n"
        f"Is ID ko copy karke mujhe de dena!"
    )
    bot.reply_to(message, response_text, parse_mode='HTML')

if __name__ == '__main__':
    print("Helper Bot Started... Message forward karo!")
    bot.infinity_polling()
