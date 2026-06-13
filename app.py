import os
import telebot
import google.generativeai as genai
from flask import Flask, request

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# AI နှင့် Bot အား Setup ပြုလုပ်ခြင်း
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(BOT_TOKEN, threaded=False) # Thread ပိတ်ထားမှ Flask နဲ့ ငြိမတက်မှာပါ
app = Flask(__name__)

# --- TELEGRAM BOT LOGIC ---

# /start သို့မဟုတ် /help ခေါ်ဆိုပါက တုံ့ပြန်ရန်
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.reply_to(message, "မင်္ဂလာပါ! ကျွန်တော်က Gemini AI Bot ဖြစ်ပါတယ်။ သိလိုသမျှ မေးမြန်းနိုင်ပါတယ်။")
    except Exception as e:
        print(f"Error sending welcome: {e}")

# စာသားမက်ဆေ့ခ်ျအားလုံးကို Gemini AI ဖြင့် တွက်ချက်ပြီး ပြန်စာပို့ရန်
@bot.message_handler(func=lambda message: True)
def reply_with_gemini(message):
    try:
        # AI ဆီမှ အဖြေတောင်းခြင်း
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Gemini Error: {e}")
        bot.reply_to(message, "စိတ်မကောင်းပါဘူး၊ AI အလုပ်လုပ်ရာတွင် အမှားတစ်ခုရှိနေလို့ပါ။")

# --- SERVER FOR RENDER (WEBHOOK ROUTER) ---

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def getMessage():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Invalid Secret', 403

# Browser ကနေ ဝင်ကြည့်ရင် သာမန် Message ပဲ ပြတော့မှာဖြစ်လို့ 429 Error ထပ်မတက်တော့ပါဘူး
@app.route("/")
def webhook():
    return "Bot Server is Alive and Running!", 200

if __name__ == "__main__":
    # စက်စနိုးနိုးချင်းမှာ Webhook ကို အလိုအလျောက် တစ်ခေါက်တည်း ချိတ်ပေးမည့်စနစ်
    if WEBHOOK_URL:
        try:
            clean_url = WEBHOOK_URL.strip().rstrip('/')
            bot.remove_webhook()
            bot.set_webhook(url=f"{clean_url}/{BOT_TOKEN}")
            print("Webhook set successfully during startup!")
        except Exception as e:
            print(f"Failed to set webhook at startup: {e}")
            
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


# ပင်မ URL ကို နှိပ်လျှင် Webhook လမ်းကြောင်းကို အလိုအလျောက် Reset ချပေးမည့်နေရာ
@app.route("/")
def webhook():
    bot.remove_webhook()
    if WEBHOOK_URL:
        clean_url = WEBHOOK_URL.strip().rstrip('/')
        # လမ်းကြောင်းကို အတိအကျ ချိတ်ဆက်ခြင်း
        bot.set_webhook(url=f"{clean_url}/{BOT_TOKEN}")
        return "Webhook Set Successfully!", 200
    return "Bot is running, but WEBHOOK_URL Environment Variable is missing.", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
