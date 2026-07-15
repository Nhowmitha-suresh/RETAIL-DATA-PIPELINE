from typing import Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, text
from .models import Order, Product, Customer, Supplier, Warehouse, Store, OrderItem, Review, Promotion
from sqlalchemy import update, delete, insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select as future_select


def _filter_payload(model, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Keep only keys that map to the model's table columns."""
    cols = set(model.__table__.columns.keys())
    return {k: v for k, v in payload.items() if k in cols}

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
    obj = Customer(**payload)
    session.add(obj)
    await session.flush()
    await session.commit()
    return {"customer_id": str(obj.customer_id)}


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
    obj = Product(**payload)
    session.add(obj)
    await session.flush()
    await session.commit()
    return {"product_id": str(obj.product_id)}


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
    obj = Order(**payload)
    session.add(obj)
    await session.flush()
    await session.commit()
    return {"order_id": str(obj.order_id)}


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


# Suppliers CRUD
async def create_supplier(session: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
    obj = Supplier(**payload)
    session.add(obj)
    await session.flush()
    await session.commit()
    return {"supplier_id": str(obj.supplier_id)}


async def get_supplier(session: AsyncSession, supplier_id: str) -> Dict[str, Any] | None:
    q = future_select(Supplier).where(Supplier.supplier_id == supplier_id)
    r = await session.execute(q)
    obj = r.scalar_one_or_none()
    if not obj:
        return None
    return {"supplier_id": str(obj.supplier_id), "name": obj.name, "contact_info": obj.contact_info}


async def update_supplier(session: AsyncSession, supplier_id: str, payload: Dict[str, Any]) -> bool:
    stmt = update(Supplier).where(Supplier.supplier_id == supplier_id).values(**payload)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def delete_supplier(session: AsyncSession, supplier_id: str) -> bool:
    stmt = delete(Supplier).where(Supplier.supplier_id == supplier_id)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def list_suppliers(session: AsyncSession, limit: int = 50, offset: int = 0, q: str | None = None, sort: str | None = None):
    base = select(Supplier)
    if q:
        like = f"%{q}%"
        base = base.where(Supplier.name.ilike(like))
    if sort and hasattr(Supplier, sort):
        base = base.order_by(getattr(Supplier, sort))
    base = base.limit(limit).offset(offset)
    r = await session.execute(base)
    rows = r.scalars().all()
    return [{"supplier_id": str(row.supplier_id), "name": row.name} for row in rows]


# Stores CRUD
async def create_store(session: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
    obj = Store(**payload)
    session.add(obj)
    await session.flush()
    await session.commit()
    return {"store_id": str(obj.store_id)}


async def get_store(session: AsyncSession, store_id: str) -> Dict[str, Any] | None:
    q = future_select(Store).where(Store.store_id == store_id)
    r = await session.execute(q)
    obj = r.scalar_one_or_none()
    if not obj:
        return None
    return {"store_id": str(obj.store_id), "name": obj.name, "city": obj.city, "state": obj.state, "region": obj.region}


async def update_store(session: AsyncSession, store_id: str, payload: Dict[str, Any]) -> bool:
    stmt = update(Store).where(Store.store_id == store_id).values(**payload)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def delete_store(session: AsyncSession, store_id: str) -> bool:
    stmt = delete(Store).where(Store.store_id == store_id)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def list_stores(session: AsyncSession, limit: int = 50, offset: int = 0, q: str | None = None, sort: str | None = None):
    base = select(Store)
    if q:
        like = f"%{q}%"
        base = base.where((Store.name.ilike(like)) | (Store.city.ilike(like)))
    if sort and hasattr(Store, sort):
        base = base.order_by(getattr(Store, sort))
    base = base.limit(limit).offset(offset)
    r = await session.execute(base)
    rows = r.scalars().all()
    return [{"store_id": str(row.store_id), "name": row.name, "city": row.city, "state": row.state, "region": row.region} for row in rows]


# Warehouses CRUD
async def create_warehouse(session: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
    obj = Warehouse(**payload)
    session.add(obj)
    await session.flush()
    await session.commit()
    return {"warehouse_id": str(obj.warehouse_id)}


async def get_warehouse(session: AsyncSession, warehouse_id: str) -> Dict[str, Any] | None:
    q = future_select(Warehouse).where(Warehouse.warehouse_id == warehouse_id)
    r = await session.execute(q)
    obj = r.scalar_one_or_none()
    if not obj:
        return None
    return {"warehouse_id": str(obj.warehouse_id), "name": obj.name, "city": obj.city, "region": obj.region}


async def update_warehouse(session: AsyncSession, warehouse_id: str, payload: Dict[str, Any]) -> bool:
    stmt = update(Warehouse).where(Warehouse.warehouse_id == warehouse_id).values(**payload)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def delete_warehouse(session: AsyncSession, warehouse_id: str) -> bool:
    stmt = delete(Warehouse).where(Warehouse.warehouse_id == warehouse_id)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def list_warehouses(session: AsyncSession, limit: int = 50, offset: int = 0, q: str | None = None, sort: str | None = None):
    base = select(Warehouse)
    if q:
        like = f"%{q}%"
        base = base.where((Warehouse.name.ilike(like)) | (Warehouse.city.ilike(like)) | (Warehouse.region.ilike(like)))
    if sort and hasattr(Warehouse, sort):
        base = base.order_by(getattr(Warehouse, sort))
    base = base.limit(limit).offset(offset)
    r = await session.execute(base)
    rows = r.scalars().all()
    return [{"warehouse_id": str(row.warehouse_id), "name": row.name, "city": row.city, "region": row.region} for row in rows]


# Order Items CRUD
async def create_order_item(session: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
    obj = OrderItem(**payload)
    session.add(obj)
    await session.flush()
    await session.commit()
    return {"item_id": str(obj.item_id)}


async def get_order_item(session: AsyncSession, item_id: str) -> Dict[str, Any] | None:
    q = future_select(OrderItem).where(OrderItem.item_id == item_id)
    r = await session.execute(q)
    obj = r.scalar_one_or_none()
    if not obj:
        return None
    return {"item_id": str(obj.item_id), "order_id": obj.order_id, "product_id": obj.product_id, "quantity": obj.quantity, "unit_price": float(obj.unit_price or 0.0), "total_price": float(obj.total_price or 0.0)}


async def update_order_item(session: AsyncSession, item_id: str, payload: Dict[str, Any]) -> bool:
    stmt = update(OrderItem).where(OrderItem.item_id == item_id).values(**payload)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def delete_order_item(session: AsyncSession, item_id: str) -> bool:
    stmt = delete(OrderItem).where(OrderItem.item_id == item_id)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def list_order_items(session: AsyncSession, limit: int = 50, offset: int = 0, q: str | None = None, sort: str | None = None):
    base = select(OrderItem)
    if q:
        like = f"%{q}%"
        base = base.where((OrderItem.order_id.ilike(like)) | (OrderItem.product_id.ilike(like)))
    if sort and hasattr(OrderItem, sort):
        base = base.order_by(getattr(OrderItem, sort))
    base = base.limit(limit).offset(offset)
    r = await session.execute(base)
    rows = r.scalars().all()
    return [{"item_id": str(row.item_id), "order_id": row.order_id, "product_id": row.product_id, "quantity": row.quantity, "total_price": float(row.total_price or 0.0)} for row in rows]


# Reviews CRUD
async def create_review(session: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
    obj = Review(**payload)
    session.add(obj)
    await session.flush()
    await session.commit()
    return {"review_id": str(obj.review_id)}


async def get_review(session: AsyncSession, review_id: str) -> Dict[str, Any] | None:
    q = future_select(Review).where(Review.review_id == review_id)
    r = await session.execute(q)
    obj = r.scalar_one_or_none()
    if not obj:
        return None
    return {"review_id": str(obj.review_id), "order_id": obj.order_id, "rating": float(obj.rating or 0.0), "comment": obj.comment}


async def update_review(session: AsyncSession, review_id: str, payload: Dict[str, Any]) -> bool:
    stmt = update(Review).where(Review.review_id == review_id).values(**payload)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def delete_review(session: AsyncSession, review_id: str) -> bool:
    stmt = delete(Review).where(Review.review_id == review_id)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def list_reviews(session: AsyncSession, limit: int = 50, offset: int = 0, q: str | None = None, sort: str | None = None):
    base = select(Review)
    if q:
        like = f"%{q}%"
        base = base.where(Review.comment.ilike(like))
    if sort and hasattr(Review, sort):
        base = base.order_by(getattr(Review, sort))
    base = base.limit(limit).offset(offset)
    r = await session.execute(base)
    rows = r.scalars().all()
    return [{"review_id": str(row.review_id), "order_id": row.order_id, "rating": float(row.rating or 0.0), "comment": row.comment} for row in rows]


# Promotions CRUD
async def create_promotion(session: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
    obj = Promotion(**payload)
    session.add(obj)
    await session.flush()
    await session.commit()
    return {"promotion_id": str(obj.promotion_id)}


async def get_promotion(session: AsyncSession, promotion_id: str) -> Dict[str, Any] | None:
    q = future_select(Promotion).where(Promotion.promotion_id == promotion_id)
    r = await session.execute(q)
    obj = r.scalar_one_or_none()
    if not obj:
        return None
    return {"promotion_id": str(obj.promotion_id), "code": obj.code, "description": obj.description, "discount_pct": float(obj.discount_pct or 0.0), "start_date": obj.start_date.isoformat() if obj.start_date else None, "end_date": obj.end_date.isoformat() if obj.end_date else None}


async def update_promotion(session: AsyncSession, promotion_id: str, payload: Dict[str, Any]) -> bool:
    stmt = update(Promotion).where(Promotion.promotion_id == promotion_id).values(**payload)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def delete_promotion(session: AsyncSession, promotion_id: str) -> bool:
    stmt = delete(Promotion).where(Promotion.promotion_id == promotion_id)
    r = await session.execute(stmt)
    await session.commit()
    return r.rowcount > 0


async def list_promotions(session: AsyncSession, limit: int = 50, offset: int = 0, q: str | None = None, sort: str | None = None):
    base = select(Promotion)
    if q:
        like = f"%{q}%"
        base = base.where((Promotion.code.ilike(like)) | (Promotion.description.ilike(like)))
    if sort and hasattr(Promotion, sort):
        base = base.order_by(getattr(Promotion, sort))
    base = base.limit(limit).offset(offset)
    r = await session.execute(base)
    rows = r.scalars().all()
    return [{"promotion_id": str(row.promotion_id), "code": row.code, "description": row.description, "discount_pct": float(row.discount_pct or 0.0)} for row in rows]
