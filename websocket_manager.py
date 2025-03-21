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
SOCKET_ENDPOINT = "wss://stream.coindcx.com"

# Load API credentials
API_KEY = os.getenv("CDX_KEY")
API_SECRET = os.getenv("CDX_SEC")

if not API_KEY or not API_SECRET:
    raise ValueError("❌ API Key or Secret is missing. Set them as environment variables!")

# Convert secret to bytes
SECRET_BYTES = bytes(API_SECRET, encoding="utf-8")

class WebSocketManager:
    def __init__(self):
        self.sio = socketio.Client(ssl_verify=False, logger=False, engineio_logger=False)
        self._register_events()

    def _generate_signature(self, payload: dict) -> str:
        """Generates an HMAC SHA256 signature."""
        json_body = json.dumps(payload, separators=(",", ":"))
        return hmac.new(SECRET_BYTES, json_body.encode(), hashlib.sha256).hexdigest()

    def _register_events(self):
        """Registers WebSocket event handlers."""
        @self.sio.event
        def connect():
            print("✅ Connected to WebSocket!")
            self.subscribe("coindcx")

        @self.sio.event
        def connect_error(data):
            print("❌ Connection failed:", data)

        @self.sio.event
        def disconnect():
            print("🔌 Disconnected from WebSocket. Retrying in 3 seconds...")
            time.sleep(3)
            self.connect()

        @self.sio.on("df-user-cross-position-details")
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

        @self.sio.on("*")
        def catch_all(event, data):
            print(f"🔥 Event: {event}, Data: {data}")

    def subscribe(self, channel_name: str):
        """Subscribes to a WebSocket channel."""
        body = {"channel": channel_name}
        signature = self._generate_signature(body)
        self.sio.emit("join", {
            "channelName": channel_name,
            "authSignature": signature,
            "apiKey": API_KEY
        })
        print(f"📡 Subscribed to {channel_name} WebSocket.")

    def connect(self):
        """Connects to the WebSocket server."""
        try:
            self.sio.connect(SOCKET_ENDPOINT, transports=["websocket"])
            self.sio.wait()
        except Exception as e:
            print("❌ WebSocket connection error:", str(e))

if __name__ == "__main__":
    ws_manager = WebSocketManager()
    ws_manager.connect()
