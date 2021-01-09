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
[_,live_or_test,buy,amount,currency] = sys.argv
base_url = {"test": "https://api.sandbox.gemini.com"
           ,"live": "https://api.gemini.com"}[live_or_test]

pub_key = os.environ['PUBLIC_KEY']
priv_key = os.environ['PRIVATE_KEY'].encode()

endpoint = "/v1/balances"
url = base_url + endpoint

payload_nonce = str(int(time.mktime(datetime.datetime.now().timetuple())*1000))

payload = {
   "request": endpoint,
    "nonce": payload_nonce,
}
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
balances = response.json()
print(balances)
balance = next(filter(lambda x: x["currency"] == currency.upper(),
    balances))["available"]

time.sleep(1)

endpoint = "/v1/order/new"
url = base_url + endpoint

payload_nonce = str(int(time.mktime(datetime.datetime.now().timetuple())*1000))

payload = {
   "request": endpoint,
    "nonce": payload_nonce,
    "symbol": (buy + currency).lower(),
    "amount": amount,
    "price": balance,
    "side": "buy",
    "type": "exchange limit",
    "options": ["immediate-or-cancel"] 
}
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
print(new_order)
