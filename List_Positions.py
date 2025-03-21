import hmac
import hashlib
import base64
import json
import time
import requests
from datetime import datetime
import pytz
import os


# Enter your API Key and Secret here. If you don't have one, you can generate it from the website.
key = os.getenv("CDX_KEY")
secret = os.getenv("CDX_SEC")

# python3
#secret_bytes = secret.encode('utf-8')
secret_bytes = bytes(secret, encoding='utf-8')
# python2 secret_bytes = bytes(secret)
# Generating a timestamp
timeStamp = int(round(time.time() * 1000))
body = {
"timestamp":timeStamp , # EPOCH timestamp in seconds
"page": "1", #no. of pages needed
"size": "10" #no. of records needed
}
json_body = json.dumps(body, separators = (',', ':'))

signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
url = "https://api.coindcx.com/exchange/v1/derivatives/futures/positions"
headers = {
'Content-Type': 'application/json',
'X-AUTH-APIKEY': key,
'X-AUTH-SIGNATURE': signature
}
response = requests.post(url, data = json_body, headers = headers)
data = response.json()
#print(data)
# Filter only active positions (active_pos > 0)
active_positions = [pos for pos in data if pos["active_pos"] > 0]

# Convert timestamp to IST and display relevant data
ist = pytz.timezone('Asia/Kolkata')

for pos in active_positions:
    updated_at_utc = datetime.utcfromtimestamp(pos["updated_at"] / 1000)
    updated_at_ist = updated_at_utc.replace(tzinfo=pytz.utc).astimezone(ist).strftime('%Y-%m-%d %H:%M:%S IST')

# Print active positions
#print(json.dumps(active_positions, indent=4))
# Display required details
for pos in active_positions:
    print(f"Active Position: {pos['active_pos']} {pos['pair'].split('_')[0][2:]}")
    print(f"Entry Price: ${pos['avg_price']}")
    print(f"Current Mark Price: ${pos['mark_price']}")
    print(f"Leverage: {pos['leverage']}x")
    print(f"Locked Margin: ${pos['locked_margin']}")
    print(f"Updated At: {updated_at_ist}")
    print("-" * 40)  # Separator for readability
