from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from typing import List
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from .database import Base, engine, get_db, AsyncSessionLocal
from . import models, schemas, crud
from .ml.train import train_model
from .ml.predict import predict_tomorrow_total_quantity

app = FastAPI(title="Shawarma MLOps API")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ====== STARTUP ======

@app.on_event("startup")
async def on_startup():
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ====== SALES API ======

@app.post("/sales", response_model=schemas.SaleRead)
async def create_sale_endpoint(
    sale_in: schemas.SaleCreate,
    db: AsyncSession = Depends(get_db),
):
    sale = await crud.create_sale(db, sale_in)
    # Synchronous training
    await train_model(db)
    return sale


@app.get("/sales", response_model=List[schemas.SaleRead])
async def list_sales_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    sales = await crud.get_sales(db, skip=skip, limit=limit)
    return sales


@app.put("/sales/{sale_id}", response_model=schemas.SaleRead)
async def update_sale_endpoint(
    sale_id: int,
    sale_in: schemas.SaleUpdate,
    db: AsyncSession = Depends(get_db),
):
    sale = await crud.update_sale(db, sale_id, sale_in)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
        
    # Synchronous training
    await train_model(db)
    return sale


@app.delete("/sales/{sale_id}")
async def delete_sale_endpoint(
    sale_id: int,
    db: AsyncSession = Depends(get_db),
):
    success = await crud.delete_sale(db, sale_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    # Synchronous training
    await train_model(db)
    return {"message": "Sale deleted and model retrained"}

# ====== CSV IMPORT & AUTO RETRAIN ======

@app.post("/sales/import-csv")
async def import_sales_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # Only accept CSV
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {e}")

    required_cols = ["date", "product_name", "size", "unit_price", "quantity"]
    for col in required_cols:
        if col not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing column: {col}. Required columns: {required_cols}",
            )

    inserted = 0
    try:
        # Bulk insert might be faster, but loop is fine for now
        for index, row in df.iterrows():
            sale_in = schemas.SaleCreate(
                date=row["date"],
                product_name=row["product_name"],
                size=row["size"],
                unit_price=int(row["unit_price"]),
                quantity=int(row["quantity"]),
            )
            await crud.create_sale(db, sale_in)
            inserted += 1
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing row {inserted + 1}: {e}")

    # Synchronous Training
    await train_model(db)

    return {
        "message": f"Successfully imported {inserted} records. Model retrained.",
        "inserted": inserted
    }

# ====== MODEL TRAIN / FORECAST ======

@app.get("/forecast/tomorrow")
async def forecast_tomorrow_endpoint(
    db: AsyncSession = Depends(get_db),
):
    result = await predict_tomorrow_total_quantity(db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ====== MODEL REGISTRY ======

@app.get("/models", response_model=List[schemas.ModelVersionRead])
async def list_models(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(models.ModelVersion).order_by(models.ModelVersion.trained_at.desc()))
    return result.scalars().all()


@app.delete("/models/{version}")
async def delete_model(version: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    import os
    
    # Check if active
    result = await db.execute(select(models.ModelVersion).where(models.ModelVersion.version == version))
    model_v = result.scalars().first()
    
    if not model_v:
        raise HTTPException(status_code=404, detail="Model version not found")
        
    if model_v.is_active:
        raise HTTPException(status_code=400, detail="Cannot delete active model")
        
    # Delete file
    try:
        if os.path.exists(model_v.path):
            os.remove(model_v.path)
    except Exception as e:
        print(f"Error deleting file: {e}")
        
    await db.delete(model_v)
    await db.commit()
    return {"message": f"Model {version} deleted"}