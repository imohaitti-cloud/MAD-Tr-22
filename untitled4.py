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
MY_CHAT_ID = "8842616064"

# قائمة جميع الأسواق
ALL_SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "EURJPY", 
    "NZDUSD", "CADJPY", "GBPJPY", "AUDJPY", "EURGBP", "EURAUD", 
    "USDCAD", "AUDCHF", "GBPCAD", "XAUUSD", "USOIL"
]

# متغيرات التحكم
is_auto_running = False # التلقائي معطل افتراضياً

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
            for symbol in ALL_SYMBOLS:
                signal = get_analysis(symbol)
                if signal in ["🟢 CALL UP ⬆️", "🔴 PUT DOWN ⬇️"]:
                    text = f"🤖 Auto Scanner Found:\n📊 {symbol}\n🎯 {signal}\n⏰ {datetime.datetime.now().strftime('%H:%M:%S')}"
                    try: bot.send_message(MY_CHAT_ID, text)
                    except: pass
                time.sleep(2) # تأخير بسيط بين كل فحص سوق لتجنب الحظر
        time.sleep(10)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔍 وضع يدوي (اختيار سوق)", callback_data="manual_mode"))
    markup.add(types.InlineKeyboardButton("🤖 وضع تلقائي (فحص الكل)", callback_data="auto_mode"))
    bot.send_message(message.chat.id, "مرحباً! اختر نظام عمل البوت:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global is_auto_running
    
    if call.data == "auto_mode":
        is_auto_running = True
        bot.answer_callback_query(call.id, "تم تفعيل الوضع التلقائي!")
        bot.send_message(call.message.chat.id, "✅ تم تفعيل الوضع التلقائي: البوت سيفحص كل الأسواق تلقائياً.")
        
    elif call.data == "manual_mode":
        is_auto_running = False
        markup = types.InlineKeyboardMarkup(row_width=3)
        buttons = [types.InlineKeyboardButton(s, callback_data=f"sel_{s}") for s in ALL_SYMBOLS]
        markup.add(*buttons)
        bot.edit_message_text("اختر السوق للتحليل اليدوي:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    elif call.data.startswith("sel_"):
        symbol = call.data.split("_")[1]
        signal = get_analysis(symbol)
        text = f"📊 السوق: {symbol}\n🎯 النتيجة: {signal}\n⏰ {datetime.datetime.now().strftime('%H:%M:%S')}"
        bot.send_message(call.message.chat.id, text)

if __name__ == "__main__":
    Thread(target=run_web).start()
    Thread(target=auto_monitor, daemon=True).start()
    bot.infinity_polling()
