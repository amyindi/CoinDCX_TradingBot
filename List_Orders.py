import hmac
import hashlib
import base64
import json
import time
import requests
import os


# Enter your API Key and Secret here. If you don't have one, you can generate it from the website.
key = os.getenv("CDX_KEY")
secret = os.getenv("CDX_SEC")

# python3
secret_bytes = bytes(secret, encoding='utf-8')
# python2 secret_bytes = bytes(secret)
# Generating a timestamp
timeStamp = int(round(time.time() * 1000))
body = {
"timestamp": timeStamp , # EPOCH timestamp in seconds
"status": "open", # Comma separated statuses as open,filled,cancelled
"side": "buy", # buy OR sell
"page": "1", #// no.of pages needed
"size": "10" #// no.of records needed
}
json_body = json.dumps(body, separators = (',', ':'))
signature = hmac.new(secret_bytes, json_body.encode(),hashlib.sha256).hexdigest()
url = "https://api.coindcx.com/exchange/v1/derivatives/futures/orders"
headers = {
'Content-Type': 'application/json',
'X-AUTH-APIKEY': key,
'X-AUTH-SIGNATURE': signature
}
response = requests.post(url, data = json_body, headers = headers)
data = response.json()
print(data)

