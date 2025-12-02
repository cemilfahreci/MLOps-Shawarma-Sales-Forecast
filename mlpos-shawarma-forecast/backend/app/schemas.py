from datetime import date, datetime
from pydantic import BaseModel


# ========= SALES =========

class SaleBase(BaseModel):
    date: date
    product_name: str
    size: str
    unit_price: int
    quantity: int


from typing import Optional

class SaleCreate(SaleBase):
    pass


class SaleUpdate(BaseModel):
    date: Optional[date] = None
    product_name: Optional[str] = None
    size: Optional[str] = None
    unit_price: Optional[int] = None
    quantity: Optional[int] = None


class SaleRead(SaleBase):
    id: int

    class Config:
        from_attributes = True


# ========= MODEL VERSIONS =========

class ModelVersionBase(BaseModel):
    version: str
    path: str
    mae: float


class ModelVersionCreate(ModelVersionBase):
    is_active: bool = False


class ModelVersionRead(ModelVersionBase):
    id: int
    trained_at: datetime
    is_active: bool

    class Config:
        from_attributes = True