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

    summary = {
        "total_rows": int(len(df)),
        "total_sales": round(float(df["sales"].sum()), 2),
        "average_sales": round(float(df["sales"].mean()), 2),
        "average_customer_count": round(float(df["customer_count"].mean()), 2),
        "top_region": df.groupby("region")["sales"].sum().sort_values(ascending=False).idxmax(),
        "top_category": df.groupby("category")["sales"].sum().sort_values(ascending=False).idxmax(),
        "top_store": df.groupby("store")["sales"].sum().sort_values(ascending=False).idxmax(),
        "promotion_boost": round(float(df.loc[df["promotion"], "sales"].mean() - df.loc[~df["promotion"], "sales"].mean()), 2),
        "monthly_sales": monthly_sales,
        "region_sales": region_sales,
        "category_sales": category_sales,
    }
    return summary
