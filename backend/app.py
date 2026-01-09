from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

# -------------------------------------------------
# Load ML model safely
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load model.pkl: {e}")

# -------------------------------------------------
# Open-Meteo base URL (NO query params here)
# -------------------------------------------------
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def get_current_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,direct_normal_irradiance,diffuse_radiation",
        "timezone": "auto"
    }

    response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    # Defensive check (important)
    if "hourly" not in data or not isinstance(data["hourly"], dict):
        raise RuntimeError(f"Unexpected API response: {data}")

    hourly = data["hourly"]

    times = hourly["time"]
    now_hour = datetime.now().strftime("%Y-%m-%dT%H:00")
    idx = times.index(now_hour) if now_hour in times else 0

    return {
        "temperature": hourly["temperature_2m"][idx],          # °C
        "direct": hourly["direct_normal_irradiance"][idx],     # W/m²
        "diffuse": hourly["diffuse_radiation"][idx]            # W/m²
    }

# -------------------------------------------------
# Health check
# -------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "backend alive"})

# -------------------------------------------------
# Predict endpoint (LIVE WEATHER → ML)
# Feature order (LOCKED):
# [direct_norm, diffuse_norm, temperature]
# -------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    lat = data.get("latitude")
    lon = data.get("longitude")

    if lat is None or lon is None:
        return jsonify({"error": "latitude and longitude required"}), 400

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return jsonify({"error": "latitude and longitude must be numeric"}), 400

    try:
        # 1️⃣ Fetch live weather
        weather = get_current_weather(lat, lon)

        direct_raw = weather["direct"]
        diffuse_raw = weather["diffuse"]
        temperature = weather["temperature"]

        # 2️⃣ Normalize irradiance (same as training)
        direct_norm = direct_raw / 1000.0
        diffuse_norm = diffuse_raw / 1000.0

        # 3️⃣ Build feature vector
        X = np.array([[
            direct_norm,
            diffuse_norm,
            temperature
        ]])

        # 4️⃣ Predict
        raw_prediction = float(model.predict(X)[0])

        # 5️⃣ Enforce physical constraint
        power_fraction = max(0.0, min(1.0, raw_prediction))

        return jsonify({
            "inputs": {
                "temperature_c": temperature,
                "direct_irradiance_wm2": direct_raw,
                "diffuse_irradiance_wm2": diffuse_raw
            },
            "raw_model_output": raw_prediction,
            "power_fraction": power_fraction
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
