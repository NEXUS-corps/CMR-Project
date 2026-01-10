
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

    required = [
        "latitude",
        "longitude",
        "max_grid_power",
        "max_battery_capacity",
        "current_battery_capacity",
        "energy_consumption"
    ]

    for key in required:
        if key not in data:
            return jsonify({"error": f"{key} is required"}), 400

    lat = float(data["latitude"])
    lon = float(data["longitude"])
    max_grid_power = float(data["max_grid_power"])
    max_battery_capacity = float(data["max_battery_capacity"])
    current_battery_capacity = float(data["current_battery_capacity"])
    energy_consumption = float(data["energy_consumption"])

    weather = get_current_weather(lat, lon)

    direct_norm = weather["direct"] / 1000.0
    diffuse_norm = weather["diffuse"] / 1000.0
    temperature = weather["temperature"]

    X = np.array([[direct_norm, diffuse_norm, temperature]])

    raw_prediction = float(model.predict(X)[0])
    power_fraction = max(0.0, min(1.0, raw_prediction))
    effective_power_fraction = power_fraction * (1 - SYSTEM_LOSS)

    generated_power = effective_power_fraction * max_grid_power
    net_power = generated_power - energy_consumption

    energy_to_battery = 0.0
    energy_from_battery = 0.0
    unmet_energy = 0.0
    status_message = "Battery idle"

    if net_power > 0:
        available_space = max_battery_capacity - current_battery_capacity
        energy_to_battery = min(net_power, available_space)
        current_battery_capacity += energy_to_battery

        if energy_to_battery > 0:
            status_message = f"{energy_to_battery:.2f} kWh can be stored in battery"
        else:
            status_message = "Battery full, excess energy cannot be stored"

    elif net_power < 0:
        required_energy = abs(net_power)
        energy_from_battery = min(required_energy, current_battery_capacity)
        current_battery_capacity -= energy_from_battery
        unmet_energy = required_energy - energy_from_battery

        if energy_from_battery > 0:
            status_message = f"{energy_from_battery:.2f} kWh must be discharged from battery"
        else:
            status_message = "Battery empty, unable to meet demand"

    current_battery_capacity = max(
        0.0,
        min(current_battery_capacity, max_battery_capacity)
    )

    battery_percentage = (
        current_battery_capacity / max_battery_capacity
        if max_battery_capacity > 0 else 0.0
    )

    return jsonify({
        "generated_power": generated_power,
        "effective_power_fraction": effective_power_fraction,
        "battery": {
            "current_capacity": current_battery_capacity,
            "max_capacity": max_battery_capacity,
            "percentage": battery_percentage,
            "energy_to_battery": energy_to_battery,
            "energy_from_battery": energy_from_battery,
            "unmet_energy": unmet_energy,
            "status_message": status_message
        }
    })


if __name__ == "__main__":
    app.run(debug=True)
