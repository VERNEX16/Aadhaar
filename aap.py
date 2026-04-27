from flask import Flask, request, jsonify
import requests, uuid, json, time, os

app = Flask(__name__)

DB_FILE = "keys.json"

# -------- LOAD / SAVE --------
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

# -------- CREATE KEY --------
def create_key(days):
    key = "VRX-" + uuid.uuid4().hex[:10]

    expiry = None if days == 0 else int(time.time()) + days * 86400

    db = load_db()
    db[key] = {"expiry": expiry}
    save_db(db)

    return key

# -------- CHECK KEY --------
def check_key(key):
    db = load_db()

    if key not in db:
        return False, "Invalid key"

    expiry = db[key]["expiry"]

    if expiry is None:
        return True, "Lifetime key"

    if time.time() > expiry:
        return False, "Key expired"

    return True, "Valid key"

# -------- CLEAN RESPONSE --------
REMOVE_KEYS = ["owner", "dm", "contact", "telegram", "whatsapp", "message", "by"]

def clean_data(data):
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items() if k not in REMOVE_KEYS}
    elif isinstance(data, list):
        return [clean_data(i) for i in data]
    return data

# -------- HOME --------
@app.route("/")
def home():
    return "VERNEX API WITH KEY SYSTEM 🚀"

# -------- ADMIN: GENERATE KEY --------
@app.route("/admin/generate")
def generate():
    admin = request.args.get("admin")
    days = int(request.args.get("days", 1))

    if admin != "VERNEX-ADMIN":
        return jsonify({"status": "error", "message": "Unauthorized"})

    key = create_key(days)

    return jsonify({
        "status": "success",
        "key": key,
        "valid_days": "lifetime" if days == 0 else days
    })

# -------- API --------
@app.route("/api/adharfamily")
def adharfamily():
    key = request.args.get("key")
    num = request.args.get("num")

    valid, msg = check_key(key)

    if not valid:
        return jsonify({"status": "error", "message": msg, "powered_by": "VERNEX"}), 403

    try:
        res = requests.get(
            "https://ft-osint-api.duckdns.org/api/adharfamily",
            params={"key": "ft-key-tr-jzynhifn87aq", "num": num},
            timeout=10
        )

        data = clean_data(res.json())
        data["powered_by"] = "VERNEX"

        return jsonify(data)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
