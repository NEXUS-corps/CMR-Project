
from flask import Flask, request, jsonify
from flask_cors import CORS

from dotenv import load_dotenv
from services.weather_service import get_live_weather

load_dotenv()


app = Flask(__name__)
CORS(app) 

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "backend alive"})
a = 6
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    a = 7
    location = data.get("location")
    duration = data.get("duration")

    if not location or not duration:
        return jsonify({"error": "location and duration required"}), 400


    result = {
        "location": location,
        "duration": duration,
        "predicted_energy": 0.0
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)