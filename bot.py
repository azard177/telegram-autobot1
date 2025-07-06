
import json, os, logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# Загрузка токена и ID оператора из переменных среды
TOKEN = os.getenv("BOT_TOKEN")
OPERATOR_CHAT_ID = int(os.getenv("OPERATOR_CHAT_ID", "17868551565"))  

# ---------- читаем каталог ----------
with open("catalog.json", encoding="utf-8") as f:
    CATALOG = json.load(f)

def categories_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(cat["cat_name"], callback_data=f"cat_{cat['cat_id']}")]
        for cat in CATALOG
    ])

def items_keyboard(cat_id):
    cat = next(c for c in CATALOG if c["cat_id"] == cat_id)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(item["name"], callback_data=f"item_{item['id']}")]
        for item in cat["items"]
    ])

# ---------- главное меню ----------
main_menu = ReplyKeyboardMarkup(
    [["🛍 Каталог", "📄 Инструкции"],
     ["👨‍💻 Техподдержка", "❓ Другой вопрос"]],
    resize_keyboard=True
)

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Я помогу вам выбрать и купить товары.\n"
        "Нажмите «🛍 Каталог» или выберите действие:",
        reply_markup=main_menu
    )

# ---------- текст ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.lower()
    if "каталог" in txt:
        await update.message.reply_text("Выберите категорию:", reply_markup=categories_keyboard())
    elif "инструк" in txt:
        await update.message.reply_text("Инструкции: https://xn----7sbbqqeail6cgq0d.xn--p1ai/faq/")
    elif "техпод" in txt or "оператор" in txt:
        user = update.message.from_user
        user_info = f"👤 @{user.username or user.first_name} (ID: {user.id})"
        await update.message.reply_text("Оператор подключится в ближайшее время.")
        await context.bot.send_message(
            chat_id=OPERATOR_CHAT_ID,
            text=f"📞 Новый запрос в техподдержку от {user_info}:\n{update.message.text}"
        )
    else:
        await update.message.reply_text("Выберите кнопку ниже:", reply_markup=main_menu)

# ---------- нажали категорию ----------
async def category_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat_id = update.callback_query.data.removeprefix("cat_")
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "Товары:",
        reply_markup=items_keyboard(cat_id)
    )

# ---------- нажали товар ----------
async def item_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item_id = update.callback_query.data.removeprefix("item_")
    await update.callback_query.answer()
    item = next(i for cat in CATALOG for i in cat["items"] if i["id"] == item_id)
    caption = (
        f"*{item['name']}* — {item['price']} ₽\n"
        f"{item['desc']}\n\n"
        "✏️ Напишите количество или вопрос по товару."
    )
    await update.callback_query.message.reply_photo(
        photo=item["photo"],
        caption=caption,
        parse_mode="Markdown"
    )

# ---------- запуск ----------
def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(category_click, pattern=r"^cat_"))
    app.add_handler(CallbackQueryHandler(item_click,      pattern=r"^item_"))

    print("Bot with full catalog is running…")
    app.run_polling()

if __name__ == "__main__":
    main()
