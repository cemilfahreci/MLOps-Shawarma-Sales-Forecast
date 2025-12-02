from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from . import models, schemas


# ====== SALES CRUD ======

async def create_sale(db: AsyncSession, sale_in: schemas.SaleCreate) -> models.Sale:
    sale = models.Sale(
        date=sale_in.date,
        product_name=sale_in.product_name,
        size=sale_in.size,
        unit_price=sale_in.unit_price,
        quantity=sale_in.quantity,
    )
    db.add(sale)
    await db.commit()
    await db.refresh(sale)
    return sale


async def get_sales(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Sale]:
    result = await db.execute(
        select(models.Sale).order_by(models.Sale.date.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_sale(db: AsyncSession, sale_id: int) -> models.Sale | None:
    result = await db.execute(select(models.Sale).where(models.Sale.id == sale_id))
    return result.scalars().first()


async def update_sale(db: AsyncSession, sale_id: int, sale_in: schemas.SaleUpdate) -> models.Sale | None:
    sale = await get_sale(db, sale_id)
    if not sale:
        return None
    
    update_data = sale_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sale, key, value)
        
    db.add(sale)
    await db.commit()
    await db.refresh(sale)
    return sale


async def delete_sale(db: AsyncSession, sale_id: int) -> bool:
    sale = await get_sale(db, sale_id)
    if not sale:
        return False
        
    await db.delete(sale)
    await db.commit()
    return True