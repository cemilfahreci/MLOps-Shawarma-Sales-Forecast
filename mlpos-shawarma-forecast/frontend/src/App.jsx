import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import Forecast from './components/Forecast';
import SalesUpload from './components/SalesUpload';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div style={{ fontFamily: 'Times New Roman, serif', padding: '20px' }}>
      <h1>Shawarma MLOps</h1>
      <hr />
      <br />

      <div style={{ marginBottom: '20px' }}>
        <h3>1. Data Upload</h3>
        <SalesUpload onUploadSuccess={handleRefresh} />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>2. Summary</h3>
        <Dashboard refreshTrigger={refreshTrigger} />
      </div>

      <div>
        <h3>3. Forecast</h3>
        <Forecast refreshTrigger={refreshTrigger} />
      </div>
    </div>
  );
}

export default App;
