import tempfile
from pathlib import Path

import pandas as pd

from asi_project.data import normalize_input
from asi_project.model_package import load_model_package

ARTIFACT = "asi-projekt-26/asi_project/production-model:production"
SAMPLE_DATA_PATH = Path("data/01_raw/sample.csv")
ROWS = 5


def run_smoke_test(artifact_ref: str, sample_path: Path, rows: int) -> None:
    import wandb

    artifact = wandb.Api().artifact(artifact_ref)
    with tempfile.TemporaryDirectory() as tmp_dir:
        model_package_dir = Path(artifact.download(root=tmp_dir))
        model_package = load_model_package(model_package_dir)
        sample_df = normalize_input(pd.read_csv(sample_path).head(rows))
        predictions = model_package.predict(sample_df)
        assert isinstance(predictions, pd.Series), f"Expected pd.Series, got {type(predictions)}"
        assert len(predictions) == rows, f"Expected {rows} predictions, got {len(predictions)}"
        assert pd.api.types.is_integer_dtype(predictions), (
            f"Expected integer dtype, got {predictions.dtype}"
        )
        assert set(predictions).issubset({0, 1}), (
            f"Unexpected values in predictions: {set(predictions.unique)}"
        )
        print(f"Predictions ({rows} rows): {predictions.tolist()}")


def main() -> None:
    run_smoke_test(ARTIFACT, SAMPLE_DATA_PATH, ROWS)


if __name__ == "__main__":
    main()
