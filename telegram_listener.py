from telegram.ext import Updater, CommandHandler

BOT_TOKEN = "7404930359:AAFBMfFIZUZuToI25LszgYcAlgdcYdWCLTo"

def start(update, context):
    update.message.reply_text("Hey 👋🏽 Bot is live and listening!")

updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))

updater.start_polling()
updater.idle()
