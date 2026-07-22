"""
KASSA BOT — ikki kishilik (siz + akangiz) kirim/chiqim hisobi uchun Telegram bot.

O'RNATISH QADAMLARI ilovaning oxirida, README.md faylida yozilgan.
"""

import sqlite3
import logging
from datetime import datetime

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(level=logging.INFO)

# ============ SOZLAMALAR — SHU YERNI TO'LDIRING ============

BOT_TOKEN = 8300081981:AAH5FknJiwTRhd9ejO3vF7b9tmFUOw42Awk
# Telegram raqamli ID'laringizni 834334406
# Faqat shu ikki ID botga yoza oladi — boshqa hech kim emas.
ALLOWED_USERS = {
    111111111: "Siz",   # <--834334406 Saidjamolxon
    222222222: "Akam",  # <-- 1072634760 Aka
}

DB_PATH = "kassa.db"

# =============================================================

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [["➕ Kirim", "➖ Chiqim"], ["💰 Balans", "📜 Oxirgi yozuvlar"]],
    resize_keyboard=True,
)


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT,
            user_name TEXT NOT NULL,
            ts TEXT NOT NULL
        )"""
    )
    return conn


def get_balance():
    conn = db()
    cur = conn.execute(
        "SELECT type, SUM(amount) FROM transactions GROUP BY type"
    )
    totals = {"kirim": 0.0, "chiqim": 0.0}
    for t, s in cur.fetchall():
        totals[t] = s or 0.0
    conn.close()
    return totals["kirim"] - totals["chiqim"], totals["kirim"], totals["chiqim"]


def add_transaction(tx_type, amount, note, user_name):
    conn = db()
    conn.execute(
        "INSERT INTO transactions (type, amount, note, user_name, ts) VALUES (?,?,?,?,?)",
        (tx_type, amount, note, user_name, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def last_transactions(limit=10):
    conn = db()
    cur = conn.execute(
        "SELECT type, amount, note, user_name, ts FROM transactions ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def fmt(n):
    return f"{n:,.0f}".replace(",", " ")


def is_allowed(user_id):
    return user_id in ALLOWED_USERS


async def guard(update: Update) -> bool:
    if not is_allowed(update.effective_user.id):
        await update.message.reply_text(
            "⛔ Kechirasiz, sizda bu botdan foydalanishga ruxsat yo'q."
        )
        return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    context.user_data.pop("pending", None)
    name = ALLOWED_USERS[update.effective_user.id]
    await update.message.reply_text(
        f"Assalomu alaykum, {name}! 👋\nKassa botiga xush kelibsiz.\n\n"
        "➕ Kirim — pul kiritish\n➖ Chiqim — xarajat yozish\n"
        "💰 Balans — joriy kassa holati\n📜 Oxirgi yozuvlar — tarix",
        reply_markup=MAIN_KEYBOARD,
    )


async def show_balance(update: Update):
    bal, tin, tout = get_balance()
    await update.message.reply_text(
        f"💰 Kassada: {fmt(bal)} so'm\n\n"
        f"➕ Jami kirim: {fmt(tin)} so'm\n"
        f"➖ Jami chiqim: {fmt(tout)} so'm",
        reply_markup=MAIN_KEYBOARD,
    )


async def show_history(update: Update):
    rows = last_transactions(10)
    if not rows:
        await update.message.reply_text("Hozircha yozuvlar yo'q.", reply_markup=MAIN_KEYBOARD)
        return
    lines = ["📜 Oxirgi yozuvlar:\n"]
    for t, amount, note, user_name, ts in rows:
        sign = "+" if t == "kirim" else "-"
        date = ts.replace("T", " ")[:16]
        note_part = f" — {note}" if note else ""
        lines.append(f"{sign}{fmt(amount)} so'm{note_part}\n   ({user_name}, {date})")
    await update.message.reply_text("\n".join(lines), reply_markup=MAIN_KEYBOARD)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return

    text = update.message.text.strip()
    user_name = ALLOWED_USERS[update.effective_user.id]
    pending = context.user_data.get("pending")

    # Asosiy menyu tugmalari
    if text == "➕ Kirim":
        context.user_data["pending"] = {"type": "kirim", "stage": "amount"}
        await update.message.reply_text("Summani kiriting (faqat raqam, masalan: 150000):")
        return
    if text == "➖ Chiqim":
        context.user_data["pending"] = {"type": "chiqim", "stage": "amount"}
        await update.message.reply_text("Summani kiriting (faqat raqam, masalan: 50000):")
        return
    if text == "💰 Balans":
        await show_balance(update)
        return
    if text == "📜 Oxirgi yozuvlar":
        await show_history(update)
        return

    # Kirim/Chiqim jarayoni davomida
    if pending and pending["stage"] == "amount":
        try:
            amount = float(text.replace(" ", "").replace(",", "."))
            if amount <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("Iltimos, to'g'ri musbat son kiriting (masalan: 150000).")
            return
        pending["amount"] = amount
        pending["stage"] = "note"
        await update.message.reply_text("Izoh kiriting (yoki izohsiz o'tkazib yuborish uchun \"-\" yozing):")
        return

    if pending and pending["stage"] == "note":
        note = "" if text == "-" else text
        add_transaction(pending["type"], pending["amount"], note, user_name)
        context.user_data.pop("pending", None)
        bal, _, _ = get_balance()
        emoji = "➕" if pending["type"] == "kirim" else "➖"
        await update.message.reply_text(
            f"{emoji} {fmt(pending['amount'])} so'm saqlandi.\n💰 Yangi balans: {fmt(bal)} so'm",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    await update.message.reply_text(
        "Quyidagi tugmalardan birini tanlang 👇", reply_markup=MAIN_KEYBOARD
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
