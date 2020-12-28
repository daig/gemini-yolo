# USE AT YOUR OWN RISK

[Gemini](https://www.gemini.com) has much lower trading fees when using their API.
This simple script lets you access that for market buy orders.

- Unlike the webpage you must have the required USD available, it will not
automatically withdraw from your bank and credit your account.
- Unlike the webpage you must specify the _buy_ amount rather than the total
  cost. This is more accurate.
- Unlike the webpage, you can buy in any tradepair, like `eth` and `btc`, not
  just buying in `usd`
- Like the webpage, orders are filled as "market orders", which means the best
  price immediately available. There is _NO PRICE PROTECTION_, and will use up
  to your entire balance if you don't bother to look at the current price. If
  you're making a huge order, the price could rise as you dig deeper into the
  books, exhausting the best trades.

This script is intended for fast setup on casual trades. For anything more
serious use the [Industrial API](https://github.com/daig/gemini)

## Usage

recommended: use the [test exchange](https://exchange.sandbox.gemini.com) first.

- [create a gemini primary api key](https://exchange.gemini.com/settings/api)
- clone the repo
- create a .env file in the repo with

```
PUBLIC_KEY="account-stuff"
PRIVATE_KEY="aaaaa"
```

eg buy 1 btc in usd with:

`(export $(cat .env | xargs) && python3 test btc 1 usd)`
