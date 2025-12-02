from pathlib import Path
from datetime import datetime
import asyncio
import random

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import mlflow
import mlflow.sklearn

from .. import models


MODELS_DIR = Path(__file__).resolve().parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


async def train_model(db: AsyncSession) -> dict:
    # 1) Fetch all sales from DB
    result = await db.execute(select(models.Sale))
    rows = result.scalars().all()

    if not rows:
        return {"error": "No sales data found, cannot train model."}
    
    # 2) Convert to DataFrame
    data = [
        {
            "date": r.date,
            "product_name": r.product_name,
            "size": r.size,
            "quantity": r.quantity,
        }
        for r in rows
    ]
    df = pd.DataFrame(data)

    # 3) Group by Date + Product + Size
    df_daily = df.groupby(["date", "product_name", "size"], as_index=False)["quantity"].sum()
    df_daily = df_daily.rename(columns={"quantity": "total_quantity"})
    
    # Convert date to datetime
    df_daily["date"] = pd.to_datetime(df_daily["date"])

    # Feature Engineering
    df_daily["year"] = df_daily["date"].dt.year
    df_daily["month"] = df_daily["date"].dt.month
    df_daily["day"] = df_daily["date"].dt.day
    df_daily["day_of_week"] = df_daily["date"].dt.weekday
    
    # Features: year, month, day, day_of_week, product_name, size
    X = df_daily[["year", "month", "day", "day_of_week", "product_name", "size"]]
    y = df_daily["total_quantity"]

    # 4) Create Pipeline with OneHotEncoder for categorical features
    categorical_features = ["product_name", "size"]
    numerical_features = ["year", "month", "day", "day_of_week"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numerical_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    model_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    # 5) Train/Test Split
    if len(df_daily) >= 10:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
    else:
        X_train, y_train = X, y
        X_test, y_test = X, y
        
    # Train
    model_pipeline.fit(X_train, y_train)

    # Evaluate
    if len(df_daily) >= 10:
        y_pred = model_pipeline.predict(X_test)
        mae = float(mean_absolute_error(y_test, y_pred))
    else:
        mae = 0.0
    
    # 6) Versioning
    result_versions = await db.execute(select(models.ModelVersion))
    versions = result_versions.scalars().all()
    if not versions:
        new_version_number = 1
    else:
        nums = []
        for v in versions:
            try:
                nums.append(int(v.version.replace("v", "")))
            except Exception:
                continue
        new_version_number = max(nums) + 1 if nums else 1

    version_str = f"v{new_version_number}"

    # 7) Save Model
    model_path = MODELS_DIR / f"model_{version_str}.pkl"
    joblib.dump(model_pipeline, model_path)

    # --- MLflow Logging ---
    mlflow.set_experiment("Shawarma_Sales_Forecast")
    with mlflow.start_run(run_name=version_str):
        # Log Parameters
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("random_state", 42)
        mlflow.log_param("version", version_str)
        
        # Log Metrics
        mlflow.log_metric("mae", mae)
        
        # Log Model
        mlflow.sklearn.log_model(model_pipeline, "model")
    # ----------------------

    # 8) Update DB
    for v in versions:
        v.is_active = False

    new_model_version = models.ModelVersion(
        version=version_str,
        path=str(model_path),
        mae=mae,
        trained_at=datetime.utcnow(),
        is_active=True,
    )
    db.add(new_model_version)
    await db.commit()
    
    return {
        "version": version_str,
        "mae": mae,
        "path": str(model_path),
        "trained_at": new_model_version.trained_at.isoformat() + "Z",
    }