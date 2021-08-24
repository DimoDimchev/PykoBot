import telegram
import os
from telegram.ext import Updater, CommandHandler, ConversationHandler
from tracker import get_prices, add_coin, remove_coin

telegram_bot_token = os.environ['BOT_API']

updater = Updater(token=telegram_bot_token, use_context=True)
job_queue = updater.job_queue
dispatcher = updater.dispatcher


def start(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Welcome to PykoBot!! I will update you on the latest prices for selected cryptocurrencies and alert you when significant price changes occur!\n\n▶️ Type /update to get the latest info on your selected crypto\n▶️ Type /add <i>currency name</i> to add currencies to watchlist\n▶️ Type /remove <i>currency name</i> to remove currencies to watchlist.\n\nInitial currencies in watchlist are: BTC, ADA, DOGE", parse_mode='html')


def update_crypto_data(update, context):
    chat_id = update.effective_chat.id
    message = ""

    crypto_data = get_prices()
    for i in crypto_data:
        coin = crypto_data[i]["coin"]
        price = crypto_data[i]["price"]
        change_day = crypto_data[i]["change_day"]
        change_hour = crypto_data[i]["change_hour"]
        message += f"💵 Coin: {coin}\n💲 Price: ${price:,.2f}\n📈 Hour Change: {change_hour:.3f}%\n📈 Day Change: {change_day:.3f}%\n\n"

    context.bot.send_message(chat_id=chat_id, text=message)


def update_crypto_data_periodically(context: telegram.ext.CallbackContext):
    chat_id = 951078147
    message = ""

    crypto_data = get_prices()
    for i in crypto_data:
        coin = crypto_data[i]["coin"]
        price = crypto_data[i]["price"]
        change_day = crypto_data[i]["change_day"]
        change_hour = crypto_data[i]["change_hour"]
        message += f"💵 Coin: {coin}\n💲 Price: ${price:,.2f}\n📈 Hour Change: {change_hour:.3f}%\n📈 Day Change: {change_day:.3f}%\n\n"

    context.bot.send_message(chat_id=chat_id, text=message)


def add_coin_to_list(update, context):
    chat_id = update.effective_chat.id

    if len(context.args) > 0:
        for coin in context.args:
            attempt_to_add = add_coin(coin)
            if attempt_to_add:
                context.bot.send_message(chat_id=chat_id, text=f"✅ Successfully added {coin} to list of currencies")
            else:
                context.bot.send_message(chat_id=chat_id, text=f"❌ Failed to add {coin} to list of currencies. Check coin name")
    else:
        context.bot.send_message(chat_id=chat_id, text="🤔 What currency do you want to add to watchlist?")


def remove_coin_from_list(update, context):
    chat_id = update.effective_chat.id

    if len(context.args) > 0:
        for coin in context.args:
            attempt_to_remove = remove_coin(coin)
            if attempt_to_remove:
                context.bot.send_message(chat_id=chat_id, text=f"✅ Successfully removed {coin} from list of currencies")
            else:
                context.bot.send_message(chat_id=chat_id, text=f"❌ Failed to remove {coin} to list of currencies. Check coin name")
    else:
        context.bot.send_message(chat_id=chat_id, text="🤔 What currency do you want to remove from watchlist?")


def cancel(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Conversation cancelled.")


start_handler = CommandHandler("start", start)
update_handler = CommandHandler("update", update_crypto_data)
add_handler = CommandHandler("add", add_coin_to_list, pass_args=True)
remove_handler = CommandHandler("remove", remove_coin_from_list, pass_args=True)
cancel_handler = CommandHandler("cancel", cancel)


dispatcher.add_handler(start_handler)
dispatcher.add_handler(update_handler)
dispatcher.add_handler(add_handler)
dispatcher.add_handler(remove_handler)

dispatcher.add_handler(ConversationHandler(entry_points=[add_handler, remove_handler], states={}, fallbacks=[cancel_handler], conversation_timeout=10))
job_queue.run_repeating(update_crypto_data_periodically, interval=900, first=0)
updater.start_polling()
updater.idle()