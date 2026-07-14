import os
import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from threading import Thread
from flask import Flask

# التوكن
TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(TOKEN)

# قائمة الأسواق
SYMBOLS = {
    "EUR/CHF 🇪🇺🇨🇭": "EURCHF", "USD/JPY 🇺🇸🇯🇵": "USDJPY",
    "AUD/CAD 🇦🇺🇨🇦": "AUDCAD", "AUD/CHF 🇦🇺🇨🇭": "AUDCHF",
    "CAD/CHF 🇨🇦🇨🇭": "CADCHF", "CHF/JPY 🇨🇭🇯🇵": "CHFJPY",
    "EUR/USD 🇪🇺🇺🇸": "EURUSD", "EUR/JPY 🇪🇺🇯🇵": "EURJPY",
    "AUD/USD 🇦🇺🇺🇸": "AUDUSD", "USD/CHF 🇺🇸🇨🇭": "USDCHF",
    "EUR/AUD 🇪🇺🇦🇺": "EURAUD", "AUD/JPY 🇦🇺🇯🇵": "AUDJPY",
    "CAD/JPY 🇨🇦🇯🇵": "CADJPY"
}

# الدالة بالحساسية الجديدة
def get_signal(chat_id, symbol):
    try:
        handler = TA_Handler(symbol=symbol, screener="forex", exchange="FX_IDC", interval=Interval.INTERVAL_1_MINUTE)
        analysis = handler.get_analysis()
        osc = analysis.oscillators['RECOMMENDATION']
        mov = analysis.moving_averages['RECOMMENDATION']

        # شرط أكثر مرونة (يكفي توافق مؤشر واحد أو اتفاقهما)
        if osc == "BUY" or mov == "BUY":
            bot.send_message(chat_id, f"MADTrSignal 🚀\n📊 {symbol}\n🟢 إشارة شراء (Buy Signal)")
        elif osc == "SELL" or mov == "SELL":
            bot.send_message(chat_id, f"MADTrSignal 🚀\n📊 {symbol}\n🔴 إشارة بيع (Sell Signal)")
        else:
            bot.send_message(chat_id, f"📊 {symbol}\n⚠️ السوق هادئ جداً حالياً.")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطأ: {str(e)[:50]}")

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(name, callback_data=sym) for name, sym in SYMBOLS.items()]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "مرحباً MADTrSignal 📈\nاختر السوق:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id, f"جاري فحص {call.data}...")
    get_signal(call.message.chat.id, call.data)

# Flask للتشغيل المستقر
app = Flask(__name__)
@app.route('/')
def home(): return "MADTrSignal is running!"

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
