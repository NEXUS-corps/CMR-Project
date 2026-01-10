from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

model = joblib.load(MODEL_PATH)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
SYSTEM_LOSS = 0.15


def get_hourly_weather(lat, lon, hours):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,direct_normal_irradiance,diffuse_radiation",
        "timezone": "auto"
    }

    res = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    res.raise_for_status()

    hourly = res.json()["hourly"]
    times = hourly["time"]

    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    now_str = now.strftime("%Y-%m-%dT%H:00")
    start_idx = times.index(now_str) if now_str in times else 0

    weather = []
    labels = []

    for i in range(start_idx, start_idx + hours):
        weather.append({
            "temperature": hourly["temperature_2m"][i],
            "direct": hourly["direct_normal_irradiance"][i],
            "diffuse": hourly["diffuse_radiation"][i]
        })
        labels.append((now + timedelta(hours=len(labels))).strftime("%H:%M"))

    return weather, labels


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    required = [
        "latitude",
        "longitude",
        "max_grid_power",
        "max_battery_capacity",
        "current_battery_capacity",
        "energy_consumption",
        "duration_hours"
    ]

    for r in required:
        if r not in data:
            return jsonify({"error": f"{r} missing"}), 400

    lat = float(data["latitude"])
    lon = float(data["longitude"])
    max_grid_power = float(data["max_grid_power"])
    max_battery_capacity = float(data["max_battery_capacity"])
    current_battery_capacity = float(data["current_battery_capacity"])
    energy_consumption = float(data["energy_consumption"])
    duration_hours = int(data["duration_hours"])

    weather_hours, labels = get_hourly_weather(lat, lon, duration_hours)

    total_energy_generated = 0.0
    energy_to_battery = 0.0
    energy_from_battery = 0.0
    unmet_energy = 0.0

    hourly_generated = []
    hourly_battery = []

    for hour in weather_hours:
        X = np.array([[
            hour["direct"] / 1000.0,
            hour["diffuse"] / 1000.0,
            hour["temperature"]
        ]])

        fraction = float(model.predict(X)[0])
        fraction = max(0.0, min(1.0, fraction))
        fraction *= (1 - SYSTEM_LOSS)

        generated_energy = fraction * max_grid_power
        total_energy_generated += generated_energy
        hourly_generated.append(generated_energy)

        net = generated_energy - energy_consumption

        if net > 0:
            space = max_battery_capacity - current_battery_capacity
            stored = min(net, space)
            current_battery_capacity += stored
            energy_to_battery += stored
        else:
            needed = abs(net)
            drawn = min(needed, current_battery_capacity)
            current_battery_capacity -= drawn
            energy_from_battery += drawn
            unmet_energy += needed - drawn

        current_battery_capacity = max(
            0.0, min(current_battery_capacity, max_battery_capacity)
        )

        hourly_battery.append(current_battery_capacity)

    battery_percentage = (
        current_battery_capacity / max_battery_capacity
        if max_battery_capacity > 0 else 0.0
    )

    return jsonify({
        "duration_hours": duration_hours,
        "total_energy_generated": total_energy_generated,
        "hour_labels": labels,
        "hourly_generated_energy": hourly_generated,
        "hourly_battery_level": hourly_battery,
        "battery": {
            "current_capacity": current_battery_capacity,
            "max_capacity": max_battery_capacity,
            "percentage": battery_percentage,
            "energy_to_battery": energy_to_battery,
            "energy_from_battery": energy_from_battery,
            "unmet_energy": unmet_energy,
            "status_message": "Simulation completed"
        }
    })


if __name__ == "__main__":
    app.run(debug=True)
