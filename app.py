from flask import Flask, jsonify
import yfinance as yf
import threading, time
import os

app = Flask(__name__)

# Assets we will fetch
assets = {
    "Forex": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X", "USDCAD=X"],
    "Indices": ["^GSPC", "^IXIC"]  # S&P 500, NASDAQ
}

latest_data = {}

def fetch_loop():
    while True:
        print("Fetching live data...")
        for category, syms in assets.items():
            for sym in syms:
                try:
                    ticker = yf.Ticker(sym)
                    data = ticker.history(period="1d", interval="1m")
                    if not data.empty:
                        latest_data[sym] = round(float(data["Close"].iloc[-1]), 5)
                    else:
                        latest_data[sym] = "N/A"
                except Exception as e:
                    latest_data[sym] = f"ERR"
        print("Updated:", latest_data)
        time.sleep(30)  # refresh interval

threading.Thread(target=fetch_loop, daemon=True).start()

@app.route("/")
def home():
    return {
        "status": "ShadowQuantFX API Active",
        "assets": list(latest_data.keys())
    }

@app.route("/prices")
def prices():
    return latest_data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)