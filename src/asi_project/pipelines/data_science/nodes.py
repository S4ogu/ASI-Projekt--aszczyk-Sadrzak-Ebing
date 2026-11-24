import json
import os
import subprocess
from pathlib import Path

import pandas as pd
from sklearn.pipeline import Pipeline

from asi_project.config import DatasetContract, ProjectConfig, get_contract, load_project_config
from asi_project.data import make_xy, split_train_test
from asi_project.metrics import compute_metrics
from asi_project.model import build_baseline_pipeline
from asi_project.model_package import (
    FORMAT_AUTOGLUON,
    FORMAT_SKLEARN,
    build_metadata,
    save_model_package,
)

try:  # pragma: no cover - optional dependency for Sprint 3
    import wandb  # type: ignore
except ImportError:  # pragma: no cover
    wandb = None

try:  # pragma: no cover - optional dependency for Sprint 3
    from autogluon.tabular import TabularPredictor
except ImportError:  # pragma: no cover
    TabularPredictor = None


def _load_project() -> tuple[ProjectConfig, DatasetContract]:
    config = load_project_config()
    return config, get_contract(config)


def _dataset_fingerprint() -> str:
    config, contract = _load_project()
    fingerprint_path = (
        Path(config.root) / "data" / "01_raw" / contract.dataset_id / "fingerprint.json"
    )
    if not fingerprint_path.is_file():
        return "unknown"
    with fingerprint_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return str(payload.get("sha256") or payload.get("hash") or "unknown")


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def _log_wandb_run(
    run_name: str | None,
    model_type: str,
    metrics: dict,
    model_params: dict,
    split_params: dict,
    wandb_params: dict,
) -> None:
    if wandb is None:
        return
    project_name = str(wandb_params.get("project", "asi_project"))
    mode = os.environ.get("WANDB_MODE", str(wandb_params.get("mode", "disabled")))
    try:
        wandb.init(
            project=project_name, name=run_name or f"{model_type}-run", reinit=True, mode=mode
        )
        wandb.config.update(
            {
                "model_type": model_type,
                "model_params": model_params,
                "split": split_params,
                "git_sha": _git_sha(),
                "dataset_fingerprint": _dataset_fingerprint(),
            }
        )
        wandb.log(metrics)
        wandb.run.summary["git_sha"] = _git_sha()
        wandb.run.summary["dataset_fingerprint"] = _dataset_fingerprint()
    finally:
        wandb.finish()


def split_data(
    model_input_data: pd.DataFrame,
    split_params: dict[str, float],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    config, contract = _load_project()
    X, y = make_xy(model_input_data, contract, config.model_features)
    return split_train_test(
        X,
        y,
        contract,
        test_size=float(split_params["test_size"]),
        random_state=int(split_params["random_state"]),
    )


def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_type: str = "baseline",
    model_params: dict | None = None,
) -> Pipeline | object:
    config, _ = _load_project()
    if model_type == "baseline":
        model = build_baseline_pipeline(
            list(config.numeric_features),
            list(config.categorical_features),
        )
        model.fit(X_train, y_train)
        return model
    if model_type == "autogluon":
        if TabularPredictor is None:
            raise RuntimeError("AutoGluon is not installed. Install requirements/preflight-s3.txt.")
        train_frame = X_train.copy()
        train_frame["target"] = y_train.to_numpy()
        training_params = model_params or {}
        preset = str(training_params.get("preset", "medium_quality"))
        time_limit = int(training_params.get("time_limit", 60))
        if time_limit <= 0:
            raise ValueError(f"AutoGluon time_limit must be positive, got {time_limit}.")
        predictor = TabularPredictor(
            label="target",
            problem_type="binary",
            eval_metric="f1",
        )
        predictor.fit(train_frame, time_limit=time_limit, presets=[preset])
        return predictor
    raise ValueError(f"Unknown model_type: {model_type!r}.")


def train_production_model(model_input_data: pd.DataFrame, model_type: str = "autogluon") -> object:
    config, contract = _load_project()
    X, y = make_xy(model_input_data, contract, config.model_features)
    full_frame = X.copy()
    full_frame["target"] = y.to_numpy()

    if model_type != "autogluon":
        raise ValueError(
            f"Production training currently supports autogluon only, got {model_type!r}."
        )
    if TabularPredictor is None:
        raise RuntimeError("AutoGluon is not installed. Install requirements/preflight-s3.txt.")

    predictor = TabularPredictor(
        label="target",
        problem_type="binary",
        eval_metric="f1",
    )
    predictor.fit(full_frame, time_limit=60, presets=["medium_quality"])
    return predictor


def evaluate_model(
    model: Pipeline | object,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    run_name: str | None = None,
    model_type: str = "baseline",
    model_params: dict | None = None,
    split_params: dict | None = None,
    wandb_params: dict | None = None,
) -> dict:
    if hasattr(model, "predict"):
        y_pred = model.predict(X_test)
    else:
        raise TypeError(f"Unsupported model object for evaluation: {type(model)!r}")
    metrics = compute_metrics(y_test, y_pred)
    _log_wandb_run(
        run_name,
        model_type,
        metrics,
        model_params or {},
        split_params or {},
        wandb_params or {},
    )
    return metrics


def package_model(model, metrics, model_type, model_params, package_params):
    config, contract = _load_project()
    model_format = FORMAT_AUTOGLUON if model_type == "autogluon" else FORMAT_SKLEARN
    metadata = build_metadata(
        model_type=model_type,
        model_format=model_format,
        features=list(config.model_features),
        target=contract.target,
        positive_class=contract.positive_class,
        metrics=metrics,
        git_sha=_git_sha(),
        dataset_fingerprint=_dataset_fingerprint(),
        model_name=package_params.get("model_name"),
        model_parameters=model_params,
    )
    save_model_package(model, metadata, package_params["path"])
    return metadata
