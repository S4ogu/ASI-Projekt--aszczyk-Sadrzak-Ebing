import json
import platform
import shutil
from collections.abc import Mapping, Sequence
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

MODEL_DIR_NAME = "model"
METADATA_FILE_NAME = "metadata.json"
SKLEARN_MODEL_FILE_NAME = "model.joblib"
FORMAT_SKLEARN = "sklearn-joblib"
FORMAT_AUTOGLUON = "autogluon-tabular"

REQUIRED_METADATA_FIELDS = (
    "model_type",
    "model_format",
    "features",
    "target",
    "positive_class",
    "metrics",
    "git_sha",
    "dataset_fingerprint",
    "library_versions",
)
TRACKED_LIBRARIES = ("scikit-learn", "pandas", "numpy", "autogluon.tabular", "joblib")


class ModelPackageError(ValueError):
    """Wystąpił błąd podczas tworzenia lub wczytywania pakietu modelu."""

    pass


class ModelPackage:
    """Wczytywany pakiet: model gotowy do predykcji wraz z metadanymi opisującymi model i dane, na których był trenowany."""

    def __init__(self, model, metadata):
        self.model = model
        self.metadata = metadata

    def features(self):
        return self.metadata["features"]

    def predict(self, frame):
        missing = []
        for name in self.features():
            if name not in frame.columns:
                missing.append(name)
        if missing:
            raise ModelPackageError(f"Brakujące kolumny w ramce danych: {missing}")
        predictions = self.model.predict(frame[self.features()])
        return pd.Series(predictions, index=frame.index, name="prediction").astype(int)


def library_versions():
    """Zwraca słownik z wersjami bibliotek, które są śledzone w metadanych pakietu modelu."""
    versions = {"python": platform.python_version()}
    for lib in TRACKED_LIBRARIES:
        try:
            versions[lib] = importlib_metadata.version(lib)
        except importlib_metadata.PackageNotFoundError:
            versions[lib] = None
    return versions


def build_metadata(
    *,
    model_type: str,
    model_format: str,
    features: Sequence[str],
    target: str,
    positive_class: str,
    metrics: Mapping[str, Any],
    git_sha: str,
    dataset_fingerprint: str,
    model_name: str = None,
    model_parameters: Mapping[str, Any] = None,
) -> dict[str, Any]:
    """Buduje metadane pakietu modelu."""
    metadata = {
        "model_type": model_type,
        "model_format": model_format,
        "features": list(features),
        "target": target,
        "positive_class": positive_class,
        "metrics": dict(metrics),
        "git_sha": git_sha,
        "dataset_fingerprint": dataset_fingerprint,
        "library_versions": library_versions(),
        "model_name": model_name,
        "model_parameters": dict(model_parameters) if model_parameters is not None else None,
    }
    return metadata


def validate_metadata(metadata: dict[str, Any]) -> None:
    """Waliduje metadane pakietu modelu."""
    missing_fields = []
    for field in REQUIRED_METADATA_FIELDS:
        if field not in metadata:
            missing_fields.append(field)
    if missing_fields:
        raise ModelPackageError(f"Brakujące pola w metadanych pakietu modelu: {missing_fields}")


def save_model_package(model, metadata, package_dir, model_name=None):
    """Zapisuje pakiet modelu do katalogu."""
    package_dir = Path(package_dir)
    validate_metadata(metadata)
    model_format = metadata["model_format"]

    if package_dir.exists():
        shutil.rmtree(package_dir)
    model_dir = package_dir / MODEL_DIR_NAME
    model_dir.mkdir(parents=True, exist_ok=True)

    if model_format == FORMAT_SKLEARN:
        model_file = model_dir / SKLEARN_MODEL_FILE_NAME
        joblib.dump(model, model_file)
    elif model_format == FORMAT_AUTOGLUON:
        if model_name is None:
            model_name = metadata.get("model_name") or "best"
        model.clone_for_deployment(path=str(model_dir), model=model_name, dirs_exist_ok=True)
    else:
        raise ModelPackageError(f"Nieobsługiwany format modelu: {model_format}")

    with open(package_dir / METADATA_FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    return package_dir


def load_metadata(package_dir):
    """Wczytuje metadane pakietu modelu z katalogu."""
    package_dir = Path(package_dir)
    metadata_file = package_dir / METADATA_FILE_NAME
    if not metadata_file.exists():
        raise ModelPackageError(f"Nie znaleziono pliku metadanych: {metadata_file}")
    with open(metadata_file, encoding="utf-8") as f:
        metadata = json.load(f)
    validate_metadata(metadata)
    return metadata


def load_model_package(package_dir):
    """Wczytuje pakiet modelu z katalogu."""
    package_dir = Path(package_dir)
    metadata = load_metadata(package_dir)
    model_format = metadata["model_format"]
    model_dir = package_dir / MODEL_DIR_NAME

    if model_format == FORMAT_SKLEARN:
        model = joblib.load(model_dir / SKLEARN_MODEL_FILE_NAME)
    elif model_format == FORMAT_AUTOGLUON:
        from autogluon.tabular import TabularPredictor

        model = TabularPredictor.load(str(model_dir), require_py_version_match=False)
    else:
        raise ModelPackageError(f"Nieobsługiwany format modelu: {model_format}")
    return ModelPackage(model=model, metadata=metadata)
