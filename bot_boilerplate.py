import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Use environment variable for security
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello {update.effective_user.first_name}")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am a bot here to help")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am active")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("status", status))
    app.run_polling()

if __name__ == "__main__":
    main()
