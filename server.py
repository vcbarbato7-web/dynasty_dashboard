# server.py  (same as before, minor tweak for Render)
from flask import Flask, jsonify, send_from_directory
import requests, json, time, threading, os

app = Flask(__name__, static_folder='static')

LEAGUE_ID = "1328112405992968192"
API_URL = f"https://api.flockfantasy.com/leagues/{LEAGUE_ID}"
CACHE_FILE = "cache.json"
CACHE_SECONDS = 43200

def refresh_cache():
    while True:
        try:
            res = requests.get(API_URL, timeout=10)
            data = res.json()
            with open(CACHE_FILE, "w") as f:
                json.dump({"timestamp": time.time(), "data": data}, f)
            print("Cache refreshed")
        except Exception as e:
            print(f"Fetch error: {e}")
        time.sleep(CACHE_SECONDS)

@app.route("/api/league")
def league():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return jsonify(json.load(f))
    try:
        data = requests.get(API_URL, timeout=10).json()
        return jsonify({"timestamp": time.time(), "data": data})
    except:
        return jsonify({"error": "Could not fetch data"}), 500

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    threading.Thread(target=refresh_cache, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
