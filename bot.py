from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

TOKEN = os.getenv("BOT_TOKEN")

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        ["📄 Инструкции", "🛒 Купить"],
        ["👨‍💻 Позвать оператора", "❓ Другой вопрос"]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте, спасибо, что обратились в нашу техподдержку!",
        reply_markup=main_menu
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "📄 Инструкции":
        await update.message.reply_text("📘 Инструкция: example.com/manual.pdf")
    elif text == "🛒 Купить":
        await update.message.reply_text("🛍 Каталог:\n1. Бассейн — 2990 ₽\n2. Чехол — 1490 ₽\n3. Тент — 2100 ₽")
    elif text == "👨‍💻 Позвать оператора":
        await update.message.reply_text("Оператор скоро подключится. Пожалуйста, подождите.")
    elif text == "❓ Другой вопрос":
        await update.message.reply_text("Пожалуйста, опишите свой вопрос.")
    else:
        await update.message.reply_text("Я не понял сообщение. Выберите кнопку ниже:", reply_markup=main_menu)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
