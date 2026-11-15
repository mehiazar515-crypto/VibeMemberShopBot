
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8966749977"))

logging.basicConfig(level=logging.INFO)

PACKAGES = {
    "one": ("تبلیغ ۱ روزه", "100000 تومان"),
    "two": ("تبلیغ ۳ روزه", "200000 تومان"),
    "three": ("تبلیغ ۷ روزه", "400000 تومان")
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛍 مشاهده خدمات", callback_data="shop")],
        [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")]
    ]

    await update.message.reply_text(
        "⭐ به فروشگاه VibeMemberShop خوش آمدید!\n\n"
        "برای مشاهده خدمات از دکمه زیر استفاده کنید.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "shop":
        keyboard = [
            [InlineKeyboardButton("تبلیغ ۱ روزه", callback_data="one")],
            [InlineKeyboardButton("تبلیغ ۳ روزه", callback_data="two")],
            [InlineKeyboardButton("تبلیغ ۷ روزه", callback_data="three")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="home")]
        ]
        await query.edit_message_text(
            "🛒 خدمات فروشگاه:\nیک خدمت را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in PACKAGES:
        name, price = PACKAGES[query.data]
        context.user_data["package"] = name
        await query.edit_message_text(
            f"📦 خدمت: {name}\n"
            f"💰 قیمت: {price}\n\n"
            "لطفاً لینک کانال خود را ارسال کنید."
        )

    elif query.data == "support":
        await query.edit_message_text(
            "📞 برای پشتیبانی پیام خود را ارسال کنید."
        )

    elif query.data == "home":
        await start_from_query(query)

async def start_from_query(query):
    keyboard = [
        [InlineKeyboardButton("🛍 مشاهده خدمات", callback_data="shop")],
        [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")]
    ]
    await query.edit_message_text(
        "⭐ به فروشگاه VibeMemberShop خوش آمدید!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def receive_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    package = context.user_data.get("package")

    if not package:
        await update.message.reply_text(
            "برای ثبت سفارش ابتدا از منوی خدمات استفاده کنید."
        )
        return

    user = update.effective_user
    link = update.message.text

    await context.bot.send_message(
        ADMIN_ID,
        f"🛍 سفارش جدید\n\n"
        f"👤 کاربر: {user.full_name}\n"
        f"🆔 شناسه: {user.id}\n"
        f"📦 خدمت: {package}\n"
        f"🔗 لینک: {link}"
    )

    await update.message.reply_text(
        "✅ درخواست شما ثبت شد.\n"
        "پس از بررسی، پشتیبانی با شما هماهنگ می‌کند."
    )

    context.user_data.clear()

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN تنظیم نشده است")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_order))

    app.run_polling()

if __name__ == "__main__":
    main()
