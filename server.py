from flask import Flask, jsonify, send_from_directory
import requests, json, time, threading, os

app = Flask(__name__, static_folder='static')

LEAGUE_ID = "1328112405992968192"
API_URL = f"https://api.flockfantasy.com/user/league/calculate?creatorId=EXPERT&isDraft=false&leagueId={LEAGUE_ID}"
LOGIN_URL = "https://api.flockfantasy.com/auth/login"
CACHE_FILE = "cache.json"
CACHE_SECONDS = 3600

EMAIL = os.environ.get("FLOCK_EMAIL")
PASSWORD = os.environ.get("FLOCK_PASSWORD")

def get_token():
    res = requests.post(LOGIN_URL, json={
        "username": EMAIL,
        "password": PASSWORD
    }, timeout=10)
    return res.json()["accessToken"]

def refresh_cache():
    while True:
        try:
            token = get_token()
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(API_URL, headers=headers, timeout=10)
            data = res.json()
            with open(CACHE_FILE, "w") as f:
                json.dump({"timestamp": time.time(), "data": data}, f)
            print("Cache refreshed successfully")
        except Exception as e:
            print(f"Fetch error: {e}")
        time.sleep(CACHE_SECONDS)

@app.route("/api/league")
def league():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return jsonify(json.load(f))
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        data = requests.get(API_URL, headers=headers, timeout=10).json()
        return jsonify({"timestamp": time.time(), "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    threading.Thread(target=refresh_cache, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
