import os
import requests
import json
import base64
import hmac
import hashlib
import datetime, time
import itertools
import sys

[_,live_or_test] = sys.argv

base_url = {"test": "https://api.sandbox.gemini.com"
           ,"live": "https://api.gemini.com"}[live_or_test]

pub_key = os.environ['PUBLIC_KEY']
priv_key = os.environ['PRIVATE_KEY'].encode()

def gemini_get(endpoint):
    url = base_url + endpoint
    print("request: GET {}".format(endpoint))
    time.sleep(1)
    resp = requests.get(url).json()
    print("response: {}".format(resp))
    time.sleep(0.5)
    return resp

def gemini_post(endpoint,payload):
    url = base_url + endpoint
    payload_nonce = str(int(time.mktime(datetime.datetime.now().timetuple())*1000))
    payload['nonce'] = payload_nonce
    print("request: {}".format(payload))
    time.sleep(1)
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
    time.sleep(0.5)
    print("response: {}".format(resp))
    return resp

def gemini_get_balances(currency):
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
    price = round(float(prices[ask_or_bid]) * modifier, tick_size)
    print("price: {}".format(price))
    return price

def gemini_market(buy_or_sell,amount, asset = "btc" ,currency = "usd", margin = 0.1):
    "Execute a buy/sell of 'asset' in 'currency' within 1 +/- 'margin' times market price"
    print(live_or_test.upper())

    pair = (asset + currency).lower()
    print("pair: {}".format(pair))

    details = gemini_get("/v1/symbols/details/" + pair)
    tick_size = int(details['tick_size'])
    amount = round(float(amount), int(details['quote_increment']))
    print("amount: {}".format(amount))

    price = gemini_market_price(buy_or_sell,pair,tick_size,margin)

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
        print("FAILED: {}".format(resp['reason']))
    elif resp['remaining_amount'] == '0':
        print("SUCCESS")
    else:
        print("PARTIAL: {} unfilled".format(resp['remaining_amount']))
