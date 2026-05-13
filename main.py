from flask import Flask, request
import telebot
import google.generativeai as genai

# کلیلەکانت
TOKEN = '8683676881:AAGhLlMGi28Y_v36BWVLZ8UA-x0skMNaiJY'
GEMINI_API_KEY = 'AIzaSyC0d32dYq3MZt2XJBLlPMggIHtWXSehJs4'

# ڕێکخستنی جێمینای و بۆتەکە
bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "سڵاو! من بۆتی زیرەکی دەستکردم بۆ ئامادەکردنی سیمینار. 🎓\n\nتەنها ناونیشانی بابەتەکە و ئەو زمانەی دەتەوێت بۆم بنێرە."
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    msg = bot.reply_to(message, "⏳ خەریکی ئامادەکردنی سیمینارەکەم، تکایە کەمێک چاوەڕێ بکە...")
    
    try:
        prompt = f"تۆ پرۆفیسۆر و شارەزایەکی بواری ئامادەکردنی سیمیناریت. بەکارهێنەرێک داوای ئەم بابەتەی لێکردوویت: '{message.text}'\nتکایە سیمینارێکی زانستی، ورد و ڕێک و پێکی بۆ ئامادە بکە بە هەمان ئەو زمانەی کە داوای کردووە کە پێشەکی، ناوەڕۆک، و دەرەنجام لەخۆ بگرێت."
        
        response = model.generate_content(prompt)
        bot.delete_message(message.chat.id, msg.message_id)
        
        text_response = response.text
        # دابەشکردنی نامەکان ئەگەر زۆر درێژ بوون
        if len(text_response) > 4000:
            for i in range(0, len(text_response), 4000):
                bot.send_message(message.chat.id, text_response[i:i+4000])
        else:
            bot.send_message(message.chat.id, text_response)
            
    except Exception as e:
        bot.delete_message(message.chat.id, msg.message_id)
        bot.send_message(message.chat.id, "❌ ببورە، کێشەیەک ڕوویدا لە کاتی درووستکردنی سیمینارەکەدا.")

# وەرگرتنی نامەکان لە تێلیگرامەوە (Webhook)
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Forbidden', 403

# چالاککردنی پەیوەندی نێوان تێلیگرام و Vercel
@app.route('/set_webhook')
def set_webhook():
    webhook_url = request.host_url
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return f"✅ Webhook بە سەرکەوتوویی بەسترایەوە بە: {webhook_url}", 200
