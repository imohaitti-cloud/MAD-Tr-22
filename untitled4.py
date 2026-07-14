import os
import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import datetime
import time

TOKEN = "8842616064:AAEwDgWLmufrPcsvOoB-LNXIOL2O2dXehB8"
bot = telebot.TeleBot(TOKEN)

# إعداد المراقبة التلقائية
AUTO_SYMBOL = "EURUSD" 
is_auto_running = True 
MY_CHAT_ID = "ضع_رقم_الـ_ID_هنا" # <--- لا تنسَ وضع رقم الـ ID الخاص بك هنا

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

def auto_monitor():
    while True:
        if is_auto_running:
            signal = get_analysis(AUTO_SYMBOL)
            if signal in ["🟢 CALL UP ⬆️", "🔴 PUT DOWN ⬇️"]:
                next_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime("%I:%M %p")
                text = f"🤖 Auto Signal\n📊 {AUTO_SYMBOL}\n⏰ {next_time}\n⏳ 1 Minute\n🎯 {signal}"
                try: bot.send_message(MY_CHAT_ID, text)
                except: pass
            time.sleep(60)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("EUR/USD", callback_data="EURUSD"),
        types.InlineKeyboardButton("GBP/USD", callback_data="GBPUSD"),
        types.InlineKeyboardButton("USD/JPY", callback_data="USDJPY"),
        types.InlineKeyboardButton("USD/CHF", callback_data="USDCHF"),
        types.InlineKeyboardButton("AUD/USD", callback_data="AUDUSD"),
        types.InlineKeyboardButton("EUR/JPY", callback_data="EURJPY"),
        types.InlineKeyboardButton("NZD/USD", callback_data="NZDUSD"),
        types.InlineKeyboardButton("CAD/JPY", callback_data="CADJPY"),
        types.InlineKeyboardButton("GBP/JPY", callback_data="GBPJPY"),
        types.InlineKeyboardButton("AUD/JPY", callback_data="AUDJPY"),
        types.InlineKeyboardButton("EUR/GBP", callback_data="EURGBP"),
        types.InlineKeyboardButton("EUR/AUD", callback_data="EURAUD"),
        types.InlineKeyboardButton("USD/CAD", callback_data="USDCAD"),
        types.InlineKeyboardButton("AUD/CHF", callback_data="AUDCHF"),
        types.InlineKeyboardButton("GBP/CAD", callback_data="GBPCAD")
    ]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "🚀 اختر سوقاً للتحليل اللحظي:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    signal = get_analysis(call.data)
    next_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime("%I:%M %p")
    text = f"📊 {call.data}\n⏰ {next_time}\n⏳ 1 Minute\n🎯 {signal}"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    Thread(target=run_web).start()
    Thread(target=auto_monitor, daemon=True).start()
    bot.infinity_polling()
