
## 📖 Project Overview

This project is a complete **MLOps (Machine Learning Operations)** solution designed to solve the "production planning" problem in the food industry. It predicts daily sales for a Doner Kebab restaurant chain to minimize food waste and prevent stockouts.

Unlike static ML models, this system implements a **Continuous Training (CT)** pipeline. As new sales data is ingested, the system automatically retrains the model, versions it, and deploys the best-performing version for production.

---

## 🏗️ Architecture & MLOps Pipeline

The system follows an **Event-Driven Architecture**:

1.  **Data Ingestion:** Sales data (CSV) is uploaded via the React Frontend.
2.  **Validation:** Data is validated using Pydantic schemas.
3.  **Storage:** Validated data is stored in **PostgreSQL** (Single Source of Truth).
4.  **Trigger:** A data commit triggers the **Training Pipeline**.
5.  **Training:**
    *   Feature Engineering (Date -> Year, Month, Weekday, Seasonality).
    *   Model Training (Random Forest Regressor).
    *   Evaluation (Train/Test Split, MAE Calculation).
6.  **Model Registry:** The trained model is saved as an artifact (`.pkl`) and registered in the database with its metadata (Version, MAE, Timestamp).
7.  **Serving:** The **FastAPI** backend serves the latest active model to predict tomorrow's sales.

---

## 🛠️ Tech Stack

### Backend (Python)
*   **FastAPI:** High-performance async web framework.
*   **SQLAlchemy (Async):** ORM for database interactions.
*   **Scikit-Learn:** Machine Learning (Random Forest).
*   **Pandas:** Data manipulation and feature engineering.
*   **Joblib:** Model serialization.

### Frontend (JavaScript)
*   **React:** UI Library.
*   **Vite:** Next Generation Frontend Tooling.
*   **TailwindCSS:** Utility-first CSS framework.
*   **Axios:** HTTP Client.

### Database
*   **PostgreSQL:** Relational database for sales data and model registry.

---

## 🚀 Installation & Setup

### Prerequisites
*   Python 3.9+
*   Node.js 16+
*   PostgreSQL

### 1. Backend Setup
```bash
cd mlpos-shawarma-forecast/backend
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd mlpos-shawarma-forecast/frontend
# Install dependencies
npm install

# Run the development server
npm run dev
```

The UI will be available at `http://localhost:5173`.

---

## 📊 Usage Guide

1.  **Upload Data:** Go to the dashboard and upload historical sales CSV files (e.g., `2022`, `2023`).
2.  **Automatic Training:** The system will automatically train a new model version (e.g., `v1`).
3.  **View Forecast:** The dashboard will display the sales forecast for **Tomorrow**, including the breakdown by Product and Size.
4.  **Monitor Performance:** Check the **MAE (Mean Absolute Error)** displayed on the dashboard to see the model's reliability.

---

## 🧠 Key Features

*   **Cumulative Learning:** The model never forgets. New data is appended to the history, allowing the model to learn long-term trends (e.g., yearly growth).
*   **Drift Adaptation:** Includes "Year" and "Seasonality" features to adapt to Concept Drift (inflation, changing popularity).
*   **Model Versioning:** Every training run is versioned. You can track the performance history of `v1`, `v2`, `v3`...
*   **Real-Time Serving:** Predictions are generated instantly via REST API.

---

## 🧠 How It Works (Prediction Logic)

The model doesn't just memorize numbers; it learns **patterns**. Here are the key features it uses to make predictions:

1.  **📅 Seasonality (Month):**
    *   **Winter (Dec-Feb):** Sales drop by ~20% (Low season).
    *   **Summer (Jun-Aug):** Sales increase by ~40% (High season).
    *   *Example:* A prediction for December will be lower than November, even if recent sales were high.

2.  **📈 Yearly Trend (Year):**
    *   The model learns that the business grows by **~10% every year**.
    *   *Example:* A sale in 2025 will be predicted higher than the same day in 2022.

3.  **🎉 Weekly Pattern (Day of Week):**
    *   **Weekends (Fri-Sun):** Sales increase by ~50%.
    *   **Weekdays:** Standard sales volume.

4.  **🥙 Product Popularity:**
    *   **Chicken Shawarma:** Best seller (High volume).
    *   **Mixed:** Lowest volume.

---

## 📝 API Documentation

Once the backend is running, you can access the interactive API docs:

*   **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 🔬 Experiment Tracking (MLflow)
To view the experiment logs and model performance history:

```bash
cd mlpos-shawarma-forecast/backend
mlflow ui
```
Access the dashboard at: [http://localhost:5001](http://localhost:5001)

---



