import React, { useState } from 'react';

function SolarPredictor() {
  const [duration, setDuration] = useState(1);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handlePredict = async () => {
    setLoading(true);
    try {
      
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration_hours: Number(duration) }),
      });
      
      const data = await response.json();
      
      setPrediction(data.prediction); 
    } catch (error) {
      console.error("Fetch error:", error);
      alert("Backend not reached. Check Flask server.");
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'sans-serif' }}>
      <h1>Solar Power Forecast</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <label>Enter Duration (Hours): </label>
        <input 
          type="number" 
          value={duration} 
          onChange={(e) => setDuration(e.target.value)}
          style={{ padding: '8px', width: '60px', marginLeft: '10px' }}
        />
      </div>

      <button 
        onClick={handlePredict} 
        disabled={loading}
        style={{ padding: '10px 20px', cursor: 'pointer', background: '#fbc02d', border: 'none', borderRadius: '4px' }}
      >
        {loading ? 'Fetching...' : 'Get Prediction'}
      </button>

      <hr style={{ margin: '30px 0' }} />

      {prediction !== null && (
        <div>
          <h3>Estimated Generation:</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2e7d32' }}>
            {prediction} <span style={{ fontSize: '1rem' }}>kW</span>
          </p>
        </div>
      )}
    </div>
  );
}

export default SolarPredictor;