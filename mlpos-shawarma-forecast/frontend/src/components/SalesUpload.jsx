import React, { useState } from 'react';
import axios from 'axios';

const SalesUpload = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState('');

    const handleFileChange = (e) => {
        if (e.target.files) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setMessage('Uploading and training...');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:8000/sales/import-csv', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            setMessage(`Success: ${response.data.message} `);
            setFile(null);
            // Reset file input manually if needed, or just let it be
            if (onUploadSuccess) onUploadSuccess();
        } catch (error) {
            console.error("Upload failed:", error);
            const errorMsg = error.response?.data?.detail || "Upload failed";
            setMessage(`Error: ${errorMsg} `);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div style={{ border: '1px solid black', padding: '10px', width: '300px' }}>
            <input type="file" accept=".csv" onChange={handleFileChange} />
            <br /><br />
            <button
                onClick={handleUpload}
                disabled={!file || uploading}
            >
                {uploading ? 'Processing...' : 'Upload CSV'}
            </button>
            <br />
            <small>{message}</small>
        </div>
    );
};

export default SalesUpload;
