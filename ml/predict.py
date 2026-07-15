from typing import Any, Dict

from etl.pipeline import predict_sales


def main(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    sample_payload = payload or {
        "region": "North",
        "category": "Electronics",
        "store": "Store A",
        "month": 7,
        "promotion": True,
        "discount": 12,
        "customer_count": 85,
        "season": "Summer",
    }
    return predict_sales(sample_payload)


if __name__ == "__main__":
    print(main())


def predict_with_model(features: Dict[str, Any], model_name: str = 'sales_forecast.joblib') -> Dict[str, Any]:
    from pathlib import Path
    import joblib
    import pandas as pd
    model_path = Path(__file__).resolve().parents[1] / 'models' / model_name
    if not model_path.exists():
        return {"error": "model not found", "model_path": str(model_path)}
    model = joblib.load(model_path)
    df = pd.DataFrame([features])
    preds = model.predict(df)
    return {"prediction": float(preds[0])}
