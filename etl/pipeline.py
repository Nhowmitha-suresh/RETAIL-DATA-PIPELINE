from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split


DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "sales.csv"
MODEL_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "sales_model.joblib"


def ensure_dataset(path: Path | str | None = None) -> pd.DataFrame:
    target_path = Path(path or DATASET_PATH)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if target_path.exists() and target_path.stat().st_size > 0:
        df = pd.read_csv(target_path)
        if not df.empty:
            return df

    rng = np.random.default_rng(42)
    rows = 240
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=rows, freq="D"),
            "store": rng.choice(["Store A", "Store B", "Store C"], size=rows),
            "region": rng.choice(["North", "South", "East", "West"], size=rows),
            "category": rng.choice(["Electronics", "Home", "Fashion", "Groceries"], size=rows),
            "month": np.tile(np.arange(1, 13), 20)[:rows],
            "promotion": rng.choice([True, False], size=rows, p=[0.35, 0.65]),
            "discount": rng.integers(0, 25, size=rows),
            "customer_count": rng.integers(40, 180, size=rows),
            "season": rng.choice(["Spring", "Summer", "Fall", "Winter"], size=rows),
        }
    )

    category_multiplier = {"Electronics": 1.25, "Home": 1.05, "Fashion": 1.12, "Groceries": 0.95}
    region_multiplier = {"North": 1.08, "South": 1.02, "East": 1.0, "West": 1.12}
    seasonal_multiplier = {"Spring": 1.02, "Summer": 1.08, "Fall": 1.05, "Winter": 0.98}
    store_multiplier = {"Store A": 1.0, "Store B": 1.04, "Store C": 1.08}

    base_sales = (
        520
        + (df["customer_count"] * 3.2)
        + (df["discount"] * 2.4)
        + (df["month"] * 18)
        + df["promotion"].astype(int) * 140
    )
    base_sales = (
        base_sales
        * df["category"].map(category_multiplier)
        * df["region"].map(region_multiplier)
        * df["season"].map(seasonal_multiplier)
        * df["store"].map(store_multiplier)
    )
    df["sales"] = np.clip(base_sales + rng.normal(0, 35, size=rows), 120, None).round(2)
    df.to_csv(target_path, index=False)
    return df


def _prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    frame = df.copy()
    frame["promotion"] = frame["promotion"].astype(int)
    frame["region"] = frame["region"].astype("category")
    frame["category"] = frame["category"].astype("category")
    frame["store"] = frame["store"].astype("category")
    frame["season"] = frame["season"].astype("category")

    features = pd.get_dummies(
        frame[["region", "category", "store", "month", "promotion", "discount", "customer_count", "season"]],
        drop_first=True,
    )
    target = frame["sales"]
    return features, target


def train_model(df: pd.DataFrame | None = None, model_path: Path | str | None = None) -> Dict[str, Any]:
    frame = df if df is not None else ensure_dataset()
    model_file = Path(model_path or MODEL_PATH)
    model_file.parent.mkdir(parents=True, exist_ok=True)

    X, y = _prepare_features(frame)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=180, random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    score = r2_score(y_test, predictions)

    joblib.dump(model, model_file)
    return {"rows": len(frame), "r2_score": float(score), "model_path": str(model_file)}


def predict_sales(payload: Dict[str, Any], model_path: Path | str | None = None) -> Dict[str, Any]:
    model_file = Path(model_path or MODEL_PATH)
    if not model_file.exists():
        train_model(model_path=model_file)

    model = joblib.load(model_file)
    row = pd.DataFrame(
        [
            {
                "region": payload.get("region", "North"),
                "category": payload.get("category", "Electronics"),
                "store": payload.get("store", "Store A"),
                "month": int(payload.get("month", 1)),
                "promotion": int(bool(payload.get("promotion", False))),
                "discount": float(payload.get("discount", 0)),
                "customer_count": float(payload.get("customer_count", 50)),
                "season": payload.get("season", "Summer"),
            }
        ]
    )
    feature_frame = pd.get_dummies(
        row[["region", "category", "store", "month", "promotion", "discount", "customer_count", "season"]],
        drop_first=True,
    )
    missing = set(model.feature_names_in_) - set(feature_frame.columns)
    for col in missing:
        feature_frame[col] = 0
    feature_frame = feature_frame.reindex(columns=model.feature_names_in_, fill_value=0)

    prediction = float(model.predict(feature_frame)[0])
    confidence = "High" if prediction > 800 else "Medium" if prediction > 500 else "Low"
    return {"predicted_sales": round(prediction, 2), "confidence": confidence}


def get_dashboard_summary() -> Dict[str, Any]:
    df = ensure_dataset()
    rng = np.random.default_rng(59)

    monthly_sales = (
        df.groupby("month")["sales"].sum().reindex(range(1, 13), fill_value=0)
        .reset_index()
        .to_dict(orient="records")
    )
    region_sales = (
        df.groupby("region")["sales"].sum().sort_values(ascending=False)
        .reset_index()
        .to_dict(orient="records")
    )
    category_sales = (
        df.groupby("category")["sales"].sum().sort_values(ascending=False)
        .reset_index()
        .to_dict(orient="records")
    )

    total_sales = float(df["sales"].sum())
    profit = round(total_sales * rng.uniform(0.28, 0.34), 2)
    expenses = round(total_sales - profit, 2)
    total_customers = int(np.clip(len(df) * rng.uniform(0.72, 0.88), 130, 230))
    total_orders = int(np.clip(len(df) * rng.uniform(0.92, 1.05), 190, 255))
    average_order_value = round(total_sales / max(total_orders, 1), 2)
    satisfaction_score = int(np.clip(86 + rng.integers(0, 11), 86, 97))
    active_users = int(np.clip(total_customers * rng.uniform(2.0, 3.1), 190, 780))
    new_users = int(np.clip(active_users * rng.uniform(0.23, 0.32), 55, 260))
    returning_users = active_users - new_users
    bounce_rate = round(np.clip(18 + rng.uniform(-3.5, 4.5), 18.0, 32.0), 1)
    growth_pct = round(rng.uniform(12.0, 22.5), 1)
    conversion_rate = round(np.clip(1.8 + rng.uniform(0, 3.5), 1.8, 5.8), 1)
    monthly_recurring_revenue = round(total_sales / 12 * rng.uniform(0.74, 0.92), 2)
    cash_flow = round(profit * rng.uniform(0.71, 0.9), 2)

    quarterly_sales = [
        {"quarter": f"Q{idx}", "sales": round(monthly_sales[start - 1 : end]["sales"].sum() if False else float(np.sum([item["sales"] for item in monthly_sales[start - 1:end]])), 2)}
        for idx, (start, end) in enumerate([(1, 3), (4, 6), (7, 9), (10, 12)], start=1)
    ]

    if len(monthly_sales) >= 2:
        last_month_value = monthly_sales[-1]["sales"]
        prev_month_value = monthly_sales[-2]["sales"]
        monthly_change = round((last_month_value - prev_month_value) / max(prev_month_value, 1) * 100, 1)
    else:
        monthly_change = growth_pct

    favorite_region = region_sales[0]["region"] if region_sales else "North"
    favorite_category = category_sales[0]["category"] if category_sales else "Electronics"
    favorite_store = df["store"].mode().iloc[0] if not df["store"].mode().empty else "Store A"

    expense_breakdown = [
        {"label": "Marketing", "value": round(expenses * 0.29, 2)},
        {"label": "Logistics", "value": round(expenses * 0.22, 2)},
        {"label": "Payroll", "value": round(expenses * 0.21, 2)},
        {"label": "Inventory", "value": round(expenses * 0.18, 2)},
        {"label": "Operations", "value": round(expenses * 0.1, 2)},
    ]

    forecast = [
        {"label": f"M{i}", "value": round(total_sales * (0.075 + rng.normal(0.01, 0.005)), 2)}
        for i in range(1, 7)
    ]

    product_performance = [
        {"name": "UltraSmart TV", "sales": round(total_sales * 0.142, 2), "trend": "+12%"},
        {"name": "EcoFridge", "sales": round(total_sales * 0.098, 2), "trend": "+8%"},
        {"name": "StyleWear", "sales": round(total_sales * 0.085, 2), "trend": "+15%"},
        {"name": "KitchenPro", "sales": round(total_sales * 0.063, 2), "trend": "+6%"},
        {"name": "SmartSound", "sales": round(total_sales * 0.055, 2), "trend": "+18%"},
    ]

    ai_insights = [
        {"title": "Revenue insight", "text": f"Revenue accelerated by {growth_pct}% from the prior month.", "theme": "success"},
        {"title": "Top region", "text": f"{favorite_region} drove the highest revenue contribution.", "theme": "accent"},
        {"title": "Category leader", "text": f"{favorite_category} is the strongest performing segment.", "theme": "info"},
        {"title": "Forecast", "text": f"Next month expected revenue: ₹{int(total_sales * 0.088):,}.", "theme": "warning"},
    ]

    notifications = [
        f"Revenue crossed ₹{int(total_sales // 100000) * 100000:,}.",
        "New customer signup rate increased by 11%.",
        "Inventory alert: Groceries stock is low in North branches.",
        "Profit margin is stable at over 30% this quarter.",
    ]

    summary = {
        "total_rows": int(len(df)),
        "total_sales": round(total_sales, 2),
        "profit": profit,
        "expenses": expenses,
        "total_customers": total_customers,
        "total_orders": total_orders,
        "growth_pct": growth_pct,
        "conversion_rate": conversion_rate,
        "average_order_value": average_order_value,
        "satisfaction_score": satisfaction_score,
        "active_users": active_users,
        "new_users": new_users,
        "returning_users": returning_users,
        "bounce_rate": bounce_rate,
        "monthly_recurring_revenue": monthly_recurring_revenue,
        "cash_flow": cash_flow,
        "top_region": favorite_region,
        "top_category": favorite_category,
        "top_store": favorite_store,
        "monthly_sales": monthly_sales,
        "region_sales": region_sales,
        "category_sales": category_sales,
        "expense_breakdown": expense_breakdown,
        "forecast": forecast,
        "ai_insights": ai_insights,
        "notifications": notifications,
        "product_performance": product_performance,
        "monthly_change": monthly_change,
        "quarterly_sales": quarterly_sales,
    }
    return summary
