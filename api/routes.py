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
from .repositories import create_customer, get_customer, update_customer, delete_customer, list_customers
from .auth import require_role
from typing import Dict, Any
from .repositories import create_product, get_product, update_product, delete_product, list_products, create_order, get_order, update_order, delete_order, list_orders

router = APIRouter()

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

@router.get('/products')
async def products():
    # For now, return product performance from ETL
    summary = get_dashboard_summary()
    return {"status": "ok", "products": summary.get('product_performance')}



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
    return {"status": "ok"}


@router.delete('/orders/{order_id}', dependencies=[Depends(require_role('manager'))])
async def orders_delete(order_id: str, db: AsyncSession = Depends(get_db)):
    ok = await delete_order(db, order_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Order not found')
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
