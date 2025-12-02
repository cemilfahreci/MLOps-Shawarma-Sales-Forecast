import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Forecast = ({ refreshTrigger }) => {
    const [forecast, setForecast] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchForecast();
    }, [refreshTrigger]);

    const fetchForecast = async () => {
        try {
            const response = await axios.get('http://localhost:8000/forecast/tomorrow');
            if (response.data.error) {
                setError(response.data.error);
                setForecast(null);
            } else {
                setForecast(response.data);
                setError(null);
            }
        } catch (err) {
            console.error("Forecast error:", err);
            setError("Model not trained or server error.");
            setForecast(null);
        }
    };

    return (
        <div style={{ border: '1px solid black', padding: '10px', maxWidth: '600px' }}>
            {error ? (
                <div style={{ color: 'red', fontWeight: 'bold' }}>
                    Error: {error}
                </div>
            ) : forecast ? (
                <div>
                    <h4>{forecast.date ? `Forecast for ${forecast.date}` : "Tomorrow's Forecast"}</h4>
                    <p><strong>Total Predicted:</strong> {forecast.total_predicted_quantity}</p>

                    <table border="1" cellPadding="5" style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ backgroundColor: '#eee' }}>
                                <th>Product</th>
                                <th>Size</th>
                                <th>Qty</th>
                            </tr>
                        </thead>
                        <tbody>
                            {forecast.breakdown && forecast.breakdown.map((item, index) => (
                                <tr key={index}>
                                    <td>{item.product_name}</td>
                                    <td>{item.size}</td>
                                    <td style={{ textAlign: 'right' }}>{item.predicted_quantity}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    <div style={{ marginTop: '15px', borderTop: '1px solid black', paddingTop: '10px' }}>
                        <strong>Model Version:</strong> {forecast.model_version} <br />
                        <strong>MAE (Error Margin):</strong> {forecast.mae ? forecast.mae.toFixed(4) : '0'}
                    </div>
                </div>
            ) : (
                <div>Loading forecast...</div>
            )}
        </div>
    );
};

export default Forecast;
