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
