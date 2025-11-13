# app.py
import os
import json
import logging
from flask import Flask, jsonify
import redis

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
REDIS_KEY = os.environ.get("REDIS_KEY", "sqfx:latest")
r = redis.from_url(REDIS_URL, decode_responses=True)

@app.route("/")
def home():
    return {"status": "ShadowQuantFX API Active", "note": "GET /prices for latest snapshot"}

@app.route("/prices")
def prices():
    raw = r.get(REDIS_KEY)
    if not raw:
        return jsonify({"status": "ok", "message": "no data yet"}), 200
    try:
        data = json.loads(raw)
    except Exception:
        # if something odd, return raw
        return jsonify({"status": "ok", "data_raw": raw})
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
