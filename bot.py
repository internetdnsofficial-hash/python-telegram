import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask
from threading import Thread
import time

# ===== CONFIG =====
TOKEN = "8383678847:AAGUhWof4TagNAi349HZ_zGGzi--1E8BRN0"
CHANNELS = ["@temanonlineterus", "@Zbimx", "@temantapionline", "@botpremiumm"]
REDIRECT_LINK = "https://t.me/+t6GrGDnWVw0zYWI1"
REPL_URL = "https://b1b88025-e829-4df4-afcb-62bf2377b91d-00-wjbnky0oe3nt.spock.replit.dev/"

# ===== Flask =====
app = Flask(__name__)

@app.route('/webhook') 
def home():
    return "Bot is alive!"

def run_flask():
    PORT = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=PORT)

# ===== Keep Alive =====
def keep_alive_ping():
    while True:
        try:
            requests.get(REPL_URL)
        except:
            pass
        time.sleep(280)  # ping tiap ~4 menit 40 detik

# ===== Telegram Handlers =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton(ch, url=f"https://t.me/{ch.replace('@','')}")] for ch in CHANNELS]
    buttons.append([InlineKeyboardButton("✅ Coba lagi", callback_data="check_join")])
    markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "Silakan join semua channel/grup berikut, lalu klik '✅ Coba lagi':",
        reply_markup=markup
    )

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    not_joined = []

    for ch in CHANNELS:
        try:
            member = await context.bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append(ch)
        except:
            not_joined.append(ch)

    if not_joined:
        buttons = [[InlineKeyboardButton(ch, url=f"https://t.me/{ch.replace('@','')}")] for ch in CHANNELS]
        buttons.append([InlineKeyboardButton("✅ Coba lagi", callback_data="check_join")])
        markup = InlineKeyboardMarkup(buttons)

        new_text = (
            "❌ Kamu belum join semua channel/grup berikut:\n" +
            "\n".join(not_joined) +
            "\n\nJoin semua dulu lalu klik '✅ Coba lagi'."
        )

        if query.message.text != new_text:
            await query.edit_message_text(new_text, reply_markup=markup)
        else:
            await query.answer("Kamu masih belum join semua ❌", show_alert=True)

    else:
        success_text = f"✅ Mantap! Kamu sudah join semua.\nKlik link ini untuk lanjut:\n{REDIRECT_LINK}"
        if query.message.text != success_text:
            await query.edit_message_text(success_text)
        else:
            await query.answer("Kamu sudah join semua ✅", show_alert=True)

# ===== Setup Bot =====
app_bot = ApplicationBuilder().token(TOKEN).build()
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))

# ===== Jalankan Flask + Keep Alive + Bot =====
if __name__ == "__main__":
    Thread(target=run_flask).start()         # Flask server
    Thread(target=keep_alive_ping).start()   # Keep alive ping
    app_bot.run_polling()                    # Telegram bot

