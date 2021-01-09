import os
import requests
import json
import base64
import hmac
import hashlib
import datetime, time
import itertools
import sys

print(sys.argv)
[_,live_or_test,sell,amount,currency] = sys.argv
base_url = {"test": "https://api.sandbox.gemini.com"
           ,"live": "https://api.gemini.com"}[live_or_test]

pub_key = os.environ['PUBLIC_KEY']
priv_key = os.environ['PRIVATE_KEY'].encode()

endpoint = "/v2/ticker/" + sell + currency
url = base_url + endpoint

print("endpoint: " + endpoint)

response = requests.get(url)
prices = response.json()
# print(prices)
price = prices['bid']

time.sleep(0.5)

endpoint = "/v1/symbols/details/" + sell + currency
url = base_url + endpoint

response = requests.get(url)
details = response.json()
print(details)
min_price = 10 ** (- int(details['tick_size']))




if True:
    time.sleep(0.5)

    endpoint = "/v1/order/new"
    url = base_url + endpoint

    payload_nonce = str(int(time.mktime(datetime.datetime.now().timetuple())*1000))

    payload = {
       "request": endpoint,
        "nonce": payload_nonce,
        "symbol": (sell + currency).lower(),
        "amount": amount,
        "price": min_price,
        "side": "sell",
        "type": "exchange limit",
        "options": ["immediate-or-cancel"] 
    }
    print("payload:")
    print(payload)
    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(priv_key, b64, hashlib.sha384).hexdigest()
    request_headers = { 'Content-Type': "text/plain",
                        'Content-Length': "0",
                        'X-GEMINI-APIKEY': pub_key,
                        'X-GEMINI-PAYLOAD': b64,
                        'X-GEMINI-SIGNATURE': signature,
                        'Cache-Control': "no-cache" }
    response = requests.post(url,
                            data=None,
                            headers=request_headers)
    new_order = response.json()
    print("response: ")
    print(new_order)
