import requests
from pytz import timezone
from datetime import datetime

user_dict = {}

eastern = timezone('Europe/Sofia')


def add_user(user):
    if user not in user_dict.keys():
        user_dict[user] = ["ADA", "BTC", "DOGE"]


def get_current_time():
    now = datetime.now(eastern)
    current_time = now.strftime("%H:%M:%S")
    return current_time


def get_prices(user):
    crypto_data = requests.get(
        "https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms=USD".format(",".join(user_dict[user]))).json()[
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


def get_hot_news():
    request = requests.get(
        "https://cryptopanic.com/api/v1/posts/?auth_token=146b86de9eec553afcbe86e56e5438498324df97&public=true")
    response = request.json()
    return response


def strip_from_bad_chars(str):
    return str.translate(str.maketrans({"-": r"\-",
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


def call_user(username, coin, percentage, direction):
    requests.get(
        f"http://api.callmebot.com/start.php?user=@{username}&text={coin}+has+{direction}+in+price+by+{percentage:.3f}+percent+today&lang=en-US-Standard-E&rpt=2")


def add_coin(coin_to_add, user):
    if coin_to_add not in user_dict[user]:
        user_dict[user].append(coin_to_add)
        return True
    else:
        return False


def remove_coin(coin_to_remove, user):
    if coin_to_remove in user_dict[user]:
        user_dict[user].remove(coin_to_remove)
        return True
    else:
        return False


if __name__ == "__main__":
    print(get_prices())
