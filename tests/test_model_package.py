"""Sprint 3: zapis i odczyt pakietu modelu przez wspólne funkcje (bez AutoGluona i bez W&B)."""

import json

import pandas as pd
import pytest

from asi_project.data import filter_training_rows, make_xy, normalize_input
from asi_project.model import build_baseline_pipeline
from asi_project.model_package import (
    FORMAT_SKLEARN,
    METADATA_FILE_NAME,
    MODEL_DIR_NAME,
    REQUIRED_METADATA_FIELDS,
    ModelPackageError,
    build_metadata,
    load_model_package,
    save_model_package,
)


@pytest.fixture
def trained_baseline(project):
    """Baseline wytrenowany na próbce CI + dane wejściowe w tej samej postaci co w pipeline."""
    frame = filter_training_rows(normalize_input(project.sample), project.contract)
    X, y = make_xy(frame, project.contract, project.config.model_features)
    model = build_baseline_pipeline(
        list(project.config.numeric_features),
        list(project.config.categorical_features),
    )
    model.fit(X, y)
    return model, X


@pytest.fixture
def metadata(project):
    return build_metadata(
        model_type="baseline",
        model_format=FORMAT_SKLEARN,
        features=list(project.config.model_features),
        target=project.contract.target,
        positive_class=project.contract.positive_class,
        metrics={"f1": 0.5},
        git_sha="test-sha",
        dataset_fingerprint="test-fingerprint",
    )


def test_package_has_model_and_metadata(trained_baseline, metadata, tmp_path):
    model, _ = trained_baseline
    package_dir = save_model_package(model, metadata, tmp_path / "pkg")

    assert (package_dir / MODEL_DIR_NAME).is_dir()
    saved = json.loads((package_dir / METADATA_FILE_NAME).read_text(encoding="utf-8"))
    for field in REQUIRED_METADATA_FIELDS:
        assert field in saved, f"brak pola {field} w metadata.json"
    assert saved["library_versions"]["scikit-learn"] is not None


def test_roundtrip_gives_same_predictions(trained_baseline, metadata, tmp_path):
    model, X = trained_baseline
    save_model_package(model, metadata, tmp_path / "pkg")

    package = load_model_package(tmp_path / "pkg")
    rows = X.head(5)
    predictions = package.predict(rows)

    assert package.metadata["git_sha"] == "test-sha"
    assert len(predictions) == 5
    assert set(predictions.unique()) <= {0, 1}
    assert predictions.tolist() == pd.Series(model.predict(rows)).astype(int).tolist()


def test_predict_ignores_extra_columns(trained_baseline, metadata, tmp_path):
    model, X = trained_baseline
    save_model_package(model, metadata, tmp_path / "pkg")
    package = load_model_package(tmp_path / "pkg")

    rows = X.head(5).assign(extra_column=1)
    assert len(package.predict(rows)) == 5


def test_predict_rejects_missing_feature(trained_baseline, metadata, tmp_path):
    model, X = trained_baseline
    save_model_package(model, metadata, tmp_path / "pkg")
    package = load_model_package(tmp_path / "pkg")

    missing = package.features()[0]
    with pytest.raises(ModelPackageError, match=missing):
        package.predict(X.head(5).drop(columns=[missing]))


def test_save_rejects_incomplete_metadata(trained_baseline, metadata, tmp_path):
    model, _ = trained_baseline
    del metadata["git_sha"]
    with pytest.raises(ModelPackageError, match="git_sha"):
        save_model_package(model, metadata, tmp_path / "pkg")


def test_save_rejects_unknown_format(trained_baseline, metadata, tmp_path):
    model, _ = trained_baseline
    metadata["model_format"] = "onnx"
    with pytest.raises(ModelPackageError):
        save_model_package(model, metadata, tmp_path / "pkg")


def test_load_without_metadata_fails(tmp_path):
    (tmp_path / "pkg").mkdir()
    with pytest.raises(ModelPackageError):
        load_model_package(tmp_path / "pkg")
