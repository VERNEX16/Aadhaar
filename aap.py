from flask import Flask, request, jsonify
import requests
import json
import os
import secrets
from datetime import datetime, timedelta

app = Flask(__name__)

KEYS_FILE = "keys.json"

# Create keys.json automatically
if not os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, "w") as f:
        json.dump({}, f)

# Load keys
def load_keys():
    with open(KEYS_FILE, "r") as f:
        return json.load(f)

# Save keys
def save_keys(data):
    with open(KEYS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Validate API key
def validate_key(api_key):

    keys = load_keys()

    if api_key not in keys:
        return False

    expiry = datetime.fromisoformat(keys[api_key]["expiry"])

    # Remove expired keys
    if datetime.utcnow() > expiry:
        del keys[api_key]
        save_keys(keys)
        return False

    return True

# Generate Key
@app.route("/generate-key")
def generate_key():

    days = request.args.get("days", default=1, type=int)

    api_key = "vernex-day-" + secrets.token_hex(8)

    expiry = datetime.utcnow() + timedelta(days=days)

    keys = load_keys()

    keys[api_key] = {
        "expiry": expiry.isoformat()
    }

    save_keys(keys)

    return jsonify({
        "success": True,
        "owner": "VERNEX",
        "developer": "VERNEX",
        "api_key": api_key,
        "expires_at": expiry.isoformat(),
        "valid_days": days
    })

# Number API
@app.route("/api/number")
def number_lookup():

    api_key = request.args.get("key")
    number = request.args.get("num")

    if not api_key:
        return jsonify({
            "success": False,
            "error": "API Key Required"
        })

    if not validate_key(api_key):
        return jsonify({
            "success": False,
            "error": "Invalid or Expired API Key"
        })

    if not number:
        return jsonify({
            "success": False,
            "error": "Phone Number Required"
        })

    try:

        target_url = f"https://ft-osint-api.duckdns.org/api/number?key=ft-rahun2m&num={number}"

        response = requests.get(target_url)

        data = response.json()

        # Remove unwanted branding
        if isinstance(data, dict):

            data.pop("by", None)
            data.pop("channel", None)
            data.pop("cached", None)
            data.pop("cached_at", None)

        return jsonify({
            "success": True,
            "owner": "VERNEX",
            "developer": "VERNEX",
            "searched_number": number,
            "result": data
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })

# Vehicle API
@app.route("/api/vehicle")
def vehicle_lookup():

    api_key = request.args.get("key")
    rc = request.args.get("rc")

    if not api_key:
        return jsonify({
            "success": False,
            "error": "API Key Required"
        })

    if not validate_key(api_key):
        return jsonify({
            "success": False,
            "error": "Invalid or Expired API Key"
        })

    if not rc:
        return jsonify({
            "success": False,
            "error": "Vehicle Number Required"
        })

    try:

        target_url = f"https://vehicle-eight-vert.vercel.app/api?rc={rc}"

        response = requests.get(target_url)

        data = response.json()

        # Remove unwanted branding
        if isinstance(data, dict):

            data.pop("by", None)
            data.pop("channel", None)
            data.pop("cached", None)
            data.pop("cached_at", None)

        return jsonify({
            "success": True,
            "owner": "VERNEX",
            "developer": "VERNEX",
            "vehicle_number": rc,
            "result": data
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })

# Home Route
@app.route("/")
def home():
    return jsonify({
        "owner": "VERNEX",
        "developer": "VERNEX",
        "status": "ONLINE"
    })

# Run Server
if __name__ == "__main__":
    app.run(debug=True)
