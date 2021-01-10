import os
import requests
import json
import base64
import hmac
import hashlib
import datetime, time
import itertools
import sys

def wait():
    time.sleep(0.5)

[_,live_or_test] = sys.argv

base_url = {"test": "https://api.sandbox.gemini.com"
           ,"live": "https://api.gemini.com"}[live_or_test]

pub_key = os.environ['PUBLIC_KEY']
priv_key = os.environ['PRIVATE_KEY'].encode()

def gemini_get(endpoint):
    url = base_url + endpoint
    print("\nREQUEST: GET {}".format(endpoint))
    wait()
    resp = requests.get(url).json()
    print("RESPONSE: {}\n".format(resp))
    wait()
    return resp

def gemini_post(endpoint,payload):
    url = base_url + endpoint
    payload_nonce = str(int(time.mktime(datetime.datetime.now().timetuple())*1000))
    payload['nonce'] = payload_nonce
    print("\nREQUEST: {}".format(payload))
    wait()
    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(priv_key, b64, hashlib.sha384).hexdigest()
    request_headers = { 'Content-Type': "text/plain",
                        'Content-Length': "0",
                        'X-GEMINI-APIKEY': pub_key,
                        'X-GEMINI-PAYLOAD': b64,
                        'X-GEMINI-SIGNATURE': signature,
                        'Cache-Control': "no-cache" }
    resp = requests.post(url,
                            data=None,
                            headers=request_headers).json()
    wait()
    print("RESPONSE: {}\n".format(resp))
    return resp

def gemini_get_balances():
    """Get your current balance info for 'currency'"""
    endpoint = "/v1/balances"
    balances = gemini_post(endpoint, {"request": endpoint})
    return dict((x['currency'].lower(), x) for x in balances)

    
def gemini_market_price(buy_or_sell,pair,tick_size,margin):
    """Calculate a ask/bid limit price that will ensure a trade no more than
    'margin' times more/less than market price"""
    ask_or_bid = {"buy" : "ask", "sell" : "bid"}[buy_or_sell]
    prices = gemini_get("/v2/ticker/" + pair)
    modifier = {
            "buy" : 1 + margin,
            "sell" : 1 - margin
            }[buy_or_sell]
    market_price = float(prices[ask_or_bid])
    price = round(market_price * modifier, tick_size)
    return (market_price , price)

def balance_report(balances,asset):
    balance = balances[asset]
    print("You have {} {}, with {} available to trade, and {} available to withdraw"
            .format(balance['amount'],asset.upper(),balance['available'],balance['availableForWithdrawal']))

def gemini_market(buy_or_sell,amount = None, cost = None, asset = "btc" ,currency = "usd", margin = 0.001):
    "Execute a buy/sell of 'asset' in 'currency' within 1 +/- 'margin' times market price"
    print(live_or_test.upper())

    {'buy' : (), 'sell' : ()}[buy_or_sell]

    pair = (asset + currency).lower()
    print("pair: {}".format(pair))

    pre_balances = gemini_get_balances()

    details = gemini_get("/v1/symbols/details/" + pair)
    tick_size = int(details['tick_size'])
    quote_increment = int(details['quote_increment'])

    prices = gemini_market_price(buy_or_sell,pair,tick_size,margin)
    market_price = prices[0]
    price = prices[1]

    if not amount and cost:
        amount = round(float(cost)/price,quote_increment)
    elif not cost and amount:
        amount = round(float(amount),quote_increment)
    else:
        raise Exception("one of 'amount' or 'cost' must be provided")

    max_or_min = {"buy" : "maximum", "sell" : "minimum"}[buy_or_sell]
    cur = currency.upper()
    total = round(amount*price,tick_size)
    total_expected = round(amount*market_price,tick_size)
    print("attempting to {} {} {} at a {} of {} {} each ({} {} expected),\nfor a total {} of {} {} ({} {} expected)"
            .format(buy_or_sell,amount,asset.upper(),
                    max_or_min,
                    price,cur,
                    market_price,cur,
                    max_or_min,
                    total,cur,
                    total_expected,cur
                   )
            )
    balance_report(pre_balances,asset)
    balance_report(pre_balances,currency)
    cont = input("Continue? YES/NO\n")
    if cont != "YES":
        raise Exception("Aborted by user. Must confirm YES")

    endpoint = "/v1/order/new"
    payload = {
       "request": endpoint,
        "symbol": pair,
        "amount": amount,
        "price": price,
        "side": buy_or_sell,
        "type": "exchange limit",
        "options": ["immediate-or-cancel"] 
    }
    resp = gemini_post(endpoint, payload)
    if 'reason' in resp:
        if resp['reason'] == "InsufficientFunds":
            balance = gemini_get_balances()[currency]
            total = round(amount*price,tick_size)
            print("Insufficient Funds: You only have {} {} available to trade (but {} total), you tried to spend {}"
                    .format(balance['available'],currency.upper(),balance['amount'],total))
        else:
            print("FAILED: {}".format(resp['reason']))

    elif resp['remaining_amount'] == '0':
        avg_price = float(resp['avg_execution_price'])
        balances = gemini_get_balances()
        total = round(amount*avg_price,tick_size)
        print("SUCCESS: {} {} {} for {} {} each, totalling {} {}"
                .format(buy_or_sell,amount,asset.upper(),resp['avg_execution_price'],currency.upper(),total,currency.upper()))
        balance_report(balances,asset)
        balance_report(balances,currency)
    else:
        print("PARTIAL: {} {} unfilled".format(resp['remaining_amount'],asset))
