from __future__ import annotations

from typing import Any, Dict

import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from etl.pipeline import get_dashboard_summary

async def fetch_kpis_from_db(session: AsyncSession) -> Dict[str, Any]:
    # Example KPI queries - optimized queries should be used in production
    res = {"total_revenue": 0.0, "total_profit": 0.0, "completed_orders": 0}
    try:
        r = await session.execute(text('SELECT SUM(selling_price) AS total_revenue, SUM(profit) AS total_profit, COUNT(*) FILTER (WHERE order_status = ''Completed'') AS completed_orders FROM orders'))
        row = r.first()
        if row:
            res['total_revenue'] = float(row.total_revenue or 0.0)
            res['total_profit'] = float(row.total_profit or 0.0)
            res['completed_orders'] = int(row.completed_orders or 0)
    except Exception:
        # fallback to ETL summary if DB not ready
        loop = asyncio.get_event_loop()
        summary = await loop.run_in_executor(None, get_dashboard_summary)
        res['total_revenue'] = summary.get('total_sales', 0.0)
        res['total_profit'] = summary.get('profit', 0.0)
        res['completed_orders'] = summary.get('total_orders', 0)
    return res
