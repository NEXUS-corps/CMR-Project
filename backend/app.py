
from flask import Flask, request, jsonify
from flask_cors import CORS

from dotenv import load_dotenv
from services.weather_service import get_live_weather
import joblib
import numpy as np


load_dotenv()


app = Flask(__name__)
CORS(app) 


# Load trained model
model = joblib.load("model.pkl")

# Input: 3 features
X = np.array([[x1, x2, x3]])

output = model.predict(X)

print("Model output:", output[0])



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
