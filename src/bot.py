import telegram
import os
from telegram.ext import Updater, CommandHandler
from utils import get_prices, add_coin, remove_coin, call_user, get_current_time, get_hot_news, strip_from_bad_chars, add_user
import time

telegram_bot_token = os.environ['BOT_API']

updater = Updater(token=telegram_bot_token, use_context=True)
job_queue = updater.job_queue
dispatcher = updater.dispatcher


# keep store of the last time a call was made to the user for each of the currencies
call_list = {}


# add user to list of users and introduce bot
def start(update, context):
    add_user(update.message.from_user.username)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to PykoBot!! I will update you on the latest prices for selected cryptocurrencies and alert you when significant price changes occur! I will also send you some hot news at certain times in the day!\n\n▶️ Type /add <i>currency name</i> to add currencies to watchlist\n▶️ Type /remove <i>currency name</i> to remove currencies to watchlist\n▶️ Type /updates to receive updates for the currencies in your watchlist\n▶️ Type /news to receive news updates 4 times in the day\n▶️ Type /call to receive a call if one of the currencies in your watchlist experiences a price change of ±10% in 24h\n\nInitial currencies in watchlist are: BTC, ADA, DOGE",
                             parse_mode='html')


# fetch info about the cryptocurrencies in the user's watchlist
def fetch_crypto_data(call_possible: False, username):
    timestamp = get_current_time()
    message = f"⌚ Timestamp: {timestamp}\n\n"

    crypto_data = get_prices(username)
    for i in crypto_data:
        coin = crypto_data[i]["coin"]
        price = crypto_data[i]["price"]
        change_day = crypto_data[i]["change_day"]
        change_hour = crypto_data[i]["change_hour"]
        day_emoji = '📈' if change_day > 0 else '📉'
        hour_emoji = '📈' if change_hour > 0 else '📉'
        message += f"🪙 Coin: {coin}\n🚀 Price: ${price:,.2f}\n{hour_emoji} Hour Change: {change_hour:.3f}%\n{day_emoji} Day Change: {change_day:.3f}%\n\n"

        # call the user if the price of a currency has changed by ±10% over a 24h period
        if call_possible:
            current_time = int(time.time())
            if change_day > 9:
                if coin not in call_list.keys():
                    call_list[coin] = current_time
                    call_user(username, coin, change_day, 'increased')
                    return
                elif current_time - call_list[coin] > 86400:
                    call_user(username, coin, change_day, 'increased')
                    call_list[coin] = current_time
                    return
            elif change_day < -9:
                if coin not in call_list.keys():
                    call_user(username, coin, change_day, 'decreased')
                    call_list[coin] = current_time
                    return
                elif current_time - call_list[coin] > 86400:
                    call_user(username, coin, change_day, 'decreased')
                    call_list[coin] = current_time
                    return
    return message


# subscribe the user to message updates on the crypto in their watchlist. Updates are sent every 900 seconds(15 min)
def update(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='✅ You will now be updated on the latest prices of your selected crypto')

    # add a job to the job_queue which will repeat itself every 900 seconds
    context.job_queue.run_repeating(update_crypto_data_periodically, interval=900, first=0,
                                    context=[update.message.chat_id, update.message.from_user.username])


def update_crypto_data_periodically(context: telegram.ext.CallbackContext):
    context_list = context.job.context
    message = fetch_crypto_data(False, context_list[1])
    context.bot.send_message(chat_id=context_list[0], text=message)


# subscribe the user to call updates on the crypto in their watchlist. Check for drastic fluctuations in price every 81 seconds(requirement for the API through which the calls are made)
def call(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='✅ You will now get calls if there is a drastic change in price in one of your selected crypto')

    # add a job to the job queue which will repeat itself every 81 seconds
    context.job_queue.run_repeating(check_for_drastic_changes, interval=81, first=0,
                                    context=update.message.from_user.username)


def check_for_drastic_changes(context: telegram.ext.CallbackContext):
    fetch_crypto_data(True, context.job.context)


# subscribe the user to news updates 4 times in the day(every 6 hours). News are fetched through the CryptoPanic API
def news(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='✅ You will now get news updates 4 times a day')

    # add a job to the job queue which will repeat itself every 21600 seconds
    context.job_queue.run_repeating(check_for_hot_news, interval=21600, first=0,
                                    context=update.message.chat_id)


def check_for_hot_news(context: telegram.ext.CallbackContext):
    json_response = get_hot_news()
    news = json_response['results']

    message = f'🗞️ Your news at: {get_current_time()}\n\n'

    for i in range(5):
        article = news[i]
        url = article['url']
        title = strip_from_bad_chars(article['title'])
        headline = f'➡️ [{title}]({url})'
        message += f'{headline}\n\n'

    context.bot.send_message(chat_id=context.job.context, text=message, parse_mode='MarkdownV2', disable_web_page_preview=True)


# add a currency to the user's watchlist
def add_coin_to_list(update, context):
    chat_id = update.effective_chat.id

    if len(context.args) > 0:
        for coin in context.args:
            attempt_to_add = add_coin(coin, update.message.from_user.username)
            if attempt_to_add:
                context.bot.send_message(chat_id=chat_id, text=f"✅ Successfully added {coin} to list of currencies")
            else:
                context.bot.send_message(chat_id=chat_id,
                                         text=f"❌ Failed to add {coin} to list of currencies. Check coin name")
    else:
        context.bot.send_message(chat_id=chat_id, text="🤔 What currency do you want to add to watchlist?")


# remove a currency from the user's watchlist
def remove_coin_from_list(update, context):
    chat_id = update.effective_chat.id

    if len(context.args) > 0:
        for coin in context.args:
            attempt_to_remove = remove_coin(coin, update.message.from_user.username)
            if attempt_to_remove:
                context.bot.send_message(chat_id=chat_id, text=f"✅ Successfully removed {coin} from list of currencies")
            else:
                context.bot.send_message(chat_id=chat_id,
                                         text=f"❌ Failed to remove {coin} to list of currencies. Check coin name")
    else:
        context.bot.send_message(chat_id=chat_id, text="🤔 What currency do you want to remove from watchlist?")


# def cancel(update, context):
#     chat_id = update.effective_chat.id
#     context.bot.send_message(chat_id=chat_id, text="Conversation cancelled.")


# assign a command handler for each command
start_handler = CommandHandler("start", start)
update_handler = CommandHandler("update", update)
news_handler = CommandHandler("news", news)
call_handler = CommandHandler("call", call)
add_handler = CommandHandler("add", add_coin_to_list, pass_args=True)
remove_handler = CommandHandler("remove", remove_coin_from_list, pass_args=True)
# cancel_handler = CommandHandler("cancel", cancel)

# add all the handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(update_handler)
dispatcher.add_handler(add_handler)
dispatcher.add_handler(remove_handler)
dispatcher.add_handler(call_handler)
dispatcher.add_handler(news_handler)

updater.start_polling()
updater.idle()
