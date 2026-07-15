from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

MODEL_DIR = Path(__file__).resolve().parents[1] / 'models'
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def train_sales_forecast_from_csv(orders_csv: str, model_name: str = 'sales_forecast.joblib') -> Path:
    df = pd.read_csv(orders_csv, parse_dates=['order_timestamp'])
    df['month'] = df['order_timestamp'].dt.month
    df['dow'] = df['order_timestamp'].dt.dayofweek
    X = df[['month', 'dow', 'quantity']].fillna(0)
    y = df['selling_price'].fillna(0)
    model = RandomForestRegressor(n_estimators=50, n_jobs=-1, random_state=42)
    model.fit(X, y)
    path = MODEL_DIR / model_name
    joblib.dump(model, path)
    return path


def main() -> Dict[str, Any]:
    # backward compatible simple wrapper that uses existing ETL dataset
    from etl.pipeline import ensure_dataset
    df = ensure_dataset()
    csv_path = Path(__file__).resolve().parents[1] / 'data' / 'orders.csv'
    if not csv_path.exists():
        # fallback: write small sample
        df.head(10000).to_csv(csv_path, index=False)
    path = train_sales_forecast_from_csv(str(csv_path))
    return {"model_path": str(path)}


if __name__ == '__main__':
    print(main())
