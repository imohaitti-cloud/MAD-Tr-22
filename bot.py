import os
import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval

# التوكن يتم سحبه من المتغيرات في Render
TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(TOKEN)

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

def get_signal(chat_id, symbol):
    try:
        handler = TA_Handler(symbol=symbol, screener="forex", exchange="FX_IDC", interval=Interval.INTERVAL_1_MINUTE)
        analysis = handler.get_analysis()
        osc = analysis.oscillators['RECOMMENDATION']
        mov = analysis.moving_averages['RECOMMENDATION']

        if osc == "BUY" and mov == "BUY":
            bot.send_message(chat_id, f"MADTrSignal 🚀\n📊 {symbol}\n🟢 إشارة شراء قوية (Strong Buy)")
        elif osc == "SELL" and mov == "SELL":
            bot.send_message(chat_id, f"MADTrSignal 🚀\n📊 {symbol}\n🔴 إشارة بيع قوية (Strong Sell)")
        else:
            bot.send_message(chat_id, f"📊 {symbol}\n⚠️ لا توجد إشارة واضحة حالياً، جرب الضغط مرة أخرى.")
    except Exception as e:
        bot.send_message(chat_id, "⚠️ خطأ في جلب البيانات، يرجى المحاولة لاحقاً.")

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(name, callback_data=sym) for name, sym in SYMBOLS.items()]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "أهلاً بك في MADTrSignal 📈\nاختر السوق للحصول على إشارة فورية:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id, f"جاري الفحص لـ {call.data}...")
    get_signal(call.message.chat.id, call.data)

print("Bot is running...")
bot.infinity_polling()
