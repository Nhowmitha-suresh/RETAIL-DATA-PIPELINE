from pathlib import Path
from typing import Any, Dict

from etl.pipeline import MODEL_PATH, ensure_dataset, train_model


def main() -> Dict[str, Any]:
    df = ensure_dataset()
    return train_model(df=df, model_path=MODEL_PATH)


if __name__ == "__main__":
    print(main())
