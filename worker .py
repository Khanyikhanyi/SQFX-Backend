# worker.py
import os
import time
import json
import logging
import threading

import yfinance as yf
import redis

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# CONFIG (use env or fallback)
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
FETCH_INTERVAL = int(os.environ.get("FETCH_INTERVAL", "15"))  # seconds

# Tickers to fetch (yfinance symbols)
FOREX = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCHF=X", "USDCAD=X"]
INDICES = ["^GSPC", "^NDX", "^IXIC"]  # S&P500, NASDAQ100 (NDX), Nasdaq Composite
ALL = FOREX + INDICES

# Redis key
REDIS_KEY = "sqfx:latest"

# Connect to Redis
r = redis.from_url(REDIS_URL, decode_responses=True)

def fetch_once():
    out = {"ts": time.time()}
    for sym in ALL:
        try:
            ticker = yf.Ticker(sym)
            # 1m history to get latest close. If empty, try fast info
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                price = float(data["Close"].iloc[-1])
            else:
                # fallback: try info->regularMarketPrice
                price = ticker.info.get("regularMarketPrice") or None
                if price is None:
                    price = "N/A"
            out[sym] = round(price, 6) if isinstance(price, (float,int)) else price
        except Exception as e:
            logging.exception("fetch error for %s", sym)
            out[sym] = "ERR"
    return out

def loop():
    logging.info("Worker started. REDIS_URL=%s FETCH_INTERVAL=%s", REDIS_URL, FETCH_INTERVAL)
    while True:
        try:
            data = fetch_once()
            # write JSON to Redis
            r.set(REDIS_KEY, json.dumps(data))
            logging.info("Updated: %s", data)
        except Exception as e:
            logging.exception("Worker loop error")
        time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    loop()