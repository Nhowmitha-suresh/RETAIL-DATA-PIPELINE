from typing import Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, text
from .models import Order, Product, Customer
from sqlalchemy import update, delete, insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select as future_select

async def get_kpis(session: AsyncSession) -> Dict[str, Any]:
    # Aggregated KPIs
    q = select(func.count().label('orders'), func.sum(Order.selling_price).label('revenue'), func.sum(Order.profit).label('profit'))
    r = await session.execute(q)
    row = r.first()
    return {'total_orders': int(row.orders or 0), 'total_revenue': float(row.revenue or 0.0), 'total_profit': float(row.profit or 0.0)}

async def list_orders(session: AsyncSession, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    q = select(Order).order_by(desc(Order.order_timestamp)).limit(limit).offset(offset)
    r = await session.execute(q)
    rows = r.scalars().all()
    return [dict(order_id=str(r.order_id), transaction_id=r.transaction_id, store=r.store, order_timestamp=r.order_timestamp.isoformat() if r.order_timestamp else None, selling_price=float(r.selling_price or 0.0)) for r in rows]

async def top_products(session: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
    q = text("SELECT product_id, SUM(quantity) AS sold_qty, SUM(total_price) AS revenue FROM order_items GROUP BY product_id ORDER BY sold_qty DESC LIMIT :limit")
    r = await session.execute(q, {'limit': limit})
    return [{'product_id': str(row.product_id), 'sold_qty': int(row.sold_qty), 'revenue': float(row.revenue)} for row in r]

async def get_customer_count(session: AsyncSession) -> int:
    q = select(func.count(Customer.customer_id))
    r = await session.execute(q)
    return int(r.scalar() or 0)


async def create_customer(session: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
    stmt = insert(Customer).values(**payload).returning(Customer.customer_id)
    r = await session.execute(stmt)
    await session.commit()
    return {"customer_id": str(r.scalar())}


async def get_customer(session: AsyncSession, customer_id: str) -> Dict[str, Any] | None:
    q = future_select(Customer).where(Customer.customer_id == customer_id)
    r = await session.execute(q)
    obj = r.scalar_one_or_none()
    if not obj:
        return None
    return {"customer_id": str(obj.customer_id), "external_id": obj.external_id, "gender": obj.gender, "age_group": obj.age_group, "membership_tier": obj.membership_tier, "customer_type": obj.customer_type}


async def update_customer(session: AsyncSession, customer_id: str, payload: Dict[str, Any]) -> bool:
    stmt = update(Customer).where(Customer.customer_id == customer_id).values(**payload)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def delete_customer(session: AsyncSession, customer_id: str) -> bool:
    stmt = delete(Customer).where(Customer.customer_id == customer_id)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def list_customers(session: AsyncSession, limit: int = 50, offset: int = 0, q: str | None = None, sort: str | None = None):
    base = select(Customer)
    if q:
        like = f"%{q}%"
        base = base.where((Customer.external_id.ilike(like)) | (Customer.membership_tier.ilike(like)))
    if sort:
        # simple sort by column name
        if hasattr(Customer, sort):
            base = base.order_by(getattr(Customer, sort))
    base = base.limit(limit).offset(offset)
    r = await session.execute(base)
    rows = r.scalars().all()
    return [{"customer_id": str(row.customer_id), "external_id": row.external_id, "membership_tier": row.membership_tier} for row in rows]


async def create_product(session: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
    stmt = insert(Product).values(**payload).returning(Product.product_id)
    r = await session.execute(stmt)
    await session.commit()
    return {"product_id": str(r.scalar())}


async def get_product(session: AsyncSession, product_id: str) -> Dict[str, Any] | None:
    q = future_select(Product).where(Product.product_id == product_id)
    r = await session.execute(q)
    obj = r.scalar_one_or_none()
    if not obj:
        return None
    return {"product_id": str(obj.product_id), "name": obj.name, "category": obj.category, "brand": obj.brand}


async def update_product(session: AsyncSession, product_id: str, payload: Dict[str, Any]) -> bool:
    stmt = update(Product).where(Product.product_id == product_id).values(**payload)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def delete_product(session: AsyncSession, product_id: str) -> bool:
    stmt = delete(Product).where(Product.product_id == product_id)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def list_products(session: AsyncSession, limit: int = 50, offset: int = 0, q: str | None = None, sort: str | None = None):
    base = select(Product)
    if q:
        like = f"%{q}%"
        base = base.where((Product.name.ilike(like)) | (Product.category.ilike(like)) | (Product.brand.ilike(like)))
    if sort and hasattr(Product, sort):
        base = base.order_by(getattr(Product, sort))
    base = base.limit(limit).offset(offset)
    r = await session.execute(base)
    rows = r.scalars().all()
    return [{"product_id": str(row.product_id), "name": row.name, "category": row.category, "brand": row.brand} for row in rows]


async def list_orders(session: AsyncSession, limit: int = 100, offset: int = 0, q: str | None = None, sort: str | None = None):
    base = select(Order).order_by(desc(Order.order_timestamp)).limit(limit).offset(offset)
    if q:
        like = f"%{q}%"
        base = base.where((Order.transaction_id.ilike(like)) | (Order.store.ilike(like)) | (Order.region.ilike(like)))
    r = await session.execute(base)
    rows = r.scalars().all()
    return [{"order_id": str(row.order_id), "transaction_id": row.transaction_id, "store": row.store, "order_timestamp": row.order_timestamp.isoformat() if row.order_timestamp else None, "selling_price": float(row.selling_price or 0.0)} for row in rows]


async def get_order(session: AsyncSession, order_id: str) -> Dict[str, Any] | None:
    q = future_select(Order).where(Order.order_id == order_id)
    r = await session.execute(q)
    obj = r.scalar_one_or_none()
    if not obj:
        return None
    return {"order_id": str(obj.order_id), "transaction_id": obj.transaction_id, "store": obj.store}


async def create_order(session: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
    stmt = insert(Order).values(**payload).returning(Order.order_id)
    r = await session.execute(stmt)
    await session.commit()
    return {"order_id": str(r.scalar())}


async def update_order(session: AsyncSession, order_id: str, payload: Dict[str, Any]) -> bool:
    stmt = update(Order).where(Order.order_id == order_id).values(**payload)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def delete_order(session: AsyncSession, order_id: str) -> bool:
    stmt = delete(Order).where(Order.order_id == order_id)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0
