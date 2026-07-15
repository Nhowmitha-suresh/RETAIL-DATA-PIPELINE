from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db
from .services import fetch_kpis_from_db, ai_insights_query
from etl.pipeline import get_dashboard_summary, predict_sales, train_model
from .auth import login, get_current_user
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

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

@router.get('/customers')
async def customers():
    summary = get_dashboard_summary()
    return {"status": "ok", "customers": {"total_customers": summary.get('total_customers'), "new_users": summary.get('new_users')}}

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

@router.post('/predict')
async def predict(payload: dict):
    return predict_sales(payload)

@router.post('/train')
async def train():
    return train_model()


@router.post('/token')
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    return login(form_data)
