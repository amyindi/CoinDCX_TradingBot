import hmac
import hashlib
import base64
import json
import time
import requests
import os
import certifi
# Load API credentials from environment variables
API_KEY = os.getenv("CDX_KEY")
API_SECRET = os.getenv("CDX_SEC")
BASE_URL = "https://api.coindcx.com/exchange/v1/derivatives/futures/orders/create"

def generate_signature(payload: dict) -> str:
    """
    Generates an HMAC SHA256 signature for the given payload.
    """
    secret_bytes = bytes(API_SECRET, encoding='utf-8')
    json_payload = json.dumps(payload, separators=(',', ':'))
    return hmac.new(secret_bytes, json_payload.encode(), hashlib.sha256).hexdigest()

def send_request(payload: dict) -> dict:
    """
    Sends a signed request to the CoinDCX API
    """
    json_payload = json.dumps(payload, separators=(',', ':'))
    signature = generate_signature(payload)
    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': API_KEY,
        'X-AUTH-SIGNATURE': signature
    }
    response = requests.post(BASE_URL, data=json_payload, headers=headers)
    
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"error": "Invalid response from API", "status_code": response.status_code}
        
def place_order(
    side: str,
    pair: str,
    order_type: str,
    price: float,
    quantity: float,
    leverage: int,
    notification: str = "no_notification",
    time_in_force: str = "good_till_cancel",
    hidden: bool = False,
    post_only: bool = False
) -> dict:
    """
    Places an order on CoinDCX Futures.
    :param side: "buy" or "sell"
    :param pair: Trading pair (e.g., "B-BNB_USDT")
    :param order_type: "market_order" or "limit_order"
    :param price: Order price (ignored for market orders)
    :param quantity: Order size
    :param leverage: Leverage level
    :param notification: "no_notification", "email_notification", or "push_notification"
    :param time_in_force: "good_till_cancel", "fill_or_kill", "immediate_or_cancel"
    :param hidden: True if the order should be hidden
    :param post_only: True if order should only be posted as a maker order
    :return: API response as a dictionary
    """
    payload = {
        "timestamp": int(round(time.time() * 1000)),
        "order": {
            "side": side,
            "pair": pair,
            "order_type": order_type,
            "price": price,
            "total_quantity": quantity,
            "leverage": leverage,
            "notification": notification,
            "time_in_force": time_in_force,
            "hidden": hidden,
            "post_only": post_only
        }
    }
    
    return send_request(payload)

# Example usage:
if __name__ == "__main__":
    response = place_order(
        side="buy",
        pair="B-BNB_USDT",
        order_type="market_order",
        price=800,
        quantity=0.05,
        leverage=5
    )
    print(response)

    
