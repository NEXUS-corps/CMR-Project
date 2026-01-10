import { useState, useEffect } from "react";
import "./App.css";

/* ---------- BAR SUMMARY (UNCHANGED) ---------- */
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

/* ---------- LINE CHART WITH TRUE HOUR AXIS ---------- */
const LineChartWithAxes = ({ data, color, yLabel }) => {
  const n = data.length;
  const maxY = Math.max(...data, 1);

  const pad = 12;
  const W = 100 - pad * 2;
  const H = 100 - pad * 2;

  const points = data.map((v, i) => {
    const x = pad + (i / (n - 1)) * W;
    const y = pad + H - (v / maxY) * H;
    return `${x},${y}`;
  }).join(" ");

  return (
    <svg viewBox="0 0 100 100" className="line-chart">
      {/* Grid + axes */}
      <line x1={pad} y1={pad} x2={pad} y2={pad + H} />
      <line x1={pad} y1={pad + H} x2={pad + W} y2={pad + H} />

      {/* Y-axis ticks */}
      {[0, 0.5, 1].map((t, i) => {
        const y = pad + H - t * H;
        return (
          <g key={i}>
            <line x1={pad - 1} y1={y} x2={pad} y2={y} />
            <text x={pad - 2} y={y + 1.5} textAnchor="end">
              {(t * maxY).toFixed(1)}
            </text>
          </g>
        );
      })}

      {/* X-axis ticks: ONE PER HOUR */}
      {data.map((_, i) => {
        const x = pad + (i / (n - 1)) * W;
        return (
          <g key={i}>
            <line x1={x} y1={pad + H} x2={x} y2={pad + H + 1} />
            <text x={x} y={pad + H + 6} textAnchor="middle">
              H{i + 1}
            </text>
          </g>
        );
      })}

      {/* Line */}
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="2"
        points={points}
      />

      {/* Title */}
      <text x="50" y="6" textAnchor="middle">
        {yLabel}
      </text>
    </svg>
  );
};

/* ---------- MAIN APP ---------- */
function App() {
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

  const update = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const predict = async () => {
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
    }
  };

  return (
    <div className="dashboard fade-in">
      <header className="topbar">Solar Energy Dashboard</header>

      <div className="layout">
        <div className="panel input">
          <input name="latitude" placeholder="Latitude" onChange={update} />
          <input name="longitude" placeholder="Longitude" onChange={update} />
          <input name="maxGridPower" placeholder="Max Grid Power (kW)" onChange={update} />
          <input name="maxBattery" placeholder="Max Battery (kWh)" onChange={update} />
          <input name="currentBattery" placeholder="Current Battery (kWh)" onChange={update} />
          <input name="consumption" placeholder="Consumption / hr (kWh)" onChange={update} />
          <input name="duration" placeholder="Duration (hours)" onChange={update} />

          <button onClick={predict}>Run Simulation</button>
          {error && <div className="error">{error}</div>}
        </div>

        <div className="panel output">
          {result && (
            <>
              <EnergyPlot data={result} />

              <LineChartWithAxes
                data={result.hourly_generated_energy}
                yLabel="Hourly Energy (kWh)"
                color="#38bdf8"
              />

              <LineChartWithAxes
                data={result.hourly_battery_level}
                yLabel="Battery Level (kWh)"
                color="#22c55e"
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
