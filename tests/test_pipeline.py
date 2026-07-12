from pathlib import Path

from etl.pipeline import ensure_dataset, predict_sales, train_model


def test_dataset_generation_and_training(tmp_path):
    dataset_path = tmp_path / "sales.csv"
    model_path = tmp_path / "model.joblib"

    df = ensure_dataset(dataset_path)

    assert not df.empty
    assert {"sales", "region", "category", "promotion"}.issubset(df.columns)

    result = train_model(df=df, model_path=model_path)

    assert result["rows"] == len(df)
    assert result["r2_score"] >= 0.0
    assert model_path.exists()

    prediction = predict_sales(
        {
            "region": "North",
            "category": "Electronics",
            "store": "Store A",
            "month": 7,
            "promotion": True,
            "discount": 12,
            "customer_count": 85,
            "season": "Summer",
        },
        model_path=model_path,
    )

    assert prediction["predicted_sales"] > 0
    assert prediction["confidence"] in {"High", "Medium", "Low"}
