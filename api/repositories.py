from typing import Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, text
from .models import Order, Product, Customer

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
