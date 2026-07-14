import os
import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
from datetime import datetime

TOKEN = "8842616064:AAGD9riGS8YXB7P_zOOUBRyBY-uTnzvqr10"
bot = telebot.TeleBot(TOKEN)

SYMBOLS_DISPLAY = {
    "AUD/CHF 🇦🇺🇨🇭": "AUDCHF", "CAD/CHF 🇨🇦🇨🇭": "CADCHF", "CHF/JPY 🇨🇭🇯🇵": "CHFJPY",
    "EUR/USD 🇪🇺🇺🇸": "EURUSD", "EUR/JPY 🇪🇺🇯🇵": "EURJPY", "AUD/USD 🇦🇺🇺🇸": "AUDUSD",
    "USD/CHF 🇺🇸🇨🇭": "USDCHF", "EUR/AUD 🇪🇺🇦🇺": "EURAUD", "AUD/JPY 🇦🇺🇯🇵": "AUDJPY",
    "CAD/JPY 🇨🇦🇯🇵": "CADJPY", "EUR/CHF 🇪🇺🇨🇭": "EURCHF", "USD/JPY 🇺🇸🇯🇵": "USDJPY",
    "AUD/CAD 🇦🇺🇨🇦": "AUDCAD"
}

def get_analysis(symbol):
    try:
        handler = TA_Handler(symbol=symbol, screener="forex", exchange="FOREX", interval=Interval.INTERVAL_1_MINUTE)
        analysis = handler.get_analysis()
        osc = analysis.oscillators['RECOMMENDATION']
        mov = analysis.moving_averages['RECOMMENDATION']
        if osc == "BUY" and mov == "BUY": return "🟢 CALL UP ⬆️"
        elif osc == "SELL" and mov == "SELL": return "🔴 PUT DOWN ⬇️"
        else: return "⚪ NEUTRAL"
    except: return "⏳ جاري التحديث..."

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text=name, callback_data=symbol) for name, symbol in SYMBOLS_DISPLAY.items()]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "🚀 اختر سوقاً للتحليل:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    signal = get_analysis(call.data)
    time_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    msg = (
        f"╔══════════════════════╗\n"
        f"        🚀 MAD TR BOT\n"
        f"╚══════════════════════╝\n\n"
        f"💱 السوق\n{call.data}\n\n"
        f"🎯 الإشارة\n{signal}\n\n"
        f"⏱️ الإطار الزمني\n1 Minute\n\n"
        f"📡 المصدر\nTradingView\n\n"
        f"🕒 وقت التحليل\n{time_now}\n\n"
        f"⚠️ ملاحظة\nانتظر إغلاق الشمعة الحالية قبل اتخاذ أي قرار.\n\n"
        f"🤖 Powered By MAD TR"
    )
    
    bot.answer_callback_query(call.id, f"{call.data}: {signal}")
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=call.message.reply_markup)

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling(none_stop=True)
