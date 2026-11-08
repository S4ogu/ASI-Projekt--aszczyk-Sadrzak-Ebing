import pandas as pd
from sklearn.pipeline import Pipeline

from asi_project.config import DatasetContract, ProjectConfig, get_contract, load_project_config
from asi_project.data import make_xy, split_train_test
from asi_project.metrics import compute_metrics
from asi_project.model import build_baseline_pipeline


def _load_project() -> tuple[ProjectConfig, DatasetContract]:
    config = load_project_config()
    return config, get_contract(config)


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


def train_model(X_train: pd.DataFrame, y_train: pd.Series) -> Pipeline:
    config, _ = _load_project()
    model = build_baseline_pipeline(
        list(config.numeric_features),
        list(config.categorical_features),
    )
    model.fit(X_train, y_train)
    return model


def evaluate_model(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    y_pred = model.predict(X_test)
    return compute_metrics(y_test, y_pred)
