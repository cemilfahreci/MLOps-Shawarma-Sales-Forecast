from datetime import date
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import joblib
import pandas as pd
from .. import models

# Define the combinations we want to predict for
PRODUCTS = ["Chicken Shawarma", "Meat Shawarma", "Mixed Shawarma"]
SIZES = ["Small", "Medium", "Large"]

# Prices for reference (optional, but good for revenue forecast if needed)
PRICES = {
    "Chicken Shawarma": {"Small": 8, "Medium": 12, "Large": 14},
    "Meat Shawarma": {"Small": 8, "Medium": 12, "Large": 14},
    "Mixed Shawarma": {"Small": 8, "Medium": 12, "Large": 14},
}

async def get_active_model_info(db: AsyncSession):
    """Returns the active model version from DB."""
    result = await db.execute(
        select(models.ModelVersion).where(models.ModelVersion.is_active == True)
    )
    model_version = result.scalars().first()
    return model_version


async def predict_tomorrow_total_quantity(db: AsyncSession) -> dict:
    """Predicts sales for TOMORROW for ALL product/size combinations."""
    # 1) Get active model
    model_version = await get_active_model_info(db)
    if not model_version:
        return {"error": "No active model found. Please train the model first."}

    model_path = Path(model_version.path)
    if not model_path.exists():
        return {"error": f"Model file not found: {model_path}"}

    # 2) Load model
    model = joblib.load(model_path)

    # 3) Prepare features for TOMORROW
    from datetime import timedelta
    tomorrow = date.today() + timedelta(days=1)
    year = tomorrow.year
    month = tomorrow.month
    day = tomorrow.day
    day_of_week = tomorrow.weekday()

    predictions = []
    total_predicted_quantity = 0

    # 4) Iterate over all valid combinations
    for product in PRODUCTS:
        for size in SIZES:
            # Check if this combination is valid (price > 0)
            if PRICES[product].get(size, 0) == 0:
                continue

            # Create input DataFrame for this single item
            X_item = pd.DataFrame([{
                "year": year,
                "month": month,
                "day": day,
                "day_of_week": day_of_week,
                "product_name": product,
                "size": size
            }])

            # Predict
            y_pred = model.predict(X_item)[0]
            qty = int(round(max(0, y_pred))) # Ensure non-negative

            if qty > 0:
                predictions.append({
                    "product_name": product,
                    "size": size,
                    "predicted_quantity": qty
                })
                total_predicted_quantity += qty

    # Sort by quantity desc
    predictions.sort(key=lambda x: x["predicted_quantity"], reverse=True)

    return {
        "date": tomorrow.isoformat(),
        "total_predicted_quantity": total_predicted_quantity,
        "breakdown": predictions,
        "model_version": model_version.version,
        "mae": model_version.mae,
    }