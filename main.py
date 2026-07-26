import os
import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['document', 'file'])
def get_file_link(message):
    try:
        if message.document:
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            file_path = file_info.file_path
            
            # Telegram ka direct public download URL
            direct_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            
            response_text = (
                f"✅ <b>Direct Link Mil Gaya!</b>\n\n"
                f"🔗 <b>Link:</b>\n<code>{direct_url}</code>\n\n"
                f"Is link ko copy karke mujhe de dena!"
            )
            bot.reply_to(message, response_text, parse_mode='HTML')
        else:
            bot.reply_to(message, "⚠️ Bhai kripya .apk file bhejein.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

if __name__ == '__main__':
    print("Link Generator Bot Started... APK bhejo!")
    bot.infinity_polling()
