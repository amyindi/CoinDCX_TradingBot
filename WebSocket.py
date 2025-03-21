import json
import socketio
import hmac
import hashlib
import os
import certifi
import time

# Ensure SSL verification
os.environ["SSL_CERT_FILE"] = certifi.where()

# WebSocket endpoint
socketEndpoint = "wss://stream.coindcx.com"

# Create a Socket.IO client
sio = socketio.Client(ssl_verify=False, logger=False, engineio_logger=False)

# Load API credentials
key = os.getenv("CDX_KEY")
secret = os.getenv("CDX_SEC")

# Debugging: Ensure API credentials are set
if not key or not secret:
    print("❌ API Key or Secret is missing. Set them as environment variables!")
    exit()

# Convert secret to bytes
secret_bytes = bytes(secret, encoding="utf-8")

@sio.event
def connect():
    print("✅ Connected to WebSocket!")

    # Create request body
    body = {"channel": "coindcx"}
    json_body = json.dumps(body, separators=(",", ":"))

    # Generate HMAC signature
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    # Join channel
    sio.emit("join", {
        "channelName": "coindcx",
        "authSignature": signature,
        "apiKey": key
    })
    print("📡 Subscribed to CoinDCX WebSocket.")

@sio.event
def connect_error(data):
    print("❌ Connection failed:", data)

@sio.event
def disconnect():
    print("🔌 Disconnected from WebSocket. Retrying in 3 seconds...")
    time.sleep(3)
    try:
        sio.connect(socketEndpoint, transports=["websocket"])
    except Exception as e:
        print("❌ Reconnection error:", e)

# 🔥 Event handler for position updates
@sio.on("df-user-cross-position-details")
def on_position_update(response):
    try:
        if "data" in response:
            data = json.loads(response["data"])
            pnl = data.get("pnl", "N/A")
            margin = data.get("maintenance_margin", "N/A")
            balance = data.get("available_wallet_balance", "N/A")
            updated_at = data.get("updated_at", "N/A")

            print(f"📊 Position Update: PnL={pnl}, Margin={margin}, Balance={balance}, Updated At={updated_at}")

        else:
            print("⚠️ Received unexpected data format:", response)

    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", e)

# Catch unexpected events
@sio.on("*")
def catch_all(event, data):
    print(f"🔥 Event: {event}, Data: {data}")

# Connect at the end to ensure event handlers are registered
try:
    sio.connect(socketEndpoint, transports=["websocket"])
    sio.wait()  # Keep the connection alive
except Exception as e:
    print("❌ WebSocket connection error:", str(e))
