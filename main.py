import os
import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['document', 'file'])
def get_apk_id(message):
    chat_id = message.chat.id
    
    # Check if document is APK
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        
        response_text = (
            f"✅ <b>APK Mil Gayi!</b>\n\n"
            f"📁 <b>File Name:</b> {file_name}\n"
            f"🆔 <b>File ID:</b> <code>{file_id}</code>\n"
            f"💬 <b>Chat ID:</b> <code>{chat_id}</code>\n\n"
            f"Is File ID ko copy karke mujhe de dena!"
        )
        bot.reply_to(message, response_text, parse_mode='HTML')
    else:
        bot.reply_to(message, "⚠️ Bhai yeh APK file nahi hai, kripya .apk file bhejein.")

if __name__ == '__main__':
    print("APK Helper Bot Started... APK file bhejo!")
    bot.infinity_polling()
