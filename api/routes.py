from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db
from .services import fetch_kpis_from_db, ai_insights_query
from etl.pipeline import get_dashboard_summary, predict_sales, train_model
from .auth import login, get_current_user
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from .utils import pagination_params, filter_params
from .repositories import (
    create_customer,
    get_customer,
    update_customer,
    delete_customer,
    list_customers,
    create_product,
    get_product,
    update_product,
    delete_product,
    list_products,
    create_order,
    get_order,
    update_order,
    delete_order,
    list_orders,
    create_supplier,
    get_supplier,
    update_supplier,
    delete_supplier,
    list_suppliers,
    create_store,
    get_store,
    update_store,
    delete_store,
    list_stores,
    create_warehouse,
    get_warehouse,
    update_warehouse,
    delete_warehouse,
    list_warehouses,
    create_order_item,
    get_order_item,
    update_order_item,
    delete_order_item,
    list_order_items,
    create_review,
    get_review,
    update_review,
    delete_review,
    list_reviews,
    create_promotion,
    get_promotion,
    update_promotion,
    delete_promotion,
    list_promotions,
)
from .auth import require_role
from .ws import manager as ws_manager
from typing import Dict, Any

router = APIRouter(tags=["Retail API"])

@router.get('/dashboard')
async def dashboard(db: AsyncSession = Depends(get_db)):
    kpis = await fetch_kpis_from_db(db)
    return {"status": "ok", "kpis": kpis}

@router.get('/sales')
async def sales():
    summary = get_dashboard_summary()
    return {"status": "ok", "summary": summary}

@router.get('/revenue')
async def revenue():
    summary = get_dashboard_summary()
    return {"status": "ok", "revenue": {"total": summary.get('total_sales'), "monthly": summary.get('monthly_sales')}}

@router.get('/inventory')
async def inventory():
    # Inventory will be derived from ETL until DB inventory table is populated
    summary = get_dashboard_summary()
    return {"status": "ok", "inventory": {"value": summary.get('cash_flow'), "breakdown": summary.get('expense_breakdown')}}

@router.get('/finance')
async def finance():
    summary = get_dashboard_summary()
    return {"status": "ok", "finance": {"profit": summary.get('profit'), "expenses": summary.get('expenses'), "cash_flow": summary.get('cash_flow')}}

@router.get('/forecast')
async def forecast():
    summary = get_dashboard_summary()
    return {"status": "ok", "forecast": summary.get('forecast')}

@router.get('/ai-insights')
async def ai_insights(q: str = "revenue trend", db: AsyncSession = Depends(get_db)):
    # Use a simple AI-analyst mapping to translate the query into SQL and execute
    try:
        results = await ai_insights_query(q, db)
        return {"status": "ok", "query": q, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/reports')
async def reports():
    return {"status": "ok", "reports": ["daily", "weekly", "monthly", "quarterly", "annual"]}

@router.get('/settings')
async def settings():
    return {"status": "ok", "settings": {"theme": "dark", "currency": "INR"}}


# Customers CRUD
@router.post('/customers', dependencies=[Depends(require_role('manager'))])
async def customers_create(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    created = await create_customer(db, payload)
    return {"status": "ok", "created": created}


@router.get('/customers')
async def customers_list(p: dict = Depends(pagination_params), f: dict = Depends(filter_params), db: AsyncSession = Depends(get_db)):
    results = await list_customers(db, limit=p['limit'], offset=p['offset'], q=f['search'], sort=f['sort'])
    return {"status": "ok", "items": results}


@router.get('/customers/{customer_id}')
async def customers_get(customer_id: str, db: AsyncSession = Depends(get_db)):
    obj = await get_customer(db, customer_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Customer not found')
    return {"status": "ok", "customer": obj}


@router.put('/customers/{customer_id}', dependencies=[Depends(require_role('manager'))])
async def customers_update(customer_id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    ok = await update_customer(db, customer_id, payload)
    if not ok:
        raise HTTPException(status_code=404, detail='Customer not found')
    return {"status": "ok"}


@router.delete('/customers/{customer_id}', dependencies=[Depends(require_role('manager'))])
async def customers_delete(customer_id: str, db: AsyncSession = Depends(get_db)):
    ok = await delete_customer(db, customer_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Customer not found')
    return {"status": "ok"}


### Products CRUD
@router.post('/products', dependencies=[Depends(require_role('manager'))])
async def products_create(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    created = await create_product(db, payload)
    return {"status": "ok", "created": created}


@router.get('/products')
async def products_list(p: dict = Depends(pagination_params), f: dict = Depends(filter_params), db: AsyncSession = Depends(get_db)):
    results = await list_products(db, limit=p['limit'], offset=p['offset'], q=f['search'], sort=f['sort'])
    return {"status": "ok", "items": results}


@router.get('/products/{product_id}')
async def products_get(product_id: str, db: AsyncSession = Depends(get_db)):
    obj = await get_product(db, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Product not found')
    return {"status": "ok", "product": obj}


@router.put('/products/{product_id}', dependencies=[Depends(require_role('manager'))])
async def products_update(product_id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    ok = await update_product(db, product_id, payload)
    if not ok:
        raise HTTPException(status_code=404, detail='Product not found')
    return {"status": "ok"}


@router.delete('/products/{product_id}', dependencies=[Depends(require_role('manager'))])
async def products_delete(product_id: str, db: AsyncSession = Depends(get_db)):
    ok = await delete_product(db, product_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Product not found')
    return {"status": "ok"}


### Orders CRUD
@router.post('/orders', dependencies=[Depends(require_role('manager'))])
async def orders_create(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    created = await create_order(db, payload)
    return {"status": "ok", "created": created}


@router.get('/orders')
async def orders_list(p: dict = Depends(pagination_params), f: dict = Depends(filter_params), db: AsyncSession = Depends(get_db)):
    results = await list_orders(db, limit=p['limit'], offset=p['offset'], q=f['search'], sort=f['sort'])
    return {"status": "ok", "items": results}


@router.get('/orders/{order_id}')
async def orders_get(order_id: str, db: AsyncSession = Depends(get_db)):
    obj = await get_order(db, order_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Order not found')
    return {"status": "ok", "order": obj}


@router.put('/orders/{order_id}', dependencies=[Depends(require_role('manager'))])
async def orders_update(order_id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    ok = await update_order(db, order_id, payload)
    if not ok:
        raise HTTPException(status_code=404, detail='Order not found')
    await ws_manager.broadcast({"event": "order.updated", "order_id": order_id, "payload": payload})
    return {"status": "ok"}


@router.delete('/orders/{order_id}', dependencies=[Depends(require_role('manager'))])
async def orders_delete(order_id: str, db: AsyncSession = Depends(get_db)):
    ok = await delete_order(db, order_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Order not found')
    await ws_manager.broadcast({"event": "order.deleted", "order_id": order_id})
    return {"status": "ok"}


@router.get('/summary')
async def summary():
    dashboard = get_dashboard_summary()
    return {"status": "ok", "summary": dashboard}


# Suppliers CRUD
@router.post('/suppliers', dependencies=[Depends(require_role('manager'))])
async def suppliers_create(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    created = await create_supplier(db, payload)
    await ws_manager.broadcast({"event": "supplier.created", "payload": created})
    return {"status": "ok", "created": created}


@router.get('/suppliers')
async def suppliers_list(p: dict = Depends(pagination_params), f: dict = Depends(filter_params), db: AsyncSession = Depends(get_db)):
    results = await list_suppliers(db, limit=p['limit'], offset=p['offset'], q=f['search'], sort=f['sort'])
    return {"status": "ok", "items": results}


@router.get('/suppliers/{supplier_id}')
async def suppliers_get(supplier_id: str, db: AsyncSession = Depends(get_db)):
    obj = await get_supplier(db, supplier_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Supplier not found')
    return {"status": "ok", "supplier": obj}


@router.put('/suppliers/{supplier_id}', dependencies=[Depends(require_role('manager'))])
async def suppliers_update(supplier_id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    ok = await update_supplier(db, supplier_id, payload)
    if not ok:
        raise HTTPException(status_code=404, detail='Supplier not found')
    await ws_manager.broadcast({"event": "supplier.updated", "supplier_id": supplier_id, "payload": payload})
    return {"status": "ok"}


@router.delete('/suppliers/{supplier_id}', dependencies=[Depends(require_role('manager'))])
async def suppliers_delete(supplier_id: str, db: AsyncSession = Depends(get_db)):
    ok = await delete_supplier(db, supplier_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Supplier not found')
    await ws_manager.broadcast({"event": "supplier.deleted", "supplier_id": supplier_id})
    return {"status": "ok"}


# Stores CRUD
@router.post('/stores', dependencies=[Depends(require_role('manager'))])
async def stores_create(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    created = await create_store(db, payload)
    await ws_manager.broadcast({"event": "store.created", "payload": created})
    return {"status": "ok", "created": created}


@router.get('/stores')
async def stores_list(p: dict = Depends(pagination_params), f: dict = Depends(filter_params), db: AsyncSession = Depends(get_db)):
    results = await list_stores(db, limit=p['limit'], offset=p['offset'], q=f['search'], sort=f['sort'])
    return {"status": "ok", "items": results}


@router.get('/stores/{store_id}')
async def stores_get(store_id: str, db: AsyncSession = Depends(get_db)):
    obj = await get_store(db, store_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Store not found')
    return {"status": "ok", "store": obj}


@router.put('/stores/{store_id}', dependencies=[Depends(require_role('manager'))])
async def stores_update(store_id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    ok = await update_store(db, store_id, payload)
    if not ok:
        raise HTTPException(status_code=404, detail='Store not found')
    await ws_manager.broadcast({"event": "store.updated", "store_id": store_id, "payload": payload})
    return {"status": "ok"}


@router.delete('/stores/{store_id}', dependencies=[Depends(require_role('manager'))])
async def stores_delete(store_id: str, db: AsyncSession = Depends(get_db)):
    ok = await delete_store(db, store_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Store not found')
    await ws_manager.broadcast({"event": "store.deleted", "store_id": store_id})
    return {"status": "ok"}


# Warehouses CRUD
@router.post('/warehouses', dependencies=[Depends(require_role('manager'))])
async def warehouses_create(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    created = await create_warehouse(db, payload)
    await ws_manager.broadcast({"event": "warehouse.created", "payload": created})
    return {"status": "ok", "created": created}


@router.get('/warehouses')
async def warehouses_list(p: dict = Depends(pagination_params), f: dict = Depends(filter_params), db: AsyncSession = Depends(get_db)):
    results = await list_warehouses(db, limit=p['limit'], offset=p['offset'], q=f['search'], sort=f['sort'])
    return {"status": "ok", "items": results}


@router.get('/warehouses/{warehouse_id}')
async def warehouses_get(warehouse_id: str, db: AsyncSession = Depends(get_db)):
    obj = await get_warehouse(db, warehouse_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Warehouse not found')
    return {"status": "ok", "warehouse": obj}


@router.put('/warehouses/{warehouse_id}', dependencies=[Depends(require_role('manager'))])
async def warehouses_update(warehouse_id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    ok = await update_warehouse(db, warehouse_id, payload)
    if not ok:
        raise HTTPException(status_code=404, detail='Warehouse not found')
    await ws_manager.broadcast({"event": "warehouse.updated", "warehouse_id": warehouse_id, "payload": payload})
    return {"status": "ok"}


@router.delete('/warehouses/{warehouse_id}', dependencies=[Depends(require_role('manager'))])
async def warehouses_delete(warehouse_id: str, db: AsyncSession = Depends(get_db)):
    ok = await delete_warehouse(db, warehouse_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Warehouse not found')
    await ws_manager.broadcast({"event": "warehouse.deleted", "warehouse_id": warehouse_id})
    return {"status": "ok"}


# Order items CRUD
@router.post('/order_items', dependencies=[Depends(require_role('manager'))])
async def order_items_create(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    created = await create_order_item(db, payload)
    await ws_manager.broadcast({"event": "order_item.created", "payload": created})
    return {"status": "ok", "created": created}


@router.get('/order_items')
async def order_items_list(p: dict = Depends(pagination_params), f: dict = Depends(filter_params), db: AsyncSession = Depends(get_db)):
    results = await list_order_items(db, limit=p['limit'], offset=p['offset'], q=f['search'], sort=f['sort'])
    return {"status": "ok", "items": results}


@router.get('/order_items/{item_id}')
async def order_items_get(item_id: str, db: AsyncSession = Depends(get_db)):
    obj = await get_order_item(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Order item not found')
    return {"status": "ok", "item": obj}


@router.put('/order_items/{item_id}', dependencies=[Depends(require_role('manager'))])
async def order_items_update(item_id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    ok = await update_order_item(db, item_id, payload)
    if not ok:
        raise HTTPException(status_code=404, detail='Order item not found')
    await ws_manager.broadcast({"event": "order_item.updated", "item_id": item_id, "payload": payload})
    return {"status": "ok"}


@router.delete('/order_items/{item_id}', dependencies=[Depends(require_role('manager'))])
async def order_items_delete(item_id: str, db: AsyncSession = Depends(get_db)):
    ok = await delete_order_item(db, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Order item not found')
    await ws_manager.broadcast({"event": "order_item.deleted", "item_id": item_id})
    return {"status": "ok"}


# Reviews CRUD
@router.post('/reviews', dependencies=[Depends(require_role('manager'))])
async def reviews_create(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    created = await create_review(db, payload)
    await ws_manager.broadcast({"event": "review.created", "payload": created})
    return {"status": "ok", "created": created}


@router.get('/reviews')
async def reviews_list(p: dict = Depends(pagination_params), f: dict = Depends(filter_params), db: AsyncSession = Depends(get_db)):
    results = await list_reviews(db, limit=p['limit'], offset=p['offset'], q=f['search'], sort=f['sort'])
    return {"status": "ok", "items": results}


@router.get('/reviews/{review_id}')
async def reviews_get(review_id: str, db: AsyncSession = Depends(get_db)):
    obj = await get_review(db, review_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Review not found')
    return {"status": "ok", "review": obj}


@router.put('/reviews/{review_id}', dependencies=[Depends(require_role('manager'))])
async def reviews_update(review_id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    ok = await update_review(db, review_id, payload)
    if not ok:
        raise HTTPException(status_code=404, detail='Review not found')
    await ws_manager.broadcast({"event": "review.updated", "review_id": review_id, "payload": payload})
    return {"status": "ok"}


@router.delete('/reviews/{review_id}', dependencies=[Depends(require_role('manager'))])
async def reviews_delete(review_id: str, db: AsyncSession = Depends(get_db)):
    ok = await delete_review(db, review_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Review not found')
    await ws_manager.broadcast({"event": "review.deleted", "review_id": review_id})
    return {"status": "ok"}


# Promotions CRUD
@router.post('/promotions', dependencies=[Depends(require_role('manager'))])
async def promotions_create(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    created = await create_promotion(db, payload)
    await ws_manager.broadcast({"event": "promotion.created", "payload": created})
    return {"status": "ok", "created": created}


@router.get('/promotions')
async def promotions_list(p: dict = Depends(pagination_params), f: dict = Depends(filter_params), db: AsyncSession = Depends(get_db)):
    results = await list_promotions(db, limit=p['limit'], offset=p['offset'], q=f['search'], sort=f['sort'])
    return {"status": "ok", "items": results}


@router.get('/promotions/{promotion_id}')
async def promotions_get(promotion_id: str, db: AsyncSession = Depends(get_db)):
    obj = await get_promotion(db, promotion_id)
    if not obj:
        raise HTTPException(status_code=404, detail='Promotion not found')
    return {"status": "ok", "promotion": obj}


@router.put('/promotions/{promotion_id}', dependencies=[Depends(require_role('manager'))])
async def promotions_update(promotion_id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    ok = await update_promotion(db, promotion_id, payload)
    if not ok:
        raise HTTPException(status_code=404, detail='Promotion not found')
    await ws_manager.broadcast({"event": "promotion.updated", "promotion_id": promotion_id, "payload": payload})
    return {"status": "ok"}


@router.delete('/promotions/{promotion_id}', dependencies=[Depends(require_role('manager'))])
async def promotions_delete(promotion_id: str, db: AsyncSession = Depends(get_db)):
    ok = await delete_promotion(db, promotion_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Promotion not found')
    await ws_manager.broadcast({"event": "promotion.deleted", "promotion_id": promotion_id})
    return {"status": "ok"}


@router.post('/predict')
async def predict(payload: dict):
    return predict_sales(payload)

@router.post('/train')
async def train():
    return train_model()


@router.post('/token')
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    return login(form_data)
