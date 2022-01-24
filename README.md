# USE AT YOUR OWN RISK

[Gemini](https://www.gemini.com) has much lower trading fees when using their API.
This simple script lets you access that for market buy orders.

- Unlike the webpage you must have the required USD available, it will not
automatically withdraw from your bank and credit your account.
- Unlike the webpage you must specify the _buy_ amount rather than the total
  cost. This is more accurate. You can estimate the correct amount using "cost" instead of "amount".
- Unlike the webpage, you can buy in any tradepair, like `eth` and `btc`, not
  just buying in `usd`
- Unlike the webpage, orders are filled as "limit orders", which means it will
  use the best price immediately available up to some limit you set.
  If you're making a huge order, the price could change as you dig deeper into the
  books, exhausting the best trades - so this protects you from unexpected
  price swings. Limits are controlled fractionally by the `margin` parameter.

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

Start with:

`(export $(cat .env | xargs) && python3 -i yolo.py test)`

(substitute "test" for "live" when running with your real account, and remember
to update the .env with the live credentials too)

inside the interactive environment, 

eg buy 1 btc in usd with:

`gemini_market('buy', amount = 1)`

or sell 1 eth in btc with:
`gemini_market('sell', amount = 1, asset = 'eth', currency = 'btc')`

You can limit the worst case trade by setting the margin parameter.
Eg to buy 1 btc with a maximum price 1% higher than the current best market buy price:
`gemini_market('buy', amount = 1, margin = 0.01)`

Or 1% lower than the current best market sell price:
`gemini_market('sell', amount = 1, margin = 0.01)`

You can instead set how much currency you want to exchange for the asset in the
worst case.

eg to buy up to 1000 dollars worth of ethereum:

`gemini_market('buy', cost = 1000, asset = 'eth')`
