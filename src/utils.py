import requests
from pytz import timezone
from datetime import datetime

# keep store of all users using the bot and their watchlists
user_dict = {}

eastern = timezone('Europe/Sofia')


# fetch the current time(EEST)
def get_current_time():
    now = datetime.now(eastern)
    current_time = now.strftime("%H:%M:%S")
    return current_time


# strip article title from bad characters so it can be passed to MarkdownV2 in Telegram API
def strip_from_bad_chars(str):
    return str.translate(str.maketrans({" ": r"\-",
                                        "-": r"\-",
                                        "]": r"\]",
                                        "\\": r"\\",
                                        "^": r"\^",
                                        "$": r"\$",
                                        "*": r"\*",
                                        ".": r"\.",
                                        "_": r"\_",
                                        "[": r"\[",
                                        "(": r"\(",
                                        ")": r"\)",
                                        "~": r"\~",
                                        "`": r"\`",
                                        ">": r"\>",
                                        "+": r"\+",
                                        "=": r"\=",
                                        "|": r"\|",
                                        "{": r"\{",
                                        "}": r"\}",
                                        "!": r"\!",
                                        "#": r"\#"}))


# fetch price info for the currencies in the user's watchlist via the CryptoCompare API
def get_prices(user):
    crypto_data = requests.get(
        "https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms=USD".format(
            ",".join(user_dict[user]))).json()[
        "RAW"]

    data = {}
    for i in crypto_data:
        data[i] = {
            "coin": i,
            "price": crypto_data[i]["USD"]["PRICE"],
            "change_day": crypto_data[i]["USD"]["CHANGEPCT24HOUR"],
            "change_hour": crypto_data[i]["USD"]["CHANGEPCTHOUR"]
        }

    return data


# fetch news from the CryptoCompare API
def get_hot_news():
    request = requests.get(
        "https://min-api.cryptocompare.com/data/v2/news/?lang=EN")
    response = request.json()
    return response


# add user to user_dict and assign the default cryptocurrencies to them
def add_user(user):
    if user not in user_dict.keys():
        user_dict[user] = ["ADA", "BTC", "DOGE"]


# call the user via the CallMeBot API
def call_user(username, coin, percentage, direction):
    requests.get(
        f"http://api.callmebot.com/start.php?user=@{username}&text={coin}+has+{direction}+in+price+by+{percentage:.3f}+percent+today&lang=en-US-Standard-E&rpt=2")


# add coin to the user's watchlist
def add_coin(coin_to_add, user):
    if coin_to_add not in user_dict[user]:
        user_dict[user].append(coin_to_add)
        return True
    else:
        return False


# remove coin from the user's watchlist
def remove_coin(coin_to_remove, user):
    if coin_to_remove in user_dict[user]:
        user_dict[user].remove(coin_to_remove)
        return True
    else:
        return False
