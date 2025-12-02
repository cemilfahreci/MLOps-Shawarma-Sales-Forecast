import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Dashboard = ({ refreshTrigger }) => {
    const [forecast, setForecast] = useState(0);

    useEffect(() => {
        fetchForecast();
    }, [refreshTrigger]);

    const fetchForecast = async () => {
        try {
            const response = await axios.get('http://localhost:8000/forecast/tomorrow');
            setForecast(response.data.total_predicted_quantity || 0);
        } catch (error) {
            console.error("Error fetching forecast:", error);
        }
    };

    return (
        <div style={{ border: '1px solid black', padding: '10px', width: '200px' }}>
            <strong>Tomorrow's Prediction:</strong>
            <br />
            <span style={{ fontSize: '24px' }}>{forecast.toLocaleString()}</span> items
        </div>
    );
};

export default Dashboard;
