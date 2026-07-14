import os
import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
import time
from threading import Thread
from flask import Flask

# سحب التوكن من إعدادات Render
TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(TOKEN)

# قائمة الأسواق المحدثة بناءً على طلبك
SYMBOLS = {
    "EUR/CHF 🇪🇺🇨🇭": "EURCHF",
    "USD/JPY 🇺🇸🇯🇵": "USDJPY",
    "AUD/CAD 🇦🇺🇨🇦": "AUDCAD",
    "AUD/CHF 🇦🇺🇨🇭": "AUDCHF",
    "CAD/CHF 🇨🇦🇨🇭": "CADCHF",
    "CHF/JPY 🇨🇭🇯🇵": "CHFJPY",
    "EUR/USD 🇪🇺🇺🇸": "EURUSD",
    "EUR/JPY 🇪🇺🇯🇵": "EURJPY",
    "AUD/USD 🇦🇺🇺🇸": "AUDUSD",
    "USD/CHF 🇺🇸🇨🇭": "USDCHF",
    "EUR/AUD 🇪🇺🇦🇺": "EURAUD",
    "AUD/JPY 🇦🇺🇯🇵": "AUDJPY",
    "CAD/JPY 🇨🇦🇯🇵": "CADJPY"
}

user_market = {}

def monitor_market(chat_id):
    while user_market.get(chat_id):
        symbol = user_market[chat_id]
        try:
            # استخدام FX_IDC لمعظم أزواج الفوركس
            handler = TA_Handler(symbol=symbol, screener="forex", exchange="FX_IDC", interval=Interval.INTERVAL_1_MINUTE)
            analysis = handler.get_analysis()
            osc = analysis.oscillators['RECOMMENDATION']
            mov = analysis.moving_averages['RECOMMENDATION']

            if osc == "BUY" and mov == "BUY":
                bot.send_message(chat_id, f"MADTrSignal 🚀\n📊 {symbol}\n🟢 STRONG BUY ⬆️")
            elif osc == "SELL" and mov == "SELL":
                bot.send_message(chat_id, f"MADTrSignal 🚀\n📊 {symbol}\n🔴 STRONG SELL ⬇️")
            
            time.sleep(60) 
        except:
            time.sleep(10)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(name, callback_data=sym) for name, sym in SYMBOLS.items()]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🚫 إيقاف المراقبة", callback_data="STOP"))
    bot.send_message(message.chat.id, "Welcome to MADTrSignal 📈\nاختر السوق للبدء بالمراقبة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "STOP":
        user_market[call.message.chat.id] = None
        bot.answer_callback_query(call.id, "تم إيقاف المراقبة")
    else:
        user_market[call.message.chat.id] = call.data
        bot.answer_callback_query(call.id, f"تم تفعيل {call.data}")
        bot.send_message(call.message.chat.id, f"✅ تم تفعيل مراقبة {call.data}.. سأرسل لك التنبيهات.")
        Thread(target=monitor_market, args=(call.message.chat.id,)).start()

# كود التشغيل كـ Web Service لضمان عمل البوت 24/7 مجاناً
app = Flask(__name__)

@app.route('/')
def home():
    return "MADTrSignal is running!"

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
