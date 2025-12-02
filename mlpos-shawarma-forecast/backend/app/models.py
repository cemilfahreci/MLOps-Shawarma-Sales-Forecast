from sqlalchemy import Column, Integer, String, Date, Boolean, Float, DateTime
from datetime import datetime
from .database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)          # Satış tarihi
    product_name = Column(String, index=True)  # Chicken / Meat / Mixed Shawarma
    size = Column(String)                    # Small / Medium / Big
    unit_price = Column(Integer)             # 8 / 12 / 14 (QR)
    quantity = Column(Integer)               # Bu kayıtta satılan adet


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, unique=True, index=True)     # 'v1', 'v2'...
    product_name = Column(String, index=True)             # Chicken / Meat / Mixed Shawarma
    size = Column(String, index=True)                     # Small / Medium / Big
    path = Column(String)                                 # models/model_...pkl
    mae = Column(Float)                                   # Mean Absolute Error
    trained_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False)            # Şu an aktif model mi?