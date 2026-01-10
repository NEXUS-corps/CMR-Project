import { useState, useEffect } from "react";
import "./App.css";

const EnergyPlot = ({ data }) => {
  const items = [
    { label: "Generated", value: data.total_energy_generated, color: "#38bdf8" },
    { label: "Stored", value: data.battery.energy_to_battery, color: "#22c55e" },
    { label: "Used", value: data.battery.energy_from_battery, color: "#f97316" },
    { label: "Unmet", value: data.battery.unmet_energy, color: "#ef4444" }
  ];

  const max = Math.max(...items.map(i => i.value), 1);

  return (
    <div className="plot">
      {items.map((item, i) => (
        <div key={i} className="bar-row">
          <span>{item.label}</span>
          <div className="bar-track">
            <div
              className="bar-fill"
              style={{
                width: `${(item.value / max) * 100}%`,
                background: item.color
              }}
            />
          </div>
          <strong>{item.value.toFixed(2)} kWh</strong>
        </div>
      ))}
    </div>
  );
};

function App() {
  const [showWelcome, setShowWelcome] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setShowWelcome(false), 2000);
    return () => clearTimeout(t);
  }, []);

  const [form, setForm] = useState({
    latitude: "",
    longitude: "",
    maxGridPower: "",
    maxBattery: "",
    currentBattery: "",
    consumption: "",
    duration: ""
  });

  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const update = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const predict = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          latitude: Number(form.latitude),
          longitude: Number(form.longitude),
          max_grid_power: Number(form.maxGridPower),
          max_battery_capacity: Number(form.maxBattery),
          current_battery_capacity: Number(form.currentBattery),
          energy_consumption: Number(form.consumption),
          duration_hours: Number(form.duration)
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Request failed");
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (showWelcome) {
    return (
      <div className="welcome">
        <div className="welcome-box">
          <h1>Solar Energy Dashboard</h1>
          <p>Initializing system intelligence…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard fade-in">
      <header className="topbar">Solar Energy Dashboard</header>

      <div className="layout">
        <div className="panel input slide-in-left">
          <h2>System Inputs</h2>

          <input name="latitude" placeholder="Latitude" onChange={update} />
          <input name="longitude" placeholder="Longitude" onChange={update} />
          <input name="maxGridPower" placeholder="Max Grid Power (kW)" onChange={update} />
          <input name="maxBattery" placeholder="Max Battery Capacity (kWh)" onChange={update} />
          <input name="currentBattery" placeholder="Current Battery (kWh)" onChange={update} />
          <input name="consumption" placeholder="Consumption per Hour (kWh)" onChange={update} />
          <input name="duration" placeholder="Duration (hours)" onChange={update} />

          <button onClick={predict} disabled={loading}>
            {loading ? "Simulating…" : "Run Simulation"}
          </button>

          {error && <div className="error">{error}</div>}
        </div>

        <div className="panel output slide-in-right">
          <h2>System Status</h2>

          {!result && <div className="placeholder">Awaiting input</div>}

          {result && (
            <>
              <div className="stat big">
                <span>Total Energy Generated</span>
                <strong>{result.total_energy_generated.toFixed(2)} kWh</strong>
              </div>

              <div className="stat">
                <span>Battery Level</span>
                <strong>{(result.battery.percentage * 100).toFixed(1)}%</strong>
              </div>

              <div className="stat">
                <span>Status</span>
                <strong>{result.battery.status_message}</strong>
              </div>

              <div className="grid">
                <div>
                  <span>Stored</span>
                  <strong>{result.battery.energy_to_battery.toFixed(2)} kWh</strong>
                </div>
                <div>
                  <span>Used</span>
                  <strong>{result.battery.energy_from_battery.toFixed(2)} kWh</strong>
                </div>
                <div>
                  <span>Unmet</span>
                  <strong>{result.battery.unmet_energy.toFixed(2)} kWh</strong>
                </div>
              </div>

              <EnergyPlot data={result} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
