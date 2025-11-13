# app.py
import os, json
from flask import Flask, jsonify
import redis

app = Flask(__name__)

REDIS_URL = os.environ.get("REDIS_URL")
REDIS_KEY = "sqfx:latest"

r = redis.from_url(REDIS_URL, decode_responses=True)

@app.route("/")
def home():
    return {
        "status": "ShadowQuantFX API Active",
        "note": "GET /prices for live data"
    }

@app.route("/prices")
def prices():
    raw = r.get(REDIS_KEY)
    if raw is None:
        return {"status": "waiting", "message": "no data yet"}, 200
    return json.loads(raw)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
