
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

model = joblib.load(MODEL_PATH)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

SYSTEM_LOSS = 0.15

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
    hourly = data["hourly"]

    times = hourly["time"]
    now_hour = datetime.now().strftime("%Y-%m-%dT%H:00")
    idx = times.index(now_hour) if now_hour in times else 0

    return {
        "temperature": hourly["temperature_2m"][idx],
        "direct": hourly["direct_normal_irradiance"][idx],
        "diffuse": hourly["diffuse_radiation"][idx]
    }

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "backend alive"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    lat = data.get("latitude")
    lon = data.get("longitude")

    if lat is None or lon is None:
        return jsonify({"error": "latitude and longitude required"}), 400

    lat = float(lat)
    lon = float(lon)

    weather = get_current_weather(lat, lon)

    direct_raw = weather["direct"]
    diffuse_raw = weather["diffuse"]
    temperature = weather["temperature"]

    direct_norm = direct_raw / 1000.0
    diffuse_norm = diffuse_raw / 1000.0

    X = np.array([[direct_norm, diffuse_norm, temperature]])

    raw_prediction = float(model.predict(X)[0])
    power_fraction = max(0.0, min(1.0, raw_prediction))
    effective_power_fraction = power_fraction * (1 - SYSTEM_LOSS)

    return jsonify({
        "inputs": {
            "temperature_c": temperature,
            "direct_irradiance_wm2": direct_raw,
            "diffuse_irradiance_wm2": diffuse_raw
        },
        "raw_model_output": raw_prediction,
        "power_fraction": power_fraction,
        "effective_power_fraction": effective_power_fraction
    })

if __name__ == "__main__":
    app.run(debug=True)
