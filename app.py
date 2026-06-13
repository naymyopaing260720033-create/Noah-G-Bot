import os
import telebot
import google.generativeai as genai
from flask import Flask, request

# --- CONFIGURATION ---
# local မှာ စမ်းရင် ဒီနေရာမှာ direct ထည့်နိုင်ပါတယ်။ 
# Render ပေါ်တင်ရင်တော့ Environment Variables အနေနဲ့ သုံးပါမယ်။
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
GEMINI_KEY = os.getenv("GEMINI_KEY", "YOUR_GEMINI_API_KEY_HERE")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") # Render URL ရမှ ပြန်ထည့်ရပါမယ်။

# AI နဲ့ Bot ကို Setup လုပ်ခြင်း
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- TELEGRAM BOT LOGIC ---

# /start သို့မဟုတ် /help ခေါ်ရင် တုံ့ပြန်ရန်
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! ကျွန်တော်က Gemini AI Bot ဖြစ်ပါတယ်။ သိလိုသမျှ မေးမြန်းနိုင်ပါတယ်။")

# စာသားမက်ဆေ့ခ်ျအားလုံးကို Gemini AI နဲ့ တွက်ချက်ပြီး ပြန်စာပို့ရန်
@bot.message_handler(func=lambda message: True)
def reply_with_gemini(message):
    try:
        # AI ဆီက အဖြေတောင်းခြင်း
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"စိတ်မကောင်းပါဘူး၊ အမှားတစ်ခုရှိနေလို့ပါ: {str(e)}")

# --- SERVER FOR RENDER (WEBHOOK) ---
# Render မှာ ပုံမှန် bot.polling() သုံးရင် စက်က ပိတ်သွားတတ်လို့ Webhook (Flask) ကို သုံးရပါတယ်။

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    if WEBHOOK_URL:
        bot.set_webhook(url=WEBHOOK_URL + '/' + BOT_TOKEN)
        return "Webhook Set Successfully!", 200
    return "Bot is running, but Webhook URL is missing.", 200

if __name__ == "__main__":
    # Render သည် ၎င်း၏ Port ကို Environment Variable မှ ပေးလေ့ရှိသည်
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
