import telegram
import os
from telegram.ext import Updater, CommandHandler
from utils import get_prices, add_coin, remove_coin, call_user, eastern
from datetime import datetime
import time

telegram_bot_token = os.environ['BOT_API']

updater = Updater(token=telegram_bot_token, use_context=True)
job_queue = updater.job_queue
dispatcher = updater.dispatcher

CHAT_ID = None
USERNAME = None

call_list = {}


def get_current_time():
    now = datetime.now(eastern)
    current_time = now.strftime("%H:%M:%S")
    return current_time


def start(update, context):
    global CHAT_ID, USERNAME
    CHAT_ID = update.effective_chat.id
    USERNAME = update.message.from_user.username

    context.bot.send_message(chat_id=CHAT_ID, text="Welcome to PykoBot!! I will update you on the latest prices for selected cryptocurrencies and alert you when significant price changes occur!\n\n▶️ Type /update to get the latest info on your selected crypto\n▶️ Type /add <i>currency name</i> to add currencies to watchlist\n▶️ Type /remove <i>currency name</i> to remove currencies to watchlist.\n\nInitial currencies in watchlist are: BTC, ADA, DOGE", parse_mode='html')


def fetch_crypto_data(call_possible: False):
    timestamp = get_current_time()
    message = f"⌚ Timestamp: {timestamp}\n\n"

    crypto_data = get_prices()
    for i in crypto_data:
        coin = crypto_data[i]["coin"]
        price = crypto_data[i]["price"]
        change_day = crypto_data[i]["change_day"]
        change_hour = crypto_data[i]["change_hour"]
        day_emoji = '📈' if change_day > 0 else '📉'
        hour_emoji = '📈' if change_hour > 0 else '📉'
        message += f"🪙 Coin: {coin}\n🚀 Price: ${price:,.2f}\n{hour_emoji} Hour Change: {change_hour:.3f}%\n{day_emoji} Day Change: {change_day:.3f}%\n\n"

        if call_possible:
            current_time = int(time.time())
            if change_day > 9:
                if coin not in call_list.keys():
                    call_list[coin] = current_time
                    call_user(USERNAME, coin, change_day, 'increased')
                    return
                elif current_time - call_list[coin] > 86400:
                    call_user(USERNAME, coin, change_day, 'increased')
                    call_list[coin] = current_time
                    return
            elif change_day < -9:
                if coin not in call_list.keys():
                    call_user(USERNAME, coin, change_day, 'decreased')
                    call_list[coin] = current_time
                    return
                elif current_time - call_list[coin] > 86400:
                    call_user(USERNAME, coin, change_day, 'decreased')
                    call_list[coin] = current_time
                    return
    return message


def update_crypto_data(update, context):
    message = fetch_crypto_data(False)
    context.bot.send_message(chat_id=CHAT_ID, text=message)


def update_crypto_data_periodically(context: telegram.ext.CallbackContext):
    message = fetch_crypto_data(False)
    context.bot.send_message(chat_id=CHAT_ID, text=message)


def check_for_drastic_changes(context: telegram.ext.CallbackContext):
    fetch_crypto_data(True)


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

job_queue.run_repeating(update_crypto_data_periodically, interval=900, first=0)
job_queue.run_repeating(check_for_drastic_changes, interval=81, first=0)
updater.start_polling()
updater.idle()
