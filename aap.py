from flask import Flask, request, jsonify
import requests
import sqlite3
import time
import random
import string

app = Flask(__name__)

# 🔗 BACKEND API
BACKEND_URL = "https://mean-folders-athletic-divide.trycloudflare.com/search/number"
BACKEND_KEY = "Mauryaji12"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            key TEXT PRIMARY KEY,
            expiry REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- KEY SYSTEM ----------------
def generate_key(days):
    key = "VERNX-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    expiry = time.time() + (days * 86400)

    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("INSERT INTO keys VALUES (?, ?)", (key, expiry))
    conn.commit()
    conn.close()

    return key, expiry

def is_valid(key):
    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("SELECT expiry FROM keys WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()

    if not row:
        return False

    return time.time() < row[0]

# ---------------- CLEAN FUNCTION ----------------
def clean_data(data):
    remove_keys = ["owner", "developer", "branding", "processed_by"]

    if isinstance(data, dict):
        return {
            k: clean_data(v)
            for k, v in data.items()
            if k not in remove_keys
        }
    elif isinstance(data, list):
        return [clean_data(i) for i in data]

    return data

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return "VERNX API LIVE 🚀"

# 🔑 GENERATE KEY (ANY DAYS)
@app.route("/generate")
def generate():
    plan = request.args.get("plan")

    try:
        if plan.endswith("d"):
            days = int(plan[:-1])
        else:
            return jsonify({"error": "Use format like 4d, 10d"})

        key, expiry = generate_key(days)

        return jsonify({
            "key": key,
            "valid_days": days,
            "expires_at": expiry
        })

    except:
        return jsonify({"error": "Invalid input"})

# 📞 MAIN API
@app.route("/api/numinfo")
def numinfo():
    num = request.args.get("num")
    key = request.args.get("key")

    if not num:
        return jsonify({"error": "Number required"})

    if not is_valid(key):
        return jsonify({"error": "Invalid or expired key"})

    try:
        # 🔥 CALL BACKEND
        res = requests.get(BACKEND_URL, params={
            "key": BACKEND_KEY,
            "number": num
        }, timeout=10)

        raw = res.json()

        # 🧹 CLEAN DATA
        data = clean_data(raw)

        # ✅ ADD YOUR NAME
        data["owner"] = "VERNX"

        return jsonify(data)

    except Exception as e:
        return jsonify({
            "error": "Backend failed",
            "details": str(e)
        })

if __name__ == "__main__":
    app.run()
