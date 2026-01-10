import { useState } from "react";
import "./App.css";

function App() {
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const predict = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          latitude: Number(latitude),
          longitude: Number(longitude),
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Prediction failed");
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="card">
        <h1>Solar Power Prediction</h1>

        <div className="field">
          <label>Latitude</label>
          <input
            type="number"
            value={latitude}
            onChange={(e) => setLatitude(e.target.value)}
            placeholder="e.g. 12.97"
          />
        </div>

        <div className="field">
          <label>Longitude</label>
          <input
            type="number"
            value={longitude}
            onChange={(e) => setLongitude(e.target.value)}
            placeholder="e.g. 77.59"
          />
        </div>

        <button onClick={predict} disabled={loading}>
          {loading ? "Predicting…" : "Predict"}
        </button>

        {error && <div className="error">{error}</div>}

        {result && (
          <div className="result">
            <div className="metric">
              <span>Effective Power Fraction</span>
              <strong>
                {(result.effective_power_fraction * 100).toFixed(2)}%
              </strong>
            </div>

            <div className="details">
              <div>Temperature: {result.inputs.temperature_c} °C</div>
              <div>Direct Irradiance: {result.inputs.direct_irradiance_wm2} W/m²</div>
              <div>Diffuse Irradiance: {result.inputs.diffuse_irradiance_wm2} W/m²</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
