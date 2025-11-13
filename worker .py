# worker.py
import os, time, json, logging
import yfinance as yf
import redis

logging.basicConfig(level=logging.INFO)

REDIS_URL = os.environ.get("REDIS_URL")
FETCH_INTERVAL = 15  # seconds
REDIS_KEY = "sqfx:latest"

FOREX = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCHF=X", "USDCAD=X"]
INDICES = ["^GSPC", "^NDX", "^IXIC"]
ALL = FOREX + INDICES

r = redis.from_url(REDIS_URL, decode_responses=True)

def fetch_once():
    out = {"ts": time.time()}
    for sym in ALL:
        try:
            ticker = yf.Ticker(sym)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                price = float(data["Close"].iloc[-1])
            else:
                price = None
            out[sym] = price
        except:
            out[sym] = None
    return out

while True:
    data = fetch_once()
    r.set(REDIS_KEY, json.dumps(data))
    logging.info(f"Updated: {data}")
    time.sleep(FETCH_INTERVAL)
