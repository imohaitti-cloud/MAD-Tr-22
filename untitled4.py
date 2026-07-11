import os
import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread

# ==========================
# إعداد البوت
# ==========================
TOKEN = "8842616064:AAEwDgWLmufrPcsvOoB-LNXIOL2O2dXehB8"
bot = telebot.TeleBot(TOKEN)

# ==========================
# إعداد خادم الويب (للحفاظ على التشغيل)
# ==========================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ==========================
# أسواق الفوركس
# ==========================
MARKETS = {
    "EUR/USD 🇪🇺": "EURUSD", "GBP/USD 🇬🇧": "GBPUSD", "USD/JPY 🇯🇵": "USDJPY",
    "USD/CHF 🇨🇭": "USDCHF", "USD/CAD 🇨🇦": "USDCAD", "AUD/USD 🇦🇺": "AUDUSD",
    "NZD/USD 🇳🇿": "NZDUSD", "EUR/GBP": "EURGBP", "EUR/JPY": "EURJPY",
    "GBP/JPY": "GBPJPY", "EUR/CHF": "EURCHF", "GBP/CHF": "GBPCHF",
    "AUD/JPY": "AUDJPY", "CAD/JPY": "CADJPY", "CHF/JPY": "CHFJPY",
    "NZD/JPY": "NZDJPY", "AUD/CAD": "AUDCAD", "AUD/NZD": "AUDNZD",
    "EUR/AUD": "EURAUD", "GBP/AUD": "GBPAUD"
}

# ==========================
# التحليل الفني
# ==========================
def get_analysis(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener="forex",
            exchange="OANDA",
            interval=Interval.INTERVAL_1_MINUTE
        )
        analysis = handler.get_analysis()
        result = analysis.summary['RECOMMENDATION']
        if result == "BUY": return "🟢 BUY"
        elif result == "SELL": return "🔴 SELL"
        else: return "⚪ NEUTRAL"
    except Exception:
        return "❌ غير متاح حالياً"

# ==========================
# أوامر البوت
# ==========================
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(name, callback_data=code) for name, code in MARKETS.items()]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "🚀 MAD Tr\n\nاختر سوق الفوركس للتحليل:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    pair = call.data
    signal = get_analysis(pair)
    text = f"📊 MAD Tr Signal\n\n📈 Pair: {pair}\n\n🎯 Signal: {signal}\n\n⏱ Timeframe: 1 Minute\n\n🌍 Market: Real Forex"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

# ==========================
# التشغيل المتوازي
# ==========================
if __name__ == "__main__":
    # تشغيل خادم الويب في الخلفية
    Thread(target=run_web).start()
    # تشغيل البوت
    print("🚀 MAD Tr Real Forex Bot Running...")
    bot.infinity_polling()
