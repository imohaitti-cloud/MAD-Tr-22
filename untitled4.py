import os
import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import datetime

TOKEN = "8842616064:AAEwDgWLmufrPcsvOoB-LNXIOL2O2dXehB8"
bot = telebot.TeleBot(TOKEN)

# قائمة الأسواق
ALL_SYMBOLS = [
    "AUDJPY", "CADJPY", "AUDCAD", "AUDCHF", "CADCHF", "CHFJPY", 
    "EURAUD", "EURCHF", "EURJPY", "USDCHF", "USDJPU", "EURUSD", 
    "AUDUSD",
]

def get_analysis(symbol):
    try:
        handler = TA_Handler(symbol=symbol, screener="forex", exchange="OANDA", interval=Interval.INTERVAL_1_MINUTE)
        analysis = handler.get_analysis()
        osc = analysis.oscillators['RECOMMENDATION']
        mov = analysis.moving_averages['RECOMMENDATION']
        
        if osc == "BUY" and mov == "BUY": return "🟢 CALL UP ⬆️"
        elif osc == "SELL" and mov == "SELL": return "🔴 PUT DOWN ⬇️"
        else: return "⚪ NEUTRAL"
    except: return "ERROR"

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(s, callback_data=s) for s in ALL_SYMBOLS]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "🚀 اختر سوقاً للتحليل اللحظي:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    symbol = call.data
    signal = get_analysis(symbol)
    text = f"📊 السوق: {symbol}\n🎯 النتيجة: {signal}\n⏰ {datetime.datetime.now().strftime('%H:%M:%S')}"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=call.message.reply_markup)

if __name__ == "__main__":
    # تشغيل خادم الويب
    Thread(target=run_web).start()
    # تشغيل البوت بدون أي فحص تلقائي
    bot.infinity_polling(none_stop=True)
