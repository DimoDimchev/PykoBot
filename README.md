
# PykoBot

A Telegram bot created in Python for the purpose of being helpful to crypto-hobbyists

**DISLAIMER**: THIS BOT IS FOR EXPERIMENTAL USE ONLY. USE AT YOUR OWN RISK. THE CREATOR OF THIS BOT IS NOT RESPONSIBLE FOR ANY LOSSES   
## Functionality

After the `/start` command is given to the bot it will register the user and assign the default cryptocurrencies(_ADA_, _BTC_, _DOGE_) to their watchlist

Here is a list to all other commands and their functions:
- `/update`: receive price updates for the cryptocurrencies in your watchlist every 2 hours
- `/call`: receive a phone call if any of your cryptocurrencies fluctuates in price ±10% in a period of 24hours. **IMPORTANT: send `/start` to @CallMeBot_txtbot in Telegram to enable this functionality**
- `/news`: receive news updates 4 times in a day
- `/add crypto_abbreviation`: add cryptocurrency to your watchlist
- `/remove crypto_abbreviation`: remove cryptocurrency from your watchlist

## Technical stuff

This is an interesting project and I have implemented a few API's into it in order for all commands to work properly:
- The core functionality of the bot is built using [The Telegram Bot API](https://core.telegram.org/bots/api) and the [python-telegram-bot library](https://python-telegram-bot.readthedocs.io/en/stable/#)
- Automated calls to users are made using the [CallMeBot Telegram API](https://www.callmebot.com/telegram-call-api/)
- News are fetched using the [CryptoCompare API](https://min-api.cryptocompare.com/)
- Price info is fetched using the [CryptoCompare API](https://min-api.cryptocompare.com/)

## What's next

This is a project that I use on a daily basis and I plan to keep improving it in the future. The next step is to add automated trading to the bot but I don't see that happening soon as there is a lot of learning I need to do to fully understand how automated trading works.

## Contributing

If you have any suggestions for improving the bot or adding new functionality feel free to open a PR or create an issue