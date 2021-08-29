import requests

coins = ["BTC", "ADA", "DOGE"]


def get_prices():
    crypto_data = requests.get(
        "https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms=USD".format(",".join(coins))).json()["RAW"]

    data = {}
    for i in crypto_data:
        data[i] = {
            "coin": i,
            "price": crypto_data[i]["USD"]["PRICE"],
            "change_day": crypto_data[i]["USD"]["CHANGEPCT24HOUR"],
            "change_hour": crypto_data[i]["USD"]["CHANGEPCTHOUR"]
        }

    return data


def call_user(username, coin, percentage, direction):
    requests.get(f"http://api.callmebot.com/start.php?user=@{username}&text={coin}+has+{direction}+in+price+by+{percentage:.3f}+percent+today&lang=en-US-Standard-E&rpt=2")


def add_coin(coin_to_add):
    if coin_to_add not in coins:
        coins.append(coin_to_add)
        return True
    else:
        return False


def remove_coin(coin_to_remove):
    if coin_to_remove in coins:
        coins.remove(coin_to_remove)
        return True
    else:
        return False


if __name__ == "__main__":
    print(get_prices())