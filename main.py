import os
import threading
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from flask import Flask

# ١. درووستکردنی سێرڤەرێکی بچووک بۆ مانەوەی لە Render
app = Flask(__name__)
@app.route('/')
def index():
    return "Bot is successfully running on Render!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ٢. کلیلەکانت
TELEGRAM_TOKEN = '8725342011:AAFayx5fayQwUoFLDiXUdWWDVk0NMFI5DcA'
GEMINI_API_KEY = 'AIzaSyC0d32dYq3MZt2XJBLlPMggIHtWXSehJs4'

# ڕێکخستنی جێمینای
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "سڵاو! من بۆتی زیرەکی دەستکردم بۆ ئامادەکردنی سیمینار. 🎓\n\nتەنها ناونیشانی بابەتەکە و ئەو زمانەی دەتەوێت بۆم بنێرە."
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    wait_message = await update.message.reply_text("⏳ خەریکی ئامادەکردنی سیمینارەکەم، تکایە کەمێک چاوەڕێ بکە...")
    
    try:
        prompt = f"""تۆ پرۆفیسۆر و شارەزایەکی بواری ئامادەکردنی سیمیناریت. بەکارهێنەرێک داوای ئەم بابەتەی لێکردوویت: "{user_text}"\nتکایە سیمینارێکی زانستی بۆ ئامادە بکە بە هەمان ئەو زمانەی کە داوای کردووە کە پێشەکی، ناوەڕۆک، و دەرەنجام لەخۆ بگرێت."""
        response = model.generate_content(prompt)
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=wait_message.message_id)
        
        text_response = response.text
        if len(text_response) > 4000:
            for i in range(0, len(text_response), 4000):
                await update.message.reply_text(text_response[i:i+4000])
        else:
            await update.message.reply_text(text_response)
    except Exception as e:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=wait_message.message_id)
        await update.message.reply_text("❌ کێشەیەک ڕوویدا لە کاتی درووستکردنی سیمینارەکەدا.")

if __name__ == '__main__':
    # خستنەگەڕی ماڵپەڕەکە لە پشتەوە (Background)
    t = threading.Thread(target=run_web)
    t.start()
    
    # خستنەگەڕی بۆتەکە
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("بۆتەکە ئامادەیە...")
    application.run_polling()
