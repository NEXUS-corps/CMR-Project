import React from 'react';

function ResultCard({ result }) {
    return (
        <div className="card result-card">
            <h2 style={{ color: 'var(--neon-yellow)', marginBottom: '1rem' }}>Forecast</h2>

            <div className="energy-value">
                {result.energy_kwh}
                <span className="unit"> kWh</span>
            </div>

            <p style={{ color: 'var(--text-secondary)' }}>
                Estimated energy consumption for the next hour based on current weather conditions.
            </p>
        </div>
    );
}

export default ResultCard;
