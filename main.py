import os
import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['voice', 'audio'])
def get_voice_id(message):
    chat_id = message.chat.id
    
    if message.voice:
        file_id = message.voice.file_id
        file_type = "Voice Note"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "Audio File"
    else:
        file_id = "N/A"
        file_type = "Unknown"

    response_text = (
        f"✅ <b>{file_type} Mil Gaya!</b>\n\n"
        f"🆔 <b>Voice File ID:</b>\n<code>{file_id}</code>\n\n"
        f"💬 <b>Chat ID:</b> <code>{chat_id}</code>\n\n"
        f"Is File ID ko copy karke mujhe de dena!"
    )
    bot.reply_to(message, response_text, parse_mode='HTML')

if __name__ == '__main__':
    print("Voice ID Helper Bot Started... Voice note bhejo!")
    bot.infinity_polling()
